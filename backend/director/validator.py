"""
validator.py
Quality Control and Metaphor Validation Layer for Educational Video Storyboards.
Detects unconstrained metaphors, enforces universal technical visual types,
strictly rejects AI human presenters and avatars, and auto-corrects non-compliant scenes.
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
    ContentType.ALGORITHM.value: [
        r"\bdetective\b", r"\bmagnifying glass\b", r"\blibrary\b", r"\bbook\b",
        r"\bmagic wand\b", r"\brabbit hole\b", r"\brollercoaster\b"
    ],
    ContentType.MACHINE_LEARNING.value: [
        r"\bhuman brain thinking\b", r"\bcosmic beam\b", r"\bmagic\b", r"\bportal\b",
        r"\bcars driving\b", r"\bfireworks\b"
    ],
    ContentType.CONTROL_SYSTEM.value: [
        r"\bsteering wheel\b", r"\btraffic\b", r"\bthermostat\b", r"\btightrope\b",
        r"\bmagic crystal\b", r"\bfireworks\b"
    ],
    ContentType.AUTOMOTIVE_PROCESS.value: [
        r"\bpolice car\b", r"\btraffic jam\b", r"\btalking car\b", r"\blightning strike\b",
        r"\bboxing\b", r"\btrain crash\b"
    ],
    ContentType.CAD_TUTORIAL.value: [
        r"\bspaceship\b", r"\bportal\b", r"\bmagic wand\b", r"\bfantasy\b",
        r"\bsuit and tie\b", r"\bhandshake\b", r"\bspreadsheet\b", r"\bcalculator\b"
    ],
    ContentType.EV.value: [
        r"\bmagic lightning\b", r"\bgreen leaf\b", r"\bcartoon battery\b", r"\bhighway\b"
    ],
    ContentType.MANUFACTURING.value: [
        r"\bblacksmith\b", r"\banvil\b", r"\baction movie\b", r"\bfireworks\b",
        r"\blaser melting\b", r"\bdancing robot\b", r"\bsledgehammer\b"
    ],
    ContentType.PROGRAMMING_TUTORIAL.value: [
        r"\brussian doll\b", r"\bnesting doll\b", r"\bhall of mirrors\b", r"\bbottomless pit\b",
        r"\brabbit hole\b", r"\bmatrix rain\b"
    ],
    ContentType.SOFTWARE_TUTORIAL.value: [
        r"\bboxing glove\b", r"\bfight\b", r"\btrain crash\b", r"\bexplosion\b",
        r"\bcolliding cubes\b", r"\bmatrix rain\b"
    ],
    ContentType.GENERAL_EDUCATIONAL.value: [
        r"\bsteering wheel in traffic\b", r"\bthermostat knob\b", r"\bmagic crystal\b",
        r"\bfireworks\b"
    ],
}

AVATAR_PATTERNS = [
    r"\bpresenter\b", r"\binstructor\b", r"\bavatar\b", r"\bhost\b", r"\bhuman face\b",
    r"\bperson sitting\b", r"\bengineer sitting\b", r"\bwoman in\b", r"\bman in\b",
    r"\bfashion\b", r"\bportrait\b", r"\bclose-up face\b", r"\btalking head\b"
]


class QualityControlValidator:
    """Evaluates storyboards against technical educational rigor and auto-corrects non-compliant scenes."""

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

            # Check 2: Avatar / Human Presenter Prohibition
            avatar_flagged = False
            if any(w in scene.visual_type.lower() for w in ["presenter", "avatar", "workstation_video"]):
                avatar_flagged = True
            else:
                for ap in AVATAR_PATTERNS:
                    if re.search(ap, f"{scene.subject} {scene.action}".lower()):
                        avatar_flagged = True
                        break
            if avatar_flagged:
                msg = f"Scene {scene.scene_id}: FAIL - AI human presenter / avatar detected. Universal Technical Video Mode mandates 100% subject focus."
                warnings.append(msg)

            # Check 3: Action Presence (reject static prompts)
            static_flagged = False
            if len(scene.action.strip()) < 15 or any(w in scene.action.lower() for w in ["static image", "still photo", "decorative visual"]):
                msg = f"Scene {scene.scene_id}: FAIL - Insufficient physical/computational action described."
                warnings.append(msg)
                static_flagged = True

            # If failed, auto-correct the scene based on domain standards
            if metaphor_flagged or avatar_flagged or static_flagged:
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

        # 3. Visual type check - ensure no presenter types persist
        for idx, s in enumerate(storyboard.scenes):
            if not s.visual_type or any(w in s.visual_type.lower() for w in ["presenter", "avatar", "static"]):
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
        """Rewrites a rejected scene into an educationally correct technical scene without any avatars."""
        t_clean = topic.strip()
        t_lower = t_clean.lower()

        if "gradient" in t_lower or content_type == ContentType.MATHEMATICAL_CONCEPT.value:
            if scene_index == 0:
                scene.shot_type = ShotType.PERSPECTIVE_3D.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "3D Continuous Objective Loss Surface"
                scene.action = "Camera orbits a continuous convex paraboloid loss surface J(w1, w2) = 0.5*(w1^2 + 1.5*w2^2). Elevation contour rings project onto the base parameter plane."
                scene.animation = "Rotating 3D wireframe mesh with gradient contour rings."
                scene.technical_content = "Cost Function J(w1, w2) = 1/2(w1^2 + 1.5w2^2)."
                scene.on_screen_text = f"{t_clean.upper()}: Objective Space"
                scene.narration = f"To understand {t_clean}, we examine how model parameters navigate an objective error surface."
            elif scene_index == 1:
                scene.shot_type = ShotType.PERSPECTIVE_3D.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "Initial Parameter State and High Error Region"
                scene.action = "An initial parameter coordinate theta_0 = [2.40, 2.10]^T is plotted high on the loss slope with vertical dashed drop-lines to the parameter plane. Real-time HUD displays high loss."
                scene.animation = "Pulsing parameter coordinate theta_0; drop-lines connect to axes; HUD readout displays J(theta_0) = 4.88."
                scene.technical_content = "theta_0 = [2.40, 2.10]^T; J(theta_0) = 4.88."
                scene.on_screen_text = "INITIAL STATE: High Loss Coordinate theta_0"
                scene.narration = "Initial random parameters place the model high on the error surface with significant loss."
            elif scene_index == 2:
                scene.shot_type = ShotType.CLOSE_UP.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "Gradient Vector vs Negative Gradient Direction"
                scene.action = "A local tangent plane touches the surface at theta_0. An amber arrow displays the gradient vector pointing uphill, while a bold cyan arrow points downhill in the negative gradient direction."
                scene.animation = "Uphill gradient vector nabla J fades; cyan negative gradient vector -nabla J highlights the descent trajectory."
                scene.technical_content = "nabla J(theta) = [dJ/dw1, dJ/dw2]^T; Step: -alpha * nabla J."
                scene.on_screen_text = "STEEPEST DESCENT: Stepping in Direction -nabla J"
                scene.narration = "The gradient calculates steepest ascent; stepping in the negative gradient direction guarantees decreasing loss."
            elif scene_index == 3:
                scene.shot_type = ShotType.PERSPECTIVE_3D.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "Iterative Parameter Updates and Trajectory"
                scene.action = "The parameter point takes sequential discrete downhill steps along the surface. Consecutive update vectors connect theta_0 through theta_5, leaving a glowing descent trajectory."
                scene.animation = "Step-by-step parameter progression down contour lines; live HUD loss counter decreases."
                scene.technical_content = "theta_{t+1} = theta_t - alpha * nabla J(theta_t); alpha = 0.16."
                scene.on_screen_text = "UPDATE RULE: theta_{t+1} = theta_t - alpha * nabla J"
                scene.narration = "Scaled by learning rate alpha, repeated iterations move parameters steadily down the slope."
            else:
                scene.shot_type = ShotType.PERSPECTIVE_3D.value
                scene.visual_type = VisualType.MATHEMATICAL_ANIMATION.value
                scene.subject = "Convergence at Global Minimum Basin"
                scene.action = "Camera zooms into the lowest basin point (0, 0). The parameter point settles at the minimum; concentric target rings pulse green as gradient magnitude shrinks to zero."
                scene.animation = "Concentric glowing rings pulse at global minimum; gradient arrow shrinks to zero; loss flatlines."
                scene.technical_content = "theta* = [0.0, 0.0]^T, ||nabla J|| = 0.00."
                scene.on_screen_text = "GLOBAL MINIMUM: Convergence Achieved"
                scene.narration = "At the basin, the gradient diminishes to zero, yielding the optimal model weights."

        elif "binary search" in t_lower or content_type == ContentType.ALGORITHM.value:
            if scene_index == 0:
                scene.shot_type = ShotType.TECHNICAL_SCHEMATIC.value
                scene.visual_type = VisualType.ALGORITHM_VISUALIZATION.value
                scene.subject = "Sorted Array and Target Query"
                scene.action = "A horizontal sequence of sorted integer boxes appears with indices 0 through 8. Pointers 'low' at index 0 and 'high' at index 8 frame the search space for target 42."
                scene.animation = "Array boxes slide in; pointer badges highlight low=0 and high=8."
                scene.technical_content = "Array: [3, 9, 14, 21, 28, 35, 42, 57, 68]; Target: 42."
                scene.on_screen_text = "INITIAL INTERVAL: low = 0, high = 8"
                scene.narration = "Binary search operates on sorted arrays by repeatedly halving the search interval."
            elif scene_index == 1:
                scene.shot_type = ShotType.CLOSE_UP.value
                scene.visual_type = VisualType.ALGORITHM_VISUALIZATION.value
                scene.subject = "Midpoint Calculation and Comparison"
                scene.action = "Midpoint pointer 'mid = 4' highlights value 28 in yellow. A comparison operator tests whether 28 equals 42."
                scene.animation = "Midpoint pointer flashes; comparison badge evaluates '28 < 42'."
                scene.technical_content = "mid = (0 + 8) // 2 = 4; array[4] = 28 < 42."
                scene.on_screen_text = "MIDPOINT COMPARISON: array[mid] < target"
                scene.narration = "Calculating the midpoint reveals that twenty-eight is less than our target of forty-two."
            elif scene_index == 2:
                scene.shot_type = ShotType.SPLIT_SCREEN.value
                scene.visual_type = VisualType.ALGORITHM_VISUALIZATION.value
                scene.subject = "Partition Elimination and Boundary Shift"
                scene.action = "Indices 0 through 4 turn translucent gray and are discarded. Pointer 'low' jumps to index 5 (mid + 1)."
                scene.animation = "Left partition fades out; 'low' pointer slides to index 5."
                scene.technical_content = "low = mid + 1 = 5; active search space: [35, 42, 57, 68]."
                scene.on_screen_text = "HALVING SEARCH SPACE: low = mid + 1"
                scene.narration = "Because the array is sorted, all elements at and below the midpoint are safely eliminated."
            elif scene_index == 3:
                scene.shot_type = ShotType.CLOSE_UP.value
                scene.visual_type = VisualType.ALGORITHM_VISUALIZATION.value
                scene.subject = "Second Iteration and Target Hit"
                scene.action = "New midpoint mid = (5 + 8) // 2 = 6 highlights value 42. The element turns glowing emerald green as a match is confirmed."
                scene.animation = "Mid pointer highlights index 6; box pulses green with checkmark."
                scene.technical_content = "mid = (5 + 8) // 2 = 6; array[6] == 42."
                scene.on_screen_text = "TARGET LOCATED: Match Confirmed at Index 6"
                scene.narration = "The next midpoint directly inspects index six, finding forty-two in just two comparisons."
            else:
                scene.shot_type = ShotType.TECHNICAL_SCHEMATIC.value
                scene.visual_type = VisualType.ALGORITHM_VISUALIZATION.value
                scene.subject = "Logarithmic Time Complexity Summary"
                scene.action = "A step-reduction tree and O(log N) complexity curve show why binary search completes in logarithmic time."
                scene.animation = "Array size splits in half each step: N -> N/2 -> N/4 -> 1."
                scene.technical_content = "Time Complexity: O(log2 N); Comparisons: <= ceil(log2 N)."
                scene.on_screen_text = "COMPLEXITY: O(log N) Time Efficiency"
                scene.narration = "By dividing the search space in half at each step, binary search achieves logarithmic efficiency."

        elif "catia" in t_lower or "cad" in t_lower or content_type == ContentType.CAD_TUTORIAL.value:
            if scene_index == 0:
                scene.shot_type = ShotType.VIEWPORT_SCREEN.value
                scene.visual_type = VisualType.CAD_3D_VISUALIZATION.value
                scene.subject = "CAD 3D Modeling Interface and Part Viewport"
                scene.action = "Full-screen CAD workstation interface displaying active 3D mechanical part geometry, specification tree on left, and 3D compass on top-right."
                scene.animation = "3D solid rotates smoothly in viewport showing profile sketch."
                scene.technical_content = "Parametric 3D CAD environment and PartBody tree."
                scene.on_screen_text = f"{t_clean.upper()}: Accelerated Workflow"
                scene.narration = f"When modeling complex parts in CAD, navigating nested toolbars can slow down your design workflow."
            elif scene_index == 1:
                scene.shot_type = ShotType.SCREEN_CLOSEUP.value
                scene.visual_type = VisualType.SOFTWARE_INTERFACE_SIMULATION.value
                scene.subject = "Command Finder in Bottom Status Bar"
                scene.action = "Screen close-up of the bottom action bar. The mouse cursor glides smoothly toward the Command Finder input field."
                scene.animation = "Cursor moves with realistic acceleration and clicks into search input."
                scene.technical_content = "Command Finder / Power Input box."
                scene.on_screen_text = "COMMAND FINDER: Direct Tool Search"
                scene.narration = "Instead of hunting through menus, use the Command Finder in the bottom status bar to locate any feature."
            elif scene_index == 2:
                scene.shot_type = ShotType.SCREEN_CLOSEUP.value
                scene.visual_type = VisualType.SOFTWARE_INTERFACE_SIMULATION.value
                scene.subject = "Dynamic Query Entry and Tool Auto-Complete"
                scene.action = "The search query 'c:Pad' is typed. An auto-complete dropdown filters matching commands across all workbenches simultaneously."
                scene.animation = "Keystrokes appear; matching Pad tool row highlights in blue."
                scene.technical_content = "Search syntax: c:Pad; workbench breadcrumb: Part Design."
                scene.on_screen_text = "INSTANT FILTERING: Multi-Workbench Lookup"
                scene.narration = "Typing the command name or prefix instantly filters tools across all workbenches simultaneously."
            elif scene_index == 3:
                scene.shot_type = ShotType.VIEWPORT_SCREEN.value
                scene.visual_type = VisualType.CAD_3D_VISUALIZATION.value
                scene.subject = "Feature Definition Dialog and 3D Extrusion"
                scene.action = "Clicking the result activates the feature. The Pad Definition dialog opens in the viewport and generates a 3D extrusion preview on the 2D sketch."
                scene.animation = "Pad dialog opens; 2D profile extrudes into 3D solid with orange preview outline."
                scene.technical_content = "Pad Definition: Length = 25mm, Profile = Sketch.1."
                scene.on_screen_text = "ONE-CLICK EXECUTION: Feature Activated"
                scene.narration = "Clicking the command opens its definition dialog and applies the geometric modification directly to your model."
            else:
                scene.shot_type = ShotType.VIEWPORT_SCREEN.value
                scene.visual_type = VisualType.CAD_3D_VISUALIZATION.value
                scene.subject = "Completed Parametric Solid in Geometry Tree"
                scene.action = "The extrusion is confirmed; the completed solid turns shaded green and registers in the specification tree as a parametric feature."
                scene.animation = "Solid renders in metallic shading; feature tree updates with Pad.1."
                scene.technical_content = "Parametric tree: PartBody -> Pad.1 (25mm)."
                scene.on_screen_text = "WORKFLOW COMPLETE: Rapid Feature Creation"
                scene.narration = "Mastering the Command Finder eliminates toolbar searching and maximizes modeling productivity."

        else:
            # Universal Procedural Fallback
            rec_shots = rules.get("shot_sequence", [ShotType.TECHNICAL_SCHEMATIC.value])
            rec_vtypes = rules.get("visual_types", [VisualType.TECHNICAL_3D_ANIMATION.value])
            scene.shot_type = rec_shots[scene_index % len(rec_shots)]
            scene.visual_type = rec_vtypes[scene_index % len(rec_vtypes)]
            scene.subject = f"{t_clean} - Operational Stage {scene_index + 1}"
            scene.action = f"Technical visualization demonstrating active mechanism, signal flow, and calibrated parameters of {t_clean}."
            scene.animation = f"Dynamic movement and state transitions illustrating physical operation of {t_clean}."
            scene.technical_content = f"Calibrated operational telemetry for {t_clean}."
            scene.on_screen_text = f"{t_clean.upper()}: Technical Analysis"
            scene.narration = f"Observing the core operational behavior and dynamic state transitions of {t_clean}."
