"""Reviewed-input identity semantics and the critique artifact binding.

Split from `test_critique_prepare_packet.py`, which owns adapter loading, section
execution, and packet rendering. These tests own the other half: what enters the
identity digest, when a binding goes stale, and when a declared binding is
rejected outright.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import date
from functools import cache
from pathlib import Path

import pytest
import yaml

from scripts.critique_packet_lib import (
    build_reviewed_input_identity,
)
from scripts.reviewed_input_verification import verify_reviewed_input_identity
from scripts.validate_critique_artifacts import (
    ValidationError as CritiqueValidationError,
)
from scripts.validate_critique_artifacts import (
    validate_reviewed_input_binding,
)
from tests.reviewed_input_identity_fixtures import (
    repo_seed as identity_repo_seed,
)
from tests.reviewed_input_identity_fixtures import reviewed_identity_seed
from tests.reviewed_input_identity_fixtures import (
    tree_snapshot as _tree_snapshot,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _init_identity_repo(repo: Path) -> None:
    shutil.copytree(identity_repo_seed(), repo, dirs_exist_ok=True)


@cache
def _cached_seed_identity() -> dict:
    """Capture one immutable seed identity for integrity-only semantics tests."""
    return reviewed_identity_seed()


def _empty_identity() -> dict:
    """Build a deliberately empty binding without invoking repository capture."""
    from scripts.reviewed_input_identity import _with_identity_digest

    return _with_identity_digest(
        {
            "algorithm": "sha256-v2",
            "status": "captured",
            "mode": "working-tree",
            "substrate_mode": "working-tree",
            "changed_ref": None,
            "reviewed_paths": [],
        }
    )


def _write_static_packet(repo: Path, identity: dict) -> Path:
    """Write the smallest valid packet for binding-only tests."""
    packet = {
        "kind": "charness.critique_prepare_packet",
        "version": 1,
        "repo": "identity-fixture",
        "prepared_for": "working tree",
        "changed_ref": None,
        "substrate_mode": "working-tree",
        "reviewed_input_identity": identity,
    }
    path = repo / "charness-artifacts" / "critique" / "bound-packet.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(packet, separators=(",", ":")).encode("utf-8"))
    return path


@pytest.fixture(scope="session")
def cached_identity_repo_seed() -> Path:
    return identity_repo_seed()


def test_cached_identity_seed_is_never_mutated_by_a_test_clone(
    tmp_path: Path, cached_identity_repo_seed: Path
) -> None:
    before_seed = _tree_snapshot(cached_identity_repo_seed)
    clone = tmp_path / "clone"
    shutil.copytree(cached_identity_repo_seed, clone)
    (clone / "reviewed.txt").write_text("clone only\n", encoding="utf-8")
    _run_git(clone, "add", ".")
    _run_git(clone, "commit", "-m", "clone-only")

    assert _tree_snapshot(cached_identity_repo_seed) == before_seed


def test_reviewed_input_identity_is_ordered_and_content_addressed(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    (tmp_path / "reviewed.txt").write_text("unstaged\n", encoding="utf-8")
    (tmp_path / "new.txt").write_text("initial\n", encoding="utf-8")
    first = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt", "new.txt"],
    )
    reversed_order = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["new.txt", "reviewed.txt"],
    )
    assert first == reversed_order

    # Staging changes the index, not the bytes the reviewers read, so it must not
    # stale the binding — the failure that made writing a critique reject itself.
    _run_git(tmp_path, "add", "reviewed.txt")
    staged = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt", "new.txt"])
    assert staged["identity_sha256"] == first["identity_sha256"]
    assert staged["staged_patch_sha256"] != first["staged_patch_sha256"]

    (tmp_path / "new.txt").write_text("untracked\n", encoding="utf-8")
    untracked = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt", "new.txt"])
    assert untracked["identity_sha256"] != staged["identity_sha256"]
    assert untracked["declared_untracked"] == [
        {"path": "new.txt", "content_sha256": untracked["reviewed_content"][0]["content_sha256"]}
    ]

    # ...and staging that new file is likewise invisible to the digest, even though
    # it leaves the untracked set.
    _run_git(tmp_path, "add", "new.txt")
    staged_new = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt", "new.txt"])
    assert staged_new["identity_sha256"] == untracked["identity_sha256"]
    assert staged_new["declared_untracked"] == []

    (tmp_path / "reviewed.txt").write_text("edited after review\n", encoding="utf-8")
    edited = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt", "new.txt"])
    assert edited["identity_sha256"] != staged_new["identity_sha256"]


def test_noncurrent_identity_algorithm_is_refused(tmp_path: Path) -> None:
    current = _cached_seed_identity()
    retired = dict(current, algorithm="sha256-v1")
    ok, reason = verify_reviewed_input_identity(tmp_path, retired)
    assert not ok
    assert "must use `sha256-v2`" in reason


def test_directory_reviewed_path_is_rejected(tmp_path: Path) -> None:
    """A directory's content digest is `null` and stays `null` however the files
    beneath it change, so a binding over one could never go stale."""
    _init_identity_repo(tmp_path)
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg/mod.py").write_text("code\n", encoding="utf-8")

    with pytest.raises(ValueError, match="is a directory"):
        build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["pkg"])


def test_mode_only_change_stales_a_v2_binding(tmp_path: Path) -> None:
    """`chmod +x` on a reviewed script leaves its bytes identical; v1 caught it
    through the digested patch, so v2 folds the exec bit into the content hash."""
    _init_identity_repo(tmp_path)
    before = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt"])
    (tmp_path / "reviewed.txt").chmod(0o755)
    after = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt"])
    assert after["identity_sha256"] != before["identity_sha256"]
    assert verify_reviewed_input_identity(tmp_path, before)[1] == "declared reviewed inputs are stale"


def test_zero_path_binding_is_not_current(tmp_path: Path) -> None:
    """An empty path set digests to the same constant in every repo forever."""
    empty = _empty_identity()
    assert verify_reviewed_input_identity(tmp_path, empty) == (
        False,
        "declared reviewed inputs cover zero paths",
    )


def test_auto_sweep_drops_excluded_prefixes_but_never_explicit_paths(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    record_dir = tmp_path / "charness-artifacts/critique"
    record_dir.mkdir(parents=True)
    (record_dir / "today-critique.md").write_text("verdict\n", encoding="utf-8")
    # A sibling whose name merely starts with the same characters must survive:
    # the exclusion is a directory prefix, not a string prefix.
    sibling = tmp_path / "charness-artifacts/critique-notes"
    sibling.mkdir(parents=True)
    (sibling / "note.md").write_text("kept\n", encoding="utf-8")
    (tmp_path / "reviewed.txt").write_text("changed\n", encoding="utf-8")

    swept = build_reviewed_input_identity(
        repo_root=tmp_path, excluded_prefixes=["charness-artifacts/critique/"]
    )
    assert swept["reviewed_paths"] == ["charness-artifacts/critique-notes/note.md", "reviewed.txt"]
    assert swept["auto_excluded_paths"] == ["charness-artifacts/critique/today-critique.md"]

    explicit = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["charness-artifacts/critique/today-critique.md"],
        excluded_prefixes=["charness-artifacts/critique/"],
    )
    assert explicit["reviewed_paths"] == ["charness-artifacts/critique/today-critique.md"]
    assert explicit["auto_excluded_paths"] == []


def test_working_tree_identity_requires_explicit_symlink_target(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    symlink = tmp_path / "link.txt"
    symlink.symlink_to("reviewed.txt")
    with pytest.raises(ValueError, match="is a symlink; declare the target file explicitly"):
        build_reviewed_input_identity(
            repo_root=tmp_path,
            reviewed_paths=["reviewed.txt", "link.txt"],
        )

    # The target is a separate, explicit reviewed path; the identity then has
    # ordinary working-tree semantics and does not hash the symlink spelling.
    before = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt"])
    (tmp_path / "unrelated.txt").write_text("unrelated commit\n", encoding="utf-8")
    _run_git(tmp_path, "add", "unrelated.txt")
    _run_git(tmp_path, "commit", "-m", "unrelated")
    after_unrelated_commit = build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=["reviewed.txt"]
    )
    assert after_unrelated_commit["base_head"] != before["base_head"]
    assert after_unrelated_commit["identity_sha256"] == before["identity_sha256"]


def test_reviewed_input_identity_rejects_traversal_and_symlinked_directory(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("outside\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside repo root"):
        build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["../outside.txt"])

    (tmp_path / "outside-dir").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="outside repo root"):
        build_reviewed_input_identity(
            repo_root=tmp_path,
            reviewed_paths=["outside-dir/secret.txt"],
        )


def test_explicit_reviewed_path_is_never_silently_excluded(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    identity = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt"],
        excluded_paths=["reviewed.txt"],
    )
    assert identity["reviewed_paths"] == ["reviewed.txt"]


def _write_bound_critique(repo: Path, packet_path: Path, identity_sha256: str) -> Path:
    artifact = repo / "charness-artifacts/critique/2026-07-20-bound-review.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    packet_sha = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    artifact.write_text(
        "\n".join(
            [
                "# Bound Review",
                "Date: 2026-07-20",
                "",
                "## Reviewed Input Identity",
                "",
                f"- Packet path: {packet_path.relative_to(repo).as_posix()}",
                f"- Packet SHA256: {packet_sha}",
                f"- Identity SHA256: {identity_sha256}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return artifact


def test_reviewed_input_binding_stales_only_for_declared_input(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    identity = _cached_seed_identity()
    packet_path = _write_static_packet(tmp_path, identity)
    artifact = _write_bound_critique(
        tmp_path,
        packet_path,
        identity["identity_sha256"],
    )
    text = artifact.read_text(encoding="utf-8")

    validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))
    (tmp_path / "unrelated.txt").write_text("changed but not reviewed\n", encoding="utf-8")
    validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))

    (tmp_path / "reviewed.txt").write_text("changed reviewed input\n", encoding="utf-8")
    with pytest.raises(CritiqueValidationError, match="declared reviewed inputs are stale"):
        validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))
    validate_reviewed_input_binding(
        artifact,
        text,
        date(2026, 7, 20),
        check_current=False,
    )


def test_reviewed_input_binding_rejects_packet_byte_tamper(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    identity = _cached_seed_identity()
    packet_path = _write_static_packet(tmp_path, identity)
    artifact = _write_bound_critique(tmp_path, packet_path, identity["identity_sha256"])
    packet_path.write_text(packet_path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(CritiqueValidationError, match="packet bytes are stale or tampered"):
        validate_reviewed_input_binding(
            artifact,
            artifact.read_text(encoding="utf-8"),
            date(2026, 7, 20),
        )


def test_packet_consumed_requires_reviewed_input_binding_after_rule_date(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/critique/2026-07-20-missing-binding.md"
    artifact.parent.mkdir(parents=True)
    text = "# Review\nDate: 2026-07-20\n\nPacket Consumed: packet.md\n"
    artifact.write_text(text, encoding="utf-8")

    with pytest.raises(CritiqueValidationError, match="packet-bound critique"):
        validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))


def test_runner_cli_dogfood_smoke(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
packet_sections:
  - id: smoke
    title: Smoke
    content_kind: static
    content: smoke-body
""")
    runner = REPO_ROOT / "skills/public/critique/scripts/prepare_packet.py"
    result = subprocess.run(
        ["python3", str(runner), "--repo-root", str(tmp_path),
         "--prepared-for", "smoke", "--slug", "smoke"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["section_count"] == 1
    assert payload["changed_ref"] is None
    assert payload["adapter_path"] == ".agents/critique-adapter.yaml"
    binding = payload["reviewed_input_binding"]
    assert binding["packet_path"].endswith("smoke-packet.json")
    assert len(binding["packet_sha256"]) == 64
    assert len(binding["identity_sha256"]) == 64
    artifact = tmp_path / "charness-artifacts/critique/smoke-packet.json"
    assert artifact.is_file()


def _commit_with_deletion(repo: Path) -> str:
    """A committed range that removes a file, which is what #759 could not declare."""
    _init_identity_repo(repo)
    (repo / "kept.txt").write_text("edited\n", encoding="utf-8")
    (repo / "unrelated.txt").unlink()
    _run_git(repo, "add", "-A")
    _run_git(repo, "commit", "-m", "remove unrelated, edit kept")
    return "HEAD^..HEAD"


def test_a_committed_range_with_a_deletion_binds_the_preimage_instead_of_refusing(
    tmp_path: Path,
) -> None:
    """#759: both declarations of a removal slice refused, and they refused each other.

    `git diff --name-only` lists deletions, so the natural manifest hit
    `null-content-hash`; `--diff-filter=d` dropped them, so the manifest no longer
    matched the range and hit `changed-ref-path-mismatch`. A removal slice — the
    change class where a fresh-eye review is worth most — had no valid input.
    """
    changed_ref = _commit_with_deletion(tmp_path)
    preimage = subprocess.run(
        ["git", "show", "HEAD^:unrelated.txt"], cwd=tmp_path, capture_output=True, check=True
    ).stdout

    identity = build_reviewed_input_identity(repo_root=tmp_path, changed_ref=changed_ref)

    assert identity["status"] == "captured"
    assert identity["reviewed_paths"] == ["kept.txt", "unrelated.txt"]
    entries = {entry["path"]: entry for entry in identity["reviewed_content"]}
    # The marker stays deletion-only so existing surviving-file identities keep
    # their prior digest shape.
    assert "disposition" not in entries["kept.txt"]
    assert entries["unrelated.txt"]["disposition"] == "deleted"
    # The bound hash is the PRE-image, so the identity answers "what was removed".
    assert entries["unrelated.txt"]["content_sha256"] == hashlib.sha256(preimage).hexdigest()
    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (True, "current")

def test_a_single_commit_that_deletes_resolves_its_preimage_from_the_parent(
    tmp_path: Path,
) -> None:
    """The `--commit <sha>` form refused identically, and its pre-image is `sha^`."""
    _commit_with_deletion(tmp_path)

    identity = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD")

    entries = {entry["path"]: entry for entry in identity["reviewed_content"]}
    assert entries["unrelated.txt"]["disposition"] == "deleted"
    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (True, "current")


def test_a_refreshed_current_pointer_is_bound_by_its_link_payload(tmp_path: Path) -> None:
    """Filing a record and refreshing its `latest.md` pointer must stay reviewable.

    The documented flow after writing any dated record is
    `refresh_current_pointer.py --execute`, which repoints a `latest.md` SYMLINK.
    That left a modified symlink in the change set, and the sweep fed it to
    `_checked_path`, which refuses symlinks by design — so every session that
    filed a record was unreviewable until it committed.

    The pointer is BOUND rather than excluded. An earlier cut dropped it from the
    sweep, and a fresh-eye review blocked on that: `auto_excluded_paths` sits in
    `PROVENANCE_FIELDS` and is never digested, so retargeting the pointer left the
    identity unchanged and an approved verdict silently followed the move.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "2026-08-30-record.md").write_text("# Record\n", encoding="utf-8")
    (records / "2026-08-29-older.md").write_text("# Older\n", encoding="utf-8")
    (records / "latest.md").symlink_to("2026-08-30-record.md")

    identity = build_reviewed_input_identity(repo_root=tmp_path)

    assert identity["status"] == "captured"
    pointer = "charness-artifacts/quality/latest.md"
    assert pointer in identity["reviewed_paths"]
    assert pointer not in identity["auto_excluded_paths"]
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")


def test_retargeting_the_current_pointer_stales_the_verdict(tmp_path: Path) -> None:
    """The discriminator the fresh-eye review demanded.

    Binding the link payload is only worth more than excluding it if a retarget
    actually moves the digest. It is the selection that carries meaning here, so
    pointing at a different record must not read as an unchanged input.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "a.md").write_text("# A\n", encoding="utf-8")
    (records / "b.md").write_text("# B\n", encoding="utf-8")
    (records / "latest.md").symlink_to("a.md")
    identity = build_reviewed_input_identity(repo_root=tmp_path)
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")

    (records / "latest.md").unlink()
    (records / "latest.md").symlink_to("b.md")

    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (False, "declared reviewed inputs are stale")


def test_an_ordinary_symlink_in_the_sweep_is_not_silently_dropped(tmp_path: Path) -> None:
    """The exception is current-pointer-only; anything else stays loud.

    An earlier cut dropped EVERY symlink from the sweep, which is a hole, not a
    fix. `CLAUDE.md` in this repo is a tracked compatibility symlink whose
    retarget needs the operator's explicit approval, and `auto_excluded_paths`
    sits in `PROVENANCE_FIELDS` and is never digested — so a silently excluded
    symlink could not have staled any verdict either.
    """
    _init_identity_repo(tmp_path)
    (tmp_path / "COMPAT.md").symlink_to("reviewed.txt")

    with pytest.raises(ValueError, match="is a symlink; declare the target file explicitly"):
        build_reviewed_input_identity(repo_root=tmp_path)


def test_retargeting_an_ordinary_symlink_cannot_pass_as_an_unchanged_input(
    tmp_path: Path,
) -> None:
    """The staleness negative control: a retarget must not read as `current`."""
    _init_identity_repo(tmp_path)
    (tmp_path / "other.txt").write_text("other\n", encoding="utf-8")
    (tmp_path / "COMPAT.md").symlink_to("reviewed.txt")
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "add compat symlink")

    identity = build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=["reviewed.txt"]
    )
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")

    # Retarget the compatibility symlink: a substantive change the sweep must not
    # swallow. It is not a current pointer, so the sweep refuses outright rather
    # than quietly continuing without it.
    (tmp_path / "COMPAT.md").unlink()
    (tmp_path / "COMPAT.md").symlink_to("other.txt")
    with pytest.raises(ValueError, match="is a symlink; declare the target file explicitly"):
        build_reviewed_input_identity(repo_root=tmp_path)


