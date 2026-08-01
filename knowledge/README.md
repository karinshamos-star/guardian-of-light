# Guardian Knowledge Platform

This directory is Guardian's canonical knowledge source. Notion (or any other
tool) is an *authoring adapter* that produces files here — it is not itself
the source of truth, and the build pipeline never reads from it directly.

## How this is built

```
Authoring (Notion, or any adapter)
       ↓
Structured YAML files (this directory)
       ↓
Validation (guardian_core.knowledge, Pydantic + structural checks)
       ↓
Knowledge Package (compiled/indexed artifact, knowledge/_compiled/)
       ↓
guardian_core
```

Build locally with:

```
python -m guardian_core.knowledge.build --knowledge-root knowledge --out knowledge/_compiled
```

Add `--gate ready_for_ai` to produce the production package: only entities
whose `status` is `ready_for_ai` are included, matching Guardian's rule that
unreviewed content must never reach a user.

## File layout convention

Every entity, with no exceptions, lives at:

```
knowledge/domains/<domain>/<entity_type>s/<slug>.yaml
```

For domain-rooted content this reads naturally, e.g. `domains/tarot/cards/major-00.yaml`
(id `tarot.card.major-00`) or `domains/numerology/numbers/7.yaml` (id `numerology.number.7`).

Cross-cutting entity types (Source, KnowledgeClaim, Concept) use a fixed
`domain` equal to their `entity_type` — e.g. a Source always has
`domain: source, entity_type: source`, living at `domains/source/sources/<slug>.yaml`.
Their ids can drop the redundant middle segment and use the shorter
`{domain}.{slug}` form (e.g. `source.guardian-editorial`, `concept.new-beginnings`)
since the id pattern only requires two or more dot-segments, not exactly three.

An entity's file must live at the path its `domain`/`entity_type`/`id` imply —
the build fails otherwise.

## What belongs in this README vs. content

This file documents *infrastructure*: the pipeline, the file layout, the
validation rules. It intentionally says nothing about what any domain's
entities should contain (how many numerology numbers, what a tarot card's
fields are, which historical source wins a naming disagreement) — those are
content decisions, made and changed independently of this architecture, one
domain and one migration task at a time.

## Entity schema (infrastructure-level, domain-agnostic)

Every entity file has:

- `id`, `domain`, `entity_type`, `name`
- `status`: `draft | needs_review | reviewed | ready_for_ai | deprecated`
- `provenance`: `{ source_ids, confidence, claim_ids }`
- `changelog`: list of `{ version, date, reason, reviewer }`
- `related`: map of relation name -> list of other entity ids
- `tags`: free-form list of strings
- `data`: open payload for whatever fields this domain/entity_type defines

`ready_for_ai` requires `provenance.confidence != unverified` and at least
one changelog entry — content can't be silently promoted to production-ready
without a review trail.
