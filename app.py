import streamlit as st
import pandas as pd
from health_engine import generate_smart_diet, generate_workout_plan, get_user_history, calculate_health_score

st.set_page_config(page_title="HealthMeta", page_icon="🧬", layout="wide")

st.title("🧬 HealthMeta")
st.subheader("Your Real-Time AI Health Partner")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Your Profile")
    name = st.text_input("Name", "User")
    age = st.slider("Age", 10, 100, 25)
    gender = st.radio("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 175)
    veg_nonveg = st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintain"])
    activity = st.selectbox("Activity Level", ["Sedentary", "Active", "Very Active"])
    
    st.markdown("---")
    steps = st.number_input("Steps Today", 0, 50000, 6000)
    sleep = st.number_input("Sleep (Hours)", 0, 24, 7)
    hr = st.number_input("Heart Rate", 40, 200, 72)
    
    run_ai = st.button("Run AI Analysis 🚀")

# --- MAIN PAGE ---
if run_ai:
    # 1. Metrics
    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 2)
    score = calculate_health_score(bmi, steps, sleep, hr)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BMI", f"{bmi}")
    col2.metric("Health Score", f"{score}/100")
    col3.metric("Steps", steps)
    col4.metric("Sleep", f"{sleep}h")
    
    # 2. THE GRAPH (Restored here!)
    st.markdown("### 📈 Your Progress")
    hist_df = get_user_history(name)
    st.line_chart(hist_df.set_index("Date")[["Weight (kg)", "Calories"]])

    # 3. AI Results
    st.markdown("---")
    tab1, tab2 = st.tabs(["🥗 AI Diet Plan", "💪 AI Workout Plan"])
    
    with tab1:
        with st.spinner("Talking to Google AI..."):
            df_diet, msg, cals = generate_smart_diet(name, age, gender, weight, height, veg_nonveg, goal, activity)
            if "FAILED" in msg:
                st.error(msg)  # This will show us the EXACT error if it fails
            else:
                st.success(msg)
                st.table(df_diet)
            
    with tab2:
        with st.spinner("Building Workout..."):
            df_workout = generate_workout_plan(name, age, gender, weight, height, goal)
            st.table(df_workout)

else:
    st.info("👈 Click 'Run AI Analysis' to generate your dashboard.")
