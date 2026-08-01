from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..models import KnowledgeEntity
from .registry import DomainSchema, register_domain_schema


class CalculationMethodData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    formula_description: str
    formula_steps: list[str] = Field(min_length=1)
    inputs: list[str] = Field(min_length=1)
    worked_example: str | None = None


class CalculationMethod(KnowledgeEntity):
    """entity_type is fixed, but domain is deliberately NOT narrowed: a
    calculation can belong to numerology, astrology, or any future domain
    that needs a documented formula -- this type is reusable across domains."""

    entity_type: Literal["calculation"] = "calculation"
    data: CalculationMethodData


def calculation_schema_for(domain: str) -> DomainSchema:
    return DomainSchema(domain=domain, entity_type="calculation", current_version="1.0", model=CalculationMethod)


register_domain_schema(calculation_schema_for("numerology"))
