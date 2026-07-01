from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_script


def test_critique_skill_surfaces_counterweight_and_deliberately_not_doing() -> None:
    skill_text = (ROOT / "skills" / "public" / "critique" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    angle_text = (
        ROOT / "skills" / "public" / "critique" / "references" / "angle-selection.md"
    ).read_text(encoding="utf-8")
    capability_text = (
        ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    ).read_text(encoding="utf-8")
    counterweight_text = (
        ROOT / "skills" / "public" / "critique" / "references" / "counterweight-triage.md"
    ).read_text(encoding="utf-8")
    packet_text = (
        ROOT / "skills" / "public" / "critique" / "references" / "prepare-packet.md"
    ).read_text(encoding="utf-8")
    autonomous_text = (
        ROOT / "skills" / "public" / "critique" / "references" / "autonomous-trigger.md"
    ).read_text(encoding="utf-8")
    cadence_text = (
        ROOT / "skills" / "public" / "critique" / "references" / "cadence.md"
    ).read_text(encoding="utf-8")
    handoff_text = (ROOT / "skills" / "public" / "handoff" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    spec_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "counterweight" in skill_text
    assert "Deliberately Not Doing" in skill_text
    assert "Task-completing repo work always records critique before closeout." in skill_text
    assert "Scale the\npass, not the obligation" in skill_text
    assert "use subagents as the canonical path" in skill_text
    assert "at least two angle subagents plus one separate counterweight subagent" in skill_text
    assert "default to three angle subagents" in skill_text
    assert "if the host cannot provide subagents, stop" in skill_text
    assert "do not collapse into a same-agent local pass or degraded variant" in skill_text
    assert "customer-of-this-capability" in angle_text
    assert "first real use" in angle_text
    assert "stale adapters" in angle_text
    assert "blast-radius" in angle_text
    assert "future maintainer" in angle_text
    assert "minimum: two contrasting angle subagents plus one separate counterweight" in angle_text
    assert "canonical critique path is unavailable" in angle_text
    assert "Do not present a local pass as the canonical fresh-eye review" in capability_text
    assert "host/runtime contract" in capability_text
    assert "shell-only runner" in capability_text
    assert "model self-report" in capability_text
    assert "only observed tool is shell execution" in capability_text
    assert "Subagent Delegation" in capability_text
    assert "repo-mandated bounded fresh-eye reviews are already delegated" in capability_text
    assert "`host signal:` or `tool signal:`" in capability_text
    assert "wrong next action" in handoff_text
    assert "likely implementer misread" in spec_text
    assert "Delegated reviewer fast path" in skill_text
    assert "Do not report blocked for missing nested subagents" in skill_text
    assert "First branch for delegated reviewers" in capability_text
    assert "do not run this capability check" in capability_text
    assert "return the requested findings or triage" in capability_text
    assert "Act Before Ship" in counterweight_text
    assert "Over-Worry" in counterweight_text
    assert "Autonomous trigger" in skill_text
    assert "do\nnot ask first by default" in skill_text
    assert "`references/autonomous-trigger.md`" in skill_text
    assert "docs/handoff.md" in autonomous_text
    assert "git status --short" in autonomous_text
    assert "git log --oneline origin/main..HEAD" in autonomous_text
    assert "otherwise continue from local\n   status and diff evidence" in autonomous_text
    assert "Proceed autonomously" in autonomous_text
    assert "Ask one concise clarifying question" in autonomous_text
    assert "Do not ask the user to provide a change artifact merely because none was\nsupplied" in autonomous_text
    assert "risk boundary, not by commit count" in cadence_text
    assert "The commit is not the review unit." in cadence_text
    assert "Small local-risk slice" in cadence_text
    assert "Substantial slice or bundle" in cadence_text
    assert "Final closeout" in cadence_text
    assert "changed files and owning/generated surfaces" in cadence_text
    assert "Counterweight triage stays mandatory" in cadence_text
    assert "`references/cadence.md`" in skill_text
    assert 'python3 "$SKILL_DIR/scripts/prepare_packet.py" --repo-root .' in skill_text
    assert 'prepare_packet.py" --repo-root . --prepared-for "<short label>" 2>/dev/null || true' not in skill_text
    assert "The `critique` bootstrap runs the runner before spawning reviewers" in packet_text
    assert "does not fire automatically inside the `critique` workflow" not in packet_text
    for risk_class in (
        "workflow",
        "prompt",
        "public-skill",
        "validator",
        "export",
        "release",
        "issue-closeout",
        "compatibility",
        "host-proof",
        "install/update",
        "rename",
        "deletion",
        "design-lock",
        "migration",
    ):
        assert risk_class in cadence_text


def test_spec_and_narrative_preserve_rejected_alternatives() -> None:
    spec_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    narrative_text = (ROOT / "skills" / "public" / "narrative" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "call `critique` for non-trivial contract decisions" in spec_text
    assert "Deliberately Not Doing" in spec_text
    # The rejected-alternatives gist now lives inline in spec SKILL.md (the
    # references/rejected-alternatives.md DUP was removed in reference-compaction
    # Slice 3), so the concept is asserted against the core, not a deleted ref.
    assert "rejected alternatives" in spec_text
    assert "Deliberately Not Doing" in narrative_text


def test_critique_artifact_validator_rejects_missing_explicit_allowance_blocker(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "## Subagent Delegation",
                "",
                "- Repo-mandated bounded fresh-eye subagent reviews are already delegated by this repo contract.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "blocked because the current developer instruction only permits spawning subagents when the user explicitly asks.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "must not treat missing explicit subagent delegation" in result.stderr


def test_critique_artifact_validator_allows_parent_delegated_artifact_with_blocked_domain_content(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "## Subagent Delegation",
                "",
                "- Repo-mandated bounded fresh-eye subagent reviews are already delegated by this repo contract.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated.",
                "",
                "## Reviewer Tier Evidence",
                "",
                "- **Requested tier**: `high-leverage`",
                "- **Requested spawn fields**: `model=gpt-5.5`",
                "- **Host exposure state**: `requested_fields_sent`",
                "- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`",
                "",
                "The runtime still has blocked JSON endpoints; this is domain content, not a subagent blocker.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 0, result.stderr
    assert "Validated 1 critique artifact" in result.stdout


def test_critique_artifact_validator_requires_reviewer_tier_evidence_for_parent_delegated(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "reviewer tier evidence missing fields" in result.stderr


def test_critique_artifact_validator_requires_reviewer_tier_evidence_when_packet_consumed(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Packet Consumed: charness-artifacts/critique/demo-packet.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "reviewer tier evidence missing fields" in result.stderr


def test_critique_artifact_validator_accepts_concrete_blocked_signal(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "blocked.",
                "",
                "host signal: agent-count budget exhausted before the bounded reviewer could be spawned.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 0, result.stderr
    assert "Validated 1 critique artifact" in result.stdout


def test_critique_artifact_validator_accepts_reviewer_tier_evidence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated.",
                "",
                "## Reviewer Tier Evidence",
                "",
                "- **Requested tier**: `high-leverage`",
                "- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`",
                "- **Host exposure state**: `requested_fields_sent`",
                "- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--all",
    )

    assert result.returncode == 0, result.stderr


def test_critique_artifact_validator_rejects_applied_without_host_confirmation(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated.",
                "",
                "## Reviewer Tier Evidence",
                "",
                "- **Requested tier**: `high-leverage`",
                "- **Requested spawn fields**: `model=gpt-5.5`",
                "- **Host exposure state**: `applied`",
                "- **Application state**: `fields were sent`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--all",
    )

    assert result.returncode == 1
    assert "host-confirmed:" in result.stderr


def test_critique_artifact_validator_accepts_signal_section_with_body(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "blocked.",
                "",
                "## Host Signal",
                "",
                "agent-count budget exhausted before the bounded reviewer could be spawned.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 0, result.stderr
    assert "Validated 1 critique artifact" in result.stdout


def test_critique_artifact_validator_rejects_empty_signal_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "blocked.",
                "",
                "## Host Signal",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "must cite `host signal:` or `tool signal:`" in result.stderr


def test_critique_artifact_validator_rejects_marker_only_signal_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "blocked.",
                "",
                "## Tool Signal",
                "",
                "-",
                ".",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "must cite `host signal:` or `tool signal:`" in result.stderr


def test_critique_artifact_validator_fails_closed_when_changed_path_discovery_fails(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "critique artifact changed-path discovery failed" in result.stderr


def _seed_structured_critique(repo: Path, body: str) -> Path:
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    return artifact


_STRUCTURED_PRELUDE = (
    "# Demo Critique\n"
    "\n"
    "Fresh-Eye Satisfaction: parent-delegated.\n"
    "\n"
    "## Reviewer Tier Evidence\n"
    "\n"
    "- **Requested tier**: `high-leverage`\n"
    "- **Requested spawn fields**: `model=gpt-5.5`\n"
    "- **Host exposure state**: `requested_fields_sent`\n"
    "- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`\n"
    "\n"
)


def test_validate_critique_structured_findings_accepts_well_formed_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/impl/SKILL.md:139 | action: fix | note: missing Lint Gate\n"
        + "- F2 | bin: over-worry | evidence: weak | ref: n/a | action: document | note: speculative\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_validate_critique_structured_findings_rejects_unknown_bin(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: must-fix | evidence: strong | ref: a:1 | action: fix | note: typo bin\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "unknown bin" in result.stderr


def test_validate_critique_structured_findings_rejects_missing_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: bundle-anyway | evidence: moderate | action: fix | note: missing ref\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "missing required field `ref`" in result.stderr


def test_validate_critique_structured_findings_rejects_duplicate_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: act-before-ship | evidence: strong | ref: a:1 | action: fix | note: first\n"
        + "- F1 | bin: over-worry | evidence: weak | ref: b:2 | action: document | note: dup\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "duplicate id" in result.stderr


def test_validate_critique_structured_findings_section_is_opt_in(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = _STRUCTURED_PRELUDE + "## Findings\n\n- prose only\n"
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_validate_critique_structured_findings_rejects_file_issue_without_followup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: valid-but-defer | evidence: moderate | ref: a:1 | action: file-issue | note: missing follow-up\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "file-issue" in result.stderr
    assert "follow-up:" in result.stderr


def test_validate_critique_structured_findings_accepts_file_issue_with_followup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: valid-but-defer | evidence: moderate | ref: a:1 | action: file-issue | follow-up: https://github.com/x/y/issues/1 | note: filed\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_validate_critique_structured_findings_rejects_bare_deferred_followup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _STRUCTURED_PRELUDE
        + "## Structured Findings\n"
        + "\n"
        + "- F1 | bin: valid-but-defer | evidence: moderate | ref: a:1 | action: file-issue | follow-up: deferred | note: bare\n"
        + "\n"
    )
    _seed_structured_critique(repo, body)
    result = run_script("scripts/validate_critique_artifacts.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
