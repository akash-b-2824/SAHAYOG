import os
import subprocess
import requests
import dwani
import logging
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import time

def pick_call():
    subprocess.run(["adb", "shell", "input", "tap", "281", "1658"])
    print("Call picked up.")

def enable_speaker():
    subprocess.run(["adb", "shell", "input", "tap", "281", "1658"])
    print("Speaker enabled.")


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
TARGET_LANG = "Hindi"
REVERSE_SOURCE = "Hindi"
REVERSE_TARGET = "English"
SAMPLERATE = 16000
DURATION = 10  


def accept_incoming_call():
    print("📲 Waiting for an incoming call...")
    while True:
        try:
            result = subprocess.check_output(["adb", "shell", "dumpsys", "telecom"]).decode()
            if "state=RINGING" in result:
                print("📞 Incoming call detected.")
                subprocess.run(["adb", "shell", "input keyevent 5"])# Answer the call
                time.sleep(1)
                enable_speaker()
                return True
        except subprocess.CalledProcessError as e:
            print("Error checking call state:", e)
        time.sleep(2)

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
    print("Speak in Hindi. Type 'exit' to quit.")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file_path = os.path.join(script_dir, "output_audio.mp3")

    while True:
        # Record voice
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            audio_path = tmpfile.name

        record_audio(audio_path)

        # Transcribe Hindi speech
        transcription_result = transcribe_audio(audio_path, "Hindi")
        os.remove(audio_path)

        if "error" in transcription_result:
            print("Transcription error:", transcription_result["error"])
            continue

        Hindi_text = transcription_result.get("text") or transcription_result.get("transcription")
        print("You (Hindi):", Hindi_text)

        # Translate Hindi to English
        translation_to_english = translate_api(Hindi_text, REVERSE_SOURCE, REVERSE_TARGET)
        if "error" in translation_to_english:
            print("Translation error:", translation_to_english["error"])
            continue

        english_texts = translation_to_english.get("translations") or translation_to_english.get("result")
        english_input = english_texts[0] if isinstance(english_texts, list) else english_texts
        print("Translated to English:", english_input)

        # Call LM Studio
        model_payload["messages"].append({
            "role": "user",
            "content": "short answer:" + english_input
        })

        try:
            result = call_lmstudio_with_retry(model_payload)
            assistant_reply = result['choices'][0]['message']['content']
            print("Assistant (English):", assistant_reply)

            # Translate back to Hindi
            translation_to_Hindi = translate_api(assistant_reply, SOURCE_LANG, TARGET_LANG)
            if "error" in translation_to_Hindi:
                print("Translation Error:", translation_to_Hindi["error"])
                continue

            Hindi_reply = translation_to_Hindi.get("translations") or translation_to_Hindi.get("result")
            Hindi_output = Hindi_reply[0] if isinstance(Hindi_reply, list) else Hindi_reply
            print("Translated to Hindi:", Hindi_output)

            # Convert to speech
            text_to_speech(Hindi_output, audio_file_path)
            print(f"Playing audio from {audio_file_path}...")
            play_audio_with_vlc(audio_file_path)

            # Maintain conversation context
            model_payload["messages"].append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print("Error communicating with LM Studio or processing:", e)

while True:
    if accept_incoming_call():
        chat_with_lmstudio()
