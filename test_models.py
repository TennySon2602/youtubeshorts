import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OXION_API_KEY"),
    base_url=os.getenv("OXION_BASE_URL")
)

models = ["gemini-3.6-flash", "kimi-k3", "gemma-2-2b", "seed-2.1-pro", "grok-4.6"]

for m in models:
    try:
        res = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=10
        )
        print(f"Model {m}: SUCCESS -> {res.choices[0].message.content}")
        break
    except Exception as e:
        print(f"Model {m}: FAILED -> {e}")
