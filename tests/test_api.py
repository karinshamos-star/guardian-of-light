from fastapi.testclient import TestClient

from guardian_core.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.3.0"}


def test_intent_endpoint():
    response = client.post("/v1/intent/classify", json={
        "question": "אני מתלבט אם לעבור עבודה",
        "conversation_context": [],
        "language": "he",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "career"
    assert body["core_need"] == "decision_support"


def test_spread_endpoint():
    intent = client.post("/v1/intent/classify", json={
        "question": "אני מתלבט אם לעבור עבודה",
        "conversation_context": [],
        "language": "he",
    }).json()

    response = client.post("/v1/spreads/select", json={
        "question_dna": intent,
        "available_spreads": [],
        "user_preferences": {},
    })
    assert response.status_code == 200
    assert response.json()["spread_id"] == "decision-three"
