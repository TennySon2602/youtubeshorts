import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stream_clipper.streamer_clipper import search_live_gta_streamers, get_streamer_clips

streamers = search_live_gta_streamers(min_viewers=30000)
print(f"Total live GTA streamers >= 30,000 viewers: {len(streamers)}")
for s in streamers[:6]:
    clips = get_streamer_clips(s["login"], limit=2)
    print(f"- {s['displayName']} (@{s['login']}): {s['viewersCount']:,} viewers | {len(clips)} clips available")
    if clips:
        print(f"    Top clip: '{clips[0]['title']}' ({clips[0]['url']})")
