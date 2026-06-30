#!/usr/bin/env python3
"""Plan the first phase of a debug run before broad search or repair."""

from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

MAX_PRIOR_INCIDENTS = 5
ON_DEMAND_REFERENCE_READS = (
    ("references/disconfirmer-first.md", "before absence, attribution, liveness, or frequency claims"),
    ("references/named-target-verification.md", "when the diagnosis names a specific target or runtime object"),
    ("references/five-whys-causal-chain.md", "before converting symptom evidence into root cause"),
    ("references/invariant-first-review.md", "for workflow-boundary bugs, propagated diagnostics, or readiness decisions"),
    ("references/detection-gap.md", "before closeout, map what existing gate failed to catch"),
    ("references/sibling-search.md", "before closeout, classify sibling decisions and proof levels"),
)


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
scaffold_debug_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "scaffold_debug_artifact")
risk_interrupt_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.risk_interrupt_lib")
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"))
)


def _read(path: str, kind: str, why: str, *, base: str) -> dict[str, str]:
    return ENVELOPE.read(path, why, kind=kind, base=base)


_packet = ENVELOPE.gate_packet


def _relative_script_command(repo_root: Path, rel_path: str, *args: str) -> dict[str, Any]:
    path = repo_root / rel_path
    return {
        "command": " ".join(["python3", rel_path, *args]),
        "available": path.is_file(),
        "path": rel_path,
    }


def _parse_field(text: str, label: str) -> str | None:
    prefix = f"- {label}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            value = stripped[len(prefix) :].strip()
            return value or None
    return None


def _risk_summary(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "risk_classes": [],
            "next_step": None,
            "requires_interrupt": False,
        }
    text = path.read_text(encoding="utf-8")
    risk_class_raw = _parse_field(text, "Risk Class")
    next_step = _parse_field(text, "Next Step")
    generalization_pressure = _parse_field(text, "Generalization Pressure")
    try:
        risk_classes = risk_interrupt_lib._parse_risk_classes(risk_class_raw or "")
        risk_parse_error = None
    except risk_interrupt_lib.ValidationError as exc:
        risk_classes = ()
        risk_parse_error = str(exc)
    forced = bool(
        set(risk_classes) & risk_interrupt_lib.FORCED_RISK_CLASSES
        or generalization_pressure == "factor-now"
    )
    return {
        "risk_classes": list(risk_classes),
        "risk_parse_error": risk_parse_error,
        "generalization_pressure": generalization_pressure,
        "next_step": next_step,
        "requires_interrupt": forced,
    }


def _artifact_summary(repo_root: Path, scaffold: dict[str, Any]) -> dict[str, Any]:
    artifact_rel = str(scaffold["artifact_path"])
    write_rel = str(scaffold["write_artifact_path"])
    artifact_path = repo_root / artifact_rel
    write_path = repo_root / write_rel
    exists = artifact_path.is_file()
    write_exists = write_path.is_file()
    text = artifact_path.read_text(encoding="utf-8") if exists else ""
    line_count = len(text.splitlines()) if exists else 0
    # Resolution lifecycle: an existing current pointer is treated as an OPEN
    # investigation to continue UNLESS it explicitly declares `- Resolution: resolved`.
    # Default open (missing field) keeps same-investigation resume and legacy
    # behavior; only an explicit `resolved` (set at closeout) makes the planner
    # treat the pointer as a closed prior incident instead of a continuation, so a
    # closed artifact stops hijacking a fresh bug (#debug claim-fidelity mis-fire).
    resolution = "resolved" if (exists and (_parse_field(text, "Resolution") or "").strip().lower() == "resolved") else "open"
    if exists and scaffold["write_artifact_role"] == "current_pointer_target":
        status = "current_pointer_target_exists"
    elif exists:
        status = "current_pointer_exists"
    else:
        status = "missing"
    summary: dict[str, Any] = {
        "path": artifact_rel,
        "exists": exists,
        "resolution": resolution,
        "line_count": line_count,
        "status": status,
        "role": scaffold["artifact_role"],
        "write_path": write_rel,
        "write_exists": write_exists,
        "write_role": scaffold["write_artifact_role"],
        "current_pointer_symlink_target": scaffold["current_pointer_symlink_target"],
    }
    summary.update(_risk_summary(artifact_path))
    return summary


