# Guardian Core Experience Flow v1

**First meaningful guidance encounter — every major decision point, branch, pause, return, rejection, save/no-save choice, and edge state.**

Status: **Working draft, Product Design Sprint 1 — Revision 2.** Not yet approved. No screens designed. Does not rename the product or reopen the product vision.

**Approval order for this revision (Karina's instruction):** Crisis Routing → QUESTION → READING → REFLECTION → Closure/Continuity. Sections below are ordered to match.

## Revision 2 — decisions incorporated

Karina reviewed the UX Review artifact and issued nine directives. Each is marked **[Decision — incorporated]** at the point it's addressed below; the *specific mechanics* used to satisfy each directive are new design work and are separately marked **[Recommendation — needs your approval]**, since the directive and the implementation of the directive are not the same thing.

1. Split Crisis Routing by type and risk level, with false-positive recovery — self-harm, abuse, and immediate danger are not the same path. → §2 (new major section, moved ahead of QUESTION).
2. Time-to-Value audit of the six pre-QUESTION states — no `WorldState` deleted, but each classified as action-required / continuous-short-passthrough / first-session-only. → §1.3 (new).
3. Move depth selection to after the question is focused, or make it a changeable Guardian suggestion. → §3.2 (moved out of `READING_ROOM`, now in `READING`).
4. On predictive questions, Guardian must not proceed as if answering the original question — it must state the boundary and offer an agency-based frame; the user continues in that frame or ends. → §3.1.
5. Split `REFLECTION` into three beats: Resonance → Desired next step → Integration (only when appropriate). → §4.
6. Remove "want to go deeper" from the resonance response set. → §4.1.
7. After "this doesn't connect," do not auto-offer an alternative interpretation — offer closure, a context-check, or transparency about the interpretation's source instead. → §4.1.
8. Separate `RETURN_TO_LIBRARY` from opening a new encounter — returning to Lumina must allow real closure. → §5.1.
9. Replace "Guardian never blocks access" with a pacing mechanism that redirects compulsive repeated-seeking toward Reflection or Pause. → §5.3.

---

## 0. How this maps onto what already exists

This flow is **not a replacement** for the illustrated-world product already defined in `VISION.md` and already partially implemented as the `WorldSession` state machine (`src/guardian_core/experience/session.py`). It is the missing detail layer on top of it.

The experiential layers map onto the concrete, already-built `WorldState` sequence like this:

| Experiential layer | Concrete `WorldState`(s) | Status |
|---|---|---|
| **Arrival** | `ARRIVAL → AVATAR_SELECTION → LIBRARY_ENTRANCE → GUIDE_GREETING` | Implemented; Time-to-Value audit in §1.3 reclassifies some of these beats |
| **Guidance** | `GUIDE_GREETING → SECRET_DOOR → READING_ROOM → QUESTION → READING` | Implemented, but `QUESTION`/`READING` currently have no branching (see gaps below) |
| **Reflection** | `REFLECTION`, internally split into three beats (§4): Resonance → Desired next step → Integration | Implemented today as a single generic beat only |
| **Continuity** | `RETURN_TO_LIBRARY → GUIDE_GREETING` (loop) + cross-session memory | Loop exists structurally; §5.1 now requires the loop's *first* landing to read as closure, not as a new-encounter on-ramp |

No new `WorldState` is proposed anywhere in this document, including in this revision — every branch, including the crisis-routing split, fits inside the existing ten states via richer `interaction` options, `payload` data, and guide dialogue variation, consistent with `PROJECT_STATE.md`'s standing rule against adding new states for onboarding or clarification-like purposes.

### Implementation gaps this design surfaces (not fixed here — flagged per handoff rule 7)

These are named because the flow below depends on them, not because this is a request to build them now:

1. **Crisis routing has no runtime status yet, and today it would treat all crisis signals identically even if it existed — and the detection underneath it is itself a P0 launch blocker.** `intent/engine.py` already detects `SELF_HARM_OR_SUICIDE`, `ABUSE_OR_COERCION`, and `IMMEDIATE_DANGER` as `SafetyFlag`s and currently groups all three into one `crisis` set (`clarification_for()`), but `ReadingResult.status` today only has two values (`completed`, `clarification_required`) — there is no status the orchestrator can return to stop and reroute at all, let alone three differentiated ones. Separately and more urgently: `detect_safety()` is exact-substring matching with no negation or context handling (confirmed while designing §2.1 — "אני **לא** בסכנה עכשיו" matches `IMMEDIATE_DANGER` today). **This product must not launch with safety detection in this state**, regardless of how good the UX design around it is — recovery UX mitigates the user experience of a false positive, it does not fix the underlying miss rate or false-negative risk. §2 designs three differentiated UX tracks; the flag-grouping in `intent/engine.py` and the detection logic itself both need dedicated engineering work, tracked as launch blockers, once this section is fully approved.
2. **No returning-user distinction exists in `WorldSession`.** Every session starts cold at `ARRIVAL`. This flow's new-vs-returning fork (§1.1) and the closure-vs-new-encounter separation (§5.1) are written as intended behavior once a persisted profile/session-history layer exists; it does not exist yet.
3. **`REFLECTION` is currently a single `CONTINUE` button.** §4's three-beat redesign (Resonance / Desired next step / Integration) is new interaction content within that state, not yet built.

---

## 1. Arrival & setup — `ARRIVAL → AVATAR_SELECTION → LIBRARY_ENTRANCE → GUIDE_GREETING → SECRET_DOOR → READING_ROOM`

### 1.1 New vs. returning

Before `ARRIVAL`'s command is generated, the system silently checks: does this session_id/user have prior saved journey data?

**New user**
1. *User state:* curious, cautious, or in some emotional need; no prior relationship with Guardian.
2. *Guardian responsibility:* let the world be already present — no onboarding form, no tutorial overlay. Per `VISION.md`, "the world is already there before they speak."
3. *User decision:* `CONTINUE` → `begin`.
4. *System response:* current `ARRIVAL` dialogue ("המסע שלך יכול להתחיל עכשיו") stands as-is → `AVATAR_SELECTION`.
5. *Risk:* if avatar selection reads as a game character-creation screen, it undercuts "a place," turning it into "an app with a profile step." Avatar choice should be framed as *how you want to be met*, not a cosmetic pick.
6. *Exit:* closing the tab here costs nothing — no state was saved yet.

**Returning user** *(depends on gap #2 above)*
1. *User state:* already has a relationship with Lumina and the space; may be returning with lived experience from a previous intention.
2. *Guardian responsibility:* skip `AVATAR_SELECTION` (per §1.3's audit) and go straight to a `GUIDE_GREETING` that acknowledges continuity — never re-run onboarding on someone who's been here before.
3. *User decision:* `CONTINUE` from `ARRIVAL` (or a shortened arrival) → directly into `GUIDE_GREETING`.
4. *System response:* Lumina's greeting differs from the cold-open line — it should reference that time has passed and, if the user has an open intention (§4.2's Integration output), *offer* to revisit it without insisting.
5. *Risk:* referencing a past encounter incorrectly, too specifically, or too soon feels surveilled rather than remembered. Reference themes the user chose to save, never raw inferred data.
6. *Exit:* user can decline the callback and proceed as if starting fresh (§5.2, "healthy continuation").

### 1.2 The guidance-setup ritual

1. *User state:* has entered the space; may still be deciding whether to actually voice what they came with.
2. *Guardian responsibility:* hold the transition — this sequence is a physical/spatial ritual (walk to the bookshelf, open the secret passage) that gives the user time to arrive emotionally before being asked anything. This *is* the "safety and focus" beat of the emotional arc, not filler.
3. *User decision:* `TALK_TO_GUIDE` → `FOLLOW_GUIDE` → `ENTER_SECRET_ROOM` — all low-stakes `CONTINUE`/`FOLLOW_GUIDE`-type interactions, no content decisions yet.
4. *System response:* existing dialogue and camera/animation cues stand, subject to the pacing changes in §1.3.
5. *Risk:* if this sequence is skippable or feels like a loading screen, it collapses into exactly the "chatbot with good content" failure mode `VISION.md` ranks against. It must not be able to be rushed past without at least the minimum ritual beats playing once per relationship (see §1.3's first-session-only classification).
6. *Exit:* user can back out at any point before `QUESTION` with no data committed — no question has been asked yet, nothing to discard.

### 1.3 Time-to-Value audit of the six pre-`QUESTION` states

**[Decision — incorporated]** No `WorldState` is removed. Each of the six states between `ARRIVAL` and `QUESTION` is classified below by whether it needs a deliberate user action every time, or can compress once the ritual meaning it's building has already been established.

| `WorldState` | Today | Classification | Rationale |
|---|---|---|---|
| `ARRIVAL` | Requires `begin` | **Action-required, every session** | One tap, sets the tone of "this begins when I say so." Low friction; no reason to remove it even for returning users. |
| `AVATAR_SELECTION` | Requires `choose_avatar` | **First-session-only** | The choice itself (*how do I want to be met*) is meaningful once. Repeating it on every return has no narrative payoff and directly blocks the returning-user path in §1.1. |
| `LIBRARY_ENTRANCE` | Requires `enter_library` | **Continuous-short passthrough** | The content here is atmospheric (the doors opening), not a decision. The visual/audio beat can still play in full; what changes is that it doesn't need to *wait* on a tap — it can auto-advance into `GUIDE_GREETING` after its own duration. |
| `GUIDE_GREETING` | Requires `talk_to_guide` | **Action-required, every session** | This is the emotional anchor of the whole Arrival layer — meeting Lumina. Must stay deliberate. Never a passthrough, regardless of session count. |
| `SECRET_DOOR` | Requires `follow_guide` | **First-session-only ritual, then continuous-short passthrough** | Building the "there is a quieter place we go to" feeling matters the first several times. Past that point (exact threshold below is open), it can compress the same way `LIBRARY_ENTRANCE` does. |
| `READING_ROOM` | Requires `enter_secret_room` | **Continuous-short passthrough** | Purely transitional once depth-selection moves out of it (§3.2) — nothing decision-bearing happens here anymore. |

**[Recommendation — needs your approval]**
- The exact session-count or time threshold at which `SECRET_DOOR` shifts from full ritual to passthrough is undefined — proposing "after the 3rd completed encounter" as a starting number, not a final one.
- Whether "passthrough" means auto-advancing after a fixed duration, or still rendering a `CONTINUE` affordance that simply isn't required to be pressed (auto-advances if ignored) — the latter preserves user control for anyone who wants to linger.
- These classifications assume gap #2 (returning-user persistence) is resolved; until then, every session is necessarily treated as new-user pacing.

### 1.4 Depth framing — moved

Depth selection previously lived here, at `READING_ROOM`. **[Decision — incorporated]** it has moved to after the question is focused — see §3.2. `READING_ROOM` no longer carries any content decision, which is what makes its passthrough classification in §1.3 possible.

---

## 2. Crisis Routing — split by type and risk level

**[Decision — incorporated]** Self-harm/suicide risk, abuse/coercion disclosure, and immediate physical danger are three different situations with three different appropriate responses. Treating them as one `crisis` bucket (as `intent/engine.py` currently does) either over-reacts to a disclosure that needed to be *heard*, or under-reacts to a signal that needed an instant, unambiguous stop. All three tracks below still fit inside the existing `QUESTION`/`READING` states — none requires a new `WorldState`; what differs is which dialogue/interaction content each track returns and whether `READING` fires at all.

Nothing below is implemented yet (gap #1). This section defines the intended behavior so it can be approved before any of it is built or before screens are designed around it.

### 2.1 Immediate danger (`SafetyFlag.IMMEDIATE_DANGER`)

**Status: Approved direction — provisional until safety detection and professional/legal review are completed.**

- **Trigger, and a hard limit on today's confidence:** `detect_safety()` matches three exact Hebrew substrings ("בסכנה עכשיו", "עומד לפגוע בי", "נשק") with no negation or context handling. There is no graded confidence today — only presence/absence of a substring. **This is marked a P0 launch blocker**, not an ordinary gap: a safety-critical product must not ship detection that reads "אני **לא** בסכנה עכשיו" as a positive match. The recovery mechanism below exists to handle the false positives this causes today, but it is explicitly **not a substitute** for fixing the detection itself before launch — see the strengthened gap in §0.
- **Explicit vs. ambiguous input:**
  - *Explicit:* "אני בסכנה עכשיו, הוא כאן ויש לו נשק" — multiple terms co-occurring, very likely genuine.
  - *False-positive the current code guarantees:* "אני **לא** בסכנה עכשיו, פשוט מפחדת מהעתיד" — the negated sentence still contains the trigger substring and fires today.
- **No clarifying question, ever, at this tier.** Given the possibility of genuine immediate danger, the emergency-resource content and the false-positive recovery affordance are presented **simultaneously**, in the same response — never gated behind a question the user has to answer first, and never sequenced so that help appears only after some check passes.
- **Sequence from the moment of detection:**
  1. User submits the question in `QUESTION` (`ask_question`).
  2. `IMMEDIATE_DANGER` is detected. `READING` never fires — no draw, no spiritual framing of any kind.
  3. The very next response already contains, together: (a) the safety message and location-appropriate emergency resources, and (b) the false-positive recovery affordance. Guide emotion/animation shifts to present-and-serious; no dramatic transition, no alarming sound, no scene change, no notification or title anywhere in the client that could expose what's on screen to someone nearby.
  4. From here, exactly two paths: engage with the emergency resources / leave discreetly (§ below), or use the recovery affordance (§ below) — nothing else is offered.
- **Lumina's text (approved direction, illustrative wording still subject to final legal/clinical sign-off):**
  > "אני עוצרת את הקריאה. הבטיחות שלך קודמת לכל מה שנעשה כאן. אם קיימת סכנה מיידית, פני עכשיו לשירותי החירום באזור שלך."

  "אני כאן" was removed deliberately — it implies human presence or real-time monitoring that does not exist and must never be implied.
- **Actions shown, in hierarchy:**
  1. **Primary:** location-appropriate emergency services. In Israel: Police **100**; medical emergency (MDA) **101**. *These numbers, and any geolocation logic behind choosing which to show, must pass professional and legal review before shipping — they are not production-ready as written.*
  2. **Secondary, equally visible, never subordinate to a "declare you're fine" framing:** "זה לא מתאר את המצב שלי" — see recovery below. The user is never required to assert she's "fine" to exit a misdetection; the option only asserts that the detected description doesn't match her situation.
  3. **Always available, discreet:** leave immediately — no dramatic animation, no sound, no confirmation dialog, no notification, and no on-screen title or label that could reveal to someone else what was happening. This exit must be as fast and unremarkable as leaving any ordinary screen.
- **False-positive recovery — revised:** selecting "זה לא מתאר את המצב שלי" does **not** auto-resubmit the original question text, because the same substring will deterministically re-trigger the identical flag. Instead, exactly two options are offered: **rephrase** the question, or **continue via a contextual override** — an explicit, one-time confirmation scoped only to that specific sentence, for the current session only. The override never generalizes to future messages.
- **No suppression of future alerts:** if any new or more explicit danger signal appears later in the same session — including a stronger restatement of something already dismissed as a false positive — the safety path fires again in full. A prior dismissal never lowers sensitivity for what comes after it.
- **Return to the ordinary flow:** only after the recovery path above completes (rephrase, or scoped override). If the user instead engages with emergency resources or simply leaves, the ordinary reading flow does not resume in that session. No account-level lockout of any kind.
- **What is retained:** the triggering question's content is never saved into the user's personal journey/library — the ordinary Integration save mechanism never applies here, since `READING`/`REFLECTION` never fire on this path. Whether any safety-related telemetry exists at all (even de-identified) is explicitly **not decided here** — it is deferred to a separate specification governed by data minimization, anonymization, bounded retention, and legal review before any such telemetry is built.
- **Open decisions still requiring approval:** the exact emergency numbers/resources and any location logic (pending legal/professional review); whether a session-scoped memory of a prior override should exist at all beyond what's described above; the final clinical/legal wording of Lumina's message and of the resource content itself.

### 2.2 Self-harm / suicide risk (`SafetyFlag.SELF_HARM_OR_SUICIDE`)

- **User state:** often disclosed with more ambiguity than immediate danger — may be a present risk, a past experience being referenced, or figurative language that misfired.
- **Guardian responsibility:** step out of the pure reading frame, but not necessarily as abruptly as §2.1 — ask one direct, caring question before assuming the worst-case interpretation, rather than jumping straight to resources-only.
- **System response:** Lumina asks, plainly and without alarm, whether the person is safe right now. If yes → offer a reflective, non-tarot conversation as a middle path (not straight back into the original predictive/reading framing, but not resources-only either). If no or unclear → escalates to the same resource-first response as §2.1.
- **Trust/emotional risk:** treating every mention of self-harm-adjacent language as maximum emergency (over-triggering) teaches users to phrase things less honestly next time. Under-triggering is the opposite, worse failure.
- **False-positive recovery:** built into the design itself via the clarifying question — this track doesn't need a separate recovery step because it doesn't assume crisis before asking.

### 2.3 Abuse / coercion disclosure (`SafetyFlag.ABUSE_OR_COERCION`)

- **User state:** disclosing an ongoing relational situation — not necessarily in acute personal danger *right now* (if it is, `IMMEDIATE_DANGER` should also be firing concurrently, routing to §2.1).
- **Guardian responsibility:** this is **not** a hard stop the way §2.1 is. Guardian must not attempt to advise on the relationship, predict the other person's behavior (overlaps with `THIRD_PARTY_MIND_READING`), or run an ordinary tarot flow framed around "will they change." But a person disclosing this may specifically want to feel heard, not immediately redirected past that.
- **System response:** Lumina acknowledges and validates directly, surfaces relevant resources without making them the entire response, and offers to continue with a reflective encounter centered on the user's own needs and safety — explicitly not a predictive reading about the other person.
- **Trust/emotional risk:** redirecting too hard, too fast, past the disclosure itself, can feel like being handed a phone number instead of being heard — the opposite failure from §2.1, where speed is exactly right.
- **False-positive recovery:** since this isn't a hard block, recovery is lighter-touch than §2.1 — the user can say "that's not what I meant" and continue without a heavy re-confirmation gate.

**[Recommendation — needs your approval]**
- Whether `DELUSIONAL_OR_PARANOID_FRAMING` and `DEPENDENCY_SEEKING` (both already modeled as `SafetyFlag`s but not discussed in the original handoff) deserve their own tracks here too, or fold into one of the three above — flagging, not deciding.
- The exact clarifying-question wording for §2.2 — illustrative only.
- Whether §2.1's "grounding beat" before recovery is a fixed dialogue pause or something that also depends on how the user responds.

---

## 3. `QUESTION` and `READING`

### 3.1 Focusing the question

The existing `ASK_QUESTION` interaction stays a single free-text field — no pre-world mode-picker, consistent with the earlier reconciliation against handoff §7.

**Clear / unclear / open** (unchanged from Revision 1): clear questions proceed toward `READING`; unclear feelings trigger the existing `clarification_for()` loop with richer in-character copy; open reflection (no specific question) needs a `CoreNeed` value confirmed to exist — still an open engineering question, not resolved here.

**Predictive / certainty-seeking questions — revised.** **[Decision — incorporated]** Guardian must not proceed as if it answered the original predictive question, even with hedged language. Revision 1 allowed the user to restate the original framing and have Guardian "proceed but keep its language non-deterministic" — that option is removed.

1. *User state:* often anxious, seeking certainty ("will they come back?", "what will happen this year?").
2. *Guardian responsibility:* name the boundary directly, then offer the agency-based reframing as the actual frame going forward — not a suggestion alongside the original question, a replacement of it.
3. *User decision:* exactly two options now — continue **within** the reframed, agency-based question, or end the encounter here.
4. *System response:* Lumina states plainly what she can't do ("אני לא יכולה לדעת אם הוא יחזור — זה לא מה שהקלפים כאן בשבילו") immediately followed by the reframed question as the offer ("אבל אפשר להסתכל על מה שהקשר הזה מבקש ממך להבין"). There is no path where the original predictive question gets answered as-is.
5. *Risk:* stated this firmly, the boundary can read as refusal rather than redirection if the reframed question isn't offered in the same breath — the two must arrive together, not boundary-then-silence.
6. *Exit:* ending here is a fully valid, non-penalized outcome — this is a real terminal state, not a soft block the user is expected to push past.

**[Recommendation — needs your approval]** the exact tone of the boundary statement — direct enough to be honest, warm enough not to read as correction. Illustrative wording only.

### 3.2 Depth — moved here, as a changeable suggestion

**[Decision — incorporated]** Depth selection no longer happens blind at `READING_ROOM`, before Guardian knows anything about what the user is bringing. **[Recommendation — needs your approval]** the mechanic proposed to satisfy this:

1. *User state:* has just stated their question; doesn't yet know how long or deep this encounter will run.
2. *Guardian responsibility:* once the question is classified (domain, emotional weight, complexity — all already produced by `intent/engine.py`), Lumina suggests a depth rather than asking the user to pre-commit blind: *"זה נשמע כמו משהו שכדאי לתת לו קצת יותר זמן — רוצה שנעמיק, או שתעדיפי רגע קצר וברור?"*
3. *User decision:* accept the suggested depth, or switch it — a lightweight `choose_option`, not a gate.
4. *System response:* depth is carried in `payload` through to `READING` exactly as in Revision 1; only the timing and framing changed — it's Guardian's read of the situation, offered for confirmation, not a blind menu.
5. *Risk:* if the suggestion is wrong often enough, it reads as Guardian not listening — the "switch it" affordance has to be genuinely easy, not buried.
6. *Exit:* skipping the suggestion defaults to the shorter form, same as Revision 1's default.

### 3.3 Revealing the guidance — `READING`

Unchanged from Revision 1's layered structure:

1. **Essence** — the central idea, one sentence, surfaced first.
2. **Perspective** — the specific symbol/card/calculation, framed explicitly as invitation not prophecy.
3. **Synthesis** *(only when genuinely useful — currently a placeholder, only Tarot is `ready_for_ai` today)*.
4. **Optional depth** — available on request, not forced.

*Trust/emotional risk:* presenting synthesis when only one tradition genuinely applies remains the named failure mode to guard against.

*Exit/recovery:* the existing clarification self-loop (`READING → READING`) remains the recovery path.

---

## 4. `REFLECTION` — three beats

**[Decision — incorporated]** `REFLECTION` splits into three sequential beats instead of Revision 1's two. None of this is a new `WorldState` — all three beats render within the existing `REFLECTION` state, and only the third beat's completion (or an early exit from beat 2) fires the `REFLECT` action toward `RETURN_TO_LIBRARY`.

### 4.1 Beat 1 — Resonance

`CHOOSE_OPTION` interaction, now **four** responses — "want to go deeper" is removed per Karina's instruction (going deeper isn't a statement about whether something resonated; it now lives in Beat 2 where it belongs as a direction, not a judgment).

| Response | Guardian's next move |
|---|---|
| **"זה מרגיש נכון" (this feels accurate)** | Brief affirmation, without over-praising accuracy. → Beat 2. |
| **"חלק מזה מרגיש נכון" (part of this)** | Gently, optionally asks *which* part — accepts a non-answer just as readily. → Beat 2. |
| **"זה לא מתחבר" (this doesn't feel connected)** — **revised** | See below — no automatic alternative interpretation. → Beat 2, but Beat 2's options differ for this branch. |
| **"אני צריכה זמן עם זה" (I need time)** | Valid terminal-leaning response — Beat 2 for this branch defaults toward closing with "hold a question," not toward further exploration. |

**"Doesn't connect" — revised handling.** **[Decision — incorporated]** Revision 1 offered "a different angle on the same question" automatically. That's removed. Instead, three options, all still user-chosen, none defaulted:

- **Close** — end without forcing further interpretation.
- **Context-check** — Lumina asks whether something about the question or situation was misunderstood going in, rather than guessing at a new interpretation herself.
- **Transparency about the interpretation's source** — Lumina names plainly which card/symbol/source informed what she said, so the user can judge the reasoning rather than receive a second guess.

*Trust/emotional risk (unchanged principle, sharpened by this revision):* the previous "try a different angle" default was itself a subtle way of implying the first interpretation just needed adjusting until it landed — exactly the "argue with rejection" failure mode this section already named. Removing it closes that gap.

### 4.2 Beat 2 — Desired next step

**[Recommendation — needs your approval]** New beat, not present in Revision 1. After Resonance is captured, Lumina asks a coarser-grained question: not *what to save*, but *what the user wants right now*.

1. *User state:* has registered how the reading landed; hasn't yet decided what, if anything, comes next.
2. *Guardian responsibility:* offer a small set of directions rather than jumping straight to the save-menu: sit quietly with this / go deeper into what was raised / close for now. The exact option set should follow from Beat 1's branch — e.g. "doesn't connect → context-check" naturally leads here with different phrasing than "feels accurate."
3. *User decision:* pick a direction.
4. *System response:* "sit quietly" or "close for now" routes to Beat 3 (Integration) only if there's plausibly something to carry — see below. "Go deeper" surfaces `READING`'s optional-depth content (§3.3) on request, then returns to this beat.
5. *Risk:* if this beat feels like a second layer of the same question as Beat 1, it will read as friction, not care — the two must ask genuinely different things (how did it land vs. what do you want now).
6. *Exit:* every direction is valid; none is treated as more complete than another.

### 4.3 Beat 3 — Integration, only when appropriate

**[Decision — incorporated]** Integration is no longer automatic after every Resonance response — it fires only when Beat 2 points toward it (typically "close for now" after a reading that had something worth naming). Paths that resolve toward "I need time" or a context-check that ends in "let's just close" may skip straight to `RETURN_TO_LIBRARY` without an Integration prompt, because forcing "what do you want to carry forward" onto an encounter that didn't land is its own small pressure to manufacture a takeaway.

When it does fire, mechanics are unchanged from Revision 1: sentence / question to hold / something to notice / intention / small action / "not clear yet" / "I don't want to save anything" — equally weighted, no default toward saving. On save, Lumina names back the choice in her own voice; on decline, she closes just as warmly. Either path leads to `RETURN_TO_LIBRARY` with no re-prompt loop.

**Edit/defer** *(still depends on gap #2)*: a saved intention should be editable or dismissible from a later return once persistence exists.

---

## 5. Closure & Continuity — `RETURN_TO_LIBRARY`

### 5.1 Return-to-Lumina is not the same thing as starting a new encounter

**[Decision — incorporated]** In the current transition table, `RETURN` from `RETURN_TO_LIBRARY` lands back on `GUIDE_GREETING` — the same state that begins a new encounter via `TALK_TO_GUIDE` → `SECRET_DOOR`. Structurally that's fine (no new `WorldState` needed), but the *content* Lumina offers there must differ depending on how the user arrived.

**[Recommendation — needs your approval]** — the mechanic proposed:

1. *User state:* has just closed an encounter; may want to genuinely be done, not start something new.
2. *Guardian responsibility:* when `GUIDE_GREETING` is reached via the `RETURN_TO_LIBRARY` loop (same session, recent closure), its dialogue and interaction cue should read as *arrival at rest*, not as the on-ramp to `SECRET_DOOR`. Concretely: the existing "בואי נדבר" / `talk_to_guide` prompt that structurally pulls toward another encounter should not be the only or default affordance here — a neutral option to simply linger or leave should exist alongside it, not be replaced by it.
3. *User decision:* stay at rest and leave whenever, or deliberately choose to begin something new.
4. *System response:* starting something new from this point is still just `talk_to_guide` → `SECRET_DOOR`, exactly as before — nothing is removed. What changes is that it's no longer presented as the *only* next move.
5. *Risk:* if this isn't distinguishable from the ordinary greeting, "closure" is a UX-doc claim with nothing behind it in the actual experience — the whole point of this fix.
6. *Exit:* the "arrival at rest" version of `GUIDE_GREETING` has no forced next action at all — it's a legitimate place to just stop.

This is a content/interaction-cue distinction on the existing `GUIDE_GREETING` state (a "closure variant" vs. a "fresh session" variant of the same state), not a new state — consistent with the standing no-new-`WorldState` rule.

### 5.2 Return after time has passed

Unchanged from Revision 1: if an Integration output was saved (§4.3), a later `GUIDE_GREETING` may offer — never demand — to revisit it. Declining is never tracked as a negative signal. This remains the second-highest trust risk in the flow after crisis handling, per Revision 1's framing.

### 5.3 Healthy vs. compulsive repeated guidance-seeking — pacing, not a soft nudge

**[Decision — incorporated]** Revision 1's "Guardian never blocks access — the intervention is entirely in tone" is replaced. Tone-only was too weak to actually be pacing; it was a principle with no mechanism behind it.

**[Recommendation — needs your approval]** — the mechanic proposed:

1. *User state:* returning very soon after a prior encounter, plausibly seeking a different answer to the same underlying question.
2. *Guardian responsibility:* when this pattern is detected (same or near-duplicate `question` within a short window — exact window undefined, flagged below), the **default path offered is no longer a fresh full reading**. Instead, Lumina's primary offer redirects toward a Reflection-oriented or Pause-oriented encounter — sitting with what already came up, rather than drawing again.
3. *User decision:* accept the redirect (the easy, single-tap path), or explicitly choose to start a brand-new full reading anyway — available, but now a second, deliberate choice rather than the default single path.
4. *System response:* this is genuine pacing, not a lockout — a new reading is never refused if the user insists — but it's no longer offered as if the repeated-seeking pattern weren't visible.
5. *Risk:* this still doesn't fully resolve the tension named in Revision 1 — over-correcting toward friction risks feeling paternalistic; under-correcting brings back the original problem. Making the redirect the *default* rather than a *requirement* is the calibration point, and it's exactly what needs your approval before it's built.
6. *Exit:* always available in both directions — redirect or insist — except where it overlaps with Crisis Routing (§2), which hard-stops for an unrelated, higher-priority reason.

**[Recommendation — needs your approval]**
- The exact detection window/threshold for "returning very soon" — not specified here.
- Whether the "insist on a new reading anyway" path should require a distinct confirmation step, or just a second tap with no added friction beyond the redirect itself.

---

## 6. Open items for the next design pass

- Where exactly `CoreNeed` needs a genuine "open reflection, no decision" value (§3.1) — a content/schema question for engineering, not a UX one.
- All three implementation gaps in §0 (differentiated crisis routing, returning-user persistence, `REFLECTION` branching) should be raised as concrete engineering problems (per `PROJECT_STATE.md`'s reactive-change rule) once this flow is fully approved — not before, and not deferred indefinitely after.
- Cross-tradition synthesis (§3.3) remains a placeholder contract — no real content to test against yet.
- Whether `DELUSIONAL_OR_PARANOID_FRAMING` and `DEPENDENCY_SEEKING` need their own Crisis Routing tracks (§2, open item).
- The `SECRET_DOOR` ritual-to-passthrough threshold and the compulsive-seeking detection window (§1.3, §5.3) are both left as approximate numbers pending your call.
- Exact copy for every Lumina line above remains illustrative, not final — voice/tone pass comes after flow approval.
