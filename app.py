import streamlit as st
from health_engine import *

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🧬",
    layout="wide"
)

# Initialize database
init_db()

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
    <h1 style="text-align:center;">🧬 HealthMate AI</h1>
    <p style="text-align:center; color: gray;">
    Offline-First Personal Health Dashboard
    </p>
    """,
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.header("👤 Personal Profile")
    age = st.slider("Age", 10, 100, 25)
    gender = st.radio("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30, 200, 70)
    height = st.number_input("Height (cm)", 100, 250, 175)
    goal = st.selectbox(
        "Goal",
        ["Lose Weight", "Gain Weight", "Bulking"]
    )

    st.markdown("---")
    st.header("📊 Daily Lifestyle")
    steps = st.number_input("Steps Today", 0, 50000, 6000)
    sleep = st.number_input("Sleep (hours)", 0.0, 24.0, 7.0)

    run = st.button("🚀 Run Analysis")

# =====================================================
# MAIN DASHBOARD
# =====================================================
if run:
    bmi = calculate_bmi(weight, height)
    score = health_score(bmi, steps, sleep)
    risk = risk_level(score)
    attention = attention_needed(bmi, steps, sleep)

    # Save daily history
    save_history(weight, bmi, score, steps, sleep, goal)

    # ================= METRICS =================
    st.subheader("📌 Health Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BMI", bmi)
    c2.metric("Target BMI", target_bmi(goal))
    c3.metric("Health Score", f"{score}/100")
    c4.metric("Risk Level", risk)

    if attention:
        st.error("⚠ Attention Needed: " + ", ".join(attention))
    else:
        st.success("✅ No immediate health risks detected")

    # ================= HISTORY =================
    st.markdown("### 📈 Progress History")
    history_df = load_history()

    if not history_df.empty:
        st.line_chart(
            history_df.set_index("date")[["weight", "bmi", "score"]]
        )
    else:
        st.info("No history available yet. Run analysis daily to track progress.")

    # ================= PLANS =================
    st.markdown("### 🧠 Personalized Plans")

    t1, t2 = st.tabs(["🥗 Nutrition Plan", "💪 Workout Plan"])

    with t1:
        if ollama_available():
            st.info("Using Offline AI Engine")
            st.table(ai_diet(age, gender, weight, height, goal))
        else:
            st.warning("AI engine not detected. Showing backup nutrition plan.")
            st.table(backup_diet(goal))

    with t2:
        if ollama_available():
            st.info("Using Offline AI Engine")
            st.table(ai_workout(gender, goal))
        else:
            st.warning("AI engine not detected. Showing backup workout plan.")
            st.table(backup_workout(goal))