def test_the_current_pointer_filename_matches_its_owning_module(tmp_path: Path) -> None:
    """The restated constant must not drift from `artifact_naming_lib`."""
    from scripts.artifact_naming_lib import CURRENT_POINTER_FILENAME as OWNED
    from scripts.reviewed_input_identity import CURRENT_POINTER_FILENAME as RESTATED

    assert RESTATED == OWNED


def test_the_sweep_exclusion_does_not_weaken_the_declared_symlink_refusal(
    tmp_path: Path,
) -> None:
    """The discriminator: sweeping is not declaring.

    `f7a09d672` added the symlink refusal as an approval-boundary repair. Relaxing
    the sweep must not relax that, or this change would have quietly undone it.
    """
    _init_identity_repo(tmp_path)
    (tmp_path / "link.txt").symlink_to("reviewed.txt")

    with pytest.raises(ValueError, match="is a symlink; declare the target file explicitly"):
        build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["link.txt"])


def test_a_symmetric_range_resolves_its_start_to_the_merge_base(tmp_path: Path) -> None:
    """`a...b` crashed with a raw traceback instead of refusing or working.

    `_auto_paths` handed the string to git untouched, so it enumerated correctly,
    while `_patch_components` did `split("..", 1)` and turned `main...feature`
    into `("main", ".feature")`. Two functions in ONE module disagreeing about
    their own input — the same shape as the cross-module disagreements this class
    keeps producing.
    """
    _init_identity_repo(tmp_path)
    _run_git(tmp_path, "checkout", "-q", "-b", "feature")
    (tmp_path / "on-feature.txt").write_text("f\n", encoding="utf-8")
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "feature work")
    _run_git(tmp_path, "checkout", "-q", "-")

    two_dot = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD..feature")
    three_dot = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD...feature")

    assert two_dot["reviewed_paths"] == ["on-feature.txt"]
    assert three_dot["reviewed_paths"] == ["on-feature.txt"]
    # git diffs `a...b` from the MERGE BASE, so the recorded start endpoint must
    # be that base rather than the literal left side.
    base = subprocess.run(
        ["git", "merge-base", "HEAD", "feature"], cwd=tmp_path, capture_output=True, text=True
    ).stdout.strip()
    assert three_dot["resolved_changed_ref"][0] == base


