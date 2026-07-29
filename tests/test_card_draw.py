from guardian_core.cards import CardDrawRequest, draw_cards


def test_seed_reproduces_same_cards_and_orientations():
    request = CardDrawRequest(
        card_count=3,
        position_ids=["a", "b", "c"],
        seed="guardian-test-seed",
        allow_reversals=True,
    )
    first = draw_cards(request)
    second = draw_cards(request)
    assert first.cards == second.cards
    assert len({card.card_id for card in first.cards}) == 3


def test_position_count_must_match():
    try:
        draw_cards(CardDrawRequest(
            card_count=2,
            position_ids=["only-one"],
            seed="x",
        ))
    except ValueError as exc:
        assert "position_ids" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
