from types import SimpleNamespace

from guardian_core.cards.deck import DECK
from guardian_core.reading.demo_card_text import card_text
from guardian_core.reading.engine import _card_section_text

# The Fool is authored in the knowledge package, so it is deliberately not a placeholder.
AUTHORED = {"major-00"}


def test_every_unauthored_card_has_complete_placeholder_text():
    for card in DECK:
        if card["card_id"] in AUTHORED:
            continue
        parts = card_text(card["card_id"])
        assert parts is not None, card["card_id"]
        assert len(parts) == 4 and all(p.strip() for p in parts), card["card_id"]
        assert "{" not in "".join(parts), card["card_id"]


def test_every_card_renders_specific_text_in_both_orientations():
    for card in DECK:
        for orientation in ("upright", "reversed"):
            ns = SimpleNamespace(card_id=card["card_id"], name_he=card["name_he"], orientation=orientation)
            text = _card_section_text(ns)
            assert card["name_he"] in text
            assert "הוא מציע להתבונן" not in text, f"{card['card_id']} fell back to the generic theme line"


def test_authored_entity_wins_over_placeholder():
    fool = SimpleNamespace(card_id="major-00", name_he="השוטה", orientation="upright")
    assert "עמידה על סף הידוע" in _card_section_text(fool)
