import streamlit as st
from health_engine import *

st.set_page_config("HealthMate AI","🧬",layout="wide")
init_db()

# =========================
# HEADER
# =========================
st.markdown(
    "<h1 style='text-align:center;'>🧬 HealthMate AI</h1>",
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("👤 User Profile")
    name = st.text_input("Your Name", "User")
    age = st.slider("Age",10,100,25)
    gender = st.radio("Gender",["Male","Female"])
    weight = st.number_input("Weight (kg)",30,200,70)
    height = st.number_input("Height (cm)",100,250,175)
    goal = st.selectbox("Goal",["Lose Weight","Gain Weight","Bulking"])

    st.markdown("---")
    st.header("📊 Daily Lifestyle")
    steps = st.number_input("Steps Today",0,50000,6000)
    sleep = st.number_input("Sleep (hours)",0.0,24.0,7.0)

    run = st.button("🚀 Run Analysis")

# =========================
# MAIN
# =========================
if run:
    bmi = calculate_bmi(weight,height)
    score = health_score(bmi,steps,sleep)
    risk = risk_level(score)
    attention = attention_needed(bmi,steps,sleep)
    progress = goal_progress(bmi,goal)

    save_history(name,weight,bmi,score,steps,sleep,goal)

    st.subheader(f"📌 Health Overview for {name}")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("BMI",bmi)
    c2.metric("Target BMI",target_bmi(goal))
    c3.metric("Health Score",f"{score}/100")
    c4.metric("Risk Level",risk)

    st.markdown("### 🎯 Goal Progress")
    st.progress(progress)
    st.caption(f"You are **{progress}%** towards your goal")

    if attention:
        st.warning("⚠ Attention Needed: " + ", ".join(attention))
    else:
        st.success("✅ No immediate health risks detected")

    # ================= HISTORY =================
    st.markdown("### 📈 Progress History")

    hist = load_history(name)
    if not hist.empty:
        st.line_chart(hist.set_index("date")[["weight","bmi","score"]])
        st.markdown("### 📋 History Table")
        st.dataframe(hist, use_container_width=True)
    else:
        st.info("No history yet. Start tracking daily!")

    # ================= PLANS =================
    st.markdown("### 🧠 Personalized Plans")

    t1,t2 = st.tabs(["🥗 Nutrition Plan","💪 Workout Plan"])

    with t1:
        st.table(backup_diet(goal))

    with t2:
        st.table(backup_workout(goal))
