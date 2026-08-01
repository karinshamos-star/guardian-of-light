# Tarot Editorial Standard

This is the editorial blueprint for every Major and Minor Arcana card
Guardian synthesizes. It defines the **knowledge layers** a card is built
from — not the YAML fields (`CardKnowledge` in
`src/guardian_core/knowledge/domains/tarot.py` already defines those) and
not a source's own structure. The layers are Guardian's; the same six
apply to every card regardless of which sources happen to inform it,
matching the general principle in `synthesis/README.md` that canonical
knowledge is never a transcription of any single author's work.

Each layer below has its own **sourcing rule** — that rule is what makes
the layer belong to Guardian rather than to whichever source fills it in
for a given card. When writing a card's synthesis document, work through
these six layers in order; a layer with nothing to draw on stays thin or
notes the gap, it is never padded or invented.

## The six layers

### 1. Structural Identity

What the card objectively *is*: arcana, suit/rank, position/number in the
deck, and its place in documented sequence (e.g. which stage of the
Fool's Journey a Major Arcana card belongs to; a pip card's place in its
suit's 1-10 progression).

- **Sourcing rule:** must be verifiable. Where sources disagree (card
  numbering history is a real example), state the documented version and
  note the disagreement — never silently prefer the more colorful claim
  over the cited one.
- **Registered sources that feed this layer:**
  `source.tarot-numerology-kabbalah-symbolism-guide` (cites the actual
  historian Michael Dummett, and documents A.E. Waite's real 1909
  Rider-Waite-Smith redesign) — currently the only source with citable
  structural/historical claims. Its `sources/numerology/`-filed duplicate,
  `source.numerology-kabbalah-tarot-synergy-guide`, carries the same
  content.
- **Typical `provenance.confidence`:** `secondary` (documented history,
  not Guardian's own claim) where a specific citable fact is used;
  `interpretive` for structural framing Guardian adds itself (e.g.
  deciding how to describe a pip card's progression stage in Guardian's
  own words).

### 2. Symbolic Language

What is visually depicted on the card — figures, objects, gestures,
setting, color — described plainly, **before** any interpretation is
attached. This layer answers "what do we see," not "what does it mean";
that separation is deliberate, so Layer 3 has something concrete to
interpret rather than jumping straight to meaning.

- **Sourcing rule:** describe only imagery that is actually standard for
  the deck tradition being described — nothing invented or embellished.
  **Working assumption, stated explicitly here rather than left implicit:**
  Guardian describes standard **Rider-Waite-Smith** imagery, since every
  currently registered source orients around that tradition (the Synergy
  guide explicitly frames the 1909 RWS deck as the reference point). If
  Guardian ever supports a different deck tradition, that's a scope
  decision to make explicitly, not something this layer should drift into
  silently.
- **Registered sources that feed this layer:** none. No source in
  `sources/tarot/` catalogs card imagery directly — they're interpretive
  and historical texts, not visual references. This layer currently draws
  on Guardian's own established RWS-imagery literacy (the same kind of
  general tradition-knowledge that produced `tarot.card.major-00`
  editorially). Worth registering a dedicated imagery reference source if
  one becomes available; until then, this is a known gap, not a silent
  one.
- **Typical `provenance.confidence`:** `unverified` or `interpretive`
  until a citable imagery reference is registered.

### 3. Canonical Meaning

Guardian's own defined interpretation of the card — light, shadow, and
reversed expression. This is **not** a claim about what most sources or
traditions agree on. It's Guardian's authored position, informed by
whatever traditions are available, but not a survey result and not
required to average or pick a majority view across sources.

- **Sourcing rule:** write it as Guardian's own editorial voice. When more
  than one source or lens bears on a card, let them inform the judgment
  call; don't average them into a flattened blend, and don't caveat every
  sentence with "according to tradition X." This layer is where the
  `synthesis/` stage does its real work — see `synthesis/README.md`'s
  "Guardian's synthesized understanding" section.
- **Registered sources that feed this layer:** no single registered
  source gives Guardian a clean baseline meaning to build from — that gap
  was already flagged when the tarot sources were classified. Any of the
  four tarot sources may inform this layer's judgment call where they're
  actually relevant to the specific card, but none of them *is* this
  layer.
- **Typical `provenance.confidence`:** `interpretive`, essentially always
  — by construction, this layer is Guardian's authored synthesis, not a
  transcribed or cited claim.

### 4. Interpretive Lenses

Named, explicitly attributed perspectives that add depth beyond the
canonical meaning: psychological/archetypal, esoteric-symbolic
(Kabbalistic/astrological), numerological. Each lens stays **labeled as a
lens** in the synthesis document — "in the psychological reading..." —
never folded into Layer 3's voice as if it were the one true meaning.

- **Sourcing rule:** optional, per card, per lens. Omit a lens entirely
  if nothing informs it for this specific card — never invent one to fill
  a gap. A lens's own proprietary vocabulary or renaming stays attributed
  to that lens; it never becomes Guardian's default term for the card.
- **Registered sources that feed this layer:**
  - *Psychological/Jungian* — `source.tarot-psychology-shadow-work-guide`.
    Use the archetypal/shadow-work insight; exclude its uncited origin
    story and its proprietary card-renaming (Devil→Adversity etc.) — see
    that source's `notes` for the full caveat.
  - *Esoteric/symbolic* — `source.tarot-numerology-kabbalah-symbolism-guide`.
    Present as "in the Kabbalistic/esoteric tradition...", never as fact.
  - *Numerological* — `source.tarot-numerological-number-cards-guide` /
    `source.numerology-number-cards-1-9-guide` (Roytal Cohen's method).
    Mainly relevant to numbered Minor Arcana pip cards 1-9; the Synergy
    guide's own Pythagorean number-reduction groupings also touch Major
    Arcana and may be more relevant there.
- **Typical `provenance.confidence`:** `interpretive` (Guardian's
  presentation of the lens) informed by `secondary` source material.

### 5. Lived Application

Translating everything above into concrete, present-day situations:
love, work, money, decision, growth.

- **Sourcing rule:** always Guardian's own synthesis. None of the
  registered sources write this content directly — nobody hands Guardian
  "here's what this card means for a decision you're facing today." This
  layer can never legitimately carry a `primary` or `secondary` source
  citation; it's synthesis by construction, not just by policy.
- **Registered sources that feed this layer:** none, by design.
- **Typical `provenance.confidence`:** `interpretive`.

### 6. Guardian Voice

The actual words said to a person: reflection questions, grounded
actions, safety notes.

- **Sourcing rule:** always original — the highest bar of the six layers.
  This is the layer that faces the user directly, so "not a transcription"
  isn't a nice-to-have here, it's the entire point. Safety notes in
  particular must be Guardian's own judgment about what could go wrong if
  this card's meaning were taken the wrong way — never copied from a
  source's own advice-giving language, since sources don't share
  Guardian's safety obligations.
- **Registered sources that feed this layer:** none, by design.
- **Typical `provenance.confidence`:** `interpretive`.

## Explicitly out of scope: Relational/Combinatorial knowledge

`source.tarot-card-combinations-ellershaw`'s elemental-dignities material
— how a card behaves next to other cards in a spread — does not feed any
of the six layers above. It's not a property of a single card, so it
doesn't belong on a single `CardKnowledge` entity. It's a different kind
of knowledge (spread/combination-shaped), out of scope until Guardian
builds spread-reading as a feature. Flagged here so it isn't quietly
dropped, not proposed as a seventh layer.

## Applying this to Minor Arcana, not just Major

The six layers apply the same way to Minor Arcana (pip and court cards);
only what fills them shifts:

- Layer 1 additionally covers the pip's position within its suit's 1-10
  progression (or a court card's rank).
- Layer 4's numerological lens becomes more central for pip cards than
  for Major Arcana, since that's what `source.numerology-number-cards-1-9-guide`
  actually speaks to.
- Court cards currently have no registered source touching them
  specifically — same "known gap, not silent gap" treatment as Layers 2
  and 3 applies.

## Relationship to the compiled schema

For reference only — this model doesn't define or constrain the schema:

| Layer | Rough `CardKnowledge` field(s) |
|---|---|
| 1. Structural Identity | `arcana`, `suit`, `rank`, `name_he` |
| 2. Symbolic Language | not currently a distinct field — informs `core_essence` |
| 3. Canonical Meaning | `core_essence`, `light_expression`, `shadow_expression`, `reversed_expression` |
| 4. Interpretive Lenses | `dimensions` (emotional/mental/relational/practical/spiritual) |
| 5. Lived Application | `contexts` (love/work/money/decision/growth) |
| 6. Guardian Voice | `reflection_questions`, `grounded_actions`, `safety_notes` |

Layer 2 (Symbolic Language) has no dedicated field today — whether it
needs one, or stays folded into how `core_essence` gets written, is a
schema question for later, not something this document decides.
