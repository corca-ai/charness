from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_current_pointer_freshness import (
    ValidationError,
    _load_catalog_sanitizer,
    validate_capability_catalog_integration_claims,
)

from .support import run_script


def write_runtime_signals(
    repo: Path, *, pytest_latest: int = 37638, pytest_median: int = 36544
) -> None:
    runtime_dir = repo / ".charness" / "quality"
    runtime_dir.mkdir(parents=True)
    (runtime_dir / "runtime-signals.json").write_text(
        (
            "{\n"
            '  "commands": {\n'
            '    "pytest": {\n'
            f'      "latest": {{"elapsed_ms": {pytest_latest}, "status": "pass"}},\n'
            f'      "median_recent_elapsed_ms": {pytest_median}\n'
            "    }\n"
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )


def seed_repo(
    tmp_path: Path,
    *,
    quality_text: str = "# Quality Review\n\n## Missing\n\n- Freshness validator exists; extend concrete claim coverage.\n",
    queued: bool = True,
) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / "plugins" / "charness" / ".codex-plugin").mkdir(parents=True)
    (repo / "plugins" / "charness" / ".claude-plugin").mkdir(parents=True)
    (repo / "skills" / "public" / "quality" / "scripts").mkdir(parents=True)
    queue_line = (
        'queue_selected "validate-current-pointer-freshness" '
        'python3 scripts/validate_current_pointer_freshness.py --repo-root "$REPO_ROOT"\n'
        if queued
        else ""
    )
    (repo / "scripts" / "run-quality.sh").write_text(queue_line, encoding="utf-8")
    if queued:
        (repo / ".agents" / "quality-gates.yaml").write_text(
            "schema: charness/quality-gates/v1\n"
            "phases:\n"
            "  - id: main\n"
            "    isolation: concurrent\n"
            "    fail_fast: false\n"
            "    gates:\n"
            "      - label: validate-current-pointer-freshness\n"
            "        command:\n"
            "          - python3\n"
            "          - scripts/validate_current_pointer_freshness.py\n"
            "          - --repo-root\n"
            "          - $REPO_ROOT\n"
            "        lane: standard\n",
            encoding="utf-8",
        )
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        quality_text, encoding="utf-8"
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        "# Release Surface Check\n\n## Current Version\n\n- target version: `1.2.3`\n",
        encoding="utf-8",
    )
    for relative_path in (
        "packaging/charness.json",
        "plugins/charness/.codex-plugin/plugin.json",
        "plugins/charness/.claude-plugin/plugin.json",
    ):
        (repo / relative_path).write_text('{"version": "1.2.3"}\n', encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "runtime_budgets:\n  pytest: 45000\n",
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text(".charness/quality/runtime-smoothing.json\n", encoding="utf-8")
    (repo / "scripts" / "record_quality_runtime.py").write_text(
        "\n".join(
            [
                'SMOOTHING_FILENAME = "runtime-smoothing.json"',
                "SMOOTHING_ALPHA_BASE = 0.35",
                "SMOOTHING_WARMUP_N = 5",
                '"advisory": True',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "check_coverage.py").write_text("# coverage\n", encoding="utf-8")
    (repo / "scripts" / "check_test_production_ratio.py").write_text("# ratio\n", encoding="utf-8")
    (repo / "skills" / "public" / "quality" / "scripts" / "check_runtime_budget.py").write_text(
        "\n".join(
            [
                'SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"',
                "ewma_advisory_elapsed_ms",
                "ewma {entry['ewma_advisory_elapsed_ms']:.1f}ms advisory",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def test_current_pointer_freshness_accepts_queued_non_stale_pointers(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    result = run_script(
        "scripts/validate_current_pointer_freshness.py",
        "--repo-root",
        str(repo),
        real_process=True,
    )
    assert result.returncode == 0
    assert "Validated rolling current-pointer freshness claims." in result.stdout


def test_current_pointer_freshness_requires_run_quality_queue(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, queued=False)
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must queue `validate-current-pointer-freshness`" in result.stderr


def test_current_pointer_freshness_rejects_stale_quality_missing_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Missing\n\n"
            "- No deterministic freshness check yet cross-validates current pointers.\n"
        ),
    )
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "charness-artifacts/quality/latest.md" in result.stderr
    assert "No deterministic freshness check yet" in result.stderr


def test_current_pointer_freshness_rejects_missing_command_script_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Commands Run\n\n"
            "- `python3 scripts/missing_inventory.py --repo-root .`\n"
        ),
    )
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "quality pointer command claims are stale" in result.stderr
    assert "scripts/missing_inventory.py" in result.stderr


def test_current_pointer_freshness_rejects_runtime_smoothing_claim_drift(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Current Gates\n\n"
            "- Runtime EWMA is advisory in `.charness/quality/runtime-smoothing.json`.\n"
        ),
    )
    (repo / ".gitignore").write_text("", encoding="utf-8")
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "runtime smoothing claim is stale" in result.stderr
    assert ".charness/quality/runtime-smoothing.json" in result.stderr


def test_current_pointer_freshness_accepts_matching_runtime_signal_claims(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Runtime Signals\n\n"
            "- runtime hot spots: latest full gate had `pytest` `37.6s`.\n"
            "- Budgeted phases: `pytest` median `36.5s / 45.0s`.\n"
        ),
    )
    write_runtime_signals(repo)
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_current_pointer_freshness_ignores_volatile_runtime_signal_numbers(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        quality_text=(
            "# Quality Review\n\n"
            "## Runtime Signals\n\n"
            "- runtime hot spots: latest full gate had `pytest` `99.9s`.\n"
            "- Budgeted phases: `pytest` median `99.9s / 45.0s`.\n"
        ),
    )
    write_runtime_signals(repo)
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_current_pointer_freshness_rejects_stale_release_version_claim(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    (repo / "packaging" / "charness.json").write_text('{"version": "1.2.4"}\n', encoding="utf-8")
    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "release pointer version claim is stale" in result.stderr
    assert "packaging/charness.json" in result.stderr


def test_current_pointer_freshness_rejects_stale_capability_catalog_integration_snapshot(
    tmp_path: Path,
) -> None:
    repo = seed_repo(tmp_path)
    integrations = repo / "integrations" / "tools"
    integrations.mkdir(parents=True)
    (integrations / "demo.json").write_text(
        json.dumps(
            {
                "tool_id": "demo",
                "kind": "external_binary_with_skill",
                "intent_triggers": ["prompt behavior regression"],
                "supports_public_skills": ["quality"],
                "recommendation_role": "validation",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    inventory_dir = repo / "charness-artifacts" / "capability-catalog"
    inventory_dir.mkdir(parents=True)
    (inventory_dir / "latest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "artifact_kind": "capability-catalog",
                "generated_at": "2026-04-24T00:00:00Z",
                "repo": "repo",
                "inventory": {
                    "integrations": [
                        {
                            "path": "integrations/tools/demo.json",
                            "intent_triggers": ["review"],
                            "supports_public_skills": ["quality"],
                            "recommendation_role": "validation",
                        }
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "capability catalog pointer is stale" in result.stderr
    assert "integrations/tools/demo.json" in result.stderr

    with pytest.raises(ValidationError, match="capability catalog pointer is stale"):
        validate_capability_catalog_integration_claims(repo)

    (inventory_dir / "latest.json").write_text(
        json.dumps({"schema_version": 1, "inventory": {"integrations": []}}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="capability catalog pointer is stale"):
        validate_capability_catalog_integration_claims(repo)


def test_current_pointer_freshness_loads_catalog_sanitizer_in_process() -> None:
    alias_path, sanitize = _load_catalog_sanitizer(Path(__file__).resolve().parents[2])
    assert alias_path is not None
    assert sanitize is not None
    assert (
        alias_path("integrations/tools/github-gh.json") == "integrations/tools/github-worker.json"
    )


def _write_release_pointer(repo: Path, body: str) -> None:
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(
        f"# Release Surface Check\n\n## Current Version\n\n{body}", encoding="utf-8"
    )


def test_release_version_claim_is_checked_in_every_rendering(tmp_path: Path) -> None:
    """D5 regression: the claim pattern required backticks and a leading `- `,
    so re-rendering the SAME claim as bold silently disabled the one standing
    cross-check between the release pointer and the shipped manifests.

    Each rendering below is genuinely stale against the seeded 1.2.3 manifests
    and must block."""
    for label, body in (
        ("backticked", "- target version: `9.9.9`\n"),
        ("bold", "- target version: **9.9.9**\n"),
        ("bare", "- target version: 9.9.9\n"),
        ("no list marker", "target version: `9.9.9`\n"),
    ):
        repo = seed_repo(tmp_path / label)
        _write_release_pointer(repo, body)
        result = run_script(
            "scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo)
        )
        assert result.returncode == 1, (label, result.stdout)
        assert "release pointer version claim is stale" in result.stderr, label


def test_release_version_claim_absent_from_an_existing_pointer_is_refused(tmp_path: Path) -> None:
    """An existing release pointer carrying no parseable claim is an
    UNESTABLISHED scope, not a satisfied one. Returning silently made a
    reformatted or dropped claim indistinguishable from a verified one."""
    repo = seed_repo(tmp_path)
    _write_release_pointer(repo, "nothing resembling a version claim here\n")

    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "no parseable `target version:` claim" in result.stderr


def test_release_version_decoy_claim_cannot_shadow_a_stale_one(tmp_path: Path) -> None:
    """`re.search` took the FIRST match, so a decoy line agreeing with the
    manifests shadowed a genuinely stale claim below it and the comparison never
    ran on the real one. Disagreeing claims are now refused outright."""
    repo = seed_repo(tmp_path)
    _write_release_pointer(
        repo, "- target version: `1.2.3`\n\nthe real one:\n\n- target version: `9.9.9`\n"
    )

    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "disagreeing target-version claims" in result.stderr


def test_release_version_claim_matching_the_manifests_still_passes(tmp_path: Path) -> None:
    """Falsifiable counterpart: a current claim passes in any rendering, and a
    claim repeated identically is not a disagreement."""
    for label, body in (
        ("backticked", "- target version: `1.2.3`\n"),
        ("bold", "- target version: **1.2.3**\n"),
        ("repeated identically", "- target version: `1.2.3`\nlater\n- target version: `1.2.3`\n"),
    ):
        repo = seed_repo(tmp_path / f"ok-{label}")
        _write_release_pointer(repo, body)
        result = run_script(
            "scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo)
        )
        assert result.returncode == 0, (label, result.stderr)


def test_release_version_claim_survives_nested_markup_and_placeholders(tmp_path: Path) -> None:
    """Second-round D5 regression, all confirmed by execution.

    The three renderings NEST, and the capture kept the residue: `**\\`1.2.3\\`**`
    captured the backticks inside the bold group and compared them literally,
    turning a current pointer into a false "stale". A trailing period did the
    same. And `target version: TBD` was compared as if `TBD` were a version,
    reporting "manifest is 1.2.3, pointer claims TBD" — the wrong diagnosis for
    the same condition the absent-claim branch calls unestablished."""
    for label, body in (
        ("bold wrapping backticks", "- target version: **`1.2.3`**\n"),
        ("backticks wrapping bold", "- target version: `**1.2.3**`\n"),
        ("trailing period", "- target version: 1.2.3.\n"),
        (
            "previous and target siblings",
            "- previous version: `1.2.2`\n- target version: `1.2.3`\n",
        ),
    ):
        repo = seed_repo(tmp_path / f"ok-{label}")
        _write_release_pointer(repo, body)
        result = run_script(
            "scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo)
        )
        assert result.returncode == 0, (label, result.stderr)

    for label, body in (("TBD", "- target version: TBD\n"), ("N/A", "- target version: N/A\n")):
        repo = seed_repo(tmp_path / f"placeholder-{label}")
        _write_release_pointer(repo, body)
        result = run_script(
            "scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo)
        )
        assert result.returncode == 1, label
        assert "no parseable `target version:` claim" in result.stderr, label
        assert "is stale" not in result.stderr, label


def test_release_version_claim_ignores_claim_shaped_lines_inside_a_fence(tmp_path: Path) -> None:
    """The release artifact verbatim-embeds captured tool output. A claim-shaped
    line in a fenced block is quoted text, not the artifact's own assertion — and
    with disagreement now refused, treating one as a claim would hard-fail the
    freshness gate on a correct pointer."""
    repo = seed_repo(tmp_path)
    _write_release_pointer(repo, "- target version: `1.2.3`\n\n```\ntarget version: 9.9.9\n```\n")

    result = run_script("scripts/validate_current_pointer_freshness.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_capability_catalog_claims_refuse_an_unestablishable_scope(tmp_path: Path) -> None:
    """D10 regression: two silent early-returns.

    With a genuinely stale claim in place, deleting the integrations directory or
    corrupting the inventory shape flipped BLOCK to PASS — the comparison never
    ran and the absence of a complaint read as freshness. A missing directory is
    only benign when the catalog claims no integrations."""
    from scripts.validate_current_pointer_freshness import (
        CAPABILITY_CATALOG,
        INTEGRATIONS_DIR,
        ValidationError,
        validate_capability_catalog_integration_claims,
    )

    repo = tmp_path / "repo"
    catalog = repo / CAPABILITY_CATALOG
    catalog.parent.mkdir(parents=True)

    # Inventory present but not an object: the catalog exists and was never read.
    catalog.write_text(
        json.dumps({"schema_version": 1, "inventory": "not-a-dict"}), encoding="utf-8"
    )
    with pytest.raises(ValidationError, match="not an object"):
        validate_capability_catalog_integration_claims(repo)

    # Claims integrations, but the tree they describe is gone.
    catalog.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "inventory": {"integrations": [{"path": "integrations/tools/tool.json"}]},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="does not exist"):
        validate_capability_catalog_integration_claims(repo)

    # Falsifiable counterpart: no claims and no directory is genuinely
    # not-configured, and must stay a pass.
    catalog.write_text(
        json.dumps({"schema_version": 1, "inventory": {"integrations": []}}), encoding="utf-8"
    )
    validate_capability_catalog_integration_claims(repo)

    # And a repo with no catalog at all is still exempt.
    catalog.unlink()
    assert not (repo / INTEGRATIONS_DIR).is_dir()
    validate_capability_catalog_integration_claims(repo)


def test_capability_catalog_claims_name_unreadable_and_unknown_schema_apart(tmp_path: Path) -> None:
    """Two refusals that a shape complaint would have mis-diagnosed.

    `_load_json` swallows OSError/JSONDecodeError and returns `{}`, so a
    truncated catalog reached the shape check and was reported as "inventory is
    NoneType" — the right refusal with the wrong remedy. A catalog written by a
    schema this validator does not read is a third case again: nothing was
    compared, and saying "malformed v1" sends the reader to fix the wrong file.
    """
    from scripts.validate_current_pointer_freshness import CAPABILITY_CATALOG

    repo = tmp_path / "repo"
    catalog = repo / CAPABILITY_CATALOG
    catalog.parent.mkdir(parents=True)

    catalog.write_text('{"schema_version": 1, "inven', encoding="utf-8")
    with pytest.raises(ValidationError, match="could not be read as JSON"):
        validate_capability_catalog_integration_claims(repo)

    catalog.write_text(json.dumps({"schema_version": 2, "inventory": {}}), encoding="utf-8")
    with pytest.raises(ValidationError, match="does not read"):
        validate_capability_catalog_integration_claims(repo)
