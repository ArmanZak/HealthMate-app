import streamlit as st
from health_engine import *

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🧬",
    layout="wide"
)

# Initialize DB
init_db()

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
    <h1 style="text-align:center;">🧬 HealthMate AI</h1>
    <p style="text-align:center; color: gray;">
    Your Real-Time Health Partner
    </p>
    """,
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.header("👤 Your Profile")
    name = st.text_input("Name", "User")
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
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "🥗 Nutrition", "💪 Workout", "📜 History"]
)

# =====================================================
# DASHBOARD TAB
# =====================================================
with tab1:
    if run:
        bmi = calculate_bmi(weight, height)
        score = health_score(bmi, steps, sleep)
        risk = risk_level(score)
        attention = attention_needed(bmi, steps, sleep)
        progress = goal_progress(bmi, goal)

        save_history(name, weight, bmi, score, steps, sleep, goal)

        st.subheader(f"📌 Health Overview for {name}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Health Score", f"{score}/100")
        c2.metric("BMI", bmi)
        c3.metric("Target BMI", target_bmi(goal))
        c4.metric("Risk Level", risk)

        st.markdown("### 🎯 Goal Progress")
        st.progress(progress)
        st.caption(f"You are **{progress}%** towards your goal")

        if attention:
            st.warning("⚠ Attention Needed: " + ", ".join(attention))
        else:
            st.success("✅ No immediate health risks detected")
    else:
        st.info("👉 Enter details in sidebar and click **Run Analysis**")

# =====================================================
# NUTRITION TAB
# =====================================================
with tab2:
    if run:
        st.subheader("🥗 Nutrition Plan")

        if ollama_available():
            st.info("Using Offline AI Engine")
            st.table(ai_diet(age, gender, weight, height, goal))
        else:
            st.warning("AI engine not detected. Showing backup nutrition plan.")
            st.table(backup_diet(goal))
    else:
        st.info("Run analysis to generate your nutrition plan.")

# =====================================================
# WORKOUT TAB
# =====================================================
with tab3:
    if run:
        st.subheader("💪 Workout Plan")

        if ollama_available():
            st.info("Using Offline AI Engine")
            st.table(ai_workout(gender, goal))
        else:
            st.warning("AI engine not detected. Showing backup workout plan.")
            st.table(backup_workout(goal))
    else:
        st.info("Run analysis to generate your workout plan.")

# =====================================================
# HISTORY TAB
# =====================================================
with tab4:
    st.subheader("📜 Progress History")

    history_df = load_history(name)

    if not history_df.empty:
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No history available yet. Start tracking daily.")
