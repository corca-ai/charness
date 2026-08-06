from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import scripts.slice_manifest_lib as slice_manifest_lib
from scripts.slice_manifest_lib import ManifestError, validate_manifest
from tests.repo_copy import clone_seeded_charness_repo

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
SOURCE_ROOT = ROOT
SOURCE_MANIFEST = MANIFEST


def _load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture
def fixture_path(tmp_path: Path, seeded_charness_git_repo: Path, monkeypatch: pytest.MonkeyPatch):
    repo = clone_seeded_charness_repo(tmp_path, seeded_charness_git_repo)
    for relative in (
        "charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md",
        "charness-artifacts/critique/2026-08-06-slice-1-manifest-implementation-review.md",
    ):
        source = SOURCE_ROOT / relative
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    data = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    seed_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    data["target"]["sha"] = seed_head
    data["carrier"]["sha"] = seed_head
    data["premise"]["published_target_sha"] = seed_head
    data["premise"]["local_head_sha"] = seed_head
    data["premise"]["remote_observation"]["sha"] = seed_head
    data["ci_readback"]["head_sha"] = seed_head
    for job in data["ci_readback"]["jobs"]:
        job["head_sha"] = seed_head
    data["remote_readback"]["target_sha"] = seed_head
    data["remote_readback"]["open_issues"]["target_sha"] = seed_head
    for reader_root in data["reader_roots"]:
        reader_root["identity_sha256"] = slice_manifest_lib._root_identity_digest(
            repo, reader_root["identity_paths"]
        )
    for parity_pair in data["parity_pairs"]:
        parity_pair["source_sha256"] = slice_manifest_lib._sha256_file(
            repo / parity_pair["source"]
        )
        parity_pair["derived_sha256"] = slice_manifest_lib._sha256_file(
            repo / parity_pair["derived"]
        )
    manifest = repo / "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    (repo / ".charness").mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "ROOT", repo)
    monkeypatch.setattr(sys.modules[__name__], "MANIFEST", manifest)
    return repo / ".charness" / f"slice_manifest_test_{tmp_path.name}.json"


def _write_fixture(fixture: Path, data: dict) -> Path:
    fixture.write_text(json.dumps(data), encoding="utf-8")
    return fixture


def test_committed_baseline_manifest_is_valid() -> None:
    result = validate_manifest(ROOT, MANIFEST)
    assert result["status"] == "structurally-valid-captured-record"
    assert result["target_sha"] == "e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5"
    assert result["ci_run_id"] == 31062451122
    assert result["captured_open_issue_count"] == 0
    assert result["live_revalidation"] == "not-run"


def test_current_identity_mode_and_parity_check_are_opt_in(fixture_path: Path) -> None:
    result = validate_manifest(ROOT, MANIFEST, verify_current=True)
    assert result["status"] == "structurally-valid-captured-record"


def test_captured_validation_does_not_rehash_frozen_files(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(slice_manifest_lib, "_sha256_file", lambda path: pytest.fail(f"unexpected current read: {path}"))
    result = validate_manifest(ROOT, MANIFEST)
    assert result["status"] == "structurally-valid-captured-record"


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("target", "sha"), "e7c3e1b3", "invalid_identity"),
        (("target", "sha"), "main", "invalid_identity"),
        (("carrier", "sha"), "0" * 40, "identity_mismatch"),
        (("ci_readback", "head_sha"), "0" * 40, "identity_mismatch"),
    ],
)
def test_identity_mismatches_refuse(fixture_path: Path, path: tuple[str, ...], value: str, code: str) -> None:
    data = _load()
    current = data
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == code


def test_stale_current_reader_identity_refuses(fixture_path: Path) -> None:
    data = _load()
    data["reader_roots"][0]["identity_mode"] = "current"
    data["reader_roots"][0]["identity_sha256"] = "0" * 64
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == "stale_reader_root"


def test_missing_captured_issue_readback_refuses(fixture_path: Path) -> None:
    data = _load()
    data["remote_readback"]["open_issues"]["status"] = "live"
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == "uncaptured_evidence"


def test_source_plugin_parity_refuses(fixture_path: Path) -> None:
    data = _load()
    data["parity_pairs"][0]["identity_mode"] = "current"
    data["parity_pairs"][0]["source"] = "packaging/charness.json"
    data["parity_pairs"][0]["derived"] = "README.md"
    data["parity_pairs"][0]["source_sha256"] = "0" * 64
    data["parity_pairs"][0]["derived_sha256"] = "0" * 64
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture, verify_current=True)
    assert caught.value.code == "parity_mismatch"


