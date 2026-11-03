"""
Autonomous Gaming Drama Discovery Engine
Fetches real-time, breaking gaming controversies, lawsuits, boycotts, and scandals.
"""

import re
import urllib.parse
import xml.etree.ElementTree as ET
import requests

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

REQUIRED_GAMING_WORDS = [
    'game', 'gaming', 'gamer', 'steam', 'nintendo', 'playstation', 'xbox', 'developer',
    'studio', 'rpg', 'fps', 'multiplayer', 'valve', 'epic', 'ubisoft', 'activision',
    'blizzard', 'ea', 'roblox', 'esports', 'mod', 'dlc', 'patch', 'server', 'lawsuit',
    'cloning', 'clone', 'vr', 'consoles', 'pc'
]

FILTER_KEYWORDS = [
    'nfl', 'nba', 'super bowl', 'mahomes', 'football coach', 'premier league',
    'champions league', 'baseball', 'quarterback', 'touchdown', 'mlb', 'costume',
    'halloween costume', 'celebrity', 'hollywood', 'movie trailer', 'real madrid',
    'barcelona', 'soccer', 'football', 'fifa world cup', 'mbappe'
]

def search_gaming_news(custom_query: str = None, limit: int = 5):
    """
    Finds trending gaming drama from Google News RSS.
    If custom_query is provided, searches for that topic + drama.
    Otherwise, hunts for the #1 breaking gaming controversy.
    """
    if custom_query and custom_query.strip():
        q = f'"{custom_query.strip()}" (controversy OR drama OR backlash OR lawsuit OR boycott OR update) when:7d'
    else:
        q = '(video game OR steam OR nintendo OR playstation OR xbox OR "game developer") (controversy OR drama OR lawsuit OR backlash OR boycott OR "review bomb") when:3d'

    encoded_q = urllib.parse.quote(q)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-US&gl=US&ceid=US:en"
    
    print(f"[NewsHunter] Querying live gaming feeds: {q[:70]}...")
    items = []
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item'):
                raw_title = item.find('title').text or ""
                link = item.find('link').text or ""
                pub_date = item.find('pubDate').text or ""
                
                # Clean up title and extract source publisher
                # Google News titles format: "Headline text - Publisher Name"
                parts = raw_title.rsplit(" - ", 1)
                headline = parts[0].strip()
                source = parts[1].strip() if len(parts) > 1 else "Gaming News"

                # Filter out non-gaming news
                lower_h = headline.lower()
                if any(k in lower_h for k in FILTER_KEYWORDS):
                    continue
                if not any(w in lower_h for w in REQUIRED_GAMING_WORDS):
                    continue

                items.append({
                    "headline": headline,
                    "source": source,
                    "link": link,
                    "pub_date": pub_date
                })
                if len(items) >= limit:
                    break
    except Exception as e:
        print(f"[NewsHunter] Warning: Failed to fetch live news: {e}")

    return items

def extract_topic_slug(text: str) -> str:
    """Generates a clean directory slug from a headline."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()
    words = cleaned.split()[:4]
    return "_".join(words) if words else "gaming_drama"

if __name__ == "__main__":
    print("--- Auto Discovery ---")
    stories = search_gaming_news(limit=5)
    for i, s in enumerate(stories):
        print(f"{i+1}. [{s['source']}] {s['headline']}")

    print("\n--- Custom Query: 'Roblox' ---")
    custom_stories = search_gaming_news("Roblox", limit=3)
    for i, s in enumerate(custom_stories):
        print(f"{i+1}. [{s['source']}] {s['headline']}")
