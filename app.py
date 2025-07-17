import streamlit as st
import pandas as pd
from recommendation import load_data, recommend_plan
from sentiment import analyze_sentiment
from logger import log_interaction

# ---- CONFIG ----
st.set_page_config(page_title="Healthcare Recommendation System", layout="wide")

# ---- USER DB ----
import pandas as pd
import os

# 📂 Load users from CSV
USERS_FILE = "data/users.csv"
if os.path.exists(USERS_FILE):
    users_df = pd.read_csv(USERS_FILE)
else:
    users_df = pd.DataFrame(columns=["username", "password", "role"])

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""

# Sidebar authentication toggle
auth_mode = st.sidebar.radio("🔐 Choose Action", ["Login", "Register"])

if not st.session_state.authenticated:
    st.subheader("🔐 User Authentication")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Login":
        if st.button("Login"):
            user_row = users_df[users_df["username"] == username]
            if not user_row.empty and user_row.iloc[0]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = user_row.iloc[0]["role"]
                st.success(f"✅ Welcome, {username.title()}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    elif auth_mode == "Register":
        role = st.selectbox("Choose Role", ["user", "admin"])
        if st.button("Register"):
            if username in users_df["username"].values:
                st.warning("🚫 Username already exists.")
            else:
                # Append new user to CSV
                new_user = pd.DataFrame([{
                    "username": username,
                    "password": password,
                    "role": role
                }])
                new_user.to_csv(USERS_FILE, mode="a", header=not os.path.exists(USERS_FILE), index=False)
                st.success("✅ Registration successful! You can now log in.")

    st.stop()  # Prevent rest of the app from loading if not logged in

# ---- APP TITLE ----
st.title("🩺 Healthcare Recommendation System")

# ---- SIDEBAR NAV ----
menu_options = ["Recommendation", "My History"]
if st.session_state.role == "admin":
    menu_options.append("Admin Dashboard")

menu = st.sidebar.radio("📌 Navigate", menu_options)


# 🔓 Logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.success("You have been logged out.")
    st.rerun()


# ---- LOAD DATA ----
df = load_data()

# ---- RECOMMENDATION PAGE ----
if menu == "Recommendation":
    st.subheader("📝 Enter Symptoms")
    symptoms_input = st.text_input("Separate multiple symptoms with commas (e.g., fever, headache)")

    user_symptoms = []
    recs = []
    sentiment_result = ""

    if st.button("Get Recommendation"):
        if symptoms_input:
            user_symptoms = [s.strip() for s in symptoms_input.split(",")]
            recs = recommend_plan(user_symptoms, df)

            st.subheader("🔍 Top Recommendation(s):")
            for i, (rec, score) in enumerate(recs, 1):
                st.markdown(f"**{i}. {rec}**  \n🧠 *Symptom Match Score:* `{score}`")

            st.session_state["user_symptoms"] = user_symptoms
            st.session_state["recs"] = recs
        else:
            st.warning("Please enter at least one symptom.")

    st.subheader("🗣️ Optional: Give Feedback")
    feedback = st.text_area("How do you feel about this recommendation?", key="feedback_box")

    if st.button("Submit Feedback"):
        if "user_symptoms" in st.session_state and "recs" in st.session_state:
            sentiment_result = analyze_sentiment(feedback)
            st.info(f"Sentiment Analysis: **{sentiment_result}**")
            log_interaction(
                st.session_state["user_symptoms"],
                st.session_state["recs"],
                feedback,
                sentiment_result
            )
        else:
            st.warning("Please generate a recommendation before submitting feedback.")

    # Footer
    st.markdown("""---  
    📊 **Welcome to the healthcare recommendation app**  
    💡 Upload patient info or use the dataset to get started.""")

# ---- MY HISTORY PAGE ----
elif menu == "My History":
    st.subheader("📜 My Recommendation History")

    username = st.session_state.get("username", "guest")
    log_file = f"data/logs_{username}.csv"

    try:
        history_df = pd.read_csv(log_file)
        st.dataframe(history_df, use_container_width=True)

        st.markdown("### 🕑 Most Recent Entries")
        st.dataframe(history_df.tail(5), use_container_width=True)

    except FileNotFoundError:
        st.info("You don't have any history yet. Submit a recommendation first.")

elif menu == "Admin Dashboard":
    st.subheader("📊 Admin Analytics Dashboard")

    import matplotlib.pyplot as plt
    import plotly.express as px
    import glob

    # Collect all user logs
    all_logs = pd.DataFrame()
    for file in glob.glob("data/logs_*.csv"):
        df = pd.read_csv(file)
        df["user"] = file.split("_")[-1].replace(".csv", "")
        all_logs = pd.concat([all_logs, df], ignore_index=True)

    if all_logs.empty:
        st.info("No feedback logs found yet.")
    else:
        # Show all logs
        st.markdown("### 🧾 Full Feedback Log")
        st.dataframe(all_logs)

        # Sentiment pie chart
        st.markdown("### 🥧 Sentiment Distribution")
        sentiment_counts = all_logs["sentiment"].value_counts()
        fig = px.pie(
            names=sentiment_counts.index,
            values=sentiment_counts.values,
            title="Overall Sentiment Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig)

        # Most recommended plans
        st.markdown("### 🌟 Most Frequently Recommended Plans")
        recs_flat = all_logs["recommendations"].dropna().str.split(", ").explode()
        top_recs = recs_flat.value_counts().head(5)
        fig2 = px.bar(
            top_recs,
            x=top_recs.index,
            y=top_recs.values,
            labels={"x": "Plan", "y": "Count"},
            title="Top 5 Recommended Plans",
            color=top_recs.values,
        )
        st.plotly_chart(fig2)

