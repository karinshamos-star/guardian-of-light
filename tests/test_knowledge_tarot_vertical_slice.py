from __future__ import annotations

from pathlib import Path

from guardian_core.knowledge.corpus import build_corpus
from guardian_core.knowledge.domains import CardKnowledge
from guardian_core.knowledge.domains.tarot import TAROT_CARD_SCHEMA
from guardian_core.knowledge.loader import load_knowledge_package
from guardian_core.knowledge.models import ReviewStatus
from guardian_core.knowledge.writers.json_writer import JSONPackageWriter

KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent / "knowledge"


def test_real_knowledge_directory_builds_without_validation_errors() -> None:
    corpus = build_corpus(KNOWLEDGE_ROOT)
    assert "tarot.card.major-00" in corpus.entities


def test_the_fool_materializes_into_typed_card_knowledge() -> None:
    corpus = build_corpus(KNOWLEDGE_ROOT)
    entity = corpus.entities["tarot.card.major-00"]

    card = TAROT_CARD_SCHEMA.materialize(entity)

    assert isinstance(card, CardKnowledge)
    assert card.data.arcana.value == "major"
    assert card.data.name_he == "השוטה"
    assert len(card.data.reflection_questions) >= 1
    assert len(card.data.grounded_actions) >= 1


def test_the_fool_relations_resolve_to_real_entities_in_the_corpus() -> None:
    corpus = build_corpus(KNOWLEDGE_ROOT)
    fool = corpus.entities["tarot.card.major-00"]

    assert fool.provenance.source_ids == ["source.guardian-editorial"]
    assert fool.provenance.source_ids[0] in corpus.entities
    assert fool.provenance.claim_ids[0] in corpus.entities
    assert fool.related["concepts"][0] in corpus.entities

    reverse = corpus.reverse_relations()
    assert "tarot.card.major-00" in reverse["concept.new-beginnings"]


def test_the_fool_survives_a_gated_build_and_reload_round_trip(tmp_path: Path) -> None:
    corpus = build_corpus(KNOWLEDGE_ROOT)
    gated = corpus.filtered(min_status=ReviewStatus.READY_FOR_AI)
    assert "tarot.card.major-00" in gated.entities
    # Card, source, concept, and claim are all ready_for_ai, so gating keeps
    # the whole connected slice together rather than orphaning its relations.
    assert "source.guardian-editorial" in gated.entities
    assert "concept.new-beginnings" in gated.entities
    assert "claim.tarot-0001" in gated.entities

    out_dir = tmp_path / "_compiled"
    JSONPackageWriter().write(gated, out_dir, gate="ready_for_ai")

    package = load_knowledge_package(out_dir / "knowledge_package.json")
    reloaded_entity = package.get("tarot.card.major-00")
    card = TAROT_CARD_SCHEMA.materialize(reloaded_entity)

    assert card.data.core_essence.startswith("עמידה על סף הידוע")
    assert package.related("tarot.card.major-00", "concepts")[0].id == "concept.new-beginnings"
