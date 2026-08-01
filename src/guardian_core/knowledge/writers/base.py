from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..corpus import KnowledgeCorpus
from .manifest import PackageManifest


class PackageWriter(Protocol):
    """A pluggable serializer from the generic KnowledgeCorpus to a concrete
    runtime format. JSON is the first implementation; SQLite, DuckDB, or a
    vector index are future writers behind this same interface -- adding one
    never requires touching the corpus or the authored knowledge files."""

    format_name: str

    def write(self, corpus: KnowledgeCorpus, out_dir: Path) -> PackageManifest: ...
