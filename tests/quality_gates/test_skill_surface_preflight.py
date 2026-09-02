from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import check_skill_surface_preflight as preflight

ROOT = Path(__file__).resolve().parents[2]


def _write_skill(repo: Path, *, skill_lines: list[str]) -> Path:
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text("\n".join(skill_lines) + "\n", encoding="utf-8")
    return skill_path


def _skill_at_ceiling() -> list[str]:
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
    ]
    lines.extend(f"Core line {index}" for index in range(159))
    lines.extend(["", "## References", "", "- `references/note.md`"])
    lines.extend("" for _ in range(31))
    assert len(lines) == 200
    return lines


def test_skill_surface_preflight_blocks_skill_md_preview_past_known_ceilings(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_at_ceiling())

    payload = preflight.build_report(repo.resolve(), str(skill_path), 1, False)
    assert json.loads(json.dumps(payload))["status"] == "blocked"
    assert payload["status"] == "blocked"
    assert set(payload["blockers"]) == {"skill_md_total", "core_nonempty"}
    assert payload["headroom"]["skill_md_total"]["remaining_after_preview"] == -1
    assert payload["headroom"]["core_nonempty"]["remaining_after_preview"] == -1


def _skill_near_cap(total_lines: int) -> list[str]:
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        "Use this when the repo needs a demo skill.",
        "",
        "## References",
        "",
        "- `references/note.md`",
    ]
    lines.extend("" for _ in range(total_lines - len(lines)))
    assert len(lines) == total_lines
    return lines


def test_skill_surface_preflight_warns_near_cap_without_blocking(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_near_cap(195))

    payload = preflight.build_report(repo.resolve(), str(skill_path), 0, False)
    assert payload["status"] == "ok"
    assert payload["blockers"] == []
    assert [row["id"] for row in payload["warnings"]] == ["near_cap"]
    assert "195/200" in payload["warnings"][0]["message"]
    assert "never silently drop" in payload["warnings"][0]["message"]
    # The warning has to reach the reader through the payload the gate actually
    # emits, not a side renderer: `preflight_payload` is that emitted surface.
    emitted = preflight.preflight_payload(payload)
    assert [row["id"] for row in emitted["warnings"]] == ["near_cap"]
    assert "195/200" in emitted["warnings"][0]["message"]


def test_skill_surface_preflight_no_near_cap_warning_below_floor(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_near_cap(194))

    payload = preflight.build_report(repo.resolve(), str(skill_path), 0, False)
    assert payload["status"] == "ok"
    assert payload["warnings"] == []
    assert preflight.preflight_payload(payload)["warnings"] == []


def test_skill_surface_preflight_at_ceiling_warns_and_blocks_independently(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_at_ceiling())

    payload = preflight.build_report(repo.resolve(), str(skill_path), 1, False)
    assert payload["status"] == "blocked"
    assert [row["id"] for row in payload["warnings"]] == ["near_cap"]


