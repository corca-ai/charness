#!/usr/bin/env python3

"""A/B efficiency harness for charness skills: turn n=1 anecdotes into n>1
comparisons with mean/range across isolated arms.

This is the EFFICIENCY axis (process + output waste), kept strictly separate from
the correctness axis (claim-fidelity pass/fail). Efficiency here is ADVISORY: this
runner never gates commit and emits no pass/fail verdict — it measures and compares.
The correctness floor stays owned by the claim matcher in
build-skill-execution-observation.mjs + cautilus. floor-addition-restraint: advisory.

What it does (`--run <config>`): for each arm, n times, capture one real isolated
`claude -p` run at the arm's git ref (capture-skill-run.sh — throwaway worktree +
isolated CLAUDE_CONFIG_DIR, so arms can't cross-contaminate, the ponytail
baseline-contamination lesson), build the observed packet
(build-skill-execution-observation.mjs), and read its per-run metrics. Aggregate
mean/min/max/median per arm and emit a side-by-side report + raw results.json. Each
run preserves its PRODUCED outputs (the changed file set, bounded) and an
assistant-text transcript into the bundle.

An "arm" is a labeled git ref (+ optional invocation override): subsumes
baseline-vs-skill (one ref without the skill, one with) and variant-A-vs-B (a ref
before a fix vs after) — the highest-value charness A/B, proving a fix's effect.

Outcome grade (skill_outcome_wiring.py): when the eval ships an outcome-assertions.json
the harness auto-grades each preserved bundle and folds the per-arm grade into the
report — an efficiency number is trustworthy only alongside an outcome check, since a
leaner number can just mean an arm did LESS. Judge-kind assertions need `--judge-cmd`
(ask-before-run spend); deterministic checks grade for free.

Self-tested instruments (`--selftest`, offline, no API): prove the extractor ranks a
known-WASTEFUL run worse than a known-LEAN one before trusting any comparison; the
harness refuses otherwise (mirrors ponytail's `run.py --selftest`). Metrics per run:
total_tokens, output_tokens, duration_ms, tool_count, waste_smell_count, output_lines
(added worktree lines vs the capture base ref, best-effort; includes an in-run commit's slice, #409).

Config schema (JSON):
  {"name": "<label>", "spec_path": "evals/cautilus/<skill>-claim-fidelity/spec.json",
   "runs": 4, "arms": [{"name": "baseline", "ref": "HEAD~1"},
                       {"name": "treatment", "ref": "HEAD", "invocation": "<override>"}]}
The invocation defaults to the spec's `prompt`; per-arm `invocation`/`spec_path`
override it. `_comment` keys are ignored.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

import grade_skill_outcome
import skill_outcome_wiring as outcome

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
AGENT_RUNTIME = Path("scripts/agent-runtime")
CAPTURE_SCRIPT = AGENT_RUNTIME / "capture-skill-run.sh"
OBSERVE_SCRIPT = AGENT_RUNTIME / "build-skill-execution-observation.mjs"

# Metrics aggregated and compared across runs. "lower is leaner" for every key
# here — the comparison reads a positive delta as the arm spending more.
METRIC_KEYS = (
    "total_tokens",
    "output_tokens",
    "duration_ms",
    "tool_count",
    "waste_smell_count",
    "output_lines",
)


# --- pure aggregation / comparison (unit-tested) --------------------------------


def aggregate_metrics(runs: list[dict]) -> dict:
    """Per-metric mean/median/min/max + pass_rate across one arm's runs."""
    agg: dict = {"n": len(runs)}
    if runs:
        passed = sum(1 for r in runs if r.get("outcome") == "passed")
        agg["pass_rate"] = round(passed / len(runs), 3)
    else:
        agg["pass_rate"] = None
    for key in METRIC_KEYS:
        vals = [r[key] for r in runs if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]
        if not vals:
            agg[key] = None
            continue
        agg[key] = {
            "mean": round(statistics.mean(vals), 1),
            "median": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
            "n": len(vals),
        }
    return agg


