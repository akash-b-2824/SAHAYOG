import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import haversine_distances
from math import radians

# ----------------------------
# Step 1: Generate dummy dataset
# ----------------------------

np.random.seed(42)

names = [f"Worker_{i}" for i in range(100)]
adhars = [f"{np.random.randint(10000, 99999)}" for _ in range(100)]
phones = [f"{np.random.randint(6000, 99999)}" for _ in range(100)]
genders = np.random.choice(["Male", "Female"], size=100)
languages = np.random.choice(["Hindi", "English", "Bengali", "Telugu", "Marathi"], size=100)
ages = np.random.randint(18, 60, size=100)

# Skill pyramid: Level 1 (basic), 2 (intermediate), 3 (advanced)
skill_pool = {
    1: ["digging", "watering", "harvesting"],
    2: ["tractor driving", "irrigation management", "crop monitoring"],
    3: ["pesticide application", "soil testing", "disease detection"]
}

def generate_skills():
    skill_list = []
    for level in range(1, 4):
        skill_list += np.random.choice(skill_pool[level], size=np.random.randint(1, 3)).tolist()
    return ";".join(skill_list)

skills = [generate_skills() for _ in range(100)]

# Generate latitude and longitude around a fixed location (say central India)
latitudes = np.random.uniform(21.0, 23.0, size=100)
longitudes = np.random.uniform(78.0, 80.0, size=100)

data = pd.DataFrame({
    "name": names,
    "adhar": adhars,
    "phone": phones,
    "skills": skills,
    "age": ages,
    "gender": genders,
    "language": languages,
    "latitude": latitudes,
    "longitude": longitudes
})

# ----------------------------
# Step 2: Recommendation Logic
# ----------------------------

def skill_score(worker_skills, job_skills):
    # Match skill intersection with weights based on pyramid level
    skill_points = 0
    for skill in job_skills:
        for level, group in skill_pool.items():
            if skill in worker_skills and skill in group:
                skill_points += level
    return skill_points

def recommend_labors(job_lat, job_lon, job_skills, job_gender=None, job_age=None):
    job_skills = job_skills.lower().split(';')
    results = []

    for _, row in data.iterrows():
        # 1. Distance Score
        loc1 = [radians(job_lat), radians(job_lon)]
        loc2 = [radians(row.latitude), radians(row.longitude)]
        distance_km = haversine_distances([loc1, loc2])[1][0] * 6371  # Earth's radius
        location_score = 1 / (1 + distance_km)  # Closer = higher score

        # 2. Skill Match Score
        worker_skills = row.skills.lower().split(";")
        skillmatch_score = skill_score(worker_skills, job_skills) / 10  # Normalize

        # 3. Gender Match
        gender_score = 1 if row.gender.lower() == job_gender.lower() else 0

        # 4. Age Proximity Score
        age_score = 1 - abs(row.age - job_age) / 50  # 50-year span

        # Total weighted score
        total_score = (0.4 * location_score +
                       0.3 * skillmatch_score +
                       0.2 * gender_score +
                       0.1 * age_score)

        results.append((row.name, row.phone, total_score))

    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    print(sorted_results)
    return pd.DataFrame(sorted_results[:10], columns=["Name", "Phone", "Score"])

# ----------------------------
# Step 3: Use the recommender
# ----------------------------

# Example Job input
job_lat = 22.5
job_lon = 79.0
job_skills = "soil testing"
job_gender = "Female"
job_age = 30

recommendations = recommend_labors(job_lat, job_lon, job_skills, job_gender, job_age)
print(recommendations)