def test_skill_surface_preflight_reference_preview_preserves_core_headroom(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _write_skill(
        repo,
        skill_lines=[
            "---",
            "name: demo",
            'description: "Demo skill."',
            "---",
            "",
            "# Demo",
            "",
            "Use this when the repo needs a demo skill.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    reference_path = repo / "skills" / "public" / "demo" / "references" / "note.md"

    payload = preflight.build_report(repo.resolve(), str(reference_path), 200, False)
    assert payload["target"]["kind"] == "reference"
    assert payload["headroom"]["skill_md_total"]["preview_delta"] == 0
    assert payload["headroom"]["core_nonempty"]["preview_delta"] == 0
    assert "reference_link_depth" in {row["id"] for row in payload["couplings"]}
    assert "plugin_mirror_sync" in {row["id"] for row in payload["couplings"]}


def test_check_commands_cover_full_portable_package_gate_set() -> None:
    # #328: the one-shot --run-checks preflight must report ALL the portable-package
    # gates at once (a narrower set leaves ~4 commit-boundary round-trips uncaught).
    ids = {check_id for check_id, _command in preflight._check_commands(Path("."))}
    assert {
        "validate_skills",
        "validate_skill_ergonomics",
        "check_skill_ownership_overlap",
        "validate_attention_state_visibility",
        "check_doc_links",
        "check_markdown",
    } <= ids


def test_run_checks_reports_all_portable_package_gates_in_declared_order(
    tmp_path: Path,
    monkeypatch,
) -> None:
    # Fast in-process simulation: prove the one-shot preflight still runs the full
    # portable gate set in declared order, maps ids/commands/results correctly, and
    # blocks/surfaces tails when a gate fails.
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_near_cap(12))
    repo_root = repo.resolve()
    (repo_root / "tools").mkdir()  # the authoring shape: tools/ gates are declared and run
    declared = preflight._check_commands(repo_root)
    expected_ids = [check_id for check_id, _command in declared]
    expected_commands = [command for _check_id, command in declared]
    long_stdout = "stdout-" + ("a" * 1100)
    long_stderr = "stderr-" + ("b" * 1100)
    calls: list[tuple[list[list[str]], Path, None]] = []

    def fake_run_processes_in_order(commands, *, cwd, timeout_seconds):
        calls.append((commands, cwd, timeout_seconds))
        return [
            subprocess.CompletedProcess(command, 0, stdout="", stderr="")
            if index != 2
            else subprocess.CompletedProcess(command, 7, stdout=long_stdout, stderr=long_stderr)
            for index, command in enumerate(commands)
        ]

    monkeypatch.setattr(preflight, "run_processes_in_order", fake_run_processes_in_order)

    checks = preflight._run_checks(repo_root)
    assert calls == [(expected_commands, repo_root, None)]
    assert [row["id"] for row in checks] == expected_ids
    assert [row["command"] for row in checks] == [" ".join(command) for command in expected_commands]
    assert checks[2]["returncode"] == 7
    assert checks[2]["stdout_tail"] == long_stdout[-1000:]
    assert checks[2]["stderr_tail"] == long_stderr[-1000:]

    report = preflight.build_report(repo_root, str(skill_path), 0, True)
    assert calls == [
        (expected_commands, repo_root, None),
        (expected_commands, repo_root, None),
    ]
    assert [row["id"] for row in report["checks"]] == expected_ids
    assert report["check_failures"] == [expected_ids[2]]
    assert report["status"] == "blocked"


def test_skill_surface_preflight_rejects_non_skill_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    outside = repo / "docs" / "note.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("# Note\n", encoding="utf-8")

    with pytest.raises(preflight.PreflightError, match="target must live under skills/public"):
        preflight.build_report(repo.resolve(), str(outside), 0, False)


# --- #319: commit-boundary core_nonempty headroom-buffer ratchet ---


_LIMIT = preflight.MAX_CORE_NONEMPTY_LINES
_BUFFER = preflight.CORE_NONEMPTY_HEADROOM_BUFFER


def _skill_with_core(core: int) -> str:
    lines = ["---", "name: demo", 'description: "Demo skill."', "---", "", "# Demo"]
    lines.extend(f"Core line {index}" for index in range(core - 1))
    lines.extend(["", "## References", "", "- `references/note.md`"])
    return "\n".join(lines) + "\n"


def test_skill_with_core_helper_counts_match_core_nonempty() -> None:
    # Guards the test fixture itself: the broad-gate computation must agree with
    # what _skill_with_core claims, or the ratchet cases below would be vacuous.
    assert preflight._core_nonempty_lines(_skill_with_core(_LIMIT)) == _LIMIT
    assert preflight._core_nonempty_lines(_skill_with_core(_LIMIT - 10)) == _LIMIT - 10


def test_evaluate_core_headroom_blocks_healthy_skill_dropped_below_buffer() -> None:
    # The #316 triggering instance generalized: a skill with headroom edited down
    # to the hard limit (0 remaining) is blocked at the commit boundary.
    verdict = preflight.evaluate_core_headroom(_LIMIT, _LIMIT - (_BUFFER + 4))
    assert verdict["new_remaining"] == 0
    assert verdict["blocked"] is True


def test_evaluate_core_headroom_grandfathers_existing_under_buffer_flat_edit() -> None:
    # A skill already at the limit (0 remaining) may take a flat edit without being
    # retroactively blocked -- the ratchet only blocks fresh erosion.
    verdict = preflight.evaluate_core_headroom(_LIMIT, _LIMIT)
    assert verdict["under_buffer"] is True
    assert verdict["regressed"] is False
    assert verdict["blocked"] is False


def test_evaluate_core_headroom_allows_under_buffer_improvement() -> None:
    verdict = preflight.evaluate_core_headroom(_LIMIT - 1, _LIMIT)
    assert verdict["under_buffer"] is True
    assert verdict["blocked"] is False


def test_evaluate_core_headroom_blocks_brand_new_surface_without_buffer() -> None:
    verdict = preflight.evaluate_core_headroom(_LIMIT - (_BUFFER - 2), None)
    assert verdict["base_remaining"] is None
    assert verdict["blocked"] is True


def test_evaluate_core_headroom_allows_healthy_change() -> None:
    verdict = preflight.evaluate_core_headroom(_LIMIT - (_BUFFER + 2), _LIMIT - (_BUFFER + 6))
    assert verdict["under_buffer"] is False
    assert verdict["blocked"] is False


def _git_stage(repo: Path, rel: str, content: str) -> None:
    (repo / rel).write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=repo, check=True, capture_output=True, text=True)


def _git_commit_skill(repo: Path, rel: str, content: str) -> None:
    from .repo_shapes import install_committed_repo

    install_committed_repo(repo, {rel: content}, message="base")


def test_scan_changed_skill_md_blocks_new_drop_below_buffer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT - (_BUFFER + 4)))
    _git_stage(repo, rel, _skill_with_core(_LIMIT))

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["blocked"] == [rel]


