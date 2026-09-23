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
    AI_PRESENTER = "ai_presenter"
    AI_WORKSTATION_VIDEO = "ai_workstation_video"
    SOFTWARE_DEMONSTRATION = "software_demonstration"
    SCREEN_CLOSEUP = "screen_closeup"
    MATHEMATICAL_ANIMATION = "mathematical_animation"
    TECHNICAL_3D_ANIMATION = "technical_3d_animation"
    MOTION_GRAPHIC = "motion_graphic"
    STATIC_VISUAL = "static_visual"


class ContentType(str, Enum):
    TECHNICAL_CONCEPT = "TECHNICAL_CONCEPT"
    MATHEMATICAL_CONCEPT = "MATHEMATICAL_CONCEPT"
    SOFTWARE_TUTORIAL = "SOFTWARE_TUTORIAL"
    CAD_TUTORIAL = "CAD_TUTORIAL"
    PROGRAMMING_TUTORIAL = "PROGRAMMING_TUTORIAL"
    ENGINEERING_PROCESS = "ENGINEERING_PROCESS"
    AUTOMOTIVE_PROCESS = "AUTOMOTIVE_PROCESS"
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
    generation_requirements: List[str] = field(default_factory=list)
    
    # Optional metadata populated during generation
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    clip_path: Optional[str] = None
    validation_status: str = "PASSED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryboardScene":
        return cls(
            scene_id=int(data.get("scene_id", 1)),
            duration=float(data.get("duration", 3.5)),
            shot_type=str(data.get("shot_type", "medium_shot")),
            visual_type=str(data.get("visual_type", "ai_workstation_video")),
            subject=str(data.get("subject", "")),
            action=str(data.get("action", "")),
            environment=str(data.get("environment", "")),
            camera=str(data.get("camera", "")),
            animation=str(data.get("animation", "")),
            technical_content=str(data.get("technical_content", "")),
            on_screen_text=str(data.get("on_screen_text", "")),
            narration=str(data.get("narration", "")),
            transition=str(data.get("transition", "cut")),
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
    presenter_required: bool
    software_required: bool
    mathematical_visualization_required: bool
    technical_visualization_required: bool
    required_visuals: List[str]
    required_actions: List[str]
    prohibited_visual_behavior: List[str]
    scenes: List[StoryboardScene]
    script: str = ""
    visual_direction: str = ""
    validation_passed: bool = True
    validation_warnings: List[str] = field(default_factory=list)
    generation_backend_used: str = "MULTI_DISPATCH_DIRECTOR"

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
            presenter_required=bool(data.get("presenter_required", True)),
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
