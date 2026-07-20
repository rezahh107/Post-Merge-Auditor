#!/usr/bin/env python3
"""Trusted GitHub-hosted provenance attestor for Project Foundry.

This module is intended to run from an immutable commit in a repository that is
separate from the target repository. It never executes target-repository code.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

API_ROOT = "https://api.github.com"
APPROVED_FOUNDATION_WORKFLOW_SHA256 = "a6973556b2f03a75fea2feecd11cc322a466c9840a7db3aea5704261971a39e1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
CANONICAL_JSON_KWARGS = {
    "sort_keys": True,
    "separators": (",", ":"),
    "ensure_ascii": False,
    "allow_nan": False,
}


class AttestationError(RuntimeError):
    """Raised when hosted evidence does not satisfy the trust contract."""


@dataclass(frozen=True)
class Inputs:
    repository: str
    run_id: int
    run_attempt: int
    expected_workflow_id: int
    expected_workflow_path: str
    expected_head_sha: str
    expected_event: str
    expected_pr_number: int | None
    expected_head_ref: str
    expected_base_ref: str
    producer_repository: str
    producer_ref: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AttestationError(message)


def _api_get(path: str, token: str) -> Any:
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Project-Foundry-Trusted-Attestor/1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        raise AttestationError(f"GitHub API request failed for {path}: {exc}") from exc


def _full_name(value: Any) -> str | None:
    return value.get("full_name") if isinstance(value, dict) else None


def _ref(value: Any) -> str | None:
    return value.get("ref") if isinstance(value, dict) else None


def _sha(value: Any) -> str | None:
    return value.get("sha") if isinstance(value, dict) else None


def _pr_numbers(run: dict[str, Any]) -> set[int]:
    numbers: set[int] = set()
    for item in run.get("pull_requests", []):
        if isinstance(item, dict) and isinstance(item.get("number"), int):
            numbers.add(item["number"])
    return numbers


def validate_payloads(
    inputs: Inputs,
    run: dict[str, Any],
    workflow: dict[str, Any],
    pr: dict[str, Any] | None,
    commit: dict[str, Any] | None = None,
    merge_prs: list[Any] | None = None,
    workflow_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Validate canonical workflow and exact PR/push association."""
    _require(SHA40.fullmatch(inputs.expected_head_sha) is not None, "expected Head SHA is malformed")
    _require(SHA40.fullmatch(inputs.producer_ref) is not None, "attestor action is not pinned to an immutable commit SHA")
    _require(inputs.producer_repository == "rezahh107/Post-Merge-Auditor", "unexpected attestor repository")

    _require(isinstance(run, dict), "workflow-run payload is not an object")
    _require(run.get("id") == inputs.run_id, "workflow run ID mismatch")
    _require(run.get("run_attempt") == inputs.run_attempt, "stale or unexpected workflow run attempt")
    _require(run.get("workflow_id") == inputs.expected_workflow_id, "noncanonical workflow ID")
    _require(run.get("head_sha") == inputs.expected_head_sha, "workflow run Head SHA mismatch")
    _require(run.get("event") == inputs.expected_event, "workflow event mismatch")
    _require(run.get("status") == "completed", "workflow run is not completed")
    _require(run.get("conclusion") == "success", "canonical workflow did not succeed")
    _require(_full_name(run.get("repository")) == inputs.repository, "workflow run belongs to another repository")

    _require(isinstance(workflow, dict), "workflow payload is not an object")
    _require(workflow.get("id") == inputs.expected_workflow_id, "resolved workflow ID mismatch")
    _require(workflow.get("path") == inputs.expected_workflow_path, "resolved workflow path mismatch")
    _require(workflow.get("state") == "active", "canonical workflow is not active")
    _require(workflow_bytes is not None, "canonical workflow bytes are absent")
    actual_workflow_sha256 = hashlib.sha256(workflow_bytes).hexdigest()
    _require(
        actual_workflow_sha256 == APPROVED_FOUNDATION_WORKFLOW_SHA256,
        "canonical workflow bytes are not approved by the active attestor policy",
    )

    if inputs.expected_event == "pull_request":
        _require(inputs.expected_pr_number is not None, "PR run lacks an expected PR number")
        _require(pr is not None and isinstance(pr, dict), "PR payload is absent")
        _require(inputs.expected_pr_number in _pr_numbers(run), "workflow run is associated with another PR")
        _require(pr.get("number") == inputs.expected_pr_number, "PR number mismatch")
        _require(_full_name((pr.get("base") or {}).get("repo")) == inputs.repository, "PR base repository mismatch")
        _require(_sha(pr.get("head")) == inputs.expected_head_sha, "PR Head SHA mismatch")
        _require(_ref(pr.get("head")) == inputs.expected_head_ref, "PR Head ref mismatch")
        _require(_ref(pr.get("base")) == inputs.expected_base_ref, "PR base ref mismatch")
        _require(run.get("head_branch") == inputs.expected_head_ref, "workflow run Head branch mismatch")
        _require(_full_name(run.get("head_repository")) == inputs.repository, "workflow run Head repository mismatch")
    elif inputs.expected_event == "push":
        _require(inputs.expected_pr_number is None, "push run unexpectedly carries a PR number")
        _require(inputs.expected_head_ref in {"main", "refs/heads/main"}, "push attestation is not bound to main")
        _require(inputs.expected_base_ref in {"main", "refs/heads/main"}, "push base/ref contract is not main")
        _require(run.get("head_branch") == "main", "successful push run is not on main")
        _require(commit is not None and isinstance(commit, dict), "push commit payload is absent")
        _require(commit.get("sha") == inputs.expected_head_sha, "push commit identity mismatch")
        parents = [item.get("sha") for item in commit.get("parents", []) if isinstance(item, dict)]
        _require(all(isinstance(item, str) and SHA40.fullmatch(item) for item in parents), "push commit has malformed parents")
        if len(parents) == 2:
            first, second = parents
            matches = []
            for candidate in merge_prs or []:
                if not isinstance(candidate, dict):
                    continue
                head = candidate.get("head") if isinstance(candidate.get("head"), dict) else {}
                base = candidate.get("base") if isinstance(candidate.get("base"), dict) else {}
                base_repo = base.get("repo") if isinstance(base.get("repo"), dict) else {}
                if (
                    candidate.get("merged_at")
                    and candidate.get("merge_commit_sha") == inputs.expected_head_sha
                    and head.get("sha") == second
                    and base.get("sha") == first
                    and base.get("ref") == "main"
                    and base_repo.get("full_name") == inputs.repository
                ):
                    matches.append(candidate)
            _require(len(matches) == 1, "two-parent main push is not bound to exactly one hosted PR merge")
        elif len(parents) != 1:
            raise AttestationError("main push has unsupported parent cardinality")
    else:
        raise AttestationError(f"unsupported canonical workflow event: {inputs.expected_event}")

    attestation = {
        "schema_version": "project-foundry-trusted-attestation.v1",
        "producer": {
            "repository": inputs.producer_repository,
            "commit_sha": inputs.producer_ref,
        },
        "target": {
            "repository": inputs.repository,
            "workflow_id": inputs.expected_workflow_id,
            "workflow_path": inputs.expected_workflow_path,
            "workflow_run_id": inputs.run_id,
            "run_attempt": inputs.run_attempt,
            "event": inputs.expected_event,
            "head_sha": inputs.expected_head_sha,
            "head_ref": inputs.expected_head_ref,
            "base_ref": inputs.expected_base_ref,
            "pr_number": inputs.expected_pr_number,
        },
        "result": "trusted",
    }
    if inputs.expected_event == "push" and commit is not None:
        parents = [item.get("sha") for item in commit.get("parents", []) if isinstance(item, dict)]
        attestation["integration"] = {
            "kind": "merge_commit" if len(parents) == 2 else "linear_main_commit",
            "parents": parents,
        }
    canonical = json.dumps(attestation, **CANONICAL_JSON_KWARGS).encode("utf-8")
    attestation["sha256"] = hashlib.sha256(canonical).hexdigest()
    return attestation