def test_scan_changed_skill_md_judges_staged_not_worktree(tmp_path: Path) -> None:
    # #319 honesty: the gate must judge what is being committed (the index), not a
    # working tree that was repaired after a bad version was staged.
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/demo/SKILL.md"
    healthy = _skill_with_core(_LIMIT - (_BUFFER + 4))
    _git_commit_skill(repo, rel, healthy)
    _git_stage(repo, rel, _skill_with_core(_LIMIT))  # stage the 0-headroom version
    (repo / rel).write_text(healthy, encoding="utf-8")  # repair only the working tree

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["blocked"] == [rel]


def test_scan_changed_skill_md_grandfathers_existing_under_buffer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/support/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT))
    # Reword a core line in place: still 0 remaining, not made worse.
    _git_stage(
        repo,
        rel,
        _skill_with_core(_LIMIT).replace("Core line 0", "Reworded core line"),
    )

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "ok"
    assert report["checked"][0]["base_remaining"] == 0


def test_scan_changed_skill_md_blocks_brand_new_skill_without_buffer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/fresh/SKILL.md"
    target = repo / rel
    target.parent.mkdir(parents=True)
    target.write_text(_skill_with_core(_LIMIT - (_BUFFER - 1)), encoding="utf-8")

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["checked"][0]["base_remaining"] is None


def test_scan_changed_skill_md_ignores_non_skill_core_paths(tmp_path: Path) -> None:
    """A non-core path in a mixed named set is dropped, not gated — but the set
    still has to ratchet something, or the verdict covers no scope at all (that
    all-dropped case is pinned in test_empty_scope_refusals.py)."""
    repo = tmp_path / "repo"
    rel = "skills/public/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT - (_BUFFER + 4)))
    (repo / "docs").mkdir()
    (repo / "docs" / "note.md").write_text("# Note\n", encoding="utf-8")

    report = preflight.scan_changed_skill_md(repo.resolve(), ["docs/note.md", rel])
    assert report["status"] == "ok"
    assert [row["path"] for row in report["checked"]] == [rel]


def test_changed_skill_md_cli_blocks_with_exit_one(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT - (_BUFFER + 4)))
    _git_stage(repo, rel, _skill_with_core(_LIMIT))

    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--changed-skill-md", rel],
    )
    assert preflight.main() == 1
    emitted = yaml.safe_load(capsys.readouterr().out)
    assert emitted["status"] == "blocked"
    assert emitted["blocked"] == [rel]
    assert "core_nonempty headroom buffer" in emitted["remedy"]


def test_changed_skill_md_cli_empty_list_is_ok(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--changed-skill-md"],
    )
    assert preflight.main() == 0


