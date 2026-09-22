"""
video_generator.py — turns per-scene assets (image + audio + caption) into
one final MP4 using FFmpeg.

Default output: 1920x1080, 30fps, H.264 video, AAC audio.
"""

import os
import subprocess
import tempfile

WIDTH, HEIGHT, FPS = 1920, 1080, 30


def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("'", "\u2019")  # avoid quote-escaping headaches entirely
    text = text.replace("%", "\\%")
    return text


def _build_scene_clip(scene, clip_path: str):
    caption = _escape_drawtext(scene.caption or "")

    if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        font_spec = "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    else:
        font_spec = "font=Arial"

    drawtext_filter = ""
    if caption:
        drawtext_filter = (
            f"drawtext={font_spec}:text='{caption}':"
            f"fontcolor=white:fontsize=54:borderw=4:bordercolor=black@0.7:"
            f"x=(w-text_w)/2:y=h-160,"
        )

    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"{drawtext_filter}"
        f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(scene.duration - 0.25, 0)}:d=0.25"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", scene.image_path,
        "-i", scene.audio_path,
        "-t", str(scene.duration),
        "-vf", vf,
        "-af", f"apad=whole_dur={scene.duration}",
        "-r", str(FPS),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        clip_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        err_msg = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
        print(f"[video_generator] FFmpeg clip error: {err_msg}")
        raise RuntimeError(f"FFmpeg failed to create scene clip: {err_msg}")


def assemble_video(scene_assets, final_path: str):
    with tempfile.TemporaryDirectory() as tmp:
        clip_paths = []
        for scene in scene_assets:
            clip_path = os.path.join(tmp, f"clip_{scene.index}.mp4")
            _build_scene_clip(scene, clip_path)
            clip_paths.append(clip_path)

        concat_list_path = os.path.join(tmp, "concat.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for p in clip_paths:
                clean_p = p.replace("\\", "/")
                f.write(f"file '{clean_p}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            final_path,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:
            err_msg = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
            print(f"[video_generator] FFmpeg concat error: {err_msg}")
            raise RuntimeError(f"FFmpeg failed to assemble final video: {err_msg}")

    return final_path
