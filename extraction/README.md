# Extraction Workspace

This directory is the intermediate authoring workspace between raw source
material and Guardian's canonical knowledge. Nobody — human or AI — authors
`knowledge/**/*.yaml` directly from a source. Instead, analysis happens here
first, gets reviewed, and only reviewed extraction documents are transcribed
into canonical YAML.

```
sources_raw/<file>                                     (immutable reference material)
      ↓  analysis
extraction/<domain>/<entity_type>/<slug>.md             (this directory)
      ↓  human review
knowledge/domains/<domain>/<entity_type>s/<slug>.yaml   (manual, mechanical transcription)
      ↓  build_corpus() validation → Knowledge Package → guardian_core
```

Extraction documents are not schema-validated the way `knowledge/` YAML is —
that looseness is intentional. This is where interpretive judgment happens,
before it's forced into the canonical entity shape.

## What belongs here

An extraction document describes **what is in the source** — it is strictly
source-oriented and must never become a second knowledge base. If a document
starts accumulating polished, freestanding content that could ship on its
own, that content belongs in `knowledge/`, reached through the normal review
and status-gating pipeline, not left to live here instead.

Guardian's own interpretation is always allowed, but must be explicitly
separated from what the source actually says — never blended into the same
sentence or paragraph as a quote or paraphrase.

## File layout

```
extraction/<domain>/<entity_type>/<slug>.md
```

Mirrors `knowledge/domains/<domain>/<entity_type>s/<slug>.yaml`'s layout
(singular directory here vs. pluralized `s` there is the only difference),
so a given entity's extraction doc and compiled YAML are easy to pair up by
eye.

## Document format

Frontmatter:

```yaml
target_id: tarot.card.major-01
source_refs:
  - path: sources_raw/<file>
    location: "p. 42"   # page, section, chapter, timestamp -- whatever locates it
extraction_status: draft   # draft | reviewed
reviewer: null              # filled in when status moves to reviewed
reviewed_date: null
```

Body — four explicit sections, in this order, every time:

1. **Direct quotes** — verbatim text from the source, quoted, with enough
   location detail (already covered by `source_refs`, repeat inline if a
   single document draws from multiple locations) to trace it back.
2. **Source-derived paraphrase** — the source's content in Guardian's own
   words, without adding meaning the source doesn't contain. A restatement,
   not an extension.
3. **Proposed Guardian interpretation** — Guardian's own reading, framing,
   or application of the source material. Anything that goes beyond what
   the source says belongs here, never in section 1 or 2.
4. **Open questions / unresolved decisions** — anything uncertain enough
   that it should not yet be transcribed into canonical YAML: ambiguous
   source wording, conflicting sources, missing information, judgment
   calls that need a second opinion.

An entity should not move to `extraction_status: reviewed` while it still
has open questions that bear on the fields being compiled.

## Review

Review here checks one thing: **fidelity to the source** — do the quotes,
paraphrase, and interpretation accurately and honestly represent what the
source material says, with Guardian's own voice clearly marked as such?
This is a different check than the `ready_for_ai` gate applied later in
`knowledge/` (which asks whether the compiled entity is complete, safe, and
fit to reach users) — both gates are kept, because they check different
things.

## Compiling to YAML

Once `extraction_status: reviewed`, a human transcribes the finalized
content into `knowledge/domains/<domain>/<entity_type>s/<slug>.yaml` by
hand. Nothing is decided at this step — every value transcribed should
already be settled in the extraction document. The compiled entity starts
at `status: draft` in the normal `knowledge/` lifecycle and proceeds through
the existing review gates from there. `provenance.source_ids` on the
compiled entity should reference the same `Source` entity the extraction
document's `source_refs` point at.

This step is manual for now. Scripting it is deferred until the same
transcription pattern repeats often enough to justify the infrastructure.