def relative_deltas(baseline_agg: dict, arm_agg: dict) -> dict:
    """Percent change of each metric's mean vs the baseline arm (None when either
    side is missing or the baseline mean is zero)."""
    out: dict = {}
    for key in METRIC_KEYS:
        base = baseline_agg.get(key)
        arm = arm_agg.get(key)
        if not isinstance(base, dict) or not isinstance(arm, dict) or not base.get("mean"):
            out[key] = None
            continue
        out[key] = round((arm["mean"] - base["mean"]) / base["mean"] * 100.0, 1)
    return out


def ranks_worse(lean_metrics: dict, wasteful_metrics: dict, keys: tuple[str, ...]) -> list[str]:
    """Keys on which `wasteful` is NOT strictly greater than `lean`. Empty list
    means the instruments correctly ranked the wasteful run worse on every key —
    the self-test gate."""
    failed = []
    for key in keys:
        lean = lean_metrics.get(key)
        waste = wasteful_metrics.get(key)
        if not isinstance(lean, (int, float)) or not isinstance(waste, (int, float)) or not waste > lean:
            failed.append(key)
    return failed


def _fmt_metric(stat: dict | None) -> str:
    if not isinstance(stat, dict):
        return "n/a"
    return f"{stat['mean']:g} [{stat['min']:g}–{stat['max']:g}]"


def _fmt_scalar(value: object) -> str:
    return "n/a" if value is None else str(value)


def build_report(config: dict, agg_by_arm: dict, outcome_by_arm: dict | None = None) -> str:
    """Markdown comparison: per-arm mean [min–max] table + deltas vs the first arm,
    plus the advisory outcome-grade section when an eval has an assertion set."""
    arms = list(agg_by_arm.keys())
    lines = [
        f"# Efficiency A/B — {config.get('name', 'unnamed')}",
        "",
        "Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.",
        "",
        "## Per-arm (mean [min–max])",
        "",
        "| metric | " + " | ".join(arms) + " |",
        "| --- | " + " | ".join(["---"] * len(arms)) + " |",
        "| n | " + " | ".join(str(agg_by_arm[a]["n"]) for a in arms) + " |",
        "| pass_rate | " + " | ".join(_fmt_scalar(agg_by_arm[a]["pass_rate"]) for a in arms) + " |",
    ]
    for key in METRIC_KEYS:
        row = f"| {key} | " + " | ".join(_fmt_metric(agg_by_arm[a].get(key)) for a in arms) + " |"
        lines.append(row)
    if len(arms) >= 2:
        baseline = arms[0]
        lines += ["", f"## Deltas vs `{baseline}` (mean %, + = spends more)", ""]
        others = arms[1:]
        lines.append("| metric | " + " | ".join(others) + " |")
        lines.append("| --- | " + " | ".join(["---"] * len(others)) + " |")
        for key in METRIC_KEYS:
            cells = []
            for arm in others:
                delta = relative_deltas(agg_by_arm[baseline], agg_by_arm[arm]).get(key)
                cells.append("n/a" if delta is None else f"{delta:+g}%")
            lines.append(f"| {key} | " + " | ".join(cells) + " |")
    section = outcome.render_outcome_section(outcome_by_arm) if outcome_by_arm else ""
    if section:
        lines.append(section)
    lines += [
        "",
        "## Honest caveats",
        "",
        f"- n={config.get('runs')} per arm — read the [min–max] range, not just the mean; small-n means overlap is common.",
        "- output_lines is best-effort (added lines in the worktree vs the capture base ref, including any in-run commit's slice).",
        "- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.",
        "- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.",
        "",
    ]
    return "\n".join(lines)


# --- live orchestration (capture -> observe -> metrics) -------------------------


