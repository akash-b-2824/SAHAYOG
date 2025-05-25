import mysql.connector
import random
import string

# -------------------------------
# 1. MySQL DB connection setup
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # default for XAMPP
    database="sads"
)
cursor = conn.cursor()

# -------------------------------
# 2. Skill pyramid for workers
# -------------------------------
skill_pool = {
    1: ["digging", "watering", "harvesting"],
    2: ["tractor driving", "irrigation management", "crop monitoring"],
    3: ["pesticide application", "soil testing", "disease detection"]
}

languages = ["Hindi", "English", "Bengali", "Telugu", "Marathi"]
genders = ["Male", "Female"]

def generate_skills():
    skill_list = []
    for level in range(1, 4):
        skill_list += random.sample(skill_pool[level], random.randint(1, 2))
    return ";".join(skill_list)

# -------------------------------
# 3. Insert 1000 dummy records
# -------------------------------
for i in range(1000):
    name = f"Worker_{i+1}"
    adhar = ''.join(random.choices(string.digits, k=12))
    phone = ''.join(random.choices("6789" + string.digits, k=10))
    skills = generate_skills()
    age = random.randint(18, 60)
    gender = random.choice(genders)
    language = random.choice(languages)
    latitude = round(random.uniform(21.0, 23.0), 6)
    longitude = round(random.uniform(78.0, 80.0), 6)

    query = """
    INSERT INTO laborers (name, adhar, phone, skills, age, gender, language, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (name, adhar, phone, skills, age, gender, language, latitude, longitude)
    
    cursor.execute(query, values)

conn.commit()
print("✅ Inserted 1000 dummy laborer records.")
cursor.close()
conn.close()
