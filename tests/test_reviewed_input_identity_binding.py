"""Reviewed-input identity semantics and the critique artifact binding.

Split from `test_critique_prepare_packet.py`, which owns adapter loading, section
execution, and packet rendering. These tests own the other half: what enters the
identity digest, when a binding goes stale, and when a declared binding is
rejected outright.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest
import yaml

from scripts.critique_adapter_lib import load_adapter
from scripts.critique_packet_lib import (
    build_packet,
    build_reviewed_input_identity,
    write_packet,
)
from scripts.reviewed_input_verification import verify_reviewed_input_identity
from scripts.validate_critique_artifacts import (
    ValidationError as CritiqueValidationError,
)
from scripts.validate_critique_artifacts import (
    validate_reviewed_input_binding,
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
    _run_git(repo, "init")
    (repo / "reviewed.txt").write_text("base\n", encoding="utf-8")
    (repo / "unrelated.txt").write_text("base\n", encoding="utf-8")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "initial")


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
    _init_identity_repo(tmp_path)
    current = build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=["reviewed.txt"]
    )
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
    _init_identity_repo(tmp_path)
    empty = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=[])
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
    adapter = load_adapter(tmp_path)
    packet = build_packet(
        adapter=adapter,
        repo_root=tmp_path,
        prepared_for="working tree",
        reviewed_paths=["reviewed.txt"],
    )
    packet_path, _ = write_packet(packet, output_dir=tmp_path / "charness-artifacts/critique", slug="bound")
    artifact = _write_bound_critique(
        tmp_path,
        packet_path,
        packet["reviewed_input_identity"]["identity_sha256"],
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
    adapter = load_adapter(tmp_path)
    packet = build_packet(
        adapter=adapter,
        repo_root=tmp_path,
        prepared_for="working tree",
        reviewed_paths=["reviewed.txt"],
    )
    packet_path, _ = write_packet(packet, output_dir=tmp_path / "charness-artifacts/critique", slug="bound")
    artifact = _write_bound_critique(tmp_path, packet_path, packet["reviewed_input_identity"]["identity_sha256"])
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
    assert entries["unrelated.txt"]["disposition"] == "deleted"
    # The bound hash is the PRE-image, so the identity answers "what was removed".
    assert entries["unrelated.txt"]["content_sha256"] == hashlib.sha256(preimage).hexdigest()
    ok, reason = verify_reviewed_input_identity(tmp_path, identity)
    assert (ok, reason) == (True, "current")


def test_a_surviving_path_carries_no_disposition_so_older_identities_do_not_move(
    tmp_path: Path,
) -> None:
    """The marker is deletion-only on purpose.

    Stamping every entry with a disposition would change the digest of every
    identity ever captured, and each one would then read as `stale` — a corpus-wide
    false alarm. A deleted entry could not exist before this repair, so nothing
    already recorded moves.
    """
    changed_ref = _commit_with_deletion(tmp_path)

    identity = build_reviewed_input_identity(repo_root=tmp_path, changed_ref=changed_ref)

    entries = {entry["path"]: entry for entry in identity["reviewed_content"]}
    assert "disposition" not in entries["kept.txt"]


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
    _init_identity_repo(tmp_path)
    packet_dir = tmp_path / "charness-artifacts" / "critique"
    packet_dir.mkdir(parents=True)
    identity = build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=[], substrate_mode="working-tree"
    )
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
    identity = build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=["reviewed.txt"], substrate_mode="working-tree"
    )
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
