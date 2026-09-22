"""
Provider abstraction layer.

Every external capability the agent needs (LLM planning, visual generation,
text-to-speech) is accessed through a small provider interface. Each provider
has a "real" implementation that calls a hosted API when a key is configured,
and a local fallback implementation that requires no network access or key at
all. This keeps the pipeline runnable end-to-end for the prototype/demo, and
lets you drop in real API keys later without touching agent.py or main.py.
"""

import os
import json
import re
import textwrap
from io import BytesIO
from typing import Optional

import httpx
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

# Load env variables from backend/.env or root .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel" default
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Automatically detect if a Gemini key was set as ANTHROPIC_API_KEY
if not GEMINI_API_KEY and ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.startswith("AQ."):
    GEMINI_API_KEY = ANTHROPIC_API_KEY
    ANTHROPIC_API_KEY = None

# Streamlit Community Cloud secrets support
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        if not GEMINI_API_KEY and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        if not ANTHROPIC_API_KEY and "ANTHROPIC_API_KEY" in st.secrets:
            ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
        if not OPENAI_API_KEY and "OPENAI_API_KEY" in st.secrets:
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
        if not ELEVENLABS_API_KEY and "ELEVENLABS_API_KEY" in st.secrets:
            ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
except Exception:
    pass


# --------------------------------------------------------------------------
# LLM provider — turns a user prompt into a structured video plan
# --------------------------------------------------------------------------

PLANNER_SYSTEM_PROMPT = """You are a video planning agent inside an automated \
AI video generation pipeline. Given a user's natural-language request for a \
short video, produce a structured JSON video plan.

Rules:
- Infer topic, purpose, visual style, tone, and duration from the request. \
If the user gives a duration, use it; otherwise default to 10 seconds.
- Break the video into 2-5 scenes whose durations sum to the total duration.
- Every scene needs: duration (seconds, number), visual_prompt (a concrete, \
literal description an image-generation model could render — no abstract \
jargon, describe what is actually seen), narration (a short spoken line for \
that scene), and caption (a very short on-screen text, <=8 words).
- Reason dynamically about the actual subject matter. Never reuse a canned \
template — the visuals and narration must be specific to what the user asked \
for.
- Respond with ONLY a single JSON object, no markdown fences, no commentary, \
matching exactly this shape:
{
  "title": "string",
  "topic": "string",
  "duration": number,
  "style": "string",
  "tone": "string",
  "narration": "string (full narration, all scenes concatenated)",
  "scenes": [
    {"duration": number, "visual_prompt": "string", "narration": "string", "caption": "string"}
  ]
}
"""


