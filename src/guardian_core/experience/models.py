"""Transport contracts between Guardian Brain and interactive clients.

The models in this module deliberately describe *what* should happen in the
experience. Rendering, animation playback, audio, camera movement, and input
handling remain client responsibilities (web today, Unity later).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SceneId(StrEnum):
    AVATAR_SELECTION = "avatar_selection"
    LIBRARY_ENTRANCE = "library_entrance"
    LIBRARY = "library"
    SECRET_PASSAGE = "secret_passage"
    SECRET_READING_ROOM = "secret_reading_room"


class GuideEmotion(StrEnum):
    NEUTRAL = "neutral"
    WELCOMING = "welcoming"
    CURIOUS = "curious"
    THOUGHTFUL = "thoughtful"
    REASSURING = "reassuring"


class GuideAnimation(StrEnum):
    IDLE = "idle"
    GREET = "greet"
    LISTEN = "listen"
    SPEAK = "speak"
    INVITE_FOLLOW = "invite_follow"
    WALK_TO_BOOKSHELF = "walk_to_bookshelf"
    OPEN_SECRET_PASSAGE = "open_secret_passage"
    PRESENT_READING_TABLE = "present_reading_table"


class InteractionType(StrEnum):
    NONE = "none"
    CHOOSE_AVATAR = "choose_avatar"
    CONTINUE = "continue"
    TALK_TO_GUIDE = "talk_to_guide"
    FOLLOW_GUIDE = "follow_guide"
    ASK_QUESTION = "ask_question"
    CHOOSE_OPTION = "choose_option"


class WorldObjectType(StrEnum):
    PROP = "prop"
    DOOR = "door"
    BOOK = "book"
    NPC = "npc"
    LIGHT = "light"


class WorldObjectCue(BaseModel):
    """Semantic state for an object that a client can render locally."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(min_length=1, max_length=120)
    object_type: WorldObjectType
    state: str = Field(default="idle", min_length=1, max_length=80)
    visible: bool = True
    interactive: bool = False
    available_actions: list[str] = Field(default_factory=list, max_length=20)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorldSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: str = Field(min_length=1, max_length=120)
    objects: list[WorldObjectCue] = Field(default_factory=list, max_length=100)
    guide_activity: str = Field(default="idle", min_length=1, max_length=80)


class CameraMode(StrEnum):
    NONE = "none"
    FOCUS = "focus"
    FOLLOW = "follow"
    CUT = "cut"


class InteractionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=160)
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class GuideCue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str = Field(default="keeper_of_light", min_length=1, max_length=80)
    dialogue: str = Field(default="", max_length=4000)
    emotion: GuideEmotion = GuideEmotion.NEUTRAL
    animation: GuideAnimation = GuideAnimation.IDLE
    voice_style: str | None = Field(default=None, max_length=80)


class CameraCue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: CameraMode = CameraMode.NONE
    target: str | None = Field(default=None, max_length=120)
    duration_seconds: float | None = Field(default=None, ge=0, le=30)

    @model_validator(mode="after")
    def target_is_required_for_camera_action(self) -> "CameraCue":
        if self.mode is not CameraMode.NONE and not self.target:
            raise ValueError("camera target is required when camera mode is not 'none'")
        return self


class InteractionCue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: InteractionType = InteractionType.NONE
    prompt: str | None = Field(default=None, max_length=500)
    options: list[InteractionOption] = Field(default_factory=list, max_length=20)
    input_key: str | None = Field(default=None, max_length=80)
    # Passthrough steps (EXPERIENCE_FLOW_V1 §1.3): the client shows no button and
    # advances on its own after this many seconds if it is ignored.
    auto_advance_seconds: float | None = Field(default=None, ge=0.5, le=30)

    @model_validator(mode="after")
    def validate_interaction_shape(self) -> "InteractionCue":
        if self.type is InteractionType.CHOOSE_OPTION and not self.options:
            raise ValueError("choose_option interaction requires at least one option")
        if self.type is InteractionType.ASK_QUESTION and not self.input_key:
            raise ValueError("ask_question interaction requires input_key")
        return self


class ExperienceCommand(BaseModel):
    """Versioned command that any Guardian client can render.

    The backend owns narrative state and returns semantic IDs. A client maps
    those IDs to its local scenes, Animator states, audio, and UI components.
    """

    model_config = ConfigDict(extra="forbid")

    contract_version: str = Field(default="1.0", pattern=r"^\d+\.\d+$")
    command_id: str = Field(min_length=1, max_length=120)
    session_id: str = Field(min_length=1, max_length=120)
    sequence: int = Field(ge=0)
    scene: SceneId
    guide: GuideCue = Field(default_factory=GuideCue)
    camera: CameraCue = Field(default_factory=CameraCue)
    interaction: InteractionCue = Field(default_factory=InteractionCue)
    effects: list[str] = Field(default_factory=list, max_length=20)
    world: WorldSnapshot = Field(default_factory=lambda: WorldSnapshot(location_id="unassigned"))
    payload: dict[str, Any] = Field(default_factory=dict)
