import mysql.connector
import pandas as pd
from math import radians
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import haversine_distances
from joblib import dump, load
import os
import random
from sklearn.metrics import accuracy_score
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

y=main(job_lat, job_lon,job_skills,job_gender,job_age)
for i in y:
    print(i)
for index, row in y.iterrows():
    print(f"Index: {index}, phone: {row['Phone']},name: {row['Name']}")
    import subprocess; subprocess.run(["python", "ai.py", str(row['Phone'])])