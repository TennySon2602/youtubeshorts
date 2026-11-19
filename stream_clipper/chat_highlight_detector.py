"""
Chat Highlight Detector for Twitch Streams & Clips
Monitors and analyzes chat activity for spikes in LOL, LMAO, WTF, KEKW, OMEGALUL, and shock reactions.
Identifies the exact hype moments and ranks clips based on genuine chat excitement.
"""

import re
import requests
from typing import Dict, List, Optional, Tuple

TWITCH_GQL_URL = "https://gql.twitch.tv/gql"
TWITCH_HEADERS = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

# Highlight Keywords & Emote patterns
HYPE_KEYWORDS = {
    "lol": re.compile(r"\b(lol+|lmao+|lmfao+|lul|kekw|omegalul|rofl|xd+|haha+|jajaja+)\b", re.IGNORECASE),
    "wtf": re.compile(r"\b(wtf+|wth|what\s*the\s*fuck|hell\s*nah|no\s*way|tf+|omfg|aint\s*no\s*way)\b", re.IGNORECASE),
    "shock": re.compile(r"\b(bruh+|bro+|rip+|dead|skull|💀|😂|🤣|😭|nah|fr)\b", re.IGNORECASE),
    "hype": re.compile(r"\b(pog+|poggers|omg+|holy+|crazy|insane|yo+|w+|goat|clip\s*it)\b", re.IGNORECASE)
}

def analyze_clip_chat(vod_id: str, offset_seconds: int, duration_seconds: int = 30) -> Optional[Dict]:
    """
    Analyzes chat messages during a clip's timeframe directly from Twitch VOD chat replay.
    Counts spikes in LOL, LMAO, WTF, KEKW, OMEGALUL, and identifies the peak second.
    """
    if not vod_id or offset_seconds is None or offset_seconds < 0:
        return None

    query = f"""
    query {{
      video(id: "{vod_id}") {{
        comments(contentOffsetSeconds: {max(0, offset_seconds - 3)}) {{
          edges {{
            cursor
            node {{
              contentOffsetSeconds
              message {{
                fragments {{
                  text
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    try:
        resp = requests.post(
            TWITCH_GQL_URL,
            headers=TWITCH_HEADERS,
            json={"query": query},
            timeout=8
        )
        data = resp.json().get("data", {}).get("video", {})
        if not data or not data.get("comments"):
            return None

        edges = data["comments"].get("edges", [])
        if not edges:
            return None

        start_window = max(0, offset_seconds - 2)
        end_window = offset_seconds + duration_seconds + 3

        sec_histogram: Dict[int, int] = {}
        total_messages = 0
        hype_messages = 0
        details = {"lol": 0, "wtf": 0, "shock": 0, "hype": 0}

        for edge in edges:
            node = edge.get("node", {})
            sec = node.get("contentOffsetSeconds", 0)
            if sec < start_window or sec > end_window:
                continue

            fragments = node.get("message", {}).get("fragments", [])
            msg_text = " ".join([f.get("text", "") for f in fragments])
            total_messages += 1

            rel_sec = sec - offset_seconds
            sec_histogram[rel_sec] = sec_histogram.get(rel_sec, 0)

            matched_any = False
            for cat, pattern in HYPE_KEYWORDS.items():
                if pattern.search(msg_text):
                    details[cat] += 1
                    matched_any = True

            if matched_any:
                hype_messages += 1
                sec_histogram[rel_sec] = sec_histogram.get(rel_sec, 0) + 2

        # Calculate metrics
        dur = max(5, duration_seconds)
        hypes_per_min = (hype_messages / dur) * 60.0
        hype_ratio = hype_messages / max(1, total_messages)

        # Composite score prioritizing LOL and WTF
        composite_score = (
            (details["lol"] * 5.0) +
            (details["wtf"] * 6.0) +
            (details["shock"] * 3.0) +
            (details["hype"] * 2.0) +
            (hypes_per_min * 1.5) +
            (hype_ratio * 40.0)
        )

        peak_sec = max(sec_histogram, key=sec_histogram.get) if sec_histogram else int(duration_seconds / 2)
        # Ensure peak_sec is within valid bounds of the clip
        peak_sec = max(1, min(peak_sec, duration_seconds - 1))

        return {
            "total_messages": total_messages,
            "hype_messages": hype_messages,
            "hype_ratio": round(hype_ratio, 3),
            "hypes_per_min": round(hypes_per_min, 1),
            "peak_second": peak_sec,
            "composite_score": round(composite_score, 1),
            "details": details
        }
    except Exception as e:
        # Fallback gracefully if Twitch GQL comments fail
        return None

def calculate_title_fallback_score(title: str) -> float:
    """Heuristic fallback score when VOD chat is unavailable (e.g. deleted VOD)"""
    score = 10.0
    title_lower = title.lower()
    for cat, pattern in HYPE_KEYWORDS.items():
        if pattern.search(title_lower):
            if cat in ["lol", "wtf"]:
                score += 30.0
            else:
                score += 15.0
    return score

def rank_clips_by_chat_hype(clips: List[Dict]) -> List[Dict]:
    """
    Scores each clip by querying chat replay for LOL, LMAO, WTF spikes.
    Returns clips sorted in descending order of chat hype score.
    """
    scored_clips = []
    print(f"\n💬 Analyzing chat activity (LOL, LMAO, WTF spikes) for {len(clips)} candidate clips...")

    for c in clips:
        vod_info = c.get("video") or {}
        vod_id = vod_info.get("id") if isinstance(vod_info, dict) else None
        offset = c.get("videoOffsetSeconds")
        duration = c.get("duration", c.get("durationSeconds", 30))

        chat_stats = None
        if vod_id and offset is not None:
            chat_stats = analyze_clip_chat(vod_id, offset, duration)

        if chat_stats:
            c["chat_stats"] = chat_stats
            c["chat_score"] = chat_stats["composite_score"]
            c["peak_second"] = chat_stats["peak_second"]
            det = chat_stats["details"]
            print(f"   🔥 Clip '{c['title'][:35]}...': Score={c['chat_score']} | LOL={det['lol']}, WTF={det['wtf']}, Shock={det['shock']} | Peak={c['peak_second']}s")
        else:
            fallback_score = calculate_title_fallback_score(c.get("title", "")) + (c.get("viewCount", 0) / 1000.0)
            c["chat_stats"] = None
            c["chat_score"] = round(fallback_score, 1)
            c["peak_second"] = max(2, int(duration * 0.4))
            print(f"   ℹ️ Clip '{c['title'][:35]}...': Fallback Score={c['chat_score']} (VOD chat not available)")

        scored_clips.append(c)

    # Sort descending by chat_score
    scored_clips.sort(key=lambda x: x["chat_score"], reverse=True)
    return scored_clips
