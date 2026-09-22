"""
agent.py — the orchestration layer.

This is deliberately NOT an autonomous-agent framework. It's a linear
pipeline function: prompt -> plan -> per-scene visuals -> per-scene voice ->
captions -> handed off to video_generator for FFmpeg assembly.

USER PROMPT -> LLM PLAN -> VISUALS -> VOICEOVER -> ASSEMBLE -> MP4
"""

import os
import uuid
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
    visual_prompt: str
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
    script: str
    scenes: list
    video_path: str
    using_fallback_llm: bool
    using_fallback_visual: bool
    using_fallback_tts: bool


ProgressCallback = Optional[Callable[[str], "asyncio.Future"]]


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

    # 1-2. Understand request + create video plan
    await emit("understanding")
    await emit("planning")
    plan = await llm.plan_video(user_prompt)

    # 3. Script/narration already produced as part of the plan
    await emit("scripting")

    # 4-6. Generate scene visuals + voiceover concurrently per scene
    await emit("scenes")
    scenes_raw = plan["scenes"]

    await emit("visuals")
    await emit("audio")

    scene_assets: list[SceneAsset] = []
    for i, scene in enumerate(scenes_raw):
        img_path = os.path.join(job_dir, f"scene_{i}.png")
        audio_path = os.path.join(job_dir, f"scene_{i}.mp3")

        await visual.generate_scene_image(scene["visual_prompt"], i, img_path)
        has_voice = await tts.synthesize(scene["narration"], audio_path, min_duration=scene["duration"])

        scene_assets.append(
            SceneAsset(
                index=i,
                duration=scene["duration"],
                visual_prompt=scene["visual_prompt"],
                narration=scene["narration"],
                caption=scene["caption"],
                image_path=img_path,
                audio_path=audio_path,
                has_real_voice=has_voice,
            )
        )

    # 7-8. Add captions + assemble into final MP4 (captions are burned in
    # during assembly so timing stays in sync with each scene).
    await emit("captions")
    await emit("rendering")

    final_video_path = os.path.join(job_dir, "final.mp4")
    assemble_video(scene_assets, final_video_path)

    await emit("done")

    return GenerationResult(
        job_id=job_id,
        title=plan["title"],
        description=f"A {plan.get('style', 'generated')} video about {plan.get('topic', plan['title'])}.",
        script=plan["narration"],
        scenes=[
            {
                "index": s.index,
                "duration": s.duration,
                "visual_prompt": s.visual_prompt,
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
