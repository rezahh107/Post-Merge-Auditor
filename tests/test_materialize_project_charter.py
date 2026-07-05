from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "materialize_project_charter.py"

spec = importlib.util.spec_from_file_location("materialize_project_charter", SCRIPT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
materializer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(materializer)


class MaterializeProjectCharterTests(unittest.TestCase):
    def test_internal_lf_and_crlf_wrapping_preserves_canonical_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            source_dir = temporary_root / "source"
            source_dir.mkdir()
            output = temporary_root / "PROJECT_CHARTER.generated.md"

            for index, part_name in enumerate(materializer.PART_NAMES):
                original = materializer.SOURCE_DIR.joinpath(part_name).read_text(
                    encoding="ascii"
                )
                compact = "".join(original.split())
                separator = "\r\n" if index % 2 == 0 else "\n"
                wrapped = separator.join(
                    compact[offset : offset + 76]
                    for offset in range(0, len(compact), 76)
                )
                source_dir.joinpath(part_name).write_text(
                    f"  {wrapped}\n",
                    encoding="ascii",
                    newline="",
                )

            digest = materializer.materialize(
                source_dir,
                output,
                expected_sha256=materializer.EXPECTED_SHA256,
                expected_size=materializer.EXPECTED_SIZE,
            )

            content = output.read_bytes()
            self.assertEqual(digest, materializer.EXPECTED_SHA256)
            self.assertEqual(len(content), materializer.EXPECTED_SIZE)
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
