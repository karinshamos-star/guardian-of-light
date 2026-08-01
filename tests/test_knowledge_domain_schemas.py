from __future__ import annotations

import pytest
from pydantic import BaseModel, ConfigDict

from guardian_core.knowledge.corpus import KnowledgeValidationError
from guardian_core.knowledge.domains.registry import DomainSchema, VersionMigration
from guardian_core.knowledge.models import KnowledgeEntity, Provenance


class _WidgetDataV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    labels: list[str]


class _WidgetV2(KnowledgeEntity):
    data: _WidgetDataV2


def _migrate_v1_to_v2(data: dict) -> dict:
    return {"labels": [data["label"]]} if "label" in data else data


_WIDGET_SCHEMA = DomainSchema(
    domain="sample",
    entity_type="widget",
    current_version="2.0",
    model=_WidgetV2,
    migrations=[VersionMigration(from_version="1.0", to_version="2.0", migrate=_migrate_v1_to_v2)],
)


def test_materialize_applies_registered_migration_for_old_schema_version() -> None:
    old_entity = KnowledgeEntity(
        id="sample.widget.alpha", domain="sample", entity_type="widget", name="Alpha",
        schema_version="1.0", provenance=Provenance(confidence="primary"),
        data={"label": "hello"},
    )

    materialized = _WIDGET_SCHEMA.materialize(old_entity)

    assert materialized.data.labels == ["hello"]
    assert materialized.schema_version == "2.0"


def test_materialize_is_a_passthrough_when_already_current() -> None:
    entity = KnowledgeEntity(
        id="sample.widget.beta", domain="sample", entity_type="widget", name="Beta",
        schema_version="2.0", provenance=Provenance(confidence="primary"),
        data={"labels": ["already-current"]},
    )

    materialized = _WIDGET_SCHEMA.materialize(entity)

    assert materialized.data.labels == ["already-current"]


def test_materialize_raises_when_no_migration_path_exists() -> None:
    entity = KnowledgeEntity(
        id="sample.widget.gamma", domain="sample", entity_type="widget", name="Gamma",
        schema_version="0.1", provenance=Provenance(confidence="primary"),
        data={},
    )

    with pytest.raises(KnowledgeValidationError):
        _WIDGET_SCHEMA.materialize(entity)
