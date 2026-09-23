import asyncio
import os
import sys
import time
import subprocess
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agent import generate_video

ARTIFACT_DIR = r"C:\Users\kimaya\.gemini\antigravity-ide\brain\078ad98e-5796-4a7a-b8a3-e8f4b4b31200"

import re

TEST_TOPICS = [
    ("gradient_descent", "Explain Gradient Descent"),
    ("binary_search", "Explain Binary Search"),
    ("neural_network", "Explain a Neural Network"),
    ("pid_control", "Explain PID Control"),
    ("can_bus", "Explain CAN Bus Arbitration"),
    ("catia_command_finder", "Explain Command Finder in CATIA"),
    ("ev_regenerative_braking", "Explain regenerative braking"),
    ("ev_bms", "Explain EV Battery Management System"),
    ("manufacturing_cnc", "Explain a manufacturing process"),
    ("programming_recursion", "Explain a programming concept"),
]


async def run_test(key: str, prompt: str):
    print(f"\n==================================================", flush=True)
    print(f"TESTING: {prompt}", flush=True)
    print(f"==================================================", flush=True)
    t0 = time.time()
    
    stages_hit = []
    async def on_progress(stage: str):
        stages_hit.append(stage)
        print(f"  [Stage] {stage}", flush=True)

    res = await generate_video(prompt, on_progress=on_progress)
    elapsed = time.time() - t0
    
    print(f"\nCompleted in: {elapsed:.2f} seconds!", flush=True)
    print(f"Title: {res.title}", flush=True)
    print(f"Content Type: {res.content_type}", flush=True)
    print(f"Scenes ({len(res.scenes)}):", flush=True)
    
    avatar_found = False
    for i, s in enumerate(res.scenes):
        vtype = s.get("visual_type", "")
        action = s.get("action", "")
        caption = s.get("caption", "")
        duration = s.get("duration", 0)
        print(f"  Scene {i+1} ({duration}s): [{vtype}] - {caption}")
        print(f"    Action: {action[:80]}")
        # Verify no avatar keywords in prompt or visual type
        text_check = f"{vtype} {action} {caption}".lower()
        if re.search(r'\b(avatar|presenter|talking\s*head|human\s*host|man\s+in\s+sweater)\b', text_check):
            avatar_found = True
            print(f"    [WARNING] Avatar keyword detected in scene {i+1}!")
            
    print(f"Avatar Check: {'FAILED (avatar detected)' if avatar_found else 'PASSED (0 avatars, 100% technical)'}")
    print(f"Video File: {res.video_path}")
    assert os.path.exists(res.video_path), f"Video file not found at {res.video_path}"
    file_size_kb = os.path.getsize(res.video_path) / 1024
    print(f"Video Size: {file_size_kb:.1f} KB")
    
    # Extract frames using ffmpeg at 2s and 8s for artifact inspection
    frame1 = os.path.join(ARTIFACT_DIR, f"{key}_frame_2s.png")
    frame2 = os.path.join(ARTIFACT_DIR, f"{key}_frame_8s.png")
    
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "00:00:02.000", "-i", res.video_path, "-vframes", "1", frame1],
        capture_output=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "00:00:07.500", "-i", res.video_path, "-vframes", "1", frame2],
        capture_output=True,
    )
    
    if os.path.exists(frame1):
        print(f"Extracted Frame 1: {frame1}")
    if os.path.exists(frame2):
        print(f"Extracted Frame 2: {frame2}")
        
    return {
        "key": key,
        "prompt": prompt,
        "elapsed": elapsed,
        "scenes_count": len(res.scenes),
        "content_type": res.content_type,
        "file_size_kb": file_size_kb,
        "avatar_found": avatar_found,
    }


async def main():
    results = []
    for key, prompt in TEST_TOPICS:
        try:
            r = await run_test(key, prompt)
            results.append(r)
        except Exception as e:
            print(f"ERROR on {prompt}: {e}")
            import traceback
            traceback.print_exc()
            
    print("\n==================================================")
    print("SUMMARY RESULTS ACROSS DOMAINS")
    print("==================================================")
    for r in results:
        status_str = "PASS" if not r["avatar_found"] and r["elapsed"] < 30 else "WARN"
        print(f"[{status_str}] {r['prompt']}: {r['elapsed']:.2f}s | {r['scenes_count']} scenes | {r['file_size_kb']:.1f} KB | Avatars: {r['avatar_found']}")


if __name__ == "__main__":
    asyncio.run(main())
