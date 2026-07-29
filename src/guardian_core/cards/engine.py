from __future__ import annotations

import hashlib
import random
import uuid

from .deck import DECK
from .models import CardDrawRequest, CardDrawResult, DrawnCard


def draw_cards(request: CardDrawRequest) -> CardDrawResult:
    if len(request.position_ids) != request.card_count:
        raise ValueError("position_ids length must match card_count")

    seed = request.seed or str(uuid.uuid4())
    rng = random.Random(seed)
    selected = rng.sample(DECK, request.card_count)

    cards = []
    for card, position_id in zip(selected, request.position_ids):
        orientation = "reversed" if request.allow_reversals and rng.random() < 0.35 else "upright"
        cards.append(DrawnCard(
            card_id=card["card_id"],
            name_en=card["name_en"],
            name_he=card["name_he"],
            orientation=orientation,
            position_id=position_id,
        ))

    return CardDrawResult(
        draw_id=str(uuid.uuid4()),
        seed=seed,
        seed_hash=hashlib.sha256(seed.encode("utf-8")).hexdigest(),
        cards=cards,
    )
