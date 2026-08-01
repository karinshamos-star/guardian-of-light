from __future__ import annotations

from typing import Literal

from guardian_core.ai import AIReadingProvider, AIReadingUnavailable
from guardian_core.cards import CardDrawRequest, draw_cards
from guardian_core.intent import IntentRequest, classify_intent
from guardian_core.intent.models import ConversationTurn
from guardian_core.spread import SpreadSelectionRequest, select_spread

from .engine import create_reading
from .models import ReadingOutcome, ReadingResult, ReadingSection


def run_reading(
    *,
    question: str,
    conversation_context: list[ConversationTurn] | None = None,
    language: Literal["he", "en"] = "he",
    seed: str | None = None,
) -> ReadingOutcome:
    """The Runtime Orchestrator (Guardian Engine Contracts v1.0, §10).

    Single in-process implementation shared by /v1/readings and WorldSession's
    COMPLETE_READING action, so both surfaces stay consistent by construction.
    """
    dna = classify_intent(IntentRequest(
        question=question,
        conversation_context=conversation_context or [],
        language=language,
    ))

    if dna.clarification_required:
        return ReadingOutcome(
            status="clarification_required",
            question_dna=dna,
            spread=None,
            draw=None,
            reading=None,
            reading_source=None,
            clarification_question=dna.clarification_question,
        )

    spread = select_spread(SpreadSelectionRequest(question_dna=dna))
    draw = draw_cards(CardDrawRequest(
        card_count=spread.card_count,
        position_ids=[position.id for position in spread.positions],
        seed=seed,
        allow_reversals=True,
    ))

    provider = AIReadingProvider()
    reading_source: Literal["ai", "template"] = "template"
    try:
        reading = provider.generate(question=question, question_dna=dna, spread=spread, draw=draw)
        reading_source = "ai"
    except AIReadingUnavailable:
        reading = create_reading(dna, spread, draw)

    return ReadingOutcome(
        status="completed",
        question_dna=dna,
        spread=spread,
        draw=draw,
        reading=reading,
        reading_source=reading_source,
        clarification_question=None,
    )


def project_reading_result(outcome: ReadingOutcome) -> ReadingResult:
    """Narrows a full ReadingOutcome to the client-safe shape WorldSession embeds."""
    if outcome.status == "clarification_required":
        return ReadingResult(status="clarification_required", clarification_question=outcome.clarification_question)

    reading = outcome.reading or {}
    return ReadingResult(
        status="completed",
        central_message=reading.get("central_message"),
        sections=[ReadingSection(**section) for section in reading.get("sections", [])],
        reflection_question=reading.get("reflection_question"),
        grounded_action=reading.get("grounded_action"),
        closing=reading.get("closing"),
    )
