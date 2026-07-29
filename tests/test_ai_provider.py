import pytest

from guardian_core.ai import AIReadingProvider, AIReadingUnavailable


def test_ai_provider_disabled_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = AIReadingProvider()
    assert provider.enabled is False


def test_ai_provider_enabled_with_explicit_key():
    provider = AIReadingProvider(api_key="test-key")
    assert provider.enabled is True


def test_ai_validation_accepts_valid_shape():
    value = {
        "central_message": "מסר",
        "sections": [
            {"position": "א", "card": "קלף", "text": "פירוש"}
        ],
        "reflection_question": "מה עולה?",
        "grounded_action": "כתבי משפט.",
        "closing": "הבחירה בידייך.",
    }
    AIReadingProvider._validate(value, expected_cards=1)


def test_ai_validation_rejects_wrong_section_count():
    value = {
        "central_message": "מסר",
        "sections": [],
        "reflection_question": "מה עולה?",
        "grounded_action": "כתבי משפט.",
        "closing": "הבחירה בידייך.",
    }
    with pytest.raises(AIReadingUnavailable):
        AIReadingProvider._validate(value, expected_cards=1)
