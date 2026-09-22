import os
import json
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

from agent import generate_video, OUTPUT_DIR  # noqa: E402

os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="AI Video Generation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

STAGE_LABELS = {
    "understanding": "Understanding your idea...",
    "planning": "Planning cinematic scenes...",
    "quality_check": "Refining director prompts...",
    "scripting": "Writing narration script...",
    "scenes": "Configuring scene composition...",
    "visuals": "Generating high-quality visuals...",
    "audio": "Synthesizing voiceover audio...",
    "captions": "Generating lower-third captions...",
    "rendering": "Assembling video with motion...",
    "done": "Video complete!",
}


class GenerateRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    """
    Non-streaming convenience endpoint: runs the full pipeline and returns
    the final result in one response. Use /generate/stream for live
    progress events.
    """
    result = await generate_video(req.prompt)
    return _serialize(result)


@app.post("/generate/stream")
async def generate_stream(req: GenerateRequest):
    """
    Server-Sent-Events endpoint. Emits one JSON event per pipeline stage,
    ending with a "done" event containing the final result payload.
    """

    async def event_gen():
        queue: asyncio.Queue = asyncio.Queue()

        async def on_progress(stage: str):
            await queue.put({"type": "progress", "stage": stage, "label": STAGE_LABELS.get(stage, stage)})

        async def run():
            try:
                result = await generate_video(req.prompt, on_progress=on_progress)
                await queue.put({"type": "result", "data": _serialize(result)})
            except Exception as exc:  # surface pipeline errors to the client
                await queue.put({"type": "error", "message": str(exc)})
            finally:
                await queue.put(None)

        task = asyncio.create_task(run())
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield f"data: {json.dumps(item)}\n\n"
        finally:
            await task

    return StreamingResponse(event_gen(), media_type="text/event-stream")


def _serialize(result):
    rel_video_path = os.path.relpath(result.video_path, OUTPUT_DIR).replace("\\", "/")
    return {
        "job_id": result.job_id,
        "title": result.title,
        "description": result.description,
        "style": getattr(result, "style", "cinematic explainer"),
        "visual_direction": getattr(result, "visual_direction", ""),
        "shared_visual_anchor": getattr(result, "shared_visual_anchor", {}),
        "script": result.script,
        "scenes": result.scenes,
        "video_url": f"/output/{rel_video_path}",
        "providers": {
            "llm_fallback": result.using_fallback_llm,
            "visual_fallback": result.using_fallback_visual,
            "tts_fallback": result.using_fallback_tts,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
