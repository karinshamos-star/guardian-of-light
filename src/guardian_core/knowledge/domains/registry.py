from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..corpus import KnowledgeValidationError
from ..models import KnowledgeEntity

Migration = Callable[[dict], dict]


@dataclass
class VersionMigration:
    from_version: str
    to_version: str
    migrate: Migration


@dataclass
class DomainSchema:
    """Optional, pluggable typed schema for one (domain, entity_type) pair.

    Registering one never changes how the generic pipeline validates or
    builds the corpus -- it only lets a consumer `materialize()` a generic
    KnowledgeEntity into a strongly-typed subclass, applying any registered
    migrations if the entity predates the current schema_version.
    """

    domain: str
    entity_type: str
    current_version: str
    model: type[KnowledgeEntity]
    migrations: list[VersionMigration] = field(default_factory=list)

    def upgrade_data(self, data: dict, schema_version: str) -> dict:
        version = schema_version
        data = dict(data)
        while version != self.current_version:
            step = next((m for m in self.migrations if m.from_version == version), None)
            if step is None:
                raise KnowledgeValidationError([
                    f"{self.domain}.{self.entity_type}: no migration path from "
                    f"schema_version '{version}' to '{self.current_version}'"
                ])
            data = step.migrate(data)
            version = step.to_version
        return data

    def materialize(self, entity: KnowledgeEntity):
        payload = entity.model_dump(mode="json")
        if entity.schema_version != self.current_version:
            payload["data"] = self.upgrade_data(entity.data, entity.schema_version)
            payload["schema_version"] = self.current_version
        return self.model.model_validate(payload)


_REGISTRY: dict[tuple[str, str], DomainSchema] = {}


def register_domain_schema(schema: DomainSchema) -> None:
    _REGISTRY[(schema.domain, schema.entity_type)] = schema


def get_domain_schema(domain: str, entity_type: str) -> DomainSchema | None:
    return _REGISTRY.get((domain, entity_type))