class LLMProvider:
    """Wraps whichever LLM backend is configured (Anthropic or Gemini, with local fallback)."""

    def __init__(self):
        has_anthropic = bool(ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith("AQ."))
        has_gemini = bool(GEMINI_API_KEY)
        self.using_fallback = not (has_anthropic or has_gemini)

    async def plan_video(self, user_prompt: str) -> dict:
        if ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith("AQ."):
            try:
                plan = await self._plan_with_anthropic(user_prompt)
                self.using_fallback = False
                return plan
            except Exception as exc:  # network/key/parse failure -> degrade gracefully
                print(f"[LLMProvider] Anthropic call failed ({exc}); trying alternative.")

        if GEMINI_API_KEY:
            try:
                plan = await self._plan_with_gemini(user_prompt)
                self.using_fallback = False
                return plan
            except Exception as exc:
                print(f"[LLMProvider] Gemini call failed ({exc}); using fallback planner.")

        self.using_fallback = True
        return self._plan_with_fallback(user_prompt)

    async def _plan_with_anthropic(self, user_prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 1500,
                    "system": PLANNER_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(
                block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
            )
            text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
            plan = json.loads(text)
            return _normalize_plan(plan, user_prompt)

    async def _plan_with_gemini(self, user_prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            last_err = None
            full_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\nUser Request: {user_prompt}"
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

            for model in ["gemini-3-flash-preview", "gemini-3.5-flash-lite", "gemini-3.6-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
                    plan = json.loads(text)
                    return _normalize_plan(plan, user_prompt)
                except Exception as exc:
                    last_err = exc
                    continue
            raise last_err or RuntimeError("All Gemini models failed")

    def _plan_with_fallback(self, user_prompt: str) -> dict:
        """
        A deterministic, dependency-free planner used when no LLM key is
        configured. It does lightweight keyword reasoning over the prompt so
        the demo still produces a *topic-specific* plan rather than a static
        template, without calling any external service.
        """
        prompt = user_prompt.strip()
        duration = _extract_duration(prompt) or 10
        topic = _extract_topic(prompt)
        style = "cinematic" if any(w in prompt.lower() for w in ["cinematic", "futuristic", "dramatic"]) else "clean educational"
        tone = "energetic" if style == "cinematic" else "clear and informative"

        beats = _reason_about_topic(topic, prompt)
        n = len(beats)
        base = duration // n
        remainder = duration - base * n
        scenes = []
        for i, beat in enumerate(beats):
            d = base + (1 if i < remainder else 0)
            scenes.append(
                {
                    "duration": max(d, 1),
                    "visual_prompt": beat["visual"],
                    "narration": beat["narration"],
                    "caption": beat["caption"],
                }
            )

        plan = {
            "title": topic.title() if topic else "Generated Video",
            "topic": topic,
            "duration": duration,
            "style": style,
            "tone": tone,
            "narration": " ".join(s["narration"] for s in scenes),
            "scenes": scenes,
        }
        return _normalize_plan(plan, user_prompt)


def _extract_duration(prompt: str) -> Optional[int]:
    m = re.search(r"(\d+)\s*[- ]?second", prompt.lower())
    if m:
        return int(m.group(1))
    return None


_STOPWORDS = [
    "create", "make", "generate", "a", "an", "the", "short", "cinematic",
    "educational", "video", "of", "explaining", "explain", "how", "works",
    "work", "please", "can", "you",
]


def _extract_topic(prompt: str) -> str:
    p = prompt.strip()
    p = re.sub(r"(?i)\bin\s+\d+[- ]?seconds?\b", " ", p)
    p = re.sub(r"(?i)\b\d+[- ]?seconds?\b", " ", p)
    stop_pattern = r"(?i)\b(" + "|".join(_STOPWORDS) + r")\b"
    p = re.sub(stop_pattern, " ", p)
    p = re.sub(r"\s+", " ", p).strip(" .")
    return p if p else prompt.strip(" .")


def _reason_about_topic(topic: str, full_prompt: str) -> list:
    """
    Very small piece of "reasoning": build a 3-beat narrative arc
    (introduce -> mechanism -> outcome) around whatever noun phrase the
    topic resolves to, so different topics produce genuinely different
    scene content without hardcoding specific subjects like "gearbox" or
    "gradient descent".
    """
    t = topic.strip() or "the subject"
    t_lower = t.lower()

    return [
        {
            "visual": f"A clean, well-lit establishing shot introducing {t_lower}, "
                      f"labelled clearly, centered composition, soft studio lighting, "
                      f"minimal background, {('dramatic wide shot, moody lighting' if 'cinematic' in full_prompt.lower() else 'bright flat-design illustration style')}",
            "narration": f"Let's take a look at {t_lower}.",
            "caption": t[:40],
        },
        {
            "visual": f"A close-up diagrammatic view showing the internal mechanism or process "
                      f"of {t_lower} in action, arrows indicating motion or flow, "
                      f"labelled parts, clean vector-style illustration",
            "narration": f"Here's how {t_lower} actually works, step by step.",
            "caption": "How it works",
        },
        {
            "visual": f"A final wide shot showing the completed result or effect of {t_lower}, "
                      f"satisfying and clear payoff, bright and polished look",
            "narration": f"And that's the core idea behind {t_lower}.",
            "caption": "The result",
        },
    ]


def _normalize_plan(plan: dict, user_prompt: str) -> dict:
    plan.setdefault("title", "Generated Video")
    plan.setdefault("topic", plan["title"])
    plan.setdefault("style", "clean educational")
    plan.setdefault("tone", "clear and informative")
    scenes = plan.get("scenes") or []
    if not scenes:
        scenes = _reason_about_topic(plan["topic"], user_prompt)
    for s in scenes:
        s["duration"] = float(s.get("duration", 3))
        s.setdefault("visual_prompt", plan["title"])
        s.setdefault("narration", "")
        s.setdefault("caption", "")
    plan["scenes"] = scenes
    plan["duration"] = sum(s["duration"] for s in scenes)
    plan.setdefault("narration", " ".join(s["narration"] for s in scenes))
    return plan


# --------------------------------------------------------------------------
# Visual provider — one image per scene
# --------------------------------------------------------------------------

class VisualProvider:
    """
    Real backend: OpenAI Images API (if OPENAI_API_KEY is set).
    Topic-specific AI visuals: Pollinations.ai generates real scene imagery
    (Flux / SD) directly matching the LLM visual prompt so the video actually
    represents the subject matter.
    Fallback: procedurally generated scene cards using Pillow with system fonts.
    """

    def __init__(self):
        self.using_fallback = OPENAI_API_KEY is None

    async def generate_scene_image(self, visual_prompt: str, index: int, out_path: str, size=(1920, 1080)):
        if OPENAI_API_KEY:
            try:
                await self._generate_with_openai(visual_prompt, out_path, size)
                self.using_fallback = False
                return
            except Exception as exc:
                print(f"[VisualProvider] OpenAI image call failed ({exc}); using visual generator.")

        # When OpenAI key is not set or fails, generate real topic-relevant visuals
        try:
            await self._generate_with_pollinations(visual_prompt, out_path, size)
            return
        except Exception as exc:
            print(f"[VisualProvider] Pollinations visual call failed ({exc}); using procedural fallback.")

        self._generate_fallback(visual_prompt, index, out_path, size)

    async def _generate_with_openai(self, visual_prompt: str, out_path: str, size):
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "dall-e-3",
                    "prompt": visual_prompt,
                    "size": "1024x1024",
                    "n": 1,
                    "response_format": "b64_json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            import base64
            b64 = data["data"][0]["b64_json"]
            img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGB")
            if img.size != size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(out_path, "PNG", quality=95)

    async def _generate_with_pollinations(self, visual_prompt: str, out_path: str, size):
        import urllib.parse
        encoded = urllib.parse.quote(visual_prompt[:200])
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true"
        async with httpx.AsyncClient(timeout=12) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            if img.size != size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(out_path, "PNG", quality=95)

    def _generate_fallback(self, visual_prompt: str, index: int, out_path: str, size):
        palettes = [
            ((20, 24, 38), (86, 97, 240)),
            ((15, 32, 39), (44, 200, 178)),
            ((36, 16, 46), (233, 89, 154)),
            ((10, 30, 20), (110, 220, 130)),
            ((40, 20, 10), (240, 150, 60)),
        ]
        top, bottom = palettes[index % len(palettes)]
        img = Image.new("RGB", size, top)
        draw = ImageDraw.Draw(img)
        for y in range(size[1]):
            t = y / size[1]
            r = int(top[0] + (bottom[0] - top[0]) * t)
            g = int(top[1] + (bottom[1] - top[1]) * t)
            b = int(top[2] + (bottom[2] - top[2]) * t)
            draw.line([(0, y), (size[0], y)], fill=(r, g, b))

        # soft decorative circles for visual interest
        overlay = Image.new("RGBA", size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        for i in range(6):
            cx = (index * 137 + i * 260) % size[0]
            cy = (index * 91 + i * 180) % size[1]
            r = 80 + (i * 37) % 220
            odraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 14))
        overlay = overlay.filter(ImageFilter.GaussianBlur(30))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Wrapped prompt text as a stand-in for the described scene
        try:
            if os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 54)
                small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
            elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            else:
                font = ImageFont.load_default()
                small_font = font
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        wrapped = textwrap.fill(visual_prompt, width=34)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=14)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size[0] - tw) / 2
        y = (size[1] - th) / 2
        draw.multiline_text((x, y), wrapped, font=font, fill=(255, 255, 255), align="center", spacing=14)
        draw.text((60, size[1] - 70), f"Scene {index + 1}", font=small_font, fill=(255, 255, 255, 180))

        img.save(out_path, quality=92)