def _git_added_lines(worktree: Path, base: str = "HEAD") -> int | None:
    """Added lines in the worktree vs `base` (its checkout commit): tracked numstat +
    untracked lines. Diff `base` not HEAD — a committing run moves HEAD off base (#409)."""
    try:
        numstat = subprocess.run(
            ["git", "-C", str(worktree), "diff", "--numstat", base],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    added = 0
    for line in numstat.splitlines():
        head = line.split("\t", 1)[0]
        if head.isdigit():
            added += int(head)
    others = subprocess.run(
        ["git", "-C", str(worktree), "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=False,
    ).stdout
    for rel in others.splitlines():
        path = worktree / rel
        try:
            with open(path, "rb") as handle:
                added += sum(1 for _ in handle)
        except OSError:  # pragma: no cover - unreadable/vanished untracked file
            continue
    return added


def _changed_files(worktree: Path, base: str = "HEAD", include_ignored: bool = False) -> list[str]:
    """Paths the run produced vs `base` (its checkout commit): tracked ACMR + untracked —
    the grader's artifact evidence, not the whole checkout. Diff `base` not HEAD: a committing
    run moves HEAD off base, so diff-vs-HEAD reads EMPTY and the judge grades blind (#409 Gap
    1). include_ignored adds gitignored outputs; defaults to HEAD for unit fixtures."""
    try:
        tracked = subprocess.run(
            ["git", "-C", str(worktree), "diff", "--name-only", "--diff-filter=ACMR", base],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    others_cmd = ["git", "-C", str(worktree), "ls-files", "--others"]
    if not include_ignored:
        others_cmd.append("--exclude-standard")
    others = subprocess.run(others_cmd, capture_output=True, text=True, check=False).stdout
    return sorted({p for p in tracked.splitlines() + others.splitlines() if p.strip()})


def preserve_outputs(worktree: Path, outputs_dir: Path, base: str = "HEAD", max_bytes: int = 65536,
                     include_ignored: bool = False) -> dict:
    """Copy the run's PRODUCED files (the changed set vs `base`, never the whole tree) into
    the durable bundle so the grader reads the real artifacts. `base` not HEAD is load-bearing
    for a committing run — see _changed_files (#409 Gap 1). Over-max_bytes files are
    omitted-with-reason; include_ignored adds gitignored outputs. Returns the manifest."""
    manifest: dict = {"copied": [], "omitted": []}
    for rel in _changed_files(worktree, base, include_ignored):
        src = worktree / rel
        if not src.is_file():
            continue
        size = src.stat().st_size
        if size > max_bytes:
            manifest["omitted"].append({"path": rel, "reason": f"size {size} > {max_bytes}"})
            continue
        if outcome.is_binary_file(src):
            manifest["omitted"].append({"path": rel, "reason": "binary (NUL byte)"})
            continue
        dst = outputs_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        manifest["copied"].append(rel)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    (outputs_dir / "outputs-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _write_transcript(stream_path: Path, dest: Path, max_chars: int = 20000) -> None:
    """Render the assistant TEXT turns from the capture's complete stream-json stdout
    (stream.jsonl) into dest — AUTHORITATIVE: the session tree can drop the final block on a
    clean exit, blinding the judge to the closeout (#409 Gap 2). Excludes tool_result contents
    (no secrets); a missing/unreadable stream yields an empty transcript, never a crash."""
    parts: list[str] = []
    try:
        lines = Path(stream_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                parts.append(block["text"])
    dest.write_text("\n\n".join(parts)[:max_chars], encoding="utf-8")


def _parse_session_tree(stdout: str) -> str | None:
    for line in stdout.splitlines():
        if line.startswith("SESSION_TREE="):
            return line[len("SESSION_TREE="):].strip()
    return None


def _capture_base(out_dir: Path) -> str:
    """The worktree's checkout commit (capture-skill-run.sh records it in base-commit.txt);
    extractors diff this, not the run-moved HEAD (#409). HEAD fallback when the marker is absent."""
    try:
        return (out_dir / "base-commit.txt").read_text(encoding="utf-8").strip() or "HEAD"
    except OSError:
        return "HEAD"


def _metrics_from_packet(packet: dict) -> dict:
    evaluation = (packet.get("evaluations") or [{}])[0]
    metrics = dict(evaluation.get("metrics") or {})
    metrics["outcome"] = evaluation.get("outcome")
    return metrics


def run_one(repo_root: Path, ref: str, invocation: str, spec_path: Path, out_dir: Path, timeout_sec: int) -> dict:
    """Capture one isolated run at `ref`, build its observed packet, return metrics.

    Raises RuntimeError (carrying the captured stderr tail) on a capture/observe
    failure so run_ab can log + skip the data point instead of crashing the whole
    matrix, and so the real error is surfaced rather than a bare CalledProcessError."""
    capture = subprocess.run(
        [
            "bash", str(repo_root / CAPTURE_SCRIPT),
            "--ref", ref, "--invocation", invocation,
            "--out-dir", str(out_dir), "--repo-root", str(repo_root),
            "--timeout-sec", str(timeout_sec),
        ],
        capture_output=True, text=True, check=False,
    )
    if capture.returncode != 0:
        raise RuntimeError(f"capture failed (rc={capture.returncode}) for ref {ref}:\n{capture.stderr[-2000:]}")
    tree = _parse_session_tree(capture.stdout)
    if not tree:
        raise RuntimeError(f"capture produced no SESSION_TREE for ref {ref}\n{capture.stderr[-2000:]}")
    observed = out_dir / "observed.v1.json"
    observe = subprocess.run(
        [
            "node", str(repo_root / OBSERVE_SCRIPT),
            "--session-tree", tree, "--spec", str(spec_path), "--output", str(observed),
        ],
        capture_output=True, text=True, check=False,
    )
    if observe.returncode != 0:
        raise RuntimeError(f"observe failed (rc={observe.returncode}) for ref {ref}:\n{observe.stderr[-2000:]}")
    metrics = _metrics_from_packet(json.loads(observed.read_text(encoding="utf-8")))
    metrics["output_lines"] = _git_added_lines(out_dir / "worktree", _capture_base(out_dir))
    # Transcript from stream.jsonl (the complete stdout), NOT the session tree: the tree can
    # drop the final assistant block (the closeout) on a clean exit (#409 Gap 2).
    _write_transcript(out_dir / "stream.jsonl", out_dir / "transcript.txt")
    return metrics


def _cleanup_run(repo_root: Path, out_dir: Path) -> None:
    subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "remove", "--force", str(out_dir / "worktree")],
        capture_output=True, text=True, check=False,
    )
    shutil.rmtree(out_dir, ignore_errors=True)


def run_ab(repo_root: Path, config: dict, results_dir: Path, timeout_sec: int, keep_runs: bool,
           judge_fn=None, keep_untracked: bool = False) -> dict:
    runs = int(config.get("runs", 4))
    default_spec = config.get("spec_path")
    raw_runs: list[dict] = []
    agg_by_arm: dict = {}
    outcome_by_arm: dict = {}
    gate = outcome.GraderGate()
    results_dir.mkdir(parents=True, exist_ok=True)
    for arm in config["arms"]:
        spec_path = repo_root / (arm.get("spec_path") or default_spec)
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        invocation = arm.get("invocation") or spec["prompt"]
        assertion_set = outcome.resolve_assertion_set(spec_path)
        arm_runs: list[dict] = []
        preserved_dirs: list[Path] = []
        for index in range(runs):
            out_dir = results_dir / "work" / f"{arm['name']}__{index}"
            print(f"[{arm['name']}] run {index + 1}/{runs} @ {arm['ref']}", file=sys.stderr)
            try:
                metrics = run_one(repo_root, arm["ref"], invocation, spec_path, out_dir, timeout_sec)
                record = {"arm": arm["name"], "ref": arm["ref"], "run": index, **metrics}
                arm_runs.append(record)
                raw_runs.append(record)
                preserve = results_dir / "preserved" / f"{arm['name']}__{index}"
                preserve.mkdir(parents=True, exist_ok=True)
                for name in ("observed.v1.json", "trace-digest.jsonl", "transcript.txt"):
                    src = out_dir / name
                    if src.is_file():
                        shutil.copy(src, preserve / name)
                # Outcome-grader evidence: the run's PRODUCED files (changed set only),
                # so output_file_* assertions and the LLM judge can read real artifacts.
                worktree = out_dir / "worktree"
                if worktree.is_dir():
                    # Diff the produced set against the capture base, not the worktree HEAD:
                    # a faithful run commits its slice and moves HEAD, so diff-vs-HEAD is
                    # empty and the grader sees an empty outputs/ (#409 Gap 1).
                    preserve_outputs(worktree, preserve / "outputs", _capture_base(out_dir),
                                     include_ignored=keep_untracked)
                preserved_dirs.append(preserve)
            except (subprocess.CalledProcessError, RuntimeError) as exc:
                # One flaky capture must not nuke a multi-run matrix or leak its
                # worktree; log, drop the data point, and let aggregate cope with n-1.
                print(f"  [skip] {arm['name']} run {index}: {exc}", file=sys.stderr)
            finally:
                if not keep_runs:
                    _cleanup_run(repo_root, out_dir)
        agg_by_arm[arm["name"]] = aggregate_metrics(arm_runs)
        # Outcome grade: decoupled from capture so a grade error never drops a data
        # point. Skipped-with-reason when the eval has no assertion set (most today).
        arm_outcomes = outcome.grade_arm(preserved_dirs, assertion_set, judge_fn, gate)
        # attempted = bundles grading actually ran on (set present + grader trusted), so
        # aggregate_arm can distinguish grade-failures from a wholesale skip. gate.ok()
        # is memoized, so this re-check is free.
        attempted = len(preserved_dirs) if (assertion_set is not None and gate.ok()) else 0
        outcome_by_arm[arm["name"]] = outcome.aggregate_arm(arm_outcomes, assertion_set, attempted)
    report = build_report(config, agg_by_arm, outcome_by_arm)
    (results_dir / "results.json").write_text(
        json.dumps({"config": config, "runs": raw_runs, "aggregate": agg_by_arm,
                    "outcome": outcome_by_arm}, indent=2) + "\n",
        encoding="utf-8",
    )
    (results_dir / "report.md").write_text(report + "\n", encoding="utf-8")
    return {"aggregate": agg_by_arm, "outcome": outcome_by_arm, "report": report, "runs": raw_runs}


# --- self-test: synthetic lean vs wasteful trees, real extractor ----------------


def _event(tools: list[dict], output_tokens: int, ts: str) -> dict:
    return {
        "type": "assistant",
        "timestamp": ts,
        "message": {
            "role": "assistant",
            "usage": {"output_tokens": output_tokens},
            "content": [{"type": "tool_use", "id": t["id"], "name": t["name"], "input": t["input"]} for t in tools],
        },
    }


def _result(tool_id: str, content: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": content}]}}


def _ts(second: int) -> str:
    return f"2026-01-01T00:00:{second:02d}.000Z"


def _write_lean(tree_dir: Path) -> None:
    events = [
        _event([{"id": "r1", "name": "Read", "input": {"file_path": "/x/a.md"}}], 20, _ts(0)),
        _result("r1", "a" * 500),
        _event([{"id": "r2", "name": "Read", "input": {"file_path": "/x/b.md"}}], 15, _ts(2)),
        _result("r2", "b" * 500),
        _event([{"id": "b1", "name": "Bash", "input": {"command": "ls"}}], 10, _ts(4)),
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "done"}]}},
    ]
    _dump(tree_dir, events)


