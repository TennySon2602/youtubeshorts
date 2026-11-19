"""
Local 24/7 Autonomous Stream Clipper Runner
Runs continuous clipping cycles every 15 minutes right from your machine.
- Automatically discovers GTA streamers with >= 30,000 viewers
- Detects chat spikes in LOL, LMAO, WTF, KEKW
- Generates 50/50 Snickerly video with kinetic 1-word subtitles
- Automatically publishes to Facebook Reels & Instagram Reels
"""

import sys
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = BASE_DIR.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BASE_DIR))

from stream_clipper.streamer_clipper import run_cli

if __name__ == "__main__":
    print("=" * 65)
    print("🚀 24/7 LOCAL AUTONOMOUS STREAM CLIPPER (Chat Spike Detection)")
    print("   Target: Live GTA Streamers >= 30,000 viewers")
    print("   Cadence: Every 15 minutes")
    print("   Press Ctrl+C to stop")
    print("=" * 65)

    # Inject arguments
    sys.argv = [
        "streamer_clipper.py",
        "--auto-discover",
        "--min-viewers", "30000",
        "--max-streamers", "3",
        "--publish",
        "--loop",
        "--interval", "900"
    ]
    run_cli()