# --------------------------------------------------------------------------
# TTS provider — narration audio
# --------------------------------------------------------------------------

class TTSProvider:
    """
    Real backend: ElevenLabs (if ELEVENLABS_API_KEY set).
    Smart speech fallback: edge-tts synthesizes natural voiceover.
    Silent fallback: silent audio track of the right duration.
    """

    def __init__(self):
        self.using_fallback = ELEVENLABS_API_KEY is None

    async def synthesize(self, text: str, out_path: str, min_duration: float = 1.0) -> bool:
        """Returns True if real speech audio was written, False if silence."""
        clean_text = text.strip()
        if not clean_text:
            self._silence(out_path, min_duration)
            return False

        if ELEVENLABS_API_KEY:
            try:
                await self._synthesize_with_elevenlabs(clean_text, out_path)
                self.using_fallback = False
                return True
            except Exception as exc:
                print(f"[TTSProvider] ElevenLabs call failed ({exc}); trying voice fallback.")

        # Use neural TTS for natural human voiceover
        try:
            await self._synthesize_with_edgetts(clean_text, out_path)
            return True
        except Exception as exc:
            print(f"[TTSProvider] Voice synthesis failed ({exc}); using silent fallback.")

        self._silence(out_path, min_duration)
        return False

    async def _synthesize_with_edgetts(self, text: str, out_path: str):
        import edge_tts
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        await communicate.save(out_path)

    async def _synthesize_with_elevenlabs(self, text: str, out_path: str):
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "accept": "audio/mpeg",
                    "content-type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                },
            )
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(resp.content)

    def _silence(self, out_path: str, duration: float):
        import subprocess
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-t", str(max(duration, 0.5)), "-q:a", "9", "-acodec", "libmp3lame", out_path,
            ],
            check=True,
            capture_output=True,
        )
