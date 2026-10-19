from fastapi.testclient import TestClient

from guardian_core.api.app import app

client = TestClient(app)


def _resolve_action(interaction: dict) -> tuple[str, dict]:
    """Mirrors world-demo.js's actionFor(): the client only ever branches on
    interaction.type, never on scene/state names, so this proves a generic
    ExperienceCommand-driven client can walk the whole lifecycle."""
    kind = interaction["type"]
    if kind == "continue":
        return interaction["input_key"], {}
    if kind == "ask_question":
        key = interaction.get("input_key") or "question"
        return "ask_question", {key: "אני מתלבט אם לעבור עבודה"}
    if kind == "choose_option":
        return interaction["input_key"], {"option_id": interaction["options"][0]["id"]}
    if kind in ("talk_to_guide", "follow_guide"):
        return kind, {}
    raise AssertionError(f"no client rule for interaction type '{kind}'")


def test_generic_interaction_driven_client_completes_full_lifecycle():
    created = client.post("/v1/world/sessions").json()
    session_id = created["session"]["session_id"]
    command = created["command"]

    seen_states = [created["session"]["state"]]
    saw_completed_reading = False

    for _ in range(15):
        action, payload = _resolve_action(command["interaction"])
        response = client.post(f"/v1/world/sessions/{session_id}/actions", json={"action": action, "payload": payload})
        assert response.status_code == 200
        body = response.json()
        command = body["command"]
        seen_states.append(body["session"]["state"])

        reading = command.get("payload", {}).get("reading")
        if reading and reading.get("status") == "completed":
            saw_completed_reading = True

        if body["session"]["state"] == "return_to_library":
            break

    assert seen_states[-1] == "return_to_library"
    assert saw_completed_reading


def test_generic_client_never_needs_internal_engine_fields():
    created = client.post("/v1/world/sessions").json()
    session_id = created["session"]["session_id"]
    command = created["command"]

    for _ in range(15):
        action, payload = _resolve_action(command["interaction"])
        response = client.post(f"/v1/world/sessions/{session_id}/actions", json={"action": action, "payload": payload})
        command = response.json()["command"]
        assert "question_dna" not in command
        assert "spread" not in command
        assert "draw" not in command
        if command["scene"] == "library" and command["interaction"]["input_key"] == "return":
            break
