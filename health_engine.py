import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# 1. CONFIGURE AI KEY
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        pass
except Exception as e:
    st.error(f"API Key Error: {e}")

# ==========================================
# PART 1: HEALTH SCORE CALCULATION
# ==========================================
def calculate_health_score(bmi, steps, sleep, heart_rate):
    """
    Calculates a simple health score (0-100)
    """
    score = 80 # Base score
    
    # Steps Adjustment
    if steps > 10000: score += 10
    elif steps < 5000: score -= 10
    
    # Sleep Adjustment
    if 7 <= sleep <= 9: score += 10
    elif sleep < 6: score -= 10
    
    # BMI Adjustment
    if 18.5 <= bmi <= 25: score += 5
    else: score -= 5
    
    # Ensure 0-100 range
    return int(max(0, min(score, 100)))

# ==========================================
# PART 2: HISTORY TRACKER
# ==========================================
def get_user_history(name):
    """
    Generates dummy history data so the graph doesn't crash.
    """
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    data = {
        "Date": list(reversed(dates)),
        "Calories": [2100, 2300, 1950, 2200, 2400, 2150, 2000],
        "Weight (kg)": [70.5, 70.4, 70.3, 70.2, 70.1, 70.0, 69.8]
    }
    return pd.DataFrame(data)

# ==========================================
# PART 3: AI DIET GENERATOR
# ==========================================
def generate_smart_diet(name, age, gender, weight, height, veg_nonveg, goal, activity):
    # Math for Calories
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multipliers = {
        "Sedentary (Little/no exercise)": 1.2,
        "Lightly active": 1.375,
        "Moderately active": 1.55,
        "Very active": 1.725
    }
    tdee = bmr * activity_multipliers.get(activity, 1.2)

    if goal == "Weight Loss":
        target_calories = int(tdee - 500)
    elif goal == "Muscle Gain":
        target_calories = int(tdee + 400)
    else:
        target_calories = int(tdee)

    # AI Prompt
    prompt = f"""
    Act as a professional nutritionist. Create a daily diet plan for:
    - Profile: {age}y, {gender}, {weight}kg, {height}cm
    - Diet Preference: {veg_nonveg}
    - Goal: {goal}
    - Target Calories: {target_calories} kcal
    
    Return ONLY a valid JSON array with exactly these keys: "Meal", "Option A ({veg_nonveg})", "Option B (Alternative)", "Calories".
    Do not add any markdown formatting like ```json.
    
    Example format:
    [
        {{"Meal": "Breakfast", "Option A (Veg)": "Oatmeal", "Option B (Non-Veg)": "Eggs", "Calories": 350}}
    ]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        return pd.DataFrame(data), f"✅ AI Custom Diet Generated ({target_calories} kcal)", target_calories

    except Exception as e:
        return pd.DataFrame({
            "Meal": ["Error", "Error"],
            "Option A": ["System Error", "Check Secrets"],
            "Option B": ["System Error", "Check Secrets"],
            "Calories": [0, 0]
        }), f"❌ AI DIET FAILED: {str(e)}", 0

# ==========================================
# PART 4: AI WORKOUT GENERATOR
# ==========================================
def generate_workout_plan(name, age, gender, weight, height, goal):
    prompt = f"""
    Act as a fitness trainer. Create a weekly workout schedule for:
    - {gender}, {age} years old, {weight}kg
    - Goal: {goal}
    
    Return ONLY a valid JSON array with keys: "Day", "Focus Area", "Exercises".
    Do not add any markdown formatting like ```json.
    
    Example format:
    [
        {{"Day": "Mon", "Focus Area": "Chest", "Exercises": "Pushups 3x12"}}
    ]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        return pd.DataFrame(data)

    except Exception as e:
        return pd.DataFrame({
            "Day": ["Error"], 
            "Focus Area": ["AI Connection Failed"], 
            "Exercises": [f"Error: {str(e)}"]
        })
