# Editorial Synthesis

**Principle: Guardian's canonical knowledge is never a transcription of any
single author's work.** External books, PDFs, and courses are research
sources — inputs to Guardian's own understanding, not content Guardian
republishes. This directory is the stage where that understanding gets
written down, in Guardian's own voice, before it becomes canonical YAML.

```
sources/<file>                                          (raw, local, untracked)
      ↓  analysis (per source — see extraction/README.md)
extraction/<domain>/<entity_type>/<slug>.md              (what the source(s) say)
      ↓  editorial synthesis (this directory)
synthesis/<domain>/<entity_type>/<slug>.md               (Guardian's own understanding)
      ↓  review + mechanical compile
knowledge/domains/<domain>/<entity_type>s/<slug>.yaml    (canonical — unchanged from here)
      ↓  build_corpus() validation → Knowledge Package → guardian_core
```

## Why this is a separate stage from extraction

Extraction and synthesis get reviewed against different questions, and
collapsing them into one document muddles both checks:

- Extraction review asks: *does this accurately represent what the
  source(s) say?*
- Synthesis review asks: *is this genuinely Guardian's own reasoned
  understanding — safe, coherent, in Guardian's voice — rather than one
  source's framework or wording with the serial numbers filed off?*

An extraction document may still contain a "Proposed Guardian
interpretation" section (see `extraction/README.md`) — that's the analyst's
first-pass reaction while reading *one* source, kept there because it's
useful context. It is not the canonical synthesis. The deliberate,
cross-source, this-is-what-Guardian-actually-teaches version is written
here, and only what's written here ever gets compiled into `knowledge/`.

## Multiple sources, one synthesis

When more than one extraction document exists for the same `target_id`,
synthesis is where they get reconciled — not by picking one source and
discarding the rest, but by writing Guardian's own account informed by all
of them. A single-source `target_id` is fine (most will be, at this
content scale); what's required either way is that the canonical fields
represent Guardian's own reasoning, not a paraphrase of one document's
specific structure or terminology.

## Document format

Frontmatter:

```yaml
target_id: numerology.number.1
extraction_refs:
  - extraction/numerology/number/1.md   # list — one entry per contributing extraction doc
synthesis_status: draft   # draft | reviewed
reviewer: null
reviewed_date: null
```

Body — four sections, in this order:

1. **Guardian's synthesized understanding** — written fresh, organized by
   the canonical fields the target schema actually needs (e.g. for a
   `NumberKnowledge`: essence, supporting_frequency, blocking_frequency,
   guardian_guidance), not by source. Nothing here should be a close
   paraphrase of a single extraction document's wording.
2. **Cross-source notes** — where multiple sources exist: where they
   agree, where they conflict, and which framing Guardian chose and why.
   Empty/omitted when only one source informed this entity.
3. **Departures from source language** — anywhere Guardian deliberately
   uses different terms or framing than a source's own branded system
   (e.g. renaming a proprietary term into Guardian's general vocabulary),
   and why. This is the concrete, checkable evidence that synthesis
   happened rather than transcription.
4. **Safety / fit for Guardian's voice** — does this read as reflective
   and non-prescriptive, consistent with how Guardian talks elsewhere
   (mirrors the `safety_notes` field already used on `CardKnowledge`).

## Review

Checks: is this genuinely synthesized rather than reworded from a single
extraction document, safe and in-voice, and — when only one source
informed it — is that honestly reflected in the compiled entity's
`provenance.confidence` (usually `interpretive`, not `primary`, in that
case)?

## Compiling to YAML

Once `synthesis_status: reviewed`, a human transcribes the finalized
content into `knowledge/domains/<domain>/<entity_type>s/<slug>.yaml`, same
as before (manual, mechanical — see `extraction/README.md`). One change
from the earlier version of this pipeline: `provenance.source_ids` on the
compiled entity should list every source that contributed across all
`extraction_refs` cited in the synthesis document, not just one.