def test_a_merge_commit_binds_the_paths_its_packet_section_lists(tmp_path: Path) -> None:
    """`diff-tree` without `-m` reports NOTHING for a merge.

    The identity bound zero paths while the changed-files section — which already
    passed `-m` — listed the real ones. A reviewer read a file list and the
    verdict covered none of it.
    """
    _init_identity_repo(tmp_path)
    _run_git(tmp_path, "checkout", "-q", "-b", "side")
    (tmp_path / "side.txt").write_text("s\n", encoding="utf-8")
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "side")
    _run_git(tmp_path, "checkout", "-q", "-")
    (tmp_path / "trunk.txt").write_text("m\n", encoding="utf-8")
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "trunk")
    _run_git(tmp_path, "merge", "--no-ff", "-m", "merge side", "side")

    identity = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD")

    assert identity["reviewed_paths"] == ["side.txt", "trunk.txt"]


def test_a_staged_then_deleted_path_binds_its_index_blob(tmp_path: Path) -> None:
    """Staged, then removed from disk: absent from the worktree AND from HEAD.

    It was rendered and surface-matched while binding nothing. The staged blob is
    the reviewed input in that state.
    """
    _init_identity_repo(tmp_path)
    (tmp_path / "staged.txt").write_text("hello\n", encoding="utf-8")
    _run_git(tmp_path, "add", "staged.txt")
    (tmp_path / "staged.txt").unlink()

    identity = build_reviewed_input_identity(repo_root=tmp_path)

    assert "staged.txt" in identity["reviewed_paths"]
    blob = subprocess.run(
        ["git", "show", ":staged.txt"], cwd=tmp_path, capture_output=True
    ).stdout
    entry = next(e for e in identity["reviewed_content"] if e["path"] == "staged.txt")
    assert entry["content_sha256"] == hashlib.sha256(blob).hexdigest()