# --- pressure-exempt-section anti-abuse preflight ---


def test_pressure_exempt_findings_flags_overlong_and_prose() -> None:
    tokens = [f"- token-{index} <command>" for index in range(12)]
    text = "\n".join(
        [
            "# Demo",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            *tokens,
            "This is prose. It clearly runs two sentences.",
            "",
            "## Next",
            "",
            "- after",
        ]
    )
    findings = preflight.pressure_exempt_findings(text)
    # The prose line is a finding; the block being over its 12-line budget is NOT.
    # Overflow pays core density instead, so a long-but-token-shaped list is never
    # blocked by a rule whose own remediation says it merely costs density.
    assert any("multi-sentence prose" in finding for finding in findings)
    assert not any("budget" in finding for finding in findings)
    # 13 non-empty exempt lines against a 12-line budget: one line of overflow,
    # charged to core density.
    without_overflow = text.replace("- token-11 <command>\n", "")
    assert preflight._core_nonempty_lines(text) == preflight._core_nonempty_lines(without_overflow) + 1


def test_pressure_exempt_findings_empty_when_token_shaped() -> None:
    text = "\n".join(
        [
            "# Demo",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            "- ran-fail-deferred <command> <issue|anchor>",
            "",
            "## Next",
            "",
            "- after",
        ]
    )
    assert preflight.pressure_exempt_findings(text) == []


def test_payload_surfaces_exempt_section_block(tmp_path: Path) -> None:
    tokens = ["- token <command>", "One sentence here. And a second one follows."]
    skill_lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        "Use this when the repo needs a demo skill.",
        "",
        f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
        "",
        *tokens,
        "",
        "## References",
        "",
        "- `references/note.md`",
    ]
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=skill_lines)
    payload = preflight.build_report(repo.resolve(), str(skill_path), 0, False)
    assert payload["exempt_findings"]
    emitted = preflight.preflight_payload(payload)
    assert emitted["status"] == "blocked"
    assert any("multi-sentence prose" in finding for finding in emitted["exempt_findings"])
    assert emitted["remedy"] == preflight.EXEMPT_SECTION_REMEDIATION


def test_changed_payload_surfaces_exempt_findings() -> None:
    report = {
        "status": "blocked",
        "checked": [
            {
                "path": "skills/public/demo/SKILL.md",
                "blocked": True,
                "base_remaining": None,
                "new_remaining": 3,
                "buffer": 5,
                "exempt_findings": ["`## Closeout Vocabulary` line is multi-sentence prose"],
            }
        ],
    }
    payload = preflight.changed_payload(report)
    assert payload["status"] == "blocked"
    assert payload["checked"][0]["exempt_findings"] == [
        "`## Closeout Vocabulary` line is multi-sentence prose"
    ]
    assert payload["remedy"] == preflight.EXEMPT_SECTION_REMEDIATION


# --- S5 (2026-07-28 triage sweep): the exemption audited less than it exempted ---


def _prose_block(count: int) -> list[str]:
    return [f"Decision prose line {index}. It carries a second sentence." for index in range(count)]


def _skill_with_exempt_prose(section: str, *, repeat_heading: bool) -> str:
    lines = ["# Demo", "", "## Workflow", "", "Step one.", "Step two.", ""]
    if repeat_heading:
        lines += [f"## {section}", "", "- `Refresh kept:` tokens", ""]
    # 60 lines: past every exempt budget, and the sweep's own reproduction size.
    lines += [f"## {section}", "", *_prose_block(60), ""]
    return "\n".join(lines)


@pytest.mark.parametrize(
    ("section", "repeat_heading"),
    [
        # The sweep's own trigger: a SECOND `## Closeout Vocabulary` block was
        # exempt while only the first was audited.
        (preflight.CLOSEOUT_VOCAB_SECTION, True),
        # Cheaper bypass the row did not name: `## References` is exempt with no
        # audit at all, so one block was enough.
        ("References", False),
    ],
)
def test_exempt_section_prose_pays_density_and_is_reported(section: str, repeat_heading: bool) -> None:
    text = _skill_with_exempt_prose(section, repeat_heading=repeat_heading)
    core = preflight._core_nonempty_lines(text)

    # Before the repair both variants cost nothing: the prose was exempt and, for
    # a second block or a sibling heading, never audited either.
    core_without_the_block = preflight._core_nonempty_lines(
        "\n".join(["# Demo", "", "## Workflow", "", "Step one.", "Step two.", ""])
    )
    assert core >= core_without_the_block + 20, "prose past the exempt budget must pay density"


