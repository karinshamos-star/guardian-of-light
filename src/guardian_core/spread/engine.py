from __future__ import annotations

from guardian_core.intent.models import CoreNeed, SafetyFlag

from .catalog import DEFAULT_SPREADS
from .models import SpreadDefinition, SpreadSelection, SpreadSelectionRequest

CRISIS_FLAGS = {
    SafetyFlag.SELF_HARM_OR_SUICIDE,
    SafetyFlag.ABUSE_OR_COERCION,
    SafetyFlag.IMMEDIATE_DANGER,
}


def _candidate_score(spread: SpreadDefinition, request: SpreadSelectionRequest) -> float:
    dna = request.question_dna
    score = 0.0

    if dna.core_need.value in spread.supported_needs:
        score += 0.55

    if dna.complexity in spread.supported_complexities:
        score += 0.25

    preferred_count = request.user_preferences.get("preferred_card_count")
    if preferred_count == spread.card_count:
        score += 0.10

    # Smaller spreads are preferred when equally capable.
    score += max(0.0, 0.10 - (spread.card_count - 1) * 0.02)
    return min(score, 1.0)


def select_spread(request: SpreadSelectionRequest) -> SpreadSelection:
    dna = request.question_dna

    if CRISIS_FLAGS.intersection(dna.safety_flags):
        raise ValueError("Tarot spread selection is blocked for crisis-routed requests.")

    catalog = [spread for spread in (request.available_spreads or DEFAULT_SPREADS) if spread.active]
    if not catalog:
        raise ValueError("No active spreads are available.")

    if dna.clarification_required:
        raise ValueError("Spread selection requires a resolved Question DNA profile.")

    scored = sorted(
        ((spread, _candidate_score(spread, request)) for spread in catalog),
        key=lambda item: (-item[1], item[0].card_count, item[0].spread_id),
    )
    selected, score = scored[0]

    if score < 0.55:
        raise ValueError("No available spread safely matches the Question DNA profile.")

    reason = (
        f"Selected the smallest active spread matching core need "
        f"'{dna.core_need.value}' and complexity '{dna.complexity}'."
    )

    return SpreadSelection(
        spread_id=selected.spread_id,
        spread_version=selected.version,
        reason=reason,
        positions=selected.positions,
        card_count=selected.card_count,
        confidence=round(score, 2),
    )
