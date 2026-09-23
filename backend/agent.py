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
    visual_type: str = "ai_workstation_video"
    shot_type: str = "medium_shot"
    subject: str = ""
    action: str = ""
    technical_content: str = ""
    validation_status: str = "PASSED"


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
    content_type: str = "GENERAL_EDUCATIONAL"
    validation_passed: bool = True
    validation_warnings: list = field(default_factory=list)
    generation_backend_used: str = "MULTI_DISPATCH_DIRECTOR"


ProgressCallback = Optional[Callable[[str], "asyncio.Future"]]


def validate_and_refine_plan(plan: dict, user_prompt: str) -> dict:
    """
    Ensures duration balance, clean cadence, and category tags.
    """
    scenes = plan.get("scenes") or []
    if not scenes:
        return plan

    target_dur = plan.get("duration", 15.0)
    current_total = sum(s.get("duration", 3.0) for s in scenes)
    if current_total > 0 and abs(current_total - target_dur) > 0.5:
        ratio = target_dur / current_total
        for s in scenes:
            s["duration"] = round(max(s.get("duration", 3.0) * ratio, 2.5), 1)
        plan["duration"] = sum(s["duration"] for s in scenes)

    if not plan.get("shared_visual_anchor"):
        plan["shared_visual_anchor"] = {
            "color_palette": ["#0b0f19 deep graphite", "#0ea5e9 electric cyan", "#10b981 tech emerald"],
            "lighting_setup": "Volumetric key studio spotlight with high-contrast rim lighting",
            "primary_material": "Precision brushed aluminum, matte composite, and dark reflective glass",
            "environment_aesthetic": "Modern high-tech engineering workstation and laboratory",
        }

    for i, s in enumerate(scenes):
        s["duration"] = max(2.5, min(s.get("duration", 3.5), 6.0))
        s.setdefault("visual_type", "ai_workstation_video")
        s.setdefault("shot_type", "medium_shot")
        s.setdefault("beat_role", s.get("visual_type", "SCENE").upper())
        s.setdefault("category_tag", plan.get("content_type", "HOW IT WORKS").replace("_", " "))
        s.setdefault("purpose", f"Scene {i+1}: {s.get('subject', 'Demonstration')}")
        s.setdefault("camera_direction", s.get("camera", "Slow cinematic push-in toward active screen"))

        # Narration word pacing check
        narr = s.get("narration", "").strip()
        narr_words = narr.split()
        max_words = int(s["duration"] * 2.8)
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
            visual_prompt=scene.get("visual_prompt", scene.get("action", "")),
            index=i,
            out_path=img_path,
            visual_direction=visual_direction,
            environment=scene.get("environment", ""),
            lighting=scene.get("lighting", ""),
            shared_visual_anchor=shared_visual_anchor,
            visual_type=scene.get("visual_type", ""),
            shot_type=scene.get("shot_type", ""),
            action=scene.get("action", ""),
            technical_content=scene.get("technical_content", ""),
        )
        has_voice = await tts.synthesize(scene["narration"], audio_path, min_duration=scene["duration"])

        scene_assets.append(
            SceneAsset(
                index=i,
                duration=scene["duration"],
                beat_role=scene.get("beat_role", scene.get("visual_type", "SCENE")).upper(),
                purpose=scene.get("purpose", ""),
                category_tag=scene.get("category_tag", "HOW IT WORKS"),
                caption=scene.get("caption", scene.get("on_screen_text", "")),
                visual_prompt=scene.get("visual_prompt", ""),
                camera_direction=scene.get("camera_direction", "Slow cinematic push-in"),
                environment=scene.get("environment", ""),
                lighting=scene.get("lighting", ""),
                narration=scene["narration"],
                image_path=img_path,
                audio_path=audio_path,
                has_real_voice=has_voice,
                visual_type=scene.get("visual_type", "ai_workstation_video"),
                shot_type=scene.get("shot_type", "medium_shot"),
                subject=scene.get("subject", ""),
                action=scene.get("action", ""),
                technical_content=scene.get("technical_content", ""),
                validation_status=scene.get("validation_status", "PASSED"),
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
        description=f"An authentic educational video explaining {plan.get('topic', plan['title'])}.",
        style=plan.get("style", "educational explainer"),
        visual_direction=visual_direction,
        shared_visual_anchor=shared_visual_anchor,
        script=plan.get("narration", plan.get("script", "")),
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
                "visual_type": s.visual_type,
                "shot_type": s.shot_type,
                "subject": s.subject,
                "action": s.action,
                "technical_content": s.technical_content,
                "validation_status": s.validation_status,
            }
            for s in scene_assets
        ],
        video_path=final_video_path,
        using_fallback_llm=llm.using_fallback,
        using_fallback_visual=visual.using_fallback,
        using_fallback_tts=tts.using_fallback,
        content_type=plan.get("content_type", "GENERAL_EDUCATIONAL"),
        validation_passed=plan.get("validation_passed", True),
        validation_warnings=plan.get("validation_warnings", []),
        generation_backend_used="MULTI_DISPATCH_DIRECTOR",
    )