@pytest.mark.parametrize(
    ("section", "repeat_heading"),
    [(preflight.CLOSEOUT_VOCAB_SECTION, True), ("References", False)],
)
def test_exempt_section_prose_is_audited_in_every_block(section: str, repeat_heading: bool) -> None:
    findings = preflight.pressure_exempt_findings(
        _skill_with_exempt_prose(section, repeat_heading=repeat_heading)
    )
    # Every block of the heading is read, not just the first: the prose sits in the
    # SECOND `## Closeout Vocabulary` block in the repeat-heading case.
    assert any("multi-sentence prose" in finding for finding in findings)
    assert len(findings) >= 60


def test_exempt_budget_leaves_the_live_corpus_headroom() -> None:
    # Read the REAL corpus, not a generated fixture sized from the constant under
    # test: a fixture built from PRESSURE_EXEMPT_BUDGET passes for any budget value,
    # including one that would block every skill in the repo.
    skill_paths = sorted((ROOT / "skills").glob("*/*/SKILL.md"))
    assert len(skill_paths) >= 20, "corpus scan found no skills; the guard would be vacuous"
    observed: dict[str, int] = {}
    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        assert preflight.pressure_exempt_findings(text) == [], path
        _kept, blocks = preflight._density.split_pressure_exempt_sections(
            preflight._density.strip_frontmatter(text).splitlines()
        )
        for section, section_blocks in blocks.items():
            count = sum(1 for block in section_blocks for line in block if line.strip())
            observed[section] = max(observed.get(section, 0), count)
    for section, count in observed.items():
        budget = preflight.PRESSURE_EXEMPT_BUDGET[section]
        assert count <= budget, (
            f"{section}: live corpus already spends {count} exempt lines against a "
            f"budget of {budget}"
        )
        # Ratchet the budget from ABOVE too. A budget far over observed usage is
        # the hatch in its original form: exempt lines nobody is asking for.
        assert budget <= count + 6, (
            f"{section}: budget {budget} sits far above the observed corpus maximum "
            f"{count}; the slack is free unaudited prose"
        )


def test_ordered_lists_and_abbreviations_are_not_multi_sentence_prose() -> None:
    # Both shapes match the raw sentence-boundary regex but are ordinary reference
    # entries; the audit blocks, so a false positive is a blocked legitimate skill.
    text = "\n".join(
        [
            "# Demo",
            "",
            "## References",
            "",
            "1. Read the ladder before deciding",
            "- `references/hosts.md` - per-host defaults, e.g. Codex hosts",
            "",
        ]
    )
    assert preflight.pressure_exempt_findings(text) == []


def test_fenced_exempt_heading_does_not_open_a_real_exempt_block() -> None:
    # A skill teaching SKILL.md shape carries a literal `## References` inside a
    # fence; treating it as a heading would exempt everything after it for free.
    text = "\n".join(
        [
            "# Demo",
            "",
            "## Workflow",
            "",
            "```markdown",
            "## References",
            "```",
            *[f"Decision prose line {index}. It runs two sentences." for index in range(20)],
            "",
        ]
    )
    assert preflight._core_nonempty_lines(text) >= 20


def test_fenced_lines_still_pay_core_density() -> None:
    # Suppressing heading detection inside a fence must not excuse the fenced lines
    # from the count: that would re-open the free-prose hatch one layer down.
    base = ["# Demo", "", "## Workflow", "", "Step one.", ""]
    fenced = base + ["```bash", *[f"command_{index} --flag" for index in range(10)], "```", ""]
    assert preflight._core_nonempty_lines("\n".join(fenced)) == preflight._core_nonempty_lines(
        "\n".join(base)
    ) + 12  # 10 commands + the two fence markers