def test_a_zero_path_binding_is_refused_even_when_currency_is_disabled(
    tmp_path: Path,
) -> None:
    """`--all` disables the currency check for a real reason, but took this with it.

    A corpus sweep re-reads historical bindings that are stale BY DESIGN, so
    turning currency off there is correct. "Covers zero paths" is not a currency
    question — an empty path set digests to the same constant in every repo
    forever — so the registered `critique-artifacts` surface command could never
    catch a vacuous binding, while the same artifact checked with `--paths`
    failed. One correctly-disabled check was silently disabling a second,
    independent one.
    """
    packet_dir = tmp_path / "charness-artifacts" / "critique"
    packet_dir.mkdir(parents=True)
    identity = _empty_identity()
    packet = {
        "kind": "charness.critique_prepare_packet",
        "substrate_mode": "working-tree",
        "changed_ref": None,
        "reviewed_input_identity": identity,
    }
    packet_path = packet_dir / "zero.json"
    packet_bytes = json.dumps(packet).encode("utf-8")
    packet_path.write_bytes(packet_bytes)

    from scripts.reviewed_input_verification import verify_packet_binding

    for check_current in (True, False):
        ok, reason = verify_packet_binding(
            repo_root=tmp_path,
            packet_path="charness-artifacts/critique/zero.json",
            packet_sha256=hashlib.sha256(packet_bytes).hexdigest(),
            identity_sha256=identity["identity_sha256"],
            expected_kind="charness.critique_prepare_packet",
            check_current=check_current,
        )
        assert (ok, reason) == (False, "declared reviewed inputs cover zero paths"), check_current


