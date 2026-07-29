from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from guardian_core.cards import CardDrawRequest, draw_cards
from guardian_core.intent import IntentRequest, classify_intent
from guardian_core.reading import create_reading
from guardian_core.spread import SpreadSelectionRequest, select_spread

app = FastAPI(
    title="Guardian of Light MVP",
    version="0.3.0",
    description="Runnable local MVP for Guardian of Light.",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadingRequest(IntentRequest):
    seed: str | None = None


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.3.0")


@app.post("/v1/intent/classify")
def classify(request: IntentRequest):
    return classify_intent(request)


@app.post("/v1/spreads/select")
def spread_select(request: SpreadSelectionRequest):
    try:
        return select_spread(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/readings")
def create_full_reading(request: ReadingRequest):
    dna = classify_intent(IntentRequest(
        question=request.question,
        conversation_context=request.conversation_context,
        language=request.language,
    ))

    if dna.clarification_required:
        return {
            "status": "clarification_required",
            "question_dna": dna,
            "clarification_question": dna.clarification_question,
        }

    try:
        spread = select_spread(SpreadSelectionRequest(question_dna=dna))
        draw = draw_cards(CardDrawRequest(
            card_count=spread.card_count,
            position_ids=[position.id for position in spread.positions],
            seed=request.seed,
            allow_reversals=True,
        ))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    reading = create_reading(dna, spread, draw)
    return {
        "status": "completed",
        "question_dna": dna,
        "spread": spread,
        "draw": draw,
        "reading": reading,
    }
