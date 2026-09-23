"""
storyboard.py
Data structures and schema definitions for the AI Educational Video Director.
Replaces simplistic 3-beat image prompts with a full multi-scene, action-oriented storyboard.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class ShotType(str, Enum):
    WIDE_WORKSPACE = "wide_workspace"
    OVER_THE_SHOULDER = "over_the_shoulder"
    SCREEN_CLOSEUP = "screen_closeup"
    MEDIUM_SHOT = "medium_shot"
    MEDIUM_ENGINEER = "medium_engineer"
    CLOSE_UP = "close_up"
    MACRO_DETAIL = "macro_detail"
    PERSPECTIVE_3D = "3d_perspective"
    SPLIT_SCREEN = "split_screen"
    TECHNICAL_SCHEMATIC = "technical_schematic"
    SCOPE_VIEW = "scope_view"
    VIEWPORT_SCREEN = "viewport_screen"


class VisualType(str, Enum):
    MATHEMATICAL_ANIMATION = "mathematical_animation"
    ALGORITHM_VISUALIZATION = "algorithm_visualization"
    NEURAL_NETWORK_ANIMATION = "neural_network_animation"
    CONTROL_SYSTEM_ANIMATION = "control_system_animation"
    NETWORK_PROTOCOL_ANIMATION = "network_protocol_animation"
    BATTERY_SYSTEM_ANIMATION = "battery_system_animation"
    CAD_3D_VISUALIZATION = "cad_3d_visualization"
    SOFTWARE_INTERFACE_SIMULATION = "software_interface_simulation"
    AUTOMOTIVE_SYSTEM_ANIMATION = "automotive_system_animation"
    MANUFACTURING_PROCESS_ANIMATION = "manufacturing_process_animation"
    SYSTEM_ARCHITECTURE_DIAGRAM = "system_architecture_diagram"
    DATA_VISUALIZATION = "data_visualization"
    TECHNICAL_3D_ANIMATION = "technical_3d_animation"
    MOTION_GRAPHIC = "motion_graphic"
    STATIC_VISUAL = "static_visual"


class ContentType(str, Enum):
    MATHEMATICAL = "MATHEMATICAL"
    MATHEMATICAL_CONCEPT = "MATHEMATICAL_CONCEPT"
    ALGORITHM = "ALGORITHM"
    MACHINE_LEARNING = "MACHINE_LEARNING"
    CONTROL_SYSTEM = "CONTROL_SYSTEM"
    AUTOMOTIVE = "AUTOMOTIVE"
    AUTOMOTIVE_PROCESS = "AUTOMOTIVE_PROCESS"
    EV = "EV"
    CAD = "CAD"
    CAD_TUTORIAL = "CAD_TUTORIAL"
    SOFTWARE_TUTORIAL = "SOFTWARE_TUTORIAL"
    PROGRAMMING = "PROGRAMMING"
    PROGRAMMING_TUTORIAL = "PROGRAMMING_TUTORIAL"
    MANUFACTURING = "MANUFACTURING"
    ENGINEERING_PROCESS = "ENGINEERING_PROCESS"
    PHYSICS = "PHYSICS"
    ELECTRONICS = "ELECTRONICS"
    SYSTEM_ARCHITECTURE = "SYSTEM_ARCHITECTURE"
    PROCESS = "PROCESS"
    DATA_VISUALIZATION = "DATA_VISUALIZATION"
    TECHNICAL_CONCEPT = "TECHNICAL_CONCEPT"
    SCIENTIFIC = "SCIENTIFIC"
    GENERAL_EDUCATIONAL = "GENERAL_EDUCATIONAL"


@dataclass
class StoryboardScene:
    scene_id: int
    duration: float
    shot_type: str
    visual_type: str
    subject: str
    action: str
    environment: str
    camera: str
    animation: str
    technical_content: str
    on_screen_text: str
    narration: str
    transition: str
    purpose: str = ""
    visual_description: str = ""
    camera_motion: str = ""
    caption: str = ""
    generation_requirements: List[str] = field(default_factory=list)
    
    # Optional metadata populated during generation
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    clip_path: Optional[str] = None
    validation_status: str = "PASSED"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["caption"] = self.caption or self.on_screen_text
        d["visual_description"] = self.visual_description or self.action
        d["camera_motion"] = self.camera_motion or self.camera
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryboardScene":
        action_val = str(data.get("action", data.get("visual_description", "")))
        camera_val = str(data.get("camera", data.get("camera_motion", "")))
        text_val = str(data.get("on_screen_text", data.get("caption", "")))
        return cls(
            scene_id=int(data.get("scene_id", 1)),
            duration=float(data.get("duration", 3.5)),
            shot_type=str(data.get("shot_type", "medium_shot")),
            visual_type=str(data.get("visual_type", "universal_technical_diagram")),
            subject=str(data.get("subject", "")),
            action=action_val,
            environment=str(data.get("environment", "")),
            camera=camera_val,
            animation=str(data.get("animation", "")),
            technical_content=str(data.get("technical_content", "")),
            on_screen_text=text_val,
            narration=str(data.get("narration", "")),
            transition=str(data.get("transition", "cut")),
            purpose=str(data.get("purpose", "")),
            visual_description=action_val,
            camera_motion=camera_val,
            caption=text_val,
            generation_requirements=list(data.get("generation_requirements", [])),
            image_path=data.get("image_path"),
            audio_path=data.get("audio_path"),
            clip_path=data.get("clip_path"),
            validation_status=data.get("validation_status", "PASSED"),
        )


@dataclass
class EducationalStoryboard:
    title: str
    topic: str
    content_type: str
    learning_objective: str
    duration: float
    presenter_required: bool = False
    software_required: bool = False
    mathematical_visualization_required: bool = False
    technical_visualization_required: bool = True
    required_visuals: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    prohibited_visual_behavior: List[str] = field(default_factory=list)
    scenes: List[StoryboardScene] = field(default_factory=list)
    script: str = ""
    visual_direction: str = ""
    validation_passed: bool = True
    validation_warnings: List[str] = field(default_factory=list)
    generation_backend_used: str = "UNIVERSAL_TECHNICAL_DIRECTOR"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["scenes"] = [s.to_dict() for s in self.scenes]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EducationalStoryboard":
        scenes_data = data.get("scenes", [])
        scenes = [
            s if isinstance(s, StoryboardScene) else StoryboardScene.from_dict(s)
            for s in scenes_data
        ]
        return cls(
            title=data.get("title", "Educational Video"),
            topic=data.get("topic", "Educational Topic"),
            content_type=data.get("content_type", ContentType.GENERAL_EDUCATIONAL.value),
            learning_objective=data.get("learning_objective", ""),
            duration=float(data.get("duration", sum(s.duration for s in scenes) or 15.0)),
            presenter_required=bool(data.get("presenter_required", False)),
            software_required=bool(data.get("software_required", False)),
            mathematical_visualization_required=bool(data.get("mathematical_visualization_required", False)),
            technical_visualization_required=bool(data.get("technical_visualization_required", True)),
            required_visuals=list(data.get("required_visuals", [])),
            required_actions=list(data.get("required_actions", [])),
            prohibited_visual_behavior=list(data.get("prohibited_visual_behavior", [])),
            scenes=scenes,
            script=data.get("script", " ".join(s.narration for s in scenes)),
            visual_direction=data.get("visual_direction", ""),
            validation_passed=bool(data.get("validation_passed", True)),
            validation_warnings=list(data.get("validation_warnings", [])),
            generation_backend_used=data.get("generation_backend_used", "MULTI_DISPATCH_DIRECTOR")
        )
