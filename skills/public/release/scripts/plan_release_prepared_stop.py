"""What the planner can observe about a prepared claims-review stop.

One concept, split out of `plan_release_run.py` (which reached its length cap): every
question the planner asks about a release that is mid-flight at a marked prepared record —
where its release record lives, what that record says at HEAD, whether the claims evidence
is already committed, which critique artifact the publish gate would actually accept, and
which drafted notes the resume command should name.

These are all TOLERANT where the publish helper is STRICT, and the asymmetry is deliberate
rather than an oversight. The publish helper refuses an unresolvable record path, because
publishing against one is how the claims floor goes blind. The planner is read-only: its
worst honest outcome is "no prepared stop detected", and a crash in a planner is strictly
less useful than that. `plan_release_run_packets.py` turns these observations into the
resume packets; this module only observes.
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    from scripts.core.subprocess_guard import run_process

RELEASE_RECORD_FILENAME = "latest.md"


def git(repo_root: Path, args: list[str]) -> tuple[int, str]:
    result = run_process(["git", "-C", str(repo_root), *args], cwd=repo_root, timeout_seconds=None)
    return result.returncode, result.stdout


def release_record_path(adapter_data: dict[str, Any]) -> str | None:
    """The release record path this repo's adapter declares, or None when it declares none.

    A second copy of this path as a CONSTANT is what made the planner blind in exactly the
    repos the publish helper's own copy made the claims floor blind: it read no marker,
    skipped the prepared-stop branch, and reported `inspect_only` — "nothing to do here" —
    at a live prepared stop.
    """
    output_dir = adapter_data.get("output_dir")
    if not isinstance(output_dir, str) or not output_dir.strip():
        return None
    return str(PurePosixPath(output_dir.strip()) / RELEASE_RECORD_FILENAME)


def drafted_notes_candidates(
    repo_root: Path, adapter_data: dict[str, Any], tag_name: str | None, *, find_drafted_notes
) -> list[str]:
    """Drafted notes for the pending tag, so the emitted resume command can name one.

    Load-bearing rather than convenient now that the resume lane RUNS the notes-file
    preflight: a resume command emitted without `--notes-file`, in a repo that has drafted
    notes for this tag, is a command the operator will be refused for running verbatim.
    """
    output_dir = adapter_data.get("output_dir")
    if not tag_name or not isinstance(output_dir, str):
        return []
    try:
        found = find_drafted_notes(repo_root, output_dir, target_tag=tag_name)
    except Exception:
        return []
    return [path.relative_to(repo_root).as_posix() for path in found]


def head_release_record(repo_root: Path, record_path: str | None) -> str | None:
    """The release record AS COMMITTED at HEAD, which is what the publish helper reads."""
    if not record_path:
        return None
    code, out = git(repo_root, ["show", f"HEAD:{record_path}"])
    return out if code == 0 else None


def committed_claims_record(repo_root: Path, *, claims_record_in_change_set) -> str | None:
    """The claims record already committed as HEAD's own change, when there is one.

    Delegates the shape rule to the claims-review module rather than restating it, so the
    planner cannot come to disagree with the publish helper about what R looks like."""
    code, out = git(repo_root, ["show", "--no-commit-id", "--name-only", "-r", "--format=", "HEAD"])
    if code != 0:
        return None
    return claims_record_in_change_set([line for line in out.splitlines() if line])


def critique_acceptor(repo_root: Path, tokens: list[str], *, closeout_evidence):
    """Return a predicate that answers the publish gate's OWN question about a candidate.

    Binding alone is not what the gate asks: it also requires the artifact to be TRACKED
    and to clear a stub-residual floor. A binding-only filter named candidates the gate
    then refused, which is the refusal this planner exists to save the operator from.
    """

    def accepts(rel_path: str) -> bool:
        if git(repo_root, ["ls-files", "--error-unmatch", rel_path])[0] != 0:
            return False
        report = closeout_evidence.check(
            repo_root=repo_root,
            required=["standalone_critique"],
            evidence={"standalone_critique": rel_path},
            skips={},
            kind="release",
            tokens=tokens,
        )
        return bool(report["ok"])

    return accepts
