#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_OUTPUT_DIR = Path("charness-artifacts/cautilus/chatbot-benchmark")


class EvalError(Exception):
    pass


def _run_proposal_summary(target_repo: Path, output_dir: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "python3",
            "scripts/eval_cautilus_chatbot_proposals.py",
            "--repo-root",
            str(target_repo),
            "--output-dir",
            str(output_dir),
            "--json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvalError(
            f"proposal summary failed for `{target_repo}`: {result.stderr.strip() or result.stdout.strip() or 'no output'}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvalError(f"proposal summary did not emit valid JSON for `{target_repo}`") from exc
    if not isinstance(payload, dict):
        raise EvalError(f"proposal summary output must be a JSON object for `{target_repo}`")
    return payload


def _git_head(repo: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise EvalError(f"proposal summary is missing string-list `{key}`")
    return list(value)


def _sorted_delta(left: list[str], right: list[str]) -> list[str]:
    return sorted(set(left) - set(right))


def build_summary(
    *,
    baseline_repo: Path,
    candidate_repo: Path,
    baseline_summary: dict[str, object],
    candidate_summary: dict[str, object],
) -> dict[str, object]:
    baseline_candidate_keys = _string_list(baseline_summary, "candidate_keys")
    candidate_candidate_keys = _string_list(candidate_summary, "candidate_keys")
    baseline_proposal_keys = _string_list(baseline_summary, "proposal_keys")
    candidate_proposal_keys = _string_list(candidate_summary, "proposal_keys")
    baseline_omitted = _string_list(baseline_summary, "omitted_candidate_keys")
    candidate_omitted = _string_list(candidate_summary, "omitted_candidate_keys")

    return {
        "schema_version": 1,
        "repo": REPO_ROOT.name,
        "baseline_repo": str(baseline_repo),
        "candidate_repo": str(candidate_repo),
        "baseline_commit": _git_head(baseline_repo),
        "candidate_commit": _git_head(candidate_repo),
        "baseline": {
            "candidate_count": baseline_summary.get("candidate_count"),
            "proposal_count": baseline_summary.get("proposal_count"),
            "candidate_keys": baseline_candidate_keys,
            "proposal_keys": baseline_proposal_keys,
            "omitted_candidate_keys": baseline_omitted,
        },
        "candidate": {
            "candidate_count": candidate_summary.get("candidate_count"),
            "proposal_count": candidate_summary.get("proposal_count"),
            "candidate_keys": candidate_candidate_keys,
            "proposal_keys": candidate_proposal_keys,
            "omitted_candidate_keys": candidate_omitted,
        },
        "diff": {
            "added_candidate_keys": _sorted_delta(candidate_candidate_keys, baseline_candidate_keys),
            "removed_candidate_keys": _sorted_delta(baseline_candidate_keys, candidate_candidate_keys),
            "added_proposal_keys": _sorted_delta(candidate_proposal_keys, baseline_proposal_keys),
            "removed_proposal_keys": _sorted_delta(baseline_proposal_keys, candidate_proposal_keys),
            "newly_omitted_candidate_keys": _sorted_delta(candidate_omitted, baseline_omitted),
            "resolved_omitted_candidate_keys": _sorted_delta(baseline_omitted, candidate_omitted),
        },
    }


def write_summary(output_dir: Path, summary: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    diff = summary["diff"]
    assert isinstance(diff, dict)
    lines = [
        "# Cautilus Chatbot Benchmark",
        "",
        f"- baseline commit: `{summary['baseline_commit'] or 'unknown'}`",
        f"- candidate commit: `{summary['candidate_commit'] or 'unknown'}`",
        f"- baseline repo: `{summary['baseline_repo']}`",
        f"- candidate repo: `{summary['candidate_repo']}`",
        "",
        "## Candidate Delta",
        "",
    ]
    for key in ("added_candidate_keys", "removed_candidate_keys"):
        values = diff[key]
        assert isinstance(values, list)
        lines.append(f"- `{key}`: {', '.join(f'`{value}`' for value in values) if values else 'none'}")
    lines.extend(["", "## Proposal Delta", ""])
    for key in ("added_proposal_keys", "removed_proposal_keys"):
        values = diff[key]
        assert isinstance(values, list)
        lines.append(f"- `{key}`: {', '.join(f'`{value}`' for value in values) if values else 'none'}")
    lines.extend(["", "## Omitted Delta", ""])
    for key in ("newly_omitted_candidate_keys", "resolved_omitted_candidate_keys"):
        values = diff[key]
        assert isinstance(values, list)
        lines.append(f"- `{key}`: {', '.join(f'`{value}`' for value in values) if values else 'none'}")
    (output_dir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_repo_pair(
    *,
    repo_root: Path,
    baseline_repo: Path | None,
    candidate_repo: Path | None,
    baseline_ref: str | None,
) -> tuple[Path, Path]:
    if baseline_repo is not None and candidate_repo is not None:
        return baseline_repo.resolve(), candidate_repo.resolve()
    if baseline_repo is not None or candidate_repo is not None:
        raise EvalError("pass both `--baseline-repo` and `--candidate-repo`, or neither")
    if baseline_ref is None:
        raise EvalError("pass `--baseline-ref` or both compare worktree paths")

    workspace_root = Path(tempfile.mkdtemp(prefix="cautilus-chatbot-compare-"))
    result = subprocess.run(
        [
            "cautilus",
            "workspace",
            "prepare-compare",
            "--repo-root",
            str(repo_root),
            "--baseline-ref",
            baseline_ref,
            "--output-dir",
            str(workspace_root),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvalError(
            "workspace prepare-compare failed: "
            f"{result.stderr.strip() or result.stdout.strip() or 'no output'}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvalError("workspace prepare-compare did not emit valid JSON") from exc
    baseline_payload = payload.get("baseline")
    candidate_payload = payload.get("candidate")
    if not isinstance(baseline_payload, dict) or not isinstance(candidate_payload, dict):
        raise EvalError("workspace prepare-compare output is missing baseline/candidate payloads")
    baseline_path = baseline_payload.get("path")
    candidate_path = candidate_payload.get("path")
    if not isinstance(baseline_path, str) or not isinstance(candidate_path, str):
        raise EvalError("workspace prepare-compare output is missing compare paths")
    return Path(baseline_path).resolve(), Path(candidate_path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--baseline-repo", type=Path)
    parser.add_argument("--candidate-repo", type=Path)
    parser.add_argument("--baseline-ref")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir = (repo_root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir.resolve()
    baseline_repo, candidate_repo = resolve_repo_pair(
        repo_root=repo_root,
        baseline_repo=args.baseline_repo,
        candidate_repo=args.candidate_repo,
        baseline_ref=args.baseline_ref,
    )
    with tempfile.TemporaryDirectory(prefix="cautilus-chatbot-benchmark-baseline-") as baseline_tmp, tempfile.TemporaryDirectory(
        prefix="cautilus-chatbot-benchmark-candidate-"
    ) as candidate_tmp:
        baseline_summary = _run_proposal_summary(baseline_repo, Path(baseline_tmp))
        candidate_summary = _run_proposal_summary(candidate_repo, Path(candidate_tmp))
    summary = build_summary(
        baseline_repo=baseline_repo,
        candidate_repo=candidate_repo,
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
    )
    write_summary(output_dir, summary)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Wrote cautilus chatbot benchmark to {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvalError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