def test_a_populated_binding_still_passes_integrity_only_mode(tmp_path: Path) -> None:
    """The discriminator: the tightened rule must not refuse an ordinary sweep.

    940 checked-in critique artifacts pass `--all`; a rule that refused them
    would be a corpus-wide false alarm rather than a repair.
    """
    _init_identity_repo(tmp_path)
    packet_dir = tmp_path / "charness-artifacts" / "critique"
    packet_dir.mkdir(parents=True)
    identity = _cached_seed_identity()
    packet = {
        "kind": "charness.critique_prepare_packet",
        "substrate_mode": "working-tree",
        "changed_ref": None,
        "reviewed_input_identity": identity,
    }
    packet_bytes = json.dumps(packet).encode("utf-8")
    (packet_dir / "ok.json").write_bytes(packet_bytes)

    from scripts.reviewed_input_verification import verify_packet_binding

    ok, reason = verify_packet_binding(
        repo_root=tmp_path,
        packet_path="charness-artifacts/critique/ok.json",
        packet_sha256=hashlib.sha256(packet_bytes).hexdigest(),
        identity_sha256=identity["identity_sha256"],
        expected_kind="charness.critique_prepare_packet",
        check_current=False,
    )
    assert (ok, reason) == (True, "packet-integrity-only")


