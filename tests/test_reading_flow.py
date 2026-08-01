from fastapi.testclient import TestClient
from guardian_core.api import app

client = TestClient(app)


def test_home_page_is_available():
    response = client.get("/")
    assert response.status_code == 200
    assert "שומר האור" in response.text


def test_end_to_end_reading():
    response = client.post("/v1/readings", json={
        "question": "אני מתלבט אם לעבור עבודה",
        "conversation_context": [],
        "language": "he",
        "seed": "e2e-test",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["spread"]["spread_id"] == "decision-three"
    assert len(body["draw"]["cards"]) == 3
    assert len(body["reading"]["sections"]) == 3
    assert body["reading"]["reflection_question"]
    assert body["reading"]["grounded_action"]


def test_ambiguous_question_requests_clarification():
    response = client.post("/v1/readings", json={
        "question": "אני רוצה לעזוב",
        "conversation_context": [],
        "language": "he",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "clarification_required"
