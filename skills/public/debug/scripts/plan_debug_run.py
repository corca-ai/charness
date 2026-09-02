#!/usr/bin/env python3
"""Plan the first phase of a debug run before broad search or repair."""

from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

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


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_RUNTIME = _load_skill_runtime_bootstrap()
resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
scaffold_debug_artifact = SKILL_RUNTIME.load_local_skill_module(__file__, "scaffold_debug_artifact")
risk_interrupt_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.gates_support.risk_interrupt_lib")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
_scaffold_artifact_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.core.scaffold_artifact_lib")
declarations = SKILL_RUNTIME.load_local_skill_module(__file__, "debug_artifact_declarations")
# The artifact-state questions the plan is assembled FROM, in one owner.
_state = SKILL_RUNTIME.load_local_skill_module(__file__, "debug_artifact_state")
_artifact_summary = _state._artifact_summary
_prior_incidents = _state._prior_incidents
_refusal_keys = _state._refusal_keys
_continues_existing_artifact = _state._continues_existing_artifact
# Re-exported because a test drives this branch directly; the owner is `_state`.
_title_for = _state._title_for
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



def _required_reads(
    *,
    adapter: dict[str, Any],
    artifact: dict[str, Any],
    prior_incidents: list[dict[str, Any]],
    continues_existing: bool,
) -> list[dict[str, str]]:
    reads: list[dict[str, str]] = []
    # `continues_existing`, not a THIRD private spelling of the same two fields. A bounded
    # round found this branch still deciding on its own after `mode` and `next_action` were
    # unified: the plan reported a fresh investigation while `required_reads[0]` — the surface
    # a run opens FIRST — still named the refused record as "current debugging state".
    if continues_existing:
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
                "artifact is missing, resolved, or another subject's; scaffold a fresh investigation before recording diagnosis",
                base="skill",
            )
        )
        if artifact["exists"]:
            reads.append(
                _read(
                    str(artifact["path"]),
                    "artifact",
                    # Not "resolved prior incident" unconditionally: this branch is also reached
                    # when the record is OPEN and belongs to a different declared subject, and
                    # calling that resolved states a lifecycle fact the plan did not read.
                    "prior incident this run is not continuing; ownership unconfirmed, so read it "
                    "if the symptom or seam is related, then scaffold a new artifact",
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
    scaffold_command = _scaffold_command(scaffold)
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
            command=scaffold_command,
            artifact_path=scaffold["artifact_path"],
            write_artifact_path=scaffold["write_artifact_path"],
            write_artifact_role=scaffold["write_artifact_role"],
            validator_command=scaffold["validator_command"],
        ),
        # Scoped to the artifact this run writes. The packet calls itself a
        # "current-artifact schema gate" and emitted the whole-corpus command, so its
        # exit code answered a different question than its own label: a fresh valid
        # artifact still exited 1 when an unrelated older record carried legacy-schema
        # debt, and the operator had to read a long report to learn the failure was not
        # theirs. The corpus sweep is still reachable -- `--all` is the audit mode, and
        # the broad gate and CI already run it.
        _packet(
            "debug-artifact-shape",
            "deterministic schema gate for the artifact this run writes; trust section/order failures",
            # Ordering is load-bearing now that the command NAMES the artifact: run before
            # the write and the validator refuses a path that resolves to nothing, which
            # reads as a typo accusation for an agent doing the ordinary thing (cheap
            # deterministic packets first).
            run_when="after the artifact is written; the command names it by path",
            **_relative_script_command(
                repo_root,
                "scripts/gates/validate_debug_artifact.py",
                "--repo-root",
                ".",
                "--paths",
                scaffold["write_artifact_path"],
                *(["--evidence-led"] if scaffold.get("evidence_mode") else []),
            ),
        ),
        _packet(
            "seam-risk-index",
            "deterministic index builder when available; agent judges whether a risk interrupt is warranted",
            **_relative_script_command(repo_root, "scripts/build_debug_seam_risk_index.py", "--repo-root", "."),
        ),
    ]


