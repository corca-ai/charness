"""The public-release narrative audit gate at the publish boundary.

One concept: everything that reads a release NARRATIVE — the durable audit
artifact and the release notes — and refuses publish when what it says is not
supported. Split out of `publish_release_cli.py` (which had reached its length
cap) because these three entrypoints share one question, distinct from the CLI's
job of wiring a run together:

- `run_narrative_audit` — the durable artifact's headings and its five-entry
  release state ledger;
- `run_notes_file_preflight` — mutable source-tree pointers in a notes FILE,
  plus the derived claim block's agreement with the tree, before publish;
- `audit_notes_text` — the same pointer rule over notes TEXT, so the PUBLISHED
  body can be audited after `--generate-notes`, which composes the notes at
  creation time and leaves no file to inspect beforehand.

The pre-publish pair raise `SystemExit`; the post-publish reader does not, and
must not — the release already exists by then, so its finding is an advisory.
"""
from __future__ import annotations

import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_audit_narrative = SKILL_RUNTIME.load_local_skill_module(__file__, "audit_public_release_narrative")
_notes_claims = SKILL_RUNTIME.load_local_skill_module(__file__, "release_notes_claims")
_narrative_lint = SKILL_RUNTIME.load_local_skill_module(__file__, "lint_release_narrative")
_repo_file_listing = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.repo_file_listing")
#: `RepoFileListingError` subclasses `SystemExit`, so it derives from
#: `BaseException` and an `except Exception` handler NEVER catches it. The
#: first version of the guard below was dead code for the one cause it named,
#: and the comment claiming the type was not importable was false -- it is
#: imported right here.
RepoFileListingError = _repo_file_listing.RepoFileListingError

build_narrative_audit_payload = _audit_narrative.build_payload
audit_notes_text = _audit_narrative.audit_notes_text
audit_notes_file = _audit_narrative.audit_notes_file
find_drafted_notes = _audit_narrative.find_drafted_notes
load_adapter = _audit_narrative.load_adapter


def _drafted_notes_for(repo_root: Path, *, target_tag: str) -> list[Path]:
    """Drafted notes for ``target_tag``, or none when the adapter cannot be read.

    An invalid adapter is `build_payload`'s blocker to raise with its own
    message; this preflight must not pre-empt it with a listing failure."""
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        return []
    return find_drafted_notes(repo_root, adapter["data"]["output_dir"], target_tag=target_tag)


def derived_claims_required(repo_root: Path) -> bool:
    """Whether this repo requires release claims to be derived rather than typed.

    Defaults to TRUE, including when the adapter is absent or invalid. An
    unreadable adapter is not a declared opt-out, and reading it as one would put
    the strength of a publish gate behind whether a YAML file happened to parse.
    """
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        return True
    return bool(adapter["data"].get("require_derived_release_claims", True))


def _known_versions(repo_root: Path, target_tag: str, previous_version: str | None = None) -> tuple[str, ...]:
    """Versions this note may name without grounding them.

    The tag being cut, plus the version currently in the packaging manifest —
    which is the version a rollback paragraph names. Reading it here rather than
    leaving it to the author is the difference between a rule that permits
    "to return to 5.2.0" and one that refuses every rollback path it is given.

    ``previous_version`` exists because the manifest read is LANE-DEPENDENT and
    that made the same note legal at prepare and illegal at publish. The execute
    lane preflights the notes BEFORE the bump, so the manifest still reads the
    outgoing version and a rollback paragraph naming it is grounded. The resume
    lane runs after the bump, so the manifest reads the version being cut, the
    outgoing version becomes ungrounded, and the note is refused at the one
    boundary where the remedy — edit the file — lands a commit on top of the
    claims record and locks the resume out entirely. Passing the previous version
    explicitly makes both lanes ground the same set.
    """
    versions = [target_tag]
    adapter = load_adapter(repo_root)
    if adapter["valid"]:
        manifest = repo_root / adapter["data"]["packaging_manifest_path"]
        try:
            current = json.loads(manifest.read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError, AttributeError):
            current = None
        if isinstance(current, str) and current:
            versions.append(current)
    if isinstance(previous_version, str) and previous_version:
        versions.append(previous_version)
    return tuple(dict.fromkeys(versions))


def notes_narrative_blockers(
    repo_root: Path, notes_file: Path, *, target_tag: str, previous_version: str | None = None
) -> list[str]:
    """Ungrounded quantities in the notes' AUTHORED prose.

    A separate arm from the derived block on purpose, because they fail
    separately: the block catches a claim that was derived and went stale, and
    this catches a claim that was never derived at all. The recorded false
    sentence — "twelve public skill scripts still declare one" — is invisible to
    the block arm, since no marker and no derived surface was ever attached to
    it. Containment is what makes the block arm's coverage mean something.

    Only the lint's BLOCKING findings refuse a publish. Its advisory arm — the
    completeness words — is deliberately not a publish blocker: measured against
    this repo's own release note it fires on honest-limits language, and a rule
    that refuses the sentence making a note honest is one an operator disables,
    taking the arm that works with it.
    """
    if not derived_claims_required(repo_root):
        return []
    findings = _narrative_lint.lint_file(
        notes_file, versions=_known_versions(repo_root, target_tag, previous_version)
    )
    return _narrative_lint.finding_lines(_narrative_lint.blocking(findings))


