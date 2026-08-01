from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Protocol

from .models import KnowledgeEntity
from .writers.manifest import PackageManifest


class KnowledgePackage(Protocol):
    """What guardian_core's engines depend on. Backed by JSON today; a future
    SQLite/DuckDB-backed package would implement the same three methods
    without any caller needing to change."""

    manifest: PackageManifest

    def get(self, entity_id: str) -> KnowledgeEntity: ...
    def find(self, domain: str, entity_type: str | None = None) -> list[KnowledgeEntity]: ...
    def related(self, entity_id: str, relation: str) -> list[KnowledgeEntity]: ...


class JSONKnowledgePackage:
    def __init__(
        self,
        manifest: PackageManifest,
        entities: dict[str, KnowledgeEntity],
        by_domain: dict[str, list[str]],
    ):
        self.manifest = manifest
        self._entities = entities
        self._by_domain = by_domain

    def get(self, entity_id: str) -> KnowledgeEntity:
        return self._entities[entity_id]

    def find(self, domain: str, entity_type: str | None = None) -> list[KnowledgeEntity]:
        entities = [self._entities[i] for i in self._by_domain.get(domain, [])]
        if entity_type is not None:
            entities = [e for e in entities if e.entity_type == entity_type]
        return entities

    def related(self, entity_id: str, relation: str) -> list[KnowledgeEntity]:
        targets = self._entities[entity_id].related.get(relation, [])
        return [self._entities[t] for t in targets]


def _load_json(path: Path) -> JSONKnowledgePackage:
    payload = json.loads(path.read_text(encoding="utf-8"))
    manifest = PackageManifest.model_validate(payload["manifest"])
    entities = {eid: KnowledgeEntity.model_validate(e) for eid, e in payload["entities"].items()}
    return JSONKnowledgePackage(manifest=manifest, entities=entities, by_domain=payload["indexes"]["by_domain"])


_LOADERS: dict[str, Callable[[Path], KnowledgePackage]] = {"json": _load_json}


def register_loader(format_name: str, loader_fn: Callable[[Path], KnowledgePackage]) -> None:
    """Extension point for future backends (SQLite, DuckDB, ...)."""
    _LOADERS[format_name] = loader_fn


def load_knowledge_package(path: Path, format: str = "json") -> KnowledgePackage:
    return _LOADERS[format](path)
