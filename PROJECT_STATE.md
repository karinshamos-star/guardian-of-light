# Guardian — Project State

Canonical handover document. Read this alone; no prior chat history is required to continue development.

## Executive Summary

Guardian is a reflective tarot/numerology reading app. Backend (`guardian_core`, Python/FastAPI/Pydantic) implements a `WorldSession` state machine driving a spatial "library" narrative, plus a reading pipeline (Intent → Spread → Card Draw → Narrative). A new subsystem, the **Guardian Knowledge Platform**, is now the canonical source for tarot/numerology/etc. domain content: Git + YAML, Pydantic-validated, compiled into a versioned runtime package. Notion is an editorial/authoring surface only, never the runtime source.

Canonical knowledge is never authored directly, and is never a transcription of any single external source. Authoring flows through a staged pipeline — `sources/` → `extraction/` → `synthesis/` → `knowledge/` → Knowledge Package — detailed in "Architecture Overview" below.

**Git is initialized and the repo has real commit history.** This is no longer the blocking item it once was — see "Current Implementation Status" and "Exact Next Implementation Task" below for what's actually next.

## Repository Structure

```
sources/                            # raw reference material — local only, gitignored except README.md
  README.md                         # source-registration SOP (scan, register, wait for approval)

extraction/                         # per-source faithful analysis, one doc per target entity
  README.md                         # format, review rules

synthesis/                          # Guardian's own editorial voice, cross-source
  README.md                         # format, review rules

knowledge/                          # canonical knowledge source (data, no Python)
  README.md                         # governance + layout rules
  domains/<domain>/<entity_type>s/<slug>.yaml   # every entity, no exceptions
  _compiled/knowledge_package.json  # committed build artifact

src/guardian_core/
  api/                 # FastAPI app + static web clients (index.html, world-demo.*)
  experience/          # WorldSession state machine, ExperienceCommand contract
  intent/ spread/ cards/ reading/   # reading pipeline engines + Runtime Orchestrator
  ai/                  # AIReadingProvider (OpenAI, with template fallback)
  knowledge/           # Guardian Knowledge Platform (models, corpus, writers, loader, build, domains/)

tests/                 # pytest, flat structure, 67 tests passing
pyproject.toml         # deps: pydantic, fastapi, uvicorn, openai, pyyaml; optional groups: dev, extraction (pypdf)
.venv/                 # project-local virtualenv (gitignored) — pip install -e ".[dev,extraction]"
```

## Architecture Overview

Two subsystems, both mature:

1. **WorldSession / reading pipeline** — `experience/session.py` is a state machine (`ARRIVAL → AVATAR_SELECTION → LIBRARY_ENTRANCE → GUIDE_GREETING → SECRET_DOOR → READING_ROOM → QUESTION → READING → REFLECTION → RETURN_TO_LIBRARY`, looping `RETURN_TO_LIBRARY → GUIDE_GREETING`). Backend owns all narrative/world state; clients send `WorldAction`s and render the returned `ExperienceCommand` (versioned Pydantic contract: guide dialogue/emotion/animation, camera, interaction cue, world snapshot, payload). The web client (`api/static/world-demo.js`) is a **generic** renderer keyed only on `interaction.type` (`continue`/`ask_question`/`choose_option`/`talk_to_guide`/`follow_guide`) — it never branches on scene/state names.

2. **Guardian Knowledge Platform** — canonical pipeline:
   ```
   sources/ → extraction/ → synthesis/ → knowledge/ (Structured YAML)
     → Validation (Pydantic + structural checks) → KnowledgeCorpus (generic, in-memory)
     → Writer (pluggable; JSON first) → Knowledge Package → guardian_core (loader)
   ```

   Each stage has a distinct, deliberately non-interchangeable role (each
   directory carries its own README with the full format/review rules):

   - **`sources/`** — private reference materials (PDFs, books, course
     files, notes). Local only; gitignored except its own `README.md`;
     **never loaded by Guardian at runtime**. Adding or changing a file
     here runs the source-registration SOP: scan → register a `draft`
     `Source` entity in `knowledge/domains/source/sources/` (matched by
     `data.reference_url` + a SHA-256 in `data.notes`) → stop and wait for
     explicit per-source approval before any extraction begins.
   - **`extraction/`** — faithful analysis of one specific source (or set
     of sources cited together) for one target entity. Four required
     sections: direct quotes, source-derived paraphrase, first-pass
     proposed interpretation, open questions. Reviewed on exactly one
     question — does this honestly represent what the source says? Not
     schema-validated; that looseness is intentional.
   - **`synthesis/`** — **Guardian's original editorial synthesis**,
     written fresh and organized by the target schema's fields, not by
     source, and explicitly separated from any single source's wording or
     proprietary framework. This is the stage that actually decides what
     Guardian teaches. Reconciles multiple extraction documents when more
     than one source touches the same target entity. Reviewed on a
     different question than extraction — is this genuine synthesis, not
     reworded source material?
   - **`knowledge/`** — canonical, validated, machine-readable knowledge.
     Compiled by hand (manual by design, for now) from a reviewed
     synthesis document — never authored directly, never a transcription.
     Pydantic-validated, status-gated
     (`draft → needs_review → reviewed → ready_for_ai → deprecated`).
   - **Knowledge Package** — the compiled, versioned runtime artifact
     (`knowledge/_compiled/knowledge_package.json` today) that
     `guardian_core` actually loads. Only `ready_for_ai`-gated entities are
     included.

