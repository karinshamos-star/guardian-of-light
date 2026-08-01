from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..corpus import KnowledgeCorpus
from .manifest import PackageManifest


class JSONPackageWriter:
    format_name = "json"

    def write(self, corpus: KnowledgeCorpus, out_dir: Path, *, gate: str | None = None) -> PackageManifest:
        out_dir.mkdir(parents=True, exist_ok=True)

        manifest = PackageManifest(
            format=self.format_name,
            content_hash=corpus.content_hash(),
            built_at=datetime.now(timezone.utc).isoformat(),
            gate=gate,
            counts=_counts(corpus),
        )
        payload = {
            "manifest": manifest.model_dump(mode="json"),
            "entities": {eid: e.model_dump(mode="json") for eid, e in corpus.entities.items()},
            "indexes": {
                "by_domain": _by_domain(corpus),
                "reverse_relations": corpus.reverse_relations(),
            },
        }
        (out_dir / "knowledge_package.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest


def _counts(corpus: KnowledgeCorpus) -> dict[str, int]:
    counts: dict[str, int] = {}
    for e in corpus.entities.values():
        key = f"{e.domain}.{e.entity_type}"
        counts[key] = counts.get(key, 0) + 1
    return counts


def _by_domain(corpus: KnowledgeCorpus) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for e in corpus.entities.values():
        out.setdefault(e.domain, []).append(e.id)
    return out
