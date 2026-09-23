"""
router.py
Universal Technical Video Mode Router and Classifier.
Classifies educational and engineering topics into specialized technical domains
and injects domain-specific visual primitives, required actions, camera sequences,
and prohibited metaphors. Strictly bans AI human presenters and avatars across all domains.
"""

import re
from typing import Dict, Any, List
from .storyboard import ContentType, VisualType, ShotType


CATEGORY_RULES: Dict[str, Dict[str, Any]] = {
    ContentType.MATHEMATICAL_CONCEPT.value: {
        "presenter_required": False,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "coordinate axes and mathematical function curves or 3D surfaces",
            "active parameter points moving in coordinate space with projection drop-lines",
            "directional vectors, local tangent planes, and gradient arrows (nabla J)",
            "mathematical LaTeX equations with synchronized term highlights and live HUD",
            "contour elevation maps and numerical convergence readouts"
        ],
        "required_actions": [
            "plot continuous 3D/2D objective error surface or mathematical curve",
            "place initial parameter coordinate with coordinate droplines",
            "calculate rate of change, gradient vector, or functional transformation",
            "animate step-by-step parameter trajectory moving toward solution",
            "display formula and show convergence at target minimum or limit"
        ],
        "shot_sequence": [
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.PERSPECTIVE_3D.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.PERSPECTIVE_3D.value,
        ],
        "visual_types": [
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "car or vehicle driving down roads or highways",
            "rollercoaster or ski slope",
            "random natural mountain landscapes or hiking trails",
            "rolling physical balls down real-world terrain"
        ]
    },

    ContentType.ALGORITHM.value: {
        "presenter_required": False,
        "mathematical_visualization_required": False,
        "software_required": True,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "sequential array memory cells with integer index labels",
            "colored pointer markers (e.g. low, mid, high) tracking algorithm state",
            "highlighted comparison values and conditional evaluation badges",
            "grayed-out eliminated search partitions or sorted sub-lists",
            "target match confirmation ring with step counter HUD"
        ],
        "required_actions": [
            "render full sorted array with initial boundaries and target query",
            "compute midpoint index (mid = (low + high) // 2) and highlight comparison",
            "evaluate comparison and discard irrelevant half with visual fade",
            "re-position boundary pointers to remaining active interval",
            "settle on exact target index with green success badge"
        ],
        "shot_sequence": [
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.CLOSE_UP.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.CLOSE_UP.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
        ],
        "visual_types": [
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "detective looking through magnifying glass",
            "physical library book searching",
            "magic sorting wands or hats",
            "static code screenshots without animated pointer execution"
        ]
    },

    ContentType.MACHINE_LEARNING.value: {
        "presenter_required": False,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "multi-layer neural network architecture (Input, Hidden, Output nodes)",
            "interconnecting synaptic lines weighted by thickness and color",
            "forward propagating electrical pulse wavefronts across layers",
            "mathematical node activation formula (sigma(Wx+b)) with live telemetry",
            "backward error flow and loss gradient weight updates"
        ],
        "required_actions": [
            "display deep neural network graph topology with labeled layers",
            "feed input feature vector and propagate activations forward through weights",
            "calculate non-linear activation function at hidden layer neurons",
            "generate output prediction and compute loss with respect to ground truth",
            "backpropagate error gradients and adjust synaptic connection weights"
        ],
        "shot_sequence": [
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.PERSPECTIVE_3D.value,
        ],
        "visual_types": [
            VisualType.NEURAL_NETWORK_ANIMATION.value,
            VisualType.NEURAL_NETWORK_ANIMATION.value,
            VisualType.NEURAL_NETWORK_ANIMATION.value,
            VisualType.NEURAL_NETWORK_ANIMATION.value,
            VisualType.NEURAL_NETWORK_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "glowing sci-fi human brains thinking",
            "cosmic laser particle storms",
            "circuits turning into biological neurons",
            "disconnected abstract cubes"
        ]
    },

    ContentType.CONTROL_SYSTEM.value: {
        "presenter_required": False,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "closed-loop block diagram (Setpoint, Summing Junction, PID, Plant, Feedback)",
            "real-time oscilloscope step response curve tracking target setpoint",
            "error signal curve e(t) = r(t) - y(t) with shaded deficit area",
            "proportional (Kp*e), integral (Ki*int e), and derivative (Kd*de/dt) vector telemetry",
            "damped harmonic response curve settling cleanly at steady state"
        ],
        "required_actions": [
            "introduce step setpoint input and observe instantaneous error signal",
            "demonstrate aggressive proportional response driving the actuator",
            "show integral term eliminating steady-state offset over time",
            "show derivative term damping rate of change to prevent overshoot",
            "stabilize system output on setpoint line with minimal settling time"
        ],
        "shot_sequence": [
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
        ],
        "visual_types": [
            VisualType.CONTROL_SYSTEM_ANIMATION.value,
            VisualType.CONTROL_SYSTEM_ANIMATION.value,
            VisualType.CONTROL_SYSTEM_ANIMATION.value,
            VisualType.CONTROL_SYSTEM_ANIMATION.value,
            VisualType.CONTROL_SYSTEM_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "car steering wheel in traffic",
            "household thermostat cartoons",
            "tightrope walker balancing",
            "static disconnected diagrams"
        ]
    },

    ContentType.AUTOMOTIVE_PROCESS.value: {
        "presenter_required": False,
        "mathematical_visualization_required": False,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "CAN Bus dual-wire differential topology (CAN_H, CAN_L) with multiple nodes",
            "synchronized digital logic voltage waveforms (Dominant 0 vs Recessive 1)",
            "bit-by-bit message identifier comparison during arbitration phase",
            "losing node backing off to listen state upon recessive bit detection",
            "winning highest-priority frame broadcasting payload across bus"
        ],
        "required_actions": [
            "illustrate multiple ECUs (Brakes, Engine, Transmission) sharing physical bus",
            "initiate simultaneous message broadcast creating bus contention",
            "compare identifier bits synchronously at bit-level resolution",
            "demonstrate wired-AND behavior where dominant '0' overwrites recessive '1'",
            "show losing node cease transmission while winning node takes complete bus"
        ],
        "shot_sequence": [
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.CLOSE_UP.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
        ],
        "visual_types": [
            VisualType.NETWORK_PROTOCOL_ANIMATION.value,
            VisualType.NETWORK_PROTOCOL_ANIMATION.value,
            VisualType.NETWORK_PROTOCOL_ANIMATION.value,
            VisualType.NETWORK_PROTOCOL_ANIMATION.value,
            VisualType.NETWORK_PROTOCOL_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "traffic intersection with police directing cars",
            "train station switching tracks",
            "boxing fight between data packets",
            "cartoon characters talking"
        ]
    },

    ContentType.CAD_TUTORIAL.value: {
        "presenter_required": False,
        "mathematical_visualization_required": False,
        "software_required": True,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "high-definition 3D CAD interface (specification tree, 3D compass, toolbar)",
            "smooth animated mouse cursor gliding to command tools or search field",
            "Command Finder search bar typing 'c:Pad' with dynamic auto-complete popup",
            "parametric feature definition dialog with editable parameter spinboxes",
            "3D viewport mechanical geometry updating from sketch to extruded solid"
        ],
        "required_actions": [
            "display CAD interface layout and active 3D part geometry in viewport",
            "glide mouse cursor smoothly to Command Finder in bottom action bar",
            "type command query and filter matching tools across workbenches in real time",
            "click matching command and open feature definition dialog window",
            "execute feature and render 3D parametric solid in viewport"
        ],
        "shot_sequence": [
            ShotType.VIEWPORT_SCREEN.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.SCREEN_CLOSEUP.value,
            ShotType.VIEWPORT_SCREEN.value,
            ShotType.VIEWPORT_SCREEN.value,
        ],
        "visual_types": [
            VisualType.CAD_3D_VISUALIZATION.value,
            VisualType.SOFTWARE_INTERFACE_SIMULATION.value,
            VisualType.SOFTWARE_INTERFACE_SIMULATION.value,
            VisualType.CAD_3D_VISUALIZATION.value,
            VisualType.CAD_3D_VISUALIZATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "floating holographic spaceships",
            "magic wand tools",
            "corporate generic handshakes",
            "omitting the actual software interface"
        ]
    },

    ContentType.EV.value: {
        "presenter_required": False,
        "mathematical_visualization_required": False,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "EV powertrain schematic (Battery Pack, Inverter, Traction Motor, Wheels)",
            "bi-directional energy flux arrows (Acceleration forward vs Braking reverse)",
            "battery pack internal cell matrix with thermal gradient heatmap",
            "real-time BMS telemetry HUD (State of Charge %, Voltage, Cell Temp, Current kW)",
            "kinetic-to-electrical energy conversion with regenerative efficiency gauge"
        ],
        "required_actions": [
            "display EV powertrain layout and high-voltage electrical architecture",
            "initiate vehicle deceleration triggering generator mode in traction motor",
            "invert 3-phase AC voltage to DC charge current through power inverter",
            "monitor battery cell voltage balancing and thermal distribution across pack",
            "store recovered energy in battery pack with state-of-charge readout"
        ],
        "shot_sequence": [
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.PERSPECTIVE_3D.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.CLOSE_UP.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
        ],
        "visual_types": [
            VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
            VisualType.BATTERY_SYSTEM_ANIMATION.value,
            VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
            VisualType.BATTERY_SYSTEM_ANIMATION.value,
            VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "car driving down random scenic highway",
            "cartoon battery with smiling face",
            "magic lightning bolts",
            "abstract green eco leaves"
        ]
    },

    ContentType.MANUFACTURING.value: {
        "presenter_required": False,
        "mathematical_visualization_required": False,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "raw stock material block clamped in precision machining fixture",
            "rotating CNC end mill tool with multi-axis trajectory vectors",
            "high-speed chip evacuation and progressive pocket milling cutaway",
            "feed rate, spindle speed (RPM), and depth of cut telemetry readout",
            "finished precision aerospace bracket with dimensional inspection tolerance lines"
        ],
        "required_actions": [
            "display raw billet stock material and toolpath coordinate reference",
            "engage rotating milling cutter along programmed G-code path",
            "perform progressive material removal across roughing and finishing passes",
            "mill interior pockets and complex contours with coolant spray",
            "reveal final machined component meeting exact geometric tolerances"
        ],
        "shot_sequence": [
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.PERSPECTIVE_3D.value,
            ShotType.CLOSE_UP.value,
            ShotType.PERSPECTIVE_3D.value,
        ],
        "visual_types": [
            VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
            VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
            VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
            VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
            VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "cartoon blacksmith hammering an anvil",
            "action-movie explosions",
            "magical instant laser melting without physical tooling",
            "static non-interactive stock photos"
        ]
    },

    ContentType.PROGRAMMING_TUTORIAL.value: {
        "presenter_required": False,
        "mathematical_visualization_required": False,
        "software_required": True,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "IDE syntax-highlighted function definition with active line execution cursor",
            "memory layout diagram (Call Stack frames, Heap allocation, pointers)",
            "recursive branching tree with parameter state badges (e.g. n=4, n=3, n=2)",
            "base case condition highlight terminating recursive calls",
            "stack frame popping with return value bubbling up call tree"
        ],
        "required_actions": [
            "display source function in IDE and enter initial invocation",
            "push new stack frame with local parameters onto call stack",
            "evaluate branching base condition vs recursive invocation step",
            "reach base condition and trigger return sequence",
            "pop stack frames in reverse order, accumulating return value to final result"
        ],
        "shot_sequence": [
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.CLOSE_UP.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
        ],
        "visual_types": [
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
            VisualType.ALGORITHM_VISUALIZATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "Russian nesting dolls instead of call stack frames",
            "hall of mirrors infinity visual effect",
            "rabbit hole cartoons",
            "matrix green code falling without syntax"
        ]
    },

    ContentType.GENERAL_EDUCATIONAL.value: {
        "presenter_required": False,
        "mathematical_visualization_required": True,
        "software_required": False,
        "technical_visualization_required": True,
        "required_visual_primitives": [
            "system architectural block diagram with active directional signal paths",
            "mathematical transfer functions or physical law formulas",
            "dynamic oscilloscope curve or telemetry HUD tracking system response",
            "animated state machine or operational parameter gauge",
            "steady-state system output visualization"
        ],
        "required_actions": [
            "introduce system topology and fundamental operating parameters",
            "apply input stimulus, disturbance, or force to system input",
            "animate dynamic state transition and signal flow across components",
            "plot time-domain response curve showing settling behavior",
            "demonstrate stable steady-state target achievement"
        ],
        "shot_sequence": [
            ShotType.TECHNICAL_SCHEMATIC.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.SPLIT_SCREEN.value,
            ShotType.SCOPE_VIEW.value,
            ShotType.TECHNICAL_SCHEMATIC.value,
        ],
        "visual_types": [
            VisualType.TECHNICAL_3D_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
            VisualType.MATHEMATICAL_ANIMATION.value,
            VisualType.TECHNICAL_3D_ANIMATION.value,
        ],
        "prohibited_metaphors": [
            "AI avatars, human presenters, people sitting at desks",
            "car driving down roads",
            "floating fantasy crystal balancing acts",
            "decorative fireworks or light shows",
            "abstract disconnected diagrams"
        ]
    }
}