def _title_for(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _prior_incidents(repo_root: Path, output_dir: str, current_path: str) -> list[dict[str, Any]]:
    directory = repo_root / output_dir
    if not directory.is_dir():
        return []
    current_resolved = (repo_root / current_path).resolve()
    candidates: list[Path] = []
    for pattern in ("debug-*.md", "20*.md"):
        candidates.extend(directory.glob(pattern))
    unique = sorted(set(candidates), key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
    incidents = []
    for path in unique:
        if path.name == "latest.md" or path.resolve() == current_resolved:
            continue
        rel_path = str(path.relative_to(repo_root))
        incidents.append(
            {
                "path": rel_path,
                "title": _title_for(path),
                "mtime": path.stat().st_mtime,
            }
        )
        if len(incidents) >= MAX_PRIOR_INCIDENTS:
            break
    return incidents


def _required_reads(
    *,
    adapter: dict[str, Any],
    artifact: dict[str, Any],
    prior_incidents: list[dict[str, Any]],
) -> list[dict[str, str]]:
    reads: list[dict[str, str]] = []
    if artifact["exists"] and artifact["resolution"] != "resolved":
        reads.append(
            _read(
                str(artifact["path"]),
                "artifact",
                "current debugging state before broad search",
                base="repo",
            )
        )
    else:
        reads.append(
            _read(
                "scripts/scaffold_debug_artifact.py",
                "script",
                "artifact is missing or resolved; scaffold a fresh investigation before recording diagnosis",
                base="skill",
            )
        )
        if artifact["exists"]:
            reads.append(
                _read(
                    str(artifact["path"]),
                    "artifact",
                    "resolved prior incident; read if the symptom or seam is related, then scaffold a new artifact",
                    base="repo",
                )
            )

    reads.append(_read("references/five-steps.md", "reference", "canonical RCA sequence for the run", base="skill"))
    reads.append(
        _read(
            "references/debug-memory.md",
            "reference",
            "how to preserve and reuse prior incident memory",
            base="skill",
        )
    )

    if not adapter.get("found") or adapter.get("warnings") or adapter.get("errors"):
        reads.append(_read("references/adapter-contract.md", "reference", "adapter was missing, warned, or invalid", base="skill"))

    for incident in prior_incidents:
        reads.append(
            _read(
                str(incident["path"]),
                "artifact",
                "prior debug memory candidate; read if the symptom or seam is related",
                base="repo",
            )
        )

    if artifact["requires_interrupt"]:
        reads.append(
            _read(
                "references/document-seams.md",
                "reference",
                "structured handoff when local reasoning cannot prove the seam",
                base="skill",
            )
        )
        reads.append(
            _read(
                "references/invariant-first-review.md",
                "reference",
                "prove producer-to-final-consumer behavior before ordinary repair",
                base="skill",
            )
        )
    return reads


def _on_demand_reads() -> list[dict[str, str]]:
    return [_read(path, "reference", why, base="skill") for path, why in ON_DEMAND_REFERENCE_READS]


def _gate_packets(repo_root: Path, adapter: dict[str, Any], scaffold: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _packet(
            "adapter-readiness",
            "deterministic adapter parser; trust failures and warnings",
            status="pass" if adapter.get("valid") else "fail",
            path=adapter.get("path"),
            warnings=adapter.get("warnings", []),
            errors=adapter.get("errors", []),
        ),
        _packet(
            "debug-artifact-scaffold",
            "deterministic scaffold payload; trust write target and validator command",
            command="python3 $SKILL_DIR/scripts/scaffold_debug_artifact.py --repo-root . --json",
            artifact_path=scaffold["artifact_path"],
            write_artifact_path=scaffold["write_artifact_path"],
            write_artifact_role=scaffold["write_artifact_role"],
            validator_command=scaffold["validator_command"],
        ),
        _packet(
            "debug-artifact-shape",
            "deterministic current-artifact schema gate; trust section/order failures",
            **_relative_script_command(repo_root, "scripts/validate_debug_artifact.py", "--repo-root", "."),
        ),
        _packet(
            "seam-risk-index",
            "deterministic index builder when available; agent judges whether a risk interrupt is warranted",
            **_relative_script_command(repo_root, "scripts/build_debug_seam_risk_index.py", "--repo-root", "."),
        ),
    ]


def _artifact_next_action(kind: str, instruction: str, artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind,
        "instruction": instruction,
        "artifact_path": artifact["path"],
        "write_artifact_path": artifact["write_path"],
    }


def _next_action(artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact["requires_interrupt"]:
        return _artifact_next_action(
            "interrupt-to-spec",
            "read the current artifact and seam references, then hand off a named spec artifact before ordinary repair",
            artifact,
        )
    if artifact["exists"] and artifact["resolution"] != "resolved":
        return _artifact_next_action(
            "continue-existing-artifact",
            "read the current artifact, preserve observed facts, then continue with the cheapest falsifier before repair",
            artifact,
        )
    return {
        "kind": "scaffold-debug-artifact",
        "command": "python3 $SKILL_DIR/scripts/scaffold_debug_artifact.py --repo-root . --json",
        "instruction": "write the emitted template to write_artifact_path before broad search or repair",
        "write_artifact_path": artifact["write_path"],
    }


def build_plan(repo_root: Path) -> dict[str, Any]:
    adapter = resolve_adapter.load_adapter(repo_root)
    scaffold = scaffold_debug_artifact.payload_for(repo_root, title=None)
    scaffold_summary = {key: value for key, value in scaffold.items() if key != "template"}
    artifact = _artifact_summary(repo_root, scaffold)
    output_dir = str(adapter["data"]["output_dir"])
    prior_incidents = _prior_incidents(repo_root, output_dir, str(artifact["write_path"]))
    if artifact["requires_interrupt"]:
        mode = "risk-interrupt"
    elif artifact["exists"] and artifact["resolution"] != "resolved":
        mode = "continue-existing-artifact"
    elif prior_incidents or artifact["exists"]:
        mode = "fresh-investigation-with-prior-memory"
    else:
        mode = "fresh-investigation"
    return ENVELOPE.build_envelope(
        schema_version="debug.run_plan.v1",
        required_reads=_required_reads(adapter=adapter, artifact=artifact, prior_incidents=prior_incidents),
        next_action=_next_action(artifact),
        gate_packets=_gate_packets(repo_root, adapter, scaffold),
        ok=bool(adapter.get("valid")),
        repo_root=str(repo_root),
        mode=mode,
        adapter=ENVELOPE.adapter_echo(adapter),
        artifact=artifact,
        scaffold=scaffold_summary,
        prior_incidents=prior_incidents,
        on_demand_reads=_on_demand_reads(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a debug run before broad search or repair.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit JSON; accepted for parity with other planners")
    args = parser.parse_args()
    payload = build_plan(args.repo_root.resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