## Licensing & Usage Rights

External sources in `sources/` remain subject to ordinary copyright and
licensing rules no matter which pipeline stage touches them.

- **Synthesis does not automatically resolve licensing concerns.** Writing
  Guardian's own editorial synthesis instead of transcribing a source is a
  real, meaningful step away from republishing someone's text, but it is
  not a substitute for actually knowing the usage-rights relationship with
  a source's author — especially when one source is a dominant or sole
  input to an entity.
- **No source-derived content may reach `status: ready_for_ai` while its
  usage rights are unresolved.** If a `Source` entity's `data.notes` (or
  any later review step) flags an open rights/licensing question, every
  entity whose `provenance.source_ids` includes it stays capped below
  `ready_for_ai` until that question is explicitly resolved by a human.
  `corpus.build_corpus()` does not currently check this automatically —
  it's a review discipline, not (yet) an enforced rule.

## Infrastructure Completed (`src/guardian_core/knowledge/`)

- `models.py` — generic `KnowledgeEntity` envelope: `id` (`{domain}.{entity_type}.{slug}`, dot-namespaced, permanent), `schema_version`, `domain`, `entity_type`, `name`, `status` (`ReviewStatus`: draft/needs_review/reviewed/ready_for_ai/deprecated), `provenance` (`source_ids`, `confidence`: primary/secondary/interpretive/unverified, `claim_ids`), `changelog`, `related` (generic `dict[str, list[str]]`), `tags`, `data` (open dict — domain content lives here, infra never inspects it).
- `corpus.py` — `build_corpus()`: discover YAML, parse, validate schema/ID format/uniqueness/path-convention/dangling relations & sources/claims/ready_for_ai gating (confidence≠unverified + non-empty changelog required). `find_possible_duplicates()`: near-duplicate name heuristic (difflib), warns not fails. `KnowledgeCorpus.filtered(min_status=...)` for gating.
- `writers/` — `PackageWriter` protocol; `JSONPackageWriter` is the first, not the only, implementation. `PackageManifest` (format, content_hash, built_at, gate, counts) — `content_hash` is meant to populate the reading pipeline's `trace.knowledge_version`.
- `loader.py` — `KnowledgePackage` protocol; `JSONKnowledgePackage` first backend; `register_loader()` extension point.
- `build.py` — CLI: `python -m guardian_core.knowledge.build --knowledge-root knowledge --out knowledge/_compiled --gate ready_for_ai`.

## Domain Schemas (`src/guardian_core/knowledge/domains/`)

Optional, pluggable layer on top of the generic envelope — core infra never imports these. Each is a `KnowledgeEntity` subclass narrowing `domain`/`entity_type` (Literal) and typing `data`, registered via `DomainSchema`/`register_domain_schema`:

- **`tarot.py`** — `CardKnowledge` (arcana, suit, rank, name_he, core_essence, light/shadow/reversed expression, `CardDimensions` [emotional/mental/relational/practical/spiritual], `CardContexts` [love/work/money/decision/growth], reflection_questions, grounded_actions, safety_notes). Merges the old rich Notion tarot schema with the newer cross-tradition relation habit.
- **`numerology.py`** — `NumberKnowledge` (value: **unconstrained int** — range is a content decision, not infra).
- **`calculations.py`** — `CalculationMethod` (formula_description, formula_steps, inputs, worked_example). `entity_type` fixed; `domain` deliberately NOT narrowed (reusable across numerology/astrology/etc.).
- **`sources.py`** — `Source` (author, source_type, publication_year, reference_url, citation, notes). `domain=entity_type="source"` always.
- **`claims.py`** — `KnowledgeClaim` (statement, claim_type, confidence, `disputed: bool`, evidence_note). `domain=entity_type="claim"`.
- **`concepts.py`** — `Concept` (category: archetype/process/state/virtue/shadow/practice, definition, light/shadow expression, guardian_language). `domain=entity_type="concept"`.

