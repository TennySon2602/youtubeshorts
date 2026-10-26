# File: script_generator.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OXION_API_KEY = os.getenv("OXION_API_KEY")
OXION_BASE_URL = os.getenv("OXION_BASE_URL", "https://www.oxionai.com/v1")
OXION_MODEL = os.getenv("OXION_MODEL", "gemini-3.7-flash")

FALLBACK_SCRIPTS = {
    "anechoic_chamber": {
        "topic": "The Anechoic Chamber: What happens inside the quietest room on Earth?",
        "language": "en",
        "hook": "What happens if you sit inside a room so quiet that you can hear your own eyeballs moving?",
        "full_narration": "What happens if you sit inside a room so quiet that you can hear your own eyeballs moving? Inside Microsoft's anechoic chamber, background noise measures at minus twenty decibels. That is quieter than complete silence. Within minutes, your ears adapt. Suddenly, your heartbeat sounds like a bass drum. You hear your lungs pumping air and your blood rushing through your veins. Without any external sound, your brain begins to hallucinate, inventing phantom noises just to stay sane. The longest anyone has ever survived inside this room in total darkness is just forty-five minutes. Follow for more dark science secrets you won't learn in school.",
        "segments": [
            {
                "segment_index": 1,
                "narration_part": "What happens if you sit inside a room so quiet that you can hear your own eyeballs moving?",
                "visual_search_keyword": "dark room silence"
            },
            {
                "segment_index": 2,
                "narration_part": "Inside Microsoft's anechoic chamber, background noise measures at minus twenty decibels. That is quieter than complete silence.",
                "visual_search_keyword": "soundproof room studio"
            },
            {
                "segment_index": 3,
                "narration_part": "Within minutes, your ears adapt. Suddenly, your heartbeat sounds like a bass drum. You hear your lungs pumping air and your blood rushing through your veins.",
                "visual_search_keyword": "human heart pulse"
            },
            {
                "segment_index": 4,
                "narration_part": "Without any external sound, your brain begins to hallucinate, inventing phantom noises just to stay sane.",
                "visual_search_keyword": "human brain neurology dark"
            },
            {
                "segment_index": 5,
                "narration_part": "The longest anyone has ever survived inside this room in total darkness is just forty-five minutes. Follow for more dark science secrets.",
                "visual_search_keyword": "dark silhouette mystery"
            }
        ],
        "call_to_action": "Follow for more dark science secrets you won't learn in school."
    }
}

SYSTEM_PROMPT = """
You are a viral YouTube Shorts and TikTok scriptwriter specializing in the 'Dark Curiosity & Science Mysteries' niche.
Your mission is to write an addictive, suspenseful, fast-paced script (around 45 to 55 seconds when read aloud).

Output strictly in valid JSON format with this exact structure:
{
  "topic": "Topic title",
  "language": "en",
  "hook": "An intensely shocking opening question or statement within the first 3 seconds to stop viewers from scrolling.",
  "full_narration": "The complete, continuous narration text connecting the hook, body, and conclusion for text-to-speech reading.",
  "segments": [
    {
      "segment_index": 1,
      "narration_part": "Narration text for this portion",
      "visual_search_keyword": "1-2 concise English keywords for stock video search (e.g., dark room, human brain)"
    }
  ],
  "call_to_action": "Follow for more dark science secrets you won't learn in school."
}
IMPORTANT: Return ONLY raw JSON without markdown code fences or extra text.
"""

def generate_script(topic: str, language: str = "en", model: str = None) -> dict:
    if model is None:
        model = OXION_MODEL
    
    try:
        client = OpenAI(api_key=OXION_API_KEY, base_url=OXION_BASE_URL)
        user_prompt = f"Create an addictive viral short video script about: '{topic}'. Language: '{language}'."
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        return json.loads(raw_content.strip())
    except Exception as e:
        print(f"[Oxion AI Notice]: {e}")
        print("💡 Đang kích hoạt kịch bản mẫu chất lượng cao để hoàn tất render video...")
        return FALLBACK_SCRIPTS["anechoic_chamber"]

if __name__ == "__main__":
    result = generate_script("The anechoic chamber", language="en")
    print(json.dumps(result, indent=2, ensure_ascii=False))
