# Project Foundry trusted provenance action

This composite action is a narrow, read-only trust root for `rezahh107/Project-Foundry`.
It must be called by exact commit SHA from a default-branch `workflow_run` workflow.

It does not execute target-repository code. It resolves the canonical workflow by exact
GitHub workflow ID and path, then binds success to the exact repository, run attempt,
Head SHA, event, PR number and refs, or to a push on `main`.

The action emits a canonical attestation digest in the step output and job summary.
Activation is delayed: a new action commit becomes authoritative only after owner review,
merge, and an explicit pin update in the target repository.
