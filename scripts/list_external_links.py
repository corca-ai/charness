#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".jsonc", ".toml"}
SKIP_DIR_NAMES = {".git", ".charness", "node_modules", ".pytest_cache", "charness-artifacts", "__pycache__"}
SKIP_FILE_NAMES = {"package-lock.json"}
SKIP_HOSTS = {"example.com", "example.org", "example.net"}
URL_PATTERN = re.compile(r"https?://[^\s<>'\"\\]+")
FENCED_CODE_BLOCK_PATTERN = re.compile(r"(^|\n)(```|~~~).*?(\n\2)(?=\n|$)", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args()


def list_candidate_files(repo_root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            candidates = []
            for line in result.stdout.splitlines():
                rel = line.strip()
                if not rel:
                    continue
                path = repo_root / rel
                if should_scan_path(path):
                    candidates.append(path)
            return sorted(candidates)
    except FileNotFoundError:
        pass

    candidates = []
    for path in repo_root.rglob("*"):
        if should_scan_path(path):
            candidates.append(path)
    return sorted(candidates)


def should_scan_path(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name in SKIP_FILE_NAMES:
        return False
    if path.suffix not in TEXT_SUFFIXES:
        return False
    return not any(part in SKIP_DIR_NAMES for part in path.parts)


def strip_markdown_code(text: str) -> str:
    without_fences = FENCED_CODE_BLOCK_PATTERN.sub("\n", text)
    return INLINE_CODE_PATTERN.sub("", without_fences)


def normalize_candidate(candidate: str) -> str | None:
    cleaned = candidate.rstrip(".,;:)]}>`'")
    parsed = urlsplit(cleaned)
    hostname = parsed.hostname
    if parsed.scheme not in {"http", "https"} or not hostname:
        return None
    if hostname in SKIP_HOSTS:
        return None
    if any(token in cleaned for token in ("${", "{", "}", "<", ">")):
        return None
    return cleaned


def extract_urls(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()

    if path.suffix == ".md":
        text = strip_markdown_code(text)

    urls = set()
    for match in URL_PATTERN.findall(text):
        normalized = normalize_candidate(match)
        if normalized is not None:
            urls.add(normalized)
    return urls


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    urls = set()
    for path in list_candidate_files(repo_root):
        urls.update(extract_urls(path))

    for url in sorted(urls):
        print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
