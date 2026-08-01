from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .corpus import KnowledgeValidationError, build_corpus, find_possible_duplicates
from .models import ReviewStatus
from .writers.json_writer import JSONPackageWriter

WRITERS = {"json": JSONPackageWriter()}


def run(knowledge_root: Path, out_dir: Path, gate: str | None, format: str) -> int:
    try:
        corpus = build_corpus(knowledge_root)
    except KnowledgeValidationError as exc:
        for issue in exc.issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    for warning in find_possible_duplicates(corpus):
        print(f"WARNING: {warning}", file=sys.stderr)

    if gate:
        corpus = corpus.filtered(min_status=ReviewStatus(gate))

    writer = WRITERS[format]
    manifest = writer.write(corpus, out_dir, gate=gate)
    print(f"Built {len(corpus.entities)} entities -> {out_dir} ({manifest.content_hash})")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Guardian knowledge package from knowledge/.")
    parser.add_argument("--knowledge-root", type=Path, default=Path("knowledge"))
    parser.add_argument("--out", type=Path, default=Path("knowledge/_compiled"))
    parser.add_argument("--gate", choices=[s.value for s in ReviewStatus], default=None,
                         help="Only include entities at or above this review status (e.g. ready_for_ai for production).")
    parser.add_argument("--format", choices=list(WRITERS), default="json")
    args = parser.parse_args()
    sys.exit(run(args.knowledge_root, args.out, args.gate, args.format))


if __name__ == "__main__":
    main()
