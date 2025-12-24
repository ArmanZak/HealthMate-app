import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="HealthMeta", page_icon="🧬", layout="wide")

# --- 1. DIRECT API CONNECTION (The "Fail-Safe") ---
def get_gemini_response(api_key, prompt):
    """
    Sends a direct web request to Google. 
    Bypasses library version issues completely.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if the key is wrong
        if response.status_code == 400:
            return None, "🚨 API Key Invalid. Check your key."
        
        # Check if the model is having issues
        if response.status_code != 200:
            return None, f"🚨 Google Error ({response.status_code}): {response.text}"
            
        return response.json(), "Success"
    except Exception as e:
        return None, f"🚨 Connection Error: {str(e)}"

# --- 2. LOGIC FUNCTIONS ---
def calculate_health_score(bmi, steps, sleep, hr):
    score = 80
    if steps > 10000: score += 10
    elif steps < 5000: score -= 10
    if 7 <= sleep <= 9: score += 10
    elif sleep < 6: score -= 10
    if 18.5 <= bmi <= 25: score += 5
    else: score -= 5
    return int(max(0, min(score, 100)))

def get_user_history():
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    data = {
        "Date": list(reversed(dates)),
        "Calories": [2100, 2300, 1950, 2200, 2400, 2150, 2000],
        "Weight (kg)": [70.5, 70.4, 70.3, 70.2, 70.1, 70.0, 69.8]
    }
    return pd.DataFrame(data)

# --- 3. UI & APP STRUCTURE ---
st.title("🧬 HealthMeta")
st.subheader("Your Real-Time AI Health Partner")

# SIDEBAR
with st.sidebar:
    st.header("🔑 API Setup")
    
    # TRIPLE CHECK: Try finding the key in Secrets, or let user paste it
    default_key = ""
    if "GOOGLE_API_KEY" in st.secrets:
        default_key = st.secrets["GOOGLE_API_KEY"]
    
    api_key = st.text_input("Google API Key", value=default_key, type="password")
    if not api_key:
        st.warning("⚠️ Paste your API Key here to start.")

    st.markdown("---")
    st.header("Your Profile")
    name = st.text_input("Name", "User")
    age = st.slider("Age", 10, 100, 25)
    gender = st.radio("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 175)
    veg_nonveg = st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintain"])
    
    st.markdown("---")
    steps = st.number_input("Steps Today", 0, 50000, 6000)
    sleep = st.number_input("Sleep (Hours)", 0, 24, 7)
    
    run_ai = st.button("Run AI Analysis 🚀")

# MAIN PAGE LOGIC
if run_ai:
    if not api_key:
        st.error("❌ Please enter an API Key in the sidebar.")
        st.stop()

    # Metrics
    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 2)
    score = calculate_health_score(bmi, steps, sleep, 72)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BMI", f"{bmi}")
    c2.metric("Health Score", f"{score}/100")
    c3.metric("Steps", steps)
    c4.metric("Sleep", f"{sleep}h")

    # Graph
    st.markdown("### 📈 Your Progress")
    df_hist = get_user_history()
    st.line_chart(df_hist.set_index("Date")[["Weight (kg)", "Calories"]])

    # AI Section
    st.markdown("---")
    t1, t2 = st.tabs(["🥗 AI Diet Plan", "💪 AI Workout Plan"])

    # DIET TAB
    with t1:
        with st.spinner("Talking to Google..."):
            prompt_diet = f"""
            Act as a nutritionist. Create a daily diet for: {age}y, {gender}, {weight}kg, Goal: {goal}, Diet: {veg_nonveg}.
            Return ONLY a JSON array: [{{"Meal": "...", "Option A": "...", "Option B": "...", "Calories": 0}}]
            Do not use markdown blocks. Just the JSON string.
            """
            
            raw_data, msg = get_gemini_response(api_key, prompt_diet)
            
            if raw_data:
                try:
                    # Parse the nested JSON response from Google
                    text_content = raw_data['candidates'][0]['content']['parts'][0]['text']
                    clean_json = text_content.replace("```json", "").replace("```", "").strip()
                    diet_data = json.loads(clean_json)
                    st.success("✅ AI Diet Generated!")
                    st.table(pd.DataFrame(diet_data))
                except Exception as e:
                    st.error(f"Failed to parse AI response: {e}")
                    st.write("Raw Output:", raw_data)
            else:
                st.error(msg)

    # WORKOUT TAB
    with t2:
        with st.spinner("Building Workout..."):
            prompt_workout = f"""
            Act as a trainer. Create a weekly workout for: {gender}, {goal}.
            Return ONLY a JSON array: [{{"Day": "...", "Focus Area": "...", "Exercises": "..."}}]
            Do not use markdown blocks.
            """
            
            raw_data, msg = get_gemini_response(api_key, prompt_workout)
            
            if raw_data:
                try:
                    text_content = raw_data['candidates'][0]['content']['parts'][0]['text']
                    clean_json = text_content.replace("```json", "").replace("```", "").strip()
                    workout_data = json.loads(clean_json)
                    st.table(pd.DataFrame(workout_data))
                except:
                    st.error("Could not read workout data.")
            else:
                st.error(msg)