def _write_wasteful(tree_dir: Path) -> None:
    events = [
        _event([{"id": "d1", "name": "Read", "input": {"file_path": "/x/a.md"}}], 40, _ts(0)),
        _result("d1", "a" * 800),
        _event([{"id": "d2", "name": "Read", "input": {"file_path": "/x/a.md"}}], 40, _ts(3)),  # duplicate_read
        _result("d2", "a" * 800),
        _event([{"id": "g1", "name": "Bash", "input": {"command": "git status"}}], 30, _ts(6)),
        _event([{"id": "g2", "name": "Bash", "input": {"command": "git status"}}], 30, _ts(9)),  # repeated_bash
        _event([{"id": "big", "name": "Read", "input": {"file_path": "/x/big.md"}}], 50, _ts(12)),
        _result("big", "z" * 60000),  # large_output
        _event([{"id": "e1", "name": "Edit", "input": {"file_path": "/x/c.md"}}], 20, _ts(15)),
        _event([{"id": "e2", "name": "Edit", "input": {"file_path": "/x/c.md"}}], 20, _ts(18)),
        _event([{"id": "e3", "name": "Edit", "input": {"file_path": "/x/c.md"}}], 20, _ts(21)),  # repeated_edit
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "done"}]}},
    ]
    _dump(tree_dir, events)


