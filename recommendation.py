# ML recommendation logic will go here.

import pandas as pd
from datetime import datetime

def load_data():
    return pd.read_csv("data/health_plans.csv")

def recommend_plan(symptoms, df):
    scores = []
    month = datetime.now().month
    season = get_season(month)

    for _, row in df.iterrows():
        plan_symptoms = row["symptoms"].lower().split(", ")
        match_score = sum(1 for s in symptoms if s.lower() in plan_symptoms)

        # ✅ Season-aware bonus
        if "hydration" in row["plan"].lower() and season == "summer":
            match_score += 3

        if "immunity" in row["plan"].lower() and season == "winter":
            if any(s in ["cold", "cough", "flu"] for s in symptoms):
                match_score += 3

        scores.append((row["plan"], match_score))

    # Sort by highest score
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return scores[:3]  # Top 3

def get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"


