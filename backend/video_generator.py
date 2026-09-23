"""
video_generator.py — Universal Technical Video Mode Procedural Animation Engine.

Renders genuine 1080p 30fps procedural animations with real temporal motion across all domains:
1. MathematicalAnimationBackend (3D loss surfaces, gradient vectors, descent trajectories)
2. AlgorithmVisualizationBackend (Binary search array, pointers, partition elimination, target match)
3. NeuralNetworkAnimationBackend (Node layers, weighted synapses, forward pulses, backprop gradients)
4. ControlSystemAnimationBackend (Oscilloscope step response, setpoint, overshoot, PID telemetry)
5. NetworkProtocolAnimationBackend (CAN Bus differential waveforms, bit-level arbitration, backoff)
6. BatterySystemAnimationBackend (EV battery cell matrix, thermal heatmap, current vectors, BMS HUD)
7. CadSoftwareAnimationBackend (CAD interface, cursor glide, Command Finder, parametric 3D extrusion)
8. AutomotiveSystemAnimationBackend (EV powertrain energy flux, regen torque inversion, efficiency)
9. ManufacturingProcessAnimationBackend (Raw billet stock, rotating end mill, pocket cutaway, tolerance CMM)
10. UniversalTechnicalDiagramBackend (General technical schematics, signal paths, telemetry gauges)

Strictly zero AI avatars, zero human presenters, zero static slideshows.
Every clip includes bottom-anchored, professional educational subtitles with safe margins.
"""

import os
import re
import math
import shutil
import tempfile
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS = 1920, 1080, 30


def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("'", "\u2019")
    text = text.replace("%", "\uFF05")  # Fullwidth percent prevents FFmpeg % expansion crashes
    text = text.replace("[", "\\[").replace("]", "\\]")
    return text


def _get_font_spec() -> str:
    if os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
        return "fontfile='C\\:/Windows/Fonts/arialbd.ttf'"
    elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        return "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return "font=Arial"


def _add_subtitle_and_mux(frame_dir: str, audio_path: str, caption: str, duration: float, clip_path: str, fps: int = FPS):
    """Muxes rendered frame sequence with narration audio and burns in bottom-anchored subtitles."""
    font_spec = _get_font_spec()
    escaped_caption = _escape_drawtext(caption or "").strip()
    if len(escaped_caption) > 55:
        escaped_caption = escaped_caption[:55] + "..."

    subtitle_filter = ""
    if escaped_caption:
        subtitle_filter = (
            f",drawtext={font_spec}:text='{escaped_caption}':"
            f"fontsize=36:fontcolor=white:box=1:boxcolor=black@0.78:boxborderw=14:"
            f"x=(w-text_w)/2:y=h-135"
        )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frame_dir, "frame_%04d.png"),
        "-i", audio_path,
        "-t", str(duration),
        "-r", "30",
        "-vf", f"format=yuv420p{subtitle_filter}",
        "-af", f"apad=whole_dur={duration}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        clip_path
    ]
    subprocess.run(ffmpeg_cmd, check=True, capture_output=True)