Cross-cutting types (Source/Claim/Concept) may use short 2-segment ids (`source.guardian-editorial`) since the id pattern only requires ≥2 dot-segments.

## Build Pipeline & Runtime Flow

`build_corpus(root)` → raises `KnowledgeValidationError` with *every* issue found (not just first) → `corpus.filtered(min_status=ReviewStatus.READY_FOR_AI)` for production → `JSONPackageWriter().write(corpus, out_dir, gate=...)` → `load_knowledge_package(path)` → `DomainSchema.materialize(entity)` gives a typed object (e.g. `CardKnowledge`) to consumers. **Not yet wired**: `reading/engine.py` still uses hardcoded `CARD_THEMES`/`SUIT_THEMES` dicts — has not been switched to load from the Knowledge Package.

## Validation & CI Rules (all in `corpus.build_corpus`, enforced today via pytest, not yet via a CI workflow file)

Schema validation; ID format + uniqueness; file path matches `domains/<domain>/<entity_type>s/<slug>.yaml`; no dangling `related`/`source_ids`/`claim_ids`; `ready_for_ai` requires confidence≠unverified AND ≥1 changelog entry; near-duplicate name warning (non-blocking). **No `.github/workflows` exists yet** — validation currently runs only via manually-invoked pytest.

## Versioning & Migration Strategy

`schema_version` (per entity, `MAJOR.MINOR`) records which version of its `(domain, entity_type)` data shape it was authored against. Additive/optional-field changes = minor bump, no migration needed. Renamed/removed/retyped fields = major bump, requires a registered `VersionMigration(from_version, to_version, migrate_fn)` on that type's `DomainSchema`. `DomainSchema.materialize()` applies the migration chain transparently at load time — authored YAML is never force-rewritten when a schema evolves.

## Current Implementation Status

67/67 tests passing. **Git is initialized with real commit history** (git init through the sources/extraction/synthesis pipeline design, in a series of small commits).

The original vertical slice — 4 `ready_for_ai` entities (`tarot.card.major-00` "The Fool", `source.guardian-editorial`, `claim.tarot-0001`, `concept.new-beginnings`) — is still the only content compiled all the way through to `knowledge/_compiled/knowledge_package.json`, reloaded, and materialized into a typed object. It **predates** `extraction/` and `synthesis/` and was authored editorially, not produced through them — don't treat it as an example of the current authoring workflow, only of the compile/validate/load mechanics.

`sources/` is populated with real reference material (numerology and tarot PDFs). 13 `Source` entities exist in `knowledge/domains/source/sources/`, all `status: draft` except one `deprecated` (its file was removed from `sources/` after registration; never extracted from). **No entity has yet been produced through the full `sources/` → `extraction/` → `synthesis/` → `knowledge/` pipeline** — that first real end-to-end run is the immediate next task (see "Exact Next Implementation Task"), currently blocked on source approval and an unresolved licensing question.

## Completed Milestones

1. WorldSession onboarding question resolved (no separate `ONBOARDING` state; deferred true once-per-user flow until profiles exist).
2. Reading pipeline extracted into a shared `run_reading()` orchestrator (`reading/orchestrator.py`), wired into `WorldSession.COMPLETE_READING`; clarification-required stays in `READING` (self-loop via `ASK_QUESTION`), no new state.
3. `world-demo` web client rewritten as a generic `ExperienceCommand` renderer; dead `readingPanel` code removed from `index.html`/`app.js`.
4. Full Notion knowledge-base audit performed (found: duplicate tarot schemas, Numerology DB/page mismatch, zero populated cross-domain relations, no Notion→code ingestion contract).
5. Canonical architecture decided: Git+YAML+Pydantic over SQLite/Postgres/Neo4j (all premature at current content scale).
6. Guardian Knowledge Platform infrastructure built and tested (generic layer).
7. Six domain schemas designed, implemented, with versioning/migration mechanism.
8. End-to-end vertical slice (The Fool) proven.

