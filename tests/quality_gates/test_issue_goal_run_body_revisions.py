from __future__ import annotations

import hashlib
import json
import re
import runpy
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.quality_gates.issue_goal_run_test_support import (
    close_inputs as _close_inputs,
)
from tests.quality_gates.issue_goal_run_test_support import (
    parent_body as _parent_body,
)

# Changed-line mapper discovery: this file drives the two modules below
# in-process (via runpy through the provider and binding entry points), so no
# import statement can name them. Their full paths are spelled literally here
# so the textual mapper resolves the coverage that already exists.
#   "skills/public/issue/scripts/issue_goal_run_body_chain.py"
#   "skills/public/issue/scripts/issue_goal_run_operations.py"

ROOT = Path(__file__).resolve().parents[2]
PROVIDER_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run.py"
OPERATIONS_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_operations.py"
GUARD_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_guard.py"
CLOSE_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_close.py"
BINDING_PATH = ROOT / "skills/public/issue/scripts/issue_goal_run_binding.py"
PICKUP_CONTRACT_PATH = ROOT / "skills/public/achieve/scripts/goal_run_pickup_contract.py"
REPO = "corca-ai/charness"

OLD_CHILD_BODY = "old child body\n"
NEW_CHILD_BODY = "<!-- charness-work-item-key: child-725 -->\nnew child prose\n"
UNRECORDED_BODY = "unrecorded replacement prose\n"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _revision(body: str, supersedes: str | None = OLD_CHILD_BODY) -> dict[str, object]:
    return {
        "key": "child-725",
        "number": 725,
        "body_sha256": _sha(body),
        "supersedes_sha256": _sha(supersedes) if supersedes is not None else None,
    }