def test_fixture_mutation_does_not_change_committed_manifest() -> None:
    before = _load()
    changed = copy.deepcopy(before)
    changed["slice_id"] = "changed"
    assert _load() == before
    assert changed["slice_id"] != before["slice_id"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (("premise", "remote_observation", "repository"), "other/repo"),
        (("ci_readback", "repository"), "other/repo"),
        (("ci_readback", "remote_ref"), "refs/heads/other"),
        (("remote_readback", "remote_ref"), "refs/heads/other"),
        (("remote_readback", "open_issues", "target_sha"), "0" * 40),
        (("remote_readback", "open_issues", "repository"), "other/repo"),
    ],
)
def test_remote_observer_identity_mismatch_refuses(fixture_path: Path, field: tuple[str, ...], value: str) -> None:
    data = _load()
    current = data
    for key in field[:-1]:
        current = current[key]
    current[field[-1]] = value
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == "identity_mismatch"


def test_critique_identity_mismatch_refuses(fixture_path: Path) -> None:
    data = _load()
    data["critique"]["reviewed_identity_sha256"] = "0" * 64
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture, verify_current=True)
    assert caught.value.code == "unbound_critique"


def test_empty_owner_reference_refuses(fixture_path: Path) -> None:
    data = _load()
    data["reader_roots"][0]["owner"] = "#missing"
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == "invalid_owner"


def test_nonexistent_owner_anchor_refuses(fixture_path: Path) -> None:
    data = _load()
    data["reader_roots"][0]["owner"] = "packaging/charness.json#source.missing"
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == "invalid_owner"


def test_non_ancestor_local_capture_head_refuses(fixture_path: Path) -> None:
    data = _load()
    empty_tree = subprocess.check_output(["git", "mktree"], cwd=ROOT, input="", text=True).strip()
    unrelated = subprocess.check_output(["git", "commit-tree", empty_tree, "-m", "unrelated fixture"], cwd=ROOT, text=True).strip()
    data["premise"]["local_head_sha"] = unrelated
    fixture = _write_fixture(fixture_path, data)
    with pytest.raises(ManifestError) as caught:
        validate_manifest(ROOT, fixture)
    assert caught.value.code == "identity_mismatch"


def test_cli_refuses_manifest_outside_repo_as_json(tmp_path: Path) -> None:
    external = tmp_path / "manifest.json"
    external.write_text("{}", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_slice_manifest.py"),
            "--repo-root",
            str(ROOT),
            "--manifest",
            str(external),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "unsafe_path"
    assert result.stderr == ""


def test_cli_plugin_layout_names_source_checkout_boundary() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "plugins/charness/scripts/validate_slice_manifest.py"),
            "--repo-root",
            str(ROOT / "plugins/charness"),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "missing_manifest" in result.stdout
    assert "source-checkout-only" in result.stdout
    assert "--manifest" in result.stdout


def test_cli_refuses_manifest_directory_as_json(tmp_path: Path) -> None:
    isolated_root = tmp_path / "repo"
    isolated_root.mkdir()
    manifest_dir = isolated_root / "manifest-dir"
    manifest_dir.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(SOURCE_ROOT / "scripts/validate_slice_manifest.py"),
            "--repo-root",
            str(isolated_root),
            "--manifest",
            str(manifest_dir),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "invalid_manifest_path"


def _manifest_raises(code: str, function: Any, *args: Any, **kwargs: Any) -> None:
    with pytest.raises(ManifestError) as caught:
        function(*args, **kwargs)
    assert caught.value.code == code


