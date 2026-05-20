#!/usr/bin/env python3
"""Pick a deterministic stratified sample of Cosmic Ray mutation targets.

The sample rewrites `cosmic-ray.toml`'s `module-path` list so the following
Cosmic Ray init/exec run mutates only the selected files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POOL_DIR = "scripts"
POOL_PATTERN = "*.py"
EXCLUDED_NAMES = {"__init__.py"}
DEFAULT_MAX_FILES = 10
DEFAULT_CHANGED_QUOTA = 5
DEFAULT_COVERAGE_JSON = Path("reports/mutation/test-coverage.json")


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def deterministic_sample(files: list[str], count: int, seed: str) -> list[str]:
    if count <= 0 or not files:
        return []
    return sorted(files, key=lambda path: stable_hash(f"{seed}:{path}"))[:count]


def list_eligible(repo_root: Path) -> list[str]:
    return sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / POOL_DIR).glob(POOL_PATTERN)
        if path.name not in EXCLUDED_NAMES
    )


def read_test_command(config_path: Path) -> str:
    text = config_path.read_text(encoding="utf-8")
    match = re.search(r"^test-command\s*=\s*([\"'])(.*?)\1\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit(f"could not find cosmic-ray test-command in {config_path}")
    return match.group(2)


def coverage_run_command(test_command: str, data_file: Path) -> list[str]:
    parts = shlex.split(test_command)
    if len(parts) >= 3 and parts[0] in {"python", "python3"} and parts[1:3] == ["-m", "pytest"]:
        return [
            parts[0],
            "-m",
            "coverage",
            "run",
            "--data-file",
            str(data_file),
            "-m",
            "pytest",
            *parts[3:],
        ]
    if parts and parts[0] == "pytest":
        return [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--data-file",
            str(data_file),
            "-m",
            "pytest",
            *parts[1:],
        ]
    raise SystemExit(
        "mutation coverage sampling supports pytest commands shaped as "
        "`python3 -m pytest ...` or `pytest ...`; use a helper script for other runners"
    )


def run_test_coverage(repo_root: Path, test_command: str, coverage_json: Path) -> None:
    coverage_json.parent.mkdir(parents=True, exist_ok=True)
    data_file = coverage_json.with_name(".mutation-coverage")
    if data_file.exists():
        data_file.unlink()
    command = coverage_run_command(test_command, data_file)
    subprocess.run(command, cwd=repo_root, check=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "coverage",
            "json",
            "--data-file",
            str(data_file),
            "-o",
            str(coverage_json),
        ],
        cwd=repo_root,
        check=True,
    )


def load_covered_lines(repo_root: Path, coverage_json: Path) -> dict[str, set[int]]:
    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    files = data.get("files") or {}
    covered: dict[str, set[int]] = {}
    for raw_path, payload in files.items():
        path = Path(raw_path)
        if path.is_absolute():
            try:
                rel = path.resolve().relative_to(repo_root).as_posix()
            except ValueError:
                continue
        else:
            rel = path.as_posix()
        lines = payload.get("executed_lines") or []
        covered[rel] = {int(line) for line in lines}
    return covered


def filter_eligible_by_coverage(eligible: list[str], covered_lines: dict[str, set[int]]) -> list[str]:
    return [path for path in eligible if covered_lines.get(path)]


def display_path(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def list_changed(repo_root: Path, base_sha: str, head_sha: str) -> list[str]:
    if not base_sha:
        return []
    head = head_sha or "HEAD"
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_sha}..{head}", "--", POOL_DIR],
            cwd=repo_root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"git diff {base_sha}..{head} failed: {exc.stderr}\n")
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def positive_int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SystemExit(f"expected non-negative integer, got: {value!r}") from exc
    if parsed < 0:
        raise SystemExit(f"expected non-negative integer, got: {value!r}")
    return parsed


def rewrite_cosmic_ray_targets(config_path: Path, paths: list[str]) -> None:
    text = config_path.read_text(encoding="utf-8")
    block = "module-path = [\n" + "".join(f'    "{path}",\n' for path in paths) + "]"
    pattern = re.compile(r"^module-path\s*=\s*\[.*?\]", re.MULTILINE | re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"could not find cosmic-ray module-path list in {config_path}")
    config_path.write_text(pattern.sub(block, text, count=1), encoding="utf-8")


def write_manifest(manifest: dict, manifest_json: Path, manifest_md: Path) -> None:
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        "# Mutation Sample",
        "",
        f"- Base SHA: `{manifest['base_sha'] or '(none)'}`",
        f"- Head SHA: `{manifest['head_sha'] or '(unknown)'}`",
        f"- Seed: `{manifest['seed']}`",
        f"- Mutation pool files: {manifest.get('all_eligible_count', manifest['eligible_count'])}",
        f"- Eligible files after coverage filter: {manifest['eligible_count']}",
        f"- Covered eligible files: {manifest.get('covered_eligible_count', 'n/a')}",
        f"- Changed pool files: {len(manifest.get('changed_files_before_coverage', manifest['changed_files']))}",
        f"- Changed eligible files after coverage filter: {len(manifest['changed_files'])}",
        f"- Changed files excluded by coverage filter: {len(manifest.get('uncovered_changed_files', []))}",
        f"- Selected: {len(manifest['sample'])}/{manifest['max_files']}",
        f"- Test command: `{manifest.get('test_command') or '(not recorded)'}`",
        "",
        "## Changed sample",
        "",
        *([f"- `{path}`" for path in manifest["changed_sample"]] or ["(none)"]),
        "",
        "## Fill sample",
        "",
        *([f"- `{path}`" for path in manifest["fill_sample"]] or ["(none)"]),
        "",
    ]
    manifest_md.parent.mkdir(parents=True, exist_ok=True)
    manifest_md.write_text("\n".join(md_lines), encoding="utf-8")


def append_github_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"{name}={value}\n")


def build_manifest(
    *,
    seed: str,
    base_sha: str,
    head_sha: str,
    max_files: int,
    changed_quota: int,
    eligible: list[str],
    all_eligible: list[str],
    coverage_enabled: bool,
    coverage_json: Path,
    repo_root: Path,
    test_command: str,
    changed_before_coverage: list[str],
    uncovered_changed_files: list[str],
    changed: list[str],
    changed_sample: list[str],
    fill_sample: list[str],
    sample: list[str],
) -> dict:
    return {
        "seed": seed,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "max_files": max_files,
        "changed_quota": changed_quota,
        "eligible_count": len(eligible),
        "all_eligible_count": len(all_eligible),
        "coverage_enabled": coverage_enabled,
        "coverage_json": display_path(repo_root, coverage_json),
        "test_command": test_command,
        "covered_eligible_count": len(eligible) if coverage_enabled else None,
        "uncovered_eligible_count": len(all_eligible) - len(eligible) if coverage_enabled else None,
        "changed_files_before_coverage": changed_before_coverage,
        "uncovered_changed_files": uncovered_changed_files,
        "changed_files": changed,
        "changed_sample": changed_sample,
        "fill_sample": fill_sample,
        "sample": sample,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path, default=Path("cosmic-ray.toml"))
    parser.add_argument("--manifest-json", type=Path, default=Path("reports/mutation/sample.json"))
    parser.add_argument("--manifest-md", type=Path, default=Path("reports/mutation/sample.md"))
    parser.add_argument("--coverage-json", type=Path, default=DEFAULT_COVERAGE_JSON)
    parser.add_argument(
        "--skip-coverage",
        action="store_true",
        help="Skip test-command coverage collection. Intended for narrow unit tests only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = args.repo_root.resolve()
    config_path = args.config if args.config.is_absolute() else repo_root / args.config
    max_files = positive_int(os.environ.get("MUTATION_SAMPLE_MAX_FILES"), DEFAULT_MAX_FILES)
    changed_quota = min(
        positive_int(os.environ.get("MUTATION_SAMPLE_CHANGED_QUOTA"), DEFAULT_CHANGED_QUOTA),
        max_files,
    )
    base_sha = (os.environ.get("MUTATION_BASE_SHA") or "").strip()
    head_sha = (os.environ.get("MUTATION_HEAD_SHA") or "").strip()
    seed = (os.environ.get("MUTATION_SAMPLE_SEED") or "").strip() or str(int(time.time()))

    coverage_json = args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    test_command = read_test_command(config_path)
    coverage_enabled = (
        not args.skip_coverage and (os.environ.get("MUTATION_SAMPLE_COVERAGE") or "1") != "0"
    )

    all_eligible = list_eligible(repo_root)
    covered_lines: dict[str, set[int]] = {}
    if coverage_enabled:
        try:
            run_test_coverage(repo_root, test_command, coverage_json)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                f"test-command coverage probe failed with exit {exc.returncode}: {test_command}"
            ) from exc
        covered_lines = load_covered_lines(repo_root, coverage_json)
        eligible = filter_eligible_by_coverage(all_eligible, covered_lines)
    else:
        eligible = all_eligible

    if not eligible:
        if coverage_enabled:
            sys.stderr.write(
                f"no eligible files matched {POOL_DIR}/{POOL_PATTERN} with coverage from {test_command!r}\n"
            )
        else:
            sys.stderr.write(f"no eligible files matched {POOL_DIR}/{POOL_PATTERN}\n")
        return 1
    all_eligible_set = set(all_eligible)
    eligible_set = set(eligible)
    changed_before_coverage = [
        path for path in list_changed(repo_root, base_sha, head_sha) if path in all_eligible_set
    ]
    changed = [path for path in changed_before_coverage if path in eligible_set]
    uncovered_changed_files = [
        path for path in changed_before_coverage if coverage_enabled and path not in eligible_set
    ]

    changed_sample = deterministic_sample(changed, changed_quota, f"{seed}:changed")
    selected = set(changed_sample)
    fill_pool = [path for path in eligible if path not in selected]
    fill_sample = deterministic_sample(fill_pool, max_files - len(changed_sample), f"{seed}:fill")
    sample = changed_sample + fill_sample
    if not sample:
        sys.stderr.write("no mutation sample files were selected\n")
        return 1

    manifest_json = (
        args.manifest_json if args.manifest_json.is_absolute() else repo_root / args.manifest_json
    )
    manifest_md = args.manifest_md if args.manifest_md.is_absolute() else repo_root / args.manifest_md
    manifest = build_manifest(
        seed=seed,
        base_sha=base_sha,
        head_sha=head_sha,
        max_files=max_files,
        changed_quota=changed_quota,
        eligible=eligible,
        all_eligible=all_eligible,
        coverage_enabled=coverage_enabled,
        coverage_json=coverage_json,
        repo_root=repo_root,
        test_command=test_command,
        changed_before_coverage=changed_before_coverage,
        uncovered_changed_files=uncovered_changed_files,
        changed=changed,
        changed_sample=changed_sample,
        fill_sample=fill_sample,
        sample=sample,
    )
    write_manifest(manifest, manifest_json, manifest_md)
    rewrite_cosmic_ray_targets(config_path, sample)

    sample_arg = " ".join(sample)
    append_github_output("sample_files", sample_arg)
    sys.stdout.write(f"sample ({len(sample)}/{max_files}): {sample_arg}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
