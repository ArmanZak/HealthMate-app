import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# ==========================================
# 🚨 DIRECT KEY CONFIGURATION (Emergency Fix)
# ==========================================
# We are putting the key directly here to ensure it works.
API_KEY = "AIzaSyAx_cobNaiKZKOzgCxdQFHhxec-6WvNQ-Q"

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"CRITICAL API ERROR: {e}")

# ==========================================
# 1. HEALTH SCORE CALCULATION
# ==========================================
def calculate_health_score(bmi, steps, sleep, heart_rate):
    score = 80
    if steps > 10000: score += 10
    elif steps < 5000: score -= 10
    if 7 <= sleep <= 9: score += 10
    elif sleep < 6: score -= 10
    if 18.5 <= bmi <= 25: score += 5
    else: score -= 5
    return int(max(0, min(score, 100)))

# ==========================================
# 2. HISTORY TRACKER (Data for the Graph)
# ==========================================
def get_user_history(name):
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    data = {
        "Date": list(reversed(dates)),
        "Calories": [2100, 2300, 1950, 2200, 2400, 2150, 2000],
        "Weight (kg)": [70.5, 70.4, 70.3, 70.2, 70.1, 70.0, 69.8]
    }
    return pd.DataFrame(data)

# ==========================================
# 3. AI DIET GENERATOR
# ==========================================
def generate_smart_diet(name, age, gender, weight, height, veg_nonveg, goal, activity):
    # Quick Math
    if gender == "Male": bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else: bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    tdee = bmr * 1.2 # simplified activity
    target_calories = int(tdee - 500) if goal == "Weight Loss" else int(tdee)

    # Prompt
    prompt = f"""
    Create a daily diet for: {age}y, {gender}, {weight}kg.
    Preference: {veg_nonveg}. Goal: {goal}. Calories: {target_calories}.
    Return ONLY a JSON array: [{{"Meal": "...", "Option A": "...", "Option B": "...", "Calories": 0}}]
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return pd.DataFrame(data), f"✅ Success! ({target_calories} kcal)", target_calories
    except Exception as e:
        # If this fails, it prints the EXACT error causing the issue
        return pd.DataFrame(), f"AI DIET FAILED: {str(e)}", 0

# ==========================================
# 4. AI WORKOUT GENERATOR
# ==========================================
def generate_workout_plan(name, age, gender, weight, height, goal):
    prompt = f"""
    Create a weekly workout for: {gender}, {goal}.
    Return ONLY a JSON array: [{{"Day": "...", "Focus Area": "...", "Exercises": "..."}}]
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame({"Day": ["Error"], "Focus Area": ["Connection Failed"], "Exercises": [str(e)]})
