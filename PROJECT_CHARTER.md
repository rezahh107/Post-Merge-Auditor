# Post-Merge Auditor — Project Charter

**Canonical charter version:** `0.4.0`  
**Canonical SHA-256:** `aba3fbc0d34b407934ac3bee1fa04e1ed3eee325cfe9ea30e65108e49821e5a6`  
**Canonical size:** `87,799 bytes`

The exact Charter source is stored losslessly as a deterministic gzip/base64 payload split across four files under [`docs/charter/source/`](docs/charter/source/).

This representation is used only because the current GitHub Connector cannot transfer the complete Markdown file in one safe write. It does not change the Charter content or status.

## Materialize the readable Charter

From the repository root:

```bash
python scripts/materialize_project_charter.py
```

The script:

1. reads the four numbered source parts in lexical order;
2. concatenates their base64 payloads without separators;
3. decodes and decompresses the original Markdown;
4. verifies the exact SHA-256 and byte size;
5. writes `PROJECT_CHARTER.generated.md`.

Do not edit the generated file as a source of truth. Amendments must replace the canonical payload, expected hash, version, and this index together through an explicit Charter revision.

## Status

The Charter remains a planning and governance document. It is not an executable protocol and does not prove that the auditor has been implemented or validated.
