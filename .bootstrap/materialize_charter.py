from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

EXPECTED_PARTS = 17
EXPECTED_SHA256 = "aba3fbc0d34b407934ac3bee1fa04e1ed3eee325cfe9ea30e65108e49821e5a6"
EXPECTED_LENGTH = 87_799
OUTPUT = Path("PROJECT_CHARTER.md")


def main() -> int:
    parts = sorted(Path(".bootstrap").glob("charter.b64.*"))
    if len(parts) != EXPECTED_PARTS:
        raise SystemExit(
            f"Expected {EXPECTED_PARTS} charter payload parts, found {len(parts)}."
        )

    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    compressed = base64.b64decode(encoded, validate=True)
    content = gzip.decompress(compressed)

    if len(content) != EXPECTED_LENGTH:
        raise SystemExit(
            f"Charter length mismatch: expected {EXPECTED_LENGTH}, got {len(content)}."
        )

    digest = hashlib.sha256(content).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"Charter SHA-256 mismatch: expected {EXPECTED_SHA256}, got {digest}."
        )

    text = content.decode("utf-8")
    required_markers = (
        "# Post-Merge Auditor — Project Charter",
        "**Version:** `0.4.0`",
        "## 41. Adoption Status",
    )
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        raise SystemExit(f"Charter semantic marker(s) missing: {missing!r}")

    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"Materialized {OUTPUT} ({len(content)} bytes, sha256={digest}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