def _binding(tmp_path: Path) -> dict[str, object]:
    _close_inputs(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    metadata = json.loads((tmp_path / ".goal-run-fixture.json").read_text(encoding="utf-8"))
    return module["load_binding"](
        tmp_path,
        "goal.binding.json",
        repo=REPO,
        parent_number=724,
        draft_sha256=metadata["draft_sha256"],
        binding_sha256=metadata["binding_sha256"],
    )


def test_chain_validation_accepts_absent_and_wellformed() -> None:
    module = runpy.run_path(str(PICKUP_CONTRACT_PATH))
    assert module["validate_body_revisions"](None) == []
    entry = _revision(NEW_CHILD_BODY)
    assert module["validate_body_revisions"]([entry]) == [entry]


@pytest.mark.parametrize(
    "value",
    [
        "not-a-list",
        [{"key": "child-725"}],
        [
            {
                "key": "child-725",
                "number": 725,
                "body_sha256": "z" * 64,
                "supersedes_sha256": None,
            }
        ],
        [
            {
                "key": "BAD KEY",
                "number": 725,
                "body_sha256": "a" * 64,
                "supersedes_sha256": None,
            }
        ],
        [
            {
                "key": "child-725",
                "number": 0,
                "body_sha256": "a" * 64,
                "supersedes_sha256": None,
            }
        ],
    ],
)
def test_chain_validation_refuses_malformed(value: object) -> None:
    module = runpy.run_path(str(PICKUP_CONTRACT_PATH))
    with pytest.raises(module["PickupError"]):
        module["validate_body_revisions"](value)


def test_descent_accepts_live_matching_recorded_chain(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    metadata = {"body_revisions": [_revision(NEW_CHILD_BODY)]}
    module["require_body_descent"](
        binding, [{"number": 725, "body": NEW_CHILD_BODY}], metadata
    )


def test_descent_grandfathers_pre_chain_items_despite_observed_digest(
    tmp_path: Path,
) -> None:
    # The fixture binding records an observed digest, but with no chain the
    # item is untouched by the new contract: even a body matching NEITHER the
    # observed digest NOR any chain entry still closes (marker path), so runs
    # established before the chain stay closeable.
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    module["require_body_descent"](
        binding, [{"number": 725, "body": "edited pre-chain prose\n"}], None
    )


def test_descent_accepts_item_without_recorded_anchor() -> None:
    module = runpy.run_path(str(BINDING_PATH))
    binding = {
        "approved_work_items": [
            {"key": "fresh", "issue": {"number": 9}, "observed": None},
        ]
    }
    module["require_body_descent"](
        binding, [{"number": 9, "body": "anything at all\n"}], None
    )


def test_update_validation_still_refuses_a_missing_marker(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    body = tmp_path / "nomarker.md"
    body.write_text("prose without identity\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="exactly once"):
        module["validate_managed_body"](
            binding, key="child-725", number=725, body=body.read_bytes(), metadata={}
        )


def test_descent_resolves_by_marker_when_numbers_do_not_match(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    forked = "<!-- charness-work-item-key: child-725 -->\nforked prose\n"
    metadata = {"body_revisions": [_revision(forked, supersedes=None)]}
    module["require_body_descent"](binding, [{"number": 999, "body": forked}], metadata)


def test_descent_skips_issues_with_no_identifiable_key(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    metadata = {"body_revisions": [_revision(NEW_CHILD_BODY)]}
    module["require_body_descent"](
        binding, [{"number": 999, "body": "no marker anywhere\n"}], metadata
    )


def test_descent_skips_non_matching_keys_before_the_match() -> None:
    module = runpy.run_path(str(BINDING_PATH))
    binding = {
        "approved_work_items": [
            {"key": "other", "issue": {"number": 2}, "observed": None},
            {
                "key": "mine",
                "issue": {"number": 1},
                "observed": {"body_sha256": _sha("b\n")},
            },
        ]
    }
    module["require_body_descent"](binding, [{"number": 1, "body": "b\n"}], None)


def test_descent_collects_observed_digest_past_non_matching_items() -> None:
    # With an adopted chain, _accepted_body_digests walks every work item:
    # the leading non-matching key is skipped while the matching item's
    # observed digest still joins the accepted set.
    module = runpy.run_path(str(BINDING_PATH))
    binding = {
        "approved_work_items": [
            {
                "key": "other",
                "issue": {"number": 2},
                "observed": {"body_sha256": _sha("other\n")},
            },
            {
                "key": "mine",
                "issue": {"number": 1},
                "observed": {"body_sha256": _sha("b\n")},
            },
        ]
    }
    metadata = {
        "body_revisions": [
            {
                "key": "mine",
                "number": 1,
                "body_sha256": _sha("b\n"),
                "supersedes_sha256": None,
            }
        ]
    }
    module["require_body_descent"](binding, [{"number": 1, "body": "b\n"}], metadata)


def test_descent_refuses_an_unreadable_body_with_an_anchor(tmp_path: Path) -> None:
    # Post-adoption (a chain exists), so the anchor enforces and an unreadable
    # live body cannot prove descent.
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    metadata = {"body_revisions": [_revision(NEW_CHILD_BODY)]}
    with pytest.raises(RuntimeError, match="no readable live body"):
        module["require_body_descent"](binding, [{"number": 725}], metadata)


def test_descent_refuses_unrecorded_replacement(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    module = runpy.run_path(str(BINDING_PATH))
    metadata = {"body_revisions": [_revision(NEW_CHILD_BODY)]}
    with pytest.raises(RuntimeError, match="unrecorded body replacement"):
        module["require_body_descent"](
            binding, [{"number": 725, "body": UNRECORDED_BODY}], metadata
        )


def _close_module(tmp_path: Path, parent: dict, child: dict) -> dict:
    module = runpy.run_path(str(CLOSE_PATH))
    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=lambda _repo, number, **_kwargs: {
            "issue": parent if number == 724 else child
        }
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {
            "children": [{"number": 725, "state": "CLOSED"}]
        },
    )
    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("close mutation must not run on refusal")
        ),
        close_after_verified_comment=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("close mutation must not run on refusal")
        ),
    )
    return module


def test_close_refuses_unrecorded_child_body_before_mutation(tmp_path: Path) -> None:
    # Post-adoption scenario: the run recorded an authorized revision, then the
    # live body was replaced outside the operation path. The live digest is in
    # neither the chain nor the observed evidence, so close refuses pre-write.
    proof = _close_inputs(tmp_path, attempt_id="close-chain-neg")
    parent = {
        "number": 724,
        "state": "OPEN",
        "body": _parent_body(tmp_path, body_revisions=[_revision(NEW_CHILD_BODY)]),
        "comments": [],
    }
    child = {
        "number": 725,
        "state": "CLOSED",
        "body": UNRECORDED_BODY,
        "comments": [{"url": "comment"}],
    }
    module = _close_module(tmp_path, parent, child)
    emitted: list[dict[str, object]] = []
    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )
    assert rc == 2
    assert emitted[0]["status"] == "close-refused"
    assert emitted[0]["mutation_invoked"] is False
    assert "revision chain" in emitted[0]["error"]


def test_close_accepts_chain_recorded_evolution(tmp_path: Path) -> None:
    proof = _close_inputs(tmp_path, attempt_id="close-chain-pos")
    parent = {
        "number": 724,
        "state": "OPEN",
        "body": _parent_body(tmp_path, body_revisions=[_revision(NEW_CHILD_BODY)]),
        "comments": [],
    }
    child = {
        "number": 725,
        "state": "CLOSED",
        "body": NEW_CHILD_BODY,
        "comments": [{"url": "comment"}],
    }
    module = runpy.run_path(str(CLOSE_PATH))
    module["command_close"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=lambda _repo, number, **_kwargs: {
            "issue": parent if number == 724 else child
        }
    )
    module["command_close"].__globals__["TRACKER"] = SimpleNamespace(
        list_sub_issues=lambda *_args, **_kwargs: {
            "children": [{"number": 725, "state": "CLOSED"}]
        },
        update_issue_body=lambda _repo, _number, body_file, **_kwargs: (
            parent.update(state="CLOSED", body=body_file.read_text(encoding="utf-8"))
            or {
                "ok": True,
                "status": "verified-write",
                "outcome": "verified-write",
                "mutation_invoked": True,
                "body_verified": True,
            }
        ),
    )
    module["command_close"].__globals__["CLOSE"] = SimpleNamespace(
        close_with_comment=lambda *_args, **kwargs: {
            "carrier": "test",
            "preflight_state": kwargs["preflight_state"],
        }
    )
    emitted: list[dict[str, object]] = []
    rc = module["command_close"](
        Namespace(repo=REPO, number=724, proof_file=proof, repo_root=tmp_path),
        resolve_backend=lambda _root, **_kwargs: {"adapter_ok": True, "backend": {"id": "gh"}},
        emit=emitted.append,
    )
    assert rc == 0
    assert emitted[0]["status"] == "verified-write"


RACE_BODY = "<!-- charness-work-item-key: child-725 -->\nconcurrent edit\n"


def _update_harness(
    tmp_path: Path,
    *,
    parent_body: object,
    child_body: object,
    fail_parent_write: bool = False,
    race_child: bool = False,
) -> SimpleNamespace:
    """Stateful provider double: tracks write order for record-first proofs."""
    _close_inputs(tmp_path)
    (tmp_path / "body.md").write_text(NEW_CHILD_BODY, encoding="utf-8")
    store = {724: parent_body, 725: child_body}
    calls: list[tuple[str, int]] = []

    def fake_read(_repo: str, number: int, **_kwargs: object) -> dict[str, object]:
        return {
            "issue": {
                "number": number,
                "state": "OPEN",
                "url": f"https://github.com/{REPO}/issues/{number}",
                "body": store[number],
                "comments": [],
            }
        }

    def fake_update(
        _repo: str,
        number: int,
        body_file: Path,
        *,
        backend: object = None,
        expected_body_sha256: str | None = None,
        pre_write_validator: object = None,
        parent_amendment_validator: object = None,
        terminal_metadata_update: bool = False,
    ) -> dict[str, object]:
        calls.append(("write", number))
        current = store[number]
        if race_child and number == 725:
            # A concurrent edit lands after the operation's live read.
            current = store[number] = RACE_BODY
        if expected_body_sha256 is not None and _sha(current) != expected_body_sha256:
            return {
                "ok": False,
                "status": "unverified-write",
                "outcome": "unverified-write",
                "mutation_invoked": True,
            }
        desired = body_file.read_text(encoding="utf-8")
        if callable(pre_write_validator):
            pre_write_validator(current, desired)
        if callable(parent_amendment_validator):
            parent_amendment_validator(current, desired)
        if fail_parent_write and number == 724:
            return {
                "ok": False,
                "status": "unverified-write",
                "outcome": "unverified-write",
                "mutation_invoked": True,
            }
        store[number] = desired
        return {
            "ok": True,
            "status": "verified-write",
            "outcome": "verified-write",
            "mutation_invoked": True,
            "body_verified": True,
        }

    module = runpy.run_path(str(PROVIDER_PATH))
    module["command_apply"].__globals__["READ"] = SimpleNamespace(
        read_issue_with_comments=fake_read
    )
    module["command_apply"].__globals__["TRACKER"] = SimpleNamespace(
        update_issue_body=fake_update
    )
    operation = tmp_path / "update-body.json"
    metadata = json.loads((tmp_path / ".goal-run-fixture.json").read_text(encoding="utf-8"))
    operation.write_text(
        json.dumps(
            {
                "kind": "charness.goal-run-operation/v1",
                "repo": REPO,
                "parent_number": 724,
                "operation": "update-body",
                "attempt_id": "attempt-update-body",
                "draft_sha256": metadata["draft_sha256"],
                "binding_sha256": metadata["binding_sha256"],
                "binding_path": "goal.binding.json",
                "observation_dir": "observations",
                "target": {
                    "repo": REPO,
                    "number": 725,
                    "work_item_key": "child-725",
                },
                "body_file": "body.md",
            }
        ),
        encoding="utf-8",
    )

    attempts = {"n": 0}

    def apply() -> tuple[int, list[dict[str, object]]]:
        attempts["n"] += 1
        payload = json.loads(operation.read_text(encoding="utf-8"))
        payload["attempt_id"] = f"attempt-update-body-{attempts['n']}"
        operation.write_text(json.dumps(payload), encoding="utf-8")
        emitted: list[dict[str, object]] = []
        rc = module["command_apply"](
            Namespace(repo=REPO, number=724, operation_file=operation, repo_root=tmp_path),
            resolve_backend=lambda *_args, **_kwargs: {
                "adapter_ok": True,
                "backend": {"id": "fixture"},
            },
            emit=emitted.append,
        )
        return rc, emitted

    return SimpleNamespace(apply=apply, store=store, calls=calls)


def _recorded_revisions(parent_body: object) -> list[dict[str, object]]:
    assert isinstance(parent_body, str)
    return json.loads(
        re.search(
            r"<!--\s*charness-goal-run:v1\s*\n(\{.*?\})\s*\n\s*-->",
            parent_body,
            re.DOTALL,
        ).group(1)
    )["body_revisions"]


def test_update_body_records_revision_before_child_write(tmp_path: Path) -> None:
    harness = _update_harness(
        tmp_path, parent_body=_parent_body(tmp_path), child_body=OLD_CHILD_BODY
    )
    rc, emitted = harness.apply()
    assert rc == 0
    assert emitted[0]["body_revision_recorded"] is True
    assert harness.calls == [("write", 724), ("write", 725)]
    assert _recorded_revisions(harness.store[724]) == [_revision(NEW_CHILD_BODY)]
    assert harness.store[725] == NEW_CHILD_BODY


def test_update_body_retry_is_idempotent(tmp_path: Path) -> None:
    harness = _update_harness(
        tmp_path, parent_body=_parent_body(tmp_path), child_body=OLD_CHILD_BODY
    )
    assert harness.apply()[0] == 0
    rc, emitted = harness.apply()
    assert rc == 0
    assert emitted[0]["body_revision_recorded"] is False
    assert _recorded_revisions(harness.store[724]) == [_revision(NEW_CHILD_BODY)]


def test_update_body_refuses_when_parent_has_no_metadata(tmp_path: Path) -> None:
    # The apply ingress refuses a parentless run before any provider write.
    harness = _update_harness(tmp_path, parent_body="plain body\n", child_body=OLD_CHILD_BODY)
    rc, emitted = harness.apply()
    assert rc == 2
    assert emitted[0]["status"] == "parent-unverified"
    assert harness.calls == []
    assert harness.store[725] == OLD_CHILD_BODY


def test_record_refuses_a_parent_without_metadata(tmp_path: Path) -> None:
    # Unit-level: the record path itself fails closed when the parent it
    # re-reads lost its metadata between ingress and execution (TOCTOU).
    module = runpy.run_path(str(OPERATIONS_PATH))
    guard = runpy.run_path(str(GUARD_PATH))
    with pytest.raises(RuntimeError, match="does not carry Goal Run metadata"):
        module["_render_revision_body"](
            "plain body\n",
            {"key": "child-725", "number": 725, "body_sha256": "a" * 64, "supersedes_sha256": None},
            guard=SimpleNamespace(
                parse_goal_run_metadata=guard["parse_goal_run_metadata"],
                BLOCK_RE=guard["BLOCK_RE"],
            ),
        )


def test_update_body_refuses_an_unreadable_parent_body(tmp_path: Path) -> None:
    harness = _update_harness(tmp_path, parent_body=None, child_body=OLD_CHILD_BODY)
    rc, emitted = harness.apply()
    assert rc == 2
    assert emitted[0]["status"] == "parent-unverified"
    assert harness.calls == []


def test_record_refuses_an_unreadable_parent_body(tmp_path: Path) -> None:
    module = runpy.run_path(str(OPERATIONS_PATH))
    read = SimpleNamespace(
        read_issue_with_comments=lambda *_a, **_k: {"issue": {"body": None}}
    )
    with pytest.raises(RuntimeError, match="did not return a string body"):
        module["_record_body_revision"](
            repo_root=tmp_path,
            repo=REPO,
            parent=724,
            key="child-725",
            number=725,
            submitted_sha256="a" * 64,
            supersedes_sha256="b" * 64,
            backend={},
            binding={},
            contract=SimpleNamespace(),
            read=read,
            tracker=SimpleNamespace(),
            guard=SimpleNamespace(),
        )


def test_update_body_refuses_an_unreadable_child_body(tmp_path: Path) -> None:
    harness = _update_harness(
        tmp_path, parent_body=_parent_body(tmp_path), child_body=None
    )
    rc, emitted = harness.apply()
    assert rc == 2
    assert emitted[0]["status"] == "provider-refused"
    assert "child body readback" in emitted[0]["error"]
    assert harness.calls == []


def test_update_body_writes_nothing_when_the_parent_record_fails(
    tmp_path: Path,
) -> None:
    harness = _update_harness(
        tmp_path,
        parent_body=_parent_body(tmp_path),
        child_body=OLD_CHILD_BODY,
        fail_parent_write=True,
    )
    rc, emitted = harness.apply()
    assert rc == 2
    assert emitted[0]["status"] == "provider-refused"
    assert "was not recorded" in emitted[0]["error"]
    assert harness.calls == [("write", 724)]
    assert harness.store[725] == OLD_CHILD_BODY


def test_concurrent_child_edit_refuses_instead_of_overwriting(tmp_path: Path) -> None:
    harness = _update_harness(
        tmp_path,
        parent_body=_parent_body(tmp_path),
        child_body=OLD_CHILD_BODY,
        race_child=True,
    )
    rc, emitted = harness.apply()
    assert rc == 2
    assert emitted[0]["status"] == "unverified-write"
    assert harness.calls == [("write", 724), ("write", 725)]
    assert harness.store[725] == RACE_BODY
    # The recorded edge is unused and harmless: closeout still fails closed on
    # the unrecorded live body rather than having overwritten it.
    assert _recorded_revisions(harness.store[724]) == [_revision(NEW_CHILD_BODY)]
