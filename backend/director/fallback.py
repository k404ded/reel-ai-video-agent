"""
fallback.py
Deterministic Universal Technical Video Planner.
Produces authentic 5-scene technical educational storyboards across all technical domains
with meaningful animations, dynamic calculations, zero AI presenters, and zero avatars.
"""

import re
from typing import List
from .storyboard import EducationalStoryboard, StoryboardScene, ContentType, VisualType, ShotType
from .router import ContentTypeRouter


_STOPWORDS = [
    "create", "make", "generate", "a", "an", "the", "short", "cinematic",
    "educational", "video", "of", "explaining", "explain", "how", "works",
    "work", "please", "can", "you", "to", "in", "seconds", "10-second"
]


def extract_topic(prompt: str) -> str:
    p = prompt.strip()
    p = re.sub(r"(?i)\bin\s+\d+[- ]?seconds?\b", " ", p)
    p = re.sub(r"(?i)\b\d+[- ]?seconds?\b", " ", p)
    stop_pattern = r"(?i)\b(" + "|".join(_STOPWORDS) + r")\b"
    p = re.sub(stop_pattern, " ", p)
    p = re.sub(r"\s+", " ", p).strip(" .")
    return p.title() if p else prompt.strip(" .").title()


class SpecializedFallbackPlanner:
    """Generates structured educational storyboards for all universal technical categories without external API dependencies."""

    @classmethod
    def plan(cls, user_prompt: str) -> EducationalStoryboard:
        content_type = ContentTypeRouter.classify(user_prompt)
        rules = ContentTypeRouter.get_rules(content_type)
        topic = extract_topic(user_prompt)
        t_lower = topic.lower()

        scenes: List[StoryboardScene] = []

        # =========================================================================
        # 1. MATHEMATICAL / OPTIMIZATION (Gradient Descent, Calculus, Vectors)
        # =========================================================================
        if "gradient" in t_lower or content_type == ContentType.MATHEMATICAL_CONCEPT.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.MATHEMATICAL_ANIMATION.value,
                    subject="3D Continuous Objective Loss Surface",
                    action="Camera orbits a continuous convex paraboloid loss surface J(w1, w2) = 0.5*(w1^2 + 1.5*w2^2). Elevation contour rings project onto the base parameter plane.",
                    environment="Deep dark-slate mathematical coordinate canvas with glowing viridis surface mesh and cyan contour rings.",
                    camera="Smooth orbital pan around 3D surface tilting down toward coordinate axes.",
                    animation="Elevation contours illuminate as camera orbits the convex geometry.",
                    technical_content="J(w1, w2) = 0.5 * (w1^2 + 1.5 * w2^2).",
                    on_screen_text=f"{topic.upper()}: Continuous Cost Surface",
                    narration="To visualize the optimization, model parameters are mapped onto a continuous multidimensional error surface.",
                    transition="cut_to_coordinate",
                    generation_requirements=["3D surface mesh", "contour slices"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=3.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.MATHEMATICAL_ANIMATION.value,
                    subject="Initial Parameter Coordinate theta_0",
                    action="An initial parameter coordinate theta_0 = [2.40, 2.10]^T appears high on the error slope with vertical dashed drop-lines to parameter axes.",
                    environment="Precision mathematical coordinate canvas.",
                    camera="Slow push-in toward initial coordinate point.",
                    animation="Parameter point pulses in green; dashed drop-lines fall to (w1, w2) plane; HUD displays high loss J = 4.88.",
                    technical_content="theta_0 = [2.40, 2.10]^T; J(theta_0) = 4.88.",
                    on_screen_text="INITIAL STATE: High Error Region (theta_0)",
                    narration="Initial weights place the model high on the slope with high prediction error.",
                    transition="cut_to_gradient",
                    generation_requirements=["pulsing coordinate", "drop-lines", "HUD telemetry"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.0,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.MATHEMATICAL_ANIMATION.value,
                    subject="Gradient Vector and Negative Descent Direction",
                    action="A local tangent plane forms at theta_0. An amber arrow displays the gradient vector pointing uphill, while a bold cyan arrow points downhill in the negative gradient direction.",
                    environment="Mathematical coordinate space with local tangent plane.",
                    camera="35-degree close-up inspection of local slope vectors.",
                    animation="Amber gradient vector nabla J extends uphill; cyan vector -nabla J indicates descent step.",
                    technical_content="nabla J(theta) = [dJ/dw1, dJ/dw2]^T; Step: -alpha * nabla J.",
                    on_screen_text="STEEPEST DESCENT: Stepping in Direction -nabla J",
                    narration="The gradient points in the direction of steepest ascent; stepping in the negative gradient direction guarantees decreasing error.",
                    transition="cut_to_iteration",
                    generation_requirements=["tangent plane", "dual vector arrows"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.MATHEMATICAL_ANIMATION.value,
                    subject="Iterative Parameter Updates and Trajectory",
                    action="The parameter point takes sequential discrete downhill steps along the surface. Consecutive update vectors connect theta_0 through theta_5, leaving a glowing descent trajectory.",
                    environment="Full 3D surface view with illuminated trajectory.",
                    camera="Tracking shot following the parameter coordinate descending the slope.",
                    animation="Discrete steps animate sequentially; live loss readout counter drops from 4.88 down toward zero.",
                    technical_content="theta_{t+1} = theta_t - alpha * nabla J(theta_t); alpha = 0.16.",
                    on_screen_text="UPDATE RULE: theta_{t+1} = theta_t - alpha * nabla J",
                    narration="Scaled by learning rate alpha, repeated iterations move the parameters steadily down the contour valley.",
                    transition="cut_to_convergence",
                    generation_requirements=["trajectory path", "live HUD counter", "formula display"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.MATHEMATICAL_ANIMATION.value,
                    subject="Convergence at Global Minimum Basin",
                    action="Camera zooms into the lowest basin point (0, 0). The parameter point settles at the minimum; concentric target rings pulse green as gradient magnitude shrinks to zero.",
                    environment="Basin floor of convex loss surface.",
                    camera="Overhead isometric focus on converged global minimum.",
                    animation="Gradient arrow contracts to zero length; concentric target rings pulse in emerald green.",
                    technical_content="theta* = [0.00, 0.00]^T; ||nabla J(theta*)|| approx 0; Loss = 0.000.",
                    on_screen_text="GLOBAL MINIMUM: Convergence Achieved",
                    narration="At the global minimum, the gradient approaches zero, yielding optimal trained model weights.",
                    transition="fade_out",
                    generation_requirements=["pulsing convergence rings", "zero gradient indicator"]
                )
            ]

        # =========================================================================
        # 2. ALGORITHMS & DATA STRUCTURES (Binary Search, Sorting, Trees)
        # =========================================================================
        elif "binary search" in t_lower or content_type == ContentType.ALGORITHM.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Sorted Array Initialization and Pointers",
                    action="A horizontal sequence of 9 sorted memory cells [3, 9, 14, 21, 28, 35, 42, 57, 68] appears with index labels 0 to 8. Pointers 'low=0' and 'high=8' frame target query 42.",
                    environment="Clean dark slate computer science diagram with cyan cell borders.",
                    camera="Static wide framing on full array with pointer callouts.",
                    animation="Array cells slide in; pointer badges highlight low=0 and high=8; search target 42 displays in HUD.",
                    technical_content="Array: [3, 9, 14, 21, 28, 35, 42, 57, 68]; Target: 42; low=0, high=8.",
                    on_screen_text="INITIAL SEARCH BOUNDS: low = 0, high = 8",
                    narration="Binary search operates on sorted data by repeatedly dividing the search space in half.",
                    transition="cut_to_mid",
                    generation_requirements=["array cells", "index numbers", "low/high pointers"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=3.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Midpoint Calculation and Comparison",
                    action="Midpoint index mid = (0 + 8) // 2 = 4 highlights value 28 in yellow. A comparison operator tests whether 28 equals 42.",
                    environment="High-contrast algorithmic visualization canvas.",
                    camera="Zoom into central midpoint index 4.",
                    animation="Midpoint arrow drops onto cell 4; comparison equation evaluates '28 < 42' with amber warning.",
                    technical_content="mid = (0 + 8) // 2 = 4; array[mid] = 28; 28 < 42.",
                    on_screen_text="MIDPOINT TEST: array[4] = 28 < 42",
                    narration="Calculating the midpoint reveals that value twenty-eight is less than our target of forty-two.",
                    transition="cut_to_eliminate",
                    generation_requirements=["midpoint pointer", "comparison operator", "equation highlight"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.0,
                    shot_type=ShotType.SPLIT_SCREEN.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Partition Elimination and Boundary Shift",
                    action="Indices 0 through 4 turn translucent gray and are discarded. Pointer 'low' slides to index 5 (mid + 1). Active search space shrinks to [35, 42, 57, 68].",
                    environment="Algorithmic state canvas.",
                    camera="Pan to right active half of array.",
                    animation="Left sub-array grays out; low pointer animates to index 5; interval count drops from 9 to 4.",
                    technical_content="low = mid + 1 = 5; high = 8; Active elements: 4.",
                    on_screen_text="INTERVAL HALVED: Discarding Left Partition",
                    narration="Because the array is sorted, every element at and below the midpoint is eliminated immediately.",
                    transition="cut_to_hit",
                    generation_requirements=["faded cells", "animated pointer slide", "active range marker"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=3.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Second Midpoint and Target Match",
                    action="New midpoint mid = (5 + 8) // 2 = 6 highlights value 42. Comparison '42 == 42' evaluates true; cell 6 illuminates in emerald green with checkmark.",
                    environment="Focused array inspection view.",
                    camera="Tight focus on index 6.",
                    animation="Mid pointer shifts to cell 6; cell flashes green; checkmark badge confirms match.",
                    technical_content="mid = (5 + 8) // 2 = 6; array[6] = 42 == 42 (MATCH).",
                    on_screen_text="TARGET LOCATED: Match at Index 6",
                    narration="The next midpoint inspects index six, finding forty-two in just two total comparisons.",
                    transition="cut_to_complexity",
                    generation_requirements=["green success cell", "checkmark badge", "match readout"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Logarithmic Complexity Analysis O(log N)",
                    action="A binary decision tree diagram and O(log N) complexity curve illustrate how a billion items can be searched in only 30 steps.",
                    environment="Technical computer science chart canvas.",
                    camera="Wide view showing decision tree branching.",
                    animation="Decision tree splits down from root; step counter compares linear O(N) vs binary O(log N).",
                    technical_content="Time Complexity: O(log2 N); Max comparisons for N=1,000,000 <= 20.",
                    on_screen_text="TIME COMPLEXITY: O(log N) Efficiency",
                    narration="By halving the search space at each iteration, binary search achieves logarithmic execution speed.",
                    transition="fade_out",
                    generation_requirements=["decision tree", "complexity comparison graph"]
                )
            ]

        # =========================================================================
        # 3. MACHINE LEARNING & NEURAL NETWORKS (Layers, Weights, Forward/Backprop)
        # =========================================================================
        elif "neural network" in t_lower or "cnn" in t_lower or content_type == ContentType.MACHINE_LEARNING.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.NEURAL_NETWORK_ANIMATION.value,
                    subject="Deep Neural Network Layer Architecture",
                    action="A 4-layer neural network model materializes in 3D coordinate space with 4 input nodes, two hidden layers of 6 neurons each, and 2 output units.",
                    environment="Dark-slate AI laboratory stage with glowing cyan node rings and amber connection lines.",
                    camera="Orbital camera sweep moving from input layer to output units.",
                    animation="Nodes materialize sequentially; inter-layer synapses draw in with variable weights.",
                    technical_content="Architecture: Input(4) -> Dense(6, ReLU) -> Dense(6, ReLU) -> Output(2, Softmax).",
                    on_screen_text=f"{topic.upper()}: Network Topology",
                    narration="A neural network transforms raw input features through stacked layers of interconnected computational units.",
                    transition="cut_to_forward",
                    generation_requirements=["3D layered nodes", "weighted synapses", "layer labels"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=4.0,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.NEURAL_NETWORK_ANIMATION.value,
                    subject="Forward Propagation and Weighted Synaptic Signals",
                    action="Input values enter left nodes. Luminous electrical wave pulses travel along synapses, modulated in brightness by synaptic weights w_ij.",
                    environment="High-contrast synaptic detail view.",
                    camera="Tracking pan moving with the forward-traveling wave pulses.",
                    animation="Glowing pulse packets glide along connections into hidden neurons.",
                    technical_content="z_j = sum(w_{ij} * x_i) + b_j.",
                    on_screen_text="FORWARD PASS: Linear Combination z = Wx + b",
                    narration="Inputs multiply across synaptic weights, summing at each downstream neuron with an added bias.",
                    transition="cut_to_activation",
                    generation_requirements=["synaptic pulses", "formula overlay", "node summation"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=3.5,
                    shot_type=ShotType.SPLIT_SCREEN.value,
                    visual_type=VisualType.NEURAL_NETWORK_ANIMATION.value,
                    subject="Nonlinear Activation Function (ReLU / Sigmoid)",
                    action="Hidden neurons light up as activation function a = max(0, z) clips negative values and passes positive activations forward.",
                    environment="Split view: neuron cluster on left, activation curve graph on right.",
                    camera="Static split-screen focus on activation thresholding.",
                    animation="Graph curve highlights active linear region; neurons pulse brighter as activation increases.",
                    technical_content="Activation: a = ReLU(z) = max(0, z).",
                    on_screen_text="ACTIVATION: Non-Linear Feature Mapping",
                    narration="Non-linear activation functions enable the network to learn intricate patterns beyond simple linear boundaries.",
                    transition="cut_to_backprop",
                    generation_requirements=["activation curve", "illuminated neurons", "threshold indicator"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.0,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.NEURAL_NETWORK_ANIMATION.value,
                    subject="Loss Evaluation and Backpropagation Flow",
                    action="Output prediction is compared to ground truth, producing loss L. Red error gradient waves propagate backward from output to input.",
                    environment="Full network perspective showing reverse error flow.",
                    camera="Reverse tracking pan following the backward error wave.",
                    animation="Red error wave ripples backward through layers; synaptic lines update thickness as weights adjust.",
                    technical_content="dW = dL/da * da/dz * dz/dW; w = w - eta * dW.",
                    on_screen_text="BACKPROPAGATION: Gradient Error Flow",
                    narration="The chain rule of calculus propagates error gradients backward, updating each connection weight to reduce loss.",
                    transition="cut_to_decision",
                    generation_requirements=["reverse gradient wave", "weight delta formulas", "synapse update"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.NEURAL_NETWORK_ANIMATION.value,
                    subject="Trained Decision Boundary and High Accuracy",
                    action="A 2D feature plane displays trained non-linear decision boundary cleanly separating classification classes. Accuracy HUD displays 99.2%.",
                    environment="Clean machine learning metrics dashboard.",
                    camera="Direct overhead view of decision boundary plane.",
                    animation="Decision boundary curves smoothly to enclose cluster points; accuracy gauge locks at 99.2%.",
                    technical_content="Model Accuracy: 99.2%; Loss: 0.014; Status: Converged.",
                    on_screen_text="CONVERGENCE: Optimal Decision Boundary",
                    narration="After multiple training epochs, the network establishes an accurate boundary that generalizes to unseen data.",
                    transition="fade_out",
                    generation_requirements=["decision boundary", "scatter clusters", "accuracy HUD"]
                )
            ]

        # =========================================================================
        # 4. CONTROL SYSTEMS (PID Controllers, Feedback Loops)
        # =========================================================================
        elif "pid" in t_lower or content_type == ContentType.CONTROL_SYSTEM.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.CONTROL_SYSTEM_ANIMATION.value,
                    subject="Closed-Loop Feedback System Architecture",
                    action="A clean control block diagram renders: Setpoint r(t) enters summing junction (+/-), feeds PID Controller (Kp, Ki, Kd), drives Plant G(s), and feeds back output y(t).",
                    environment="High-contrast technical automation schematic on dark slate background.",
                    camera="Static overview with directional signal flow animation.",
                    animation="Signal arrows pulse in electric cyan; summing junction computes error e(t) = r(t) - y(t).",
                    technical_content="e(t) = r(t) - y(t); u(t) = Kp*e + Ki*int(e)dt + Kd*de/dt.",
                    on_screen_text=f"{topic.upper()}: Closed-Loop Control",
                    narration="A closed-loop control system continuously measures actual output and computes corrections against a desired setpoint.",
                    transition="cut_to_error",
                    generation_requirements=["block diagram", "summing junction", "PID formula"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=3.5,
                    shot_type=ShotType.SCOPE_VIEW.value,
                    visual_type=VisualType.CONTROL_SYSTEM_ANIMATION.value,
                    subject="Step Input and Instantaneous Error Signal",
                    action="A step setpoint jumps from 0 to 1.0. An oscilloscope curve displays the large instantaneous error gap e(t) with shaded red area.",
                    environment="Digital oscilloscope display with time divisions and voltage grid.",
                    camera="Close-up on oscilloscope sweep trace.",
                    animation="Dashed setpoint line rises instantly; error curve e(t) spikes and begins declining.",
                    technical_content="Step Input r(t) = 1.0 (t >= 0); Initial error e(0) = 1.0.",
                    on_screen_text="STEP DISTURBANCE: Error Signal e(t)",
                    narration="A sudden change in setpoint generates an immediate error signal that requires proportional corrective drive.",
                    transition="cut_to_components",
                    generation_requirements=["step setpoint line", "error shaded region", "scope grid"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.5,
                    shot_type=ShotType.SPLIT_SCREEN.value,
                    visual_type=VisualType.CONTROL_SYSTEM_ANIMATION.value,
                    subject="Proportional, Integral, and Derivative Actions",
                    action="Three concurrent telemetry traces reveal individual control contributions: Kp responds to present error, Ki integrates past cumulative error, and Kd dampens future rate of change.",
                    environment="Multi-channel control engineering telemetry display.",
                    camera="Split 3-channel oscilloscope view.",
                    animation="Three colored waveforms (Kp in cyan, Ki in amber, Kd in magenta) sum together into total control effort u(t).",
                    technical_content="P: Kp*e(t) | I: Ki*integral(e)dt | D: Kd*de(t)/dt.",
                    on_screen_text="PID THREE-TERM ACTION: Present, Past & Future",
                    narration="The proportional term provides immediate force, the integral term eliminates steady-state offset, and the derivative term prevents overshoot.",
                    transition="cut_to_response",
                    generation_requirements=["3-trace oscilloscope", "component labels", "summed output"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.0,
                    shot_type=ShotType.SCOPE_VIEW.value,
                    visual_type=VisualType.CONTROL_SYSTEM_ANIMATION.value,
                    subject="Damped Dynamic Step Response Curve",
                    action="The system output y(t) rises smoothly toward 1.0 with a controlled 8% overshoot, completing a damped harmonic settling oscillation.",
                    environment="Precision oscilloscope view.",
                    camera="Tracking the active drawing head of the output response curve.",
                    animation="Curve rises with steep slope, rounds peak overshoot at 1.08, and dampens quickly within 2% error band.",
                    technical_content="Rise Time: 0.42s; Overshoot: 8.2%; Settling Time: 1.15s.",
                    on_screen_text="DYNAMIC RESPONSE: Fast Rise & Controlled Damping",
                    narration="Tuned PID parameters deliver rapid rise time while derivative damping prevents destructive oscillation.",
                    transition="cut_to_stable",
                    generation_requirements=["step response curve", "overshoot marker", "settling band"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.CONTROL_SYSTEM_ANIMATION.value,
                    subject="Steady-State Stability and Zero Error",
                    action="Output locks perfectly onto the setpoint line y(t) = 1.000. Error readout drops to exactly 0.000 with green stability checkmark.",
                    environment="Clean control engineering summary display.",
                    camera="Overview of stabilized system with performance badge.",
                    animation="Error readout hits 0.000; stability margin gauge confirms phase margin 52 degrees.",
                    technical_content="Steady-State Error e_ss = 0.000; Phase Margin: 52 deg; Stability: Robust.",
                    on_screen_text="STABILITY ACHIEVED: Zero Steady-State Error",
                    narration="The integral term holds the system precisely at the setpoint with zero steady-state error.",
                    transition="fade_out",
                    generation_requirements=["zero error indicator", "stability gauge", "green checkmark"]
                )
            ]

        # =========================================================================
        # 5. AUTOMOTIVE & NETWORKING (CAN Bus Arbitration, ECUs, Protocols)
        # =========================================================================
        elif "can bus" in t_lower or "arbitration" in t_lower or content_type == ContentType.AUTOMOTIVE_PROCESS.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.NETWORK_PROTOCOL_ANIMATION.value,
                    subject="CAN Bus Multi-Node Network Topology",
                    action="A differential 2-wire CAN bus (CAN_H and CAN_L with 120-ohm termination) connects three vehicle ECUs: Node 1 (Brakes), Node 2 (Engine), and Node 3 (Transmission).",
                    environment="Automotive electronic network schematic with dark slate background.",
                    camera="Wide view of dual-wire bus and drop cables to transceivers.",
                    animation="CAN_H and CAN_L differential lines illuminate with quiescent 2.5V reference.",
                    technical_content="CAN 2.0B Differential Bus: CAN_H = 3.5V, CAN_L = 1.5V (Dominant); 2.5V (Recessive).",
                    on_screen_text=f"{topic.upper()}: Vehicle Bus Architecture",
                    narration="In modern vehicles, multiple Electronic Control Units share a single dual-wire Controller Area Network bus.",
                    transition="cut_to_contention",
                    generation_requirements=["dual-wire bus", "three ECU nodes", "120 ohm resistors"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=3.5,
                    shot_type=ShotType.SCOPE_VIEW.value,
                    visual_type=VisualType.NETWORK_PROTOCOL_ANIMATION.value,
                    subject="Simultaneous Transmission and Bus Contention",
                    action="Node 1 (Brakes, ID 0x0A) and Node 2 (Engine, ID 0x14) begin transmitting message frames at the exact same microsecond, creating bus contention.",
                    environment="Multi-channel digital logic analyzer screen.",
                    camera="Synchronized view of Node 1 transmit line, Node 2 transmit line, and actual physical bus.",
                    animation="Start-of-Frame bits pulse simultaneously across both transmitter channels.",
                    technical_content="Node 1 ID: 00000001010b (0x0A) | Node 2 ID: 00000010100b (0x14).",
                    on_screen_text="BUS CONTENTION: Simultaneous Node Transmission",
                    narration="When two control units transmit at the same time, CAN arbitration resolves the conflict without losing any data.",
                    transition="cut_to_arbitration",
                    generation_requirements=["digital logic waveforms", "bit clocks", "binary ID labels"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.NETWORK_PROTOCOL_ANIMATION.value,
                    subject="Bit-by-Bit Arbitration (Dominant 0 vs Recessive 1)",
                    action="At bit 7, Node 1 sends dominant '0' (differential voltage active) while Node 2 sends recessive '1'. The wired-AND bus resolves to dominant '0'.",
                    environment="High-magnification bit-level oscilloscope view.",
                    camera="Tight focus on the exact bit transition point.",
                    animation="Dominant '0' pulses drive bus to 3.5V/1.5V; Node 2 reads dominant '0' on bus while transmitting recessive '1'.",
                    technical_content="Node 1: Bit 7 = 0 (Dominant) | Node 2: Bit 7 = 1 (Recessive) -> Bus = 0.",
                    on_screen_text="ARBITRATION: Dominant '0' Overwrites Recessive '1'",
                    narration="Dominant zero bits electrically overwrite recessive one bits, allowing nodes to detect if higher-priority messages exist.",
                    transition="cut_to_backoff",
                    generation_requirements=["dominant/recessive levels", "bit comparison arrow", "wired-AND logic"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=3.5,
                    shot_type=ShotType.SCOPE_VIEW.value,
                    visual_type=VisualType.NETWORK_PROTOCOL_ANIMATION.value,
                    subject="Losing Node Back-Off to Receiver Mode",
                    action="Node 2 detects the mismatch, immediately ceases transmission without corrupting the message, and switches into passive receiving mode.",
                    environment="Logic analyzer showing channel status.",
                    camera="Focus on Node 2 channel transitioning to idle high.",
                    animation="Node 2 transmission line flatlines; 'BACKED OFF' status tag appears; Node 1 continues transmitting payload unimpeded.",
                    technical_content="Node 2 State: Lost Arbitration -> Passive Receiver; Error Count = 0.",
                    on_screen_text="ZERO COLLISION LOSS: Lower Priority Backs Off",
                    narration="The lower-priority engine unit immediately stops transmitting, leaving the bus clear for the critical braking message.",
                    transition="cut_to_payload",
                    generation_requirements=["channel disable", "status tag", "uninterrupted bus wave"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.NETWORK_PROTOCOL_ANIMATION.value,
                    subject="Uninterrupted High-Priority Frame Broadcast",
                    action="Node 1 completes its 64-bit payload broadcast with valid CRC checksum. All bus nodes acknowledge with dominant ACK bit.",
                    environment="Automotive bus architecture summary display.",
                    camera="Wide view showing data packet arriving at all network receivers.",
                    animation="Complete 8-byte payload packet illuminates along bus; green ACK pulses lock transmission.",
                    technical_content="Payload: 8 Bytes Verified; CRC: Valid; ACK: Dominant (All Nodes).",
                    on_screen_text="TRANSMISSION COMPLETE: Non-Destructive Arbitration",
                    narration="Non-destructive bitwise arbitration guarantees that safety-critical messages broadcast instantly with zero delay.",
                    transition="fade_out",
                    generation_requirements=["ACK bit pulse", "CRC checkmark", "bus telemetry summary"]
                )
            ]

        # =========================================================================
        # 6. CAD & SOFTWARE TUTORIALS (CATIA, SolidWorks, UI Tools)
        # =========================================================================
        elif "catia" in t_lower or "cad" in t_lower or content_type == ContentType.CAD_TUTORIAL.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.VIEWPORT_SCREEN.value,
                    visual_type=VisualType.CAD_3D_VISUALIZATION.value,
                    subject="CAD 3D Modeling Interface and Part Viewport",
                    action="Full-screen CAD workstation interface displaying active 3D mechanical part geometry, specification tree on left, and 3D compass on top-right.",
                    environment="Dark-slate professional CAD interface (CATIA / SolidWorks).",
                    camera="Static full-screen interface overview.",
                    animation="3D solid rotates smoothly in viewport showing profile sketch on reference plane.",
                    technical_content="Parametric 3D CAD environment and PartBody specification tree.",
                    on_screen_text=f"{topic.upper()}: Accelerated Workflow",
                    narration="When modeling complex parts in CAD, navigating nested toolbars can slow down your design workflow.",
                    transition="cut_to_search",
                    generation_requirements=["CAD UI layout", "specification tree", "3D compass"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=4.0,
                    shot_type=ShotType.SCREEN_CLOSEUP.value,
                    visual_type=VisualType.SOFTWARE_INTERFACE_SIMULATION.value,
                    subject="Command Finder in Bottom Status Bar",
                    action="Screen close-up of the bottom action bar. The mouse cursor glides smoothly toward the Command Finder input field at the bottom right.",
                    environment="High-definition macro monitor view of CAD status bar.",
                    camera="Zoom into bottom right action bar.",
                    animation="Cursor glides smoothly across screen and clicks into search input box; cursor pulses in blue.",
                    technical_content="Command Finder / Power Input box located in status bar.",
                    on_screen_text="COMMAND FINDER: Direct Tool Search",
                    narration="Instead of hunting through menus, use the Command Finder in the bottom status bar to locate any feature.",
                    transition="cut_to_filter",
                    generation_requirements=["smooth cursor motion", "status bar detail", "active input focus"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.5,
                    shot_type=ShotType.SCREEN_CLOSEUP.value,
                    visual_type=VisualType.SOFTWARE_INTERFACE_SIMULATION.value,
                    subject="Dynamic Query Entry and Tool Auto-Complete",
                    action="The search query 'c:Pad' is typed character by character. An auto-complete dropdown filters matching commands across all workbenches simultaneously.",
                    environment="CAD UI screen close-up.",
                    camera="Static focus on popup menu.",
                    animation="Text 'c:Pad' types in; matching Pad tool row highlights in electric cyan with workbench breadcrumb.",
                    technical_content="Search syntax: c:Pad; workbench breadcrumb: Part Design -> Sketch-Based Features.",
                    on_screen_text="INSTANT FILTERING: Multi-Workbench Lookup",
                    narration="Typing the command name or prefix instantly filters tools across all workbenches simultaneously.",
                    transition="cut_to_dialog",
                    generation_requirements=["keystroke animation", "auto-complete dropdown", "highlighted tool row"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.0,
                    shot_type=ShotType.VIEWPORT_SCREEN.value,
                    visual_type=VisualType.CAD_3D_VISUALIZATION.value,
                    subject="Feature Definition Dialog and 3D Extrusion",
                    action="Clicking the result activates the feature. The Pad Definition dialog opens in the viewport and generates a 3D extrusion preview on the 2D sketch.",
                    environment="CAD viewport with 3D model and floating dialog box.",
                    camera="Smooth pan across 3D viewport focusing on the extrusion preview.",
                    animation="Pad dialog opens; 2D profile extrudes into 3D solid with orange preview outline; dimension 25mm callout appears.",
                    technical_content="Pad Definition: Length = 25mm, Profile = Sketch.1.",
                    on_screen_text="ONE-CLICK EXECUTION: Feature Activated",
                    narration="Clicking the command opens its definition dialog and applies the geometric modification directly to your model.",
                    transition="cut_to_solid",
                    generation_requirements=["feature dialog box", "extrusion preview", "dimension callout"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.VIEWPORT_SCREEN.value,
                    visual_type=VisualType.CAD_3D_VISUALIZATION.value,
                    subject="Completed Parametric Solid in Geometry Tree",
                    action="The extrusion is confirmed; the completed solid turns shaded metallic and registers in the specification tree as a parametric feature.",
                    environment="Clean CAD design studio viewport.",
                    camera="Pull-back to show finished solid part and updated feature tree.",
                    animation="Completed solid renders in shaded metallic view; tree expands to show 'Pad.1'.",
                    technical_content="Parametric tree: PartBody -> Pad.1 (25mm); Geometry Status: Up to date.",
                    on_screen_text="WORKFLOW COMPLETE: Rapid Feature Creation",
                    narration="Mastering the Command Finder eliminates toolbar searching and maximizes modeling productivity.",
                    transition="fade_out",
                    generation_requirements=["metallic shaded solid", "updated feature tree", "success badge"]
                )
            ]

        # =========================================================================
        # 7. ELECTRIC VEHICLES & BATTERIES (Regen Braking, BMS, Packs)
        # =========================================================================
        elif "regenerative" in t_lower or "battery" in t_lower or "bms" in t_lower or content_type == ContentType.EV.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
                    subject="EV Powertrain and Energy Flux Architecture",
                    action="A high-voltage EV powertrain diagram displays Battery Pack (400V), Bidirectional Inverter, Traction Motor, and Drive Wheels with electrical bus connections.",
                    environment="Clean dark slate EV engineering schematic with glowing copper and blue bus lines.",
                    camera="Wide view showing powertrain component interconnections.",
                    animation="Quiescent high-voltage lines illuminate; telemetry HUD displays speed 80 km/h and Battery SOC 78%.",
                    technical_content="High Voltage Architecture: 400V DC Bus; Inverter/Motor-Generator; 150 kW Traction Unit.",
                    on_screen_text=f"{topic.upper()}: Powertrain Architecture",
                    narration="In an electric vehicle, the electric motor can operate bidirectionally as both a drive motor and an electric generator.",
                    transition="cut_to_braking",
                    generation_requirements=["powertrain schematic", "bidirectional inverter", "voltage telemetry"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=4.0,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
                    subject="Braking Deceleration and Torque Inversion",
                    action="Brake pedal activation triggers regenerative mode. Kinetic rotational energy from the wheels drives the motor shaft; torque arrows reverse direction.",
                    environment="Powertrain mechanical flux display.",
                    camera="Close-up on wheel hubs and motor shaft coupling.",
                    animation="Forward drive arrows turn cyan; opposing counter-electromotive torque vector generates 240 Nm braking force.",
                    technical_content="Regenerative Braking Torque: T_regen = -240 Nm; Kinetic Power P = T * omega.",
                    on_screen_text="TORQUE INVERSION: Motor Operates as Generator",
                    narration="During braking, vehicle momentum forces the motor to rotate, producing counter-electromotive force that slows the car.",
                    transition="cut_to_inverter",
                    generation_requirements=["opposing torque arrows", "kinetic flow lines", "torque telemetry"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=3.5,
                    shot_type=ShotType.SCOPE_VIEW.value,
                    visual_type=VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
                    subject="Inverter AC-to-DC Power Rectification",
                    action="The motor outputs 3-phase AC voltage. Inverter IGBT power switches rectify the AC waveforms into high-current DC charging flow toward the battery.",
                    environment="Power electronics oscilloscope and circuit schematic.",
                    camera="Split view of 3-phase AC waveforms rectifying into smooth DC current trace.",
                    animation="3-phase sinusoidal AC traces rectify into smooth +120A DC charging curve.",
                    technical_content="AC Generation: 3-Phase Back-EMF -> Fast Rectification -> +120A DC Charge Current.",
                    on_screen_text="RECTIFICATION: 3-Phase AC to High-Current DC",
                    narration="The bidirectional inverter converts 3-phase AC back-EMF into controlled direct current for battery recharge.",
                    transition="cut_to_bms",
                    generation_requirements=["3-phase AC sine waves", "DC current meter", "IGBT circuit"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.0,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.BATTERY_SYSTEM_ANIMATION.value,
                    subject="Battery Pack Matrix and BMS Thermal Telemetry",
                    action="Cutaway of battery pack reveals a matrix of 96 series cells. Blue charging current vectors flow into cell terminals while thermal gradient heatmap displays safe 32 deg C.",
                    environment="3D battery pack inspection bay with thermal false-color overlay.",
                    camera="3D isometric view of modular cell bricks and cooling plates.",
                    animation="Cell charging bars illuminate; thermal gradient stabilizes; BMS voltage balancing monitors each cell at 3.92V.",
                    technical_content="Pack: 96S 400V; Cell V: 3.92V +/- 5mV; Charge Current: +120A; Pack Temp: 32C.",
                    on_screen_text="ENERGY STORAGE: BMS Cell Balancing & Monitoring",
                    narration="The Battery Management System monitors cell voltages and temperatures, ensuring safe high-rate energy absorption.",
                    transition="cut_to_efficiency",
                    generation_requirements=["3D cell matrix", "thermal heatmap", "BMS cell voltage bars"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.AUTOMOTIVE_SYSTEM_ANIMATION.value,
                    subject="Energy Recovery Efficiency and Extended Range",
                    action="An energy flow sankey diagram displays 72% round-trip kinetic energy recovery. State of Charge meter increments by +1.4% with recovered kWh readout.",
                    environment="Clean EV efficiency telemetry display.",
                    camera="Overview showing energy recovery gauge and efficiency rating.",
                    animation="Sankey diagram arrows illustrate captured energy returning to pack; recovered energy HUD ticks +0.85 kWh.",
                    technical_content="Round-Trip Efficiency: 72%; Recovered Energy: +0.85 kWh; Range Extension: +15-20%.",
                    on_screen_text="ENERGY RECOVERED: Up to 70%+ Efficiency",
                    narration="Regenerative braking captures up to seventy percent of kinetic energy, significantly extending real-world driving range.",
                    transition="fade_out",
                    generation_requirements=["sankey energy flow", "SOC increment gauge", "efficiency badge"]
                )
            ]

        # =========================================================================
        # 8. MANUFACTURING & MACHINING (CNC Milling, Toolpaths, Material Removal)
        # =========================================================================
        elif "manufacturing" in t_lower or "cnc" in t_lower or "milling" in t_lower or content_type == ContentType.MANUFACTURING.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
                    subject="Raw Stock Billet Clamped in Machining Fixture",
                    action="A solid aerospace aluminum billet (6061-T6) is clamped in a precision CNC vise. Coordinate work offset datum (G54 X0 Y0 Z0) illuminates at corner.",
                    environment="Modern CNC vertical machining center enclosure with bright daylight task lighting.",
                    camera="3D perspective looking down at clamped billet stock.",
                    animation="Datum axes (X, Y, Z) project at corner; toolpath wireframe envelope visualizes stock dimensions.",
                    technical_content="Stock: Aluminum 6061-T6 Billet (150 x 100 x 50mm); Work Coordinate: G54.",
                    on_screen_text=f"{topic.upper()}: Stock Setup & Datum Reference",
                    narration="Subtractive manufacturing begins with rigid clamping of raw stock material and precise work datum calibration.",
                    transition="cut_to_spindle",
                    generation_requirements=["billet block", "datum axes G54", "machining vise"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=3.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
                    subject="Rotating End Mill Spindle and Toolpath Engagement",
                    action="A 12mm 4-flute carbide end mill rotates at 8,000 RPM. Spindle descends along G01 linear feed path with high-pressure coolant spray.",
                    environment="Close-up of spindle head and cutting tool.",
                    camera="Tight 45-degree angle on cutter flutes engaging stock face.",
                    animation="High-speed rotational blur on flutes; coolant spray particles deflect as tool enters material.",
                    technical_content="Tool: 12mm 4-Flute Carbide End Mill; Spindle: 8,000 RPM; Feed: 1,800 mm/min.",
                    on_screen_text="TOOL ENGAGEMENT: High-Speed Spindle Feed",
                    narration="The carbide end mill engages the workpiece at calibrated rotational speed and linear feed rate.",
                    transition="cut_to_pocketing",
                    generation_requirements=["rotating cutter flutes", "coolant stream", "telemetry HUD"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
                    subject="Progressive Pocket Milling and Chip Evacuation",
                    action="The cutter executes a spiral adaptive roughing toolpath. Metal chips evacuate rapidly as a precision rectangular interior pocket is carved layer by layer.",
                    environment="CNC machining stage showing active cutaway.",
                    camera="Tracking shot moving with circular toolpath motion.",
                    animation="Material voxels subtract continuously behind cutter path; glowing silver chips curl and evacuate.",
                    technical_content="Operation: Adaptive Pocket Roughing; Stepover: 2.4mm (20%); Depth of Cut: 15mm.",
                    on_screen_text="MATERIAL REMOVAL: Adaptive Toolpath Roughing",
                    narration="Adaptive toolpaths maintain constant cutter chip load, maximizing material removal rate while preserving tool life.",
                    transition="cut_to_finish",
                    generation_requirements=["progressive cutaway", "evacuating chips", "toolpath curve"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=3.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
                    subject="Contour Finishing Pass and Surface Tolerance",
                    action="A ball-nose finishing cutter glides across interior fillets with micro-stepover, leaving a mirror-smooth machined surface finish Ra 0.8.",
                    environment="Extreme close-up on finished pocket sidewall.",
                    camera="Macro camera glide across machined surface texture.",
                    animation="Fine tool passes polish pocket walls; surface roughness indicator displays Ra = 0.8 micrometers.",
                    technical_content="Finishing Pass: Spindle 10,000 RPM; Surface Finish: Ra 0.8 um; Tolerance: +/- 0.025mm.",
                    on_screen_text="SURFACE FINISHING: Precision Geometric Tolerance",
                    narration="A dedicated finishing pass removes minimal stock to achieve exacting dimensional tolerances and smooth surface texture.",
                    transition="cut_to_part",
                    generation_requirements=["smooth surface finish", "Ra gauge", "tolerance callout"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.MANUFACTURING_PROCESS_ANIMATION.value,
                    subject="Finished Machined Component Inspection",
                    action="The completed lightweight aerospace bracket is revealed. Green laser CMM coordinate inspection lines trace key features, confirming zero defects.",
                    environment="Quality inspection station with laser scanning grid.",
                    camera="Smooth pull-back reveal around finished component.",
                    animation="Laser scanner sweeps across bracket; green inspection points verify dimensions against CAD model.",
                    technical_content="Final Inspection: 100% Dimensions Within Tolerance (+/- 0.025mm); Status: PASS.",
                    on_screen_text="PART COMPLETED: Verified Aerospace Component",
                    narration="The finished component emerges with reduced mass, optimal structural stiffness, and verified geometric compliance.",
                    transition="fade_out",
                    generation_requirements=["finished aerospace bracket", "green laser scan lines", "inspection pass badge"]
                )
            ]

        # =========================================================================
        # 9. PROGRAMMING & COMPUTER SCIENCE (Recursion, Stacks, Memory)
        # =========================================================================
        elif "recursion" in t_lower or "stack" in t_lower or content_type == ContentType.PROGRAMMING_TUTORIAL.value:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Recursive Function Definition and Base Condition",
                    action="A clean IDE code editor shows a recursive function definition (e.g. factorial(n)). Code line highlights show the base condition 'if n <= 1 return 1' and recursive call.",
                    environment="Dark-slate modern IDE code editor with syntax highlighting.",
                    camera="Static focus on clean code layout with bracket hierarchy.",
                    animation="Code lines highlight in amber; base condition box pulses with conditional check.",
                    technical_content="def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)",
                    on_screen_text=f"{topic.upper()}: Function Anatomy",
                    narration="A recursive function solves complex problems by calling itself with smaller inputs until reaching a base condition.",
                    transition="cut_to_push",
                    generation_requirements=["syntax-highlighted code", "base condition box", "cursor highlight"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=4.0,
                    shot_type=ShotType.SPLIT_SCREEN.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Call Stack Frame Allocation (Push Sequence)",
                    action="Calling factorial(4) triggers successive stack frame allocations. Stack boxes push upward in memory: factorial(4) -> factorial(3) -> factorial(2) -> factorial(1).",
                    environment="Split screen: code execution on left, memory call stack on right.",
                    camera="Tilt up as stack frames push vertically in memory.",
                    animation="Stack frames slide in on top of each other; local variable registers (n=4, n=3, n=2, n=1) record in frames.",
                    technical_content="Stack Push: [n=4] -> [n=3] -> [n=2] -> [n=1] (Active Top).",
                    on_screen_text="STACK ALLOCATION: Pushing Frames n=4 to n=1",
                    narration="Each recursive call pauses the current execution and pushes a new frame with local variables onto the call stack.",
                    transition="cut_to_base",
                    generation_requirements=["call stack boxes", "frame parameters", "memory address labels"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=3.5,
                    shot_type=ShotType.CLOSE_UP.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Base Case Reached: Halting Recursive Descent",
                    action="At n=1, the base condition '1 <= 1' evaluates TRUE. The top stack frame turns green, halting further recursion and initiating the return chain.",
                    environment="Close-up on top of call stack.",
                    camera="Tight focus on top frame factorial(1).",
                    animation="Base condition flashes green; return value 1 appears in return register.",
                    technical_content="Base Evaluation: n=1 <= 1 -> TRUE; Return value = 1.",
                    on_screen_text="BASE CASE HIT: Halting Infinite Recursion",
                    narration="Reaching the base condition stops recursive descent, providing the concrete value needed to resolve paused calculations.",
                    transition="cut_to_unwind",
                    generation_requirements=["green base frame", "return register", "true condition badge"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.5,
                    shot_type=ShotType.SPLIT_SCREEN.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Call Stack Unwinding and Return Multiplication",
                    action="The call stack unwinds in Last-In First-Out order. Frame factorial(1) pops returning 1; frame 2 computes 2*1=2; frame 3 computes 3*2=6; frame 4 computes 4*6=24.",
                    environment="Split screen showing stack pops and mathematical bubbling.",
                    camera="Tracking down the stack as frames resolve and pop.",
                    animation="Frames pop with particle dissipate effect; return values bubble down and multiply into next frame.",
                    technical_content="factorial(2) = 2*1 = 2 -> factorial(3) = 3*2 = 6 -> factorial(4) = 4*6 = 24.",
                    on_screen_text="STACK UNWINDING: Resolving Calculations",
                    narration="As stack frames pop in reverse order, returned values multiply through previous calls until the original invocation completes.",
                    transition="cut_to_result",
                    generation_requirements=["stack pop animation", "value bubbling", "multiplication steps"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.ALGORITHM_VISUALIZATION.value,
                    subject="Final Return Result and Memory Deallocation",
                    action="Call stack clears to empty state. Final verified result 'factorial(4) = 24' displays with execution tree summary and memory freed badge.",
                    environment="Clean computer science summary display.",
                    camera="Direct view of final output terminal.",
                    animation="Console terminal prints output 24; memory meter drops to zero; green success checkmark locks.",
                    technical_content="Execution Complete: Output = 24; Total Stack Frames: 4; Memory Deallocated: 100%.",
                    on_screen_text="EXECUTION COMPLETE: Final Result = 24",
                    narration="With all stack frames deallocated, the recursive call chain completes, returning the final verified result.",
                    transition="fade_out",
                    generation_requirements=["terminal output", "empty stack", "memory freed badge"]
                )
            ]

        # =========================================================================
        # 10. GENERAL EDUCATIONAL / TECHNICAL (Fallback for other topics)
        # =========================================================================
        else:
            scenes = [
                StoryboardScene(
                    scene_id=1,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.TECHNICAL_3D_ANIMATION.value,
                    subject=f"System Architecture and Fundamentals of {topic}",
                    action=f"A clean technical schematic introduces the core components, inputs, and operational boundaries of {t_lower}.",
                    environment="Modern technical schematic on deep dark-slate background with vibrant vector annotations.",
                    camera="Smooth establishing pan across system topology.",
                    animation="System boundaries and primary nodes illuminate with directional connectivity arrows.",
                    technical_content=f"Primary Architectural Specification: {t_clean}.",
                    on_screen_text=f"{topic.upper()}: System Architecture",
                    narration=f"To understand {t_lower}, we examine its underlying architecture, physical mechanism, and operating principles.",
                    transition="cut_to_stage2",
                    generation_requirements=["system schematic", "labeled nodes", "vector connections"]
                ),
                StoryboardScene(
                    scene_id=2,
                    duration=3.5,
                    shot_type=ShotType.PERSPECTIVE_3D.value,
                    visual_type=VisualType.TECHNICAL_3D_ANIMATION.value,
                    subject=f"Input Dynamics and Operational Stimulus",
                    action=f"An active input stimulus is introduced into {t_lower}, driving state transitions across internal components.",
                    environment="High-contrast technical visualization canvas.",
                    camera="Close-up focus on input interface and signal propagation.",
                    animation="Animated particles and signal vectors travel through the mechanism, triggering calibrated reactions.",
                    technical_content=f"Input Parameters and Operating Bounds for {t_clean}.",
                    on_screen_text="OPERATIONAL DYNAMICS: State Transition",
                    narration="As input parameters change, internal components react according to governing physical and computational laws.",
                    transition="cut_to_stage3",
                    generation_requirements=["dynamic signal vectors", "component interaction"]
                ),
                StoryboardScene(
                    scene_id=3,
                    duration=4.0,
                    shot_type=ShotType.SPLIT_SCREEN.value,
                    visual_type=VisualType.MATHEMATICAL_ANIMATION.value,
                    subject="Mathematical Governing Equations and Quantitative Telemetry",
                    action=f"Split view displaying theoretical governing equations on left alongside real-time quantitative telemetry curves on right.",
                    environment="Split theoretical and observational telemetry stage.",
                    camera="Static balanced split-screen framing.",
                    animation="Equation terms illuminate in sync with telemetry data curves plotting in real time.",
                    technical_content=f"Governing Transfer Functions and Calibrated Constants for {t_clean}.",
                    on_screen_text="QUANTITATIVE ANALYSIS: Governing Equations",
                    narration="Mathematical governing equations predict exact system behavior, ensuring repeatable and reliable operation.",
                    transition="cut_to_stage4",
                    generation_requirements=["formula synchronization", "real-time telemetry plot"]
                ),
                StoryboardScene(
                    scene_id=4,
                    duration=4.0,
                    shot_type=ShotType.SCOPE_VIEW.value,
                    visual_type=VisualType.TECHNICAL_3D_ANIMATION.value,
                    subject="Dynamic State Response and Mechanism Output",
                    action=f"The system completes its transformation cycle. Mechanical movement, data throughput, and power conversion reach equilibrium.",
                    environment="Precision engineering oscilloscope / telemetry monitor.",
                    camera="Tracking shot following the settling response curve.",
                    animation="Oscilloscope wave stabilizes at target value; dynamic mechanism operates smoothly in synchronization.",
                    technical_content=f"Response Output: Steady State Calibrated at 100% Efficiency.",
                    on_screen_text="SYSTEM RESPONSE: Operational Payoff",
                    narration="The coordinated interaction of every component delivers consistent output, fulfilling the system's core function.",
                    transition="cut_to_stage5",
                    generation_requirements=["settled response curve", "synchronized mechanism animation"]
                ),
                StoryboardScene(
                    scene_id=5,
                    duration=3.5,
                    shot_type=ShotType.TECHNICAL_SCHEMATIC.value,
                    visual_type=VisualType.TECHNICAL_3D_ANIMATION.value,
                    subject=f"{topic} Key Takeaway and Verified Outcome",
                    action=f"System summary showing final operating metrics, verified tolerances, and performance achievements for {t_lower}.",
                    environment="Clean technical summary dashboard.",
                    camera="Overview with highlighted key takeaway badges.",
                    animation="Key metrics lock in with green verified badges; system schematic glows in completion state.",
                    technical_content=f"System Verification: 100% Validated; Status: Operational.",
                    on_screen_text="KEY TAKEAWAY: System Mastery",
                    narration=f"Mastering these principles provides the foundation for designing, optimizing, and controlling {t_lower} in real-world applications.",
                    transition="fade_out",
                    generation_requirements=["summary metrics", "verified checkmark badge"]
                )
            ]

        storyboard = EducationalStoryboard(
            title=topic,
            topic=topic,
            content_type=content_type,
            learning_objective=f"Understand the technical mechanisms and operational principles of {topic}.",
            duration=sum(s.duration for s in scenes),
            presenter_required=False,
            software_required=content_type in [ContentType.CAD_TUTORIAL.value, ContentType.SOFTWARE_TUTORIAL.value, ContentType.ALGORITHM.value, ContentType.PROGRAMMING_TUTORIAL.value],
            mathematical_visualization_required=content_type in [ContentType.MATHEMATICAL_CONCEPT.value, ContentType.MACHINE_LEARNING.value, ContentType.CONTROL_SYSTEM.value],
            technical_visualization_required=True,
            required_visuals=rules.get("required_visual_primitives", []),
            required_actions=rules.get("required_actions", []),
            prohibited_visual_behavior=rules.get("prohibited_metaphors", []),
            scenes=scenes,
            script=" ".join(s.narration for s in scenes),
            visual_direction="Universal Technical Video Mode: High-precision 1080p procedural animation, clean scientific styling, and professional synchronized subtitles.",
            validation_passed=True,
            validation_warnings=[],
            generation_backend_used="UNIVERSAL_TECHNICAL_DIRECTOR"
        )
        return storyboard
