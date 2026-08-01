from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import KnowledgeEntity, ReviewStatus, SourceConfidence


class KnowledgeValidationError(Exception):
    """Raised when one or more entities in the corpus fail structural validation."""

    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("\n".join(issues))


@dataclass
class KnowledgeCorpus:
    """Generic, format-agnostic, in-memory compiled representation of the
    knowledge base. Writers serialize this; nothing here assumes a target format."""

    entities: dict[str, KnowledgeEntity] = field(default_factory=dict)

    def by_domain(self, domain: str) -> list[KnowledgeEntity]:
        return [e for e in self.entities.values() if e.domain == domain]

    def find(self, domain: str, entity_type: str | None = None) -> list[KnowledgeEntity]:
        entities = self.by_domain(domain)
        if entity_type is not None:
            entities = [e for e in entities if e.entity_type == entity_type]
        return entities

    def reverse_relations(self) -> dict[str, list[str]]:
        reverse: dict[str, list[str]] = {}
        for entity in self.entities.values():
            for target in entity.relation_ids():
                reverse.setdefault(target, []).append(entity.id)
        return reverse

    def content_hash(self) -> str:
        payload = "".join(sorted(e.model_dump_json() for e in self.entities.values()))
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def filtered(self, *, min_status: ReviewStatus) -> "KnowledgeCorpus":
        order = list(ReviewStatus)
        threshold = order.index(min_status)
        kept = {
            eid: e
            for eid, e in self.entities.items()
            if e.status != ReviewStatus.DEPRECATED and order.index(e.status) >= threshold
        }
        return KnowledgeCorpus(entities=kept)


def discover_yaml_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.yaml") if p.is_file())


def load_entity(path: Path) -> KnowledgeEntity:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    try:
        return KnowledgeEntity.model_validate(raw)
    except ValidationError as exc:
        raise KnowledgeValidationError([f"{path}: {exc}"]) from exc


def expected_path(root: Path, entity: KnowledgeEntity) -> Path:
    slug = entity.id.split(".")[-1]
    return root / "domains" / entity.domain / f"{entity.entity_type}s" / f"{slug}.yaml"


def build_corpus(root: Path) -> KnowledgeCorpus:
    """Discover, parse, and structurally validate every entity under `root`.

    Raises KnowledgeValidationError with every issue found (not just the
    first) if anything is wrong: bad schema, duplicate ids, misplaced files,
    dangling relations/sources, or a ready_for_ai entity that hasn't earned it.
    """
    issues: list[str] = []
    entities: dict[str, KnowledgeEntity] = {}
    paths_by_id: dict[str, Path] = {}

    for path in discover_yaml_files(root):
        entity = load_entity(path)
        if entity.id in entities:
            issues.append(f"duplicate id '{entity.id}': {path} and {paths_by_id[entity.id]}")
            continue
        expected = expected_path(root, entity)
        if path.resolve() != expected.resolve():
            issues.append(f"{entity.id}: file at {path} does not match expected path {expected}")
        entities[entity.id] = entity
        paths_by_id[entity.id] = path

    for entity in entities.values():
        for relation_name, targets in entity.related.items():
            for target in targets:
                if target not in entities:
                    issues.append(f"{entity.id}: dangling relation '{relation_name}' -> '{target}'")
        for source_id in entity.provenance.source_ids:
            if source_id not in entities:
                issues.append(f"{entity.id}: dangling source reference '{source_id}'")
        for claim_id in entity.provenance.claim_ids:
            if claim_id not in entities:
                issues.append(f"{entity.id}: dangling claim reference '{claim_id}'")
        if entity.status == ReviewStatus.READY_FOR_AI:
            if entity.provenance.confidence == SourceConfidence.UNVERIFIED:
                issues.append(f"{entity.id}: status is ready_for_ai but provenance confidence is unverified")
            if not entity.changelog:
                issues.append(f"{entity.id}: status is ready_for_ai but has no changelog entry")

    if issues:
        raise KnowledgeValidationError(issues)

    return KnowledgeCorpus(entities=entities)


def find_possible_duplicates(corpus: KnowledgeCorpus, threshold: float = 0.85) -> list[str]:
    """Soft warning, not a hard failure: flags near-identical names within the
    same (domain, entity_type), the exact pattern that let the Numbers-vs-
    Number-Cards drift happen unnoticed in the Notion-only workspace."""
    warnings: list[str] = []
    groups: dict[tuple[str, str], list[KnowledgeEntity]] = {}
    for entity in corpus.entities.values():
        groups.setdefault((entity.domain, entity.entity_type), []).append(entity)

    for (domain, entity_type), group in groups.items():
        for a, b in combinations(group, 2):
            ratio = difflib.SequenceMatcher(None, a.name.lower(), b.name.lower()).ratio()
            if ratio >= threshold:
                warnings.append(
                    f"possible duplicate in {domain}.{entity_type}: "
                    f"'{a.id}' ~ '{b.id}' (name similarity {ratio:.2f})"
                )
    return warnings
