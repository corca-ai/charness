#!/usr/bin/env python3
"""Author the machine-owned half of a prepared release claims review.

The release validator requires exact prepared-record bindings and a complete path
partition. Those are derived facts, not reviewer judgment. Keeping them out of this
scaffold forced operators to copy hashes and thousands of paths by hand at the most
expensive release boundary.
"""

from __future__ import annotations

import argparse
import json
import re
import runpy
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_claims = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_claims_review")
_evidence = SKILL_RUNTIME.load_local_skill_module(__file__, "claims_review_evidence")
_scope = SKILL_RUNTIME.load_local_skill_module(__file__, "claims_review_scope")
_schema = SKILL_RUNTIME.load_local_skill_module(__file__, "claims_review_schema")
_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_helpers = SKILL_RUNTIME.load_local_skill_module(__file__, "publish_release_helpers")
_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")

TARGET_RE = re.compile(r"^- target version: `([^`]+)`$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive the prepared-record bindings and full release-delta scope for a "
            "claims-review v4 record. Reviewer judgment remains explicit input."
        )
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--verdict", choices=_schema.VERDICTS, default="pass")
    parser.add_argument("--reviewer-context", required=True)
    parser.add_argument(
        "--observer-kind",
        choices=(*_schema.DISTINCTNESS_KINDS, "unproven"),
        required=True,
    )
    parser.add_argument("--observer-signal", required=True)
    parser.add_argument(
        "--review-artifact",
        help="New repo-relative Markdown narrative under charness-artifacts/release-review/.",
    )
    parser.add_argument("--preparer-context", required=True)
    parser.add_argument(
        "--advisory-finding",
        action="append",
        default=[],
        help="Single-line advisory finding; repeat for multiple findings.",
    )
    parser.add_argument("--output", help="Repo-relative JSON path; a versioned default is derived.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--write", action="store_true", help="Write the derived JSON record.")
    return parser.parse_args()


def _target_version(record: str) -> str:
    matches = TARGET_RE.findall(record)
    if len(matches) != 1:
        raise SystemExit(
            "claims-review scaffold: prepared release record must carry exactly one "
            "`- target version: `<version>` ` line"
        )
    return matches[0]


def _git_text(repo_root: Path, args: list[str], *, check: bool = True) -> str:
    result = _helpers.run(["git", *args], cwd=repo_root, check=False)
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise SystemExit(f"claims-review scaffold: {detail}")
    return result.stdout