def test_a_path_deleted_against_a_non_first_parent_still_binds(tmp_path: Path) -> None:
    """`-m` enumerates ALL parents; the pre-image must be resolved the same way.

    Widening enumeration to `-m` without widening the pre-image left a path
    deleted relative to the SECOND parent — absent from the merge result and from
    the first parent both — refusing with `null-content-hash`. Enumerating across
    every parent while resolving against one is two halves of one question
    disagreeing, which is the shape these repairs exist to close. A fresh-eye
    review reproduced it on this repo's own history at `225d4b152`.
    """
    _init_identity_repo(tmp_path)
    _run_git(tmp_path, "checkout", "-q", "-b", "side")
    (tmp_path / "only-on-side.txt").write_text("side\n", encoding="utf-8")
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "add a file only this branch has")
    _run_git(tmp_path, "checkout", "-q", "-")
    (tmp_path / "trunk.txt").write_text("t\n", encoding="utf-8")
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "trunk")
    # Merge, then drop the side-only file in the merge result: it is DELETED
    # relative to the second parent and never existed on the first.
    _run_git(tmp_path, "merge", "--no-commit", "--no-ff", "side")
    (tmp_path / "only-on-side.txt").unlink()
    _run_git(tmp_path, "add", "-A")
    _run_git(tmp_path, "commit", "-m", "merge side, dropping its file")

    identity = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD")

    entries = {entry["path"]: entry for entry in identity["reviewed_content"]}
    assert "only-on-side.txt" in entries, identity["reviewed_paths"]
    assert entries["only-on-side.txt"]["disposition"] == "deleted"
    side_blob = subprocess.run(
        ["git", "show", "side:only-on-side.txt"], cwd=tmp_path, capture_output=True
    ).stdout
    assert entries["only-on-side.txt"]["content_sha256"] == hashlib.sha256(side_blob).hexdigest()
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")


