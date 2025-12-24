import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# 1. CONFIGURE THE AI KEY
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        pass
except Exception as e:
    print(f"Configuration Error: {e}")

# ==========================================
# PART 1: AI DIET GENERATOR (Your Request)
# ==========================================
def generate_smart_diet(name, age, gender, weight, height, veg_nonveg, goal, activity):
    """
    100% AI-Powered Diet Plan.
    If the API Key works, this ignores static data and asks Google Gemini.
    """
    
    # Calculate Calories (Math logic is better than AI for this part)
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

    # HERE IS THE AI PROMPT FOR DIET
    prompt = f"""
    Act as a professional nutritionist. Create a daily diet plan for:
    - Profile: {age}y, {gender}, {weight}kg, {height}cm
    - Diet Preference: {veg_nonveg}
    - Goal: {goal}
    - Target Calories: {target_calories} kcal
    
    Return ONLY a valid JSON array with exactly these keys: "Meal", "Option A ({veg_nonveg})", "Option B (Alternative)", "Calories".
    Example:
    [
        {{"Meal": "Breakfast", "Option A (Veg)": "Oatmeal", "Option B (Non-Veg)": "Eggs", "Calories": 350}}
    ]
    """

    try:
        # CALLING GOOGLE GEMINI FOR DIET...
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Parse Response
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # SUCCESS! Return AI Data
        return pd.DataFrame(data), f"✅ AI Custom Diet Generated ({target_calories} kcal)", target_calories

    except Exception as e:
        # FAIL! Return Backup Data AND Show Error
        return pd.DataFrame({
            "Meal": ["Error", "Error", "Error"],
            "Option A": ["Check API Key", "Check API Key", "Check API Key"],
            "Option B": ["See Error Below", "See Error Below", "See Error Below"],
            "Calories": [0, 0, 0]
        }), f"❌ AI DIET FAILED: {str(e)}", 0

# ==========================================
# PART 2: AI WORKOUT GENERATOR (Your Request)
# ==========================================
def generate_workout_plan(name, age, gender, weight, height, goal):
    """
    100% AI-Powered Workout Plan.
    """
    
    # HERE IS THE AI PROMPT FOR WORKOUT
    prompt = f"""
    Act as a fitness trainer. Create a weekly workout schedule for:
    - {gender}, {age} years old, {weight}kg
    - Goal: {goal}
    
    Return ONLY a valid JSON array with keys: "Day", "Focus Area", "Exercises".
    Example:
    [
        {{"Day": "Mon", "Focus Area": "Chest", "Exercises": "Pushups 3x12"}}
    ]
    """

    try:
        # CALLING GOOGLE GEMINI FOR WORKOUT...
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        return pd.DataFrame(data)

    except Exception as e:
        # FAIL! Show Error in Table
        return pd.DataFrame({
            "Day": ["Error"], 
            "Focus Area": ["AI Connection Failed"], 
            "Exercises": [str(e)]
        })

# ==========================================
# PART 3: HISTORY TRACKER (This was missing!)
# ==========================================
def get_user_history(name):
    """
    Generates dummy history data so the graph doesn't crash.
    """
    # Create fake dates
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    # Fake history data for demo
    data = {
        "Date": list(reversed(dates)),
        "Calories": [2100, 2300, 1950, 2200, 2400, 2150, 2000],
        "Weight (kg)": [70.5, 70.4, 70.3, 70.2, 70.1, 70.0, 69.8]
    }
    return pd.DataFrame(data)