def attest(inputs: Inputs, token: str, api_get: Callable[[str, str], Any] = _api_get) -> dict[str, Any]:
    run = api_get(f"/repos/{inputs.repository}/actions/runs/{inputs.run_id}", token)
    workflow = api_get(
        f"/repos/{inputs.repository}/actions/workflows/{inputs.expected_workflow_id}", token
    )
    encoded_path = urllib.parse.quote(inputs.expected_workflow_path, safe="/")
    workflow_file = api_get(
        f"/repos/{inputs.repository}/contents/{encoded_path}?ref={inputs.expected_head_sha}",
        token,
    )
    _require(
        isinstance(workflow_file, dict)
        and workflow_file.get("encoding") == "base64"
        and isinstance(workflow_file.get("content"), str),
        "canonical workflow content payload is invalid",
    )
    try:
        workflow_bytes = base64.b64decode(workflow_file["content"], validate=False)
    except (ValueError, TypeError) as exc:
        raise AttestationError("canonical workflow content cannot be decoded") from exc

    pr = None
    commit = None
    merge_prs = None
    if inputs.expected_event == "pull_request":
        _require(inputs.expected_pr_number is not None, "PR number is required")
        pr = api_get(f"/repos/{inputs.repository}/pulls/{inputs.expected_pr_number}", token)
    elif inputs.expected_event == "push":
        commit = api_get(f"/repos/{inputs.repository}/commits/{inputs.expected_head_sha}", token)
        merge_prs = api_get(f"/repos/{inputs.repository}/commits/{inputs.expected_head_sha}/pulls", token)
        _require(isinstance(merge_prs, list), "commit-to-PR association payload is not a list")
    return validate_payloads(inputs, run, workflow, pr, commit, merge_prs, workflow_bytes)


