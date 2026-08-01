import pytest

from guardian_core.intent import IntentRequest, classify_intent
from guardian_core.spread import SpreadSelectionRequest, select_spread


def dna(question: str):
    return classify_intent(IntentRequest(question=question, language="he"))


def test_daily_guidance_uses_one_card():
    result = select_spread(SpreadSelectionRequest(
        question_dna=dna("איזה מסר להיום יכול לעזור לי?")
    ))
    assert result.spread_id == "single-reflection"
    assert result.card_count == 1


def test_career_decision_uses_three_cards():
    result = select_spread(SpreadSelectionRequest(
        question_dna=dna("אני מתלבט אם לעבור עבודה")
    ))
    assert result.spread_id == "decision-three"
    assert result.card_count == 3
    assert [p.id for p in result.positions] == ["factors", "tension", "grounded_step"]


def test_healing_uses_pattern_spread():
    result = select_spread(SpreadSelectionRequest(
        question_dna=dna("איך אני יכולה להתמודד רגשית עם תקופת ההחלמה?")
    ))
    assert result.spread_id == "pattern-three"


def test_ambiguous_question_cannot_select_spread():
    with pytest.raises(ValueError, match="resolved Question DNA"):
        select_spread(SpreadSelectionRequest(
            question_dna=dna("אני רוצה לעזוב")
        ))


def test_crisis_question_is_blocked():
    with pytest.raises(ValueError, match="blocked"):
        select_spread(SpreadSelectionRequest(
            question_dna=dna("אני לא רוצה לחיות יותר")
        ))
