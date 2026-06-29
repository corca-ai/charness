#!/usr/bin/env python3

"""A/B efficiency harness for charness skills: turn n=1 anecdotes into n>1
comparisons with mean/range across isolated arms.

This is the EFFICIENCY axis (process + output waste), kept strictly separate from
the correctness axis (claim-fidelity pass/fail). Efficiency here is ADVISORY: this
runner never gates commit and emits no pass/fail verdict on a skill — it measures
and compares, and a human reads the comparison. The correctness floor stays owned
by the claim matcher in build-skill-execution-observation.mjs + cautilus.

What it does (`--run <config>`):
  for each arm, n times: capture one real isolated `claude -p` run at the arm's
  git ref (capture-skill-run.sh — throwaway worktree + isolated CLAUDE_CONFIG_DIR,
  so arms can't cross-contaminate, the ponytail baseline-contamination lesson),
  build the observed packet (build-skill-execution-observation.mjs), and read its
  per-run metrics. Then aggregate mean/min/max/median per arm and emit a side-by-side
  comparison report + raw results.json. Each run also preserves its PRODUCED outputs
  (the changed file set, bounded) and an assistant-text transcript into the bundle, so
  the outcome grader (grade_skill_outcome.py) can read the real artifacts the run made.

An "arm" is a labeled git ref (+ optional invocation override). This subsumes
baseline-vs-skill (one ref without the skill, one with) and variant-A-vs-B (a ref
before a fix vs after) — the highest-value charness A/B, since it proves a skill
fix's efficiency effect.

Self-tested instruments (`--selftest`, offline, no API): before trusting any live
comparison, prove the metric extractor ranks a known-WASTEFUL run worse than a
known-LEAN one (more tokens, more tool calls, more waste smells). If it does not,
the harness refuses — a comparison you can't trust is worse than none. Mirrors
ponytail's `run.py --selftest`.

Metrics per run (all from the observed packet; output_lines from the worktree):
  total_tokens, output_tokens, duration_ms, tool_count, waste_smell_count,
  output_lines (added lines in the worktree vs the ref, best-effort — the LOC-side
  metric; excludes any in-run commits).

NOT in this slice (deferred with rationale): an audited LLM judge (over-build /
completeness). The deterministic skeleton ships and is proven first; the judge is
the expensive, subjective part and is a clean follow-up. floor-addition-restraint:
this whole tool is advisory, never a blocking floor.

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


def build_report(config: dict, agg_by_arm: dict) -> str:
    """Markdown comparison: per-arm mean [min–max] table + deltas vs the first arm."""
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
    lines += [
        "",
        "## Honest caveats",
        "",
        f"- n={config.get('runs')} per arm — read the [min–max] range, not just the mean; small-n means overlap is common.",
        "- output_lines is best-effort (added lines in the worktree vs the ref; excludes any in-run commits).",
        "- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.",
        "- Cross-ref arms hold project CLAUDE.md / find-skills routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.",
        "",
    ]
    return "\n".join(lines)


# --- live orchestration (capture -> observe -> metrics) -------------------------


def _git_added_lines(worktree: Path) -> int | None:
    """Added lines in the worktree vs its checked-out ref: tracked diff numstat +
    untracked file line counts. None when the dir is not a usable git tree."""
    try:
        numstat = subprocess.run(
            ["git", "-C", str(worktree), "diff", "--numstat", "HEAD"],
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


def _changed_files(worktree: Path) -> list[str]:
    """Paths the run added or modified vs its checked-out ref (tracked ACMR +
    untracked). The set of files a charness skill actually PRODUCED — the outcome
    grader's artifact evidence — not the whole repo checkout."""
    try:
        tracked = subprocess.run(
            ["git", "-C", str(worktree), "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    others = subprocess.run(
        ["git", "-C", str(worktree), "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=False,
    ).stdout
    return sorted({p for p in tracked.splitlines() + others.splitlines() if p.strip()})


def preserve_outputs(worktree: Path, outputs_dir: Path, max_bytes: int = 65536) -> dict:
    """Copy the run's PRODUCED files (only the changed set, never the whole tree)
    into the durable bundle so the outcome grader can read the actual artifacts.
    Files over max_bytes are omitted-with-reason (the bundle is committed; a giant
    blob does not belong there). Writes an outputs-manifest.json and returns it."""
    manifest: dict = {"copied": [], "omitted": []}
    for rel in _changed_files(worktree):
        src = worktree / rel
        if not src.is_file():
            continue
        size = src.stat().st_size
        if size > max_bytes:
            manifest["omitted"].append({"path": rel, "reason": f"size {size} > {max_bytes}"})
            continue
        dst = outputs_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        manifest["copied"].append(rel)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    (outputs_dir / "outputs-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _write_transcript(tree_dir: Path, dest: Path, max_chars: int = 20000) -> None:
    """Render the assistant TEXT turns from the captured session tree into dest.
    Deliberately excludes tool_result contents (no tool-output secrets land in the
    committed bundle) — it is the judge's primary evidence of what the run PRESENTED,
    which for a skill like hitl lives in the assistant text, not the file outputs."""
    parts: list[str] = []
    for jsonl in sorted(Path(tree_dir).glob("*.jsonl")):
        for line in jsonl.read_text(encoding="utf-8", errors="replace").splitlines():
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
    metrics["output_lines"] = _git_added_lines(out_dir / "worktree")
    _write_transcript(Path(tree), out_dir / "transcript.txt")
    return metrics


def _cleanup_run(repo_root: Path, out_dir: Path) -> None:
    subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "remove", "--force", str(out_dir / "worktree")],
        capture_output=True, text=True, check=False,
    )
    shutil.rmtree(out_dir, ignore_errors=True)


def run_ab(repo_root: Path, config: dict, results_dir: Path, timeout_sec: int, keep_runs: bool) -> dict:
    runs = int(config.get("runs", 4))
    default_spec = config.get("spec_path")
    raw_runs: list[dict] = []
    agg_by_arm: dict = {}
    results_dir.mkdir(parents=True, exist_ok=True)
    for arm in config["arms"]:
        spec_path = repo_root / (arm.get("spec_path") or default_spec)
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        invocation = arm.get("invocation") or spec["prompt"]
        arm_runs: list[dict] = []
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
                    preserve_outputs(worktree, preserve / "outputs")
            except (subprocess.CalledProcessError, RuntimeError) as exc:
                # One flaky capture must not nuke a multi-run matrix or leak its
                # worktree; log, drop the data point, and let aggregate cope with n-1.
                print(f"  [skip] {arm['name']} run {index}: {exc}", file=sys.stderr)
            finally:
                if not keep_runs:
                    _cleanup_run(repo_root, out_dir)
        agg_by_arm[arm["name"]] = aggregate_metrics(arm_runs)
    report = build_report(config, agg_by_arm)
    (results_dir / "results.json").write_text(
        json.dumps({"config": config, "runs": raw_runs, "aggregate": agg_by_arm}, indent=2) + "\n",
        encoding="utf-8",
    )
    (results_dir / "report.md").write_text(report + "\n", encoding="utf-8")
    return {"aggregate": agg_by_arm, "report": report, "runs": raw_runs}


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
        outcome = run_ab(repo_root, config, results_dir.resolve(), args.timeout_sec, args.keep_runs)
        print(outcome["report"])
        print(f"\nresults: {results_dir}", file=sys.stderr)
        return 0
    parser.error("one of --selftest or --run is required")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
