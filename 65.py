import requests
import speech_recognition as sr
import pyttsx3
import subprocess
import time


# === Text-to-Speech Engine Setup ===
engine = pyttsx3.init()

def set_female_voice(engine):
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower() or "zira" in voice.name.lower() or "samantha" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    else:
        print("⚠️ Female voice not found, using default voice.")

set_female_voice(engine)
engine.setProperty('rate', 165)

# === LM Studio Server Setup ===
LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

model_payload = {
    "model": "gemma-3-1b-it-qat",
    "messages": [],
    "temperature": 0.7
}

# === Text-to-Speech ===
def speak(text):
    print("AI 💬:", text)
    engine.say(text)
    engine.runAndWait()

# === Speech Recognition ===
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text
        except sr.UnknownValueError:
            print("😕 Sorry, I didn't catch that.")
            return ""
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            return ""

# === Accept Incoming Call ===
def accept_incoming_call():
    print("📲 Waiting for an incoming call...")
    speak("Waiting for your call sir.")

    while True:
        try:
            result = subprocess.check_output(["adb", "shell", "dumpsys", "telecom"]).decode()
            if "state=RINGING" in result:
                print("📞 Incoming call detected.")
                speak("Hey sir, I'm answering your call now.")
                subprocess.run(["adb", "shell", "input keyevent 5"])# Answer the call
                time.sleep(3)
                enable_speaker()
                return True
        except subprocess.CalledProcessError as e:
            print("Error checking call state:", e)
        time.sleep(2)

def enable_speaker():
    # Wait to ensure UI is stable before tapping speaker
    time.sleep(2)
    speaker_x, speaker_y = 281, 1658  # Adjust these for your phone
    subprocess.run(["adb", "shell", f"input tap {speaker_x} {speaker_y}"])
    print("🔊 Speakerphone enabled.")

# === End the call ===
def end_call():
    subprocess.run(["adb", "shell", "input keyevent 6"])  # End call
    print("📴 Call ended.")

# === Main Chat Function ===
def chat_with_lmstudio():
    print("💖 Waiting for you to say hello...")

    time.sleep(2)
    speak("Hey, I'm here for you. Just talk to me.")

    while True:
        user_input = listen()
        if not user_input:
            continue
        if "bye" in user_input.lower():
            speak("Okay, talk to you later! bye")
            end_call()
            break

        model_payload["messages"].append({
            "role": "user",
            "content": "Respond concisely and professionally like an AI assistant. Do not use emojis: " + user_input
        })

        try:
            response = requests.post(LMSTUDIO_URL, headers=headers, json=model_payload)
            response.raise_for_status()
            result = response.json()

            assistant_reply = result['choices'][0]['message']['content']
            speak(assistant_reply)

            model_payload["messages"].append({
                "role": "assistant",
                "content": assistant_reply
            })

        except Exception as e:
            print("Error communicating with LM Studio:", e)
            speak("Something went wrong.")

# === Entry Point ===
while True:
    if accept_incoming_call():
        chat_with_lmstudio()