## Remaining Milestones (priority order)

1. **Run the first real end-to-end knowledge migration** through `sources/` → `extraction/` → `synthesis/` → `knowledge/` → Knowledge Package — to validate the pipeline itself, not to produce volume — before scaling to milestones 2 or 5 below. Blocked on: (a) explicit approval of which registered `Source` to use, (b) that source's usage-rights question resolved enough to proceed. **Update this document again once that validation is complete, especially if anything about the process changes as a result.**
2. Populate remaining 21 Major Arcana cards as `CardKnowledge` YAML (per "12 — Tarot Knowledge Schema"'s own MVP recommendation) — via the full pipeline this time, not authored directly the way `major-00` was.
3. Wire `reading/engine.py` to load from the Knowledge Package instead of hardcoded dicts.
4. Add a CI workflow (GitHub Actions or equivalent) running pytest + a compiled-package-freshness check (rebuild and diff against committed `knowledge_package.json`).
5. Reconcile/migrate real Numerology content into `NumberKnowledge` YAML — a content task, not an infra task. `sources/numerology/` now has real candidate material registered as draft `Source` entities; see `knowledge/domains/source/sources/`.
6. Document Life Path / Expression Number / Soul Urge calculation methods as `CalculationMethod` entities (pending real source material — do not fabricate formulas).
7. Explicitly freeze Astrology/Kabbalah/Crystals/Human Design content until Tarot+Numerology are further along.
8. Decide on (optional) a formal Notion-export adapter script vs. authoring YAML directly going forward.

## Open Architectural Decisions

- Whether to build an automated Notion→YAML export adapter now, or author YAML directly and treat Notion as pure legacy reference.
- CI platform/workflow specifics (not yet chosen or configured).
- Whether `knowledge_package.json` rebuilds should be a pre-commit hook or remain a manual step.
- Whether `CalculationMethod.inputs` should become structured/typed rather than free-text strings.
- Whether the extraction → synthesis → YAML compile steps should eventually be scripted. Currently manual by design; revisit once the same transcription pattern repeats often enough to justify the infrastructure.

## Do NOT Redesign or Change

- Notion is an authoring adapter, never the runtime/canonical source.
- Do not hardcode domain-content decisions (numeric ranges, naming conventions, specific traditions' rules) into `knowledge/models.py` or `corpus.py` — those belong in `domains/*.py` or content files.
- Do not assume JSON is the permanent Knowledge Package format — keep writer/loader behind the `PackageWriter`/`KnowledgePackage` protocols.
- No new `WorldState` for onboarding or for reading-clarification — both are handled via existing states/actions by design.
- `WorldSession` must never call `/v1/readings` over HTTP or duplicate pipeline steps — it must call the shared `run_reading()` in-process function.
- Never expose internal engine artifacts (`question_dna`, `spread`, `draw`, `reading_source`) through `ExperienceCommand` or through a `ready_for_ai`-gated Knowledge Package.
- Do not adopt SQLite/Postgres/Neo4j as canonical now — only reconsider if content/query scale genuinely demands it, and then only as an additional writer/loader backend.
- The web client must stay generic (branch on `interaction.type` only) — never re-encode narrative logic client-side.
- Canonical knowledge (`knowledge/`) must never be authored directly and must never be a transcription of any single external source — it is compiled from a reviewed `synthesis/` document, which itself synthesizes (not just aggregates) across `extraction/` documents. This holds even when only one source exists for a given entity.
- No source-derived entity may reach `status: ready_for_ai` while its source's usage rights are unresolved — see "Licensing & Usage Rights" above.

## Exact Next Implementation Task

Git is initialized; that is no longer the blocking item.

**Next: run the first real end-to-end knowledge migration** through the full `sources/` → `extraction/` → `synthesis/` → `knowledge/` → Knowledge Package pipeline — to validate the pipeline itself, not to produce content volume — before touching Remaining Milestone #2 (the other 21 Major Arcana cards) or #5 (Numerology reconciliation).

As of this writing, `source.numerology-number-cards-1-9-guide` (registered, `status: draft`) has been recommended as the first candidate on content-quality and structural-fit grounds, but is **not yet approved**. Do not begin extraction until: (a) the user explicitly approves a source, and (b) the usage-rights relationship with that source's author is clear enough to proceed — per "Licensing & Usage Rights" above, unresolved rights don't block getting as far as `needs_review`, but do block `ready_for_ai`.
