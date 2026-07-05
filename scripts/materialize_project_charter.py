#!/usr/bin/env python3
"""Materialize and verify the canonical project charter."""

from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "charter" / "source"
OUTPUT = ROOT / "PROJECT_CHARTER.generated.md"
EXPECTED_SHA256 = "aba3fbc0d34b407934ac3bee1fa04e1ed3eee325cfe9ea30e65108e49821e5a6"
EXPECTED_SIZE = 87_799


def main() -> int:
    parts = sorted(SOURCE_DIR.glob("part-*.b64"))
    if [path.name for path in parts] != [
        "part-01.b64",
        "part-02.b64",
        "part-03.b64",
        "part-04.b64",
    ]:
        raise SystemExit("ERROR: canonical charter source parts are missing or unexpected")

    encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
    try:
        content = gzip.decompress(base64.b64decode(encoded, validate=True))
    except Exception as exc:
        raise SystemExit(f"ERROR: canonical charter payload is invalid: {exc}") from exc

    digest = hashlib.sha256(content).hexdigest()
    if len(content) != EXPECTED_SIZE:
        raise SystemExit(
            f"ERROR: charter size mismatch: expected {EXPECTED_SIZE}, got {len(content)}"
        )
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"ERROR: charter SHA-256 mismatch: expected {EXPECTED_SHA256}, got {digest}"
        )

    OUTPUT.write_bytes(content)
    print(f"OK: wrote {OUTPUT.relative_to(ROOT)}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
