#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

DEFAULT_EXCLUDES = (
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
        completed = subprocess.run(
            ["tokei", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=TOKEI_VERSION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _run_tokei(repo_root: Path, excludes: list[str]) -> dict:
    cmd = ["tokei", "--output", "json"]
    for name in excludes:
        cmd.extend(["--exclude", name])
    cmd.append(str(repo_root))
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=TOKEI_SCAN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(
            cmd,
            124,
            str(exc.stdout or ""),
            f"timed out after {TOKEI_SCAN_TIMEOUT_SECONDS}s",
        )
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


def inventory_sloc(repo_root: Path, *, excludes: list[str]) -> dict:
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
    languages, totals = _summarize_languages(report)
    payload.update(
        status="ok",
        tokei_version=version,
        languages=languages,
        totals=totals,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Directory or path glob to exclude (repeatable). "
        "Defaults to common cache and vendor directories.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the JSON payload to this path in addition to stdout.",
    )
    args = parser.parse_args()

    excludes = list(args.exclude) if args.exclude else list(DEFAULT_EXCLUDES)
    payload = inventory_sloc(args.repo_root.resolve(), excludes=excludes)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json:
        print(rendered)
    else:
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