def _submodule_repo(tmp_path: Path) -> Path:
    from tests.quality_gates.repo_shapes import install_submodule_repo

    repo, _upstream = install_submodule_repo(tmp_path / "repo")
    return repo


def test_a_working_tree_submodule_binds_its_commit_not_the_index_stage(tmp_path: Path) -> None:
    """`ls-files -s` prints `<mode> <object> <stage>`; `ls-tree` prints `<mode> <type> <object>`.

    Reading field 2 from both bound the STAGE NUMBER — the constant `0` — for
    every working-tree submodule, so no submodule change could stale an identity.
    The earlier test asserted only `captured` and never that the digest tracked
    the commit, which is why it passed over a constant.
    """
    repo = _submodule_repo(tmp_path)
    recorded = subprocess.run(
        ["git", "-C", "sub", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()

    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=[".gitmodules", "sub"])

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + recorded.encode()).hexdigest()
    assert entry["content_sha256"] != hashlib.sha256(b"gitlink\0" + b"0").hexdigest()


def test_a_removed_submodule_binds_its_preimage_commit(tmp_path: Path) -> None:
    """`git show <ref>:<path>` cannot read a gitlink, so a REMOVED submodule fell
    through both the deletion fallback and the gitlink binder and refused."""
    repo = _submodule_repo(tmp_path)
    before = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", "sub"], cwd=repo, capture_output=True, text=True
    ).stdout.split()[2]
    _run_git(repo, "rm", "-q", "-f", "sub")
    _run_git(repo, "commit", "-m", "drop the submodule")

    identity = build_reviewed_input_identity(repo_root=repo, changed_ref="HEAD")

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["disposition"] == "deleted"
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + before.encode()).hexdigest()