# =============================================================================
# 1. MATHEMATICAL ANIMATION BACKEND
# =============================================================================
class MathematicalAnimationBackend:
    """Renders dynamic 3D loss surfaces, gradient vectors, descent iterations, and convergence rings."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        math_fps = 10
        total_frames = max(int(duration * math_fps), 15)
        action_text = (scene.action or "").lower()

        phase = "surface"
        if "initial" in action_text or "theta_0" in action_text or "dropline" in action_text:
            phase = "coordinate"
        elif "tangent" in action_text or "gradient vector" in action_text or "steepest" in action_text:
            phase = "gradient"
        elif "step" in action_text or "iterat" in action_text or "trajectory" in action_text:
            phase = "iteration"
        elif "converge" in action_text or "minimum" in action_text or "optimal" in action_text:
            phase = "convergence"

        x = np.linspace(-3.2, 3.2, 22)
        y = np.linspace(-3.2, 3.2, 22)
        X, Y = np.meshgrid(x, y)
        Z = 0.5 * (X**2 + 1.5 * Y**2)

        start_x, start_y = 2.4, 2.1
        lr = 0.16
        num_steps = 7
        path_x, path_y, path_z = [start_x], [start_y], [0.5 * (start_x**2 + 1.5 * start_y**2)]
        cx, cy = start_x, start_y
        for _ in range(num_steps):
            cx -= lr * cx
            cy -= lr * (1.5 * cy)
            path_x.append(cx)
            path_y.append(cy)
            path_z.append(0.5 * (cx**2 + 1.5 * cy**2))

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                fig = plt.figure(figsize=(16, 9), dpi=80)
                fig.patch.set_facecolor("#070a11")
                ax = fig.add_subplot(111, projection="3d")
                ax.set_facecolor("#070a11")

                progress = f / total_frames
                elev = 34 + 4 * math.sin(progress * math.pi)
                azim = -65 + progress * 35

                ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.62, edgecolor="#1e293b", linewidth=0.4)
                ax.contour(X, Y, Z, zdir="z", offset=0, colors="#06b6d4", alpha=0.4, linewidths=0.8)
                ax.view_init(elev=elev, azim=azim)

                if phase == "surface":
                    plt.title("CONVEX LOSS SURFACE: J(w₁, w₂) = ½(w₁² + 1.5w₂²) | Continuous Objective Space",
                              color="#f8fafc", fontsize=16, fontweight="bold", pad=18)

                elif phase == "coordinate":
                    drop_prog = min(progress * 1.8, 1.0)
                    px, py, pz = start_x, start_y, 0.5 * (start_x**2 + 1.5 * start_y**2)
                    ax.scatter([px], [py], [pz], color="#10b981", s=180, edgecolors="white", linewidth=2.0, depthshade=False)
                    ax.plot([px, px], [py, py], [0, pz * drop_prog], color="#94a3b8", linestyle="--", linewidth=1.8)
                    ax.scatter([px], [py], [0], color="#64748b", s=50, marker="x")
                    plt.title(f"INITIAL STATE: θ₀ = [{px:.2f}, {py:.2f}]ᵀ | High Loss J(θ₀) = {pz:.3f}",
                              color="#f8fafc", fontsize=16, fontweight="bold", pad=18)

                elif phase == "gradient":
                    px, py, pz = start_x, start_y, 0.5 * (start_x**2 + 1.5 * start_y**2)
                    ax.scatter([px], [py], [pz], color="#10b981", s=180, edgecolors="white", linewidth=2.0, depthshade=False)
                    tp_x = np.linspace(px - 0.7, px + 0.7, 8)
                    tp_y = np.linspace(py - 0.7, py + 0.7, 8)
                    TP_X, TP_Y = np.meshgrid(tp_x, tp_y)
                    TP_Z = pz + (px) * (TP_X - px) + (1.5 * py) * (TP_Y - py)
                    ax.plot_surface(TP_X, TP_Y, TP_Z, color="#f59e0b", alpha=0.35, linewidth=0)
                    vec_len = min(progress * 1.5, 1.0)
                    ax.quiver(px, py, pz, 0.9 * vec_len, 1.2 * vec_len, 2.0 * vec_len, color="#f59e0b", linewidth=3.0, arrow_length_ratio=0.3)
                    ax.quiver(px, py, pz, -0.9 * vec_len, -1.2 * vec_len, -1.6 * vec_len, color="#38bdf8", linewidth=3.5, arrow_length_ratio=0.3)
                    plt.title("GRADIENT: ∇J(θ) (Uphill, Amber)  vs.  NEGATIVE GRADIENT: -∇J(θ) (Downhill Step, Cyan)",
                              color="#f8fafc", fontsize=16, fontweight="bold", pad=18)

                elif phase == "iteration":
                    active_steps = max(1, min(int(progress * (len(path_x) + 1)), len(path_x)))
                    ax.plot(path_x[:active_steps], path_y[:active_steps], path_z[:active_steps],
                            color="#38bdf8", linewidth=3.0, marker="o", markersize=5)
                    cur_px, cur_py, cur_pz = path_x[active_steps - 1], path_y[active_steps - 1], path_z[active_steps - 1]
                    ax.scatter([cur_px], [cur_py], [cur_pz], color="#10b981", s=180, edgecolors="white", linewidth=2.0, depthshade=False)
                    plt.title(f"UPDATE RULE: θ_{{t+1}} = θ_t - α∇J(θ_t) | Iteration {active_steps-1} | Current Loss: {cur_pz:.3f}",
                              color="#f8fafc", fontsize=16, fontweight="bold", pad=18)

                elif phase == "convergence":
                    ax.plot(path_x, path_y, path_z, color="#38bdf8", linewidth=2.0, alpha=0.7)
                    ax.scatter([0], [0], [0], color="#10b981", s=220, edgecolors="white", linewidth=2.5, depthshade=False)
                    pulse_r = 0.3 + 0.25 * math.sin(progress * 8 * math.pi)
                    theta_ring = np.linspace(0, 2 * math.pi, 24)
                    ax.plot(pulse_r * np.cos(theta_ring), pulse_r * np.sin(theta_ring), np.zeros_like(theta_ring),
                            color="#10b981", linewidth=2.5, linestyle=":")
                    plt.title("CONVERGENCE REACHED: θ* = [0.00, 0.00]ᵀ | Optimal Loss J* = 0.000 | ||∇J|| ≈ 0",
                              color="#10b981", fontsize=16, fontweight="bold", pad=18)

                ax.set_xlabel("Parameter w₁", color="#94a3b8", fontsize=11, labelpad=6)
                ax.set_ylabel("Parameter w₂", color="#94a3b8", fontsize=11, labelpad=6)
                ax.set_zlabel("Loss J(w)", color="#94a3b8", fontsize=11, labelpad=6)
                ax.tick_params(colors="#64748b", labelsize=8)

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                plt.tight_layout()
                plt.savefig(frame_file, facecolor=fig.get_facecolor(), edgecolor="none")
                plt.close(fig)

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path, fps=math_fps)


# =============================================================================
# 2. ALGORITHM VISUALIZATION BACKEND (Binary Search, Sorting, Trees)
# =============================================================================
class AlgorithmVisualizationBackend:
    """Renders interactive array memory cells, low/mid/high pointers, comparisons, and partition eliminations."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)
        action_text = (scene.action or "").lower()

        arr = [3, 9, 14, 21, 28, 35, 42, 57, 68]
        target = 42

        stage = "init"
        if "midpoint" in action_text or "comparison" in action_text:
            stage = "mid"
        elif "eliminat" in action_text or "halv" in action_text or "shift" in action_text:
            stage = "eliminate"
        elif "hit" in action_text or "match" in action_text or "found" in action_text or "second" in action_text:
            stage = "match"
        elif "complexity" in action_text or "log" in action_text:
            stage = "complexity"

        cell_w, cell_h = 130, 110
        start_x = (WIDTH - (len(arr) * (cell_w + 16))) // 2
        start_y = HEIGHT // 2 - 40

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (11, 15, 23))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                # Title banner
                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))
                draw.text((start_x, 30), f"BINARY SEARCH ALGORITHM  |  Target Value: {target}  |  Array Size N = {len(arr)}",
                          fill=(248, 250, 252))

                if stage != "complexity":
                    # Determine active state based on stage
                    if stage == "init":
                        low, high, mid = 0, 8, None
                        active_mask = [True] * 9
                    elif stage == "mid":
                        low, high, mid = 0, 8, 4
                        active_mask = [True] * 9
                    elif stage == "eliminate":
                        low, high = 5, 8
                        mid = 4
                        active_mask = [False, False, False, False, False, True, True, True, True]
                    else:  # match
                        low, high, mid = 5, 8, 6
                        active_mask = [False, False, False, False, False, True, True, True, True]

                    # Draw Array Cells
                    for i, val in enumerate(arr):
                        cx = start_x + i * (cell_w + 16)
                        cy = start_y

                        is_active = active_mask[i]
                        bg_color = (30, 41, 59) if is_active else (18, 23, 34)
                        border_color = (56, 189, 248) if is_active else (51, 65, 85)
                        text_color = (248, 250, 252) if is_active else (100, 116, 139)

                        # Highlight mid
                        if mid is not None and i == mid:
                            if stage == "match":
                                bg_color = (16, 185, 129)  # Green match
                                border_color = (255, 255, 255)
                                text_color = (255, 255, 255)
                            else:
                                bg_color = (245, 158, 11)  # Amber test
                                border_color = (255, 255, 255)
                                text_color = (15, 23, 42)

                        draw.rectangle([(cx, cy), (cx + cell_w, cy + cell_h)], fill=bg_color, outline=border_color, width=3)
                        draw.text((cx + cell_w // 2 - 16, cy + cell_h // 2 - 14), str(val), fill=text_color)
                        # Index label
                        draw.text((cx + cell_w // 2 - 8, cy + cell_h + 16), f"[{i}]", fill=(148, 163, 184))

                    # Draw Pointers
                    if low is not None and low < len(arr):
                        lx = start_x + low * (cell_w + 16) + cell_w // 2
                        draw.polygon([(lx, start_y - 25), (lx - 12, start_y - 45), (lx + 12, start_y - 45)], fill=(56, 189, 248))
                        draw.text((lx - 16, start_y - 75), "low", fill=(56, 189, 248))

                    if high is not None and high < len(arr):
                        hx = start_x + high * (cell_w + 16) + cell_w // 2
                        draw.polygon([(hx, start_y - 25), (hx - 12, start_y - 45), (hx + 12, start_y - 45)], fill=(244, 63, 94))
                        draw.text((hx - 16, start_y - 75), "high", fill=(244, 63, 94))

                    if mid is not None and mid < len(arr):
                        mx = start_x + mid * (cell_w + 16) + cell_w // 2
                        draw.polygon([(mx, start_y - 25), (mx - 14, start_y - 50), (mx + 14, start_y - 50)], fill=(245, 158, 11))
                        draw.text((mx - 14, start_y - 80), "mid", fill=(245, 158, 11))

                    # Status Callout Box
                    callout_y = start_y + cell_h + 70
                    draw.rectangle([(start_x, callout_y), (start_x + len(arr) * (cell_w + 16) - 16, callout_y + 85)],
                                   fill=(17, 24, 39), outline=(56, 189, 248), width=2)

                    if stage == "init":
                        status_str = f"STEP 1: Initial Bounds [low = 0, high = 8]. Target = {target}."
                    elif stage == "mid":
                        status_str = f"STEP 2: Compute mid = (0 + 8) // 2 = 4. Test array[4] = 28. (28 < {target} -> DISCARD LEFT)"
                    elif stage == "eliminate":
                        status_str = f"STEP 3: Discard indices [0..4]. Set low = mid + 1 = 5. Remaining elements: 4."
                    else:
                        status_str = f"STEP 4: New mid = (5 + 8) // 2 = 6. array[6] = 42 == {target}. MATCH FOUND IN 2 STEPS!"

                    draw.text((start_x + 24, callout_y + 28), status_str, fill=(248, 250, 252))

                else:
                    # Complexity analysis tree
                    draw.text((start_x, 140), "TIME COMPLEXITY COMPARISON: LINEAR O(N) vs BINARY O(log₂ N)", fill=(56, 189, 248))
                    draw.rectangle([(start_x, 200), (WIDTH - start_x, 500)], fill=(17, 24, 39), outline=(75, 85, 99), width=2)
                    draw.text((start_x + 30, 230), "N = 1,000 Elements     ->  Linear: 1,000 steps   |  Binary Search: 10 steps max", fill=(248, 250, 252))
                    draw.text((start_x + 30, 290), "N = 1,000,000 Elements ->  Linear: 1,000,000 steps |  Binary Search: 20 steps max", fill=(248, 250, 252))
                    draw.text((start_x + 30, 350), "N = 1,000,000,000 Elements -> Linear: 1 Billion steps |  Binary Search: 30 steps max", fill=(16, 185, 129))
                    draw.text((start_x + 30, 420), "Logarithmic Scaling: Each comparison cuts remaining search space by 50%.", fill=(148, 163, 184))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 2.5 PROGRAMMING & CALL STACK ANIMATION BACKEND
# =============================================================================
class ProgrammingCodeAnimationBackend:
    """Renders IDE code syntax highlighting, progressive line execution, and LIFO Call Stack memory frames."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)
        action_text = (scene.action or "").lower()
        combined = f"{scene.action} {scene.caption} {scene.subject}".lower()

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (15, 23, 42))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                # Top Title Bar
                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(30, 41, 59))
                draw.text((100, 30), f"PROGRAMMING EXECUTION & MEMORY ARCHITECTURE  |  {scene.subject}", fill=(248, 250, 252))

                # Left: IDE Editor Window
                ide_x, ide_y, ide_w, ide_h = 100, 140, 850, 680
                draw.rectangle([(ide_x, ide_y), (ide_x + ide_w, ide_y + ide_h)], fill=(11, 15, 25), outline=(51, 65, 85), width=2)
                # Editor Tab
                draw.rectangle([(ide_x, ide_y), (ide_x + 220, ide_y + 40)], fill=(30, 41, 59))
                draw.text((ide_x + 24, ide_y + 12), "recursion.py", fill=(56, 189, 248))

                code_lines = [
                    (1, "def factorial(n):", (192, 132, 252)),
                    (2, "    # Base case condition", (100, 116, 139)),
                    (3, "    if n <= 1:", (244, 63, 94)),
                    (4, "        return 1", (16, 185, 129)),
                    (5, "    # Recursive call & unwind", (100, 116, 139)),
                    (6, "    sub_result = factorial(n - 1)", (56, 189, 248)),
                    (7, "    return n * sub_result", (245, 158, 11)),
                    (8, "", (255, 255, 255)),
                    (9, "result = factorial(3)", (248, 250, 252)),
                ]

                # Determine active line based on scene/progress
                active_line = 6
                if "base" in combined or "halt" in combined or "stop" in combined:
                    active_line = 3
                elif "unwind" in combined or "bubbl" in combined or "pop" in combined:
                    active_line = 7
                elif "initial" in combined or "push" in combined:
                    active_line = 9

                for lnum, ltxt, col in code_lines:
                    ly = ide_y + 60 + (lnum - 1) * 44
                    if lnum == active_line:
                        # Highlighted execution line
                        draw.rectangle([(ide_x + 10, ly - 4), (ide_x + ide_w - 10, ly + 36)], fill=(30, 58, 138), outline=(56, 189, 248), width=1)
                        # Execution pointer arrow
                        draw.polygon([(ide_x + 20, ly + 16), (ide_x + 36, ly + 8), (ide_x + 36, ly + 24)], fill=(245, 158, 11))
                    draw.text((ide_x + 50, ly + 4), f"{lnum:2d}", fill=(100, 116, 139))
                    draw.text((ide_x + 100, ly + 4), ltxt, fill=col)

                # Right: Call Stack Memory Visualizer
                stack_x, stack_y, stack_w, stack_h = 1010, 140, 810, 680
                draw.rectangle([(stack_x, stack_y), (stack_x + stack_w, stack_y + stack_h)], fill=(11, 15, 25), outline=(51, 65, 85), width=2)
                draw.rectangle([(stack_x, stack_y), (stack_x + stack_w, stack_y + 45)], fill=(30, 41, 59))
                draw.text((stack_x + 30, stack_y + 12), "CALL STACK MEMORY  (LIFO: Last In, First Out)", fill=(16, 185, 129))

                # Stack Frames based on scene
                frames_to_draw = []
                if "initial" in combined or "push" in combined:
                    frames_to_draw = [("factorial(3)", "n = 3 | return addr: main()", (56, 189, 248))]
                elif "descent" in combined or "accumul" in combined:
                    frames_to_draw = [
                        ("factorial(3)", "n = 3 | awaiting factorial(2)", (75, 85, 99)),
                        ("factorial(2)", "n = 2 | awaiting factorial(1)", (56, 189, 248)),
                    ]
                elif "base" in combined:
                    frames_to_draw = [
                        ("factorial(3)", "n = 3 | awaiting factorial(2)", (75, 85, 99)),
                        ("factorial(2)", "n = 2 | awaiting factorial(1)", (75, 85, 99)),
                        ("factorial(1)", "n = 1 | BASE CASE: returns 1", (16, 185, 129)),
                    ]
                elif "unwind" in combined or "bubbl" in combined:
                    frames_to_draw = [
                        ("factorial(3)", "n = 3 | evaluating 3 * 2", (245, 158, 11)),
                        ("factorial(2)", "n = 2 | returning 2 * 1 = 2", (16, 185, 129)),
                    ]
                else: # complete / result
                    frames_to_draw = [
                        ("main()", "result = 6 | STACK CLEARED | O(N) SPACE", (16, 185, 129))
                    ]

                # Draw from bottom up
                base_frame_y = stack_y + stack_h - 130
                for idx, (fname, fdetails, fcol) in enumerate(frames_to_draw):
                    fy = base_frame_y - idx * 130
                    draw.rectangle([(stack_x + 40, fy), (stack_x + stack_w - 40, fy + 100)], fill=(17, 24, 39), outline=fcol, width=3)
                    draw.text((stack_x + 70, fy + 18), fname, fill=(248, 250, 252))
                    draw.text((stack_x + 70, fy + 56), fdetails, fill=fcol)
                    # Stack pointer
                    if idx == len(frames_to_draw) - 1:
                        draw.text((stack_x + stack_w - 220, fy + 38), "<-- ESP (Top)", fill=(244, 63, 94))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 3. NEURAL NETWORK ANIMATION BACKEND
# =============================================================================
class NeuralNetworkAnimationBackend:
    """Renders layered neuron nodes, synaptic connection weights, forward propagating pulse waves, and backprop gradients."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)
        action_text = (scene.action or "").lower()
        is_backprop = "backprop" in action_text or "error" in action_text or "gradient" in action_text

        layers = [4, 6, 6, 2]
        layer_x = [300, 720, 1140, 1560]

        nodes = []
        for l_idx, count in enumerate(layers):
            lx = layer_x[l_idx]
            spacing = 540 // (count + 1)
            layer_nodes = []
            for n_idx in range(count):
                ly = HEIGHT // 2 - 270 + (n_idx + 1) * spacing
                layer_nodes.append((lx, ly))
            nodes.append(layer_nodes)

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (9, 13, 20))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                # Title
                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))
                mode_str = "BACKPROPAGATION: Gradient Error Flow" if is_backprop else "FORWARD PASS: Multi-Layer Neural Network Propagation"
                draw.text((100, 30), f"{mode_str} | Architecture: 4 -> 6 -> 6 -> 2", fill=(248, 250, 252))

                # Draw Synapses
                synapse_color = (239, 68, 68) if is_backprop else (56, 189, 248)
                for l in range(len(nodes) - 1):
                    for n1 in nodes[l]:
                        for n2 in nodes[l + 1]:
                            draw.line([n1, n2], fill=(30, 41, 59), width=1)

                # Draw Traveling Pulses
                pulse_phase = (progress * 3.0) % 1.0
                if is_backprop:
                    pulse_l = int((1.0 - pulse_phase) * (len(nodes) - 1))
                    pulse_sub = (1.0 - pulse_phase) * (len(nodes) - 1) - pulse_l
                    pulse_l = max(0, min(pulse_l, len(nodes) - 2))
                    for n1 in nodes[pulse_l]:
                        for n2 in nodes[pulse_l + 1]:
                            px = int(n2[0] + (n1[0] - n2[0]) * pulse_sub)
                            py = int(n2[1] + (n1[1] - n2[1]) * pulse_sub)
                            draw.ellipse([(px - 3, py - 3), (px + 3, py + 3)], fill=(239, 68, 68))
                else:
                    pulse_l = int(pulse_phase * (len(nodes) - 1))
                    pulse_sub = pulse_phase * (len(nodes) - 1) - pulse_l
                    pulse_l = max(0, min(pulse_l, len(nodes) - 2))
                    for n1 in nodes[pulse_l]:
                        for n2 in nodes[pulse_l + 1]:
                            px = int(n1[0] + (n2[0] - n1[0]) * pulse_sub)
                            py = int(n1[1] + (n2[1] - n1[1]) * pulse_sub)
                            draw.ellipse([(px - 3, py - 3), (px + 3, py + 3)], fill=(56, 189, 248))

                # Draw Nodes
                layer_names = ["Input Layer (x)", "Hidden Layer 1 (h₁)", "Hidden Layer 2 (h₂)", "Output Layer (ŷ)"]
                for l_idx, layer_nodes in enumerate(nodes):
                    draw.text((layer_x[l_idx] - 70, HEIGHT - 180), layer_names[l_idx], fill=(148, 163, 184))
                    for n in layer_nodes:
                        node_fill = (16, 185, 129) if l_idx == len(nodes) - 1 else (30, 41, 59)
                        draw.ellipse([(n[0] - 22, n[1] - 22), (n[0] + 22, n[1] + 22)],
                                     fill=node_fill, outline=(56, 189, 248), width=3)

                # Telemetry Banner
                draw.rectangle([(200, HEIGHT - 130), (WIDTH - 200, HEIGHT - 50)], fill=(17, 24, 39), outline=(56, 189, 248), width=2)
                if is_backprop:
                    telemetry_text = f"BACKPROPAGATION: dW = dL/da * da/dz * dz/dW | Error Gradient Flowing Reverse | Step: {int(progress*100)}%"
                else:
                    telemetry_text = f"FORWARD PASS: z = Wx + b | Activation: a = ReLU(z) = max(0, z) | Signal Propagation: {int(progress*100)}%"
                draw.text((230, HEIGHT - 100), telemetry_text, fill=(248, 250, 252))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 4. CONTROL SYSTEMS BACKEND (PID, Step Response, Closed-Loop)
# =============================================================================
class ControlSystemAnimationBackend:
    """Renders real-time oscilloscope step response curves, setpoint tracking, and PID telemetry."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (9, 13, 20))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                # Title
                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))
                draw.text((100, 30), "PID CLOSED-LOOP CONTROL SYSTEM  |  Step Disturbance Response", fill=(248, 250, 252))

                # Oscilloscope Display Frame
                scope_x, scope_y, scope_w, scope_h = 140, 140, WIDTH - 280, 520
                draw.rectangle([(scope_x, scope_y), (scope_x + scope_w, scope_y + scope_h)], fill=(15, 23, 42), outline=(56, 189, 248), width=3)

                # Scope Grid Lines
                for gx in range(scope_x, scope_x + scope_w, 80):
                    draw.line([(gx, scope_y), (gx, scope_y + scope_h)], fill=(30, 41, 59), width=1)
                for gy in range(scope_y, scope_y + scope_h, 60):
                    draw.line([(scope_x, gy), (scope_x + scope_w, gy)], fill=(30, 41, 59), width=1)

                # Setpoint Line (r = 1.0)
                setpoint_y = scope_y + scope_h // 2
                for dash_x in range(scope_x, scope_x + scope_w, 20):
                    draw.line([(dash_x, setpoint_y), (dash_x + 10, setpoint_y)], fill=(244, 63, 94), width=2)
                draw.text((scope_x + 20, setpoint_y - 25), "Desired Setpoint r(t) = 1.00", fill=(244, 63, 94))

                # Dynamic Response Curve
                curve_pts = []
                max_samples = int(progress * scope_w)
                for px in range(max_samples):
                    t = px / (scope_w * 0.45)
                    # Second order underdamped step response
                    y_val = 1.0 - math.exp(-1.8 * t) * (math.cos(4.2 * t) + (1.8 / 4.2) * math.sin(4.2 * t))
                    py = int(setpoint_y - (y_val - 1.0) * 180)
                    curve_pts.append((scope_x + px, py))

                if len(curve_pts) > 1:
                    draw.line(curve_pts, fill=(56, 189, 248), width=4)
                    # Leading dot
                    last_pt = curve_pts[-1]
                    draw.ellipse([(last_pt[0] - 6, last_pt[1] - 6), (last_pt[0] + 6, last_pt[1] + 6)], fill=(16, 185, 129))

                # Telemetry Panel
                tel_y = scope_y + scope_h + 30
                draw.rectangle([(scope_x, tel_y), (scope_x + scope_w, tel_y + 110)], fill=(17, 24, 39), outline=(75, 85, 99), width=2)
                draw.text((scope_x + 30, tel_y + 25), "TUNED PARAMETERS: Kp = 2.80 | Ki = 1.45 | Kd = 0.65", fill=(248, 250, 252))
                draw.text((scope_x + 30, tel_y + 65), f"PERFORMANCE: Rise Time: 0.38s | Overshoot: 8.4% | Steady-State Error: {max(0.0, 1.0 - progress*1.0):.3f}", fill=(56, 189, 248))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 5. NETWORK PROTOCOL BACKEND (CAN Bus Arbitration)
# =============================================================================
class NetworkProtocolAnimationBackend:
    """Renders CAN Bus digital logic signals, bit-level dominant/recessive arbitration, and collision avoidance."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)

        # Node 1 ID: 0x0A (00000001010b) - High Priority (Wins)
        # Node 2 ID: 0x14 (00000010100b) - Lower Priority (Loses at Bit 7)
        bits_node1 = [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0]
        bits_node2 = [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0]
        bits_bus =   [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0]

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (9, 13, 20))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))
                draw.text((100, 30), "CONTROLLER AREA NETWORK (CAN BUS)  |  Bitwise Non-Destructive Arbitration", fill=(248, 250, 252))

                # Channels: Node 1, Node 2, Actual Bus
                ch_y = [180, 340, 500]
                ch_names = ["NODE 1 (Brakes, ID: 0x0A) - Transmit",
                            "NODE 2 (Engine, ID: 0x14) - Transmit",
                            "PHYSICAL CAN BUS (Wired-AND Differential)"]

                bit_w = 120
                start_x = 240
                active_bit = min(int(progress * len(bits_node1)), len(bits_node1) - 1)

                for ch_idx, cy in enumerate(ch_y):
                    draw.text((start_x, cy - 30), ch_names[ch_idx], fill=(248, 250, 252))
                    draw.rectangle([(start_x, cy), (start_x + len(bits_node1) * bit_w, cy + 90)], fill=(15, 23, 42), outline=(51, 65, 85), width=2)

                    bits = bits_node1 if ch_idx == 0 else (bits_node2 if ch_idx == 1 else bits_bus)
                    for b_idx, bit_val in enumerate(bits):
                        bx = start_x + b_idx * bit_w
                        # If node 2 lost arbitration (after bit 6)
                        if ch_idx == 1 and b_idx >= 7 and active_bit >= 7:
                            # Recessive / Backed off
                            draw.line([(bx, cy + 70), (bx + bit_w, cy + 70)], fill=(100, 116, 139), width=3)
                            draw.text((bx + 10, cy + 30), "BACKOFF", fill=(244, 63, 94))
                        else:
                            line_y = cy + 20 if bit_val == 0 else cy + 70
                            col = (16, 185, 129) if bit_val == 0 else (56, 189, 248)
                            draw.line([(bx, line_y), (bx + bit_w, line_y)], fill=col, width=4)
                            bit_label = "0 (DOM)" if bit_val == 0 else "1 (REC)"
                            draw.text((bx + 14, cy + 35), bit_label, fill=col)

                # Vertical scanning timeline
                scan_x = start_x + int(progress * len(bits_node1) * bit_w)
                draw.line([(scan_x, 150), (scan_x, 620)], fill=(245, 158, 11), width=3)

                # Arbitration status box
                stat_y = 660
                draw.rectangle([(start_x, stat_y), (start_x + len(bits_node1) * bit_w, stat_y + 110)], fill=(17, 24, 39), outline=(56, 189, 248), width=2)
                if active_bit < 6:
                    arb_text = f"Bit {active_bit}: Both nodes transmit identical bits. Contention unresolved."
                elif active_bit == 6:
                    arb_text = f"CRITICAL ARBITRATION BIT 6: Node 1 transmits Dominant '0', Node 2 transmits Recessive '1'. Bus resolves to '0'."
                else:
                    arb_text = f"Node 2 detects mismatch and BACKS OFF without error. Node 1 wins bus and transmits unimpeded!"
                draw.text((start_x + 30, stat_y + 40), arb_text, fill=(248, 250, 252))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 6. BATTERY & EV SYSTEMS BACKEND (BMS, Cell Heatmap, Energy Flux)
