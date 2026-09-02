#!/usr/bin/env python3
"""Repo gate: a disposition's named destination must resolve.

WHY THIS EXISTS, measured rather than supposed. Four claims-review rounds on one
release (v6.3.0) produced ~14 blockers and not one was in the shipped code. The
dominant class was a disposition that named a destination it had never reached:

- `Structural follow-up: issue #N (recurs: ...)` -- shipped inside a release
  bundle pointing at no issue. It passed every existing gate, because `#N` is
  not in the form floor's placeholder vocabulary (`TODO|TBD|<...>|FIXME`) and
  `issue #N` is a perfectly well-formed disposition.
- `applied: ... publish_release_execute.py renders it` -- naming a mechanism
  that had been deleted, in the disposition for the finding about hardcoded
  claims that had stopped being true.
The disposition form floor states its own scope out loud: "form/enum only
(never a content classifier)", deferring substance to a fresh-eye review. That
is a defensible split and this gate does not touch it. It owns the DECIDABLE
middle the split left unclaimed:

    form      -- a disposition is present and well-shaped   (skill-side floors)
    referent  -- the thing it names is real                 (THIS gate)
    substance -- the thing it names is the right thing      (fresh-eye review)

"Is `#N` an issue number?" and "does this path exist?" need no judgment. Asking
a human reviewer to catch them is what four rounds proved does not work: the
same authoring mistake was caught in 0 seconds by the release-notes linter,
which re-derives its numbers, and took four rounds in the goal/retro artifacts,
which do not.

SCOPE. Repo-internal, like `check_spec_evidence_durability`: wired from this
repo's own `run-quality.sh`, not from a consumer install. Date-anchored so
frozen artifacts are reported and never rewritten -- editing a frozen retro so a
checker goes green is evidence edited to fit a gate, which this repo has had to
correct on more than one floor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifact_quantities import inconsistent_quantities  # noqa: E402
from scripts.artifact_referents import (  # noqa: E402
    DISPOSITION_LINE_RE,
    INLINE_DISPOSITION_RE,
    ResolverUnavailable,
    check_disposition_referents,
    commit_identity_in_ancestry,
    reachable_head_commits,
    sha_candidates,
    unresolvable_shas,
)
from scripts.critique_enforcement_scope import date_from_filename  # noqa: E402
from scripts.core.repo_path_display import display_path as _display_path  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
_quality_adapter = import_repo_module(__file__, "scripts.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.quality_universes_lib")
DEFAULT_ARTIFACT_ROOTS = _quality_universes.DEFAULT_ARTIFACT_ROOTS
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe
_retro_index = import_repo_module(__file__, "scripts.build_retro_lesson_selection_index")
load_retro_paths = _retro_index._load_retro_paths

#: One Git reachability query per SHA per artifact would be thousands of
#: subprocesses across
#: the corpus. Same SHA, same answer, so resolve each once per run.
_SHA_CACHE: dict[str, bool] = {}
_HEAD_COMMITS_CACHE: dict[str, set[str]] = {}


def _cached_commit_reachable(sha: str, repo_root: Path) -> bool:
    key = f"{repo_root}:{sha}"
    if key not in _SHA_CACHE:
        root_key = str(repo_root)
        if root_key not in _HEAD_COMMITS_CACHE:
            _HEAD_COMMITS_CACHE[root_key] = reachable_head_commits(repo_root)
        _SHA_CACHE[key] = commit_identity_in_ancestry(sha, _HEAD_COMMITS_CACHE[root_key])
    return _SHA_CACHE[key]


# Repo-only declaration of intentional local authoring context. This belongs to
# the Charness gate, not the portable resolver: consumer repositories own their
# own history/topology policy and do not inherit this exception surface.
LOCAL_CONTEXT_DECLARATIONS = Path("scripts/artifact-referent-local-context.json")
_DECLARATION_KEYS = {"artifact", "line", "token", "line_sha256", "reason"}


def line_sha256(line: str) -> str:
    """Stable identity of one artifact line, excluding the newline carrier."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def load_local_context_declarations(
    repo_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Load exact, reasoned local-history declarations; malformed input blocks."""
    path = repo_root / LOCAL_CONTEXT_DECLARATIONS
    if not path.exists():
        return [], []
    display = _display_path(path, repo_root)
    worktree_bytes = path.read_bytes()
    try:
        staged = run_process(
            ["git", "-C", str(repo_root), "show", f":{LOCAL_CONTEXT_DECLARATIONS}"],
            cwd=repo_root,
            timeout_seconds=10,
        )
    except OSError as exc:
        staged = None
        binding_error = str(exc)
    else:
        binding_error = (staged.stderr or "").strip()
    if staged is None or staged.returncode != 0 or staged.stdout.encode("utf-8") != worktree_bytes:
        return [], [
            {
                "file": display,
                "line": 1,
                "enforced": True,
                "kind": "unbound-local-context-declaration",
                "token": display,
                "detail": (
                    "the declaration must exactly match the Git index candidate; untracked or "
                    f"unstaged exception bytes are not reviewable ({binding_error or 'byte mismatch'})"
                ),
            }
        ]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [], [
            {
                "file": display,
                "line": 1,
                "enforced": True,
                "kind": "malformed-local-context-declaration",
                "token": display,
                "detail": f"local-context declarations are unreadable: {exc}",
            }
        ]
    if not isinstance(payload, list):
        payload = [payload]
        top_level_error = True
    else:
        top_level_error = False

    valid: list[dict[str, object]] = []
    defects: list[dict[str, object]] = []
    seen: set[tuple[str, int, str]] = set()
    for index, raw in enumerate(payload, 1):
        reason = raw.get("reason") if isinstance(raw, dict) else None
        artifact = raw.get("artifact") if isinstance(raw, dict) else None
        line = raw.get("line") if isinstance(raw, dict) else None
        token = raw.get("token") if isinstance(raw, dict) else None
        fingerprint = raw.get("line_sha256") if isinstance(raw, dict) else None
        keys_ok = isinstance(raw, dict) and set(raw) == _DECLARATION_KEYS
        path_ok = (
            isinstance(artifact, str)
            and artifact != ""
            and not Path(artifact).is_absolute()
            and ".." not in Path(artifact).parts
        )
        token_ok = isinstance(token, str) and sha_candidates(token) == [token]
        if (
            top_level_error
            or not keys_ok
            or not path_ok
            or not isinstance(line, int)
            or isinstance(line, bool)
            or line < 1
            or not token_ok
            or not isinstance(fingerprint, str)
            or len(fingerprint) != 64
            or any(char not in "0123456789abcdef" for char in fingerprint)
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            defects.append(
                {
                    "file": display,
                    "line": index,
                    "enforced": True,
                    "kind": "malformed-local-context-declaration",
                    "token": str(token or index),
                    "detail": (
                        "each declaration must contain exactly artifact, line, token, line_sha256, "
                        "and a nonempty reason; artifact must be repo-relative, line positive, "
                        "token one complete Git SHA candidate, and line_sha256 lowercase SHA-256"
                    ),
                }
            )
            continue
        identity = (artifact, line, token)
        if identity in seen:
            defects.append(
                {
                    "file": display,
                    "line": index,
                    "enforced": True,
                    "kind": "duplicate-local-context-declaration",
                    "token": token,
                    "detail": "duplicate declarations create two owners for one exception",
                }
            )
            continue
        seen.add(identity)
        valid.append(
            {
                "artifact": artifact,
                "line": line,
                "token": token,
                "line_sha256": fingerprint,
                "reason": reason.strip(),
            }
        )
    return valid, defects


#: Artifacts dated from here forward are ENFORCED. Earlier ones are counted and
#: reported. This is the date the gate landed.
ENFORCED_FROM = date(2026, 8, 22)

#: Families whose dispositions ship inside release bundles and are read as
#: statements of fact by later sessions.
SCANNED_FAMILIES = ("goals", "retro")
SCANNED_GLOBS = tuple(f"{DEFAULT_ARTIFACT_ROOTS[family]}/*.md" for family in SCANNED_FAMILIES)


def _artifact_default(repo_root: Path, family: str) -> str:
    if family == "retro":
        try:
            output_dir, _summary_path = load_retro_paths(repo_root)
        except FileNotFoundError:
            pass
        else:
            return output_dir.relative_to(repo_root).as_posix()
    return DEFAULT_ARTIFACT_ROOTS[family]


def _resolved_targets(repo_root: Path) -> tuple[list[Path], list[str]]:
    adapter = load_quality_adapter(repo_root)
    targets: set[Path] = set()
    empty_families: list[str] = []
    for family in SCANNED_FAMILIES:
        universe = resolve_universe(
            adapter,
            f"artifact_roots.{family}",
            default=_artifact_default(repo_root, family),
        )
        files = [
            path for path in matching_files(repo_root, universe) if path.suffix.lower() == ".md"
        ]
        refusal = refuse_if_declared_and_empty(universe, files, "check-artifact-referents")
        if refusal:
            raise ValueError(refusal)
        if not files:
            empty_families.append(family)
        targets.update(files)
    return sorted(targets), empty_families


# The disposition vocabulary is IMPORTED, not redefined. Two near-identical
# copies existed after round 1; the failure mode is not "they drift" but "one
# grows and the other silently degrades" -- adding a keyword here would have
# quietly reverted the library's value-scoping to whole-line behaviour,
# reintroducing the M2 and M3 evasions at once.


def is_enforced(path: Path) -> bool:
    """Enforced unless the filename carries a readable date BEFORE the cutoff.

    Fail-CLOSED on an undatable filename, mirroring the durability gate: an
    undated name must not buy a permanent exemption.
    """
    observed = date_from_filename(path)
    if observed is None:
        return True
    return observed >= ENFORCED_FROM


def disposition_lines(text: str) -> list[tuple[int, str]]:
    """Every disposition-bearing line, 1-indexed, fenced blocks excluded.

    Fenced blocks are skipped because this repo quotes BROKEN dispositions inside
    fences when explaining a defect -- including in this gate's own test fixtures
    and in the retro that motivated it. A gate that fired on its own worked
    example would teach authors to stop quoting evidence.
    """
    out: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if DISPOSITION_LINE_RE.match(line) or INLINE_DISPOSITION_RE.search(line):
            out.append((number, line))
    return out


def audit_file(
    path: Path,
    repo_root: Path,
    scope: dict[str, int],
    declared: dict[tuple[str, int, str, str], str] | None = None,
    matched_declarations: set[tuple[str, int, str, str]] | None = None,
) -> list[dict[str, object]]:
    """Findings for one artifact, accumulating SCOPE counters into `scope`.

    The counters exist because a gate that silently drops part of its own scope
    prints the same clean line as one with nothing to drop -- a lesson this
    session recorded and this gate then violated. `dispositions` and
    `shas_resolved` must be NUMBERS in the report so a regex that stopped
    matching, or a resolver that stopped answering, is visible as a scope
    collapse rather than as a pass.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    display_path = _display_path(path, repo_root)
    declared = declared or {}
    matched_declarations = matched_declarations if matched_declarations is not None else set()
    enforced = is_enforced(path)
    findings: list[dict[str, object]] = []
    for number, line in disposition_lines(text):
        scope["dispositions"] += 1
        for finding in check_disposition_referents(line, repo_root):
            findings.append(
                {
                    "file": _display_path(path, repo_root),
                    "line": number,
                    "enforced": enforced,
                    **finding,
                }
            )
    for finding in inconsistent_quantities(text):
        first = finding["sites"][0]["line"] if finding["sites"] else 1
        findings.append(
            {
                "file": _display_path(path, repo_root),
                "line": first,
                # Self-consistency is enforced wherever markers are USED. There is no
                # grandfathering question: an artifact with no `{{q:}}` markers cannot
                # produce a finding, so this can never fire on frozen history.
                "enforced": True,
                "kind": finding["kind"],
                "token": str(finding["id"]),
                "detail": str(finding["detail"]),
            }
        )

    # SHA enforcement is DATED, never fail-closed-on-undatable, and that
    # asymmetry with the disposition rung above is deliberate.
    #
    # `#N` was never a valid issue reference -- it was wrong the moment it was
    # typed, so an undatable artifact carrying one is fail-closed. A commit SHA
    # is different in kind: it can be correct when written and STOP resolving
    # later, when a branch is squashed, a worktree is pruned, or history is
    # rewritten. Blocking an undated rolling lesson digest for
    # citing a commit that has since been rebased away would be punishing an
    # author for a change made after they wrote it -- and the remedy a blocking
    # gate pushes toward is editing a frozen record so a checker goes green,
    # which is the failure this repo has corrected on more than one floor.
    observed = date_from_filename(path)
    sha_enforced = observed is not None and observed >= ENFORCED_FROM
    seen: set[tuple[int, str]] = set()
    for number, line in enumerate(text.splitlines(), 1):
        try:
            bad_shas = unresolvable_shas(line, repo_root, run=_cached_commit_reachable)
        except ResolverUnavailable as exc:
            # Named, counted, and NOT silently clean. The run continues -- a
            # missing resolver must not block -- but the report says the rung
            # stood down and why.
            scope["sha_resolver_unavailable"] += 1
            scope.setdefault("sha_resolver_reason", str(exc))  # type: ignore[arg-type]
            break
        # Count TOKENS actually put to the resolver, not lines walked. The
        # previous per-line increment could not fall even if `SHA_RE` stopped
        # matching entirely, which is the exact blindness the counter exists to
        # remove.
        scope["shas_resolved"] += len(sha_candidates(line))
        for sha in bad_shas:
            if (number, sha) in seen:
                continue
            seen.add((number, sha))
            declaration_key = (display_path, number, sha, line_sha256(line))
            reason = declared.get(declaration_key)
            if reason is not None:
                matched_declarations.add(declaration_key)
            findings.append(
                {
                    "file": display_path,
                    "line": number,
                    "enforced": sha_enforced and reason is None,
                    "declared_local": reason is not None,
                    "kind": (
                        "declared-local-commit-ref"
                        if reason is not None
                        else "non-durable-commit-ref"
                    ),
                    "token": sha,
                    "detail": (
                        f"`{sha}` is not reachable from the reviewed HEAD. "
                        + (
                            f"Intentional local authoring context is declared: {reason}"
                            if reason is not None
                            else "An object visible only in an authoring clone is not durable evidence."
                        )
                    ),
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".", help="Repo root that owns charness-artifacts/")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Audit only these files (repeatable); defaults to the scanned globs",
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.path:
        targets = [Path(p) if Path(p).is_absolute() else repo_root / p for p in args.path]
        empty_families: list[str] = []
    else:
        try:
            targets, empty_families = _resolved_targets(repo_root)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    declarations, declaration_defects = load_local_context_declarations(repo_root)
    declared = {
        (
            str(item["artifact"]),
            int(item["line"]),
            str(item["token"]),
            str(item["line_sha256"]),
        ): str(item["reason"])
        for item in declarations
    }
    matched_declarations: set[tuple[str, int, str, str]] = set()
    findings: list[dict[str, object]] = list(declaration_defects)
    scope: dict[str, int] = {
        "dispositions": 0,
        "shas_resolved": 0,
        "sha_resolver_unavailable": 0,
    }
    unreadable: list[str] = []
    for target in targets:
        if not target.is_file():
            # A `--path` that names nothing, or names a directory, is an INPUT
            # ERROR and must not read as a pass. Silently skipping it while
            # still counting it in `scanned` made a typo'd wiring line
            # indistinguishable from a clean run -- the gate asserting it
            # scanned a file it never opened.
            unreadable.append(_display_path(target, repo_root))
            continue
        findings.extend(audit_file(target, repo_root, scope, declared, matched_declarations))

    target_names = {_display_path(target, repo_root) for target in targets if target.is_file()}
    for key, reason in declared.items():
        artifact, line, token, _fingerprint = key
        # A focused --path run owns declarations for that path only. The default
        # corpus run owns the whole declaration surface, including paths that no
        # longer belong to the scanned globs.
        in_scope = artifact in target_names if args.path else True
        if in_scope and key not in matched_declarations:
            findings.append(
                {
                    "file": str(LOCAL_CONTEXT_DECLARATIONS),
                    "line": 1,
                    "enforced": True,
                    "kind": "stale-local-context-declaration",
                    "token": token,
                    "detail": (
                        f"{artifact}:{line} no longer produces the declared non-durable SHA finding; "
                        f"remove or correct this one-time declaration ({reason})"
                    ),
                }
            )

    #: "ran, established nothing" -- the runner's own byte for a lane that could
    #: not judge part of its scope. Opted into per label in run-quality.sh.
    UNESTABLISHED_EXIT = 3

    blocking = [f for f in findings if f["enforced"]]
    declared_local = [f for f in findings if f.get("declared_local")]
    grandfathered = [f for f in findings if not f["enforced"] and not f.get("declared_local")]
    empty_corpus = not args.path and not targets
    status = "blocked" if (blocking or unreadable) else "clean"
    report = {
        "scanned": len(targets) - len(unreadable),
        "unreadable": unreadable,
        # Scope is reported as NUMBERS so a regex that stopped matching, or a
        # resolver that stopped answering, shows up as a collapse rather than as
        # a pass. Without these, a corpus-wide false negative prints byte-for-byte
        # the same line as a real clean run.
        "dispositions_examined": scope["dispositions"],
        "shas_resolved": scope["shas_resolved"],
        "sha_resolver_unavailable_files": scope["sha_resolver_unavailable"],
        "sha_resolver_reason": scope.get("sha_resolver_reason"),
        "findings": len(findings),
        "blocking": len(blocking),
        "grandfathered": len(grandfathered),
        "declared_local": len(declared_local),
        "enforced_from": ENFORCED_FROM.isoformat(),
        "empty_corpus": empty_corpus,
        "empty_families": empty_families,
        "status": status,
        "blocking_findings": blocking,
    }

    print(f"scanned: {report['scanned']} artifact(s)")
    print(f"dispositions_examined: {report['dispositions_examined']}")
    print(f"shas_resolved: {report['shas_resolved']}")
    if report["sha_resolver_unavailable_files"]:
        # `WARNING:` is load-bearing, not decoration: run-quality.sh prints a
        # PASSING gate's log only when it matches (WARNING|WARN|WEAK|ADVISORY),
        # and a passing phase's log is deleted at EXIT. Without the token the
        # stand-down was invisible AND its explanation was destroyed.
        print(
            f"WARNING: sha_rung STOOD DOWN on {report['sha_resolver_unavailable_files']} "
            f"file(s) — {report['sha_resolver_reason']}"
        )
    print(f"enforced_from: {report['enforced_from']}")
    print(f"grandfathered (reported, not rewritten): {report['grandfathered']}")
    print(f"declared local context (reported, exact): {report['declared_local']}")
    if report["unreadable"]:
        print(f"UNREADABLE (input error, not a pass): {', '.join(report['unreadable'])}")
    if report["empty_corpus"] or report["empty_families"]:
        print(
            "DISCOVERED EMPTY: no artifacts matched the configured universe(s) "
            f"({', '.join(report['empty_families']) or 'all scanned families'}); "
            "the empty scope is reported, not treated as evidence of clean referents"
        )
    print(f"status: {report['status']}")
    for finding in blocking:
        print(
            f"- [blocking] {finding['file']}:{finding['line']} {finding['kind']}: {finding['detail']}"
        )
    for finding in grandfathered:
        print(
            f"- [grandfathered] {finding['file']}:{finding['line']} {finding['kind']}: `{finding['token']}`"
        )
    for finding in declared_local:
        print(
            f"- [declared-local] {finding['file']}:{finding['line']} {finding['kind']}: {finding['detail']}"
        )

    # Derived from `status`, NOT recomputed from `blocking`. An earlier version
    # returned `1 if blocking else 0` while `status` also accounted for unreadable
    # inputs and an empty corpus -- so the gate printed `status: blocked` and
    # exited 0. A message that disagrees with the exit code is worse than either
    # alone: the runner believes the code, the human believes the message.
    if status != "clean":
        return 1
    # A rung that could not run did not pass. Exit 3 keeps this off the runner's
    # PASS line without laundering it into a failure -- the distinction the
    # runner's own comment says cost this repo a cycle and two dead guards.
    if report["sha_resolver_unavailable_files"]:
        return UNESTABLISHED_EXIT
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
