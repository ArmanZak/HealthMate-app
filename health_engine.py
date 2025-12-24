import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# ==========================================
# 1. SECURE CONFIGURATION
# ==========================================
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("🚨 Missing API Key. Please add GOOGLE_API_KEY to Streamlit Secrets.")
except Exception as e:
    st.error(f"Configuration Error: {e}")

# ==========================================
# HELPER: ROBUST MODEL FETCHER
# ==========================================
def get_model_response(prompt):
    """
    Tries multiple model versions to ensure it never fails with a 404.
    """
    # List of models to try in order of preference
    models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-pro']
    
    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            continue # Try the next model
    
    # If all fail, raise the last error
    raise last_error

# ==========================================
# 2. HEALTH SCORE
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
# 3. HISTORY TRACKER
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
# 4. AI DIET GENERATOR
# ==========================================
def generate_smart_diet(name, age, gender, weight, height, veg_nonveg, goal, activity):
    if gender == "Male": bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else: bmr = 10 * weight + 6.25 * height - 5 * age - 161
    tdee = bmr * 1.2
    target_calories = int(tdee - 500) if goal == "Weight Loss" else int(tdee)

    prompt = f"""
    Act as a nutritionist. Create a daily diet for: {age}y, {gender}, {weight}kg.
    Preference: {veg_nonveg}. Goal: {goal}. Calories: {target_calories}.
    Return ONLY a JSON array with keys: "Meal", "Option A", "Option B", "Calories".
    Do not use markdown.
    Example: [{{"Meal": "Breakfast", "Option A": "Oats", "Option B": "Eggs", "Calories": 300}}]
    """
    
    try:
        # Use our new fail-safe function
        raw_text = get_model_response(prompt)
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return pd.DataFrame(data), f"✅ Success! ({target_calories} kcal)", target_calories
    except Exception as e:
        return pd.DataFrame(), f"AI Error: {str(e)}", 0

# ==========================================
# 5. AI WORKOUT GENERATOR
# ==========================================
def generate_workout_plan(name, age, gender, weight, height, goal):
    prompt = f"""
    Act as a trainer. Create a weekly workout for: {gender}, {goal}.
    Return ONLY a JSON array with keys: "Day", "Focus Area", "Exercises".
    Do not use markdown.
    Example: [{{"Day": "Mon", "Focus Area": "Chest", "Exercises": "Pushups 3x10"}}]
    """
    try:
        # Use our new fail-safe function
        raw_text = get_model_response(prompt)
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame({"Day": ["Error"], "Focus Area": ["Connection Failed"], "Exercises": [str(e)]})
