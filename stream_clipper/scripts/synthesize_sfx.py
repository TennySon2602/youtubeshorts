"""
Audio Synthesizer for Snickerly-style SFX Library
Generates:
1. sfx_vine_boom.mp3
2. sfx_minecraft_drink.mp3
3. sfx_minecraft_eat.mp3
4. sfx_minecraft_burp.mp3
5. sfx_whoosh.mp3
6. bgm_wholesome.mp3
"""

import math
import struct
import wave
import subprocess
import random
from pathlib import Path

SFX_DIR = Path(__file__).parent.parent / "assets" / "sfx"
SFX_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_RATE = 44100

def save_wav(filename: str, samples: list):
    wav_path = SFX_DIR / f"{filename}.wav"
    mp3_path = SFX_DIR / f"{filename}.mp3"
    with wave.open(str(wav_path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        raw_data = bytearray()
        for s in samples:
            val = max(-32767, min(32767, int(s * 32767)))
            raw_data.extend(struct.pack("<h", val))
        f.writeframes(raw_data)

    # Convert to MP3 via ffmpeg
    cmd = [
        "ffmpeg", "-y", "-i", str(wav_path),
        "-codec:a", "libmp3lame", "-qscale:a", "2",
        str(mp3_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if wav_path.exists():
        wav_path.unlink()
    print(f"Generated: {mp3_path.name} ({mp3_path.stat().st_size} bytes)")

def generate_vine_boom():
    """Heavy distorted 808 sub bass drop with punch click"""
    duration = 2.0
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Transient punch at t=0
        click = 0.8 * math.exp(-60 * t) * math.sin(2 * math.pi * 300 * t)
        # Deep sub pitch drop: 60Hz -> 28Hz
        freq = 60 * math.exp(-1.5 * t) + 25
        sub = math.sin(2 * math.pi * freq * t)
        # 2nd harmonic for 808 warmth
        sub2 = 0.45 * math.sin(2 * math.pi * (freq * 2) * t)
        # Saturation distortion
        raw = (sub + sub2) * 1.5
        distorted = math.tanh(raw)
        # Decay envelope
        env = math.exp(-1.8 * t)
        out = (click + distorted * 0.9) * env
        samples.append(out)
    save_wav("sfx_vine_boom", samples)

def generate_minecraft_drink():
    """Series of 4 liquid gulp / glug sounds"""
    duration = 1.6
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    gulp_starts = [0.05, 0.40, 0.75, 1.10]
    for start in gulp_starts:
        start_idx = int(start * SAMPLE_RATE)
        gulp_len = int(0.22 * SAMPLE_RATE)
        for j in range(gulp_len):
            t = j / SAMPLE_RATE
            # Liquid resonance sweeping upward
            freq = 320 + 260 * math.sin(math.pi * (t / 0.22))
            glug = math.sin(2 * math.pi * freq * t)
            # Water bubble noise
            noise = (random.random() * 2 - 1) * 0.2
            env = math.sin(math.pi * (t / 0.22)) ** 2
            idx = start_idx + j
            if idx < num_samples:
                samples[idx] += (glug * 0.8 + noise) * env * 0.9
    save_wav("sfx_minecraft_drink", samples)

def generate_minecraft_eat():
    """Series of 5 crisp crunching bites"""
    duration = 1.5
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    bite_starts = [0.05, 0.32, 0.60, 0.88, 1.15]
    for start in bite_starts:
        start_idx = int(start * SAMPLE_RATE)
        bite_len = int(0.18 * SAMPLE_RATE)
        for j in range(bite_len):
            t = j / SAMPLE_RATE
            # High frequency noise crunch
            noise = (random.random() * 2 - 1)
            # Modulated frequency crunch
            crunch = noise * math.sin(2 * math.pi * 1800 * t)
            env = math.exp(-25 * t)
            idx = start_idx + j
            if idx < num_samples:
                samples[idx] += (crunch * 0.75 + noise * 0.25) * env
    save_wav("sfx_minecraft_eat", samples)

def generate_minecraft_burp():
    """Pitch slide resonant comic burp"""
    duration = 0.8
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Downward pitch sweep with buzz
        freq = 135 - 75 * (t / duration)
        saw = (2 * ((freq * t) % 1) - 1)
        sub = 0.5 * math.sin(2 * math.pi * (freq * 0.5) * t)
        vibrato = math.sin(2 * math.pi * 12 * t) * 0.2
        env = math.sin(math.pi * (t / duration)) ** 0.5 * math.exp(-1.2 * t)
        out = (saw + sub + vibrato) * env * 0.8
        samples.append(out)
    save_wav("sfx_minecraft_burp", samples)

def generate_whoosh():
    """Dynamic air whoosh sweep"""
    duration = 0.4
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        noise = (random.random() * 2 - 1)
        freq = 250 + 2800 * math.sin(math.pi * (t / duration))
        sweep = noise * math.sin(2 * math.pi * freq * t)
        env = math.sin(math.pi * (t / duration)) ** 2
        samples.append(sweep * env * 0.85)
    save_wav("sfx_whoosh", samples)

def generate_wholesome_bgm():
    """Gentle, warm, emotional Rhodes/piano loop for wholesome/sentimental moments"""
    duration = 8.0
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    # Chord progression: Cmaj7 (C, E, G, B) -> Am7 (A, C, E, G) -> Fmaj7 (F, A, C, E) -> G (G, B, D)
    chords = [
        (0.0, [261.63, 329.63, 392.00, 493.88]), # Cmaj7
        (2.0, [220.00, 261.63, 329.63, 392.00]), # Am7
        (4.0, [174.61, 220.00, 261.63, 329.63]), # Fmaj7
        (6.0, [196.00, 246.94, 293.66, 392.00]), # G
    ]

    for start_t, freqs in chords:
        start_idx = int(start_t * SAMPLE_RATE)
        chord_len = int(2.0 * SAMPLE_RATE)
        for j in range(chord_len):
            t = j / SAMPLE_RATE
            note_sum = 0.0
            for f in freqs:
                # Soft sine bell with 2nd harmonic
                tone = math.sin(2 * math.pi * f * t) + 0.25 * math.sin(2 * math.pi * f * 2 * t)
                note_sum += tone
            env = (1 - math.exp(-15 * t)) * math.exp(-1.5 * t)
            idx = start_idx + j
            if idx < num_samples:
                samples[idx] += (note_sum / len(freqs)) * env * 0.55

    save_wav("bgm_wholesome", samples)

if __name__ == "__main__":
    print("Synthesizing Snickerly SFX suite...")
    generate_vine_boom()
    generate_minecraft_drink()
    generate_minecraft_eat()
    generate_minecraft_burp()
    generate_whoosh()
    generate_wholesome_bgm()
    print("Done!")
