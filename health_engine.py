import requests
import pandas as pd
import json
from datetime import datetime, timedelta

# =========================
# OLLAMA CHECK
# =========================
def ollama_available():
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except:
        return False

def call_ollama(prompt):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    res.raise_for_status()
    return res.json()["response"]

# =========================
# CORE HEALTH LOGIC
# =========================
def calculate_bmi(weight, height_cm):
    h = height_cm / 100
    return round(weight / (h * h), 2)

def target_bmi(goal):
    return {
        "Lose Weight": 22,
        "Gain Weight": 23.5,
        "Bulking": 24.5
    }[goal]

def health_score(bmi, steps, sleep):
    score = 80
    if steps > 10000: score += 10
    if steps < 5000: score -= 10
    if 7 <= sleep <= 9: score += 10
    if sleep < 6: score -= 10
    if 18.5 <= bmi <= 25: score += 5
    else: score -= 5
    return max(0, min(score, 100))

def risk_level(score):
    if score >= 75: return "Low"
    if score >= 50: return "Medium"
    return "High"

def attention_needed(bmi, steps, sleep):
    issues = []
    if sleep < 6: issues.append("Low sleep")
    if steps < 4000: issues.append("Low activity")
    if bmi < 18.5 or bmi > 30: issues.append("Unhealthy BMI")
    return issues

# =========================
# HISTORY (MOCK)
# =========================
def get_history():
    today = datetime.now()
    days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    return pd.DataFrame({
        "Date": list(reversed(days)),
        "Weight": [70.5,70.4,70.3,70.2,70.1,70.0,69.8],
        "Health Score": [72,74,75,76,78,80,82]
    })

# =========================
# BACKUP PLANS
# =========================
def backup_diet(goal):
    if goal == "Lose Weight":
        return pd.DataFrame([
            {"Meal":"Breakfast","Plan":"Oats + fruits","Calories":300},
            {"Meal":"Lunch","Plan":"Dal + rice","Calories":450},
            {"Meal":"Dinner","Plan":"Salad + soup","Calories":350}
        ])
    if goal == "Gain Weight":
        return pd.DataFrame([
            {"Meal":"Breakfast","Plan":"Milk + banana","Calories":450},
            {"Meal":"Lunch","Plan":"Rice + paneer","Calories":650},
            {"Meal":"Dinner","Plan":"Roti + curd","Calories":550}
        ])
    return pd.DataFrame([
        {"Meal":"Breakfast","Plan":"Eggs / Paneer","Calories":500},
        {"Meal":"Lunch","Plan":"Rice + chicken","Calories":700},
        {"Meal":"Dinner","Plan":"Protein bowl","Calories":600}
    ])

def backup_workout(goal):
    if goal == "Lose Weight":
        return pd.DataFrame([
            {"Day":"Mon","Workout":"Cardio + Core"},
            {"Day":"Wed","Workout":"HIIT"},
            {"Day":"Fri","Workout":"Brisk Walk"}
        ])
    if goal == "Gain Weight":
        return pd.DataFrame([
            {"Day":"Mon","Workout":"Upper Body"},
            {"Day":"Wed","Workout":"Lower Body"},
            {"Day":"Fri","Workout":"Full Body"}
        ])
    return pd.DataFrame([
        {"Day":"Mon","Workout":"Chest + Triceps"},
        {"Day":"Tue","Workout":"Back + Biceps"},
        {"Day":"Thu","Workout":"Legs"}
    ])

# =========================
# AI PLANS (OPTIONAL)
# =========================
def ai_diet(age, gender, weight, height, goal):
    prompt = f"""
    Create a one-day diet plan for {age}y {gender}, {weight}kg.
    Goal: {goal}
    Return ONLY JSON list with keys Meal, Plan, Calories.
    """
    text = call_ollama(prompt)
    return pd.DataFrame(json.loads(text))

def ai_workout(gender, goal):
    prompt = f"""
    Create weekly workout for {gender}, goal {goal}.
    Return ONLY JSON list with Day, Workout.
    """
    text = call_ollama(prompt)
    return pd.DataFrame(json.loads(text))
