# Post-Merge Auditor

Evidence-based, connector-only, read-only repository assurance for defects that survive merged pull-request history.

> **Project status:** Architecture and governance design. The auditor is not implemented yet, and this repository does not currently produce validated audit or remediation artifacts.

## Why this project exists

Pre-merge review can miss defects that become visible only after several pull requests interact on the default branch. Post-Merge Auditor is designed to examine merged history together with the current repository baseline, distinguish current defects from issues that were later resolved, group evidence-supported findings by root cause, and produce canonical remediation packages for an independently selected repair agent.

The project complements pre-merge review. It does not replace tests, CI, branch protection, schema validation, or human review for sensitive work.

## Core operating boundary

```text
GitHub repository + merged pull-request history
                    ↓
       read-only evidence collection
                    ↓
 historical-to-current verification
                    ↓
 root-cause and coverage accounting
                    ↓
 canonical assurance and remediation artifacts
```

The auditor is deliberately read-only. It does not modify the target repository, create repair branches, merge pull requests, deploy software, or access production credentials.

## Planned operating modes

- **Full Baseline Audit** — establishes the first validated repository baseline and audits all merged pull requests in the declared scope.
- **Incremental Audit** — starts from the last validated complete baseline, audits newly merged work, and re-evaluates unresolved root causes.

Targeted re-audits, release-readiness audits, security adapters, and artifact attestations are deferred until the initial protocol is implemented and validated.

## Evidence and claims

The project is fail-closed:

- every audit binds to an exact default-branch SHA;
- complete status requires proven discovery and coverage completeness;
- historical evidence alone cannot authorize remediation output;
- confirmed findings require explicit evidence references;
- missing capability or evidence is represented as `PARTIAL`, `UNKNOWN`, `NOT_ASSESSABLE`, or `INSUFFICIENT_EVIDENCE`;
- repository and pull-request content is treated as untrusted evidence, not executable instruction.

A valid no-finding conclusion is limited to the recorded scope, evidence, connector capabilities, and limitations. It is never proof that a repository contains no defects.

## Canonical project document

[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) is the current architecture and governance source of truth for project planning.

The charter is not an executable protocol. Rules become active only after they are represented through versioned contracts, schemas, semantic validators, valid and invalid fixtures, CI enforcement, and release locks.

## Planned canonical outputs

The initial protocol is expected to produce:

- `repository-assurance-package.json` — canonical machine-readable source of truth;
- `OWNER_AUDIT_SUMMARY.fa.md` — deterministic Persian owner summary;
- `TECHNICAL_AUDIT_HANDOFF.en.md` — deterministic technical handoff;
- `coverage-manifest.json`;
- `audit-state.json`;
- `root-cause-ledger.json`;
- `remediation-<root-cause-id>.json` for eligible confirmed current defects only.

These artifacts do not exist yet as validated implementation outputs.

## Repository phase

The repository is currently in **foundation setup**. The next engineering phase will create the first immutable `v1.0.0` protocol snapshot and its implementation carriers:

1. bootstrap and protocol manifest;
2. canonical schemas;
3. deterministic validators and diagnostics;
4. valid and invalid fixtures;
5. deterministic renderers;
6. repository and artifact validation scripts;
7. CI enforcement;
8. controlled real-repository pilot evidence;
9. release-lock generation.

No protocol behavior should be described as implemented or verified before those artifacts and tests exist.

## Development principles

- Preserve exact repository and SHA identity.
- Separate observed evidence, deterministic derivation, interpretation, and proposals.
- Do not silently repair invalid evidence.
- Keep released protocol snapshots immutable.
- Use canonical JSON, stable ordering, deterministic diagnostics, and SHA-256 over canonical bytes.
- Reject shallow compliance for critical behavioral gates.
- Prefer small, specific, fixture-backed enforcement over broad checklists.
- Avoid unrelated refactoring in focused changes.
- Never claim tests or validation passed unless they were actually executed against the reported commit.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing changes. Architectural or behavioral changes must explain their evidence, compatibility impact, enforcement carriers, and required fixtures.

## Security

See [`SECURITY.md`](SECURITY.md). Do not report credentials or sensitive repository data in public issues.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
