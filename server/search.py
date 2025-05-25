import pandas as pd
from skill_classifier import classify_skill  # Assuming you have skill_classifier.py to classify skills

# Load the CSV data into a DataFrame
def load_data():
    # Read data from the CSV file
    df = pd.read_csv('server/data.csv')  # Adjust the path if necessary
    return df

def search_laborers(skill, gender_preference=None):
    # Load the data
    df = load_data()

    # Classify the skill and get gender (male, female, both)
    gender = classify_skill(skill)

    if gender_preference and gender_preference != gender:
        return []  # If gender preference doesn't match, return empty

    # Filter the data based on skill
    filtered_data = df[df['skill'] == skill]

    # Further filter the data based on gender preference if provided
    if gender_preference:
        filtered_data = filtered_data[filtered_data['gender'] == gender_preference]

    # Convert filtered data to a list of dictionaries for the response
    laborers = filtered_data.to_dict(orient='records')

    return laborers