class ContentTypeRouter:
    """Classifies user queries into the appropriate educational category and returns production constraints."""

    @classmethod
    def classify(cls, prompt: str) -> str:
        p = prompt.lower()

        # 1. CAD Tutorial
        if any(w in p for w in ["catia", "solidworks", "creo", "inventor", "autocad", "command finder", "cad tutorial", "extrude in cad", "assembly mates"]):
            return ContentType.CAD_TUTORIAL.value

        # 2. Mathematical Concept
        if any(w in p for w in ["gradient descent", "fourier transform", "eigenvalue", "calculus", "linear algebra", "derivative", "differential equation", "loss surface", "convex optimization", "matrix multiplication"]):
            return ContentType.MATHEMATICAL_CONCEPT.value

        # 3. Algorithms & Data Structures
        if any(w in p for w in ["binary search", "sorting", "merge sort", "quick sort", "tree traversal", "dijkstra", "breadth first", "depth first", "hash table", "stack and queue"]):
            return ContentType.ALGORITHM.value

        # 4. Machine Learning & Deep Learning
        if any(w in p for w in ["neural network", "cnn", "convolutional", "transformer", "backpropagation", "deep learning", "machine learning", "attention mechanism", "activation function"]):
            return ContentType.MACHINE_LEARNING.value

        # 5. Control Systems & Feedback
        if any(w in p for w in ["pid", "pid control", "pid controller", "closed-loop", "feedback loop", "transfer function", "bode plot", "state space", "stability"]):
            return ContentType.CONTROL_SYSTEM.value

        # 6. Automotive & Networking Protocols
        if any(w in p for w in ["can bus", "can arbitration", "ecu communication", "automotive network", "differential signaling"]):
            return ContentType.AUTOMOTIVE_PROCESS.value

        # 7. Electric Vehicles & Energy Systems
        if any(w in p for w in ["regenerative braking", "bms", "battery management", "ev battery", "cell balancing", "electric vehicle", "inverter", "traction motor"]):
            return ContentType.EV.value

        # 8. Manufacturing & Machining
        if any(w in p for w in ["manufacturing process", "cnc", "milling", "injection molding", "machining", "toolpath", "lathe", "subtractive manufacturing"]):
            return ContentType.MANUFACTURING.value

        # 9. Programming & Computer Science
        if any(w in p for w in ["recursion", "call stack", "pointer", "memory allocation", "async await", "oop", "python function", "programming concept", "garbage collection"]):
            return ContentType.PROGRAMMING_TUTORIAL.value

        # 10. Software Tutorial & Tools
        if any(w in p for w in ["git", "merge conflict", "vs code", "github", "docker", "postman", "terminal", "debugger", "ide"]):
            return ContentType.SOFTWARE_TUTORIAL.value

        # Default fallback: General Educational
        return ContentType.GENERAL_EDUCATIONAL.value

    @classmethod
    def get_rules(cls, content_type: str) -> Dict[str, Any]:
        return CATEGORY_RULES.get(content_type, CATEGORY_RULES[ContentType.GENERAL_EDUCATIONAL.value])
