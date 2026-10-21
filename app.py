"""Rimba Tales: a bedtime story narrator that does the reading for you.

Zero third-party dependencies: this service runs on the Python standard
library alone, so it deploys anywhere Python does, with nothing to install.

Story generation, in order of preference:
  1. An open-weight model served by Groq (auto-selected from the models the
     API key can access), when GROQ_API_KEY is set.
  2. A local, offline story engine (stories.py) that needs nothing at all.

Narration, in order of preference:
  1. ElevenLabs text-to-speech, when ELEVENLABS_API_KEY is set.
  2. The browser's built-in speech synthesis (handled in app.js).
"""

import base64
import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import stories

BASE = Path(__file__).parent

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "")  # empty = auto-discover from the account
RESOLVED_MODEL = ""
MODEL_PREFERENCE = (
    "llama-4", "llama-3.3", "llama-3.2", "llama-3.1", "gpt-oss-120b", "gpt-oss",
    "qwen", "gemma", "mixtral", "mistral", "llama",
)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

SYSTEM_PROMPT = (
    "You are a gentle bedtime storyteller for young children. Write one short, "
    "calming bedtime story of about 300 to 400 words. Use simple, warm language, "
    "short paragraphs, no scary parts, and end with a slow breathing exercise and "
    "a good-night wish. The hero is an animal from the Indonesian rainforest. "
    "Weave the requested theme in as a small, kind lesson."
)


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 RimbaTales/1.0"
)


def http_post_json(url: str, payload: dict, headers: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT, **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


LAST_GROQ_ERROR = "not attempted yet"


def http_get_json(url: str, headers: dict, timeout: int = 15) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, **headers},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discover_groq_model() -> str:
    """Ask Groq which models this key can use, pick the best open-weight chat model."""
    global RESOLVED_MODEL, LAST_GROQ_ERROR
    if RESOLVED_MODEL:
        return RESOLVED_MODEL
    if GROQ_MODEL:
        RESOLVED_MODEL = GROQ_MODEL
        return RESOLVED_MODEL
    try:
        data = http_get_json(
            "https://api.groq.com/openai/v1/models",
            {"Authorization": f"Bearer {GROQ_API_KEY}"},
        )
        ids = [m.get("id", "") for m in data.get("data", [])]
        ids = [i for i in ids if i and "whisper" not in i and "tts" not in i
               and "guard" not in i and "embed" not in i]
        for pref in MODEL_PREFERENCE:
            for mid in ids:
                if pref in mid.lower():
                    RESOLVED_MODEL = mid
                    return RESOLVED_MODEL
        if ids:
            RESOLVED_MODEL = ids[0]
            return RESOLVED_MODEL
        LAST_GROQ_ERROR = "Groq returned no usable chat models"
    except Exception as exc:
        LAST_GROQ_ERROR = f"model discovery failed: {type(exc).__name__}: {exc}"
    return ""


def generate_with_groq(animal: str, theme: str, language: str, child_name: str):
    global LAST_GROQ_ERROR
    if not GROQ_API_KEY:
        LAST_GROQ_ERROR = "GROQ_API_KEY not set"
        return None
    model = discover_groq_model()
    if not model:
        return None
    lang_name = "English" if language == "en" else "Bahasa Indonesia"
    dedication = f" The story is a gift for a child named {child_name}." if child_name else ""
    hero_name = ""
    try:
        hero_name = stories.ANIMALS[animal][language]["name"]
    except Exception:
        hero_name = animal
    user_prompt = (
        f"Write the story in {lang_name}. The hero is {hero_name} (a {animal}). Theme: {theme}.{dedication} "
        "Set it in the Rimba rainforest at bedtime. Put the title alone on the first line, "
        "as plain text with no markdown symbols."
    )
    try:
        data = http_post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.8,
                "max_tokens": 900,
            },
            {"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=30,
        )
        text = data["choices"][0]["message"]["content"].strip()
        LAST_GROQ_ERROR = ""
        if len(text) < 200:
            LAST_GROQ_ERROR = f"model returned short text ({len(text)} chars)"
            return None
        first_line, _, rest = text.partition("\n")
        if len(first_line) < 90 and rest.strip():
            clean_title = first_line.strip().strip("#* ").strip()
            return {"title": clean_title, "text": rest.strip(),
                    "source": f"open-weight model ({model} via Groq)"}
        return {"title": "A Rimba Bedtime Tale", "text": text,
                "source": f"open-weight model ({model} via Groq)"}
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read()[:200].decode("utf-8", "replace")
        except Exception:
            detail = ""
        LAST_GROQ_ERROR = f"HTTP {exc.code}: {detail}"
        return None
    except Exception as exc:
        LAST_GROQ_ERROR = f"{type(exc).__name__}: {exc}"
        return None


