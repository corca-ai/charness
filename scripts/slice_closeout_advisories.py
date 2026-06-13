#!/usr/bin/env python3
"""Advisory (#328) slice-closeout helpers.

Surface likely-broken doc/SKILL test pins and the one-shot skill-surface
preflight BEFORE the broad pytest / mutation-coverage producer pays for the
failure. These never block closeout; they print ``WARN``/``ADVISORY`` lines to
stderr so the fix happens before the expensive cycle, not at minute six of the
broad suite.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

DEFAULT_GATE_RUNTIME_BUDGET_SECONDS = 120.0
DEFAULT_OVERSLICE_ARTIFACT_RUN = 3

# The rule's own home: excluded from the recorded-call scan so its example prose
# (`a Floor-Addition Restraint: line`) never counts as a recorded call.
_FLOOR_RESTRAINT_RULE_DOC = "docs/conventions/implementation-discipline.md"
# Floors are defined in source and asserted in tests; a `report["ok"] = False` in
# tests/ is a fixture, not a floor, so detection is scoped to these prefixes.
_FLOOR_SOURCE_PREFIXES = ("skills/", "scripts/")


def advise_prose_pin(repo_root: Path, changed_paths: list[str]) -> None:
    """Point at tests/ assertions that pin doc/SKILL prose or paths the slice
    changed. Reads the working-tree diff directly; the substring/path match is a
    heuristic, so it stays advisory."""
    if not any(path.endswith(".md") for path in changed_paths):
        return
    lib = import_repo_module(__file__, "scripts.check_prose_pin")
    report = lib.build_report(repo_root, paths=None, test_roots=[repo_root / "tests"])
    if report["status"] == "findings":
        print(lib.format_human(report), file=sys.stderr)


def _added_vs_base(repo_root: Path, paths: list[str], base: str = "origin/main") -> list[str]:
    """Paths absent from the base tree — the changed-line gate's range anchor.
    Degrades to no advisory when the anchor ref does not resolve (tmp repos).
    Checks `base:<path>` directly rather than merge-base(base, HEAD): a file
    deleted upstream but present at the merge-base reads as "added" and fires
    a spurious stderr-only advisory — accepted over the extra plumbing."""
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base],
        cwd=repo_root,
        capture_output=True,
    )
    if probe.returncode != 0:
        return []
    added: list[str] = []
    for path in paths:
        exists = subprocess.run(
            ["git", "cat-file", "-e", f"{base}:{path}"],
            cwd=repo_root,
            capture_output=True,
        )
        if exists.returncode != 0:
            added.append(path)
    return added


def advise_new_pool_module(repo_root: Path, changed_paths: list[str]) -> None:
    """A slice that ADDS a new mutation-pool module gets no commit-time signal
    that its environment-dependent branches (import fallbacks, dep-missing
    degrades) are uncovered; the first signal otherwise arrives at the bundle
    boundary, where repair costs a full instrumented producer re-run. Surface
    the documented early self-check (implementation-discipline.md) while the
    branch list is still cheap to walk. The unmocked glue (real git anchor +
    real eligibility glob) is pinned end-to-end by the seeded-repo positive in
    tests/quality_gates/test_slice_closeout_new_pool_advisory.py."""
    changed_py = [path for path in changed_paths if path.endswith(".py")]
    if not changed_py:
        return
    sample = import_repo_module(__file__, "scripts.sample_mutation_files")
    eligible = set(sample.list_eligible(repo_root))
    new_pool = sorted(set(_added_vs_base(repo_root, changed_py)) & eligible)
    if not new_pool:
        return
    print(
        "ADVISORY: new mutation-pool module(s) added vs origin/main: "
        + ", ".join(new_pool)
        + "; walk each branch (import fallbacks, dep-missing degrades) into the "
        "introducing slice's tests, then run the early changed-line self-check "
        "(docs/conventions/implementation-discipline.md) so the bundle producer "
        "CONFIRMS instead of discovering: run the --produce-mutation-coverage "
        "closeout, then python3 scripts/check_changed_line_mutation_coverage.py "
        "--repo-root . --base-sha origin/main --reuse-coverage. Before citing a "
        "CI mutation run as changed-line proof, gate the claim with "
        "python3 scripts/check_mutation_run_proof.py --claim changed-line "
        "(a dispatch-green run proves only the score path).",
        file=sys.stderr,
    )


def advise_skill_surface_preflight(repo_root: Path, changed_paths: list[str]) -> None:
    """When the slice edits a gated skill package, point at the one-shot
    portable-package preflight so the serial gate round-trips (ergonomics,
    ownership-overlap, attention-state, length headroom) surface in one pass
    instead of one commit-time gate failure at a time."""
    edited = [
        path
        for path in changed_paths
        if path.startswith(("skills/public/", "skills/support/"))
        and (path.endswith("/SKILL.md") or "/references/" in path)
    ]
    if not edited:
        return
    print(
        "ADVISORY: edited gated skill surface(s); run the one-shot portable-package "
        "preflight to surface all findings at once: "
        f"python3 scripts/check_skill_surface_preflight.py --path {edited[0]} --run-checks",
        file=sys.stderr,
    )


def resolve_gate_runtime_budget_seconds() -> float:
    """Portable, override-able budget for a single closeout gate's baseline
    runtime. A gate that PASSES but exceeds this is gate-baseline / code-quality
    debt (spec achieve-efficiency-improvements, direction C), distinct from
    cadence waste and from 'necessary safety cost'. The env override mirrors the
    progress-interval knob already used by run_slice_closeout; a richer per-gate
    adapter field is a follow-up probe (spec C budget probe)."""
    raw = os.environ.get("CHARNESS_GATE_RUNTIME_BUDGET_SECONDS")
    if raw is None:
        return DEFAULT_GATE_RUNTIME_BUDGET_SECONDS
    try:
        return max(1.0, float(raw))
    except ValueError:
        return DEFAULT_GATE_RUNTIME_BUDGET_SECONDS


def evaluate_gate_runtime_budget(
    executed_commands: list[dict], *, budget_seconds: float
) -> list[dict]:
    """Per-gate runtime verdict over the gates run_slice_closeout actually ran.
    Returns one record per OVER-BUDGET gate so the durable closeout JSON payload
    carries the signal, not only stderr (spec C2). Scope is honest: this sees
    ONLY gates executed THROUGH run_slice_closeout (sync / verify / broad-pytest);
    the host pre-push hook runs as its own process and is NOT covered here (spec
    C1 — capturing the hook's own runtime is a separate probe). Cached/reused
    gates carry no timing and are excluded from the verdict."""
    over_budget: list[dict] = []
    for entry in executed_commands:
        elapsed = entry.get("elapsed_seconds")
        if elapsed is None:
            continue
        if float(elapsed) > budget_seconds:
            command = str(entry.get("command") or "")
            over_budget.append(
                {
                    "phase": entry.get("phase"),
                    "command": command,
                    "elapsed_seconds": float(elapsed),
                    "budget_seconds": budget_seconds,
                    "over_budget": True,
                }
            )
    return over_budget


def advise_gate_runtime_budget(over_budget: list[dict]) -> None:
    """Non-blocking stderr advisory for gates that passed but exceeded the
    gate-baseline runtime budget. Pairs with the retro gate-baseline-runtime
    waste lens (section-guide / phase-aware-efficiency)."""
    if not over_budget:
        return
    budget = over_budget[0]["budget_seconds"]
    names = ", ".join(
        f"{r['phase']}:{r['command'][:60]} {r['elapsed_seconds']:.1f}s"
        for r in over_budget
    )
    print(
        f"ADVISORY: gate-baseline runtime over budget (> {budget:.0f}s): {names}. "
        "A gate that PASSES but is slow by design is gate-baseline / code-quality "
        "debt, not 'necessary safety cost' — classify it in the retro's "
        "gate-baseline-runtime waste lens (route to the gate-implementation "
        "owner), or raise CHARNESS_GATE_RUNTIME_BUDGET_SECONDS if the cost is "
        "accepted. Note: the host pre-push hook runs as its own process and is "
        "NOT measured here.",
        file=sys.stderr,
    )


def attach_gate_runtime_advisory(payload: dict) -> None:
    """Resolve the budget, evaluate the executed gates, attach the verdict to the
    durable JSON ``payload``, and emit the non-blocking stderr advisory — one call
    so the closeout entrypoint stays within its function-length budget."""
    budget = resolve_gate_runtime_budget_seconds()
    over_budget = evaluate_gate_runtime_budget(
        payload["executed_commands"], budget_seconds=budget
    )
    payload["gate_runtime_advisory"] = {
        "budget_seconds": budget,
        "over_budget": over_budget,
    }
    advise_gate_runtime_budget(over_budget)


def resolve_overslice_artifact_run_threshold() -> int:
    """Override-able threshold for the over-slicing advisory: how many consecutive
    artifact-only commits read as process churn (spec achieve-efficiency, B).
    Floor of 2 — a single artifact-only commit is never churn."""
    raw = os.environ.get("CHARNESS_OVERSLICE_ARTIFACT_RUN")
    if raw is None:
        return DEFAULT_OVERSLICE_ARTIFACT_RUN
    try:
        return max(2, int(raw))
    except ValueError:
        return DEFAULT_OVERSLICE_ARTIFACT_RUN


def trailing_artifact_only_run(commit_path_lists: list[list[str]]) -> int:
    """Count the leading run (most-recent-first) of commits whose changed paths are
    ALL under ``charness-artifacts/`` — the operational-artifact churn signal
    (meaningful-slice-cadence: frequent artifact-only commits are process churn,
    not progress). A commit touching any code/skill/doc path breaks the run."""
    run = 0
    for paths in commit_path_lists:
        if paths and all(p.startswith("charness-artifacts/") for p in paths):
            run += 1
        else:
            break
    return run


def _recent_commit_path_lists(repo_root: Path, max_commits: int) -> list[list[str]]:
    """Per-commit changed-path lists for the last ``max_commits`` commits,
    most-recent-first. Degrades to ``[]`` when the git command fails (e.g. not a
    git repo). Matches the sibling ``_added_vs_base`` returncode-only pattern: the
    closeout context is always a git repo with git present."""
    log = subprocess.run(
        ["git", "log", "-n", str(max_commits), "--format=%H"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if log.returncode != 0:
        return []
    result: list[list[str]] = []
    for sha in log.stdout.split():
        show = subprocess.run(
            ["git", "show", "--pretty=format:", "--name-only", sha],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if show.returncode != 0:
            break
        result.append([line for line in show.stdout.splitlines() if line.strip()])
    return result


def over_slice_run(repo_root: Path) -> tuple[int, int]:
    """The over-slice run value ``advise_over_slicing`` decides on, plus its
    threshold, exposed as ONE computation so the E1 closeout-telemetry record
    (spec achieve-efficiency, E) stores the same number the advisory prints — no
    second, drifting calculation."""
    threshold = resolve_overslice_artifact_run_threshold()
    run = trailing_artifact_only_run(
        _recent_commit_path_lists(repo_root, max_commits=threshold + 1)
    )
    return run, threshold


# --- floor-addition restraint nudge (spec achieve-efficiency, follow-up:floor- ---
# addition-restraint-nudge). A conservative before/after detector: it fires only
# when a diff ADDS a new blocking floor (a new `report["ok"] = False` site, or a
# new member in a REQUIRED_*/_SECTIONS/_EVIDENCE_NAMES set) without a recorded
# Floor-Addition Restraint call. Deliberately conservative (a probe): exotic floor
# shapes may not be caught — better a missed nudge than a false one that trains
# token-theater, and a *blocking* gate is rejected as the exact reflex D names.
# Anchored to line-start-after-indentation so it counts only an actual assignment
# STATEMENT — a `report["ok"] = False` mentioned mid-line in a comment, docstring,
# or print string (including this module's own) is not a floor and is not counted.
_OK_FALSE_FLOOR = re.compile(r"""^[ \t]*report\s*\[\s*['"]ok['"]\s*\]\s*=\s*False""", re.MULTILINE)
_REQUIRED_ASSIGN = re.compile(r"^(?P<name>[A-Z][A-Z0-9_]+)\s*=\s*(?P<open>[(\[])", re.MULTILINE)
_QUOTED = re.compile(r"['\"]([^'\"\n]+)['\"]")
# A blocking-floor required set names REQUIRED/_SECTIONS/_EVIDENCE_NAMES — but these
# substrings also name non-floor sets (optional/advisory/narration affordances, the
# RECORDED_WORK content-scan helper), so those are excluded to keep the nudge from
# false-firing on a set whose members are not a blocking requirement.
_FLOOR_SET_NEGATIVE = ("OPTIONAL", "ADVISORY", "EXEMPT", "NARRATION", "RECORDED_WORK")
# A recorded call is a `Floor-Addition Restraint:`/`# floor-addition-restraint:`
# colon-form line with content — anchored to line-start (after optional markup) so
# prose that merely *describes* the marker form mid-sentence is not a recorded call.
_RESTRAINT_MARKER = re.compile(
    r"^[\s>#*-]*floor[- ]addition[- ]restraint\s*:\s*\S", re.IGNORECASE | re.MULTILINE
)


def _is_floor_set_name(name: str) -> bool:
    if any(neg in name for neg in _FLOOR_SET_NEGATIVE):
        return False
    return "REQUIRED" in name or name.endswith("_SECTIONS") or name.endswith("_EVIDENCE_NAMES")


def _balanced_segment(text: str, open_index: int) -> str:
    open_char = text[open_index]
    close_char = ")" if open_char == "(" else "]"
    depth = 0
    for i in range(open_index, len(text)):
        if text[i] == open_char:
            depth += 1
        elif text[i] == close_char:
            depth -= 1
            if depth == 0:
                return text[open_index : i + 1]
    return text[open_index:]


def ok_false_site_count(text: str) -> int:
    """Count `report["ok"] = False` blocking-floor assignment sites in ``text``."""
    return len(_OK_FALSE_FLOOR.findall(text))


def required_set_members(text: str) -> dict[str, set[str]]:
    """Map each module-level REQUIRED_*/_SECTIONS/_EVIDENCE_NAMES tuple/list name to
    its string members (handles single- and multi-line literals via bracket
    balancing). Other UPPER_SNAKE assignments are ignored."""
    members: dict[str, set[str]] = {}
    for match in _REQUIRED_ASSIGN.finditer(text):
        name = match.group("name")
        if not _is_floor_set_name(name):
            continue
        segment = _balanced_segment(text, match.start("open"))
        members.setdefault(name, set()).update(_QUOTED.findall(segment))
    return members


def detect_new_floors(base_text: str, new_text: str, path: str) -> list[dict]:
    """Findings for blocking floors present in ``new_text`` but not ``base_text``."""
    findings: list[dict] = []
    new_sites = ok_false_site_count(new_text) - ok_false_site_count(base_text)
    if new_sites > 0:
        findings.append({"path": path, "kind": "ok_false_site",
                         "detail": f'{new_sites} new `report["ok"] = False` blocking site(s)'})
    base_members = required_set_members(base_text)
    for name, members in required_set_members(new_text).items():
        added = members - base_members.get(name, set())
        if added:
            findings.append({"path": path, "kind": "required_set_entry",
                             "detail": f"new {name} member(s): {', '.join(sorted(added))}"})
    return findings


def restraint_call_recorded(added_text: str) -> bool:
    """True when added diff lines carry a `Floor-Addition Restraint:` colon-form
    call (a line or `# floor-addition-restraint:` comment), not a bare mention."""
    return _RESTRAINT_MARKER.search(added_text) is not None


def _git_show(repo_root: Path, ref_path: str) -> str:
    res = subprocess.run(["git", "show", ref_path], cwd=repo_root, capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else ""


def _added_diff_lines(repo_root: Path, base: str, paths: list[str]) -> str:
    if not paths:
        return ""
    res = subprocess.run(["git", "diff", "--unified=0", base, "--", *paths],
                         cwd=repo_root, capture_output=True, text=True)
    if res.returncode != 0:
        return ""
    return "\n".join(line[1:] for line in res.stdout.splitlines()
                     if line.startswith("+") and not line.startswith("+++"))


def advise_floor_addition_restraint(repo_root: Path, changed_paths: list[str], base: str = "origin/main") -> None:
    """Non-blocking nudge: a new blocking floor added without a recorded
    Floor-Addition Restraint call (spec achieve-efficiency,
    follow-up:floor-addition-restraint-nudge). Gives the implementation-discipline
    checklist teeth without a blocking gate. Degrades silently off a git repo or
    when ``base`` does not resolve (tmp repos)."""
    probe = subprocess.run(["git", "rev-parse", "--verify", "--quiet", base], cwd=repo_root, capture_output=True)
    if probe.returncode != 0:
        return
    source_py = [p for p in changed_paths
                 if p.endswith(".py") and p.startswith(_FLOOR_SOURCE_PREFIXES) and not p.startswith("tests/")]
    findings: list[dict] = []
    for path in source_py:
        try:
            new_text = (repo_root / path).read_text(encoding="utf-8")
        except OSError:
            continue
        findings.extend(detect_new_floors(_git_show(repo_root, f"{base}:{path}"), new_text, path))
    if not findings:
        return
    marker_paths = [p for p in changed_paths if p != _FLOOR_RESTRAINT_RULE_DOC]
    if restraint_call_recorded(_added_diff_lines(repo_root, base, marker_paths)):
        return
    summary = "; ".join(f"{f['path']}: {f['detail']}" for f in findings)
    print(
        "ADVISORY: new blocking floor added without a recorded Floor-Addition Restraint call — "
        + summary + ". Run the Floor-Addition Restraint checklist "
        "(docs/conventions/implementation-discipline.md): does it raise closeout-contract weight? "
        "is a non-blocking advisory/prose enough? can the describe-first preflight absorb it? "
        "Prefer an advisory unless the recurrence is recorded — a blocking floor on first sight "
        "trains token-theater. Then record the call (a `Floor-Addition Restraint:` line in the "
        "slice's commit/goal/critique, or a `# floor-addition-restraint:` comment at the site).",
        file=sys.stderr,
    )


def advise_over_slicing(repo_root: Path) -> None:
    """Non-blocking advisory (spec achieve-efficiency, B): a run of consecutive
    charness-artifacts/-only commits is over-slicing churn. Enabled by default;
    the threshold tunes via ``CHARNESS_OVERSLICE_ARTIFACT_RUN``. Reads git
    directly and degrades silently when the git command fails (not a git repo)."""
    run, threshold = over_slice_run(repo_root)
    if run < threshold:
        return
    print(
        f"ADVISORY: {run} consecutive charness-artifacts/-only commits — frequent "
        "artifact-only commits are process churn, not progress. Fold artifact / "
        "current-pointer updates into the meaningful unit they support, and do not "
        "re-fire critique or broad proof within one unchanged slice intent "
        "(meaningful-slice-cadence). Update `Current slice intent:` in the goal "
        "frame when the intent actually changes, not per commit.",
        file=sys.stderr,
    )
