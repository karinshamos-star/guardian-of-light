from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..models import KnowledgeEntity
from .registry import DomainSchema, register_domain_schema


class NumberKnowledgeData(BaseModel):
    """No range constraint on `value` here: whether numerology spans 0-9,
    includes master numbers, or something else entirely is a content
    decision for the numerology domain to make and migrate independently,
    never an infrastructure-level assumption."""

    model_config = ConfigDict(extra="forbid")

    value: int
    essence: str
    supporting_frequency: list[str] = Field(min_length=1)
    blocking_frequency: list[str] = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)
    guardian_guidance: str


class NumberKnowledge(KnowledgeEntity):
    domain: Literal["numerology"] = "numerology"
    entity_type: Literal["number"] = "number"
    data: NumberKnowledgeData


NUMBER_SCHEMA = DomainSchema(
    domain="numerology",
    entity_type="number",
    current_version="1.0",
    model=NumberKnowledge,
)

register_domain_schema(NUMBER_SCHEMA)
