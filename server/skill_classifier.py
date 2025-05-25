# skill_classifier.py

# Gender-segregated skills
skills_men = [
    "Plowing (Traditional & Tractor)", "Grain Harvesting", "Combine Harvester Operation",
    "Threshing", "Tractor Operations"
]

skills_women = [
    "Fruit Picking", "Weeding", "Seedling Transplantation", "Nursery Management"
]

skills_neutral = [
    "Drip Irrigation Setup", "Sprinkler Operation", "Small machinery operation"
]

def classify_skill(skill):
    if skill in skills_men:
        return "male"
    elif skill in skills_women:
        return "female"
    elif skill in skills_neutral:
        return "both"
    else:
        return "unknown"
