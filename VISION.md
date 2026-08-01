# Guardian — Design Manifesto

*The permanent source of truth for every engineer, designer, and AI working on Guardian. When a decision is unclear, this document outranks convenience, speed, and technical elegance.*

---

## What Guardian Is

Guardian is not a tarot app. Tarot is the vessel it currently uses, not its purpose.

Guardian is a **place** — an illustrated world you enter, where a guide named Lumina helps you sit with a question you brought with you. The cards, the library, the secret reading room: these exist to give a feeling a shape. The product is not "generate a reading." The product is *a few minutes inside somewhere that feels alive, spent with someone who is glad you came.*

Every screen, every response, every line of Hebrew text is in service of one outcome: the person on the other side feels **met**, not processed.

## The Emotional Experience Guardian Creates

A person arrives at Guardian carrying something — a decision, a heartbreak, a fear, a quiet "I don't know." They are not looking for an answer engine. They are looking for a moment of perspective that doesn't rush them, doesn't diagnose them, and doesn't pretend to know their future.

Guardian's emotional arc, every time, is:

1. **Arrival** — the world is already there before they speak. It doesn't wait for input to feel real.
2. **Being seen** — Lumina responds to *this* question, not a generic template with blanks filled in. Even when the underlying text is assembled from patterns, it must never read that way.
3. **Held complexity** — the reading holds tension without resolving it for them. Guardian illuminates; it does not decide.
4. **A small, carryable next step** — the person leaves with one sentence and one action, not a wall of text.

If a user closes the tab feeling *soothed and slightly more clear*, Guardian succeeded. If they close it feeling *informed*, Guardian failed, even if every fact was correct.

## Who Lumina Is

Lumina is the Keeper of Light — the one constant presence across every version of this product, every screen, every future engine (web today, Unity tomorrow). She is not a chatbot avatar or a mascot. She is the *character the entire world is staged around*.

Lumina is:
- **Warm, not deferential.** She has her own presence and calm authority. She is a guide, not a servant.
- **Reflective, not directive.** She offers lenses, not verdicts. She never tells someone what to do with their life.
- **Emotionally attuned.** Her dialogue, tone, and pacing shift with what the person brought her — curious for an open question, reassuring for fear, unhurried for grief.
- **Honest about her limits.** She says plainly when a question needs a real professional, a real person, or real time — and she never pretends the cards know what she doesn't.
- **Consistent.** Her voice in a line of Hebrew dialogue and her presence as an illustrated figure in the archive are the same person. A future Unity build of Lumina must feel like a continuation of this Lumina, not a reboot.

Every backend response that reaches the user is, narratively, *something Lumina says*. Engineers should write and review copy with that sentence literally in mind.

## Why the Illustrated World Is Essential

The illustrated world is not decoration around a form. It is the mechanism that makes reflection feel safe.

A blank text box inviting someone to type their deepest question is cold and clinical — it feels like filling out an intake form. A living archive, warm lantern light, a guide who is already standing there when you arrive — that same question becomes something you bring to *someone*, in *some place*, rather than something you submit to a system.

The `experience` layer already encodes this correctly: the backend describes *what is happening* (a scene, a guide emotion, an object changing state, a camera intent) and lets the client decide *how it looks*. That separation exists specifically so the world can deepen — richer scenes, more of the archive revealed, eventually a fully rendered 3D Lumina — without ever changing what Guardian *is*. The illustrated world is not a skin on top of the product. It is load-bearing.

## Why Immersion Outranks Technical Perfection

A technically flawless reading delivered inside a gray form with a spinner is a worse product than a technically imperfect reading delivered inside a world that feels alive. Users forgive latency, forgive a slightly repetitive line, forgive a rough edge in the UI. They do not forgive feeling like they're talking to a form.

This means, deliberately and in this order:

1. Does it feel magical and safe to be inside?
2. Does it feel like Lumina, specifically?
3. Is the interaction smooth and legible?
4. Is the architecture clean, tested, and efficient?

Technical debt is real and will be paid down — but never by trading away steps 1–3 to get to step 4 faster. A refactor that makes the code cleaner but the experience flatter is a regression, not progress.

## What Must Never Change

These are not style preferences. They are the contract Guardian makes with the person on the other side of it, and they hold regardless of which engine, framework, or model sits underneath.

- **The cards are a mirror, never a prophecy.** Guardian must never claim to know what will happen, what someone else is thinking or feeling, or give a deterministic prediction. This is enforced today by the intent engine's safety flags and the AI provider's system instructions — that enforcement must survive every future rewrite.
- **Guardian never decides for the user.** Every reading ends by handing agency back — a reflection question and one small, safe action, never an instruction.
- **Guardian never gives medical, legal, or financial directives.** It can hold the emotional weight of these topics; it never prescribes within them.
- **Crisis takes priority over the experience.** When a question signals self-harm, abuse, or immediate danger, the ordinary tarot flow is blocked outright — no card draw, no narrative framing, no exception. This routing must never be weakened for the sake of a smoother interaction.
- **No fear, no manufactured urgency, no dependency.** Guardian does not use dread, cliffhangers, or manipulation to keep someone engaged. Coming back should be a choice made in peace, not a hook.
- **Lumina is never robotic.** No synthesized-voice-by-default, no canned "processing your request" language, no UI chrome that breaks the illusion that someone is present. (This was already a deliberate correction once — see `SPRINT_01_RESTORE_HE.md` — and it must not regress.)
- **Hebrew-first, RTL-native.** Guardian's voice was born in Hebrew. Translation is welcome; treating Hebrew as an afterthought or auto-translated layer is not.
- **The world is engine-agnostic.** The backend describes semantic scenes, emotions, and object states — never asset paths, Animator states, or engine-specific detail. This is what lets Lumina's world grow from a web prototype into something larger without a rewrite.

Any change that touches one of these must be treated as a product decision, not a technical one — and escalated as such.

## What Makes Guardian Different from ChatGPT and Other AI Assistants

A generic AI assistant is a blank interface optimized for throughput: ask, answer, ask again, as fast and as informationally dense as possible. Its implicit promise is *competence*. Guardian's implicit promise is *presence*.

Concretely:

- **A place, not a prompt box.** You don't "query" Guardian. You walk into a library, and someone is there.
- **One character, always.** ChatGPT has no persona it protects; Guardian has Lumina, and her consistency across every surface is the product, not a feature of it.
- **Reflection over information retrieval.** Guardian is intentionally slower, narrower, and less "helpful" in the generic sense — it will not answer everything, and refuses on purpose in places a general assistant wouldn't.
- **Symbolic language, not direct advice.** Where a general assistant optimizes for a correct, complete answer, Guardian optimizes for a true-feeling *lens* — the difference between being told what to do and being shown a way to see it yourself.
- **Emotional pacing is a first-class design constraint.** Scene transitions, camera focus, guide emotion, and dialogue timing are all modeled explicitly in the backend contract. A generic chat UI has no equivalent concept — for Guardian, it's core architecture, not polish.

If a redesign, a refactor, or a new feature ever makes Guardian feel more like a competent chatbot and less like a place where Lumina is waiting for you — it is moving in the wrong direction, no matter how much it improves the metrics.
