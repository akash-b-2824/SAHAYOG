import mysql.connector
import pandas as pd
from sklearn.metrics.pairwise import haversine_distances
from math import radians

# ---------- Connect to MySQL ----------
conn = mysql.connector.connect(
    host="localhost",
    user="root",         # default XAMPP username
    password="",         # empty by default
    database="sads"
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM laborers")
rows = cursor.fetchall()
data = pd.DataFrame(rows)

# ---------- Define Skill Pyramid ----------
skill_pool = {
    1: ["digging", "watering", "harvesting"],
    2: ["tractor driving", "irrigation management", "crop monitoring"],
    3: ["pesticide application", "soil testing", "disease detection"]
}

def skill_score(worker_skills, job_skills):
    skill_points = 0
    for skill in job_skills:
        for level, group in skill_pool.items():
            if skill in worker_skills and skill in group:
                skill_points += level
    return skill_points

# ---------- Recommendation Logic ----------
def recommend_labors(job_lat, job_lon, job_skills, job_gender=None, job_age=None):
    job_skills = job_skills.lower().split(';')
    results = []

    for _, row in data.iterrows():
        loc1 = [radians(job_lat), radians(job_lon)]
        loc2 = [radians(row.latitude), radians(row.longitude)]
        distance_km = haversine_distances([loc1, loc2])[1][0] * 6371
        location_score = 1 / (1 + distance_km)

        worker_skills = row.skills.lower().split(';')
        skillmatch_score = skill_score(worker_skills, job_skills) / 10

        gender_score = 1 if row.gender.lower() == job_gender.lower() else 0
        age_score = 1 - abs(row.age - job_age) / 50

        total_score = (0.4 * location_score +
                       0.3 * skillmatch_score +
                       0.2 * gender_score +
                       0.1 * age_score)

        results.append((row["name"], row["phone"], total_score))

    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    return pd.DataFrame(sorted_results[:10], columns=["Name", "Phone", "Score"])

# ---------- Example Run ----------
recs = recommend_labors(
    job_lat=22.2,
    job_lon=79.0,
    job_skills="soil testing;digging",
    job_gender="Male",
    job_age=30
)

print(recs)