NARRATOR_VOICES = {
    "ibu": "21m00Tcm4TlvDq8ikWAM",    # Rachel: Ibu Rimba, a warm mother's voice
    "bapak": "JBFqnCBsd6RMkjVDRZzb",  # George: Bapak Rimba, a warm father's voice
}


def narrate_with_elevenlabs(text: str, voice_key: str = "ibu"):
    voice_id = NARRATOR_VOICES.get(voice_key, ELEVENLABS_VOICE_ID)
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({
            "text": text[:2500],
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.75, "style": 0.2},
        }).encode("utf-8"),
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json",
                 "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def render_index() -> bytes:
    html = (BASE / "index.html").read_text(encoding="utf-8")
    engine_badge = (
        f"Story engine: open-weight model ({GROQ_MODEL} via Groq)" if GROQ_MODEL
        else ("Story engine: open-weight model via Groq (auto-selected)" if GROQ_API_KEY
              else "Story engine: local offline composer")
    )
    voice_badge = "Narrator: ElevenLabs" if ELEVENLABS_API_KEY else "Narrator: your browser voice"
    html = html.replace("{{ENGINE_BADGE}}", engine_badge)
    html = html.replace("{{VOICE_BADGE}}", voice_badge)
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep logs quiet
        pass

    def _send(self, body: bytes, content_type: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj: dict, status: int = 200):
        self._send(json.dumps(obj).encode("utf-8"), "application/json", status)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self._send(render_index(), "text/html; charset=utf-8")
        elif self.path == "/health":
            self._send_json({
                "status": "ok",
                "story_engine": "groq" if GROQ_API_KEY else "local",
                "narrator": "elevenlabs" if ELEVENLABS_API_KEY else "browser",
            })
        elif self.path == "/api/debug":
            self._send_json({
                "groq_configured": bool(GROQ_API_KEY),
                "groq_key_length": len(GROQ_API_KEY),
                "groq_model_env": GROQ_MODEL,
                "resolved_model": RESOLVED_MODEL,
                "last_groq_error": LAST_GROQ_ERROR,
                "elevenlabs_configured": bool(ELEVENLABS_API_KEY),
            })
        elif self.path in ("/static/style.css", "/static/app.js", "/static/cover.jpg"):
            target = BASE / Path(self.path).name
            if self.path.endswith(".css"):
                ctype = "text/css"
            elif self.path.endswith(".jpg"):
                ctype = "image/jpeg"
            else:
                ctype = "application/javascript"
            if target.exists():
                self._send(target.read_bytes(), ctype)
            else:
                self._send(b"not found", "text/plain", 404)
        else:
            self._send(b"not found", "text/plain", 404)

    def do_POST(self):
        if self.path == "/api/story":
            data = self._read_json()
            animal = str(data.get("animal", "elephant")).lower()
            theme = str(data.get("theme", "kindness")).lower()
            language = str(data.get("language", "en")).lower()
            child_name = str(data.get("child_name", "")).strip()[:40]
            result = generate_with_groq(animal, theme, language, child_name)
            if result is None:
                result = stories.compose_story(animal, theme, language, child_name)
                result["source"] = "local offline story engine"
            self._send_json(result)
        elif self.path == "/api/narrate":
            if not ELEVENLABS_API_KEY:
                self._send_json({"fallback": True, "reason": "ELEVENLABS_API_KEY not configured"})
                return
            data = self._read_json()
            text = str(data.get("text", "")).strip()
            voice = str(data.get("voice", "ibu")).lower()
            if not text:
                self._send_json({"error": "empty text"}, 400)
                return
            try:
                audio = narrate_with_elevenlabs(text, voice)
                self._send_json({
                    "audio_base64": base64.b64encode(audio).decode("ascii"),
                    "content_type": "audio/mpeg",
                })
            except Exception as exc:
                self._send_json({"fallback": True, "reason": f"ElevenLabs request failed: {exc}"})
        else:
            self._send(b"not found", "text/plain", 404)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
