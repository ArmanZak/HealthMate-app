import streamlit as st
from health_engine import *

st.set_page_config("HealthMate AI","🧬",layout="wide")

st.title("🧬 HealthMate AI")
st.subheader("Offline-First Personal Health Dashboard")

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("👤 Personal Profile")
    age = st.slider("Age",10,100,25)
    gender = st.radio("Gender",["Male","Female"])
    weight = st.number_input("Weight (kg)",30,200,70)
    height = st.number_input("Height (cm)",100,250,175)
    goal = st.selectbox("Goal",["Lose Weight","Gain Weight","Bulking"])
    st.markdown("---")
    steps = st.number_input("Steps Today",0,50000,6000)
    sleep = st.number_input("Sleep (hours)",0,24,7)
    run = st.button("Run Analysis 🚀")

# =========================
# MAIN DASHBOARD
# =========================
if run:
    bmi = calculate_bmi(weight,height)
    score = health_score(bmi,steps,sleep)
    risk = risk_level(score)
    attention = attention_needed(bmi,steps,sleep)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("BMI",bmi)
    c2.metric("Target BMI",target_bmi(goal))
    c3.metric("Health Score",score)
    c4.metric("Risk",risk)

    if attention:
        st.warning("⚠ Attention Needed: " + ", ".join(attention))
    else:
        st.success("✅ No immediate health risks detected")

    st.markdown("### 📈 Progress History")
    hist = get_history()
    st.line_chart(hist.set_index("Date"))

    t1,t2 = st.tabs(["🥗 Nutrition Plan","💪 Workout Plan"])

    with t1:
        if ollama_available():
            st.info("Using Offline AI (Ollama)")
            st.table(ai_diet(age,gender,weight,height,goal))
        else:
            st.info("Using Backup Nutrition Plan")
            st.table(backup_diet(goal))

    with t2:
        if ollama_available():
            st.info("Using Offline AI (Ollama)")
            st.table(ai_workout(gender,goal))
        else:
            st.info("Using Backup Workout Plan")
            st.table(backup_workout(goal))
