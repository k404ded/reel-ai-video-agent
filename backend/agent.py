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
    purpose: str
    visual_prompt: str
    camera_direction: str
    environment: str
    lighting: str
    narration: str
    caption: str
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
    - Validates visual prompts for physical clarity and strips unwanted text instructions
    - Trims or tightens narration to match spoken cadence
    - Ensures punchy, clean lower-third captions
    """
    scenes = plan.get("scenes") or []
    if not scenes:
        return plan

    # 1. Duration validation
    target_dur = plan.get("duration", 10.0)
    current_total = sum(s.get("duration", 3.0) for s in scenes)
    if current_total > 0 and abs(current_total - target_dur) > 0.5:
        # Scale scene durations proportionally
        ratio = target_dur / current_total
        for s in scenes:
            s["duration"] = round(max(s.get("duration", 3.0) * ratio, 2.0), 1)
        plan["duration"] = sum(s["duration"] for s in scenes)

    # 2. Refine each scene
    visual_dir = plan.get("visual_direction", "Photorealistic 3D technical animation, octane render, studio lighting")

    for i, s in enumerate(scenes):
        # Enforce minimum and maximum scene durations
        s["duration"] = max(2.5, min(s.get("duration", 3.5), 6.0))

        # Purpose fallback
        if not s.get("purpose"):
            s["purpose"] = f"Scene {i+1} presentation"

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
            s["environment"] = "Sleek dark graphite studio stage"
        if not s.get("lighting"):
            s["lighting"] = "Precision rim lighting with cool accent highlights"

        # Visual prompt: strip on-image text demands
        vp = s.get("visual_prompt", plan.get("title", ""))
        vp_clean = re.sub(r"(?i)\b(with text|labeled with|text saying|words saying|caption)\b.*", "", vp).strip(" ,.")
        if len(vp_clean) < 20:
            vp_clean = f"A detailed, authentic 3D representation of {plan.get('topic', 'the subject')}, showing physical structure and materials"
        s["visual_prompt"] = vp_clean

        # Caption: clean and punchy (<= 6 words)
        cap = s.get("caption", "").strip()
        words = cap.split()
        if len(words) > 6:
            s["caption"] = " ".join(words[:6])
        elif not cap:
            s["caption"] = plan.get("topic", "Overview").title()

        # Narration: ensure spoken cadence fits duration (~2.5 words per sec)
        narr = s.get("narration", "").strip()
        narr_words = narr.split()
        max_words = int(s["duration"] * 3.2)
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
        )
        has_voice = await tts.synthesize(scene["narration"], audio_path, min_duration=scene["duration"])

        scene_assets.append(
            SceneAsset(
                index=i,
                duration=scene["duration"],
                purpose=scene.get("purpose", ""),
                visual_prompt=scene["visual_prompt"],
                camera_direction=scene.get("camera_direction", "Slow cinematic push-in"),
                environment=scene.get("environment", ""),
                lighting=scene.get("lighting", ""),
                narration=scene["narration"],
                caption=scene["caption"],
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
        script=plan["narration"],
        scenes=[
            {
                "index": s.index,
                "duration": s.duration,
                "purpose": s.purpose,
                "visual_prompt": s.visual_prompt,
                "camera_direction": s.camera_direction,
                "environment": s.environment,
                "lighting": s.lighting,
                "narration": s.narration,
                "caption": s.caption,
            }
            for s in scene_assets
        ],
        video_path=final_video_path,
        using_fallback_llm=llm.using_fallback,
        using_fallback_visual=visual.using_fallback,
        using_fallback_tts=tts.using_fallback,
    )
