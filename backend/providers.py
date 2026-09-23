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

PLANNER_SYSTEM_PROMPT = """You are an elite Creative Video Director and Motion Designer producing Envato-level, high-impact short explainer videos.
Your goal is to design a visually cohesive, cinematic, 10-15 second video that feels like ONE continuous, professionally produced micro-documentary or commercial.

Key Director Rules:
1. 3-BEAT STORYBOARD STRUCTURE (CRITICAL):
   Every video MUST follow a real cinematic narrative arc across 3 scenes:
   - BEAT 1: HOOK (0.0s - 3.5s)
     * Purpose: Immediately establish the core subject visually. The first second must unmistakably communicate what the video is about.
     * Framing: Cinematic establishing close-up or macro hero shot.
     * Beat role: "HOOK"
     * Category Tag: e.g. "HOW IT WORKS" or "THE CORE CONCEPT"
   - BEAT 2: DYNAMIC MECHANISM / TRANSFORMATION (3.5s - 7.5s)
     * Purpose: Reveal the core process, internal movement, or functional interaction in motion.
     * Framing: Detailed cutaway, dynamic angle, or tracking shot of parts working together.
     * Beat role: "DYNAMIC_MECHANISM"
     * Category Tag: e.g. "INTERNAL PROCESS" or "TORQUE RATIOS"
   - BEAT 3: PAYOFF & OUTCOME (7.5s - 10.5s)
     * Purpose: Show the resulting output, systemic power delivery, or key takeaway.
     * Framing: Dynamic wide reveal or full-system harmony.
     * Beat role: "PAYOFF"
     * Category Tag: e.g. "KEY TAKEAWAY" or "FINAL DRIVE"

2. SHARED VISUAL ANCHOR (100% VISUAL COHERENCE):
   To prevent scenes from looking like random disconnected images, you MUST define a single "shared_visual_anchor" used across ALL scenes:
   - "color_palette": array of 3 harmonized colors (e.g. ["#0b0f19 deep graphite", "#0ea5e9 electric cyan", "#f59e0b warm friction amber"])
   - "lighting_setup": uniform cinematic lighting language (e.g. "45-degree volumetric key spotlight with razor-sharp cyan rim lighting")
   - "primary_material": physical materials (e.g. "brushed gunmetal steel with polished chrome bevels and translucent oil")
   - "environment_aesthetic": consistent studio stage or setting (e.g. "minimalist dark technical showroom with glossy mirror floor")
   Every scene's visual_prompt MUST reuse this exact aesthetic and material language!

3. TWO-TIER PROFESSIONAL TYPOGRAPHY:
   - "category_tag": short, stylish uppercase context tag (1-3 words, e.g. "HOW IT WORKS", "TORQUE MULTIPLICATION", "FINAL DRIVE").
   - "caption": punchy, concise lower-third headline (3-5 words, e.g. "Interlocking Power Transfer", "Converting Speed to Torque").
   - Never put full sentences in captions.

4. NARRATION CADENCE:
   - Paced for professional voiceover (~2.2 words per second).
   - Natural spoken rhythm with pauses between beats.

5. VISUAL PROMPT DISCIPLINE:
   - Describe pure physical cinematography: subject, composition, depth of field, 16:9 widescreen framing, lighting, materials, and motion.
   - Absolutely NO text, NO labels, NO logos, NO watermark inside the image prompt.

6. STRICT JSON OUTPUT FORMAT:
Respond with ONLY a single JSON object with no markdown fences, strictly conforming to:
{
  "title": "string",
  "topic": "string",
  "duration": number,
  "style": "string",
  "visual_direction": "string",
  "shared_visual_anchor": {
    "color_palette": ["string", "string", "string"],
    "lighting_setup": "string",
    "primary_material": "string",
    "environment_aesthetic": "string"
  },
  "narration": "string (full voiceover narration)",
  "scenes": [
    {
      "duration": number,
      "beat_role": "HOOK",
      "purpose": "string",
      "category_tag": "string",
      "caption": "string",
      "visual_prompt": "string",
      "camera_direction": "string",
      "environment": "string",
      "lighting": "string",
      "narration": "string"
    },
    {
      "duration": number,
      "beat_role": "DYNAMIC_MECHANISM",
      "purpose": "string",
      "category_tag": "string",
      "caption": "string",
      "visual_prompt": "string",
      "camera_direction": "string",
      "environment": "string",
      "lighting": "string",
      "narration": "string"
    },
    {
      "duration": number,
      "beat_role": "PAYOFF",
      "purpose": "string",
      "category_tag": "string",
      "caption": "string",
      "visual_prompt": "string",
      "camera_direction": "string",
      "environment": "string",
      "lighting": "string",
      "narration": "string"
    }
  ]
}
"""


