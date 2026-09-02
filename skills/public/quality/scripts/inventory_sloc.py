#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

try:
    from scripts.core import subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    import scripts.core.subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process

subprocess = _subprocess_guard.subprocess

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import add_output_args, emit_selected  # noqa: E402

DEFAULT_EXCLUDES = (
    ".charness",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
    "target",
    "vendor",
)
TOKEI_VERSION_TIMEOUT_SECONDS = 10
TOKEI_SCAN_TIMEOUT_SECONDS = 120


def _tokei_version() -> str | None:
    if shutil.which("tokei") is None:
        return None
    try:
        completed = run_process(
            ["tokei", "--version"], cwd=Path.cwd(), timeout_seconds=TOKEI_VERSION_TIMEOUT_SECONDS
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _run_tokei(repo_root: Path, excludes: list[str]) -> dict:
    cmd = ["tokei", "--output", "json"]
    for name in excludes:
        cmd.extend(["--exclude", name])
    cmd.append(str(repo_root))
    completed = run_process(cmd, cwd=repo_root, timeout_seconds=TOKEI_SCAN_TIMEOUT_SECONDS)
    if completed.returncode != 0:
        raise RuntimeError(
            f"tokei exited with status {completed.returncode}: {completed.stderr.strip()}"
        )
    return json.loads(completed.stdout)


def _summarize_languages(report: dict) -> tuple[dict, dict]:
    languages: dict[str, dict[str, int]] = {}
    totals = {"code": 0, "comments": 0, "blanks": 0, "files": 0}
    for name, payload in report.items():
        if name == "Total" or not isinstance(payload, dict):
            continue
        code = int(payload.get("code", 0))
        comments = int(payload.get("comments", 0))
        blanks = int(payload.get("blanks", 0))
        files = len(payload.get("reports", []) or [])
        if code == 0 and comments == 0 and blanks == 0 and files == 0:
            continue
        languages[name] = {
            "code": code,
            "comments": comments,
            "blanks": blanks,
            "files": files,
        }
        totals["code"] += code
        totals["comments"] += comments
        totals["blanks"] += blanks
        totals["files"] += files
    return languages, totals


def _remove_output_report(report: dict, output: Path | None) -> None:
    if output is None:
        return
    target = str(output.resolve())
    for language, language_report in report.items():
        if language == "Total" or not isinstance(language_report, dict):
            continue
        reports = language_report.get("reports")
        reports = reports if isinstance(reports, list) else []
        retained = [item for item in reports if item.get("name") != target]
        if len(retained) == len(reports):
            continue
        language_report["reports"] = retained
        for field in ("code", "comments", "blanks"):
            language_report[field] = sum(
                int(item.get("stats", {}).get(field, 0)) for item in retained
            )


def inventory_sloc(repo_root: Path, *, excludes: list[str], output: Path | None = None) -> dict:
    payload: dict = {
        "schema_version": 1,
        "scope": "tokei-sloc",
        "engine": "tokei",
        "repo_root": str(repo_root),
        "exclude": sorted(excludes),
        "advisory_notes": [
            "SLOC inventory is advisory; promote a hard gate only after the repo "
            "has tuned excludes and confirmed the signal is low-noise.",
        ],
    }
    version = _tokei_version()
    if version is None:
        payload.update(
            status="degraded",
            reason="tokei binary not on PATH",
            install_hint=(
                "See integrations/tools/tokei.json or "
                "https://github.com/XAMPPRocky/tokei#installation"
            ),
            tokei_version=None,
            languages={},
            totals={"code": 0, "comments": 0, "blanks": 0, "files": 0},
        )
        return payload
    try:
        report = _run_tokei(repo_root, excludes)
    except RuntimeError as exc:
        payload.update(
            status="degraded",
            reason=str(exc),
            tokei_version=version,
            languages={},
            totals={"code": 0, "comments": 0, "blanks": 0, "files": 0},
        )
        return payload
    _remove_output_report(report, output)
    languages, totals = _summarize_languages(report)
    payload.update(
        status="ok",
        tokei_version=version,
        languages=languages,
        totals=totals,
    )
    return payload


def _in_repo_output(repo_root: Path, output: Path | None) -> Path | None:
    if output is not None:
        resolved = output.resolve()
        if resolved.is_relative_to(repo_root):
            return resolved
    return None


def summarize(payload: dict) -> dict:
    return {
        "summary_note": "summary is triage output; use --detail for per-language SLOC records",
        "schema_version": payload["schema_version"],
        "scope": payload["scope"],
        "engine": payload["engine"],
        "repo_root": payload["repo_root"],
        "status": payload["status"],
        "reason": payload.get("reason"),
        "tokei_version": payload.get("tokei_version"),
        "totals": payload["totals"],
        "language_count": len(payload.get("languages", {})),
        "advisory_notes": payload["advisory_notes"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root for the tokei-backed SLOC inventory",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Directory or path glob to exclude (repeatable). "
        "Defaults to common cache and vendor directories.",
    )
    add_output_args(
        parser,
        summary_help="Emit compact YAML SLOC totals for triage",
        detail_help="Emit the full per-language SLOC inventory as YAML",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the JSON payload to this path in addition to stdout.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    excludes = list(args.exclude) if args.exclude else list(DEFAULT_EXCLUDES)
    payload = inventory_sloc(
        repo_root,
        excludes=excludes,
        output=_in_repo_output(repo_root, args.output),
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if not emit_selected(payload, args, summarize=summarize):
        if payload["status"] == "degraded":
            print(f"SLOC inventory: degraded ({payload['reason']})")
        else:
            totals = payload["totals"]
            print(
                f"SLOC inventory: {totals['code']} code / {totals['comments']} comments / "
                f"{totals['blanks']} blanks across {totals['files']} files "
                f"({len(payload['languages'])} languages, {payload['tokei_version']})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