def test_editing_the_record_a_pointer_selects_stales_the_verdict(tmp_path: Path) -> None:
    """Binding only `readlink` caught a retarget but not a rewrite in place.

    A pointer whose selected record is edited selects different bytes for every
    consumer while reading as unchanged, so the target's content is bound too.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "a.md").write_text("# A\n", encoding="utf-8")
    (records / "b.md").write_text("# B\n", encoding="utf-8")
    (records / "latest.md").symlink_to("a.md")
    identity = build_reviewed_input_identity(repo_root=tmp_path)
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")

    (records / "a.md").write_text("# A, rewritten\n", encoding="utf-8")

    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (False, "declared reviewed inputs are stale")


def test_a_current_pointer_escaping_the_repo_root_is_refused(tmp_path: Path) -> None:
    """Skipping `_checked_path` for pointers also skipped its boundary check."""
    _init_identity_repo(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (outside / "secret.md").write_text("secret\n", encoding="utf-8")
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "latest.md").symlink_to(outside / "secret.md")

    with pytest.raises(ValueError, match="resolving outside repo root"):
        build_reviewed_input_identity(repo_root=tmp_path)


def test_moving_a_submodule_head_without_staging_stales_the_verdict(tmp_path: Path) -> None:
    """A reviewer reads the working tree, so bind what is CHECKED OUT.

    Binding the index entry meant moving the submodule's HEAD without staging it
    left the identity unchanged, and a changed reviewed input verified as
    current. The working-tree substrate drops staged/unstaged patch hashes from
    its digest, so no other field could compensate.
    """
    repo = _submodule_repo(tmp_path)
    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=[".gitmodules", "sub"])
    assert verify_reviewed_input_identity(repo, identity) == (True, "current")

    upstream = tmp_path / "upstream"
    (upstream / "f.txt").write_text("v2\n", encoding="utf-8")
    _run_git(upstream, "commit", "-am", "v2")
    _run_git(repo / "sub", "fetch", "-q", "origin")
    _run_git(repo / "sub", "checkout", "-q", "FETCH_HEAD")

    ok, reason = verify_reviewed_input_identity(repo, identity)
    assert (ok, reason) == (False, "declared reviewed inputs are stale")


def test_an_uninitialised_submodule_does_not_bind_the_superproject_head(tmp_path: Path) -> None:
    """Git repository discovery walks UPWARD.

    `git -C <uninitialised-submodule> rev-parse HEAD` returns the SUPERPROJECT's
    HEAD, so the previous round's checked-out-HEAD repair bound an unrelated
    commit as if it were the submodule's. An uninitialised submodule has nothing
    checked out to read, which is exactly when the index entry is honest.
    """
    origin = _submodule_repo(tmp_path)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "clone", "-q", str(origin), str(clone)],
        check=True, capture_output=True,
    )
    assert not (clone / "sub" / ".git").exists(), "fixture must leave the submodule uninitialised"
    index_entry = subprocess.run(
        ["git", "ls-files", "-s", "--", "sub"], cwd=clone, capture_output=True, text=True
    ).stdout.split()[1]
    superproject = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=clone, capture_output=True, text=True
    ).stdout.strip()

    identity = build_reviewed_input_identity(
        repo_root=clone, reviewed_paths=[".gitmodules", "sub"]
    )

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + index_entry.encode()).hexdigest()
    assert entry["content_sha256"] != hashlib.sha256(b"gitlink\0" + superproject.encode()).hexdigest()


def test_a_submodule_removed_from_disk_does_not_crash_identity_construction(
    tmp_path: Path,
) -> None:
    """`subprocess.run(cwd=...)` raises when the directory is gone.

    A function named `_optional` must not do that to its caller. A submodule
    deleted from disk while its gitlink stayed in the index raised
    `FileNotFoundError` out of identity construction instead of falling through
    to the index entry — the very pre-image the removed-submodule support exists
    to bind.
    """
    origin = _submodule_repo(tmp_path)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "clone", "-q", str(origin), str(clone)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "-q"],
        cwd=clone, check=True, capture_output=True,
    )
    index_entry = subprocess.run(
        ["git", "ls-files", "-s", "--", "sub"], cwd=clone, capture_output=True, text=True
    ).stdout.split()[1]
    shutil.rmtree(clone / "sub")

    identity = build_reviewed_input_identity(repo_root=clone, reviewed_paths=["sub"])

    entry = next(e for e in identity["reviewed_content"] if e["path"] == "sub")
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0" + index_entry.encode()).hexdigest()
    assert verify_reviewed_input_identity(clone, identity) == (True, "current")


def test_a_non_absence_oserror_is_not_treated_as_a_missing_checkout(
    tmp_path: Path, monkeypatch
) -> None:
    """The axis-varying control the absent-directory test did not supply.

    A blanket `except OSError` let a `PermissionError` over a PRESENT submodule —
    one whose checked-out HEAD differs from the index — read as "no checkout to
    consult", bind the stale index value, and report `current`, with verification
    repeating the same fallback and agreeing. A failure silently converted into a
    passing verdict is the class this module exists to close.
    """
    from scripts import reviewed_input_nonblob as nonblob

    repo = _submodule_repo(tmp_path)
    real_run = subprocess.run

    def deny_inside_submodule(*args, **kwargs):
        cwd = str(kwargs.get("cwd", ""))
        if cwd.endswith("sub"):
            raise PermissionError(13, "permission denied")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(nonblob.subprocess, "run", deny_inside_submodule)

    with pytest.raises(PermissionError):
        nonblob._gitlink_commit(repo, "sub", None)
