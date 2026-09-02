"""Render the registered artifact shape sources used by the preflight gate.

Shape-source loading, scaffold unwrapping, and section extraction answer one
question: what enforced artifact form should the author see? The dispatcher
retains surface routing and verdict relocation, while this module keeps source
rendering separate and accepts those routing callbacks explicitly.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable


def run_shape_command(
    repo_root: Path,
    surface: Any,
    *,
    stub: bool,
    resolve_shape_source: Callable[[str], tuple[Path | None, str | None]],
    run_repo_script: Callable[..., subprocess.CompletedProcess[str]],
) -> tuple[str, int]:
    """Run a surface's ``shape_command`` and return its rendered text and status."""
    source, error = resolve_shape_source(surface.shape_command[0])
    if source is None:
        return (
            f"(could not render shape source {surface.shape_command[0]}: {error})",
            1,
        )
    script_args = [*surface.shape_command[1:], "--repo-root", str(repo_root)]
    if stub:
        script_args.append("--stub")
    proc = run_repo_script(repo_root, source, script_args)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout, 0
    return (
        f"(could not render shape source {surface.shape_command[0]}: "
        f"{proc.stderr.strip() or 'no output'})",
        1,
    )


def parse_structured_stdout(text: str) -> Any:
    """Parse a repo-owned structured envelope, or return None for plain text."""
    try:
        import yaml
    except ImportError:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


def run_scaffold_template(
    repo_root: Path,
    scaffold: str,
    *,
    resolve_shape_source: Callable[[str], tuple[Path | None, str | None]],
    run_repo_script: Callable[..., subprocess.CompletedProcess[str]],
) -> tuple[str, int]:
    """Run a scaffold and unwrap its markdown template when it emits an envelope."""
    source, error = resolve_shape_source(scaffold)
    if source is None:
        return f"(could not render scaffold {scaffold}: {error})", 1
    proc = run_repo_script(repo_root, source, ["--repo-root", str(repo_root)])
    if proc.returncode != 0 or not proc.stdout.strip():
        return f"(could not render scaffold {scaffold}: {proc.stderr.strip() or 'no output'})", 1
    payload = parse_structured_stdout(proc.stdout)
    template = payload.get("template") if isinstance(payload, dict) else None
    return (template, 0) if isinstance(template, str) else (proc.stdout, 0)


def shape_text(
    repo_root: Path,
    surface: Any,
    *,
    resolve_shape_source: Callable[[str], tuple[Path | None, str | None]],
    run_repo_script: Callable[..., subprocess.CompletedProcess[str]],
    run_scaffold_template: Callable[..., tuple[str, int]],
    run_shape_command: Callable[..., tuple[str, int]],
) -> str:
    if surface.scaffold:
        return run_scaffold_template(repo_root, surface.scaffold)[0]
    # Non-scaffold sources accumulate: a surface may pair a template block (the
    # lines to author into) with a shape_command (the enforced FORMS read live
    # from the owning validator). Each present source contributes one part.
    parts: list[str] = []
    if surface.template_section:
        tpl_rel, _, heading = surface.template_section.partition("|")
        tpl, error = resolve_shape_source(tpl_rel)
        parts.append(
            extract_section(tpl.read_text(encoding="utf-8"), heading)
            if tpl is not None
            else f"(template {tpl_rel} not found: {error})"
        )
    if surface.shape_command:
        parts.append(run_shape_command(repo_root, surface, stub=False)[0])
    if not parts:
        return "(no shape source registered)"
    return "\n\n".join(part.rstrip() for part in parts)


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if line.strip() == heading:
            capturing = True
            out.append(line)
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).rstrip() + "\n" if out else f"(section {heading} not found in template)"
