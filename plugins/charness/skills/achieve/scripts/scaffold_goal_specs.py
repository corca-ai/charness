#!/usr/bin/env python3
"""Create concise goal-linked phase specs without expanding the goal body."""

from __future__ import annotations

import argparse
import json
import re
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")
goal_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_cli_args")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")

_H2 = re.compile(r"^## (.+?)[ \t]*$", re.MULTILINE)
_REQUIRED = ("slug", "title", "objective", "completion", "verification", "non_claims")


def _load_specs(path: Path) -> list[dict[str, object]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"--specs-file unreadable or invalid: {exc}") from exc
    phases = raw.get("phases") if isinstance(raw, dict) else None
    if not isinstance(phases, list) or not phases:
        raise SystemExit("--specs-file must contain a non-empty `phases` list")
    normalized: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, phase in enumerate(phases, start=1):
        if not isinstance(phase, dict):
            raise SystemExit(f"phase {index} must be an object")
        missing = [key for key in _REQUIRED if not str(phase.get(key, "")).strip()]
        if missing:
            raise SystemExit(f"phase {index} missing required fields: {', '.join(missing)}")
        slug = goal_lib.slugify(str(phase["slug"]))
        if slug in seen or slug == "goal":
            raise SystemExit(f"phase {index} has duplicate or unusable slug: {phase['slug']!r}")
        seen.add(slug)
        item = dict(phase)
        item["slug"] = slug
        for key in ("scope_in", "scope_out", "dependencies", "completion", "verification", "non_claims"):
            value = item.get(key, [])
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, list) or not all(isinstance(entry, str) and entry.strip() for entry in value):
                raise SystemExit(f"phase {index} field `{key}` must be a non-empty string or list of strings")
            item[key] = value
        normalized.append(item)
    return normalized


def _bullet_lines(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def _render_spec(repo_root: Path, goal_path: Path, goal_slug: str, number: int, phase: dict[str, object]) -> str:
    scope_in = phase.get("scope_in") or ["the files and behavior named by this phase"]
    scope_out = phase.get("scope_out") or ["unrelated cleanup and later phases"]
    dependencies = phase.get("dependencies") or ["none — this is the first phase or dependencies are already satisfied"]
    return "\n".join(
        [
            f"# Phase {number}: {phase['title']}",
            "",
            "Status: planned",
            f"Goal: [{goal_slug}](../../../goals/{goal_path.name})",
            "",
            "## Objective",
            "",
            str(phase["objective"]),
            "",
            "## Scope In",
            "",
            _bullet_lines(scope_in),
            "",
            "## Scope Out",
            "",
            _bullet_lines(scope_out),
            "",
            "## Dependencies",
            "",
            _bullet_lines(dependencies),
            "",
            "## Completion Criteria",
            "",
            _bullet_lines(phase["completion"]),
            "",
            "## Verification",
            "",
            _bullet_lines(phase["verification"]),
            "",
            "## Non-Claims",
            "",
            _bullet_lines(phase["non_claims"]),
            "",
            "## Failure Handling",
            "",
            "If verification fails, use `debug` and a 5-whys root-cause pass. "
            "Record the structural pattern and repair before retrying; a retry "
            "alone is not completion.",
            "",
        ]
    )


def _phase_section(goal_text: str, links: list[str]) -> str:
    lines = [
        "## Phase Specifications",
        "",
        "Detailed phase contracts live under `charness-artifacts/specs/`; each phase must satisfy its linked spec before it is marked complete.",
        "",
    ]
    lines.extend(f"- {link}" for link in links)
    return "\n".join(lines)


def _replace_phase_section(text: str, section: str) -> str:
    match = re.search(r"^## Phase Specifications[ \t]*$", text, re.MULTILINE)
    if match is None:
        return text.rstrip() + "\n\n" + section + "\n"
    next_heading = _H2.search(text, match.end())
    end = next_heading.start() if next_heading else len(text)
    return text[:match.start()] + section + "\n\n" + text[end:].lstrip("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and link detailed phase specs for an achieve goal.")
    goal_cli.add_goal_target_args(parser)
    parser.add_argument("--specs-file", type=Path, required=True, help="JSON object with a non-empty `phases` list")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    goal_path = goal_cli.resolve_goal_path(args, goal_lib)
    if not goal_path.is_file():
        raise SystemExit(f"goal artifact not found: {goal_path}")
    repo_root = args.repo_root.expanduser().resolve()
    phases = _load_specs(args.specs_file)
    dated_slug = re.match(r"^\d{4}-\d{2}-\d{2}-(?P<slug>.+)$", goal_path.stem)
    goal_slug = dated_slug.group("slug") if dated_slug else goal_path.stem
    spec_root = repo_root / "charness-artifacts" / "specs" / goal_slug
    links: list[str] = []
    written: list[str] = []
    for index, phase in enumerate(phases, start=1):
        phase_dir = spec_root / f"phase-{index:02d}-{phase['slug']}"
        spec_path = phase_dir / "spec.md"
        rendered = _render_spec(repo_root, goal_path, goal_slug, index, phase)
        if spec_path.exists() and spec_path.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"refusing to overwrite existing phase spec: {spec_path}")
        if not spec_path.exists():
            phase_dir.mkdir(parents=True, exist_ok=True)
            spec_path.write_text(rendered, encoding="utf-8")
            written.append(str(spec_path.relative_to(repo_root)))
        link = Path("..") / "specs" / goal_slug / phase_dir.name / "spec.md"
        links.append(f"Phase {index}: [{phase['title']}]({link.as_posix()}) — completion and verification live in the spec.")
    original = goal_path.read_text(encoding="utf-8")
    updated = _replace_phase_section(original, _phase_section(original, links))
    if updated != original:
        goal_path.write_text(updated, encoding="utf-8")
    yaml_output.emit_yaml({"action": "scaffolded", "goal": str(goal_path.relative_to(repo_root)), "written_specs": written, "phase_count": len(phases)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
