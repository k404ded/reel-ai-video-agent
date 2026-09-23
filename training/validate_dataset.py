"""
validate_dataset.py
Validates syntax, schema conformity, required fields, and educational constraints
for all generated training datasets.
"""

import json
import os
import sys

REQUIRED_TOP_LEVEL_KEYS = [
    "user_prompt",
    "topic",
    "content_type",
    "learning_objective",
    "required_visuals",
    "required_actions",
    "presenter_required",
    "software_required",
    "mathematical_visualization_required",
    "technical_visualization_required",
    "camera_shots",
    "scene_sequence",
    "narration_intent",
    "expected_output_behavior",
    "prohibited_visual_behavior",
]

REQUIRED_SCENE_KEYS = [
    "scene_id",
    "duration",
    "shot_type",
    "visual_type",
    "subject",
    "action",
    "environment",
    "camera",
    "animation",
    "technical_content",
    "on_screen_text",
    "narration",
    "transition",
    "generation_requirements",
]

VALID_CONTENT_TYPES = [
    "TECHNICAL_CONCEPT",
    "MATHEMATICAL_CONCEPT",
    "SOFTWARE_TUTORIAL",
    "CAD_TUTORIAL",
    "PROGRAMMING_TUTORIAL",
    "ENGINEERING_PROCESS",
    "AUTOMOTIVE_PROCESS",
    "GENERAL_EDUCATIONAL",
]


def validate():
    base_dir = os.path.dirname(__file__)
    plans_file = os.path.join(base_dir, "educational_video_plans.jsonl")
    
    if not os.path.exists(plans_file):
        print(f"[FAIL] Missing {plans_file}")
        sys.exit(1)

    with open(plans_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"[INFO] Validating {len(lines)} records in {plans_file}...")

    seen_categories = set()
    total_scenes = 0

    BANNED_METAPHORS = [
        "car driving", "road", "vehicle", "highway", "traffic", "rollercoaster",
        "sci-fi portal", "fireworks", "hall of mirrors", "nesting doll",
        "hiker", "cartoon sawmill", "lightning bolt"
    ]

    for i, line in enumerate(lines, 1):
        try:
            record = json.loads(line)
        except Exception as exc:
            print(f"[FAIL] Line {i}: Invalid JSON - {exc}")
            sys.exit(1)

        # Check top-level keys
        for key in REQUIRED_TOP_LEVEL_KEYS:
            if key not in record:
                print(f"[FAIL] Record {i} ('{record.get('topic', 'unknown')}'): missing key '{key}'")
                sys.exit(1)

        c_type = record["content_type"]
        if c_type not in VALID_CONTENT_TYPES:
            print(f"[FAIL] Record {i}: invalid content_type '{c_type}'")
            sys.exit(1)
        seen_categories.add(c_type)

        scenes = record["scene_sequence"]
        if not isinstance(scenes, list) or len(scenes) < 3:
            print(f"[FAIL] Record {i}: requires at least 3 scenes, got {len(scenes) if isinstance(scenes, list) else 'non-list'}")
            sys.exit(1)

        for s_idx, scene in enumerate(scenes, 1):
            total_scenes += 1
            for skey in REQUIRED_SCENE_KEYS:
                if skey not in scene:
                    print(f"[FAIL] Record {i}, Scene {s_idx}: missing scene key '{skey}'")
                    sys.exit(1)

            # Ensure action is non-empty and descriptive
            if len(scene["action"].strip()) < 15:
                print(f"[FAIL] Record {i}, Scene {s_idx}: action description too short: '{scene['action']}'")
                sys.exit(1)

            # Check that prohibited metaphors are not present
            combined_text = (scene["action"] + " " + scene["subject"] + " " + scene["visual_type"]).lower()
            for bm in BANNED_METAPHORS:
                # 'vehicle' and 'road' are legitimate only in automotive/EV processes if not used as a metaphor
                if bm in ["vehicle", "road"] and c_type in ["AUTOMOTIVE_PROCESS", "ENGINEERING_PROCESS"]:
                    continue
                if bm in combined_text:
                    print(f"[FAIL] Record {i}, Scene {s_idx}: prohibited metaphor phrase '{bm}' found!")
                    sys.exit(1)

    print(f"[OK] Successfully validated all {len(lines)} records ({total_scenes} scenes).")
    print(f"[OK] Categories covered: {sorted(list(seen_categories))}")
    if len(seen_categories) < 8:
        print(f"[WARNING] Expected 8 categories, covered {len(seen_categories)}")
    else:
        print("[SUCCESS] All 8 required educational categories present and fully compliant!")


if __name__ == "__main__":
    validate()
