"""
agent.py — the orchestration layer.

Upgraded to a high-quality video production agent:
USER PROMPT -> DIRECTOR PLAN -> QUALITY CONTROL -> COHERENT VISUALS ->
VOICEOVER -> KEN BURNS MOTION & CAPTIONS -> FINAL HD MP4
"""

import os
import uuid
import re
import asyncio
from dataclasses import dataclass, field
from typing import Callable, Optional

from providers import LLMProvider, VisualProvider, TTSProvider
from video_generator import assemble_video

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


@dataclass
class SceneAsset:
    index: int
    duration: float
    beat_role: str
    purpose: str
    category_tag: str
    caption: str
    visual_prompt: str
    camera_direction: str
    environment: str
    lighting: str
    narration: str
    image_path: str
    audio_path: str
    has_real_voice: bool


@dataclass
class GenerationResult:
    job_id: str
    title: str
    description: str
    style: str
    visual_direction: str
    shared_visual_anchor: dict
    script: str
    scenes: list
    video_path: str
    using_fallback_llm: bool
    using_fallback_visual: bool
    using_fallback_tts: bool


ProgressCallback = Optional[Callable[[str], "asyncio.Future"]]


def validate_and_refine_plan(plan: dict, user_prompt: str) -> dict:
    """
    Quality Control validation step:
    - Verifies duration and scene balance
    - Enforces 3-beat visual storytelling structure (HOOK -> DYNAMIC -> PAYOFF)
    - Validates visual prompts for physical clarity and strips unwanted text instructions
    - Trims or tightens narration to match spoken cadence (~2.2 words per second)
    - Ensures punchy, clean lower-third captions (3-5 words) and category tags
    """
    scenes = plan.get("scenes") or []
    if not scenes:
        return plan

    # 1. Duration validation
    target_dur = plan.get("duration", 10.0)
    current_total = sum(s.get("duration", 3.0) for s in scenes)
    if current_total > 0 and abs(current_total - target_dur) > 0.5:
        ratio = target_dur / current_total
        for s in scenes:
            s["duration"] = round(max(s.get("duration", 3.0) * ratio, 2.5), 1)
        plan["duration"] = sum(s["duration"] for s in scenes)

    # 2. Shared visual anchor validation
    if not plan.get("shared_visual_anchor"):
        plan["shared_visual_anchor"] = {
            "color_palette": ["#0b0f19 deep graphite", "#0ea5e9 electric cyan", "#f59e0b friction amber"],
            "lighting_setup": "Volumetric key spotlight with high-contrast cyan rim lighting",
            "primary_material": "Brushed gunmetal steel and polished chrome bevels",
            "environment_aesthetic": "Minimalist dark technical showroom with mirror reflection",
        }

    # 3. Refine each scene
    roles = ["HOOK", "DYNAMIC_MECHANISM", "PAYOFF"]
    default_tags = ["HOW IT WORKS", "CORE DYNAMIC", "KEY TAKEAWAY"]

    for i, s in enumerate(scenes):
        s["duration"] = max(2.5, min(s.get("duration", 3.5), 6.0))

        # Beat role & category tag
        if not s.get("beat_role"):
            s["beat_role"] = roles[i % len(roles)]
        if not s.get("category_tag"):
            s["category_tag"] = default_tags[i % len(default_tags)]
        else:
            s["category_tag"] = s["category_tag"].upper().strip()

        # Purpose fallback
        if not s.get("purpose"):
            s["purpose"] = f"Beat {i+1}: {s['beat_role'].replace('_', ' ').title()}"

        # Camera direction fallback
        if not s.get("camera_direction"):
            default_cameras = [
                "Slow cinematic push-in toward central focal point",
                "Smooth horizontal pan across structural components",
                "Wide pull-back reveal showing complete assembly",
            ]
            s["camera_direction"] = default_cameras[i % len(default_cameras)]

        # Environment and lighting
        if not s.get("environment"):
            s["environment"] = plan["shared_visual_anchor"].get("environment_aesthetic", "Minimalist dark technical stage")
        if not s.get("lighting"):
            s["lighting"] = plan["shared_visual_anchor"].get("lighting_setup", "Studio rim lighting")

        # Visual prompt: strip on-image text demands
        vp = s.get("visual_prompt", plan.get("title", ""))
        vp_clean = re.sub(r"(?i)\b(with text|labeled with|text saying|words saying|caption)\b.*", "", vp).strip(" ,.")
        if len(vp_clean) < 20:
            vp_clean = f"A detailed 3D representation of {plan.get('topic', 'the subject')}, showing authentic physical structure and materials"
        s["visual_prompt"] = vp_clean

        # Caption: clean and punchy (3-5 words)
        cap = s.get("caption", "").strip()
        words = cap.split()
        if len(words) > 5:
            s["caption"] = " ".join(words[:5])
        elif not cap:
            s["caption"] = plan.get("topic", "Overview").title()

        # Narration: ensure spoken cadence fits duration (~2.2 words per sec)
        narr = s.get("narration", "").strip()
        narr_words = narr.split()
        max_words = int(s["duration"] * 2.6)
        if len(narr_words) > max_words:
            s["narration"] = " ".join(narr_words[:max_words]) + "."

    plan["scenes"] = scenes
    return plan


