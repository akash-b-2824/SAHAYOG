from flask import Flask, request, jsonify
from search import search_laborers

app = Flask(__name__)

@app.route("/search", methods=["GET"])
def search():
    skill = request.args.get("skill")
    gender_preference = request.args.get("gender")  # Optional query parameter for gender preference

    if not skill:
        return jsonify({"error": "Skill is required"}), 400

    laborers = search_laborers(skill, gender_preference)
    
    if not laborers:
        return jsonify({"message": "No laborers found for the given skill and preference"}), 404

    return jsonify({"laborers": laborers})

if __name__ == "__main__":
    app.run(debug=True)
