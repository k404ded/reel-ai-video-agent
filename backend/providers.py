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
# LLM provider — turns a user prompt into a structured, cinematic video plan
# --------------------------------------------------------------------------

PLANNER_SYSTEM_PROMPT = """You are an elite AI Video Director and Creative Producer for high-end short explainer videos.
Your task is to take a user's natural language request and design a compelling, cinematic, 10-15 second video plan.

Key Director Rules:
1. TOPIC & DOMAIN ANALYSIS:
   - Identify whether the topic is Technical/Engineering (e.g. gearbox, motor, engine), Computational/AI (e.g. gradient descent, neural net), Automotive/Physical (e.g. regenerative braking), or Cinematic/Atmospheric (e.g. futuristic city).
   - Design an authentic, professional visual aesthetic suited to the domain.
   - Technical topics MUST visually depict actual mechanisms, components, cutaways, and physical energy transfer — not vague abstract shapes.
   - Computational topics MUST visually depict 3D mathematical surfaces, loss valleys, optimization paths, data vectors, and contour planes.
   - Cinematic topics MUST feature dramatic lighting, depth of field, volumetric atmosphere, and cinematic framing.

2. VISUAL COHERENCE (CRITICAL):
   - Define a unified "visual_direction": specify color palette, lighting style, rendering medium (e.g. photorealistic 3D technical animation, octane render), and background environment (e.g. sleek dark graphite showroom, modern computation grid).
   - All scenes must share this visual_direction so they appear to come from the exact same production.

3. SCENE BREAKDOWN (2-4 scenes, summing to the target duration):
   - Each scene must have:
     * "duration": duration in seconds (number, typically 3-5 seconds each, summing to target duration).
     * "purpose": what this specific scene communicates in the narrative arc (e.g., establishing mechanism, internal process in action, real-world payoff).
     * "visual_prompt": a rich, photographic/3D prompt describing the subject, materials, camera angle, lighting, and action. CRITICAL: absolutely NO text, NO labels, NO words, NO subtitles inside the visual description. Describe what the camera SEES physically.
     * "camera_direction": movement instruction (e.g., "slow cinematic push-in toward central gear teeth", "smooth horizontal pan revealing gear shaft alignment", "wide pull-back showing full drivetrain").
     * "environment": the specific setting/background (e.g., "dark reflective industrial stage with soft backlighting").
     * "lighting": lighting setup (e.g., "cool cyan rim lights, soft top spotlight highlighting metal bevels").
     * "caption": a punchy lower-third caption (<= 6 words, title case, e.g. "Transferring Engine Power", "Calculating Lowest Loss").
     * "narration": concise, clear, natural spoken sentence that fits the scene duration (~2.5 words per second).

4. STRICT OUTPUT FORMAT:
Respond with ONLY a single JSON object with no markdown formatting, no commentary, strictly conforming to:
{
  "title": "string",
  "topic": "string",
  "duration": number,
  "style": "string",
  "tone": "string",
  "visual_direction": "string (cohesive style, palette, lighting, renderer)",
  "narration": "string (full voiceover narration across all scenes)",
  "scenes": [
    {
      "duration": number,
      "purpose": "string",
      "visual_prompt": "string",
      "camera_direction": "string",
      "environment": "string",
      "lighting": "string",
      "caption": "string",
      "narration": "string"
    }
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
                    "max_tokens": 1800,
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
        async with httpx.AsyncClient(timeout=35) as client:
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
        Deterministic, dependency-free planner used when no LLM key is
        configured. Produces domain-appropriate scene specifications.
        """
        prompt = user_prompt.strip()
        duration = _extract_duration(prompt) or 10
        topic = _extract_topic(prompt)
        style = "cinematic" if any(w in prompt.lower() for w in ["cinematic", "futuristic", "dramatic"]) else "clean educational"
        tone = "energetic" if style == "cinematic" else "clear and informative"
        visual_dir = (
            "Cinematic photorealistic 3D visualization, volumetric atmospheric lighting, deep contrast, 8k render"
            if style == "cinematic" else
            "Clean technical 3D engineering render, dark graphite studio background, metallic reflections, precision lighting"
        )

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
                    "purpose": beat["purpose"],
                    "visual_prompt": beat["visual"],
                    "camera_direction": beat["camera"],
                    "environment": beat["environment"],
                    "lighting": beat["lighting"],
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
            "visual_direction": visual_dir,
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
    t = topic.strip() or "the mechanism"
    t_lower = t.lower()
    is_cinematic = "cinematic" in full_prompt.lower()

    return [
        {
            "purpose": "Establishing overview and core concept",
            "visual": f"A clean, detailed establishing 3D view of {t_lower}, highlighting the primary structure, metallic materials, and realistic scale",
            "camera": "Slow cinematic push-in toward central assembly",
            "environment": "Sleek dark studio stage with subtle reflection" if not is_cinematic else "Sprawling futuristic atmosphere",
            "lighting": "Cool directional rim lighting with soft ambient fill",
            "narration": f"Here is how {t_lower} works.",
            "caption": t[:30].title(),
        },
        {
            "purpose": "Internal process and operating mechanism in action",
            "visual": f"A close-up internal cutaway view showing the working components of {t_lower} in active motion, parts interacting smoothly with authentic physical detail",
            "camera": "Smooth horizontal tracking pan across moving components",
            "environment": "High-tech engineering inspection bay",
            "lighting": "Precision spotlight highlighting friction surfaces and contact points",
            "narration": f"The components work together to transfer power with maximum efficiency.",
            "caption": "Internal Mechanism",
        },
        {
            "purpose": "Application and real-world outcome",
            "visual": f"A dynamic full-system perspective showing {t_lower} delivering output force, smooth mechanical motion, and complete operational payoff",
            "camera": "Wide pull-back reveal showing output action",
            "environment": "Modern integrated testing facility",
            "lighting": "Vibrant dynamic lighting emphasizing speed and power",
            "narration": f"Delivering consistent performance and reliable control.",
            "caption": "Power & Efficiency",
        },
    ]


