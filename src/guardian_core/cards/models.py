from pydantic import BaseModel, Field


class CardDrawRequest(BaseModel):
    card_count: int = Field(ge=1, le=5)
    position_ids: list[str]
    seed: str | None = None
    allow_reversals: bool = True


class DrawnCard(BaseModel):
    card_id: str
    name_en: str
    name_he: str
    orientation: str
    position_id: str


class CardDrawResult(BaseModel):
    draw_id: str
    seed: str
    seed_hash: str
    cards: list[DrawnCard]
