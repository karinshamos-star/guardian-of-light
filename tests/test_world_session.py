from fastapi.testclient import TestClient

from guardian_core.api.app import app
from guardian_core.experience import WorldAction, WorldSession, WorldState, new_session


def test_world_session_happy_path():
    session = new_session()
    assert session.command().interaction.input_key == "begin"
    session.apply(WorldAction.BEGIN)
    session.apply(WorldAction.CHOOSE_AVATAR, {"avatar_id": "seeker"})
    session.apply(WorldAction.ENTER_LIBRARY)
    session.apply(WorldAction.TALK_TO_GUIDE)
    session.apply(WorldAction.FOLLOW_GUIDE)
    session.apply(WorldAction.ENTER_SECRET_ROOM)
    command = session.apply(WorldAction.ASK_QUESTION, {"question": "מה חשוב לי עכשיו?"})
    assert session.state is WorldState.READING
    assert command.payload["question"] == "מה חשוב לי עכשיו?"


def _session_at_reading(question: str = "אני מתלבט אם לעבור עבודה") -> WorldSession:
    session = new_session()
    session.apply(WorldAction.BEGIN)
    session.apply(WorldAction.CHOOSE_AVATAR, {"avatar_id": "seeker"})
    session.apply(WorldAction.ENTER_LIBRARY)
    session.apply(WorldAction.TALK_TO_GUIDE)
    session.apply(WorldAction.FOLLOW_GUIDE)
    session.apply(WorldAction.ENTER_SECRET_ROOM)
    session.apply(WorldAction.ASK_QUESTION, {"question": question})
    return session


def test_complete_reading_runs_pipeline_and_transitions_to_reflection():
    session = _session_at_reading()
    command = session.apply(WorldAction.COMPLETE_READING, {"seed": "world-session-test"})
    assert session.state is WorldState.REFLECTION
    assert session.reading_result is not None
    assert session.reading_result.status == "completed"
    assert session.reading_result.sections
    assert session.reading_result.reflection_question
    assert session.reading_result.grounded_action
    assert command.guide.dialogue == session.reading_result.central_message
    assert command.payload["reading"]["reflection_question"] == session.reading_result.reflection_question


def test_complete_reading_stays_in_reading_state_when_clarification_is_required():
    session = _session_at_reading(question="אני רוצה לעזוב")
    command = session.apply(WorldAction.COMPLETE_READING)
    assert session.state is WorldState.READING
    assert session.reading_result is not None
    assert session.reading_result.status == "clarification_required"
    assert command.interaction.input_key == "question"

    command = session.apply(WorldAction.ASK_QUESTION, {"question": "אני מתלבט אם לעבור עבודה"})
    assert session.state is WorldState.READING
    assert command.interaction.input_key == "complete_reading"
    assert "לעזוב" in session.question and "עבודה" in session.question
    session.apply(WorldAction.COMPLETE_READING, {"seed": "clarify-then-complete"})
    assert session.state is WorldState.REFLECTION
    assert session.reading_result.status == "completed"


def test_reflection_command_never_leaks_internal_engine_artifacts():
    session = _session_at_reading()
    command = session.apply(WorldAction.COMPLETE_READING, {"seed": "leak-check"})
    dumped_payload = command.payload
    assert "question_dna" not in dumped_payload
    assert "spread" not in dumped_payload
    assert "draw" not in dumped_payload
    assert "reading_source" not in dumped_payload.get("reading", {})


def test_invalid_transition_is_rejected():
    session = new_session()
    try:
        session.apply(WorldAction.RETURN)
    except ValueError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("expected invalid transition")


def test_world_session_api():
    client = TestClient(app)
    created = client.post("/v1/world/sessions")
    assert created.status_code == 200
    body = created.json()
    session_id = body["session"]["session_id"]
    moved = client.post(f"/v1/world/sessions/{session_id}/actions", json={"action": "begin", "payload": {}})
    assert moved.status_code == 200
    assert moved.json()["session"]["state"] == "avatar_selection"


def test_world_objects_change_with_session_actions():
    session = new_session()
    first = session.command()
    assert first.world.location_id == "library_entrance"
    assert session.object_states["secret_door"] == "hidden"

    session.apply(WorldAction.BEGIN)
    session.apply(WorldAction.CHOOSE_AVATAR, {"avatar_id": "seeker"})
    entered = session.apply(WorldAction.ENTER_LIBRARY)
    assert session.object_states["library_doors"] == "open"
    assert entered.world.guide_activity == "greeting_visitor"

    revealed = session.apply(WorldAction.TALK_TO_GUIDE)
    secret_door = next(o for o in revealed.world.objects if o.object_id == "secret_door")
    assert secret_door.state == "revealed"


def test_world_session_api_exposes_object_state():
    client = TestClient(app)
    body = client.post("/v1/world/sessions").json()
    session_id = body["session"]["session_id"]
    fetched = client.get(f"/v1/world/sessions/{session_id}")
    assert fetched.status_code == 200
    assert fetched.json()["object_states"]["library_doors"] == "closed"
    assert fetched.json()["guide_activity"] == "waiting_at_entrance"
