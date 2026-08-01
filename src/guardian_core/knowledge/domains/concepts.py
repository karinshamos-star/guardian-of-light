from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..models import KnowledgeEntity
from .registry import DomainSchema, register_domain_schema


class ConceptCategory(StrEnum):
    ARCHETYPE = "archetype"
    PROCESS = "process"
    STATE = "state"
    VIRTUE = "virtue"
    SHADOW = "shadow"
    PRACTICE = "practice"


class ConceptData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: ConceptCategory
    definition: str
    light_expression: str | None = None
    shadow_expression: str | None = None
    guardian_language: str | None = None


class Concept(KnowledgeEntity):
    """Cross-domain by design, same as Source and KnowledgeClaim -- a
    Concept can be related to a card, a number, an astrology entity, etc."""

    domain: Literal["concept"] = "concept"
    entity_type: Literal["concept"] = "concept"
    data: ConceptData


CONCEPT_SCHEMA = DomainSchema(domain="concept", entity_type="concept", current_version="1.0", model=Concept)
register_domain_schema(CONCEPT_SCHEMA)