from director import EducationalDirectorEngine, EducationalStoryboard


class LLMProvider:
    """Specialized Educational Video Director that plans structurally correct educational videos."""

    def __init__(self):
        self.engine = EducationalDirectorEngine()
        self.using_fallback = self.engine.using_fallback

    async def plan_video(self, user_prompt: str) -> dict:
        storyboard = await self.engine.plan_video(user_prompt)
        self.using_fallback = self.engine.using_fallback
        plan = storyboard.to_dict()

        # Ensure full backward compatibility with agent.py, frontend, and Streamlit
        plan.setdefault("style", "educational instruction")
        plan.setdefault("narration", storyboard.script)
        for i, s in enumerate(plan.get("scenes", [])):
            s.setdefault("index", i)
            s.setdefault("caption", s.get("on_screen_text", f"Scene {i+1}"))
            s.setdefault("visual_prompt", f"{s.get('subject', '')}: {s.get('action', '')}. {s.get('technical_content', '')}")
            s.setdefault("camera_direction", s.get("camera", "Slow cinematic push-in"))
            s.setdefault("beat_role", s.get("visual_type", "EDUCATIONAL_SCENE").upper())
            s.setdefault("category_tag", storyboard.content_type.replace("_", " "))
        return plan


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
            "beat_role": "HOOK",
            "category_tag": "HOW IT WORKS",
            "purpose": "Establishing overview and core concept",
            "visual": f"A clean, detailed establishing 3D view of {t_lower}, highlighting the primary structure, metallic materials, and realistic scale",
            "camera": "Slow cinematic push-in toward central assembly",
            "environment": "Sleek dark studio stage with subtle reflection" if not is_cinematic else "Sprawling futuristic atmosphere",
            "lighting": "Cool directional rim lighting with soft ambient fill",
            "narration": f"Here is how {t_lower} works.",
            "caption": t[:30].title(),
        },
        {
            "beat_role": "DYNAMIC_MECHANISM",
            "category_tag": "CORE DYNAMIC",
            "purpose": "Internal process and operating mechanism in action",
            "visual": f"A close-up internal cutaway view showing the working components of {t_lower} in active motion, parts interacting smoothly with authentic physical detail",
            "camera": "Smooth horizontal tracking pan across moving components",
            "environment": "High-tech engineering inspection bay",
            "lighting": "Precision spotlight highlighting friction surfaces and contact points",
            "narration": f"The components work together to transfer power with maximum efficiency.",
            "caption": "Internal Mechanism",
        },
        {
            "beat_role": "PAYOFF",
            "category_tag": "KEY TAKEAWAY",
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
    plan.setdefault(
        "shared_visual_anchor",
        {
            "color_palette": ["#0b0f19 deep graphite", "#0ea5e9 electric cyan", "#f59e0b friction amber"],
            "lighting_setup": "Volumetric key spotlight with high-contrast cyan rim lighting",
            "primary_material": "Brushed gunmetal steel and polished chrome bevels",
            "environment_aesthetic": "Minimalist dark technical showroom with mirror reflection",
        }
    )

    scenes = plan.get("scenes") or []
    if not scenes:
        scenes = _reason_about_topic(plan["topic"], user_prompt)
    
    roles = ["HOOK", "DYNAMIC_MECHANISM", "PAYOFF"]
    default_tags = ["HOW IT WORKS", "CORE DYNAMIC", "FINAL TAKEAWAY"]

    for i, s in enumerate(scenes):
        s["duration"] = float(s.get("duration", 3.5))
        s.setdefault("beat_role", roles[i % len(roles)])
        s.setdefault("category_tag", default_tags[i % len(default_tags)])
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
    Fallback: encyclopedic visual search or procedurally generated scene cards.
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
        shared_visual_anchor: dict = None,
        visual_type: str = "",
        shot_type: str = "",
        action: str = "",
        technical_content: str = "",
    ):
        # Build domain-specific educational prompt prefix
        vtype = (visual_type or "").lower()
        if "workstation" in vtype or "presenter" in vtype:
            prefix = "Photorealistic medium shot of a realistic professional engineer working at a computer workstation, monitors visible displaying software and technical diagrams, "
        elif "software" in vtype or "screen" in vtype or "viewport" in vtype:
            prefix = "High-resolution software user interface screen capture, clean modern CAD and technical software workspace, "
        elif "mathematical" in vtype:
            prefix = "Clean scientific 3D mathematical visualization, coordinate grid lines, contoured loss surface, gradient vectors, "
        elif "technical" in vtype:
            prefix = "High-detail 3D technical engineering visualization, industrial CAD assembly, precision mechanical cutaway, "
        else:
            prefix = "Clean educational technical 3D visualization, "

        style_context = visual_direction.strip() if visual_direction else "photorealistic educational technical render, studio lighting, octane render"
        env_context = environment.strip() if environment else "engineering laboratory with monitors"
        light_context = lighting.strip() if lighting else "cinematic studio lighting with subtle rim light"

        cleaned_prompt = re.sub(r"(?i)\b(with text|labeled with|text saying|words saying|caption)\b.*", "", visual_prompt).strip(" ,.")
        action_context = f" Action: {action}." if action else ""
        tech_context = f" Technical Details: {technical_content}." if technical_content else ""

        enriched_prompt = (
            f"{prefix}{cleaned_prompt}.{action_context}{tech_context} "
            f"Framing: {shot_type or 'medium shot'}. Style: {style_context}. Environment: {env_context}. Lighting: {light_context}. "
            f"16:9 widescreen composition, 8k resolution, highly detailed, sharp focus, masterpiece composition. "
            f"No text, no labels, no watermark, no logos, no typography, no blur, no decorative fantasy."
        )

        if OPENAI_API_KEY:
            try:
                await self._generate_with_openai(enriched_prompt, out_path, size)
                self.using_fallback = False
                return
            except Exception as exc:
                print(f"[VisualProvider] OpenAI image call failed ({exc}); using visual generator.")

        # Real topic-relevant visuals via Pollinations
        try:
            seed = 100 + index * 7
            await self._generate_with_pollinations(enriched_prompt, out_path, size, seed=seed)
            return
        except Exception as exc:
            print(f"[VisualProvider] Pollinations visual call failed ({exc}); trying topic repository.")

        # Fallback to authentic visual from educational repository
        try:
            topic = cleaned_prompt.split(",")[0].split(".")[0].strip()
            if len(topic.split()) > 4:
                topic = " ".join(topic.split()[:4])
            await self._generate_with_wikipedia(topic, out_path, size)
            return
        except Exception as exc:
            print(f"[VisualProvider] Topic visual repository failed ({exc}); using procedural fallback.")

        self._generate_fallback(cleaned_prompt, index, out_path, size, visual_type, shot_type, technical_content)

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

    def _generate_fallback(self, visual_prompt: str, index: int, out_path: str, size, visual_type: str = "", shot_type: str = "", technical_content: str = ""):
        # Technical blueprint / engineering card aesthetic
        img = Image.new("RGB", size, (11, 14, 20))
        draw = ImageDraw.Draw(img)

        # Draw technical coordinate grid
        grid_color = (30, 41, 59)
        step = 80
        for x in range(0, size[0], step):
            draw.line([(x, 0), (x, size[1])], fill=grid_color, width=1)
        for y in range(0, size[1], step):
            draw.line([(0, y), (size[0], y)], fill=grid_color, width=1)

        # Corner technical registration marks
        accent = (56, 189, 248)
        bracket_len = 30
        for cx, cy in [(40, 40), (size[0] - 40, 40), (40, size[1] - 40), (size[0] - 40, size[1] - 40)]:
            dx = 1 if cx == 40 else -1
            dy = 1 if cy == 40 else -1
            draw.line([(cx, cy), (cx + dx * bracket_len, cy)], fill=accent, width=2)
            draw.line([(cx, cy), (cx, cy + dy * bracket_len)], fill=accent, width=2)

        # Central container box
        box_w, box_h = size[0] - 240, size[1] - 240
        bx1 = (size[0] - box_w) // 2
        by1 = (size[1] - box_h) // 2
        draw.rectangle([(bx1, by1), (bx1 + box_w, by1 + box_h)], outline=(51, 65, 85), width=2)

        # Header tag bar
        draw.rectangle([(bx1, by1), (bx1 + box_w, by1 + 60)], fill=(15, 23, 42))
        tag_text = f"SCENE {index + 1} // {visual_type.upper() or 'TECHNICAL INSTRUCTION'} // {shot_type.upper() or 'OVERVIEW'}"
        draw.text((bx1 + 24, by1 + 20), tag_text, fill=accent)

        try:
            if os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 46)
                small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26)
            else:
                font = ImageFont.load_default()
                small_font = font
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        # Main prompt text wrapped inside box
        wrapped = textwrap.fill(visual_prompt, width=45)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=14)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size[0] - tw) / 2
        y = by1 + 100
        draw.multiline_text((x, y), wrapped, font=font, fill=(248, 250, 252), align="center", spacing=14)

        # Technical specification readout
        if technical_content:
            tech_wrapped = textwrap.fill(f"TECHNICAL FOCUS: {technical_content}", width=60)
            draw.multiline_text((bx1 + 40, by1 + box_h - 90), tech_wrapped, font=small_font, fill=(148, 163, 184))

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
