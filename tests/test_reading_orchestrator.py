from fastapi.testclient import TestClient

from guardian_core.api.app import app
from guardian_core.reading import project_reading_result, run_reading

client = TestClient(app)


def test_run_reading_is_reproducible_with_a_seed():
    first = run_reading(question="אני מתלבט אם לעבור עבודה", seed="orchestrator-test")
    second = run_reading(question="אני מתלבט אם לעבור עבודה", seed="orchestrator-test")
    assert first.status == "completed"
    assert [c.card_id for c in first.draw.cards] == [c.card_id for c in second.draw.cards]


def test_run_reading_requests_clarification_for_ambiguous_question():
    outcome = run_reading(question="אני רוצה לעזוב")
    assert outcome.status == "clarification_required"
    assert outcome.clarification_question
    assert outcome.spread is None
    assert outcome.draw is None


def test_project_reading_result_excludes_internal_engine_artifacts():
    outcome = run_reading(question="אני מתלבט אם לעבור עבודה", seed="projection-test")
    result = project_reading_result(outcome)
    dumped = result.model_dump(mode="json")
    assert "question_dna" not in dumped
    assert "spread" not in dumped
    assert "draw" not in dumped
    assert "reading_source" not in dumped
    assert len(result.sections) == len(outcome.spread.positions)


def test_v1_readings_and_run_reading_agree_for_the_same_seed():
    response = client.post("/v1/readings", json={
        "question": "אני מתלבט אם לעבור עבודה",
        "conversation_context": [],
        "language": "he",
        "seed": "agreement-test",
    })
    assert response.status_code == 200
    api_cards = [card["card_id"] for card in response.json()["draw"]["cards"]]

    outcome = run_reading(question="אני מתלבט אם לעבור עבודה", seed="agreement-test")
    assert [c.card_id for c in outcome.draw.cards] == api_cards
