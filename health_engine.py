import requests
import pandas as pd
import json
import sqlite3
import os
from datetime import datetime

DB_PATH = "health_history.db"

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            date TEXT,
            name TEXT,
            weight REAL,
            bmi REAL,
            score INTEGER,
            steps INTEGER,
            sleep REAL,
            goal TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_history(name, weight, bmi, score, steps, sleep, goal):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history VALUES (?,?,?,?,?,?,?,?)",
        (
            datetime.now().strftime("%Y-%m-%d"),
            name,
            weight,
            bmi,
            score,
            steps,
            sleep,
            goal
        )
    )
    conn.commit()
    conn.close()

def load_history(name):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT * FROM history WHERE name=? ORDER BY date",
        conn,
        params=(name,)
    )
    conn.close()
    return df

# =========================
# OLLAMA
# =========================
def ollama_available():
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except:
        return False

def call_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]

# =========================
# HEALTH LOGIC
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

def goal_progress(current_bmi, goal):
    target = target_bmi(goal)
    diff = abs(current_bmi - target)
    max_diff = 10
    progress = max(0, min(100, int((1 - diff / max_diff) * 100)))
    return progress

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
        {"Meal":"Breakfast","Plan":"Protein rich meal","Calories":500},
        {"Meal":"Lunch","Plan":"Rice + protein","Calories":700},
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
