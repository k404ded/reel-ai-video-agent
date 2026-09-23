"""
validator.py
Quality Control and Metaphor Validation Layer for Educational Video Storyboards.
Detects unconstrained metaphors, checks technical primitives, validates shot variety,
and triggers automatic scene regeneration / correction before final video rendering.
"""

import re
from typing import Tuple, List, Dict, Any
from .storyboard import EducationalStoryboard, StoryboardScene, ContentType, VisualType, ShotType
from .router import ContentTypeRouter


BANNED_METAPHORS_BY_TYPE = {
    ContentType.MATHEMATICAL_CONCEPT.value: [
        r"\bcar\b", r"\bcars\b", r"\bdriving\b", r"\broad\b", r"\broads\b", r"\bhighway\b",
        r"\bvehicle\b", r"\bvehicles\b", r"\brollercoaster\b", r"\bmountain landscape\b",
        r"\bhiker\b", r"\bhiking\b", r"\bball rolling\b", r"\bportal\b", r"\bgalaxy\b"
    ],
    ContentType.CAD_TUTORIAL.value: [
        r"\bspaceship\b", r"\bportal\b", r"\bmagic wand\b", r"\bfantasy\b",
        r"\bsuit and tie\b", r"\bhandshake\b", r"\bspreadsheet\b", r"\bcalculator\b"
    ],
    ContentType.PROGRAMMING_TUTORIAL.value: [
        r"\brussian doll\b", r"\bnesting doll\b", r"\bhall of mirrors\b", r"\bbottomless pit\b",
        r"\brabbit hole\b", r"\bmatrix rain\b"
    ],
    ContentType.SOFTWARE_TUTORIAL.value: [
        r"\bboxing glove\b", r"\bfight\b", r"\btrain crash\b", r"\bexplosion\b",
        r"\bcolliding cubes\b", r"\bmatrix rain\b"
    ],
    ContentType.TECHNICAL_CONCEPT.value: [
        r"\bcar\b", r"\bdriving\b", r"\bhighway\b", r"\bhuman brain thinking\b",
        r"\bcosmic beam\b", r"\bmagic\b"
    ],
    ContentType.AUTOMOTIVE_PROCESS.value: [
        r"\bpolice car\b", r"\btraffic jam\b", r"\btalking car\b", r"\blightning strike\b"
    ],
    ContentType.ENGINEERING_PROCESS.value: [
        r"\baction movie\b", r"\bfireworks\b", r"\blaser melting\b", r"\bdancing robot\b",
        r"\bsledgehammer\b"
    ],
    ContentType.GENERAL_EDUCATIONAL.value: [
        r"\bsteering wheel in traffic\b", r"\bthermostat knob\b", r"\bmagic crystal\b",
        r"\bfireworks\b"
    ],
}