def _normalize_plan(plan: dict, user_prompt: str) -> dict:
    plan.setdefault("title", "Generated Video")
    plan.setdefault("topic", plan["title"])
    plan.setdefault("style", "clean educational")
    plan.setdefault("tone", "clear and informative")
    plan.setdefault(
        "visual_direction",
        "Photorealistic 3D technical render, studio lighting, high detail, 8k resolution, clean composition"
    )
    scenes = plan.get("scenes") or []
    if not scenes:
        scenes = _reason_about_topic(plan["topic"], user_prompt)
    for i, s in enumerate(scenes):
        s["duration"] = float(s.get("duration", 3.5))
        s.setdefault("purpose", f"Scene {i+1} explanation")
        s.setdefault("visual_prompt", plan["title"])
        s.setdefault("camera_direction", "Slow cinematic push-in")
        s.setdefault("environment", "Clean dark studio background")
        s.setdefault("lighting", "Studio rim lighting")
        s.setdefault("narration", "")
        s.setdefault("caption", "")
    plan["scenes"] = scenes
    plan["duration"] = sum(s["duration"] for s in scenes)
    plan.setdefault("narration", " ".join(s["narration"] for s in scenes))
    return plan


# --------------------------------------------------------------------------
# Visual provider — one high-definition coherent image per scene
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

    async def generate_scene_image(
        self,
        visual_prompt: str,
        index: int,
        out_path: str,
        size=(1920, 1080),
        visual_direction: str = "",
        environment: str = "",
        lighting: str = "",
    ):
        # Build a coherent, high-detail prompt free of text labels
        style_context = visual_direction.strip() if visual_direction else "3D cinematic technical render, octane render"
        env_context = environment.strip() if environment else "clean background"
        light_context = lighting.strip() if lighting else "studio lighting"
        
        # Clean text directives from prompt
        cleaned_prompt = re.sub(r"(?i)\b(with text|labeled with|text saying|words saying|caption)\b.*", "", visual_prompt).strip(" ,.")
        
        enriched_prompt = (
            f"{cleaned_prompt}. Style: {style_context}. Environment: {env_context}. Lighting: {light_context}. "
            f"8k resolution, highly detailed, sharp focus, masterpiece composition. "
            f"No text, no labels, no watermark, no logos, no typography, no blur."
        )

        if OPENAI_API_KEY:
            try:
                await self._generate_with_openai(enriched_prompt, out_path, size)
                self.using_fallback = False
                return
            except Exception as exc:
                print(f"[VisualProvider] OpenAI image call failed ({exc}); using visual generator.")

        # When OpenAI key is not set or fails, generate real topic-relevant visuals via Pollinations
        try:
            seed = 100 + index * 7
            await self._generate_with_pollinations(enriched_prompt, out_path, size, seed=seed)
            return
        except Exception as exc:
            print(f"[VisualProvider] Pollinations visual call failed ({exc}); trying topic visual repository.")

        # Fallback to authentic visual from educational/encyclopedic repository
        try:
            topic = cleaned_prompt.split(",")[0].split(".")[0].strip()
            if len(topic.split()) > 4:
                topic = " ".join(topic.split()[:4])
            await self._generate_with_wikipedia(topic, out_path, size)
            return
        except Exception as exc:
            print(f"[VisualProvider] Topic visual repository failed ({exc}); using procedural fallback.")

        self._generate_fallback(cleaned_prompt, index, out_path, size)

    async def _generate_with_openai(self, visual_prompt: str, out_path: str, size):
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "dall-e-3",
                    "prompt": visual_prompt[:950],
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

    async def _generate_with_pollinations(self, visual_prompt: str, out_path: str, size, seed: int = 42):
        import urllib.parse
        clean_text = re.sub(r"[^a-zA-Z0-9, ]", " ", visual_prompt)
        clean_text = " ".join(clean_text.split())
        if len(clean_text) > 140:
            clean_text = clean_text[:140].rsplit(" ", 1)[0]

        encoded = urllib.parse.quote(clean_text)
        urls = [
            f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&seed={seed}&model=turbo&nologo=true",
            f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&seed={seed}&nologo=true",
        ]
        last_exc = None
        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    img = Image.open(BytesIO(resp.content)).convert("RGB")
                    if img.size != size:
                        img = img.resize(size, Image.Resampling.LANCZOS)
                    img.save(out_path, "PNG", quality=95)
                    self.using_fallback = False
                    return
            except Exception as exc:
                last_exc = exc
                continue
        if last_exc:
            raise last_exc

    async def _generate_with_wikipedia(self, topic: str, out_path: str, size):
        import urllib.parse
        headers = {"User-Agent": "ReelVideoAgent/1.0 (contact@reelagent.ai)"}
        clean_query = re.sub(r"[^a-zA-Z0-9_ ]", "", topic).strip().replace(" ", "_")
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            resp = await client.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query}", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                img_url = (data.get("originalimage") or {}).get("source") or (data.get("thumbnail") or {}).get("source")
                if img_url:
                    img_resp = await client.get(img_url, headers=headers)
                    if img_resp.status_code == 200:
                        img = Image.open(BytesIO(img_resp.content)).convert("RGB")
                        img = img.resize(size, Image.Resampling.LANCZOS)
                        img.save(out_path, "PNG", quality=95)
                        self.using_fallback = False
                        return

            search_resp = await client.get(f"https://en.wikipedia.org/w/rest.php/v1/search/page?q={urllib.parse.quote(topic)}&limit=3", headers=headers)
            if search_resp.status_code == 200:
                pages = search_resp.json().get("pages", [])
                for p in pages:
                    thumb = p.get("thumbnail") or {}
                    url = thumb.get("url")
                    if url:
                        if url.startswith("//"):
                            url = "https:" + url
                        larger_url = re.sub(r"/\d+px-", "/1280px-", url)
                        try:
                            img_resp = await client.get(larger_url, headers=headers)
                            if img_resp.status_code != 200:
                                img_resp = await client.get(url, headers=headers)
                            if img_resp.status_code == 200:
                                img = Image.open(BytesIO(img_resp.content)).convert("RGB")
                                img = img.resize(size, Image.Resampling.LANCZOS)
                                img.save(out_path, "PNG", quality=95)
                                self.using_fallback = False
                                return
                        except Exception:
                            continue
        raise RuntimeError("No suitable image found in visual repository")

    def _generate_fallback(self, visual_prompt: str, index: int, out_path: str, size):
        palettes = [
            ((15, 20, 32), (56, 75, 160)),
            ((10, 24, 30), (32, 140, 130)),
            ((28, 14, 38), (170, 60, 120)),
            ((12, 26, 18), (80, 160, 95)),
            ((30, 18, 12), (180, 110, 45)),
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

        try:
            if os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 52)
                small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
            elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            else:
                font = ImageFont.load_default()
                small_font = font
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        wrapped = textwrap.fill(visual_prompt, width=36)
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

        try:
            await self._synthesize_with_edgetts(clean_text, out_path)
            return True
        except Exception as exc:
            print(f"[TTSProvider] Voice synthesis failed ({exc}); using silent fallback.")

        self._silence(out_path, min_duration)
        return False

    async def _synthesize_with_edgetts(self, text: str, out_path: str):
        import edge_tts
        # Clear, engaging voice with slightly optimized pacing
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural", rate="+3%")
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
