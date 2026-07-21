from __future__ import annotations

import hashlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "attestors" / "project_foundry_v1"))

import attest  # noqa: E402
from attest import AttestationError, Inputs, validate_payloads  # noqa: E402

WORKFLOW_BYTES = b"approved canonical workflow bytes\n"
attest.APPROVED_FOUNDATION_WORKFLOW_SHA256 = hashlib.sha256(WORKFLOW_BYTES).hexdigest()

SHA = "a" * 40
PRODUCER = "b" * 40
REPO = "rezahh107/Project-Foundry"
WORKFLOW_PATH = ".github/workflows/foundation-validation.yml"
WORKFLOW_ID = 315675709


def inputs(event: str = "pull_request") -> Inputs:
    return Inputs(
        repository=REPO,
        run_id=1001,
        run_attempt=2,
        expected_workflow_id=WORKFLOW_ID,
        expected_workflow_path=WORKFLOW_PATH,
        expected_head_sha=SHA,
        expected_event=event,
        expected_pr_number=3 if event == "pull_request" else None,
        expected_head_ref="agent/example" if event == "pull_request" else "main",
        expected_base_ref="main",
        producer_repository="rezahh107/Post-Merge-Auditor",
        producer_ref=PRODUCER,
    )


def run(event: str = "pull_request") -> dict:
    return {
        "id": 1001,
        "run_attempt": 2,
        "workflow_id": WORKFLOW_ID,
        "head_sha": SHA,
        "event": event,
        "status": "completed",
        "conclusion": "success",
        "repository": {"full_name": REPO},
        "head_repository": {"full_name": REPO},
        "head_branch": "agent/example" if event == "pull_request" else "main",
        "name": "Foundation validation",
        "pull_requests": [{"number": 3}] if event == "pull_request" else [],
    }


def commit(parents: int = 1) -> dict:
    values = [{"sha": "c" * 40}]
    if parents == 2:
        values.append({"sha": "d" * 40})
    return {"sha": SHA, "parents": values}


def merged_pr() -> dict:
    return {
        "number": 7,
        "merged_at": "2026-07-20T00:00:00Z",
        "merge_commit_sha": SHA,
        "head": {"sha": "d" * 40, "ref": "agent/example"},
        "base": {"sha": "c" * 40, "ref": "main", "repo": {"full_name": REPO}},
    }


def workflow() -> dict:
    return {"id": WORKFLOW_ID, "path": WORKFLOW_PATH, "state": "active", "name": "Foundation validation"}


def pr() -> dict:
    return {
        "number": 3,
        "head": {"sha": SHA, "ref": "agent/example"},
        "base": {"ref": "main", "repo": {"full_name": REPO}},
    }


