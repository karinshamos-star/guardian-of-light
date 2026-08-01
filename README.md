# Guardian of Light MVP

A runnable local prototype of Guardian of Light.

## What works

- Hebrew question input in a browser
- Intent Engine
- Spread Selector
- Reproducible 78-card draw
- Upright/reversed orientations
- Initial reflective narrative
- Clarification route for ambiguous questions
- Crisis route blocks ordinary tarot flow
- FastAPI backend and responsive web interface

## Run locally

```bash
python -m pip install -e ".[dev]"
uvicorn guardian_core.api:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Test

```bash
pytest
```

## Important limitation

The reading text in v0.3 is template-based. It is not yet connected to an LLM,
the approved tarot knowledge base, authentication, a database, or production hosting.

## Experience Contract (Unity-ready)

The `guardian_core.experience` package defines a versioned `ExperienceCommand` contract between Guardian Brain and interactive clients. See `EXPERIENCE_CONTRACT.md`.

