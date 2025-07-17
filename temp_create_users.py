import pandas as pd

df = pd.DataFrame([
    {"username": "mrunali", "password": "1234", "role": "user"},
    {"username": "admin", "password": "adminpass", "role": "admin"}
])
df.to_csv("data/users.csv", index=False)

print("✅ users.csv created successfully.")