def _env(name: str, *, required: bool = True) -> str:
    value = os.environ.get(name, "")
    if required and not value:
        raise AttestationError(f"missing required environment variable: {name}")
    return value


def _int_env(name: str, *, required: bool = True) -> int | None:
    value = _env(name, required=required)
    if not value and not required:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise AttestationError(f"{name} must be an integer") from exc


def inputs_from_env() -> Inputs:
    pr_number = _int_env("PF_ATTEST_PR_NUMBER", required=False)
    return Inputs(
        repository=_env("PF_ATTEST_REPOSITORY"),
        run_id=int(_int_env("PF_ATTEST_RUN_ID")),
        run_attempt=int(_int_env("PF_ATTEST_RUN_ATTEMPT")),
        expected_workflow_id=int(_int_env("PF_ATTEST_WORKFLOW_ID")),
        expected_workflow_path=_env("PF_ATTEST_WORKFLOW_PATH"),
        expected_head_sha=_env("PF_ATTEST_HEAD_SHA"),
        expected_event=_env("PF_ATTEST_EVENT"),
        expected_pr_number=pr_number,
        expected_head_ref=_env("PF_ATTEST_HEAD_REF"),
        expected_base_ref=_env("PF_ATTEST_BASE_REF"),
        producer_repository=_env("GITHUB_ACTION_REPOSITORY"),
        producer_ref=_env("GITHUB_ACTION_REF"),
    )


def _write_outputs(attestation: dict[str, Any]) -> None:
    rendered = json.dumps(attestation, indent=2, sort_keys=True) + "\n"
    output_path = os.environ.get("PF_ATTEST_OUTPUT_PATH")
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write("## Project Foundry trusted provenance\n\n```json\n")
            summary.write(rendered)
            summary.write("```\n")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with Path(github_output).open("a", encoding="utf-8") as output:
            output.write(f"attestation_sha256={attestation['sha256']}\n")


def main() -> int:
    try:
        inputs = inputs_from_env()
        token = _env("PF_ATTEST_TOKEN")
        attestation = attest(inputs, token)
        _write_outputs(attestation)
    except AttestationError as exc:
        print(f"PFAT-001: {exc}", file=sys.stderr)
        return 1
    print("Project Foundry trusted provenance: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
