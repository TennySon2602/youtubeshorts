"""
Optional LLM pass (--llm none|ollama|gemini): reads the transcript in ~8 min chunks and proposes story
segments with a hook, title, description and hashtags. Standard library only (urllib).
The Gemini key comes from env GEMINI_API_KEY and goes only into the x-goog-api-key header: never into
URLs, logs, state files or exception text.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from streamclipper.state import write_json_atomic
from streamclipper.util import CATEGORIES, ToolError

PROVIDERS = ("none", "ollama", "gemini")
DEFAULT_MODELS = {"ollama": "qwen2.5:7b", "gemini": "gemini-2.5-flash"}
OLLAMA_URL = "http://localhost:11434/api/chat"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
CHUNK_S = 480.0
_SENT_END = (".", "?", "!", "।", "॥")


class LLMUnavailable(Exception):
    """The provider cannot be reached (server down, bad key, quota); the run continues without it."""


def _secret() -> str:
    return os.environ.get("GEMINI_API_KEY", "")


def _scrub(text) -> str:
    """Remove the API key from any text before it is printed, stored or raised."""
    text, key = str(text), _secret()
    return text.replace(key, "***") if key else text


def _post_json(url: str, payload: dict, headers: dict, timeout: float = 180.0) -> dict:
    """POST JSON and return the JSON reply (the single network seam; tests replace it)."""
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", **headers}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _mmss(t: float) -> str:
    t = int(max(0.0, t))
    return f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60:02d}:{t % 60:02d}"


def transcript_chunks(words: list, chunk_s: float = CHUNK_S) -> list:
    """[(start, end, text)]: sentences prefixed with [mm:ss], cut into chunks of about chunk_s seconds."""
    sents, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1]["s"] if i + 1 < len(words) else None
        if str(w["w"]).endswith(_SENT_END) or nxt is None or nxt - w["e"] >= 0.6:
            sents.append((cur[0]["s"], cur[-1]["e"], " ".join(str(x["w"]).strip() for x in cur)))
            cur = []
    chunks, buf = [], []
    for s in sents:
        if buf and s[0] - buf[0][0] >= chunk_s:
            chunks.append(buf)
            buf = []
        buf.append(s)
    if buf:
        chunks.append(buf)
    return [(c[0][0], c[-1][1], "\n".join(f"[{_mmss(a)}] {t}" for a, _, t in c)) for c in chunks]


def _language_rule(language: str, text: str) -> str:
    latin = sum(ch.isascii() and ch.isalpha() for ch in text)
    deva = sum("\u0900" <= ch <= "\u097f" for ch in text)
    if language == "hi" and deva >= latin:
        return "Write hook, title and description in Hindi using Devanagari script. Do not mix in English."
    if language == "hi":
        return "The stream is Hinglish (Hindi in Latin letters): write hook, title and description the same way."
    return "Write hook, title and description in plain, natural English. Do not mix in Hindi."


def build_prompt(text: str, language: str = "en", content: str = "gaming") -> str:
    cats = ", ".join(CATEGORIES)
    if content == "talk":
        return (
            "You are a short-form video editor. Below is part of a podcast or talk-show transcript; each line "
            "starts with its [mm:ss] time.\n"
            "Find the moments that work as a 20-60 second vertical clip for someone who has not seen the "
            "episode: a self-contained statement or hot take, a short story with a punchline, or a funny "
            "exchange. setup_t is where the point starts (the viewer needs nothing before it), payoff_t is the "
            "punchline or the strongest line, end_t is right after the laugh or the reaction. Skip small talk, "
            "ads, intros and moments that need earlier context.\n"
            'Reply with JSON only: {"segments": [{"setup_t": seconds, "payoff_t": seconds, "end_t": seconds, '
            '"story_score": 0-100, "category": one of [' + cats + '], "hook": "3-6 word on-screen hook", '
            '"title": "post title, max 70 characters", "description": "one or two sentences", '
            '"hashtags": ["#tag", ...]}]}\n'
            "Times are seconds from the start (convert mm:ss). Use an empty list when nothing stands out. "
            + _language_rule(language, text)
            + "\n\nTranscript:\n"
            + text
        )
    return (
        "You are a short-form video editor. Below is part of a live-stream transcript; each line starts with "
        "its [mm:ss] time in the stream.\n"
        "Find every moment that can be a viral 15-45 second vertical clip with a clear story: setup, tension, "
        "payoff, reaction.\n"
        'Reply with JSON only: {"segments": [{"setup_t": seconds, "payoff_t": seconds, "end_t": seconds, '
        '"story_score": 0-100, "category": one of [' + cats + '], "hook": "3-6 word on-screen hook", '
        '"title": "post title, max 70 characters", "description": "one or two sentences", '
        '"hashtags": ["#tag", ...]}]}\n'
        "Times are seconds from the start of the stream (convert mm:ss). Use an empty list when nothing "
        "stands out. " + _language_rule(language, text) + "\n\nTranscript:\n" + text
    )


def _call(provider: str, model: str, prompt: str) -> str:
    """Raw text reply. Network/auth problems -> LLMUnavailable (scrubbed)."""
    try:
        if provider == "ollama":
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.3},
            }
            reply = _post_json(OLLAMA_URL, payload, {})
            return str((reply.get("message") or {}).get("content") or "")
        key = _secret()
        if not key:
            raise ToolError(
                "--llm gemini needs your own free key in the environment variable GEMINI_API_KEY.",
                "PowerShell: $env:GEMINI_API_KEY = '<your key>'  (get one at aistudio.google.com; never share it)",
            )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3},
        }
        reply = _post_json(GEMINI_URL.format(model=model), payload, {"x-goog-api-key": key})
        parts = (((reply.get("candidates") or [{}])[0].get("content") or {}).get("parts")) or [{}]
        return str(parts[0].get("text") or "")
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, ValueError) as e:
        detail = getattr(e, "reason", None) or e
        code = getattr(e, "code", None)
        msg = f"{provider} request failed" + (f" (HTTP {code})" if code else "") + f": {detail}"
        raise LLMUnavailable(_scrub(msg)) from None


def _num(v, lo: float, hi: float):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if lo <= x <= hi else None


def validate(reply: str, a: float, b: float) -> list:
    """Parse and clean the JSON reply; raises ValueError when it is not the requested shape."""
    text = reply.strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    obj = json.loads(m.group(0) if m else text)
    segs = obj.get("segments") if isinstance(obj, dict) else obj
    if not isinstance(segs, list):
        raise ValueError("no 'segments' list")
    out = []
    for s in segs:
        if not isinstance(s, dict):
            continue
        pay = _num(s.get("payoff_t"), a - 30.0, b + 30.0)
        if pay is None or not (str(s.get("title") or "").strip() or str(s.get("hook") or "").strip()):
            continue
        setup = _num(s.get("setup_t"), max(0.0, pay - 60.0), pay) or max(0.0, pay - 15.0)
        end = _num(s.get("end_t"), pay, pay + 60.0) or pay + 4.0
        cat = str(s.get("category") or "").strip().lower()
        tags = s.get("hashtags") if isinstance(s.get("hashtags"), list) else []
        tags = ["#" + re.sub(r"[^\w]", "", str(t).lstrip("#")) for t in tags][:8]
        out.append(
            {
                "setup_t": round(setup, 2),
                "payoff_t": round(pay, 2),
                "end_t": round(end, 2),
                "story_score": _num(s.get("story_score"), 0, 100),
                "category": cat if cat in CATEGORIES else None,
                "hook": str(s.get("hook") or "").strip()[:60],
                "title": str(s.get("title") or "").strip()[:100],
                "description": str(s.get("description") or "").strip()[:500],
                "hashtags": [t for t in tags if len(t) > 1],
            }
        )
    return out


def analyze_transcript(
    words: list, provider: str, model: str, language: str, state, work_dir: Path, content: str = None
) -> list:
    """
    LLM segments for the whole transcript. Each chunk result goes to <work>/llm/chunk_NNNN.json and its
    index into state.stages['llm_chunks'], so a resumed run skips finished chunks. Each provider+model has
    its own folder (<work>/llm/<provider>_<model>/, + '_talk' for --content talk), so switching models keeps
    both caches. An invalid reply is retried once, then the chunk is skipped. When the provider cannot be
    reached the run continues without the LLM (one notice).
    """
    if provider == "none" or not words:
        return []
    if provider not in PROVIDERS:
        raise ToolError(f"Unknown --llm '{provider}'.", "use none, ollama or gemini")
    model = model or DEFAULT_MODELS[provider]
    talk = content == "talk"
    llm_dir = Path(work_dir) / "llm" / re.sub(r"[^\w.-]+", "_", f"{provider}_{model}" + ("_talk" if talk else ""))
    chunks = transcript_chunks(words)
    done = set(state.stages.setdefault("llm_chunks", [])) if state is not None else set()
    print(f"LLM: {provider} '{model}' reads {len(chunks)} transcript chunk(s) ...")
    segs = []
    for i, (a, b, text) in enumerate(chunks):
        f = llm_dir / f"chunk_{i:04d}.json"
        if i in done and f.is_file():
            old = json.loads(f.read_text(encoding="utf-8"))
            if old.get("model") == f"{provider}:{model}":
                segs += old.get("segments", [])
                continue
        got, ok = [], False
        try:
            for _attempt in range(2):
                reply = _call(provider, model, build_prompt(text, language, "talk" if talk else "gaming"))
                try:
                    got, ok = validate(reply, a, b), True
                    break
                except (ValueError, AttributeError, TypeError):
                    continue
        except LLMUnavailable as e:
            print(f"LLM unavailable ({e}); continuing without it.")
            return segs
        if not ok:
            print(f"LLM chunk {i + 1}/{len(chunks)}: reply was not valid JSON twice; skipped.")
        write_json_atomic(
            f, {"start": round(a, 2), "end": round(b, 2), "model": f"{provider}:{model}", "ok": ok, "segments": got}
        )
        if state is not None:
            state.stages["llm_chunks"] = sorted(done | {i})
            done.add(i)
            state.save()
        segs += got
    print(f"LLM: {len(segs)} story segment(s) proposed")
    return segs
