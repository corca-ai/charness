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
        f"- Eligible files: {manifest['eligible_count']}",
        f"- Changed eligible files: {len(manifest['changed_files'])}",
        f"- Selected: {len(manifest['sample'])}/{manifest['max_files']}",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path, default=Path("cosmic-ray.toml"))
    parser.add_argument("--manifest-json", type=Path, default=Path("reports/mutation/sample.json"))
    parser.add_argument("--manifest-md", type=Path, default=Path("reports/mutation/sample.md"))
    args = parser.parse_args()

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

    eligible = list_eligible(repo_root)
    if not eligible:
        sys.stderr.write(f"no eligible files matched {POOL_DIR}/{POOL_PATTERN}\n")
        return 1
    eligible_set = set(eligible)
    changed = [path for path in list_changed(repo_root, base_sha, head_sha) if path in eligible_set]

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
    manifest = {
        "seed": seed,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "max_files": max_files,
        "changed_quota": changed_quota,
        "eligible_count": len(eligible),
        "changed_files": changed,
        "changed_sample": changed_sample,
        "fill_sample": fill_sample,
        "sample": sample,
    }
    write_manifest(manifest, manifest_json, manifest_md)
    rewrite_cosmic_ray_targets(config_path, sample)

    sample_arg = " ".join(sample)
    append_github_output("sample_files", sample_arg)
    sys.stdout.write(f"sample ({len(sample)}/{max_files}): {sample_arg}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
