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
PART_NAMES = (
    "part-01.b64",
    "part-02.b64",
    "part-03.b64",
    "part-04.b64",
)


def materialize(
    source_dir: Path,
    output: Path,
    expected_sha256: str,
    expected_size: int,
) -> str:
    """Decode, verify, and write the canonical charter.

    ASCII whitespace is removed before strict Base64 validation so line wrapping
    and CRLF normalization do not alter the represented payload.
    """

    parts = sorted(source_dir.glob("part-*.b64"))
    if tuple(path.name for path in parts) != PART_NAMES:
        raise ValueError("canonical charter source parts are missing or unexpected")

    encoded = "".join(
        "".join(path.read_text(encoding="ascii").split()) for path in parts
    )
    try:
        content = gzip.decompress(base64.b64decode(encoded, validate=True))
    except Exception as exc:
        raise ValueError(f"canonical charter payload is invalid: {exc}") from exc

    digest = hashlib.sha256(content).hexdigest()
    if len(content) != expected_size:
        raise ValueError(
            f"charter size mismatch: expected {expected_size}, got {len(content)}"
        )
    if digest != expected_sha256:
        raise ValueError(
            f"charter SHA-256 mismatch: expected {expected_sha256}, got {digest}"
        )

    output.write_bytes(content)
    return digest


def main() -> int:
    try:
        digest = materialize(
            SOURCE_DIR,
            OUTPUT,
            expected_sha256=EXPECTED_SHA256,
            expected_size=EXPECTED_SIZE,
        )
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    print(f"OK: wrote {OUTPUT.relative_to(ROOT)}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
