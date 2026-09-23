"""
router.py
Content-Type Classifier and Production Specification Router.
Classifies educational topics into the 8 core domains and injects domain-specific
visual primitives, required actions, camera sequences, and prohibited metaphors.
"""

import re
from typing import Dict, Any, List
from .storyboard import ContentType, VisualType, ShotType


CATEGORY_RULES: Dict[str, Dict[str, Any]] = {
    ContentType.MATHEMATICAL_CONCEPT.value: {
        "presenter_required": True,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "coordinate axes and mathematical function curves or 3D surfaces",
            "active parameter points moving in coordinate space",
            "directional vectors, tangents, and gradient arrows",
            "mathematical LaTeX equations with synchronized term highlights",
            "contour elevation maps and numerical convergence readouts"
        ],
        "required_actions": [
            "instructor frames the optimization / mathematical problem",
            "plot initial parameter coordinates or input variables",
            "calculate rate of change, gradient vector, or functional transformation",
            "animate step-by-step parameter trajectory moving toward solution",
            "display formula and show convergence at target minimum or limit"
        ],
        "shot_sequence": [
            ShotType.MEDIUM_SHOT.value,
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_PRESENTER.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.AI_PRESENTER.value,
        ],
        "prohibited_metaphors": [
            "car or vehicle driving down roads or highways",
            "rollercoaster or ski slope",
            "random natural mountain landscapes or hiking trails",
            "rolling physical balls down real-world terrain",
            "fantasy portals or magical glowing orbs"
        ]
    },

    ContentType.CAD_TUTORIAL.value: {
        "presenter_required": True,
        "mathematical_visualization_required": False,
        "software_required": True,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "mechanical engineer sitting at dual-monitor CAD workstation",
            "CAD software interface (e.g. CATIA, SolidWorks, Fusion 360)",
            "specification feature tree, workbench toolbars, and action bar",
            "screen close-up of command search / power input tool",
            "mouse cursor interacting with software icons and dialogs",
            "3D mechanical CAD geometry rendering in active viewport"
        ],
        "required_actions": [
            "show engineer at workstation navigating 3D CAD model",
            "pan camera over engineer shoulder to monitor display",
            "move cursor to command search field or toolbar",
            "type keyword query and show live auto-complete filtering",
            "click selected command and execute feature on 3D geometry"
        ],
        "shot_sequence": [
            ShotType.WIDE_WORKSPACE.value,
            ShotType.OVER_THE_SHOULDER.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.VIEWPORT_SCREEN.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_WORKSTATION_VIDEO.value,
            VisualType.SOFTWARE_DEMONSTRATION.value,
            VisualType.SCREEN_CLOSEUP.value,
            VisualType.SOFTWARE_DEMONSTRATION.value,
            VisualType.AI_WORKSTATION_VIDEO.value,
        ],
        "prohibited_metaphors": [
            "futuristic floating holographic spaceships",
            "abstract magical wand tool metaphors",
            "corporate generic suits shaking hands",
            "unrelated spreadsheets or non-CAD software",
            "omitting the CAD user interface and menus"
        ]
    },

    ContentType.SOFTWARE_TUTORIAL.value: {
        "presenter_required": True,
        "mathematical_visualization_required": False,
        "software_required": True,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "software developer at modern multi-monitor coding workstation",
            "IDE code editor or command terminal with authentic syntax",
            "screen close-up of menu items, buttons, or conflict markers",
            "cursor clicks and active keyboard text input",
            "result output terminal, compiler status, or UI preview"
        ],
        "required_actions": [
            "developer introduces software task at computer terminal",
            "navigate to active application screen or code file",
            "demonstrate precise button clicks, key shortcuts, or commands",
            "observe software state update or error resolution",
            "verify success state in output window or terminal"
        ],
        "shot_sequence": [
            ShotType.WIDE_WORKSPACE.value,
            ShotType.OVER_THE_SHOULDER.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_WORKSTATION_VIDEO.value,
            VisualType.SOFTWARE_DEMONSTRATION.value,
            VisualType.SCREEN_CLOSEUP.value,
            VisualType.SOFTWARE_DEMONSTRATION.value,
            VisualType.AI_WORKSTATION_VIDEO.value,
        ],
        "prohibited_metaphors": [
            "boxing gloves or fighting animations for merge conflicts",
            "train wrecks or explosions for software bugs",
            "generic matrix digital rain",
            "abstract glowing cubes colliding in space",
            "avoiding the actual software interface"
        ]
    },

    ContentType.PROGRAMMING_TUTORIAL.value: {
        "presenter_required": True,
        "mathematical_visualization_required": False,
        "software_required": True,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "software engineer at development workstation",
            "IDE code editor showing syntax-highlighted source functions",
            "memory layout diagram (call stack, heap, pointers, registers)",
            "step-by-step debugger breakpoint highlighting executing line",
            "variable state changes and console terminal output"
        ],
        "required_actions": [
            "programmer writes or steps into algorithm in IDE",
            "push stack frame or allocate memory structure",
            "evaluate branching conditional logic or loop termination",
            "propagate return values and pop memory frames in order",
            "print final verified execution output in console"
        ],
        "shot_sequence": [
            ShotType.OVER_THE_SHOULDER.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_WORKSTATION_VIDEO.value,
            VisualType.SOFTWARE_DEMONSTRATION.value,
            VisualType.SCREEN_CLOSEUP.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.AI_WORKSTATION_VIDEO.value,
        ],
        "prohibited_metaphors": [
            "nesting Russian dolls instead of real memory stack frames",
            "hall of mirrors infinity visual effect",
            "bottomless pit or rabbit hole cartoons",
            "unrelated cartoon characters",
            "matrix green code falling without syntax or memory"
        ]
    },

    ContentType.TECHNICAL_CONCEPT.value: {
        "presenter_required": True,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "AI technical instructor or research scientist",
            "matrix numerical arrays, tensor layers, or architectural diagrams",
            "sliding operational windows (convolution kernels, pooling, attention maps)",
            "layer-by-layer feature transformations and activations",
            "output probability distributions or metrics"
        ],
        "required_actions": [
            "instructor frames the technical architecture or model",
            "pass input data through mathematical transformation block",
            "animate localized receptive field operation across input data",
            "aggregate multi-channel feature maps into compact representations",
            "output final decision or classification state"
        ],
        "shot_sequence": [
            ShotType.MEDIUM_SHOT.value,
            ShotType.MACRO_DETAIL.value,
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.SPLIT_SCREEN.value,
        ],
        "visual_types": [
            VisualType.AI_PRESENTER.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "glowing sci-fi human brains thinking",
            "cars driving through circuit boards",
            "abstract cosmic light beams",
            "random particle storms without data matrices",
            "static disconnected diagrams"
        ]
    },

    ContentType.AUTOMOTIVE_PROCESS.value: {
        "presenter_required": True,
        "mathematical_visualization_required": False,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "automotive engineer at vehicle test bench or dyno facility",
            "electronic control units (ECUs), wire harness, and vehicle powertrain",
            "multichannel oscilloscope displaying real differential voltage signals",
            "timing diagrams comparing bit streams and priority fields",
            "mechanical power delivery (gears, motor-generators, inverters)"
        ],
        "required_actions": [
            "engineer inspects vehicle system hardware or test fixture",
            "initiate physical operation (braking event, message transmission, gear mesh)",
            "trace electrical or mechanical transmission through components",
            "resolve conflict, arbitration, or kinetic energy conversion",
            "measure and display calibrated telemetry output"
        ],
        "shot_sequence": [
            ShotType.MEDIUM_ENGINEER.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.MACRO_DETAIL.value,
            ShotType.CLOSE_UP.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_WORKSTATION_VIDEO.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.AI_WORKSTATION_VIDEO.value,
        ],
        "prohibited_metaphors": [
            "highway traffic jams or police cars as network metaphors",
            "cartoon cars talking or smiling",
            "fantasy energy lightning strikes",
            "generic stock footage of cars on racetracks without mechanical detail",
            "skipping electrical and mechanical schematics"
        ]
    },

    ContentType.ENGINEERING_PROCESS.value: {
        "presenter_required": True,
        "mathematical_visualization_required": False,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "engineer in industrial laboratory, manufacturing plant, or cleanroom",
            "equipment hardware (CNC mill, battery modules, hydraulic valves, heat exchangers)",
            "CAD/CAM cross-sections and internal component cutaways",
            "instrumented measurement readouts (voltages, temperatures, pressures)",
            "physical process steps occurring in sequential order"
        ],
        "required_actions": [
            "engineer introduces industrial process at workstation or machine",
            "establish coordinate datum, initial state, or input parameters",
            "execute progressive mechanical or electrochemical transformation",
            "verify tolerances, clearances, or thermal balance during simulation",
            "inspect completed physical output conforming to specifications"
        ],
        "shot_sequence": [
            ShotType.WIDE_WORKSPACE.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_WORKSTATION_VIDEO.value,
            VisualType.SOFTWARE_DEMONSTRATION.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
            VisualType.AI_WORKSTATION_VIDEO.value,
        ],
        "prohibited_metaphors": [
            "action-movie explosions and uncontrolled sparks",
            "magical instant laser melting without physical tooling",
            "cartoon assembly line robots dancing",
            "generic hand tools like sledgehammers",
            "static non-interactive stock imagery"
        ]
    },

    ContentType.GENERAL_EDUCATIONAL.value: {
        "presenter_required": True,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "engineering instructor in modern laboratory or lecture studio",
            "system block diagram showing input, plant, feedback, and output",
            "real-time oscilloscope or telemetry curve tracking setpoint",
            "mathematical transfer functions or physical law formulas",
            "physical mechanism responding stably to control signals"
        ],
        "required_actions": [
            "instructor frames the core physical or control challenge",
            "introduce step disturbance or input stimulus",
            "calculate corrective signal across system components",
            "plot dynamic response curve showing rise time and damping",
            "demonstrate stable steady-state target acquisition"
        ],
        "shot_sequence": [
            ShotType.MEDIUM_SHOT.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.MEDIUM_SHOT.value,
        ],
        "visual_types": [
            VisualType.AI_WORKSTATION_VIDEO.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.AI_WORKSTATION_VIDEO.value,
        ],
        "prohibited_metaphors": [
            "car steering wheel in traffic as control metaphor",
            "household thermostat cartoons",
            "floating fantasy crystal balancing acts",
            "decorative fireworks or light shows",
            "abstract disconnected diagrams"
        ]
    }
}


