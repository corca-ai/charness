"""Gate-packet construction for the retro run planner."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def build_gate_packets(
    repo_root: Path,
    adapter: dict[str, Any],
    scaffold: dict[str, Any],
    *,
    packet: Callable[..., dict[str, Any]],
    relative_script_command: Callable[..., dict[str, Any]],
    skill_script_command: Callable[..., dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build deterministic packets without interpreting their results."""
    packets = [
        packet(
            "adapter-readiness",
            "deterministic adapter parser; trust failures and warnings",
            status="pass" if adapter.get("valid") else "fail",
            path=adapter.get("path"),
            warnings=adapter.get("warnings", []),
            errors=adapter.get("errors", []),
        ),
        packet(
            "retro-artifact-scaffold",
            "deterministic scaffold payload; trust write target and validator command",
            command="python3 $SKILL_DIR/scripts/scaffold_retro_artifact.py --repo-root .",
            write_artifact_path=scaffold["write_artifact_path"],
            write_artifact_effect=scaffold["write_artifact_effect"],
            validator_command=scaffold["validator_command"],
        ),
        packet(
            "retro-artifact-shape",
            "deterministic Sibling Search follow-up grammar gate for the artifact this run writes;"
            " trust section/format failures",
            run_when="after the retro artifact is written; this validates that artifact",
            **relative_script_command(
                repo_root,
                "scripts/validate_retro_artifact.py",
                "--repo-root",
                ".",
                "--paths",
                scaffold["write_artifact_path"],
            ),
        ),
        packet(
            "auto-session-trigger",
            "deterministic slice-surface trigger probe; agent judges whether to fire a bounded session retro",
            **skill_script_command("scripts/check_auto_trigger.py", "--repo-root", "."),
        ),
    ]
    for index, command in enumerate(adapter["data"].get("metrics_commands", []), start=1):
        packets.append(
            packet(
                f"adapter-metric-{index}",
                "adapter-declared read-only metric; trust its structured counts and failures, not causal interpretation",
                command=str(command),
                run_when="after the retro disposition is written and persisted, before closeout",
            )
        )
    return packets
