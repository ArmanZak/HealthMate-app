import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from health_engine import generate_smart_diet, generate_workout_plan, get_user_history, calculated_health_score
st.set_page_config(page_title="HealthMeta AI", layout="wide", page_icon="🧬")

st.title("🧬 HealthMeta")
st.markdown("### Your Real-Time AI Health Partner")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("👤 Your Profile")
    name = st.text_input("Name", "User")
    age = st.number_input("Age", 10, 100, 24)
    gender = st.selectbox("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30, 150, 70)
    height = st.number_input("Height (cm)", 120, 220, 175)
    
    st.divider()
    st.header("❤️ Vitals")
    steps = st.slider("Daily Steps", 0, 25000, 6000)
    sleep = st.slider("Sleep (Hours)", 0, 12, 7)
    hr = st.number_input("Resting Heart Rate", 40, 120, 72)
    
    run_btn = st.button("🚀 Run AI Analysis", type="primary")

# --- SESSION STATE INITIALIZATION (Memory) ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'diet_df' not in st.session_state:
    st.session_state.diet_df = None

# --- LOGIC ENGINE ---
if run_btn:
    # 1. Calculate Basics
    bmi = round(weight / ((height/100)**2), 2)
    score = calculate_health_score(bmi, steps, sleep, hr)
    risk_label, risk_prob = predict_future_risk(bmi, age, score)
    
    # 2. Get AI Diet & Workout
    diet_df, diet_goal, cal_mod = generate_smart_diet(bmi, age, gender, weight)
    workout_df, workout_focus = generate_weekly_plan(score, bmi)
    
    # 3. Save to History
    save_user_data(name, age, gender, score)
    rank, total, all_scores = get_ranking_data(score)
    
    # 4. Save to Session State (So it remembers!)
    st.session_state.processed = True
    st.session_state.bmi = bmi
    st.session_state.score = score
    st.session_state.risk_label = risk_label
    st.session_state.risk_prob = risk_prob
    st.session_state.diet_df = diet_df
    st.session_state.diet_goal = diet_goal
    st.session_state.workout_df = workout_df
    st.session_state.workout_focus = workout_focus
    st.session_state.rank = rank
    st.session_state.total = total
    st.session_state.all_scores = all_scores
    st.session_state.calories = int((10*weight + 6.25*height - 5*age + 5) * 1.2) + cal_mod

# --- TABS DISPLAY ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🥗 AI Diet", "💪 Workout", "📜 History"])

# TAB 1: DASHBOARD
with tab1:
    if st.session_state.processed:
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Health Score", f"{st.session_state.score}/100")
        c2.metric("BMI", st.session_state.bmi)
        c3.metric("Global Rank", f"#{st.session_state.rank} / {st.session_state.total}")
        c4.metric("Risk Assessment", st.session_state.risk_label, f"{st.session_state.risk_prob}%")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Standing")
            fig, ax = plt.subplots(figsize=(6,3))
            sns.kdeplot(st.session_state.all_scores, fill=True, color="#4A90E2")
            plt.axvline(st.session_state.score, color="red", linestyle="--", label="You")
            plt.legend()
            st.pyplot(fig)
        with col2:
            st.subheader("AI Insight")
            if st.session_state.score > 75:
                st.success("Analysis: You are in peak condition. Maintain your activity levels.")
            elif st.session_state.score > 50:
                st.warning("Analysis: Average health. Improving sleep and steps will boost your score.")
            else:
                st.error("Analysis: Immediate attention needed. High risk factors detected.")
    else:
        st.info("👈 Enter details on the left and click 'Run AI Analysis'")

# TAB 2: DIET
with tab2:
    if st.session_state.processed:
        st.subheader(f"Strategy: {st.session_state.diet_goal}")
        st.info(f"Daily Target: {st.session_state.calories} Calories")
        st.table(st.session_state.diet_df)
    else:
        st.warning("Please Run Analysis first.")

# TAB 3: WORKOUT
with tab3:
    if st.session_state.processed:
        st.subheader(f"Focus: {st.session_state.workout_focus}")
        st.dataframe(st.session_state.workout_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Please Run Analysis first.")

# TAB 4: HISTORY
with tab4:
    st.header(f"History for: {name}")
    hist_df = get_user_history(name)
    if hist_df is not None:
        st.dataframe(hist_df)
    else:

        st.write("No previous records found.")

