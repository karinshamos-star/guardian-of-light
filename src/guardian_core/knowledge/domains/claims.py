from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..models import KnowledgeEntity
from .registry import DomainSchema, register_domain_schema


class ClaimType(StrEnum):
    TRADITIONAL = "traditional"
    RIDER_WAITE = "rider_waite"
    GOLDEN_DAWN = "golden_dawn"
    KABBALISTIC = "kabbalistic"
    NUMEROLOGICAL = "numerological"
    ASTROLOGICAL = "astrological"
    COMPARATIVE = "comparative"
    GUARDIAN = "guardian"


class ClaimConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class KnowledgeClaimData(BaseModel):
    """`disputed` lives here, not as a generic ReviewStatus value -- whether
    a claim can be 'disputed' is a claims-specific concept, not something the
    infrastructure's review-status enum should know about."""

    model_config = ConfigDict(extra="forbid")

    statement: str
    claim_type: ClaimType
    confidence: ClaimConfidence
    disputed: bool = False
    evidence_note: str | None = None


class KnowledgeClaim(KnowledgeEntity):
    domain: Literal["claim"] = "claim"
    entity_type: Literal["claim"] = "claim"
    data: KnowledgeClaimData


CLAIM_SCHEMA = DomainSchema(domain="claim", entity_type="claim", current_version="1.0", model=KnowledgeClaim)
register_domain_schema(CLAIM_SCHEMA)
