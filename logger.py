import pandas as pd
from datetime import datetime
import os
import streamlit as st  # Needed to access session_state (username)

def log_interaction(symptoms, recs, feedback, sentiment, log_file=None):
    # Get the current user from session_state
    username = st.session_state.get("username", "guest")

    # If no log_file path is given, use per-user default
    if not log_file:
        log_file = f"data/logs_{username}.csv"

    # Clean up inputs
    feedback_clean = feedback.strip().replace("\n", " ")
    sentiment_clean = sentiment.replace("✅", "Positive").replace("❌", "Negative").replace("➖", "Neutral")

    # Prepare data
    data = {
        "timestamp": [datetime.now().strftime("%d-%m-%Y %H:%M")],
        "user_symptoms": [", ".join(symptoms)],
        "recommendations": [", ".join([r[0] for r in recs])],
        "feedback": [feedback_clean],
        "sentiment": [sentiment_clean]
    }

    df = pd.DataFrame(data)

    # Save log
    if os.path.exists(log_file):
        df.to_csv(log_file, mode='a', header=False, index=False)
    else:
        df.to_csv(log_file, mode='w', header=True, index=False)