class ContentTypeRouter:
    """Classifies user queries into the 8 educational categories and returns production constraints."""

    @classmethod
    def classify(cls, prompt: str) -> str:
        p = prompt.lower()

        # 1. CAD Tutorial
        if any(w in p for w in ["catia", "solidworks", "creo", "inventor", "autocad", "sketch in cad", "command finder", "cad tutorial", "extrude in cad", "assembly mates"]):
            return ContentType.CAD_TUTORIAL.value

        # 2. Mathematical Concept
        if any(w in p for w in ["gradient descent", "fourier transform", "eigenvalue", "calculus", "linear algebra", "derivative", "differential equation", "loss surface", "convex optimization", "matrix multiplication"]):
            return ContentType.MATHEMATICAL_CONCEPT.value

        # 3. Programming Tutorial
        if any(w in p for w in ["recursion", "call stack", "binary search", "linked list", "pointer", "memory allocation", "async await", "oop", "algorithm", "data structure", "python function"]):
            return ContentType.PROGRAMMING_TUTORIAL.value

        # 4. Software Tutorial
        if any(w in p for w in ["git", "merge conflict", "vs code", "github", "docker", "postman", "terminal", "debugger", "ide", "command line"]):
            return ContentType.SOFTWARE_TUTORIAL.value

        # 5. Technical Concept / Machine Learning
        if any(w in p for w in ["neural network", "cnn", "convolutional", "transformer", "backpropagation", "deep learning", "machine learning", "attention mechanism", "llm", "embedding"]):
            return ContentType.TECHNICAL_CONCEPT.value

        # 6. Automotive Process
        if any(w in p for w in ["can bus", "regenerative braking", "bldc motor", "electric differential", "powertrain", "ecu", "automotive", "gearbox", "transmission"]):
            return ContentType.AUTOMOTIVE_PROCESS.value

        # 7. Engineering Process / Manufacturing / EV
        if any(w in p for w in ["bms", "battery management", "cell balancing", "thermal runaway", "cnc", "milling", "injection molding", "pcb", "machining", "toolpath", "manufacturing"]):
            return ContentType.ENGINEERING_PROCESS.value

        # 8. General Educational (PID, Control Systems, Physics, etc.)
        if any(w in p for w in ["pid controller", "control system", "feedback loop", "thermodynamics", "heat exchanger", "fluid mechanics"]):
            return ContentType.GENERAL_EDUCATIONAL.value

        # Default fallback: General Educational
        return ContentType.GENERAL_EDUCATIONAL.value

    @classmethod
    def get_rules(cls, content_type: str) -> Dict[str, Any]:
        return CATEGORY_RULES.get(content_type, CATEGORY_RULES[ContentType.GENERAL_EDUCATIONAL.value])
