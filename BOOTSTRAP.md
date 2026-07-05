# Post-Merge Auditor Bootstrap

**Bootstrap status:** Architecture and repository-foundation phase  
**Active audit protocol:** None  
**Production-ready implementation:** No

## Required load order

Before planning or changing this repository, read:

1. `README.md`
2. `PROJECT_CHARTER.md`
3. `GOVERNANCE.md`
4. `AGENTS.md`
5. `BEHAVIORAL_RULE_COVERAGE.md`
6. `FOUNDATION_PROVENANCE.json`
7. `CONTRIBUTING.md`
8. `SECURITY.md`

## Current boundary

The repository does not yet contain an active `v1.0.0` audit protocol, canonical audit schema, semantic validator, validated fixtures, release lock, or production-ready auditor.

Do not claim that planned capabilities are implemented or enforced.

The Charter defines proposed architecture. Behavioral-rule enforcement status is authoritative only in `BEHAVIORAL_RULE_COVERAGE.md`.

## Allowed work

Current work may:

- design and implement the initial versioned protocol;
- add schemas, validators, fixtures, tests, CI, deterministic rendering, and release locks;
- improve repository foundation and documentation without misrepresenting planning as enforcement.

Current work must not:

- modify a target repository as part of an audit;
- add automatic repair, merge, approval, deployment, production, or credential access;
- present synthetic fixtures as real repository evidence;
- activate a Critical rule through prose alone;
- modify a future immutable released snapshot in place.

## Intake behavior

When asked to begin development, first verify the repository foundation and state explicitly:

```text
Post-Merge-Auditor is in bootstrap development.
No active audit protocol has been released yet.
Work will proceed as engineering implementation, not as a completed repository audit.
```

Then use the Charter and governance files to select the next smallest complete vertical slice.
