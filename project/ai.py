import os
import subprocess
import requests
import dwani
import logging
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import time
import mysql.connector
import pandas as pd
from math import radians
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import haversine_distances
from joblib import dump, load
import random
from sklearn.metrics import accuracy_score
import re
from flask import Flask, render_template, request
from django.shortcuts import render

app = Flask(__name__)


MODEL_FILENAME = "labor_recommendation_model.joblib"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "labor_db"
}


skill_pool = {
    1: ["digging", "watering", "harvesting"],
    2: ["tractor driving", "irrigation management", "crop monitoring"],
    3: ["pesticide application", "soil testing", "disease detection"]
}

def skill_score(worker_skills, job_skills):
    score = 0
    for skill in job_skills:
        for level, skills in skill_pool.items():
            if skill in worker_skills and skill in skills:
                score += level
    return score

def fetch_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM laborers")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(rows)

def prepare_training_data(data, job_lat, job_lon, job_skills, job_gender, job_age):
    X, y = [], []
    for _, row in data.iterrows():
        loc1 = [radians(job_lat), radians(job_lon)]
        loc2 = [radians(row['latitude']), radians(row['longitude'])]
        dist_km = haversine_distances([loc1, loc2])[1][0] * 6371
        location_score = 1 / (1 + dist_km)

        worker_skills = row['skills'].lower().split(";")
        skillmatch_score = skill_score(worker_skills, job_skills)

        gender_match = 1 if row['gender'].lower() == job_gender.lower() else 0
        age_diff = abs(row['age'] - job_age)

        features = [
            location_score,
            skillmatch_score,
            gender_match,
            age_diff,
            row['available'],
            row['rating'],
            row['experience']
        ]
        X.append(features)

        score = (
            0.3 * location_score +
            0.25 * (skillmatch_score / 9) +
            0.15 * gender_match +
            0.1 * (1 - age_diff / 50) +
            0.1 * (row['rating'] / 5) +
            0.1 * (row['experience'] / 15)
        )
        hired = 1 if score > 0.5 + random.uniform(-0.1, 0.1) else 0
        y.append(hired)
    return X, y

def train_or_load_model(X, y):
    if os.path.exists(MODEL_FILENAME):
        print("Loading existing model...")
        model = load(MODEL_FILENAME)
        print("Retraining model on new data...")
        model.fit(X, y)
    else:
        print("Training new model...")
        model = RandomForestClassifier()
        model.fit(X, y)
    dump(model, MODEL_FILENAME)
    print(f"Model saved as {MODEL_FILENAME}")
    return model

def recommend_labors_ml(model, data, job_lat, job_lon, job_skills, job_gender, job_age):
    job_skills = job_skills.lower().split(";")
    scores = []

    for _, row in data.iterrows():
        loc1 = [radians(job_lat), radians(job_lon)]
        loc2 = [radians(row['latitude']), radians(row['longitude'])]
        dist_km = haversine_distances([loc1, loc2])[1][0] * 6371
        location_score = 1 / (1 + dist_km)

        worker_skills = row['skills'].lower().split(";")
        skillmatch_score = skill_score(worker_skills, job_skills)
        gender_match = 1 if row['gender'].lower() == job_gender.lower() else 0
        age_diff = abs(row['age'] - job_age)

        features = [[
            location_score,
            skillmatch_score,
            gender_match,
            age_diff,
            row['available'],
            row['rating'],
            row['experience']
        ]]

        prob = model.predict_proba(features)[0][1]  # prob hired
        scores.append((row['name'], row['phone'], prob))

    top_labors = sorted(scores, key=lambda x: x[2], reverse=True)[:10]
    return pd.DataFrame(top_labors, columns=["Name", "Phone", "Hired_Probability"])


def main(job_lat, job_lon,job_skills,job_gender,job_age):


    print("Fetching laborers data from DB...")
    data = fetch_data()

    print("Preparing training data...")
    X, y = prepare_training_data(data, job_lat, job_lon, job_skills.lower().split(";"), job_gender, job_age)

    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training or loading model...")
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate accuracy
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.2f}")

    print("Saving model...")
    dump(model, MODEL_FILENAME)

    print("Recommending top 10 laborers for the job:")
    recs = recommend_labors_ml(model, data, job_lat, job_lon, job_skills, job_gender, job_age)
    return recs


job_lat, job_lon = 22.2, 79.0
job_skills = "soil testing"
job_gender = "Female"
job_age = 30






@app.route('/', methods=['GET', 'POST'])
def index():
    global job_lat, job_lon,job_skills,job_gender,job_age
    if request.method == 'POST':
        job_lat = request.form.get('latitude')
        job_lon = request.form.get('longitude')
        job_age = request.form.get('age')
        job_gender = request.form.get('gender')
        job_skills = ';'.join(request.form.getlist('job_type'))
        # Now you can use these values in your recommendation logic

    return render_template('form.html')
app.run(debug=True)


print(job_lat, job_lon,job_skills,job_gender,job_age)



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DWANI Configuration
dwani.api_key = "gowthamkraj1234@gmail.com_dwani"
dwani.api_base = "https://dwani-dwani-api.hf.space"

# LLM Studio Configuration
LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}

model_payload = {
    "model": "gemma-3-1b-it-qat",
    "messages": [],
    "temperature": 0.7
}

