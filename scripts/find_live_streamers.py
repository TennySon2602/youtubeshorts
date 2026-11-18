import requests
import json

headers = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

def search_game_streams(game_name="Grand Theft Auto VI", min_viewers=30000):
    query = f"""
    query {{
      game(name: "{game_name}") {{
        id
        name
        streams(first: 30) {{
          edges {{
            node {{
              id
              title
              viewersCount
              createdAt
              broadcaster {{
                id
                login
                displayName
              }}
            }}
          }}
        }}
      }}
    }}
    """
    try:
        resp = requests.post(
            "https://gql.twitch.tv/gql",
            headers=headers,
            json={"query": query},
            timeout=10
        )
        data = resp.json()
        game_data = data.get("data", {}).get("game")
        if not game_data or not game_data.get("streams"):
            return []
        
        streamers = []
        for edge in game_data["streams"]["edges"]:
            node = edge["node"]
            vc = node.get("viewersCount", 0)
            broadcaster = node.get("broadcaster", {})
            login = broadcaster.get("login")
            display_name = broadcaster.get("displayName")
            title = node.get("title")
            if vc >= min_viewers:
                streamers.append({
                    "game": game_data.get("name"),
                    "login": login,
                    "displayName": display_name,
                    "viewersCount": vc,
                    "title": title
                })
        return streamers
    except Exception as e:
        print(f"Error searching game streams: {e}")
        return []

def get_streamer_clips(login, limit=3, time_filter="LAST_DAY"):
    query = f"""
    query {{
      user(login: "{login}") {{
        id
        login
        displayName
        clips(first: {limit}, criteria: {{ filter: {time_filter} }}) {{
          edges {{
            node {{
              id
              slug
              title
              viewCount
              durationSeconds
              url
              videoQualities {{
                sourceURL
                quality
              }}
            }}
          }}
        }}
      }}
    }}
    """
    try:
        resp = requests.post(
            "https://gql.twitch.tv/gql",
            headers=headers,
            json={"query": query},
            timeout=10
        )
        res_json = resp.json()
        data = res_json.get("data", {})
        if not data or not data.get("user"):
            return []
        user_node = data["user"]
        clips_node = user_node.get("clips")
        if not clips_node:
            return []
        edges = clips_node.get("edges", [])
        clips = []
        for edge in edges:
            n = edge["node"]
            mp4_url = None
            for q in n.get("videoQualities", []):
                if q.get("quality") in ["1080", "source", "720"]:
                    mp4_url = q.get("sourceURL")
                    break
            if not mp4_url and n.get("videoQualities"):
                mp4_url = n["videoQualities"][0].get("sourceURL")
            clips.append({
                "id": n.get("id"),
                "slug": n.get("slug"),
                "title": n.get("title"),
                "viewCount": n.get("viewCount"),
                "duration": n.get("durationSeconds"),
                "twitch_url": n.get("url"),
                "mp4_url": mp4_url,
                "streamer_login": login,
                "streamer_name": user_node.get("displayName")
            })
        return clips
    except Exception as e:
        print(f"Error fetching clips for {login}: {e}")
        return []

if __name__ == "__main__":
    top_streamers = search_game_streams("Grand Theft Auto VI", min_viewers=30000)
    print(f"Found {len(top_streamers)} streamers with >= 30,000 viewers:")
    for s in top_streamers[:6]:
        print(f"\n--- {s['displayName']} (@{s['login']}) - {s['viewersCount']} viewers ---")
        clips = get_streamer_clips(s['login'], limit=3, time_filter="LAST_DAY")
        if not clips:
            clips = get_streamer_clips(s['login'], limit=3, time_filter="LAST_WEEK")
        if not clips:
            clips = get_streamer_clips(s['login'], limit=3, time_filter="ALL_TIME")
        print(f"Clips found: {len(clips)}")
        for c in clips:
            print(f"  * [{c['viewCount']} views] {c['title']} ({c['duration']}s)\n    URL: {c['mp4_url']}")
