#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_INPUT_PATH = Path("evals/cautilus/chatbot-scenario-proposal-inputs.json")
DEFAULT_OUTPUT_DIR = Path("charness-artifacts/cautilus/chatbot-proposals")


class EvalError(Exception):
    pass


def load_input_packet(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise EvalError(f"missing `{path}`")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvalError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise EvalError(f"{path}: top-level JSON value must be an object")
    if data.get("schemaVersion") != "cautilus.scenario_proposal_inputs.v1":
        raise EvalError(f"{path}: schemaVersion must be `cautilus.scenario_proposal_inputs.v1`")
    candidates = data.get("proposalCandidates")
    if not isinstance(candidates, list) or not candidates:
        raise EvalError(f"{path}: `proposalCandidates` must be a non-empty list")
    return data


def run_scenario_propose(repo_root: Path, input_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["cautilus", "scenario", "propose", "--input", str(input_path)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def load_proposals(result: subprocess.CompletedProcess[str], input_path: Path) -> dict[str, object]:
    if result.returncode != 0:
        raise EvalError(
            "cautilus scenario propose failed for "
            f"`{input_path}`: {result.stderr.strip() or result.stdout.strip() or 'no output'}"
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvalError("cautilus scenario propose did not emit valid JSON") from exc
    if not isinstance(data, dict):
        raise EvalError("cautilus scenario propose output must be a JSON object")
    if data.get("schemaVersion") != "cautilus.scenario_proposals.v1":
        raise EvalError("cautilus scenario propose output must use `cautilus.scenario_proposals.v1`")
    proposals = data.get("proposals")
    if not isinstance(proposals, list):
        raise EvalError("cautilus scenario propose output must include list `proposals`")
    return data


def build_summary(
    *,
    repo_root: Path,
    input_path: Path,
    input_packet: dict[str, object],
    proposals_packet: dict[str, object],
    command: subprocess.CompletedProcess[str],
) -> dict[str, object]:
    candidate_keys = [
        candidate.get("proposalKey")
        for candidate in input_packet.get("proposalCandidates", [])
        if isinstance(candidate, dict) and isinstance(candidate.get("proposalKey"), str)
    ]
    proposals = proposals_packet.get("proposals", [])
    assert isinstance(proposals, list)
    proposal_keys = [
        proposal.get("proposalKey")
        for proposal in proposals
        if isinstance(proposal, dict) and isinstance(proposal.get("proposalKey"), str)
    ]
    omitted_candidate_keys = [proposal_key for proposal_key in candidate_keys if proposal_key not in proposal_keys]
    tag_counts: dict[str, int] = {}
    for candidate in input_packet.get("proposalCandidates", []):
        if not isinstance(candidate, dict):
            continue
        tags = candidate.get("tags")
        if not isinstance(tags, list):
            continue
        for tag in tags:
            if isinstance(tag, str) and tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return {
        "schema_version": 1,
        "repo": repo_root.name,
        "input_file": str(input_path.relative_to(repo_root)),
        "candidate_count": len(input_packet["proposalCandidates"]),
        "candidate_keys": candidate_keys,
        "proposal_count": len(proposals),
        "proposal_keys": proposal_keys,
        "omitted_candidate_keys": omitted_candidate_keys,
        "families": proposals_packet.get("families", []),
        "tag_counts": tag_counts,
        "command": {
            "argv": ["cautilus", "scenario", "propose", "--input", str(input_path.relative_to(repo_root))],
            "exit_code": command.returncode,
            "stderr": command.stderr.strip(),
        },
        "proposals_packet": proposals_packet,
    }


def write_summary(output_dir: Path, summary: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tag_counts = summary["tag_counts"]
    assert isinstance(tag_counts, dict)
    lines = [
        "# Cautilus Chatbot Proposals",
        "",
        f"- input: `{summary['input_file']}`",
        f"- candidates: `{summary['candidate_count']}`",
        f"- emitted proposals: `{summary['proposal_count']}`",
        "",
        "## Candidate Keys",
        "",
    ]
    candidate_keys = summary["candidate_keys"]
    assert isinstance(candidate_keys, list)
    for candidate_key in candidate_keys:
        lines.append(f"- `{candidate_key}`")
    if not candidate_keys:
        lines.append("- none")
    lines.extend([
        "",
        "## Proposal Keys",
        "",
    ])
    proposal_keys = summary["proposal_keys"]
    assert isinstance(proposal_keys, list)
    for proposal_key in proposal_keys:
        lines.append(f"- `{proposal_key}`")
    if not proposal_keys:
        lines.append("- none")
    lines.extend(["", "## Omitted Candidate Keys", ""])
    omitted_candidate_keys = summary["omitted_candidate_keys"]
    assert isinstance(omitted_candidate_keys, list)
    for omitted_key in omitted_candidate_keys:
        lines.append(f"- `{omitted_key}`")
    if not omitted_candidate_keys:
        lines.append("- none")
    lines.extend(["", "## Tag Coverage", ""])
    for tag, count in sorted(tag_counts.items()):
        lines.append(f"- `{tag}`: `{count}`")
    if not tag_counts:
        lines.append("- none")
    lines.extend(["", "## Command", "", "```text"])
    argv = summary["command"]["argv"]
    assert isinstance(argv, list)
    lines.append(" ".join(argv))
    command_stderr = summary["command"]["stderr"]
    assert isinstance(command_stderr, str)
    if command_stderr:
        lines.extend(["", command_stderr])
    lines.extend(["```", ""])
    (output_dir / "latest.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--input-file", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    input_path = (repo_root / args.input_file).resolve() if not args.input_file.is_absolute() else args.input_file.resolve()
    output_dir = (repo_root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir.resolve()

    input_packet = load_input_packet(input_path)
    result = run_scenario_propose(repo_root, input_path)
    proposals_packet = load_proposals(result, input_path)
    summary = build_summary(
        repo_root=repo_root,
        input_path=input_path,
        input_packet=input_packet,
        proposals_packet=proposals_packet,
        command=result,
    )
    write_summary(output_dir, summary)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Wrote cautilus chatbot proposals to {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvalError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
