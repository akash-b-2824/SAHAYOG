import mysql.connector
import pandas as pd
from math import radians
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import haversine_distances
from joblib import dump, load
import random

# Connect and fetch data
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="labor_db"
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM laborers")
rows = cursor.fetchall()
data = pd.DataFrame(rows)

# Skill pyramid for scoring
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

# Simulated job
job_lat, job_lon = 22.2, 79.0
job_skills = "soil testing;digging".lower().split(";")
job_gender = "Male"
job_age = 30

X = []
y = []

for _, row in data.iterrows():
    loc1 = [radians(job_lat), radians(job_lon)]
    loc2 = [radians(row['latitude']), radians(row['longitude'])]
    dist_km = haversine_distances([loc1, loc2])[1][0] * 6371
    location_score = 1 / (1 + dist_km)

    worker_skills = row['skills'].lower().split(";")
    skillmatch_score = skill_score(worker_skills, job_skills)

    gender_match = 1 if row['gender'].lower() == job_gender.lower() else 0
    age_diff = abs(row['age'] - job_age)

    available = row['available']
    rating = row['rating']
    experience = row['experience']

    features = [
        location_score,
        skillmatch_score,
        gender_match,
        age_diff,
        available,
        rating,
        experience
    ]
    X.append(features)

    # Simulated target label (replace with real feedback for real app)
    score = (
        0.3 * location_score +
        0.25 * (skillmatch_score / 9) +
        0.15 * gender_match +
        0.1 * (1 - age_diff / 50) +
        0.1 * (rating / 5) +
        0.1 * (experience / 15)
    )
    hired = 1 if score > 0.5 + random.uniform(-0.1, 0.1) else 0
    y.append(hired)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model to disk
dump(model, "labor_recommendation_model.joblib")
print("Model trained and saved.")

# Recommendation function
def recommend_labors_ml(job_lat, job_lon, job_skills, job_gender, job_age):
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

        prob = model.predict_proba(features)[0][1]  # probability of hired
        scores.append((row['name'], row['phone'], prob))

    top_labors = sorted(scores, key=lambda x: x[2], reverse=True)[:10]
    return pd.DataFrame(top_labors, columns=["Name", "Phone", "Hired_Probability"])

# Example usage
recs = recommend_labors_ml(
    job_lat=22.2,
    job_lon=79.0,
    job_skills="soil testing;digging",
    job_gender="Male",
    job_age=30
)

print(recs)