def test_manifest_private_validation_refusal_branches(fixture_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = ROOT
    _manifest_raises("invalid_type", slice_manifest_lib._require_mapping, [], "field")
    _manifest_raises("invalid_type", slice_manifest_lib._require_string, "", "field")
    _manifest_raises("invalid_type", slice_manifest_lib._require_int, True, "field")
    _manifest_raises("invalid_identity", slice_manifest_lib._require_sha, "bad", "field")
    _manifest_raises("invalid_identity", slice_manifest_lib._require_sha, "bad", "field", kind="sha256")
    _manifest_raises("unsafe_path", slice_manifest_lib._safe_repo_path, "a\\b", "field")
    _manifest_raises("unsafe_path", slice_manifest_lib._safe_repo_path, "../bad", "field")
    _manifest_raises("unsafe_path", slice_manifest_lib._safe_repo_path, "dir/", "field")
    _manifest_raises("unsafe_path", slice_manifest_lib._repo_candidate, repo, "../outside", "field")
    _manifest_raises("missing_path", slice_manifest_lib._require_repo_entry, repo, "missing", "field")
    directory = tmp_path / "directory"
    directory.mkdir()
    _manifest_raises("invalid_root", slice_manifest_lib._require_repo_entry, tmp_path, "directory", "field", file_only=True)
    _manifest_raises("missing_git_object", slice_manifest_lib._require_git_commit, repo, "0" * 40, "field")

    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "owner.py", "owner")
    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "#anchor", "owner")
    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "owner.py#bad anchor", "owner")
    invalid_json = repo / "owner.json"
    invalid_json.write_text("{", encoding="utf-8")
    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "owner.json#value", "owner")
    invalid_python = repo / "owner.py"
    invalid_python.write_text("def (\n", encoding="utf-8")
    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "owner.py#value", "owner")
    invalid_python.write_text("value = 1\n", encoding="utf-8")
    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "owner.py#value", "owner")
    text_owner = repo / "owner.txt"
    text_owner.write_text("value\n", encoding="utf-8")
    _manifest_raises("invalid_owner", slice_manifest_lib._validate_owner_ref, repo, "owner.txt#value", "owner")

    observation = {
        "status": "captured", "channel": "test", "observed_at": "now",
        "repository": "acme/charness", "ref": "refs/heads/main", "sha": "a" * 40,
        "command": ["git", "show"],
    }
    bad_observation = dict(observation, status="live")
    _manifest_raises("uncaptured_evidence", slice_manifest_lib._validate_observation, repo, bad_observation, "obs", "a" * 40, "acme/charness", "refs/heads/main")
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_observation, repo, dict(observation, ref="refs/heads/other"), "obs", "a" * 40, "acme/charness", "refs/heads/main")
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_observation, repo, dict(observation, sha="b" * 40), "obs", "a" * 40, "acme/charness", "refs/heads/main")
    _manifest_raises("invalid_command_descriptor", slice_manifest_lib._validate_observation, repo, dict(observation, command=[]), "obs", "a" * 40, "acme/charness", "refs/heads/main")

    roots = _load()["reader_roots"][0]
    _manifest_raises("invalid_reader_roots", slice_manifest_lib._validate_reader_roots, repo, [], verify_current=False)
    _manifest_raises("duplicate_reader_root", slice_manifest_lib._validate_reader_roots, repo, [roots, roots], verify_current=False)
    _manifest_raises("invalid_reader_role", slice_manifest_lib._validate_reader_roots, repo, [dict(roots, role="bad")], verify_current=False)
    _manifest_raises("invalid_reader_root", slice_manifest_lib._validate_reader_roots, repo, [dict(roots, identity_mode="bad")], verify_current=False)
    _manifest_raises("invalid_reader_root", slice_manifest_lib._validate_reader_roots, repo, [dict(roots, identity_paths=[])], verify_current=False)
    duplicate_paths = dict(roots, identity_paths=[roots["identity_paths"][0], roots["identity_paths"][0]])
    _manifest_raises("duplicate_identity_path", slice_manifest_lib._validate_reader_roots, repo, [duplicate_paths], verify_current=False)

    pair = _load()["parity_pairs"][0]
    _manifest_raises("invalid_parity", slice_manifest_lib._validate_parity, repo, [], verify_current=False)
    _manifest_raises("invalid_parity", slice_manifest_lib._validate_parity, repo, [dict(pair, identity_mode="bad")], verify_current=False)
    _manifest_raises("parity_mismatch", slice_manifest_lib._validate_parity, repo, [dict(pair, identity_mode="current", source_sha256="0" * 64)], verify_current=False)

    ci = _load()["ci_readback"]
    ci_sha = ci["head_sha"]
    _manifest_raises("uncaptured_evidence", slice_manifest_lib._validate_ci_readback, dict(ci, status="live"), ci_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("invalid_ci_readback", slice_manifest_lib._validate_ci_readback, dict(ci, non_claim="too narrow"), ci_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_ci_readback, dict(ci, remote_ref="refs/heads/other"), ci_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_ci_readback, dict(ci, head_sha="b" * 40), ci_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("invalid_ci_readback", slice_manifest_lib._validate_ci_readback, dict(ci, run_id=0), ci_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("unsuccessful_ci_readback", slice_manifest_lib._validate_ci_readback, dict(ci, conclusion="failure"), ci_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("incomplete_ci_readback", slice_manifest_lib._validate_ci_readback, dict(ci, jobs=[]), ci_sha, "corca-ai/charness", "refs/heads/main")
    bad_job = dict(ci["jobs"][0], id=0)
    _manifest_raises("invalid_ci_readback", slice_manifest_lib._validate_ci_readback, dict(ci, jobs=[bad_job]), ci_sha, "corca-ai/charness", "refs/heads/main")

    issue = _load()["remote_readback"]["open_issues"]
    issue_sha = issue["target_sha"]
    _manifest_raises("uncaptured_evidence", slice_manifest_lib._validate_issue_readback, dict(issue, status="live"), issue_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("invalid_command_descriptor", slice_manifest_lib._validate_issue_readback, dict(issue, query=[]), issue_sha, "corca-ai/charness", "refs/heads/main")
    _manifest_raises("invalid_readback", slice_manifest_lib._validate_issue_readback, dict(issue, open_count=-1), issue_sha, "corca-ai/charness", "refs/heads/main")


def test_manifest_critique_target_and_loader_error_branches(fixture_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = ROOT
    data = _load()
    critique = dict(data["critique"], packet_path="different.md")
    _manifest_raises("unbound_critique", slice_manifest_lib._validate_critique, repo, critique, verify_current=False)
    critique = dict(data["critique"], status="live")
    _manifest_raises("uncaptured_evidence", slice_manifest_lib._validate_critique, repo, critique, verify_current=False)

    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    _manifest_raises("unsafe_path", slice_manifest_lib._load_manifest, repo, outside)
    _manifest_raises("missing_manifest", slice_manifest_lib._load_manifest, repo, repo / "missing.json")
    manifest_dir = repo / "manifest-dir"
    manifest_dir.mkdir()
    _manifest_raises("invalid_manifest_path", slice_manifest_lib._load_manifest, repo, manifest_dir)
    malformed = repo / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    _manifest_raises("invalid_json", slice_manifest_lib._load_manifest, repo, malformed)
    invalid_utf8 = repo / "invalid-utf8.json"
    invalid_utf8.write_bytes(b"\xff")
    _manifest_raises("invalid_json", slice_manifest_lib._load_manifest, repo, invalid_utf8)

    target_data = _load()
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_target_and_premise, repo, {**target_data, "target": dict(target_data["target"], remote_repository="other/repo")}, "corca-ai/charness")
    _manifest_raises("invalid_target", slice_manifest_lib._validate_target_and_premise, repo, {**target_data, "target": dict(target_data["target"], kind="other")}, "corca-ai/charness")
    _manifest_raises("invalid_carrier_relation", slice_manifest_lib._validate_target_and_premise, repo, {**target_data, "carrier": dict(target_data["carrier"], relation_to_target="other")}, "corca-ai/charness")
    _manifest_raises("uncaptured_evidence", slice_manifest_lib._validate_target_and_premise, repo, {**target_data, "premise": dict(target_data["premise"], status="draft")}, "corca-ai/charness")
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_target_and_premise, repo, {**target_data, "premise": dict(target_data["premise"], published_target_sha="0" * 40)}, "corca-ai/charness")
    unrelated = subprocess.check_output(["git", "commit-tree", subprocess.check_output(["git", "mktree"], cwd=repo, input="", text=True).strip(), "-m", "unrelated"], cwd=repo, text=True).strip()
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_target_and_premise, repo, {**target_data, "premise": dict(target_data["premise"], local_head_sha=unrelated)}, "corca-ai/charness")
    _manifest_raises("identity_mismatch", slice_manifest_lib._validate_remote_readbacks, {**target_data, "remote_readback": dict(target_data["remote_readback"], actions_run_id=0)}, target_data["target"]["sha"], "corca-ai/charness", "refs/heads/main")
    _manifest_raises("unsupported_schema", slice_manifest_lib.validate_manifest, repo, _write_fixture(fixture_path, {**target_data, "schema_version": 2}))
    timestamp_fixture = _write_fixture(fixture_path, {**target_data, "captured_at": "2026-08-06T00:00:00"})
    _manifest_raises("invalid_timestamp", slice_manifest_lib.validate_manifest, repo, timestamp_fixture)

    original_read_text = slice_manifest_lib.Path.read_text
    monkeypatch.setattr(slice_manifest_lib.Path, "read_text", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("unreadable")))
    _manifest_raises("unbound_critique", slice_manifest_lib._validate_critique, repo, data["critique"], verify_current=True)

    critique = dict(data["critique"], packet_sha256="0" * 64)
    monkeypatch.setattr(slice_manifest_lib.Path, "read_text", original_read_text)
    _manifest_raises("stale_critique_packet", slice_manifest_lib._validate_critique, repo, critique, verify_current=True)
