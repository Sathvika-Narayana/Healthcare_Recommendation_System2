from recommendation import load_data, recommend_plan

df = load_data()
user_input = ["headache", "fatigue"]
result = recommend_plan(user_input, df)
print("Recommended Plan:", result)