def _new_narrative(repo_root: Path, value: str, *, prepared: dict[str, str], target: str) -> str:
    narrative = _evidence.review_relative_path(value, "--review-artifact", ".md")
    if (
        _helpers.run(
            ["git", "cat-file", "-e", f"{prepared['commit']}:{narrative}"],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    ):
        raise SystemExit(
            "claims-review scaffold: --review-artifact must be new at the prepared commit; "
            "reusing an earlier narrative is not distinct review evidence"
        )
    path = repo_root / narrative
    if not path.is_file():
        raise SystemExit(f"claims-review scaffold: review narrative does not exist: {narrative}")
    text = path.read_text(encoding="utf-8")
    if len(text.encode("utf-8")) < _evidence.MINIMUM_NARRATIVE_BYTES:
        raise SystemExit(
            f"claims-review scaffold: review narrative is under "
            f"{_evidence.MINIMUM_NARRATIVE_BYTES} bytes"
        )
    if prepared["commit"][:12] not in text or target not in text:
        raise SystemExit(
            "claims-review scaffold: review narrative must name prepared commit "
            f"{prepared['commit'][:12]} and target version {target}"
        )
    return narrative


def _release_scope(
    repo_root: Path, *, prepared_commit: str, target: str, remote: str
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    shallow = _helpers.run(
        ["git", "rev-parse", "--is-shallow-repository"], cwd=repo_root, check=False
    )
    if shallow.returncode != 0 or shallow.stdout.strip() == "true":
        raise SystemExit(
            "claims-review scaffold: a passing review requires complete history; "
            "the repository is shallow or history depth is unknown"
        )
    previous = _helpers.latest_previous_release_version(
        repo_root, target_version=target, remote=remote
    )
    if not previous:
        raise SystemExit(
            "claims-review scaffold: no previous release tag establishes the review base; "
            "record an unproven verdict instead of claiming complete scope"
        )
    base = f"refs/tags/v{previous}"
    ancestor = _helpers.run(
        ["git", "merge-base", "--is-ancestor", base, prepared_commit],
        cwd=repo_root,
        check=False,
    )
    if ancestor.returncode != 0:
        raise SystemExit(
            f"claims-review scaffold: release base {base} is not an ancestor of prepared HEAD"
        )
    delta = _git_text(
        repo_root,
        ["diff-tree", "--no-commit-id", "--name-only", "-r", f"{base}..{prepared_commit}"],
    )
    delta_paths = [line for line in delta.splitlines() if line]
    split = _scope.partition(delta_paths)
    if not split["blocking"]:
        raise SystemExit(
            "claims-review scaffold: derived release scope has no blocking path; refusing "
            "a pass record about nothing"
        )
    return {
        "blocking_paths": split["blocking"],
        "advisory_paths": split["advisory"],
    }, {
        "base_ref": base,
        "changed_paths_sha256": _scope.changed_paths_sha256(delta_paths),
        "changed_path_count": len(set(delta_paths)),
    }


def _allowed_dirty_paths(repo_root: Path, allowed: set[str]) -> None:
    status = _helpers.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repo_root,
    ).stdout.split("\0")
    observed: set[str] = set()
    index = 0
    while index < len(status):
        entry = status[index]
        index += 1
        if not entry:
            continue
        code, path = entry[:2], entry[3:]
        observed.add(path)
        if "R" in code or "C" in code:
            if index < len(status) and status[index]:
                observed.add(status[index])
                index += 1
    unexpected = sorted(observed - allowed)
    if unexpected:
        raise SystemExit(
            "claims-review scaffold: prepared stop has unrelated worktree changes; the "
            f"evidence child may contain only claims-review evidence: {unexpected}"
        )


def _prepared_facts(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    initial_allowed = {args.output} if args.output else set()
    if args.review_artifact:
        initial_allowed.add(args.review_artifact)
    _allowed_dirty_paths(repo_root, {path for path in initial_allowed if path})
    adapter = _adapter.load_adapter(repo_root)
    if not adapter.get("valid"):
        raise SystemExit(
            "claims-review scaffold: release adapter is invalid: "
            + "; ".join(adapter.get("errors") or ["unknown adapter error"])
        )
    record_path = _claims.release_record_path(adapter["data"])
    head = _git_text(repo_root, ["rev-parse", "HEAD"]).strip()
    prepared = _claims.prepared_record(
        repo_root, commit=head, record_path=record_path, run=_helpers.run
    )
    if prepared is None:
        raise SystemExit(
            "claims-review scaffold: HEAD is not the one-parent commit that introduced "
            "the prepared claims-review marker"
        )
    record_text = _git_text(repo_root, ["show", f"{head}:{record_path}"])
    target = _target_version(record_text)
    manifest_path = adapter["data"].get("packaging_manifest_path")
    if not isinstance(manifest_path, str) or not manifest_path:
        raise SystemExit("claims-review scaffold: release adapter has no packaging manifest path")
    try:
        manifest = json.loads(_git_text(repo_root, ["show", f"{head}:{manifest_path}"]))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "claims-review scaffold: prepared packaging manifest is not valid JSON"
        ) from exc
    manifest_target = manifest.get("version") if isinstance(manifest, dict) else None
    if manifest_target != target:
        raise SystemExit(
            "claims-review scaffold: prepared record target does not match prepared manifest: "
            f"record={target!r}, manifest={manifest_target!r}"
        )
    tag_state = _helpers.tag_exists(repo_root, f"v{target}", remote=args.remote)
    if tag_state["local"] or tag_state["remote"]:
        raise SystemExit(
            f"claims-review scaffold: target tag v{target} already exists locally or on {args.remote}"
        )
    output = args.output or (
        f"{_evidence.EVIDENCE_ROOT}{date.today().isoformat()}-v{target}-prepared-claims-review.json"
    )
    output = _evidence.review_relative_path(output, "--output", ".json")
    if (repo_root / output).exists():
        raise SystemExit(f"claims-review scaffold: output already exists: {output}")
    return {
        "repo_root": repo_root,
        "prepared": prepared,
        "head": head,
        "record_path": record_path,
        "target": target,
        "output": output,
    }


def _validate_operator_inputs(args: argparse.Namespace) -> None:
    _evidence.assert_signal_is_renderable(args.observer_signal)
    if not args.preparer_context.strip() or not args.reviewer_context.strip():
        raise SystemExit("claims-review scaffold: preparer and reviewer contexts must be nonempty")
    if args.preparer_context == args.reviewer_context:
        raise SystemExit("claims-review scaffold: preparer and reviewer contexts must be distinct")
    _scope._assert_findings_are_renderable(args.advisory_finding)


def build_record(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    facts = _prepared_facts(args)
    _validate_operator_inputs(args)
    repo_root = facts["repo_root"]
    prepared, head = facts["prepared"], facts["head"]
    record_path, target, output = facts["record_path"], facts["target"], facts["output"]

    if args.verdict == "pass":
        if args.observer_kind not in _schema.DISTINCTNESS_KINDS:
            raise SystemExit(
                "claims-review scaffold: verdict pass requires a distinct observer kind"
            )
        if not args.review_artifact:
            raise SystemExit("claims-review scaffold: verdict pass requires --review-artifact")
        narrative = _new_narrative(
            repo_root, args.review_artifact, prepared=prepared, target=target
        )
        scope, basis = _release_scope(
            repo_root, prepared_commit=head, target=target, remote=args.remote
        )
        allowed = {narrative, output}
    else:
        if args.observer_kind != "unproven":
            raise SystemExit(
                "claims-review scaffold: verdict unproven requires observer kind unproven"
            )
        if args.review_artifact:
            raise SystemExit(
                "claims-review scaffold: verdict unproven must not name a review artifact"
            )
        if args.advisory_finding:
            raise SystemExit(
                "claims-review scaffold: advisory findings belong to a scoped pass record"
            )
        narrative, scope, basis = None, None, None
        allowed = {output}
    _allowed_dirty_paths(repo_root, allowed)

    record: dict[str, Any] = {
        "schema_version": _schema.SCHEMA_VERSION,
        "prepared_commit": head,
        "release_record_path": record_path,
        "release_record_sha256": prepared["sha256"],
        "target_version": target,
        "tag_name": f"v{target}",
        "verdict": args.verdict,
        "preparer_context": args.preparer_context,
        "reviewer_context": args.reviewer_context,
        "observer_distinctness": {
            "kind": args.observer_kind,
            "signal": args.observer_signal,
            "review_artifact": narrative,
        },
    }
    if args.verdict == "pass":
        record["review_scope"] = scope
        record["scope_basis"] = basis
        record["advisory_findings"] = args.advisory_finding
    summary = {
        "status": "ready-to-write" if not args.write else "written",
        "output": output,
        "prepared_commit": head,
        "target_version": target,
        "tag_name": f"v{target}",
        "verdict": args.verdict,
        "scope_base": basis["base_ref"] if basis else None,
        "changed_paths_sha256": basis["changed_paths_sha256"] if basis else None,
        "blocking_path_count": len(scope["blocking_paths"]) if scope else 0,
        "advisory_path_count": len(scope["advisory_paths"]) if scope else 0,
        "review_artifact": narrative,
    }
    return record, summary


def main() -> None:
    args = parse_args()
    record, summary = build_record(args)
    if args.write:
        output = args.repo_root.resolve() / summary["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
        print(_yaml.render_yaml(summary), end="")
    else:
        print(_yaml.render_yaml(record), end="")


if __name__ == "__main__":
    main()
