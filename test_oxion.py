import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OXION_API_KEY")

url = "https://www.oxionai.com/v1/models"
try:
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        models = r.json()
        print("Available models sample:")
        for m in models.get("data", [])[:10]:
            print(" -", m.get("id"))
    else:
        print("Response:", r.text)
except Exception as e:
    print("Error:", e)
