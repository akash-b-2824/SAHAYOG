import random
import mysql.connector
from faker import Faker

fake = Faker()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # your XAMPP MySQL password
    database="labor_db"
)
cursor = conn.cursor()

skill_pool = [
    "digging", "watering", "harvesting",
    "tractor driving", "irrigation management", "crop monitoring",
    "pesticide application", "soil testing", "disease detection"
]

genders = ["Male", "Female", "Other"]
languages = ["Hindi", "English", "Marathi", "Telugu", "Tamil"]

for _ in range(1000):
    name = fake.name()
    adhar = str(random.randint(100000000000, 999999999999))  # 12-digit
    phone = fake.phone_number()
    skills = ";".join(random.sample(skill_pool, random.randint(1, 4)))
    age = random.randint(18, 60)
    gender = random.choice(genders)
    language = random.choice(languages)
    latitude = round(random.uniform(20.0, 23.0), 6)   # some location range
    longitude = round(random.uniform(77.0, 80.0), 6)
    available = random.choice([0, 1])
    rating = round(random.uniform(1, 5), 2)
    experience = random.randint(0, 15)

    cursor.execute("""
        INSERT INTO laborers 
        (name, adhar, phone, skills, age, gender, language, latitude, longitude, available, rating, experience)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, adhar, phone, skills, age, gender, language, latitude, longitude, available, rating, experience))

conn.commit()
print("Inserted 1000 dummy laborers.")
cursor.close()
conn.close()
