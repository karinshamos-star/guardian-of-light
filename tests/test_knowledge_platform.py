from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from guardian_core.knowledge.corpus import (
    KnowledgeValidationError,
    build_corpus,
    find_possible_duplicates,
)
from guardian_core.knowledge.loader import load_knowledge_package
from guardian_core.knowledge.models import ReviewStatus
from guardian_core.knowledge.writers.json_writer import JSONPackageWriter


def _write_entity(root: Path, domain: str, entity_type: str, slug: str, **overrides: Any) -> None:
    payload: dict[str, Any] = {
        "id": f"{domain}.{entity_type}.{slug}",
        "domain": domain,
        "entity_type": entity_type,
        "name": overrides.pop("name", slug.replace("-", " ").title()),
        "status": overrides.pop("status", "draft"),
        "provenance": overrides.pop("provenance", {"confidence": "unverified"}),
        "changelog": overrides.pop("changelog", []),
        "related": overrides.pop("related", {}),
        "data": overrides.pop("data", {}),
    }
    payload.update(overrides)
    directory = root / "domains" / domain / f"{entity_type}s"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{slug}.yaml").write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def test_build_corpus_loads_valid_entities_and_indexes_relations(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha")
    _write_entity(tmp_path, "sample", "widget", "beta", related={"widgets": ["sample.widget.alpha"]})

    corpus = build_corpus(tmp_path)

    assert set(corpus.entities) == {"sample.widget.alpha", "sample.widget.beta"}
    assert corpus.reverse_relations()["sample.widget.alpha"] == ["sample.widget.beta"]
    assert corpus.find("sample", "widget")[0].domain == "sample"


def test_build_corpus_rejects_duplicate_ids(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha")
    directory = tmp_path / "domains" / "sample" / "widgets"
    (directory / "alpha-again.yaml").write_text(
        yaml.safe_dump({
            "id": "sample.widget.alpha",
            "domain": "sample",
            "entity_type": "widget",
            "name": "Duplicate",
            "provenance": {"confidence": "unverified"},
        }),
        encoding="utf-8",
    )

    with pytest.raises(KnowledgeValidationError) as exc:
        build_corpus(tmp_path)
    assert any("duplicate id" in issue for issue in exc.value.issues)


def test_build_corpus_rejects_file_at_wrong_path(tmp_path: Path) -> None:
    directory = tmp_path / "domains" / "sample" / "widgets"
    directory.mkdir(parents=True)
    (directory / "wrong-name.yaml").write_text(
        yaml.safe_dump({
            "id": "sample.widget.alpha",
            "domain": "sample",
            "entity_type": "widget",
            "name": "Alpha",
            "provenance": {"confidence": "unverified"},
        }),
        encoding="utf-8",
    )

    with pytest.raises(KnowledgeValidationError) as exc:
        build_corpus(tmp_path)
    assert any("does not match expected path" in issue for issue in exc.value.issues)


def test_build_corpus_rejects_dangling_relation(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha", related={"widgets": ["sample.widget.missing"]})

    with pytest.raises(KnowledgeValidationError) as exc:
        build_corpus(tmp_path)
    assert any("dangling relation" in issue for issue in exc.value.issues)


def test_build_corpus_rejects_dangling_source_reference(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha", provenance={"confidence": "primary", "source_ids": ["source.missing"]})

    with pytest.raises(KnowledgeValidationError) as exc:
        build_corpus(tmp_path)
    assert any("dangling source reference" in issue for issue in exc.value.issues)


def test_ready_for_ai_requires_confidence_and_changelog(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha", status="ready_for_ai", provenance={"confidence": "unverified"})

    with pytest.raises(KnowledgeValidationError) as exc:
        build_corpus(tmp_path)
    issues = " ".join(exc.value.issues)
    assert "confidence is unverified" in issues
    assert "no changelog entry" in issues


def test_gate_filtering_excludes_content_below_the_gate(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha", status="draft")
    _write_entity(
        tmp_path, "sample", "widget", "beta", status="ready_for_ai",
        provenance={"confidence": "primary"},
        changelog=[{"version": "1.0", "date": "2026-07-31", "reason": "initial"}],
    )

    corpus = build_corpus(tmp_path)
    gated = corpus.filtered(min_status=ReviewStatus.READY_FOR_AI)

    assert set(gated.entities) == {"sample.widget.beta"}


def test_json_writer_and_loader_round_trip(tmp_path: Path) -> None:
    _write_entity(
        tmp_path, "sample", "widget", "alpha", status="ready_for_ai",
        provenance={"confidence": "primary"},
        changelog=[{"version": "1.0", "date": "2026-07-31", "reason": "initial"}],
        related={"widgets": []},
    )
    corpus = build_corpus(tmp_path)

    out_dir = tmp_path / "_compiled"
    JSONPackageWriter().write(corpus, out_dir)

    package = load_knowledge_package(out_dir / "knowledge_package.json")
    entity = package.get("sample.widget.alpha")

    assert entity.name == "Alpha"
    assert package.find("sample", "widget")[0].id == "sample.widget.alpha"
    assert package.manifest.counts["sample.widget"] == 1


def test_possible_duplicate_detection_warns_on_near_identical_names(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "one", name="Will and New Cycles")
    _write_entity(tmp_path, "sample", "widget", "two", name="Will and New Cycle")

    corpus = build_corpus(tmp_path)
    warnings = find_possible_duplicates(corpus)

    assert warnings
    assert "sample.widget" in warnings[0]


def test_deprecated_entities_are_excluded_by_any_gate(tmp_path: Path) -> None:
    _write_entity(tmp_path, "sample", "widget", "alpha", status="deprecated")

    corpus = build_corpus(tmp_path)
    gated = corpus.filtered(min_status=ReviewStatus.DRAFT)

    assert gated.entities == {}