async def generate_video(user_prompt: str, on_progress: ProgressCallback = None) -> GenerationResult:
    job_id = uuid.uuid4().hex[:10]
    job_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    async def emit(stage: str):
        if on_progress:
            await on_progress(stage)

    llm = LLMProvider()
    visual = VisualProvider()
    tts = TTSProvider()

    # 1. Understanding & Intelligent Planning
    await emit("understanding")
    await emit("planning")
    raw_plan = await llm.plan_video(user_prompt)

    # 2. Quality Control & Validation Step
    await emit("quality_check")
    plan = validate_and_refine_plan(raw_plan, user_prompt)

    # 3. Script / Narration ready
    await emit("scripting")

    # 4. Scenes Setup
    await emit("scenes")
    scenes_raw = plan["scenes"]
    visual_direction = plan.get("visual_direction", "")
    shared_visual_anchor = plan.get("shared_visual_anchor", {})

    # 5. High-Quality Visuals & Audio Generation
    await emit("visuals")
    await emit("audio")

    scene_assets: list[SceneAsset] = []
    for i, scene in enumerate(scenes_raw):
        img_path = os.path.join(job_dir, f"scene_{i}.png")
        audio_path = os.path.join(job_dir, f"scene_{i}.mp3")

        await visual.generate_scene_image(
            visual_prompt=scene["visual_prompt"],
            index=i,
            out_path=img_path,
            visual_direction=visual_direction,
            environment=scene.get("environment", ""),
            lighting=scene.get("lighting", ""),
            shared_visual_anchor=shared_visual_anchor,
        )
        has_voice = await tts.synthesize(scene["narration"], audio_path, min_duration=scene["duration"])

        scene_assets.append(
            SceneAsset(
                index=i,
                duration=scene["duration"],
                beat_role=scene.get("beat_role", "HOOK"),
                purpose=scene.get("purpose", ""),
                category_tag=scene.get("category_tag", "HOW IT WORKS"),
                caption=scene["caption"],
                visual_prompt=scene["visual_prompt"],
                camera_direction=scene.get("camera_direction", "Slow cinematic push-in"),
                environment=scene.get("environment", ""),
                lighting=scene.get("lighting", ""),
                narration=scene["narration"],
                image_path=img_path,
                audio_path=audio_path,
                has_real_voice=has_voice,
            )
        )

    # 6. Motion & Lower-Third Captions Assembly with FFmpeg
    await emit("captions")
    await emit("rendering")

    final_video_path = os.path.join(job_dir, "final.mp4")
    assemble_video(scene_assets, final_video_path)

    await emit("done")

    return GenerationResult(
        job_id=job_id,
        title=plan["title"],
        description=f"A {plan.get('style', 'explainer')} video about {plan.get('topic', plan['title'])}.",
        style=plan.get("style", "cinematic explainer"),
        visual_direction=visual_direction,
        shared_visual_anchor=shared_visual_anchor,
        script=plan["narration"],
        scenes=[
            {
                "index": s.index,
                "duration": s.duration,
                "beat_role": s.beat_role,
                "purpose": s.purpose,
                "category_tag": s.category_tag,
                "caption": s.caption,
                "visual_prompt": s.visual_prompt,
                "camera_direction": s.camera_direction,
                "environment": s.environment,
                "lighting": s.lighting,
                "narration": s.narration,
            }
            for s in scene_assets
        ],
        video_path=final_video_path,
        using_fallback_llm=llm.using_fallback,
        using_fallback_visual=visual.using_fallback,
        using_fallback_tts=tts.using_fallback,
    )
