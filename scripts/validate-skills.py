#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER_KEYS = ("name", "description")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ValidationError(Exception):
    pass


def extract_frontmatter(contents: str) -> list[str]:
    lines = contents.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValidationError("missing YAML frontmatter delimited by ---")

    frontmatter: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            if not frontmatter:
                raise ValidationError("frontmatter is empty")
            return frontmatter
        frontmatter.append(line)
    raise ValidationError("frontmatter is missing closing --- delimiter")


def parse_frontmatter(path: Path) -> dict[str, str]:
    contents = path.read_text(encoding="utf-8")
    lines = extract_frontmatter(contents)
    data: dict[str, str] = {}
    for index, raw in enumerate(lines, start=2):
        if not raw.strip():
            continue
        if ":" not in raw:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: missing ':'")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty key")
        if not value:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty value")
        data[key] = value
    for key in REQUIRED_FRONTMATTER_KEYS:
        if key not in data:
            raise ValidationError(f"missing field `{key}`")
    return data


def validate_quoted_string(field: str, value: str) -> None:
    if len(value) < 2 or not (value.startswith('"') and value.endswith('"')):
        raise ValidationError(
            f"`{field}` must be double-quoted so standard YAML parsers accept punctuation safely"
        )


def validate_frontmatter(path: Path) -> None:
    data = parse_frontmatter(path)
    name = data["name"]
    if not SKILL_NAME_RE.fullmatch(name):
        raise ValidationError("`name` must be a lowercase slug")
    if name != path.parent.name:
        raise ValidationError(f"`name` must match directory name `{path.parent.name}`")

    validate_quoted_string("description", data["description"])


def validate_support_files(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    contents = skill_md.read_text(encoding="utf-8")

    for rel in re.findall(r"`((?:references|scripts)/[^`]+)`", contents):
        if not (skill_dir / rel).exists():
            raise ValidationError(f"referenced path `{rel}` does not exist")

    has_adapter_example = (skill_dir / "adapter.example.yaml").exists()
    has_scripts_dir = (skill_dir / "scripts").exists()
    if has_adapter_example and not has_scripts_dir:
        raise ValidationError("adapter.example.yaml exists but scripts/ is missing")
    if has_scripts_dir:
        for required in ("resolve_adapter.py", "init_adapter.py"):
            if not (skill_dir / "scripts" / required).exists():
                raise ValidationError(f"scripts/{required} is missing")


def iter_skill_dirs(root: Path) -> list[Path]:
    public_skills_dir = root / "skills" / "public"
    return sorted(path for path in public_skills_dir.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    skill_dirs = iter_skill_dirs(root)
    if not skill_dirs:
        print("No public skills found.")
        return 0

    validated = 0
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            raise ValidationError(f"{skill_dir}: missing SKILL.md")
        try:
            validate_frontmatter(skill_md)
            validate_support_files(skill_dir)
        except ValidationError as exc:
            raise ValidationError(f"{skill_md}: {exc}") from exc
        validated += 1

    print(f"Validated {validated} public skill packages.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