def _artifact_next_action(
    kind: str, instruction: str, artifact: dict[str, Any], *, repo_root: Path, scaffold: dict[str, Any]
) -> dict[str, Any]:
    """The branches that name an EXISTING artifact as the write target.

    These carry the write-target fact too. A bounded round found the distribution inverted
    against risk: only the scaffold branch carried it, and that branch is reached when the
    artifact is absent or resolved -- almost always `create_new_file`. The
    continue-existing-artifact branch is the one whose target holds content, and it was the
    one staying silent.

    The facts come from the OWNER now. They were recomputed here from `write_exists`, which is
    `.is_file()`, while `write_target_facts` is deliberately `.exists()` -- a directory at the
    write path made the plan say `create_new_file` where the owner says
    `overwrite_existing_content`. Round 2 found this surviving as a seventh derivation of the
    rule this slice's own guard exists to consolidate, invisible because the guard accepts the
    key name as evidence of an echo.

    And they carry what the producer declined: an arm that hands back an existing record's path
    with no refusal keys reads as an ordinary write target.
    """
    return {
        "kind": kind,
        "instruction": instruction,
        "artifact_path": artifact["path"],
        "write_artifact_path": artifact["write_path"],
        **_scaffold_artifact_lib.write_target_facts(repo_root, str(artifact["write_path"])),
        **_refusal_keys(scaffold),
    }


def _scaffold_command(scaffold: dict[str, Any]) -> str:
    """The command that reproduces THIS plan's write path, `--subject` included.

    A bounded round found the plan handing back a bare command while its own
    `write_artifact_path` was derived from a declared subject: running the printed command
    produced a different file than the plan named, and the skill prose meanwhile told the
    author to pass `--subject` to both surfaces.
    """
    subject = scaffold.get("invocation_subject_key")
    suffix = f" --subject {subject}" if isinstance(subject, str) and subject else ""
    evidence = " --evidence-led" if scaffold.get("evidence_mode") else ""
    return f"python3 $SKILL_DIR/scripts/scaffold_debug_artifact.py --repo-root .{suffix}{evidence}"


def _next_action(repo_root: Path, artifact: dict[str, Any], scaffold: dict[str, Any]) -> dict[str, Any]:
    if artifact["requires_interrupt"]:
        return _artifact_next_action(
            "interrupt-to-spec",
            "read the current artifact and seam references, then hand off a named spec artifact before ordinary repair",
            artifact,
            repo_root=repo_root,
            scaffold=scaffold,
        )
    if artifact["exists"] and not artifact.get("risk_scope_established", True):
        action = _artifact_next_action(
            "repair-risk-declaration",
            "the `- Risk Class:` declaration could not be read (unparseable, or hidden behind "
            "an unclosed code fence), so the risk interrupt decision is unproven; repair the "
            "line -- and close any open fence above it -- then re-run this plan before ordinary repair",
            artifact,
            repo_root=repo_root,
            scaffold=scaffold,
        )
        action["risk_parse_error"] = artifact["risk_parse_error"]
        return action
    if _continues_existing_artifact(artifact, scaffold):
        return _artifact_next_action(
            "continue-existing-artifact",
            "read the current artifact, preserve observed facts, then continue with the cheapest falsifier before repair",
            artifact,
            repo_root=repo_root,
            scaffold=scaffold,
        )
    next_action = {
        "kind": "scaffold-debug-artifact",
        "command": _scaffold_command(scaffold),
        "instruction": "write the emitted template to write_artifact_path before broad search or repair",
        "artifact_path": scaffold["artifact_path"],
        "write_artifact_path": scaffold["write_artifact_path"],
        "write_artifact_role": scaffold["write_artifact_role"],
        # The planner is the surface `SKILL.md` routes to FIRST, so it must carry the fact
        # about the write target and not leave it only on the scaffold payload.
        "write_artifact_effect": scaffold["write_artifact_effect"],
        "write_artifact_target_exists": scaffold["write_artifact_target_exists"],
    }
    # Same reason as the two keys above, one step further: a run routed OFF another
    # investigation's open record reads as an ordinary fresh start unless the plan says what it
    # was routed off and how to continue that one deliberately.
    next_action.update(_refusal_keys(scaffold))
    if scaffold.get("update_current_pointer_after_write"):
        next_action["instruction"] = (
            "write the emitted template to write_artifact_path before broad search or repair, "
            "then refresh the current pointer with refresh_current_pointer_command"
        )
        next_action["update_current_pointer_after_write"] = True
        next_action["refresh_current_pointer_command"] = scaffold["refresh_current_pointer_command"]
    return next_action


