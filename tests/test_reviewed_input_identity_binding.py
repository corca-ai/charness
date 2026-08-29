"""Reviewed-input identity semantics and the critique artifact binding.

Split from `test_critique_prepare_packet.py`, which owns adapter loading, section
execution, and packet rendering. These tests own the other half: what enters the
identity digest, when a binding goes stale, and when a declared binding is
rejected outright.
"""
from __future__ import annotations

import hashlib
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
from scripts.reviewed_input_identity import verify_reviewed_input_identity
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


def test_a_refreshed_current_pointer_does_not_make_the_sweep_refuse(tmp_path: Path) -> None:
    """Filing a record and refreshing its `latest.md` pointer must stay reviewable.

    The documented flow after writing any dated record is
    `refresh_current_pointer.py --execute`, which repoints a `latest.md` SYMLINK.
    That left a modified symlink in the working-tree change set, and the auto
    sweep fed it to `_checked_path`, which refuses symlinks by design. So
    `build_packet` raised outright and every session that filed a record was
    unreviewable until it committed -- precisely the window in which a reviewer
    would be asked to read that record.
    """
    _init_identity_repo(tmp_path)
    records = tmp_path / "charness-artifacts" / "quality"
    records.mkdir(parents=True)
    (records / "2026-08-30-record.md").write_text("# Record\n", encoding="utf-8")
    (records / "latest.md").symlink_to("2026-08-30-record.md")

    identity = build_reviewed_input_identity(repo_root=tmp_path)

    assert identity["status"] == "captured"
    # Dropped from the sweep, but REPORTED -- an excluded input that no field
    # mentions is the same silent-scope failure this repo spends itself on.
    assert "charness-artifacts/quality/latest.md" in identity["auto_excluded_paths"]
    assert "charness-artifacts/quality/latest.md" not in identity["reviewed_paths"]
    assert "charness-artifacts/quality/2026-08-30-record.md" in identity["reviewed_paths"]


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