def notes_claim_blockers(
    repo_root: Path, notes_file: Path, *, tracked_tree=None
) -> list[str]:
    """Where the notes' derived claims disagree with the tree being published.

    This runs HERE, in the pre-bump preflight, and not also in
    `run_narrative_audit`. The drafted-notes refusal is duplicated across both
    sites because the two arms answer the same question from different inputs
    and could otherwise drift; this arm reads one file and re-derives from the
    tree, so a second copy would add a second identical failure line rather than
    a second observation. It runs on BOTH lanes, and the resume lane is the one
    that matters: it is the only path that reaches `create_release`, and its
    `--notes-file` is a free argument, so a note nothing validated can be handed
    over there.

    Two non-claims. A publish taking `--generate-notes` supplies no notes file
    and is not reached by this arm at all — the composed body never exists on
    disk for it to read. And a clean result means the notes agree with
    `release_claim_surfaces.SURFACES`, not that they are true: a claim surface
    nobody registered is invisible here.
    """
    required = derived_claims_required(repo_root)
    # `require_git` follows the arming, not the other way round. An armed repo
    # must measure the SHIPPED tree, and the listing helper silently falls back
    # to a filesystem glob -- a different population, counting untracked and
    # gitignored files, rendering a verdict indistinguishable from a real one.
    # A repo that opted out is not being gated at all, so demanding git of it
    # would refuse a publish over a check it declined.
    try:
        findings = _notes_claims.audit_notes_file(
            notes_file, repo_root, require_git=required, tracked_tree=tracked_tree
        )
    except RepoFileListingError as exc:
        # A traceback where a verdict belongs is the shape this repo keeps
        # repairing. Refusing is correct -- nothing read the shipped tree, so no
        # claim in these notes was checked -- but it has to be SAID, with cause.
        return [
            f"[unresolvable] tree-listing-failed: the derived claim surfaces could not be measured "
            f"against the shipped tree, so nothing in these notes was checked: {exc}"
        ]
    if not required:
        # The opt-out covers only "these notes carry no derived block at all".
        # A note that DOES make a derived claim is held to it either way: opting
        # out of the requirement is not a licence to publish a claim the tree
        # contradicts.
        findings = [finding for finding in findings if finding["kind"] != "missing-derived-block"]
    return _notes_claims.finding_lines(findings)


def _preflight_unreadable_blocker(exc: Exception) -> str:
    return (
        f"{exc}. Publish is refused rather than proceeding on an unread directory: "
        "this arm cannot tell drafted-and-unshipped notes from a repo that drafts "
        "none when it cannot list them."
    )


def run_narrative_audit(
    repo_root: Path,
    *,
    target_tag: str,
    notes_file: Path | None = None,
) -> None:
    audit_payload = build_narrative_audit_payload(
        repo_root,
        target_tag=target_tag,
        notes_file=notes_file,
    )
    if audit_payload["status"] == "blocked":
        raise SystemExit(
            "public release narrative audit blocked publish:\n"
            + "\n".join(f"- {blocker}" for blocker in audit_payload["blockers"])
        )


#: Named in the refusal itself, not left to a source dive.
#:
#: The first version of this arm printed N blocker lines and never said the
#: remedy commands existed, nor that the requirement is adapter-controlled at
#: all. An operator meeting it at the publish boundary could discover the opt-out
#: only by reading `resolve_adapter.py`.
CLAIMS_REMEDY = (
    "Remedy: re-run the generator rather than editing the block by hand --\n"
    "  python3 <release-skill>/scripts/generate_release_notes.py --repo-root . "
    "--notes-file <notes.md> --sync\n"
    "then re-check with the same script and `--check --version <tag>`. Passing the version matters:\n"
    "without it the check refuses a note for naming its own version, which the publish gate accepts.\n"
    "A quantity in authored prose is grounded by writing it as a\n"
    "`{{claim:<surface>.count=<value>}}` marker, or moved into a code span if it is an identifier.\n"
    "A repo that does not use derived release claims sets `require_derived_release_claims: false`\n"
    "in .agents/release-adapter.yaml; that is a recorded decision, and it disarms BOTH the derived\n"
    "block requirement and prose containment."
)

#: Whether the claim/containment arms produced anything, decided by the arms
#: themselves rather than re-derived from rendered text. The substring form
#: matched any blocker whose interpolated PATH happened to contain `surface-`
#: (this repo has one: an audit artifact named `...-evidence-surface-triage-...`),
#: so a mutable-link refusal drew a remedy telling the operator to re-run the
#: notes generator and offering an opt-out that disarms two unrelated arms.