def build_plan(repo_root: Path, *, subject: str | None = None, evidence_mode: bool = False) -> dict[str, Any]:
    adapter = resolve_adapter.load_adapter(repo_root)
    scaffold = scaffold_debug_artifact.payload_for(
        repo_root, title=None, subject=subject, evidence_mode=evidence_mode
    )
    scaffold_summary = {key: value for key, value in scaffold.items() if key != "template"}
    artifact = _artifact_summary(repo_root, scaffold)
    output_dir = str(adapter["data"]["output_dir"])
    # `current_path` excludes one record from prior_incidents: the one this run is continuing.
    # When the scaffold refused the pointer's record, this run continues nothing, so excluding
    # it would drop the refused record out of `prior_incidents` — leaving a plan that says
    # `fresh-investigation-with-prior-memory` with the one relevant memory removed.
    prior_incidents = _prior_incidents(
        repo_root,
        output_dir,
        str(artifact["write_path"]) if _continues_existing_artifact(artifact, scaffold) else str(scaffold["write_artifact_path"]),
    )
    # `continue-existing-artifact` routes the author INTO the pointer's record, so it is the
    # consumer half of the same defect the scaffold just fixed: a producer that refuses to
    # hand back another subject's record is undone by a planner that names it in the next
    # line. The two risk arms below are deliberately NOT subject-scoped: an undeclared or
    # unparseable risk interrupt blocks the repo whoever opened it.
    if artifact["requires_interrupt"]:
        mode = "risk-interrupt"
    elif artifact["exists"] and not artifact.get("risk_scope_established", True):
        mode = "repair-risk-declaration"
    elif _continues_existing_artifact(artifact, scaffold):
        mode = "continue-existing-artifact"
    elif prior_incidents or artifact["exists"]:
        mode = "fresh-investigation-with-prior-memory"
    else:
        mode = "fresh-investigation"
    return ENVELOPE.build_envelope(
        schema_version="debug.run_plan.v1",
        required_reads=ENVELOPE.measure_reads(
            _required_reads(
                adapter=adapter,
                artifact=artifact,
                prior_incidents=prior_incidents,
                continues_existing=_continues_existing_artifact(artifact, scaffold),
            ),
            {"repo": repo_root, "skill": SKILL_ROOT},
        ),
        next_action=_next_action(repo_root, artifact, scaffold),
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
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to analyze; defaults to the current working directory",
    )
    # Without this, resuming an investigation is unplannable: the planner would ask the
    # scaffold for a path while declaring no subject, and the scaffold answers that ambiguity
    # with a FRESH record rather than with someone else's open one.
    parser.add_argument(
        "--subject",
        help="Slug of the open investigation this run continues; omit to start a new one",
    )
    parser.add_argument(
        "--evidence-led",
        action="store_true",
        help="Carry reported-finding evidence mode into the scaffold and validator packets",
    )
    args = parser.parse_args()
    payload = build_plan(args.repo_root.resolve(), subject=args.subject, evidence_mode=args.evidence_led)
    yaml_output.emit_yaml(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