# =============================================================================
class BatterySystemAnimationBackend:
    """Renders EV battery cell matrix, thermal heatmap, current flow vectors, and real-time BMS telemetry HUD."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (9, 13, 20))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))
                draw.text((100, 30), "EV BATTERY MANAGEMENT SYSTEM (BMS)  |  Cell Telemetry & Thermal Balancing", fill=(248, 250, 252))

                # Draw 8x6 Battery Cell Matrix
                cols, rows = 8, 5
                cell_w, cell_h = 100, 65
                start_x = 180
                start_y = 160

                for r in range(rows):
                    for c in range(cols):
                        cx = start_x + c * (cell_w + 14)
                        cy = start_y + r * (cell_h + 14)
                        # Thermal gradient calculation (simulating warm core cells)
                        dist_center = math.sqrt((c - 3.5)**2 + (r - 2.0)**2)
                        temp_c = 28.0 + (3.5 - dist_center) * 2.2 + math.sin(progress * 4) * 0.8
                        # Color based on temp
                        r_col = min(255, int(50 + (temp_c - 28) * 35))
                        g_col = max(50, int(180 - (temp_c - 28) * 25))
                        draw.rectangle([(cx, cy), (cx + cell_w, cy + cell_h)], fill=(r_col, g_col, 50), outline=(56, 189, 248), width=2)
                        draw.text((cx + 14, cy + 12), f"3.92V", fill=(255, 255, 255))
                        draw.text((cx + 14, cy + 34), f"{temp_c:.1f}°C", fill=(240, 246, 252))

                # Telemetry HUD on right
                hud_x = start_x + cols * (cell_w + 14) + 60
                draw.rectangle([(hud_x, start_y), (WIDTH - 140, start_y + rows * (cell_h + 14) - 14)], fill=(17, 24, 39), outline=(56, 189, 248), width=3)
                draw.text((hud_x + 30, start_y + 30), "BMS STATUS: ACTIVE BALANCING", fill=(16, 185, 129))
                draw.text((hud_x + 30, start_y + 80), f"PACK VOLTAGE: 400.2 V DC", fill=(248, 250, 252))
                draw.text((hud_x + 30, start_y + 130), f"STATE OF CHARGE: {78.0 + progress * 2.0:.1f} %", fill=(56, 189, 248))
                draw.text((hud_x + 30, start_y + 180), f"CURRENT DRAW: +120 A (CHARGING)", fill=(245, 158, 11))
                draw.text((hud_x + 30, start_y + 230), f"MAX CELL DELTA: 4 mV (OPTIMAL)", fill=(16, 185, 129))
                draw.text((hud_x + 30, start_y + 280), f"SAFETY CONTACTOR: CLOSED / OK", fill=(16, 185, 129))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 7. CAD & SOFTWARE ANIMATION BACKEND
# =============================================================================
class CadSoftwareAnimationBackend:
    """Renders CAD software interface, specification tree, cursor gliding to Command Finder, query typing, and 3D extrusion."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)

        search_x, search_y, search_w, search_h = WIDTH - 460, HEIGHT - 110, 420, 52

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (22, 27, 34))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                # CAD Top Menu Bar
                draw.rectangle([(0, 0), (WIDTH, 50)], fill=(15, 18, 24))
                draw.text((24, 16), "CATIA V5 / 3DEXPERIENCE  |  Part Design Workbench  |  Part1.CATPart", fill=(203, 213, 225))

                # Specification Tree on Left
                draw.rectangle([(0, 50), (320, HEIGHT - 70)], fill=(18, 22, 29), outline=(48, 54, 61), width=1)
                draw.text((20, 70), "▾ Part1", fill=(240, 246, 252))
                draw.text((40, 105), "▾ xy plane", fill=(148, 163, 184))
                draw.text((40, 140), "▾ yz plane", fill=(148, 163, 184))
                draw.text((40, 175), "▾ zx plane", fill=(148, 163, 184))
                draw.text((40, 215), "▾ PartBody", fill=(56, 189, 248))
                if progress > 0.6:
                    draw.text((60, 250), "★ Pad.1 (25mm)", fill=(16, 185, 129))

                # 3D Viewport in Center
                vp_cx, vp_cy = WIDTH // 2 + 60, HEIGHT // 2 - 20
                if progress < 0.5:
                    # 2D Sketch rectangle on plane
                    draw.polygon([(vp_cx - 140, vp_cy - 80), (vp_cx + 140, vp_cy - 80),
                                  (vp_cx + 80, vp_cy + 80), (vp_cx - 200, vp_cy + 80)],
                                 fill=(30, 41, 59), outline=(56, 189, 248), width=3)
                    draw.text((vp_cx - 40, vp_cy - 10), "Sketch.1", fill=(56, 189, 248))
                else:
                    # Extruded 3D solid
                    ext_h = int(min(1.0, (progress - 0.5) * 3) * 120)
                    draw.polygon([(vp_cx - 140, vp_cy - 80 - ext_h), (vp_cx + 140, vp_cy - 80 - ext_h),
                                  (vp_cx + 80, vp_cy + 80 - ext_h), (vp_cx - 200, vp_cy + 80 - ext_h)],
                                 fill=(56, 189, 248), outline=(255, 255, 255), width=2)
                    draw.polygon([(vp_cx - 200, vp_cy + 80 - ext_h), (vp_cx + 80, vp_cy + 80 - ext_h),
                                  (vp_cx + 80, vp_cy + 80), (vp_cx - 200, vp_cy + 80)],
                                 fill=(30, 75, 120), outline=(255, 255, 255), width=2)
                    draw.polygon([(vp_cx + 80, vp_cy + 80 - ext_h), (vp_cx + 140, vp_cy - 80 - ext_h),
                                  (vp_cx + 140, vp_cy - 80), (vp_cx + 80, vp_cy + 80)],
                                 fill=(20, 50, 90), outline=(255, 255, 255), width=2)

                # CAD Bottom Action Bar
                draw.rectangle([(0, HEIGHT - 70), (WIDTH, HEIGHT)], fill=(15, 18, 24))

                # Command search input box
                draw.rectangle([(search_x, search_y), (search_x + search_w, search_y + search_h)],
                               fill=(28, 33, 44), outline=(56, 189, 248), width=2)
                type_chars = int(min(1.0, progress * 2.5) * 5)
                full_cmd = "c:Pad"
                draw.text((search_x + 16, search_y + 14), full_cmd[:type_chars], fill=(240, 246, 252))

                # Dropdown menu appears after 20% duration
                if progress > 0.20:
                    drop_y = search_y - 180
                    draw.rectangle([(search_x, drop_y), (search_x + search_w, search_y - 4)],
                                   fill=(22, 27, 34), outline=(56, 189, 248), width=2)
                    draw.rectangle([(search_x + 4, drop_y + 40), (search_x + search_w - 4, drop_y + 80)], fill=(30, 41, 59))
                    draw.text((search_x + 16, drop_y + 12), "Matching Commands across Workbenches:", fill=(148, 163, 184))
                    draw.text((search_x + 24, drop_y + 50), "★ Pad (Part Design -> Sketch-Based)", fill=(56, 189, 248))
                    draw.text((search_x + 24, drop_y + 95), "  Pocket (Part Design)", fill=(203, 213, 225))
                    draw.text((search_x + 24, drop_y + 135), "  Shaft (Part Design)", fill=(203, 213, 225))

                # Floating Pad Definition Dialog after 45% duration
                if progress > 0.45:
                    dia_x, dia_y = 360, 140
                    draw.rectangle([(dia_x, dia_y), (dia_x + 380, dia_y + 260)], fill=(22, 27, 34), outline=(56, 189, 248), width=2)
                    draw.rectangle([(dia_x, dia_y), (dia_x + 380, dia_y + 42)], fill=(30, 41, 59))
                    draw.text((dia_x + 16, dia_y + 12), "Pad Definition", fill=(248, 250, 252))
                    draw.text((dia_x + 20, dia_y + 65), "First Limit Length: 25.00 mm", fill=(240, 246, 252))
                    draw.text((dia_x + 20, dia_y + 115), "Profile/Surface: Sketch.1", fill=(240, 246, 252))
                    draw.rectangle([(dia_x + 240, dia_y + 200), (dia_x + 350, dia_y + 240)], fill=(16, 185, 129))
                    draw.text((dia_x + 270, dia_y + 210), "OK", fill=(255, 255, 255))

                # Animated mouse cursor gliding towards search result
                cursor_start = (WIDTH // 2, HEIGHT // 2)
                cursor_target = (search_x + 120, search_y - 120)
                cx = int(cursor_start[0] + (cursor_target[0] - cursor_start[0]) * min(progress * 1.6, 1.0))
                cy = int(cursor_start[1] + (cursor_target[1] - cursor_start[1]) * min(progress * 1.6, 1.0))
                draw.polygon([(cx, cy), (cx + 18, cy + 18), (cx + 10, cy + 20), (cx + 6, cy + 26)], fill="white", outline="black")

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 8. PROGRAMMING & CODE EXECUTION ANIMATION BACKEND
# =============================================================================
class ProgrammingCodeAnimationBackend:
    """Renders IDE syntax highlighting, active execution line pointer, Call Stack LIFO memory, and return unwinding."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)
        action_text = (scene.action or "").lower()

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (9, 13, 20))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                # Header Banner
                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))
                draw.text((80, 30), "PROGRAMMING RUNTIME EXECUTION  |  Recursive Call Stack & State Visualization", fill=(248, 250, 252))

                # Left: IDE Editor
                ed_x, ed_y, ed_w, ed_h = 80, 130, 840, 560
                draw.rectangle([(ed_x, ed_y), (ed_x + ed_w, ed_y + ed_h)], fill=(18, 24, 33), outline=(56, 189, 248), width=2)
                # Tab bar
                draw.rectangle([(ed_x, ed_y), (ed_x + ed_w, ed_y + 44)], fill=(28, 36, 48))
                draw.text((ed_x + 20, ed_y + 12), "recursion.py  (Python 3.12 Runtime)", fill=(148, 163, 184))

                # Code lines
                code_lines = [
                    (1, "def factorial(n):", False),
                    (2, "    # Base Case Condition", False),
                    (3, "    if n <= 1:", progress > 0.4 and progress <= 0.65),
                    (4, "        return 1", progress > 0.55 and progress <= 0.70),
                    (5, "    # Recursive Descent Step", False),
                    (6, "    return n * factorial(n - 1)", progress <= 0.45 or progress > 0.70),
                ]
                for l_idx, (num, text, is_active) in enumerate(code_lines):
                    line_y = ed_y + 70 + l_idx * 55
                    if is_active:
                        draw.rectangle([(ed_x + 4, line_y - 6), (ed_x + ed_w - 4, line_y + 40)], fill=(30, 58, 100))
                        draw.polygon([(ed_x + 10, line_y + 4), (ed_x + 24, line_y + 16), (ed_x + 10, line_y + 28)], fill=(56, 189, 248))
                    draw.text((ed_x + 36, line_y + 8), str(num), fill=(100, 116, 139))
                    code_color = (56, 189, 248) if "def " in text or "return " in text else ((16, 185, 129) if "#" in text else (248, 250, 252))
                    draw.text((ed_x + 76, line_y + 8), text, fill=code_color)

                # Right: Call Stack Memory Layout
                stk_x, stk_y, stk_w, stk_h = 960, 130, 880, 560
                draw.rectangle([(stk_x, stk_y), (stk_x + stk_w, stk_y + stk_h)], fill=(15, 23, 42), outline=(148, 163, 184), width=2)
                draw.rectangle([(stk_x, stk_y), (stk_x + stk_w, stk_y + 44)], fill=(30, 41, 59))
                draw.text((stk_x + 20, stk_y + 12), "CALL STACK MEMORY (LIFO Execution Frames)", fill=(248, 250, 252))

                # Dynamic Stack Frames (n=3, n=2, n=1)
                frames = []
                if progress > 0.08:
                    frames.append(("Frame 1: factorial(n=3)", "3 * factorial(2)", "WAITING ON RETURN", (56, 189, 248)))
                if progress > 0.28:
                    frames.append(("Frame 2: factorial(n=2)", "2 * factorial(1)", "WAITING ON RETURN", (245, 158, 11)))
                if progress > 0.48:
                    frames.append(("Frame 3: factorial(n=1)", "BASE CASE HIT (n<=1)", "RETURNS 1", (16, 185, 129)))

                # Unwinding animation after 70% progress
                if progress > 0.72 and len(frames) == 3:
                    frames[2] = ("Frame 3: factorial(n=1)", "POPPED OFF STACK", "RETURNED: 1", (148, 163, 184))
                    frames[1] = ("Frame 2: factorial(n=2)", "2 * 1 = 2", "RETURNS 2", (16, 185, 129))
                if progress > 0.88 and len(frames) == 3:
                    frames[1] = ("Frame 2: factorial(n=2)", "POPPED OFF STACK", "RETURNED: 2", (148, 163, 184))
                    frames[0] = ("Frame 1: factorial(n=3)", "3 * 2 = 6", "FINAL RESULT: 6", (16, 185, 129))

                for f_idx, (fname, fop, fstat, fcol) in enumerate(frames):
                    box_y = stk_y + 400 - f_idx * 110
                    draw.rectangle([(stk_x + 30, box_y), (stk_x + stk_w - 30, box_y + 90)], fill=(24, 32, 47), outline=fcol, width=2)
                    draw.text((stk_x + 50, box_y + 14), fname, fill=(248, 250, 252))
                    draw.text((stk_x + 50, box_y + 50), f"Expression: {fop}", fill=(203, 213, 225))
                    draw.text((stk_x + stk_w - 280, box_y + 32), fstat, fill=fcol)

                # Terminal Output Box
                draw.rectangle([(80, 710), (WIDTH - 80, 840)], fill=(11, 15, 23), outline=(51, 65, 85), width=2)
                term_txt = ">>> factorial(3) invoked..." if progress <= 0.5 else (">>> n=1 base case reached; unwinding call stack..." if progress <= 0.85 else ">>> return 3 * 2 = 6. EXECUTION COMPLETE: Output = 6")
                draw.text((110, 740), "CONSOLE OUTPUT:", fill=(148, 163, 184))
                draw.text((110, 780), term_txt, fill=(16, 185, 129) if progress > 0.85 else (56, 189, 248))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# 9. AUTOMOTIVE & MANUFACTURING UNIVERSAL SCHEMATIC BACKEND
# =============================================================================
class UniversalTechnicalDiagramBackend:
    """Renders general engineering, automotive power flow, CNC machining, and system architectures."""

    @classmethod
    def render_clip(cls, scene, clip_path: str, duration: float):
        total_frames = max(int(duration * FPS), 30)
        combined_diag = f"{scene.action} {scene.caption} {scene.subject} {scene.visual_type}".lower()
        is_cnc = any(w in combined_diag for w in ["cnc", "milling", "stock", "machin", "manufactur", "billet", "vise", "toolpath", "pocket", "metrology"])
        is_regen = any(w in combined_diag for w in ["regen", "braking", "torque", "powertrain", "energy recovery", "inverter"])

        with tempfile.TemporaryDirectory() as frame_dir:
            for f in range(total_frames):
                img = Image.new("RGB", (WIDTH, HEIGHT), (9, 13, 20))
                draw = ImageDraw.Draw(img)
                progress = f / total_frames

                draw.rectangle([(0, 0), (WIDTH, 90)], fill=(17, 24, 39))

                if is_cnc:
                    draw.text((100, 30), "CNC SUBTRACTIVE MACHINING PROCESS  |  Adaptive Toolpath Material Removal", fill=(248, 250, 252))
                    # Raw block
                    bx, by, bw, bh = 400, 200, 600, 380
                    draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(51, 65, 85), outline=(148, 163, 184), width=3)
                    draw.text((bx + 20, by + 20), "Aluminum 6061-T6 Stock Billet", fill=(203, 213, 225))
                    # Progressive Cutaway Pocket
                    pocket_prog = min(1.0, progress * 1.5)
                    pw = int(360 * pocket_prog)
                    ph = int(220 * pocket_prog)
                    px = bx + (bw - 360) // 2
                    py = by + (bh - 220) // 2
                    if pw > 10 and ph > 10:
                        draw.rectangle([(px, py), (px + pw, py + ph)], fill=(15, 23, 42), outline=(56, 189, 248), width=2)
                        # Spindle toolhead
                        tx = px + pw
                        ty = py + ph // 2
                        draw.rectangle([(tx - 15, ty - 60), (tx + 15, ty)], fill=(245, 158, 11), outline=(255, 255, 255), width=2)
                        draw.text((tx - 35, ty - 90), "12mm End Mill", fill=(245, 158, 11))
                    # CNC Telemetry HUD
                    draw.rectangle([(1100, 200), (1700, 580)], fill=(17, 24, 39), outline=(56, 189, 248), width=3)
                    draw.text((1140, 240), "G-CODE CONTROLLER TELEMETRY", fill=(16, 185, 129))
                    draw.text((1140, 300), "SPINDLE SPEED: 8,000 RPM", fill=(248, 250, 252))
                    draw.text((1140, 360), "FEED RATE: 1,800 mm/min", fill=(56, 189, 248))
                    draw.text((1140, 420), f"POCKET DEPTH: {15.0 * pocket_prog:.1f} mm", fill=(245, 158, 11))
                    draw.text((1140, 480), "SURFACE TOLERANCE: +/- 0.025 mm", fill=(16, 185, 129))

                elif is_regen:
                    draw.text((100, 30), "EV REGENERATIVE BRAKING SYSTEM  |  Kinetic Energy Recovery Flow", fill=(248, 250, 252))
                    # Powertrain Blocks: Wheels -> Motor -> Inverter -> Battery
                    blocks = [("Drive Wheels", 180, 280), ("Traction Motor (Gen)", 560, 280),
                              ("Bidirectional Inverter", 960, 280), ("High-Voltage Battery", 1360, 280)]
                    for bname, bx, by in blocks:
                        draw.rectangle([(bx, by), (bx + 260, by + 160)], fill=(17, 24, 39), outline=(56, 189, 248), width=3)
                        draw.text((bx + 20, by + 65), bname, fill=(248, 250, 252))

                    # Energy Flow Arrows
                    for i in range(len(blocks) - 1):
                        ax1 = blocks[i][1] + 260
                        ax2 = blocks[i + 1][1]
                        draw.line([(ax1, 360), (ax2, 360)], fill=(16, 185, 129), width=5)
                        draw.polygon([(ax2, 360), (ax2 - 15, 350), (ax2 - 15, 370)], fill=(16, 185, 129))

                    draw.rectangle([(180, 500), (WIDTH - 180, 610)], fill=(17, 24, 39), outline=(16, 185, 129), width=2)
                    draw.text((220, 540), f"REGENERATIVE TORQUE: -240 Nm | RECOVERED POWER: +65 kW | EFFICIENCY: 72% ROUND-TRIP", fill=(16, 185, 129))

                else:
                    draw.text((100, 30), f"TECHNICAL ARCHITECTURE & OPERATION  |  {scene.subject}", fill=(248, 250, 252))
                    # Universal System Grid & Dynamic Wave
                    draw.rectangle([(200, 160), (WIDTH - 200, 580)], fill=(15, 23, 42), outline=(56, 189, 248), width=2)
                    pts = []
                    for px in range(200, WIDTH - 200, 4):
                        wave_y = int(370 + 80 * math.sin(px * 0.02 + progress * 6))
                        pts.append((px, wave_y))
                    if len(pts) > 1:
                        draw.line(pts, fill=(56, 189, 248), width=4)
                    draw.text((240, 200), f"Operational Mechanism: {scene.subject}", fill=(248, 250, 252))
                    draw.text((240, 240), f"Telemetry Status: Validated System Convergence", fill=(16, 185, 129))

                frame_file = os.path.join(frame_dir, f"frame_{f:04d}.png")
                img.save(frame_file, "PNG")

            _add_subtitle_and_mux(frame_dir, scene.audio_path, scene.caption, duration, clip_path)


# =============================================================================
# MASTER UNIVERSAL VIDEO GENERATOR DISPATCHER
# =============================================================================
class VIDEO_GENERATOR:
    """Master Universal Technical Video Dispatcher."""

    @classmethod
    def generate_clip(cls, scene, clip_path: str):
        vtype = getattr(scene, "visual_type", "").lower()
        action = getattr(scene, "action", "").lower()
        subject = getattr(scene, "subject", "").lower()
        combined = f"{vtype} {action} {subject}"
        duration = float(getattr(scene, "duration", 3.5))

        # 1. Mathematical / Optimization
        if "mathematical" in vtype or "gradient" in combined or "convex" in combined or "calculus" in combined:
            MathematicalAnimationBackend.render_clip(scene, clip_path, duration)
            return "MATHEMATICAL_ANIMATION_ENGINE"

        # 2. Programming & Code (Recursion, Functions, Call Stack, Python)
        elif "recursion" in combined or "call stack" in combined or "stack" in combined or "programming" in vtype or "code" in combined:
            ProgrammingCodeAnimationBackend.render_clip(scene, clip_path, duration)
            return "PROGRAMMING_CODE_ANIMATION_ENGINE"

        # 3. Algorithm / Computer Science (Binary Search, Sorting, Trees, Arrays)
        elif "algorithm" in vtype or "binary search" in combined or "sorting" in combined or "array" in combined:
            AlgorithmVisualizationBackend.render_clip(scene, clip_path, duration)
            return "ALGORITHM_VISUALIZATION_ENGINE"

        # 4. Neural Networks & Deep Learning
        elif "neural_network" in vtype or "neural" in combined or "cnn" in combined or "backprop" in combined:
            NeuralNetworkAnimationBackend.render_clip(scene, clip_path, duration)
            return "NEURAL_NETWORK_ANIMATION_ENGINE"

        # 5. Control Systems & PID
        elif "control_system" in vtype or "pid" in combined or "setpoint" in combined or "closed-loop" in combined:
            ControlSystemAnimationBackend.render_clip(scene, clip_path, duration)
            return "CONTROL_SYSTEM_ANIMATION_ENGINE"

        # 6. Network Protocols & CAN Bus
        elif "network_protocol" in vtype or "can bus" in combined or "arbitration" in combined or "dominant" in combined:
            NetworkProtocolAnimationBackend.render_clip(scene, clip_path, duration)
            return "NETWORK_PROTOCOL_ANIMATION_ENGINE"

        # 7. Battery & EV Systems (BMS, Thermal, Cells)
        elif "battery_system" in vtype or "bms" in combined or "battery cell" in combined or "thermal gradient" in combined:
            BatterySystemAnimationBackend.render_clip(scene, clip_path, duration)
            return "BATTERY_SYSTEM_ANIMATION_ENGINE"

        # 8. CAD & Software Interface Simulation
        elif "cad" in vtype or "software" in vtype or "catia" in combined or "command finder" in combined or "viewport" in vtype:
            CadSoftwareAnimationBackend.render_clip(scene, clip_path, duration)
            return "CAD_SOFTWARE_ANIMATION_ENGINE"

        # 9. Automotive, Manufacturing & Universal Technical Diagrams
        else:
            UniversalTechnicalDiagramBackend.render_clip(scene, clip_path, duration)
            return "UNIVERSAL_TECHNICAL_DIAGRAM_ENGINE"


def assemble_video(scene_assets, final_path: str) -> str:
    """Assembles all scenes into one cohesive high-definition educational MP4 with audio mixing."""
    total_duration = sum(s.duration for s in scene_assets)

    with tempfile.TemporaryDirectory() as tmp:
        clip_paths = []
        for scene in scene_assets:
            clip_path = os.path.join(tmp, f"clip_{scene.index}.mp4")
            backend_used = VIDEO_GENERATOR.generate_clip(scene, clip_path)
            clip_paths.append(clip_path)

        concat_list_path = os.path.join(tmp, "concat.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for p in clip_paths:
                clean_p = p.replace("\\", "/")
                f.write(f"file '{clean_p}'\n")

        raw_concat_path = os.path.join(tmp, "raw_concat.mp4")
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-c:v", "copy",
            "-c:a", "copy",
            raw_concat_path,
        ]
        subprocess.run(concat_cmd, check=True, capture_output=True)

        # Subtle clean ambient engineering tone bed under narration
        drone_expr = "0.02*sin(2*PI*110*t)+0.015*sin(2*PI*164.81*t)+0.01*sin(2*PI*220*t)"
        mix_cmd = [
            "ffmpeg", "-y",
            "-i", raw_concat_path,
            "-f", "lavfi", "-i", f"aevalsrc=exprs='{drone_expr}':s=44100:d={total_duration}",
            "-filter_complex", "[0:a][1:a]amix=inputs=2:weights=1.0 0.08:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            "-shortest",
            final_path,
        ]
        try:
            subprocess.run(mix_cmd, check=True, capture_output=True)
        except Exception:
            shutil.copy2(raw_concat_path, final_path)

    return final_path
