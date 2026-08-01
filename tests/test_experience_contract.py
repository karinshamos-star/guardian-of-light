import pytest
from pydantic import ValidationError

from guardian_core.experience import (
    CameraCue,
    CameraMode,
    ExperienceCommand,
    GuideAnimation,
    GuideCue,
    GuideEmotion,
    InteractionCue,
    InteractionOption,
    InteractionType,
    SceneId,
)


def test_experience_command_serializes_for_web_or_unity_client():
    command = ExperienceCommand(
        command_id="cmd-001",
        session_id="session-001",
        sequence=3,
        scene=SceneId.LIBRARY,
        guide=GuideCue(
            dialogue="ברוכה הבאה לספרייה.",
            emotion=GuideEmotion.WELCOMING,
            animation=GuideAnimation.GREET,
        ),
        camera=CameraCue(
            mode=CameraMode.FOCUS,
            target="keeper_of_light",
            duration_seconds=1.5,
        ),
        interaction=InteractionCue(
            type=InteractionType.CHOOSE_OPTION,
            prompt="מה תרצי לעשות?",
            options=[
                InteractionOption(id="follow_guide", label="ללכת אחרי המדריך")
            ],
        ),
        effects=["library_dust_motes"],
    )

    payload = command.model_dump(mode="json")

    assert payload["contract_version"] == "1.0"
    assert payload["scene"] == "library"
    assert payload["guide"]["animation"] == "greet"
    assert payload["camera"]["target"] == "keeper_of_light"
    assert payload["interaction"]["options"][0]["id"] == "follow_guide"


def test_camera_action_requires_target():
    with pytest.raises(ValidationError, match="camera target is required"):
        CameraCue(mode=CameraMode.FOCUS)


def test_ask_question_requires_input_key():
    with pytest.raises(ValidationError, match="input_key"):
        InteractionCue(type=InteractionType.ASK_QUESTION)


def test_choose_option_requires_options():
    with pytest.raises(ValidationError, match="at least one option"):
        InteractionCue(type=InteractionType.CHOOSE_OPTION)


def test_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExperienceCommand(
            command_id="cmd-001",
            session_id="session-001",
            sequence=0,
            scene=SceneId.LIBRARY_ENTRANCE,
            unsupported="value",
        )
