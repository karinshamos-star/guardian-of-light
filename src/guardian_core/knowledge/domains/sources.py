from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..models import KnowledgeEntity
from .registry import DomainSchema, register_domain_schema


class SourceType(StrEnum):
    BOOK = "book"
    PDF = "pdf"
    COURSE = "course"
    ARTICLE = "article"
    TRADITION = "tradition"
    GUARDIAN_INTERNAL = "guardian_internal"


class SourceData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author: str | None = None
    source_type: SourceType
    publication_year: int | None = None
    reference_url: str | None = None
    citation: str | None = None
    notes: str | None = None


class Source(KnowledgeEntity):
    """A bibliography entry. Cross-domain by design -- entity_type is always
    'source' regardless of which tradition it documents; `source_type`
    (book/pdf/course/...) is a data field, not a path-affecting one."""

    domain: Literal["source"] = "source"
    entity_type: Literal["source"] = "source"
    data: SourceData


SOURCE_SCHEMA = DomainSchema(domain="source", entity_type="source", current_version="1.0", model=Source)
register_domain_schema(SOURCE_SCHEMA)