def _dump(tree_dir: Path, events: list[dict]) -> None:
    tree_dir.mkdir(parents=True, exist_ok=True)
    (tree_dir / "session.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")


_SELFTEST_SPEC = {
    "skillId": "selftest",
    "evaluationId": "execution-selftest",
    "targetId": "selftest",
    "prompt": "/charness:selftest",
    "requiredCommandFragments": [],
    "declaredReferences": [],
}
# Keys the self-test asserts wasteful > lean on. output_lines/duration are
# excluded: output_lines needs a real worktree, and both trees share a timeline.
SELFTEST_KEYS = ("total_tokens", "output_tokens", "tool_count", "waste_smell_count")


def _observe(repo_root: Path, tree_dir: Path, spec_path: Path, out_path: Path) -> dict:
    subprocess.run(
        ["node", str(repo_root / OBSERVE_SCRIPT), "--session-tree", str(tree_dir), "--spec", str(spec_path), "--output", str(out_path)],
        capture_output=True, text=True, check=True,
    )
    return _metrics_from_packet(json.loads(out_path.read_text(encoding="utf-8")))


def selftest(repo_root: Path) -> int:
    """Prove the extractor ranks a known-wasteful run worse than a known-lean one
    on every SELFTEST_KEYS metric. Refuse (exit 1) if it does not."""
    with tempfile.TemporaryDirectory(prefix="charness-ab-selftest-") as tmp:
        root = Path(tmp)
        spec_path = root / "spec.json"
        spec_path.write_text(json.dumps(_SELFTEST_SPEC), encoding="utf-8")
        _write_lean(root / "lean")
        _write_wasteful(root / "wasteful")
        lean = _observe(repo_root, root / "lean", spec_path, root / "lean.json")
        wasteful = _observe(repo_root, root / "wasteful", spec_path, root / "wasteful.json")
    failed = ranks_worse(lean, wasteful, SELFTEST_KEYS)
    for key in SELFTEST_KEYS:
        mark = "XX" if key in failed else "ok"
        print(f"  {mark} {key}: lean={lean.get(key)} wasteful={wasteful.get(key)}")
    if failed:
        print(f"SELFTEST FAILED: extractor did not rank wasteful worse on {failed}; instruments not trustworthy.", file=sys.stderr)
        return 1
    print("SELFTEST PASSED: extractor ranks the wasteful run worse on every metric.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A/B efficiency harness for charness skills (advisory; never gates).")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--selftest", action="store_true", help="Offline: prove the metric instruments rank known-bad worse than known-good (no API).")
    parser.add_argument("--run", type=Path, help="Path to an A/B config JSON; runs the live matrix (real claude -p captures).")
    parser.add_argument("--out-dir", type=Path, help="Results dir for --run (default: charness-artifacts/efficiency/<name>).")
    parser.add_argument("--timeout-sec", type=int, default=1200, help="Per-capture timeout.")
    parser.add_argument("--keep-runs", action="store_true", help="Keep each run's worktree/config instead of cleaning up.")
    parser.add_argument("--keep-untracked-outputs", action="store_true",
                        help="Also preserve gitignored runtime outputs into each bundle (for a skill whose "
                             "meaningful product is gitignored runtime state, e.g. hitl's queue); off by default "
                             "so the committed bundle stays clean. Bounded by the per-file size cap.")
    parser.add_argument("--judge-cmd", type=str, default=None,
                        help="Shell command for the live OUTCOME judge (ask-before-run SPEND), forwarded to the "
                             "outcome grader; omit to SKIP judge-kind assertions (free, offline).")
    parser.add_argument("--judge-timeout-sec", type=int, default=300,
                        help="Per-assertion timeout for the live judge command (default 300s).")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    if args.selftest:
        return selftest(repo_root)
    if args.run:
        # The slice's promise is "self-tested instruments refuse before spend": gate
        # the live matrix on the offline self-test so a broken extractor can never
        # produce a comparison we'd trust. Cheap (no API) and fail-closed.
        print("running instrument self-test before the live matrix...", file=sys.stderr)
        code = selftest(repo_root)
        if code != 0:
            print("refusing --run: instrument self-test failed; fix the extractor before spending on a live matrix.", file=sys.stderr)
            return code
        config = json.loads(args.run.read_text(encoding="utf-8"))
        results_dir = args.out_dir or (repo_root / "charness-artifacts" / "efficiency" / config.get("name", "ab"))
        judge_fn = grade_skill_outcome.judge_via_command(args.judge_cmd, args.judge_timeout_sec) if args.judge_cmd else None
        ab_result = run_ab(repo_root, config, results_dir.resolve(), args.timeout_sec, args.keep_runs,
                           judge_fn, args.keep_untracked_outputs)
        print(ab_result["report"])
        print(f"\nresults: {results_dir}", file=sys.stderr)
        return 0
    parser.error("one of --selftest or --run is required")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
