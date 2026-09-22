# Reel — AI Video Generation Agent

Type what video you want in one sentence. The agent plans it, generates the
visuals and voiceover, and renders a finished MP4.

```
USER PROMPT → LLM PLAN → SCENE VISUALS → VOICEOVER → CAPTIONS → FFMPEG → MP4
```

This is an orchestration layer, not a trained model. It calls out to hosted
AI APIs for each step and stitches the results together with FFmpeg. No part
of the pipeline is hardcoded to a specific topic — the same code path handles
"how a gearbox works", "gradient descent", or "a futuristic city at night".

## What's real vs. fallback

Every external call goes through a small provider abstraction
(`backend/providers.py`) with two implementations:

| Capability | Real backend (needs a key) | Fallback (no key needed) |
|---|---|---|
| Video planning (title, scenes, script, captions) | Anthropic Claude API | Local deterministic planner (keyword reasoning over your prompt) |
| Scene visuals | OpenAI Images API (`gpt-image-1`) | Procedurally generated gradient/typographic scene cards (Pillow) |
| Voiceover | ElevenLabs TTS | Silent audio track of the correct duration |

**The whole pipeline runs and produces a real MP4 with zero API keys
configured** — that's how it was built and tested. Add keys to get an
LLM-written script, AI-generated imagery, and a real voice; nothing else in
the code needs to change.

## Project structure

```
project/
├── backend/
│   ├── main.py            FastAPI app: /generate, /generate/stream (SSE), static /output
│   ├── agent.py            The orchestration pipeline (prompt -> plan -> assets -> video)
│   ├── providers.py         LLM / visual / TTS provider abstraction + fallbacks
│   ├── video_generator.py   FFmpeg assembly (per-scene clip with burned-in captions -> concat)
│   ├── requirements.txt
│   └── output/              Generated jobs land here as output/<job_id>/final.mp4
├── frontend/
│   ├── src/App.jsx          Prompt box, live progress stepper, result + download
│   └── ...                  Vite + React
├── .env.example
└── README.md
```

## Run it

**Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp ../.env.example .env   # fill in whichever keys you have, or leave blank
python3 main.py           # serves http://localhost:8000
```

**Frontend** (separate terminal)

```bash
cd frontend
npm install
npm run dev                # serves http://localhost:5173, proxies API calls to :8000
```

Open http://localhost:5173, type a prompt, hit Generate.

## Try these (same pipeline, no special-casing)

- "Create a 10-second educational video explaining how a gearbox works."
- "Create a 10-second explanation of gradient descent."
- "Create a cinematic 10-second video of a futuristic city at night."
- "Explain how regenerative braking works in 10 seconds."
- "Explain how a BLDC motor works."

## API keys

Copy `.env.example` to `backend/.env`:

```
ANTHROPIC_API_KEY=       # Claude — writes the video plan/script
OPENAI_API_KEY=          # gpt-image-1 — scene visuals
ELEVENLABS_API_KEY=      # narration voiceover
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

Each is independent — you can set just one and the other two stages will
still use their local fallback.

## Notes on scope

This is a working prototype, not a production service: jobs run
synchronously in-request (fine for ~10s videos), there's no auth, database,
or job queue, and the fallback planner is a simple deterministic
introduce→mechanism→result template rather than genuine LLM reasoning. The
provider abstraction is what makes swapping in the real APIs, or a job
queue, or a different image model, a localized change rather than a rewrite.