class QualityControlValidator:
    """Evaluates storyboards against educational rigor standards and auto-corrects non-compliant scenes."""

    @classmethod
    def validate_and_correct(cls, storyboard: EducationalStoryboard) -> EducationalStoryboard:
        warnings: List[str] = []
        c_type = storyboard.content_type
        rules = ContentTypeRouter.get_rules(c_type)
        banned_patterns = BANNED_METAPHORS_BY_TYPE.get(c_type, [])

        # 1. Evaluate and correct each scene
        for i, scene in enumerate(storyboard.scenes):
            scene_text = f"{scene.subject} {scene.action} {scene.visual_type} {scene.technical_content}".lower()
            
            # Check 1: Prohibited Metaphors
            metaphor_flagged = False
            for pat in banned_patterns:
                match = re.search(pat, scene_text)
                if match:
                    detected_word = match.group(0)
                    msg = (
                        f"Scene {scene.scene_id}: FAIL - Prohibited visual metaphor detected ('{detected_word}') "
                        f"for {c_type}. Direct technical visualization required."
                    )
                    warnings.append(msg)
                    metaphor_flagged = True
                    break

            # Check 2: Action Presence (reject static prompts)
            static_flagged = False
            if len(scene.action.strip()) < 15 or any(w in scene.action.lower() for w in ["static image", "still photo", "decorative visual"]):
                msg = f"Scene {scene.scene_id}: FAIL - Insufficient physical action described."
                warnings.append(msg)
                static_flagged = True

            # If failed, auto-correct the scene based on domain standards
            if metaphor_flagged or static_flagged:
                cls._auto_correct_scene(scene, i, len(storyboard.scenes), c_type, storyboard.topic, rules)
                scene.validation_status = "AUTO_CORRECTED"
            else:
                scene.validation_status = "PASSED"

        # 2. Shot variety check
        shot_types_used = set(s.shot_type for s in storyboard.scenes)
        if len(shot_types_used) < 2 and len(storyboard.scenes) >= 3:
            warnings.append("Storyboard lacks camera shot variety. Enforcing diverse camera angles.")
            rec_shots = rules.get("shot_sequence", [])
            for idx, s in enumerate(storyboard.scenes):
                if idx < len(rec_shots):
                    s.shot_type = rec_shots[idx]

        # 3. Visual type check
        for idx, s in enumerate(storyboard.scenes):
            if not s.visual_type or s.visual_type == "static_visual":
                rec_vtypes = rules.get("visual_types", [])
                s.visual_type = rec_vtypes[idx % len(rec_vtypes)] if rec_vtypes else VisualType.TECHNICAL_3D_ANIMATION.value

        storyboard.validation_warnings = warnings
        storyboard.validation_passed = len(warnings) == 0 or all(s.validation_status in ["PASSED", "AUTO_CORRECTED"] for s in storyboard.scenes)
        return storyboard

    @classmethod
    def _auto_correct_scene(
        cls,
        scene: StoryboardScene,
        scene_index: int,
        total_scenes: int,
        content_type: str,
        topic: str,
        rules: Dict[str, Any]
    ):
        """Rewrites a rejected scene into an educationally correct technical scene."""
        t_clean = topic.strip()

        if content_type == ContentType.MATHEMATICAL_CONCEPT.value:
            if scene_index == 0:
                scene.shot_type = ShotType.MEDIUM_SHOT.value
                scene.visual_type = VisualType.AI_PRESENTER.value
                scene.subject = "AI Mathematics Instructor"
                scene.action = "Instructor introduces the mathematical objective function beside a floating 3D coordinate system."
                scene.animation = "Coordinate axes materialize with labeled parameters w1, w2, and Loss."
                scene.technical_content = f"Objective Function J(w1, w2) for {t_clean}."
                scene.on_screen_text = f"{t_clean.upper()}: Formulation"
                scene.narration = f"To understand {t_clean}, we examine how parameters move across an objective error surface."
            elif scene_index == 1:
                scene.shot_type = ShotType.PERSPECTIVE_3D.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "3D Loss Surface and Parameter Position"
                scene.action = "Camera orbits a bowl-shaped convex 3D loss surface as an initial parameter point theta_0 is plotted high on the slope."
                scene.animation = "Contour lines highlight elevation; parameter point pulses on the surface slope."
                scene.technical_content = "Loss surface J(theta) and initial coordinate theta_0."
                scene.on_screen_text = "INITIAL STATE: High Error Region (theta_0)"
                scene.narration = "Initial random parameters place us high on the error surface with high loss."
            elif scene_index == 2:
                scene.shot_type = ShotType.CLOSE_UP.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "Gradient Vector Calculation"
                scene.action = "A tangent plane forms at the point. An arrow representing the gradient vector points uphill, while a negative gradient vector steps downhill."
                scene.animation = "Gradient vector nabla J points uphill; negative gradient vector -nabla J guides the step downhill."
                scene.technical_content = "Gradient vector: nabla J(theta) = [dJ/dw1, dJ/dw2]^T."
                scene.on_screen_text = "NEGATIVE GRADIENT: Stepping in Direction of Steepest Descent"
                scene.narration = "The gradient calculates the steepest ascent; stepping in the negative gradient direction guarantees decreased loss."
            elif scene_index == 3:
                scene.shot_type = ShotType.SPLIT_SCREEN.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "Iterative Updates and Formula"
                scene.action = "Successive parameter updates trace a path down the contour lines as the learning rate update equation pulses synchronously."
                scene.animation = "Trajectory points theta_1, theta_2, theta_3 step iteratively toward the basin."
                scene.technical_content = "theta_{t+1} = theta_t - alpha * nabla J(theta_t)"
                scene.on_screen_text = "UPDATE RULE: theta_{t+1} = theta_t - alpha * nabla J(theta_t)"
                scene.narration = "Scaled by the learning rate alpha, repeated iterations descend toward the minimum."
            else:
                scene.shot_type = ShotType.MEDIUM_SHOT.value
                scene.visual_type = VisualType.AI_PRESENTER.value
                scene.subject = "Instructor and Converged Minimum"
                scene.action = "Parameter point reaches the global minimum basin where gradient equals zero. Instructor summarizes convergence."
                scene.animation = "Gradient magnitude reaches zero; error curve flatlines at minimum."
                scene.technical_content = "|nabla J(theta*)| approx 0"
                scene.on_screen_text = "CONVERGENCE: Optimal Parameters theta*"
                scene.narration = "At the global minimum, the gradient approaches zero and training converges."

        elif content_type == ContentType.CAD_TUTORIAL.value:
            if scene_index == 0:
                scene.shot_type = ShotType.WIDE_WORKSPACE.value
                scene.visual_type = VisualType.AI_WORKSTATION_VIDEO.value
                scene.subject = "Mechanical Engineer at CAD Workstation"
                scene.action = "Mechanical engineer sits at a dual-monitor workstation reviewing a complex 3D CAD assembly."
                scene.animation = "3D CAD model rotates smoothly in viewport using 3D mouse."
                scene.technical_content = "Parametric 3D CAD environment."
                scene.on_screen_text = f"{t_clean.upper()}: CAD Workflow"
                scene.narration = f"When modeling complex parts in CAD, accessing commands efficiently is essential."
            elif scene_index == 1:
                scene.shot_type = ShotType.OVER_THE_SHOULDER.value
                scene.visual_type = VisualType.SOFTWARE_DEMONSTRATION.value
                scene.subject = "CAD User Interface and Command Search"
                scene.action = "Camera frames over engineer's shoulder onto CAD monitor. Cursor glides toward the Command Finder search bar."
                scene.animation = "Cursor moves with realistic acceleration to search bar."
                scene.technical_content = "Specification tree and Command Finder input field."
                scene.on_screen_text = "LOCATING TOOLS: Command Finder Search Bar"
                scene.narration = "Instead of searching nested menus, use the Command Finder to locate any tool instantly."
            elif scene_index == 2:
                scene.shot_type = ShotType.SCREEN_CLOSEUP.value
                scene.visual_type = VisualType.SCREEN_CLOSEUP.value
                scene.subject = "Command Query Entry and Live Filtering"
                scene.action = "Screen close-up as command keyword is entered. An auto-complete dropdown filters matching tools dynamically."
                scene.animation = "Text keystrokes appear; matching command row highlights in dropdown."
                scene.technical_content = "Dynamic command index and workbench breadcrumb."
                scene.on_screen_text = "INSTANT FILTERING: Auto-Complete Tool Search"
                scene.narration = "Typing the command name filters tools across all workbenches in real time."
            elif scene_index == 3:
                scene.shot_type = ShotType.VIEWPORT_SCREEN.value
                scene.visual_type = VisualType.SOFTWARE_DEMONSTRATION.value
                scene.subject = "Command Selection and 3D Execution"
                scene.action = "Engineer clicks the command; dialog box opens and previews the geometric feature on the 3D model."
                scene.animation = "Feature definition dialog opens; parametric 3D extrusion updates."
                scene.technical_content = "Feature parameters applied to 3D geometry."
                scene.on_screen_text = "FEATURE ACTIVATION: One-Click Execution"
                scene.narration = "Clicking the result activates the feature directly on your geometry."
            else:
                scene.shot_type = ShotType.MEDIUM_SHOT.value
                scene.visual_type = VisualType.AI_WORKSTATION_VIDEO.value
                scene.subject = "Engineer Finalizing CAD Model"
                scene.action = "Engineer verifies the updated feature tree solid. Camera pulls back to reveal the organized workstation."
                scene.animation = "Completed solid highlights in green."
                scene.technical_content = "Updated parametric solid."
                scene.on_screen_text = "WORKFLOW OPTIMIZED: Rapid CAD Design"
                scene.narration = "Mastering this workflow accelerates your daily modeling speed."

        else:
            # General Technical / Engineering fallback auto-correction
            rec_shots = rules.get("shot_sequence", [ShotType.MEDIUM_SHOT.value])
            rec_vtypes = rules.get("visual_types", [VisualType.TECHNICAL_3D_ANIMATION.value])
            scene.shot_type = rec_shots[scene_index % len(rec_shots)]
            scene.visual_type = rec_vtypes[scene_index % len(rec_vtypes)]
            scene.subject = f"Engineering Analysis of {t_clean}"
            scene.action = f"Technical visualization detailing physical operation and mechanism of {t_clean}."
            scene.animation = f"Animated diagram showing verified component interactions for {t_clean}."
            scene.technical_content = f"Calibrated technical parameters of {t_clean}."
            scene.on_screen_text = f"{t_clean.upper()}: Technical Detail"
            scene.narration = f"Examining the core mechanism of {t_clean} in action."
