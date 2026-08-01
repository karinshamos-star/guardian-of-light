from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PackageManifest(BaseModel):
    """Format-agnostic build metadata, shared by every writer/loader backend.

    `content_hash` is what Guardian Engine Contracts' Runtime Orchestrator
    trace.knowledge_version field should be populated from.
    """

    model_config = ConfigDict(extra="forbid")

    format: str
    content_hash: str
    built_at: str
    gate: str | None = None
    counts: dict[str, int]
