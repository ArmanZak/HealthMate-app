import streamlit as st
import pandas as pd
from health_engine import generate_smart_diet, generate_workout_plan, get_user_history, calculate_health_score

# 1. Page Config
st.set_page_config(page_title="HealthMeta", page_icon="🧬", layout="wide")

# 2. Header
st.title("🧬 HealthMeta")
st.subheader("Your Real-Time AI Health Partner")

# 3. Sidebar Inputs
with st.sidebar:
    st.header("Your Profile")
    name = st.text_input("Name", "User")
    age = st.slider("Age", 10, 100, 25)
    gender = st.radio("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 175)
    veg_nonveg = st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintain"])
    activity = st.selectbox("Activity Level", ["Sedentary (Little/no exercise)", "Lightly active", "Moderately active", "Very active"])
    
    st.markdown("---")
    st.header("Daily Vitals")
    steps = st.number_input("Steps Today", 0, 50000, 6000)
    sleep = st.number_input("Sleep (Hours)", 0, 24, 7)
    hr = st.number_input("Heart Rate", 40, 200, 72)
    
    run_ai = st.button("Run AI Analysis 🚀")

# 4. Main Dashboard Logic
if run_ai:
    # A. Calculate BMI & Score
    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 2)
    score = calculate_health_score(bmi, steps, sleep, hr)

    # B. Show Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BMI", f"{bmi}")
    col2.metric("Health Score", f"{score}/100")
    col3.metric("Steps", steps)
    col4.metric("Sleep", f"{sleep}h")
    
    # C. Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🥗 AI Diet", "💪 AI Workout", "📜 History"])
    
    with tab1:
        st.info(f"Welcome back, {name}! Your health score is {score}/100.")
        if score > 80:
            st.success("Great job! You are maintaining a healthy lifestyle.")
        elif score > 50:
            st.warning("Good, but there is room for improvement.")
        else:
            st.error("Action needed! Let's improve your health score.")
            
    with tab2:
        st.header("AI-Powered Diet Plan")
        with st.spinner("AI is crafting your menu..."):
            df_diet, msg, cals = generate_smart_diet(name, age, gender, weight, height, veg_nonveg, goal, activity)
            if "FAILED" in msg:
                st.error(msg)
            else:
                st.success(msg)
            st.table(df_diet)
            
    with tab3:
        st.header("AI-Powered Workout Plan")
        with st.spinner("AI is designing your workout..."):
            df_workout = generate_workout_plan(name, age, gender, weight, height, goal)
            st.table(df_workout)

    with tab4:
        st.header("Progress History")
        hist_df = get_user_history(name)
        st.line_chart(hist_df.set_index("Date")[["Weight (kg)", "Calories"]])

else:
    st.info("👈 Enter your details on the left and click 'Run AI Analysis'")
