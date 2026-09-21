#!/usr/bin/env python3
"""Create a reproducible manifest for files used in the project."""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import date
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--coverage", default="schema/example file")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    exists = args.output.exists()
    with args.output.open("a", newline="", encoding="utf-8") as file:
        fields = [
            "manifest_date", "relative_path", "source_url", "release", "coverage",
            "bytes", "sha256", "row_count", "status",
        ]
        writer = csv.DictWriter(file, fieldnames=fields)
        if not exists:
            writer.writeheader()
        for path in args.files:
            if not path.is_file():
                raise FileNotFoundError(path)
            row_count = "not_applicable"
            if path.suffix.lower() in {".txt", ".csv"}:
                with path.open("rb") as source:
                    row_count = sum(1 for _ in source)
            writer.writerow({
                "manifest_date": date.today().isoformat(),
                "relative_path": path.as_posix(),
                "source_url": args.source_url,
                "release": args.release,
                "coverage": args.coverage,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "row_count": row_count,
                "status": "downloaded",
            })


if __name__ == "__main__":
    main()