RESUME_REMEDY = (
    "On a resume, do NOT take this blocker's usual remedy of renaming or deleting the "
    "drafted notes and committing that. On the claims lane it puts a third commit on top of "
    "the claims evidence, after which no single-parent prepared boundary is identifiable and "
    "the next resume refuses with `no single-parent prepared boundary could be identified` -- "
    "whose own recovery text then tells you to reset past the committed claims record. "
    "Re-pass `--notes-file <the candidate named above>` instead: a resume that repeats the "
    "original arguments needs no worktree change at all. If you genuinely want DIFFERENT "
    "notes than the prepare validated, that edit is a worktree change and belongs before the "
    "prepared stop, not here."
)


def run_notes_file_preflight(
    repo_root: Path,
    *,
    target_tag: str,
    notes_file: Path | None,
    on_resume: bool = False,
    previous_version: str | None = None,
    tracked_tree=None,
) -> None:
    # The drafted-notes refusal is a directory listing with no dependency on the
    # bump, the release surface, or the pre-push gates, and `run_narrative_audit`
    # — where it also fires — runs after all three. Refusing here too makes the
    # cost of learning it milliseconds instead of a full gate run plus a rollback
    # cycle. It reads the same helpers, so the two sites cannot disagree.
    # The supplied file is audited FIRST. Running the drafted-notes arm ahead of
    # it turned a mistyped `--notes-file` path into "which is none of them" —
    # true, but it never says the path does not exist, and `audit_notes_file`'s
    # `notes file missing` is the message that names the actual mistake.
    notes_blockers = audit_notes_file(notes_file, target_tag=target_tag) if notes_file is not None else []
    # The claim arm runs only when the pointer arm found the file readable. Its
    # own `notes-unreadable` finding would otherwise restate `notes file missing`
    # in different words, and the operator holding a mistyped `--notes-file` gets
    # one message naming the mistake rather than two naming it twice.
    # The claim and containment arms run on BOTH lanes.
    #
    # A previous revision skipped them on resume, reasoning that the window
    # between the prepared stop and the resume is closed to worktree changes so
    # re-judging could only produce a refusal with no legal remedy. That
    # reasoning was about the TREE and the argument does not transfer to the
    # NOTES: `--notes-file` is a free argument on the resume, nothing binds it to
    # the file the prepare validated (`plan_release_run_packets` lists it under
    # "repeat the original arguments", which is advice, not a constraint), and
    # the resume lane is the ONLY path that reaches `create_release`. Skipping
    # here meant a second drafted note for the same tag -- stale derived block and
    # all -- could be handed over at resume and published with nothing reading its
    # claims. That is the recorded failure restored by its own repair.
    #
    # The deadlock the skip was meant to avoid does not arise: the same file that
    # passes at prepare passes at resume, because `publish_release_cli` refuses a
    # dirty worktree on every lane and the claims commit is constrained to the
    # review evidence, so the tree cannot move underneath it. A refusal here means
    # the operator handed over a DIFFERENT file, and `RESUME_REMEDY`'s advice to
    # re-pass the original one is then exactly right.
    claims_blockers: list[str] = []
    if notes_file is not None and not notes_blockers:
        claims_blockers = [
            *notes_claim_blockers(repo_root, notes_file, tracked_tree=tracked_tree),
            *notes_narrative_blockers(
                repo_root, notes_file, target_tag=target_tag, previous_version=previous_version
            ),
        ]
        notes_blockers += claims_blockers
    drafted_blockers: list[str] = []
    try:
        drafted = _drafted_notes_for(repo_root, target_tag=target_tag)
    except _audit_narrative.NotesDirectoryUnreadable as exc:
        # The two call sites read the same helpers so they cannot disagree; that
        # invariant only holds if BOTH handle the new failure, and the preflight
        # is the one that runs before the bump.
        notes_blockers.append(_preflight_unreadable_blocker(exc))
    else:
        drafted_blockers = _audit_narrative.drafted_notes_blockers(
            repo_root, drafted, target_tag=target_tag, notes_file=notes_file
        )
        notes_blockers += drafted_blockers
    if notes_blockers:
        # `RESUME_REMEDY` is scoped to the DRAFTED-NOTES blocker, not to every blocker this
        # preflight can raise. Appended unconditionally it told an operator with a mistyped
        # `--notes-file` and no drafted notes to "re-pass the candidate above" when no
        # candidate was printed, and told an operator whose notes carry a mutable pointer
        # that no worktree change is needed when editing that file is the only remedy.
        raise SystemExit(
            "public release notes preflight blocked publish:\n"
            + "\n".join(f"- {blocker}" for blocker in notes_blockers)
            + (f"\n\n{CLAIMS_REMEDY}" if claims_blockers else "")
            + (f"\n\n{RESUME_REMEDY}" if on_resume and drafted_blockers else "")
        )
