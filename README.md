# Rimba Tales 🌙

**Bedtime stories from the rainforest, written and read aloud for you.**

Rimba Tales is a tiny wind-down companion for the most universal lazy moment in
parenting: it is late, your voice is tired, and a small person asks for
*one more story*. Pick an animal hero and one gentle lesson, and Rimba Tales
writes a fresh, calming story, then reads it aloud while you put your feet up.

Heroes come from the Indonesian rainforest (the *Sahabat Rimba*, "Friends of
the Forest"): Nara the Elephant, Raka the Lion Cub, Luma the Owl, Kiki the
Mousedeer and Sasa the Turtle. Stories are available in English and
Bahasa Indonesia, and can be personalised with the child's name.

## How it works

Story generation has two layers, in order of preference:

1. **Open-weight model (live):** when `GROQ_API_KEY` is set, stories are
   written by an open-weight model (Llama 3.3 70B, `llama-3.3-70b-versatile`,
   served by Groq). The model is prompted as a gentle bedtime storyteller:
   simple language, no scary parts, a small kind lesson, and a breathing
   exercise at the end.
2. **Local story engine (offline):** when there is no key (or the request
   fails), `stories.py` composes a story from hand-written scenes: one animal,
   one theme-tied problem, one kind action, one lesson from the moon, and a
   sleepy closing ritual. No network, no key, no cost. The app can *always*
   tell a story.

Narration also has two layers:

1. **ElevenLabs** text-to-speech when `ELEVENLABS_API_KEY` is set
   (`eleven_multilingual_v2`, so Indonesian stories sound Indonesian).
2. **The browser's built-in voice** (Web Speech API) otherwise, which is
   free and runs entirely on the reader's device.

The UI shows a small badge for whichever layers are active, so what you see
is exactly what is running.

## Why open matters here

A bedtime story app that only works while a paid API key has balance is a
bedtime story app that fails on the worst possible night. Making the
open-weight model the writer, and a fully local composer the guaranteed
fallback, means anyone can clone this repo and run a complete, working
storyteller for free, forever, even offline. The commercial voice is an
enhancement, never a single point of failure.

## Run it locally

```bash
python app.py
# open http://localhost:5000
```

No install step: the service runs on the Python 3 standard library alone.

Optional keys (see `.env.example`): copy to `.env` style environment
variables in your shell, or set them in your host's dashboard.

- `GROQ_API_KEY`: free key from Groq Console, enables the open-weight writer.
- `ELEVENLABS_API_KEY`: enables studio narration. In ElevenLabs, open your
  profile and create an API key.
- `ELEVENLABS_VOICE_ID`: override the narrator voice (defaults to Rachel).

## Deploy on Render

This repo ships a `render.yaml` Blueprint:

1. Push this repo to GitHub.
2. In Render, choose **New > Blueprint**, select the repo, and apply.
3. (Optional) fill in `GROQ_API_KEY` and `ELEVENLABS_API_KEY` when prompted.
   Skip them and the app still works with the local engine and browser voice.
4. Open the service URL. Done, go be lazy.

Manual setup works too: create a Web Service from the repo with build command
`true` (there is nothing to install) and start command `python app.py`.

## Project layout

```
app.py            the service (stdlib-only): pages, /api/story, /api/narrate, /health
stories.py        the local offline story engine (animals, themes, scenes)
index.html        the single-page UI
style.css         night-sky styling
app.js            page logic and the browser-voice narration fallback
render.yaml       one-click Render Blueprint
```

## License

MIT. The Rimba characters were first created for the *Sahabat Rimba*
children's video series.
