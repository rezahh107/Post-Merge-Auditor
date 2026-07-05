# Contributing

Post-Merge Auditor is currently in architecture and foundation development. Contributions must preserve the read-only, evidence-based, fail-closed product boundary defined in `PROJECT_CHARTER.md`.

## Before opening a change

1. Read `PROJECT_CHARTER.md`.
2. Separate required changes from optional recommendations.
3. Identify whether the change is editorial, implementation-only, protocol-behavioral, or schema-breaking.
4. Do not present a proposal as active behavior.
5. Do not modify a released protocol snapshot in place.

## Pull-request expectations

A pull request should include:

- the problem being solved;
- the evidence or contract supporting the change;
- affected files and public artifacts;
- compatibility and migration impact;
- tests, fixtures, validators, and documentation affected;
- commands actually executed and their real results;
- remaining limitations or unavailable evidence.

Critical behavioral rules must identify:

```text
canonical carrier
minimum semantic children
validator rule
valid fixture
invalid fixture
CI enforcement
applicable downstream rejection
```

## Scope discipline

Do not include unrelated refactoring. Do not weaken validation to make a change pass. Do not remove or rewrite failing fixtures without explaining why the governing contract changed.

## Commit and branch guidance

Use focused branches and descriptive commits. Suggested branch prefixes:

```text
feat/
fix/
docs/
chore/
refactor/
test/
```

Prefer pull requests over direct changes to `main`.

## Validation claims

Never claim a test, validator, build, workflow, or audit passed unless it was executed against the exact reported commit. Mark unavailable execution honestly.
