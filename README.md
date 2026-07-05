# Post-Merge Auditor

Evidence-based, read-only repository assurance for merged pull-request history.

`Post-Merge-Auditor` is designed for non-technical repository owners who use LLM-assisted engineering workflows. It audits merged pull requests against the current default-branch state, verifies whether suspected defects still exist, groups evidence-supported findings by root cause, and produces canonical remediation packages for an independently selected repair agent.

> **Status:** Repository bootstrap and architecture phase. No active audit protocol or production-ready implementation has been released yet.

## Why this project exists

Pre-merge review answers whether one pull request appears ready to merge. It does not guarantee that the repository remains consistent after many changes interact over time.

This project adds a separate post-merge assurance loop:

```text
merged pull requests
→ exact repository baseline
→ historical and current evidence
→ current-defect verification
→ root-cause analysis
→ canonical remediation handoff
→ prevention recommendations
```

The system never claims that a repository is free of all defects. A no-finding result is limited to the recorded scope, available evidence, Connector capabilities, and explicit limitations.

## Core boundaries

The auditor is:

- **read-only** against target repositories;
- **GitHub-Connector-only** in the initial operating environment;
- **evidence-driven** and bound to exact repository identities and SHAs;
- **fail-closed** when identity, coverage, evidence, or validation is insufficient;
- **separate from repair execution**—the repair agent is chosen independently by the owner.

The auditor does not create or modify target-repository code, merge pull requests, deploy software, access production, or use sensitive credentials.

## Planned operating modes

### Full baseline audit

Establishes the first validated repository baseline, discovers merged pull requests in scope, evaluates historical-to-current defect status, and creates the initial root-cause ledger.

### Incremental audit

Starts from the last validated complete baseline, discovers newly merged pull requests, re-evaluates unresolved root causes, and detects recurrence or regression.

Targeted re-audit and release-readiness modes are deferred until the initial protocol is validated.

## Canonical output model

The planned canonical source of truth is:

```text
repository-assurance-package.json
```

Planned companion artifacts include:

```text
OWNER_AUDIT_SUMMARY.fa.md
TECHNICAL_AUDIT_HANDOFF.en.md
coverage-manifest.json
audit-state.json
root-cause-ledger.json
remediation-<root-cause-id>.json
```

Human-readable outputs must be deterministic derivatives of validated canonical data.

## Architecture and governance

Start with the project charter:

- [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) — project purpose, boundaries, architecture, governance, decision records, planned capabilities, and `v1.0.0` acceptance criteria.
- [`GOVERNANCE.md`](GOVERNANCE.md) — repository authority, change control, and source precedence.
- [`FOUNDATION_PROVENANCE.json`](FOUNDATION_PROVENANCE.json) — provenance for concepts adapted from `PR-Inspector`.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution and pull-request rules.
- [`SECURITY.md`](SECURITY.md) — security and prompt-injection reporting guidance.

The charter is architectural guidance, not executable enforcement. A behavioral rule becomes active only after it has the required versioned contract, schema carrier, semantic validator, fixtures, CI enforcement, and release lock.

## Development principles

- Preserve exact source and SHA identity.
- Separate historical evidence from current-state verification.
- Never produce remediation for a historical-only defect.
- Record incomplete coverage honestly as `PARTIAL`.
- Keep hypotheses distinct from confirmed findings.
- Prefer the smallest mechanism that blocks a real failure mode.
- Do not modify immutable released protocol snapshots.
- Do not claim tests or validation passed without executed evidence.

## Planned repository shape

```text
Post-Merge-Auditor/
├── PROJECT_CHARTER.md
├── BOOTSTRAP.md
├── CURRENT_VERSION
├── protocol-manifest.yaml
├── BEHAVIORAL_RULE_COVERAGE.md
├── FOUNDATION_PROVENANCE.json
├── protocols/
│   └── v1.0.0/
├── post_merge_auditor/
├── scripts/
├── fixtures/
└── tests/
```

Only the bootstrap and governance foundation exists at this stage. Protocol, schema, validator, fixture, and implementation files will be added through reviewed pull requests.

## Repository workflow

1. Create a focused branch.
2. Make the smallest coherent change.
3. Update affected contracts, schemas, validators, fixtures, tests, documentation, versions, and locks together.
4. Open a pull request with exact validation evidence.
5. Do not merge while required checks, evidence, or review scope are incomplete.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the detailed rules.

## Relationship to PR-Inspector

`PR-Inspector` and `Post-Merge-Auditor` are independent products:

```text
PR-Inspector        → one pull request before merge
Post-Merge-Auditor → repository state after merge
```

Selected foundational concepts are adapted with explicit provenance. There is no shared mutable contract, implicit inheritance, or automatic synchronization between the repositories.

## License

Licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).
