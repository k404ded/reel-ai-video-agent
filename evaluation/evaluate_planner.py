"""
evaluate_planner.py
Automated evaluation test harness for the AI Educational Video Director.
Runs the 10 benchmark topics, evaluates educational precision, verifies metaphor absence,
scores each storyboard on a 100-point rubric, and produces a comprehensive audit report.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from director import EducationalDirectorEngine, EducationalStoryboard


def load_eval_set() -> List[Dict[str, Any]]:
    path = os.path.join(os.path.dirname(__file__), "evaluation_set.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_storyboard(storyboard: EducationalStoryboard, eval_item: Dict[str, Any]) -> Dict[str, Any]:
    score_breakdown = {
        "content_type_routing": 0,
        "metaphor_absence": 0,
        "technical_visual_elements": 0,
        "visual_model_awareness": 0,
        "action_specification": 0,
    }
    notes = []

    # 1. Content-Type Routing (15 pts)
    expected_type = eval_item["expected_content_type"]
    if storyboard.content_type == expected_type:
        score_breakdown["content_type_routing"] = 15
    elif storyboard.content_type in ["TECHNICAL_CONCEPT", "ENGINEERING_PROCESS"] and expected_type in ["TECHNICAL_CONCEPT", "ENGINEERING_PROCESS", "AUTOMOTIVE_PROCESS"]:
        score_breakdown["content_type_routing"] = 12
    else:
        notes.append(f"Content-type mismatch: expected {expected_type}, got {storyboard.content_type}")

    # 2. Metaphor Absence (30 pts)
    combined_storyboard_text = (
        storyboard.title + " " +
        storyboard.visual_direction + " " +
        " ".join(f"{s.subject} {s.action} {s.visual_type} {s.technical_content}" for s in storyboard.scenes)
    ).lower()

    banned = eval_item.get("prohibited_metaphors", [])
    detected_metaphors = []
    for b in banned:
        # Context-aware check: don't flag "vehicle" or "battery" in automotive/EV topics
        if b in ["vehicle", "car"] and eval_item["expected_content_type"] == "AUTOMOTIVE_PROCESS":
            continue
        if b in combined_storyboard_text:
            detected_metaphors.append(b)

    if not detected_metaphors:
        score_breakdown["metaphor_absence"] = 30
    else:
        score_breakdown["metaphor_absence"] = 0
        notes.append(f"PROHIBITED METAPHORS DETECTED: {detected_metaphors}")

    # 3. Technical Visual Elements (25 pts)
    required_elements = eval_item.get("required_visual_elements", [])
    found_elements = [el for el in required_elements if el.lower() in combined_storyboard_text]
    fraction_found = len(found_elements) / max(len(required_elements), 1)
    score_breakdown["technical_visual_elements"] = round(fraction_found * 25, 1)
    if fraction_found < 0.6:
        missing = [el for el in required_elements if el not in found_elements]
        notes.append(f"Missing expected technical elements: {missing}")

    # 4. Visual Model Awareness (15 pts)
    req_vtypes = eval_item.get("required_visual_types", [])
    actual_vtypes = [s.visual_type for s in storyboard.scenes]
    vtype_match = any(vt in actual_vtypes for vt in req_vtypes)
    distinct_vtypes = len(set(actual_vtypes))

    if vtype_match and distinct_vtypes >= 2:
        score_breakdown["visual_model_awareness"] = 15
    elif vtype_match:
        score_breakdown["visual_model_awareness"] = 10
    else:
        score_breakdown["visual_model_awareness"] = 5
        notes.append(f"Lacks recommended visual types ({req_vtypes}), found: {actual_vtypes}")

    # 5. Action Specification (15 pts)
    valid_actions = [s for s in storyboard.scenes if len(s.action.strip()) >= 20 and not "static image" in s.action.lower()]
    action_ratio = len(valid_actions) / max(len(storyboard.scenes), 1)
    score_breakdown["action_specification"] = round(action_ratio * 15, 1)

    total_score = sum(score_breakdown.values())
    status = "PASS" if total_score >= 80 and not detected_metaphors else "FAIL"

    return {
        "id": eval_item["id"],
        "prompt": eval_item["prompt"],
        "total_score": round(total_score, 1),
        "status": status,
        "score_breakdown": score_breakdown,
        "notes": notes,
        "scenes_count": len(storyboard.scenes),
        "visual_types_used": list(set(actual_vtypes)),
    }


async def run_benchmark():
    eval_items = load_eval_set()
    engine = EducationalDirectorEngine()
    print("=" * 80)
    print("AI EDUCATIONAL VIDEO DIRECTOR — EVALUATION BENCHMARK")
    print(f"Total Test Prompts: {len(eval_items)} | Backend: {'Gemini API' if not engine.using_fallback else 'Local Fallback'}")
    print("=" * 80)

    results = []
    for item in eval_items:
        prompt = item["prompt"]
        print(f"\n[EVALUATING] {item['id']}: '{prompt}'...")
        try:
            storyboard = await engine.plan_video(prompt)
            res = evaluate_storyboard(storyboard, item)
            results.append(res)
            print(f"  -> Status: {res['status']} | Score: {res['total_score']}/100 | VTypes: {res['visual_types_used']}")
            if res["notes"]:
                for n in res["notes"]:
                    print(f"     * {n}")
        except Exception as exc:
            print(f"  -> ERROR during evaluation: {exc}")
            results.append({
                "id": item["id"],
                "prompt": prompt,
                "total_score": 0.0,
                "status": "ERROR",
                "notes": [str(exc)]
            })

    # Summary
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY REPORT")
    print("=" * 80)
    print(f"{'ID':<8} {'Status':<8} {'Score':<8} {'Prompt':<45}")
    print("-" * 80)
    total_score_sum = 0
    passed_count = 0
    for r in results:
        total_score_sum += r["total_score"]
        if r["status"] == "PASS":
            passed_count += 1
        print(f"{r['id']:<8} {r['status']:<8} {r['total_score']:<8} {r['prompt'][:43]:<45}")

    avg_score = round(total_score_sum / max(len(results), 1), 1)
    pass_rate = round((passed_count / max(len(results), 1)) * 100, 1)
    print("-" * 80)
    print(f"Total Passed: {passed_count}/{len(results)} ({pass_rate}%) | Average Score: {avg_score}/100")
    print("=" * 80)

    # Save results to evaluation/benchmark_report.json
    report_path = os.path.join(os.path.dirname(__file__), "benchmark_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"average_score": avg_score, "pass_rate": pass_rate, "results": results}, f, indent=2)
    print(f"[OK] Full benchmark report saved to {report_path}")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
