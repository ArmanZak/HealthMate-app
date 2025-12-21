# 🧬 HealthMeta AI v3.0

HealthMeta AI is an intelligent health & fitness dashboard that uses **Google Gemini AI** to generate personalized workout schedules and nutrition plans based on user biometrics.

## 🚀 Features
* **AI-Powered Diet:** Generates specific meal plans (Veg/Non-Veg) based on BMI and goals using Google Gemini 1.5.
* **Smart Workout Engine:** Customizes training schedules (Fat Loss vs. Muscle Gain).
* **Health Score Algorithm:** Calculates a 0-100 health score based on steps, sleep, and heart rate.
* **Future Risk Prediction:** Estimates the probability of metabolic syndrome risks.
* **Progress Tracking:** Saves user history to track improvements over time.

## 🛠️ Installation & Setup (VS Code)

1.  **Clone or Download** this repository.
2.  **Install Dependencies:**
    Open your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set Up API Key:**
    * Get your FREE API Key from [Google AI Studio](https://aistudio.google.com/).
    * Create a file named `.streamlit/secrets.toml` (optional for local) OR paste the key into `health_engine.py` temporarily for testing.

## ▶️ How to Run
Run the application using Streamlit:
```bash
python -m streamlit run app.py