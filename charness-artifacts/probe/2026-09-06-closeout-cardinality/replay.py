"""Exercise the unchanged final consumers, retaining bound observation receipts."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from tests.quality_gates.test_issue_worker_carrier import (  # noqa: E402
    _load_resolution_critique, _worker_delivered_artifact,
)
from tests.quality_gates.test_issue_closeout_commit_msg_hook import _init_repo, _run  # noqa: E402


MESSAGE = """Closes #1, #2

Classification #1: bug
Classification #2: feature

JTBD: close two independently proven issues.
Root cause: scalar dispatch groups every target under one class.
Debug artifact: charness-artifacts/debug/latest.md.
Siblings: mixed close carrier | decision: same bug, fix now | proof: final hook payload.
Prevention: dispatch the existing floor table once per exact target.
Critique #1 #2: blocked synthetic-test-harness: no external reviewer is needed for this local parser stimulus
Behavior #1: local-only-by-contract
Behavior #2: local-only-by-contract
AI-provenance: agent-authored fixture for read-only investigation.
"""


def save_receipt(finding, expected, stimulus, observed, consumer, payload, returncode):
    receipt = {
        "schema": "charness.adversarial-evidence.receipt.v1",
        "finding": finding, "source": str((HERE / "report.json").relative_to(REPO)),
        "expected": expected, "stimulus": stimulus, "disposition": "reproduced",
        "observed": observed, "command": "python3 " + str(Path(__file__).relative_to(REPO)),
        "fixture": "sha256:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "final_consumer": consumer, "executed": True, "final_consumer_observed": True,
        "returncode": returncode, "payload": payload,
    }
    destination = HERE / f"{finding}.receipt.json"
    with destination.open("x") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(destination.relative_to(REPO)),
                      "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                      "observed": observed}))


def main():
    with tempfile.TemporaryDirectory(prefix="goal805-closeout-parent-") as raw:
        root = Path(raw)
        carrier = root / "carrier"
        artifact = _worker_delivered_artifact(carrier)
        check = {"satisfied": [{"name": "resolution_critique", "via": "evidence",
                                "path": str(artifact)}]}
        consumer = _load_resolution_critique()
        results = {}
        for label, numbers in (("singleton", [42]), ("plural", [42, 43])):
            results[label] = consumer._observer_disposition(
                carrier, check, expected_issue_numbers=numbers,
                expected_repository="corca-ai/charness",
            )
        assert results["singleton"]["carrier_verified"] is True, results
        assert results["plural"]["carrier_verified"] is False, results
        assert "does not bind exactly to corca-ai/charness#43" in results["plural"]["carrier_reason"]
        save_receipt(
            "target-cardinality", "Distinct targets need representable source-bound membership",
            "Consume the same valid worker fixture for singleton 42 then targets 42 and 43",
            "Singleton delegated; plural carrier-unverified because prepared_for cannot bind target 43",
            "skills/public/issue/scripts/issue_resolution_observer.py:_observer_disposition",
            results, 0,
        )
        hook_root = root / "hook"
        _init_repo(hook_root)
        message = hook_root / "message.txt"
        message.write_text(MESSAGE)
        result = _run(hook_root, message)
        assert result.returncode == 0, result.payload
        reports = result.payload["reports"]
        assert len(reports) == 1 and reports[0]["classification"] == "bug", reports
        save_receipt(
            "classification-cardinality", "Each close target must receive its declared classification floor",
            "Close bug 1 and feature 2 using target declarations but omit feature-only fields",
            "Hook passes with one bug report for both targets and no feature-floor report",
            "scripts/gates/check_issue_closeout_commit_msg.py:evaluate/report_payload",
            result.payload, result.returncode,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