def test_exempt_budget_keys_match_the_exempt_sections() -> None:
    # A heading added to one constant and not the other silently gets a budget of 0
    # (fail-safe at runtime) and a KeyError in the corpus guard.
    assert set(preflight.PRESSURE_EXEMPT_H2_SECTIONS) == set(preflight.PRESSURE_EXEMPT_BUDGET)


def test_changed_skill_md_scan_blocks_on_exempt_section_prose(tmp_path: Path) -> None:
    # The enforcement point for a staged SKILL.md, driven end to end rather than
    # through a hand-built report dict: a formatting-only test would still pass if
    # the scan stopped consulting the audit at all.
    repo = tmp_path / "repo"
    skill_path = _write_skill(
        repo,
        skill_lines=[
            "---",
            "name: demo",
            'description: "Demo skill."',
            "---",
            "",
            "# Demo",
            "",
            "Use this when the repo needs a demo skill.",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            "- ran-fail-deferred <command> <issue|anchor>",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            "This block is prose. It teaches when to act rather than what to emit.",
        ],
    )
    rel = skill_path.resolve().relative_to(repo.resolve()).as_posix()

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["blocked"] == [rel]
    assert any(
        "multi-sentence prose" in finding
        for row in report["checked"]
        for finding in row["exempt_findings"]
    )


def test_fenced_example_inside_an_exempt_block_is_not_audited_as_prose() -> None:
    # `## Closeout Vocabulary` exists to carry the literal shape a run must emit;
    # blocking a skill for quoting a two-sentence commit message would punish the
    # section for doing its job. The lines still pay density.
    text = "\n".join(
        [
            "# Demo",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            "```",
            "Fixes #123. Verified by scripts/run-quality.sh.",
            "```",
            "",
        ]
    )

    assert preflight.pressure_exempt_findings(text) == []


def test_fenced_lines_in_an_exempt_block_pay_density_even_within_budget() -> None:
    # The audit excuses fenced lines, so if the budget also excused them a fence
    # would be a window that is both uncharged and unread. 10 fenced lines sit
    # under every budget and must still cost 12 (10 + the two fence markers).
    base = ["# Demo", "", f"## {preflight.CLOSEOUT_VOCAB_SECTION}", "", "- token <command>", ""]
    fenced = base + ["```", *[f"Example line {index}. Second sentence." for index in range(10)], "```", ""]

    assert preflight.pressure_exempt_findings("\n".join(fenced)) == []
    assert preflight._core_nonempty_lines("\n".join(fenced)) == preflight._core_nonempty_lines(
        "\n".join(base)
    ) + 12


def test_tilde_fenced_example_inside_an_exempt_block_is_not_audited_as_prose() -> None:
    text = "\n".join(
        [
            "# Demo",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            "~~~text",
            "Fixes #123. Verified by scripts/run-quality.sh.",
            "~~~",
            "",
        ]
    )

    assert preflight.pressure_exempt_findings(text) == []


def test_exempt_section_block_carries_its_own_remediation_not_the_headroom_one() -> None:
    # The gate has two blocking causes with opposite remedies. Carrying the
    # headroom paragraph for an exempt-section block told an author with 158 lines
    # of headroom to split a concept out — an action that does not clear the block.
    report = {
        "status": "blocked",
        "checked": [
            {
                "path": "skills/public/demo/SKILL.md",
                "blocked": True,
                "base_remaining": None,
                "new_remaining": 158,
                "buffer": 4,
                "exempt_findings": ["`## References` line is multi-sentence prose, not a token: '...'"],
            }
        ],
    }

    remedy = preflight.changed_payload(report)["remedy"]

    assert "token-shaped" in remedy
    assert "dropped below the core_nonempty headroom buffer" not in remedy


def test_headroom_block_still_carries_the_headroom_remediation() -> None:
    report = {
        "status": "blocked",
        "checked": [
            {
                "path": "skills/public/demo/SKILL.md",
                "blocked": True,
                "base_remaining": 5,
                "new_remaining": 3,
                "buffer": 4,
                "exempt_findings": [],
            }
        ],
    }

    remedy = preflight.changed_payload(report)["remedy"]

    assert "dropped below the core_nonempty headroom buffer" in remedy
    assert "token-shaped" not in remedy
