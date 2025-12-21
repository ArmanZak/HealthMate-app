import warnings
# Silence the Google deprecation warning for the demo
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import numpy as np
import os
import google.generativeai as genai
import streamlit as st
from datetime import datetime
import io

# ==========================================
# 🔑 SECURE CONFIGURATION
# ==========================================
# This looks for the key in Streamlit's secure storage
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # This runs if you haven't set up secrets yet (e.g. on your laptop)
    # You can paste your key here for local testing, BUT remove it before uploading to GitHub!
    API_KEY = "" 

# Configure AI
AI_AVAILABLE = False
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        AI_AVAILABLE = True
    except Exception as e:
        print(f"AI Setup Error: {e}")

# ==========================================
# 1. CORE HEALTH MATH
# ==========================================
def calculate_health_score(bmi, steps, sleep, heart_rate):
    score = 0
    # BMI (30%)
    if 18.5 <= bmi <= 24.9: score += 30
    elif 25 <= bmi <= 29.9: score += 20
    else: score += 10
    # Activity (25%)
    if steps > 10000: score += 25
    elif steps > 7000: score += 20
    elif steps > 4000: score += 15
    else: score += 5
    # Sleep (25%)
    if 7 <= sleep <= 9: score += 25
    elif 6 <= sleep < 7: score += 15
    else: score += 5
    # Heart (20%)
    if 50 <= heart_rate <= 70: score += 20
    elif 71 <= heart_rate <= 90: score += 15
    else: score += 10
    return score

def predict_future_risk(bmi, age, score):
    risk_prob = 0
    if bmi > 30: risk_prob += 0.4
    if age > 45: risk_prob += 0.2
    if score < 50: risk_prob += 0.3
    
    risk_label = "Low Risk"
    if risk_prob > 0.6: risk_label = "High Risk"
    elif risk_prob > 0.3: risk_label = "Moderate Risk"
    return risk_label, round(risk_prob * 100, 1)

# ==========================================
# 2. DATABASE (CSV)
# ==========================================
# Note: On Streamlit Cloud, this file will reset periodically. 
# For a permanent DB, we would need Google Sheets (but this is fine for a demo).
DB_FILE = "database.csv"

def save_user_data(name, age, gender, score):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M") 
    new_data = pd.DataFrame([[name, age, gender, score, date_str]], 
                            columns=["Name", "Age", "Gender", "Score", "Date"])
    
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False)
    else:
        new_data.to_csv(DB_FILE, mode='a', header=False, index=False)

def get_user_history(name):
    if not os.path.isfile(DB_FILE): return None
    try:
        df = pd.read_csv(DB_FILE)
        return df[df["Name"].str.lower() == name.lower()]
    except: return None

def get_ranking_data(current_score):
    if os.path.isfile(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            scores = df["Score"].tolist()
        except: scores = []
    else: scores = []
    
    # Fake data if database is empty (for demo)
    if len(scores) < 5: scores.extend(np.random.normal(65, 15, 50).tolist())
    
    scores.append(current_score)
    scores.sort(reverse=True)
    rank = scores.index(current_score) + 1
    return rank, len(scores), scores

# ==========================================
# 3. WORKOUT GENERATOR (Static Logic)
# ==========================================
def generate_weekly_plan(score, bmi):
    # Logic: If overweight, focus on cardio. If healthy, focus on strength.
    if bmi > 25:
        focus = "🔥 Fat Loss & Cardio"
        data = {
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Workout": ["Cardio 30m", "Squats & Lunges", "HIIT 20m", "Core/Abs", "Active Walk", "Full Body", "Rest"],
            "Duration": ["30 min", "40 min", "20 min", "30 min", "60 min", "45 min", "-"],
        }
    elif bmi < 18.5:
        focus = "💪 Muscle Building"
        data = {
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Workout": ["Push (Chest/Tri)", "Pull (Back/Bi)", "Legs (Squats)", "Rest", "Upper Body", "Lower Body", "Rest"],
            "Duration": ["60 min", "60 min", "60 min", "-", "45 min", "45 min", "-"],
        }
    else:
        focus = "⚖️ General Fitness"
        data = {
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Workout": ["Run 5k", "Bodyweight Circuit", "Yoga", "Sprints", "Weights", "Sports", "Rest"],
            "Duration": ["40 min", "30 min", "40 min", "20 min", "45 min", "60 min", "-"],
        }
    return pd.DataFrame(data), focus

# ==========================================
# 4. AI NUTRITION GENERATOR 🧠
# ==========================================
def generate_smart_diet(bmi, age, gender, weight):
    
    # 1. Determine Goal
    if bmi >= 25:
        goal = "Weight Loss"
        cal_mod = -400
    elif bmi < 18.5:
        goal = "Muscle Gain"
        cal_mod = +400
    else:
        goal = "Maintain Weight"
        cal_mod = 0

    # 2. Try Calling AI
    if AI_AVAILABLE:
        try:
            prompt = f"""
            Act as a nutritionist. Create a 1-day menu for a {age}yo {gender}, {weight}kg, Goal: {goal}.
            Output purely CSV data with these columns: Meal, Option A (Veg), Option B (Non-Veg), Calories.
            Rows: Breakfast, Snack 1, Lunch, Snack 2, Dinner.
            Do not include ```csv or markdown tags.
            """
            response = model.generate_content(prompt)
            clean_csv = response.text.replace("```csv", "").replace("```", "").strip()
            df = pd.read_csv(io.StringIO(clean_csv))
            return df, f"AI Plan: {goal}", cal_mod
        except Exception as e:
            print(f"AI Error: {e}")
            # Fall through to backup

    # 3. Backup (If AI fails or no internet)
    backup_data = {
        "Meal": ["Breakfast", "Lunch", "Dinner"],
        "Option A (Veg)": ["Oats + Apple", "Dal + Rice", "Soup + Salad"],
        "Option B (Non-Veg)": ["Eggs + Toast", "Chicken Curry", "Grilled Fish"],
        "Calories": [300, 500, 400]
    }
    return pd.DataFrame(backup_data), "⚠️ Offline Mode (Check API Key)", 0