SOURCE_LANG = "English"
TARGET_LANG = "Kannada"
REVERSE_SOURCE = "Kannada"
REVERSE_TARGET = "English"
SAMPLERATE = 16000
DURATION = 10  

def enable_speaker():
    time.sleep(2)
    speaker_x, speaker_y = 281, 1658  
    subprocess.run(["adb", "shell", f"input tap {speaker_x} {speaker_y}"])
    print("🔊 Speakerphone enabled.")


def retry_until_success(func, max_retries=100, delay=2, *args, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retries += 1
            print(f"[Retry {retries}] Error: {e}")
            time.sleep(delay)
    raise RuntimeError(f"Function {func.__name__} failed after {max_retries} retries.")

def translate_api(sentences, src_lang, tgt_lang):
    try:
        if isinstance(sentences, str):
            sentences = [s.strip() for s in sentences.split(",") if s.strip()]
        elif isinstance(sentences, list):
            sentences = [s.strip() for s in sentences if isinstance(s, str) and s.strip()]
        else:
            return {"error": "Invalid input: sentences must be a string or list of strings"}

        if not sentences:
            return {"error": "Please provide at least one non-empty sentence"}

        if not src_lang or not tgt_lang:
            return {"error": "Invalid source or target language selection"}

        result = retry_until_success(
            dwani.Translate.run_translate,
            sentences=sentences, src_lang=src_lang, tgt_lang=tgt_lang
        )
        return result
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def text_to_speech(text, save_path):
    try:
        audio_bytes = retry_until_success(
            dwani.Audio.speech,
            input=text, response_format="mp3"
        )
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
        return save_path
    except Exception as e:
        raise ValueError(f"Failed to get/save audio: {e}")

def play_audio_with_vlc(file_path):
    vlc_path = r"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
    vlc_command = [vlc_path, "--play-and-exit", file_path]
    subprocess.run(vlc_command, check=True)

def record_audio(filename, duration=DURATION, samplerate=SAMPLERATE):
    print("Recording started (speak now)...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    write(filename, samplerate, audio)
    print(f"Recording saved to: {filename}")

def transcribe_audio(file_path, language):
    print(f"Transcribing audio in '{language}'...")
    return retry_until_success(
        dwani.ASR.transcribe,
        file_path=file_path, language=language
    )

def call_lmstudio_with_retry(payload):
    def post_request():
        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    return retry_until_success(post_request)

def chat_with_lmstudio():
    global data
    print("Speak in Kannada. Type 'exit' to quit.")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file_path = os.path.join(script_dir, "output_audio.mp3")

    while True:
        # Record voice
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            audio_path = tmpfile.name

        record_audio(audio_path)

        # Transcribe Kannada speech
        transcription_result = transcribe_audio(audio_path, "Kannada")
        os.remove(audio_path)

        if "error" in transcription_result:
            print("Transcription error:", transcription_result["error"])
            continue

        Kannada_text = transcription_result.get("text") or transcription_result.get("transcription")
        print("You (Kannada):", Kannada_text)

        # Translate Kannada to English
        translation_to_english = translate_api(Kannada_text, REVERSE_SOURCE, REVERSE_TARGET)
        if "error" in translation_to_english:
            print("Translation error:", translation_to_english["error"])
            continue

        english_texts = translation_to_english.get("translations") or translation_to_english.get("result")
        english_input = english_texts[0] if isinstance(english_texts, list) else english_texts
        print("Translated to English:", english_input)

        # Call LM Studio
        model_payload["messages"].append({
            "role": "user",
            "content": " data:"+data+" and the question:" + english_input+" answer in just 5 words"
        })

        try:
            result = call_lmstudio_with_retry(model_payload)
            assistant_reply = result['choices'][0]['message']['content']
            if "“" in assistant_reply:
                assistant_reply = re.findall(r'“(.*?)”', assistant_reply)
            print("Assistant (English):", assistant_reply)
            # Translate back to Kannada
            assistant_reply=assistant_reply.replace(","," ")
            translation_to_Kannada = translate_api(assistant_reply, SOURCE_LANG, TARGET_LANG)
            if "error" in translation_to_Kannada:
                print("Translation Error:", translation_to_Kannada["error"])
                continue

            Kannada_reply = translation_to_Kannada.get("translations") or translation_to_Kannada.get("result")
            Kannada_output = Kannada_reply[0] if isinstance(Kannada_reply, list) else Kannada_reply
            print("Translated to Kannada:", Kannada_output)

            # Convert to speech
            text_to_speech(Kannada_output, audio_file_path)
            print(f"Playing audio from {audio_file_path}...")
            play_audio_with_vlc(audio_file_path)

            # Maintain conversation context
            model_payload["messages"].append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print("Error communicating with LM Studio or processing:", e)

y=main(job_lat, job_lon,job_skills,job_gender,job_age)
print(y)
for index, row in y.iterrows():
    data="3 acre of land need labor for ploughing land for tomorrow,location mysore"
    phone=str(row['Phone'])
    print(row['Phone'],row['Name'])
    subprocess.run("adb shell am start -a android.intent.action.CALL -d tel:+91"+phone, shell=True, check=True)
    time.sleep(1)
    enable_speaker()
    chat_with_lmstudio()
