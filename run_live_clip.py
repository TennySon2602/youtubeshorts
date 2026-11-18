"""
Execute Live Clipping Run on Kai Cenat Stream Clip (30k+ viewers)
Edits with Snickerly style (1-word subtitles, SFX, 9:16 vertical) and publishes to Meta.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "stream_clipper"))

from snickerly_editor import render_snickerly_video
from meta_uploader import upload_all_meta_reels

def main():
    src_video = BASE_DIR / "stream_clipper" / "output" / "kai_cenat_clip.mp4.webm"
    if not src_video.exists():
        print(f"❌ Source clip not found: {src_video}")
        return

    out_video = BASE_DIR / "stream_clipper" / "output" / "snickerly_kai_cenat_viral_short.mp4"

    # Define Snickerly rhythmic events
    events = [
        {"type": "drink", "time": 2.2},
        {"type": "vine_boom", "time": 6.8, "zoom": True},
        {"type": "wholesome", "start": 10.5, "end": 14.5},
        {"type": "eat", "time": 16.5}
    ]

    # Real-time 1-word-at-a-time kinetic subtitles
    raw_words = [
        ("KAI", 0.5, 0.9, True),
        ("CENAT", 0.9, 1.4, True),
        ("CANNOT", 1.4, 1.9, False),
        ("BELIEVE", 1.9, 2.5, False),
        ("THIS!", 2.5, 3.2, True),
        ("WAIT...", 3.8, 4.4, False),
        ("BRO", 4.4, 4.9, True),
        ("LOOK", 4.9, 5.4, False),
        ("AT", 5.4, 5.7, False),
        ("THAT!", 5.7, 6.4, True),
        ("HE", 7.0, 7.3, False),
        ("DID", 7.3, 7.6, False),
        ("NOT", 7.6, 8.0, True),
        ("JUST", 8.0, 8.3, False),
        ("DO", 8.3, 8.6, False),
        ("THAT!", 8.6, 9.3, True),
        ("OKAY", 10.2, 10.7, False),
        ("THAT'S", 10.7, 11.2, False),
        ("ACTUALLY", 11.2, 11.8, False),
        ("CRAZY!", 11.8, 12.8, True),
        ("WATCH", 13.5, 14.0, False),
        ("TILL", 14.0, 14.4, False),
        ("THE", 14.4, 14.7, False),
        ("END!", 14.7, 15.5, True),
    ]

    dialogues = [
        {"start": s, "end": e, "text": w, "punch": p}
        for (w, s, e, p) in raw_words
    ]

    print("\n" + "=" * 60)
    print("🎬 RENDERING VIRAL STREAM CLIP (KAI CENAT - 100K+ CCV)")
    print("=" * 60)

    rendered_file = render_snickerly_video(
        source_video=str(src_video),
        output_path=str(out_video),
        streamer_name="KaiCenat",
        hook_title="KAI CENAT PLAYS GTA - FUNNIEST MOMENT 💀",
        events=events,
        dialogues=dialogues
    )

    print(f"\n🎉 Video Rendered: {Path(rendered_file).name} ({Path(rendered_file).stat().st_size // 1024 // 1024}MB)")

    # Publish to Facebook Reels and Instagram Reels
    print("\n🚀 Publishing to Facebook Reels & Instagram Reels...")
    title = "Kai Cenat Insane GTA Moment | 100k+ Viewers Reaction 💀"
    desc = "Kai Cenat just pulled off the craziest moment in GTA! Streamer highlights and funny gaming reactions.\n\n#KaiCenat #GTA6 #GTAVI #Gaming #Reels #Shorts #Snickerly"
    tags = ["KaiCenat", "GTA6", "GTAVI", "Gaming", "Reels", "Shorts"]

    meta_results = upload_all_meta_reels(
        file_path=rendered_file,
        title=title,
        description=desc,
        tags=tags
    )
    print(f"\n✅ Upload Results: {meta_results}")

if __name__ == "__main__":
    main()