class ProjectFoundryAttestorTests(unittest.TestCase):
    def assert_rejected(self, inp: Inputs, run_payload: dict, workflow_payload: dict, pr_payload: dict | None) -> None:
        with self.assertRaises(AttestationError):
            validate_payloads(inp, run_payload, workflow_payload, pr_payload, workflow_bytes=WORKFLOW_BYTES)

    def test_valid_canonical_pr_run(self) -> None:
        result = validate_payloads(inputs(), run(), workflow(), pr(), workflow_bytes=WORKFLOW_BYTES)
        self.assertEqual(result["result"], "trusted")
        self.assertEqual(len(result["sha256"]), 64)

    def test_valid_canonical_main_push(self) -> None:
        result = validate_payloads(inputs("push"), run("push"), workflow(), None, commit(), [], WORKFLOW_BYTES)
        self.assertEqual(result["target"]["event"], "push")
        self.assertEqual(result["integration"]["kind"], "linear_main_commit")

    def test_duplicate_name_decoy_wrong_workflow_id_is_rejected(self) -> None:
        payload = run()
        payload["workflow_id"] = WORKFLOW_ID + 1
        self.assert_rejected(inputs(), payload, workflow(), pr())

    def test_wrong_workflow_path_is_rejected(self) -> None:
        payload = workflow()
        payload["path"] = ".github/workflows/decoy.yml"
        self.assert_rejected(inputs(), run(), payload, pr())

    def test_wrong_pr_number_is_rejected(self) -> None:
        payload = run()
        payload["pull_requests"] = [{"number": 9}]
        self.assert_rejected(inputs(), payload, workflow(), pr())

    def test_wrong_pr_head_ref_is_rejected(self) -> None:
        payload = pr()
        payload["head"]["ref"] = "agent/other"
        self.assert_rejected(inputs(), run(), workflow(), payload)

    def test_wrong_pr_repository_is_rejected(self) -> None:
        payload = pr()
        payload["base"]["repo"]["full_name"] = "attacker/repo"
        self.assert_rejected(inputs(), run(), workflow(), payload)

    def test_non_main_push_is_rejected(self) -> None:
        payload = run("push")
        payload["head_branch"] = "release"
        self.assert_rejected(inputs("push"), payload, workflow(), None)

    def test_stale_run_attempt_is_rejected(self) -> None:
        payload = run()
        payload["run_attempt"] = 1
        self.assert_rejected(inputs(), payload, workflow(), pr())

    def test_valid_hosted_merge_commit(self) -> None:
        result = validate_payloads(inputs("push"), run("push"), workflow(), None, commit(2), [merged_pr()], WORKFLOW_BYTES)
        self.assertEqual(result["integration"]["kind"], "merge_commit")

    def test_two_parent_push_without_exact_hosted_merge_is_rejected(self) -> None:
        self.assert_rejected(inputs("push"), run("push"), workflow(), None)
        with self.assertRaises(AttestationError):
            validate_payloads(inputs("push"), run("push"), workflow(), None, commit(2), [], WORKFLOW_BYTES)

    def test_modified_canonical_workflow_bytes_are_rejected(self) -> None:
        with self.assertRaises(AttestationError):
            validate_payloads(inputs(), run(), workflow(), pr(), workflow_bytes=b"modified workflow")

    def test_unpinned_producer_is_rejected(self) -> None:
        inp = inputs()
        inp = Inputs(**{**inp.__dict__, "producer_ref": "main"})
        self.assert_rejected(inp, run(), workflow(), pr())

    def test_inputs_from_env_accepts_context_bound_producer_identity(self) -> None:
        environment = {
            "PF_ATTEST_REPOSITORY": REPO,
            "PF_ATTEST_RUN_ID": "1001",
            "PF_ATTEST_RUN_ATTEMPT": "2",
            "PF_ATTEST_WORKFLOW_ID": str(WORKFLOW_ID),
            "PF_ATTEST_WORKFLOW_PATH": WORKFLOW_PATH,
            "PF_ATTEST_HEAD_SHA": SHA,
            "PF_ATTEST_EVENT": "pull_request",
            "PF_ATTEST_PR_NUMBER": "3",
            "PF_ATTEST_HEAD_REF": "agent/example",
            "PF_ATTEST_BASE_REF": "main",
            "GITHUB_ACTION_REPOSITORY": "rezahh107/Post-Merge-Auditor",
            "GITHUB_ACTION_REF": PRODUCER,
        }
        with patch.dict(os.environ, environment, clear=True):
            parsed = attest.inputs_from_env()
        self.assertEqual(parsed.producer_repository, "rezahh107/Post-Merge-Auditor")
        self.assertEqual(parsed.producer_ref, PRODUCER)

    def test_action_maps_github_action_context_into_verifier_environment(self) -> None:
        action = (ROOT / "attestors" / "project_foundry_v1" / "action.yml").read_text(encoding="utf-8")
        required_fragments = (
            "PF_ATTEST_PRODUCER_REPOSITORY: ${{ github.action_repository }}",
            "PF_ATTEST_PRODUCER_REF: ${{ github.action_ref }}",
            'export GITHUB_ACTION_REPOSITORY="$PF_ATTEST_PRODUCER_REPOSITORY"',
            'export GITHUB_ACTION_REF="$PF_ATTEST_PRODUCER_REF"',
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, action)


if __name__ == "__main__":
    unittest.main()
