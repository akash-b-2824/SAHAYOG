# SAHAYOG

Empowering Farmers and Laborers — One Tool at a Time

Project Overview

> “While others build apps for the connected, we’re building access for the forgotten. This is Digital India — inclusive, voice-first, and built for everyone.”




---

1. Problem & Impact

Millions of rural laborers and farmers are excluded from digital services — not by choice, but due to lack of smartphones and internet access.
We’re changing that. Using only their voice and a basic phone, we empower them to access job opportunities and connect with one another — no screens required.


---

2. Innovation

No apps. No typing. Just talk.
Our platform uses AI to understand farmers and laborers through simple voice calls, and connects them automatically — without the need for smartphones, literacy, or internet.


---

3. Technology

We’ve integrated Dwani AI for speech recognition and text-to-speech in local languages, enabling a 100% voice-driven experience — from job requests to hiring confirmations.


---

4. Scalability

Designed for India’s rural landscape:

Supports all regional languages

Works on any basic phone

Requires zero digital literacy
Ready to scale across villages nationwide.



---

5. Social Impact

This isn’t just a technical project — it’s a socioeconomic bridge.
We connect labor to livelihood, voice to value, and people to possibility — uplifting rural economies and giving the underserved a digital voice.


---

6. Value Proposition

Think Uber, but for rural work.
We connect farmers and laborers — not through an app, but with a simple phone call.


---

How to Run This Project

Step 1: Android Device Setup

Use an Android phone.

Enable Developer Options and USB Debugging.

Connect your phone via USB or set up Wireless Debugging.


To verify connection:

adb devices

For wireless pairing:

adb pair <device_ip>:<pairing_port>
adb connect <device_ip>:<connection_port>


---

Step 2: Install Python Dependencies

Open the ai.py file.

Install required libraries listed in the script:


pip install -r requirements.txt


---

Step 3: Local Language Model (LLM) Setup

Install LM Studio.

Download the Gemma 1B model (or a larger one if your system supports it).

Start the LLM server on port 1234.



---

Step 4: Run the AI Backend

python ai.py


---

Step 5: Database Setup

Open MySQL.

Create two databases:

dbauth

dblabors


Set up the necessary tables for farmers and laborers.



---

Step 6: Run the Frontend

Place the frontend folder in your Apache server’s htdocs directory.

Set the landing page (index.html or home.html) as the home page.



---

Step 7: Explore the Platform

Open the landing page in your browser.

Create an account and log in.

Navigate to the dashboard to access full features.
