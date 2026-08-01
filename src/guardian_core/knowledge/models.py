from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

ID_PATTERN = r"^[a-z0-9]+(?:\.[a-z0-9-]+)+$"
SCHEMA_VERSION_PATTERN = r"^\d+\.\d+$"


class ReviewStatus(StrEnum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    REVIEWED = "reviewed"
    READY_FOR_AI = "ready_for_ai"
    DEPRECATED = "deprecated"


class SourceConfidence(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    INTERPRETIVE = "interpretive"
    UNVERIFIED = "unverified"


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_ids: list[str] = Field(default_factory=list)
    confidence: SourceConfidence = SourceConfidence.UNVERIFIED
    claim_ids: list[str] = Field(default_factory=list)


class ChangeLogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    date: date
    reason: str
    reviewer: str | None = None


class KnowledgeEntity(BaseModel):
    """Generic envelope for any node in the knowledge corpus, regardless of domain.

    The core pipeline validates only these fields. Domain-specific content
    (a card's light/shadow expression, a number's essence, a calculation's
    formula...) lives entirely in `data`, which the infrastructure never
    inspects -- what a domain's entities look like is a content decision,
    not an architecture decision. Typed, per-domain schemas can validate
    `data` as an optional layer on top of this, added independently per
    domain without changing this model.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=ID_PATTERN)
    schema_version: str = Field(default="1.0", pattern=SCHEMA_VERSION_PATTERN)
    domain: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: ReviewStatus = ReviewStatus.DRAFT
    provenance: Provenance = Field(default_factory=Provenance)
    changelog: list[ChangeLogEntry] = Field(default_factory=list)
    related: dict[str, list[str]] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)

    def relation_ids(self) -> set[str]:
        return {ref for refs in self.related.values() for ref in refs}
