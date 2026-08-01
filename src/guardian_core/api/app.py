from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from guardian_core.ai import AIReadingProvider
from guardian_core.intent import IntentRequest, classify_intent
from guardian_core.experience import WorldAction, WorldSession, new_session
from guardian_core.reading import run_reading
from guardian_core.spread import SpreadSelectionRequest, select_spread

app = FastAPI(
    title="Guardian of Light MVP",
    version="0.6.0",
    description="Runnable local MVP for Guardian of Light.",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadingRequest(IntentRequest):
    seed: str | None = None


class WorldActionRequest(BaseModel):
    action: WorldAction
    payload: dict = {}


WORLD_SESSIONS: dict[str, WorldSession] = {}


def _session_view(session: WorldSession) -> dict:
    return {
        "session_id": session.session_id,
        "state": session.state,
        "sequence": session.sequence,
        "avatar_id": session.avatar_id,
        "question": session.question,
        "history": session.history,
        "object_states": session.object_states,
        "guide_activity": session.guide_activity,
    }




@app.post("/v1/world/sessions")
def create_world_session():
    session = new_session()
    WORLD_SESSIONS[session.session_id] = session
    command = session.command()
    return {"session": _session_view(session), "command": command}


@app.get("/v1/world/sessions/{session_id}")
def get_world_session(session_id: str):
    session = WORLD_SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="world session not found")
    return _session_view(session)


@app.post("/v1/world/sessions/{session_id}/actions")
def apply_world_action(session_id: str, request: WorldActionRequest):
    session = WORLD_SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="world session not found")
    try:
        command = session.apply(request.action, request.payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"session": _session_view(session), "command": command}


@app.get("/world-demo", include_in_schema=False)
def world_demo():
    return FileResponse(STATIC_DIR / "world-demo.html")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.6.0")


@app.get("/v1/system/status")
def system_status():
    provider = AIReadingProvider()
    return {
        "version": "0.6.0",
        "ai_enabled": provider.enabled,
        "reading_mode": "ai_with_template_fallback" if provider.enabled else "template",
    }


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
    try:
        outcome = run_reading(
            question=request.question,
            conversation_context=request.conversation_context,
            language=request.language,
            seed=request.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if outcome.status == "clarification_required":
        return {
            "status": "clarification_required",
            "question_dna": outcome.question_dna,
            "clarification_question": outcome.clarification_question,
        }

    return {
        "status": "completed",
        "reading_source": outcome.reading_source,
        "question_dna": outcome.question_dna,
        "spread": outcome.spread,
        "draw": outcome.draw,
        "reading": outcome.reading,
    }
