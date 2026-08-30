from __future__ import annotations

from pathlib import Path

import yaml

from .seeding_support import load_module
from .support import ROOT, run_script, seed_runtime_budget_repo

SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"
check_runtime_budget = load_module("check_runtime_budget_under_test", ROOT / SCRIPT)


def test_runtime_budget_gate_no_budgets_passes(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets=None, signals=None)
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--detail",
        "--runtime-profile",
        "default",
        real_process=True,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["budgets_configured"] == 0
    assert payload["runtime_profile"] == "default"
    assert payload["violations"] == []
    assert [finding["type"] for finding in payload["runtime_visibility_findings"]] == [
        "runtime_visibility_missing_budgets",
        "runtime_visibility_missing_startup_probes",
    ]

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "WEAK  runtime_visibility_missing_budgets" in plain_result.stdout


def test_runtime_budget_summary_yaml_is_structured(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets=None, signals=None)
    args = ("--repo-root", str(repo), "--runtime-profile", "default", "--summary")
    yaml_result = run_script(SCRIPT, *args)
    assert yaml_result.returncode == 0
    assert yaml.safe_load(yaml_result.stdout)["budgets_configured"] == 0


def test_runtime_budget_summary_bounds_diagnostic_lists() -> None:
    payload = check_runtime_budget.summarize(
        {
            "checked": [],
            "violations": list(range(12)),
            "latest_spikes": list(range(12)),
            "profile_config_errors": list(range(12)),
            "runtime_visibility_findings": list(range(12)),
        }
    )

    for key in (
        "violations",
        "latest_spikes",
        "profile_config_errors",
        "runtime_visibility_findings",
    ):
        assert payload[f"{key}_count"] == 12
        assert len(payload[f"{key}_sample"]) == 10
        assert payload[f"{key}_truncated"] is True


def test_runtime_budget_gate_reports_explicit_empty_runtime_fields(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets=None, signals=None, explicit_empty_budgets=True, startup_probes=[])

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [finding["type"] for finding in payload["runtime_visibility_findings"]] == [
        "runtime_visibility_missing_budgets",
        "runtime_visibility_missing_startup_probes",
    ]


def test_runtime_budget_gate_reports_empty_selected_profile_budget(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets=None,
        budget_profiles={"ci": {"budgets": {}}},
        signals={"profiles": {"ci": {"commands": {}}}},
        startup_probes=[],
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "ci")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["budgets_configured"] == 0
    assert payload["runtime_visibility_findings"][0]["type"] == "runtime_visibility_missing_budgets"


def test_runtime_budget_gate_has_no_visibility_findings_when_budget_and_probe_exist(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 22000},
        signals={"commands": {"pytest": {"latest": {"elapsed_ms": 15000, "status": "pass"}}}},
        startup_probes=[
            {
                "label": "cli-version",
                "command": ["python3", "-c", "print('ok')"],
                "class": "standing",
                "startup_mode": "warm",
                "surface": "direct",
                "samples": 1,
            }
        ],
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["runtime_visibility_findings"] == []


def test_runtime_budget_gate_passes_when_within_budget(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 15000, "status": "pass"}}}}
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["violations"] == []
    assert payload["latest_spikes"] == []
    assert payload["checked"][0] == {
        "label": "pytest",
        "budget_ms": 22000,
        "latest_elapsed_ms": 15000,
        "median_recent_elapsed_ms": 15000,
        "max_recent_elapsed_ms": None,
        "ewma_advisory_elapsed_ms": None,
        "ewma_alpha": None,
        "ewma_samples": None,
        "status": "ok",
    }


def test_runtime_budget_gate_fails_when_over_budget(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 30000, "status": "pass"}}}}
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["violations"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "median_recent_elapsed_ms": 30000,
            "latest_elapsed_ms": 30000,
        }
    ]
    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 1
    assert "exceeded" in plain_result.stderr.lower()


def test_runtime_budget_gate_consumes_samples_from_explicit_external_state_root(
    tmp_path: Path,
) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=None)
    state_root = tmp_path / "task-result" / "runtime" / "quality"
    state_root.mkdir(parents=True)
    (state_root / "runtime-signals.json").write_text(
        '{"commands":{"pytest":{"latest":{"elapsed_ms":999999,"status":"pass"},'
        '"median_recent_elapsed_ms":999999}}}\n',
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--detail",
        "--runtime-profile",
        "default",
        "--state-root",
        str(state_root),
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["signals_path"] == str(state_root / "runtime-signals.json")
    assert payload["violations"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "median_recent_elapsed_ms": 999999,
            "latest_elapsed_ms": 999999,
        }
    ]
    assert not (repo / ".charness" / "quality" / "runtime-signals.json").exists()
    sized = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--runtime-profile",
        "default",
        "--suggest-budgets",
        "--state-root",
        str(state_root),
    )
    assert sized.returncode == 0, sized.stderr
    assert "pytest: 1400000  # n=1, worst 999999ms" in sized.stdout


def test_runtime_budget_gate_can_report_over_budget_as_advisory(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 30000, "status": "pass"}}}}
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--detail",
        "--runtime-profile",
        "default",
        "--advisory",
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["violations"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "median_recent_elapsed_ms": 30000,
            "latest_elapsed_ms": 30000,
        }
    ]
    assert "ADVISORY: runtime budget exceeded" in result.stderr


def test_runtime_budget_advisory_does_not_hide_profile_configuration_errors(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 22000},
        budget_profiles={"ci": {"budgets": {"pytest": 54000}}},
        signals={"profiles": {}},
    )

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--runtime-profile",
        "missing-profile",
        "--advisory",
    )

    assert result.returncode == 1
    assert "not configured in runtime_budget_profiles" in result.stderr


def test_runtime_budget_gate_reports_latest_spike_without_failing(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 30000, "status": "pass"},
                "median_recent_elapsed_ms": 15000,
                "max_recent_elapsed_ms": 30000,
            }
        }
    }
    smoothing = {
        "commands": {
            "pytest": {
                "samples": 4,
                "ewma_elapsed_ms": 18000,
                "alpha_last": 0.28,
                "advisory": True,
            }
        }
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals, smoothing=smoothing)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["violations"] == []
    assert payload["latest_spikes"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "latest_elapsed_ms": 30000,
            "median_recent_elapsed_ms": 15000,
        }
    ]
    assert payload["checked"][0]["status"] == "latest-spike"
    assert payload["checked"][0]["ewma_advisory_elapsed_ms"] == 18000.0
    assert payload["advisory_contracts"]["latest_spikes"] == {
        "severity": "advisory",
        "reason": "latest-only wall-clock spike; recent median remains the enforcement basis",
        "enforcement_basis": "recent median",
    }

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "LATEST-SPIKE" in plain_result.stdout
    assert "advisory: latest-only wall-clock spike; recent median remains the enforcement basis" in plain_result.stdout


def test_runtime_budget_gate_summary_carries_visibility_advisory_contract(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets=None, signals=None)

    result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default", "--summary")

    assert result.returncode == 0, result.stderr
    contract = yaml.safe_load(result.stdout)["advisory_contracts"]["runtime_visibility_findings"]
    assert contract == {
        "severity": "weak",
        "reason": "configuration review gap; render_runtime_summary.py is the final consumer for the recommended action",
        "final_consumer": "render_runtime_summary.py",
    }


def test_runtime_budget_gate_reports_advisory_ewma_without_enforcing_it(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 15000, "status": "pass"},
                "median_recent_elapsed_ms": 15000,
            }
        }
    }
    smoothing = {
        "commands": {
            "pytest": {
                "samples": 7,
                "ewma_elapsed_ms": 45000.5,
                "alpha_last": 0.35,
                "advisory": True,
            }
        }
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals, smoothing=smoothing)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["violations"] == []
    assert payload["checked"][0]["status"] == "ok"
    assert payload["checked"][0]["ewma_advisory_elapsed_ms"] == 45000.5
    assert payload["checked"][0]["ewma_alpha"] == 0.35
    assert payload["checked"][0]["ewma_samples"] == 7

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "ewma 45000.5ms advisory" in plain_result.stdout


def test_runtime_budget_gate_fails_on_recent_median_drift(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 25000, "status": "pass"},
                "median_recent_elapsed_ms": 23000,
                "max_recent_elapsed_ms": 30000,
            }
        }
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["violations"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "median_recent_elapsed_ms": 23000,
            "latest_elapsed_ms": 25000,
        }
    ]


def test_runtime_budget_gate_warns_on_missing_sample(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals={"commands": {}})
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["missing_samples"] == ["pytest"]
    assert payload["violations"] == []


def test_runtime_budget_gate_reports_top_runtime_hotspots(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 15000, "status": "pass"},
                "median_recent_elapsed_ms": 14000,
            },
            "check-cli-skill-surface": {
                "latest": {"elapsed_ms": 9000, "status": "pass"},
                "median_recent_elapsed_ms": 8000,
            },
            "check-markdown": {
                "latest": {"elapsed_ms": 7000, "status": "pass"},
                "median_recent_elapsed_ms": 6500,
            },
        }
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--detail",
        "--top-runtime-count",
        "2",
        "--runtime-profile",
        "default",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["runtime_hotspots"] == [
        {
            "label": "pytest",
            "latest_elapsed_ms": 15000,
            "median_recent_elapsed_ms": 14000,
            "max_recent_elapsed_ms": None,
            "budget_ms": 22000,
            "budgeted": True,
        },
        {
            "label": "check-cli-skill-surface",
            "latest_elapsed_ms": 9000,
            "median_recent_elapsed_ms": 8000,
            "max_recent_elapsed_ms": None,
            "budget_ms": None,
            "budgeted": False,
        },
    ]

    plain_result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--top-runtime-count",
        "2",
        "--runtime-profile",
        "default",
    )
    assert plain_result.returncode == 0, plain_result.stderr
    assert "Runtime hot spots:" in plain_result.stdout
    assert "check-cli-skill-surface" in plain_result.stdout
    assert "unbudgeted" in plain_result.stdout

    # The human hot-spot line is the only place the numbers behind the JSON reach an
    # operator reading a terminal, and the two budget shapes are a branch inside the
    # renderer. Asserting membership of a substring leaves both the numbers and the
    # branch unpinned — the #453 class. Pin the whole lines.
    hotspot_lines = [
        line for line in plain_result.stdout.splitlines() if line.startswith("HOTSPOT")
    ]
    assert hotspot_lines == [
        "HOTSPOT      pytest: latest 15000ms, median 14000ms (budget 22000ms)",
        "HOTSPOT      check-cli-skill-surface: latest 9000ms, median 8000ms (unbudgeted)",
    ], plain_result.stdout


def test_runtime_budget_gate_missing_sample_human_line_names_the_budget(
    tmp_path: Path,
) -> None:
    """A budget with no sample is the one entry that can never fail, so the WARN line
    is the only signal that the budget exists but is unmeasured. Its `--json` twin is
    asserted elsewhere; the human line carries the budget value an operator needs to
    decide whether the missing sample matters, and nothing pinned that text."""
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals={"commands": {}})
    result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr

    warn_lines = [line for line in result.stdout.splitlines() if line.startswith("WARN")]
    assert warn_lines == ["WARN  pytest: no sample yet (budget 22000ms)"], result.stdout
    # The no-sample entry short-circuits before the measured-entry renderer, so it
    # must not also emit a status line with placeholder numbers.
    assert "latest None" not in result.stdout


def test_runtime_budget_gate_excludes_stale_runtime_hotspots(tmp_path: Path) -> None:
    signals = {
        "updated_at": "2026-06-26T00:00:00",
        "commands": {
            "current-pytest": {
                "latest": {
                    "timestamp": "2026-06-26T00:00:00Z",
                    "elapsed_ms": 15000,
                    "status": "pass",
                },
                "median_recent_elapsed_ms": 14000,
            },
            "retired-check": {
                "latest": {
                    "timestamp": "2026-06-04T00:00:00",
                    "elapsed_ms": 90000,
                    "status": "pass",
                },
                "median_recent_elapsed_ms": 88000,
            },
        },
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"current-pytest": 22000}, signals=signals)

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--detail",
        "--top-runtime-count",
        "2",
        "--runtime-profile",
        "default",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [item["label"] for item in payload["runtime_hotspots"]] == ["current-pytest"]
    assert payload["stale_runtime_hotspots"][0]["label"] == "retired-check"
    assert payload["stale_runtime_hotspots"][0]["stale_days"] == 22

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "Stale runtime hot spots excluded:" in plain_result.stdout
    assert "STALE       retired-check: latest sample 2026-06-04T00:00:00 (22d old)" in plain_result.stdout


def test_runtime_budget_gate_keeps_invalid_timestamps_active(tmp_path: Path) -> None:
    signals = {
        "updated_at": "2026-06-26T00:00:00Z",
        "commands": {
            "unknown-age": {
                "latest": {
                    "timestamp": "not-a-timestamp",
                    "elapsed_ms": 30000,
                    "status": "pass",
                },
                "median_recent_elapsed_ms": 28000,
            },
        },
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"unknown-age": 50000}, signals=signals)

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [item["label"] for item in payload["runtime_hotspots"]] == ["unknown-age"]
    assert payload["stale_runtime_hotspots"] == []


def test_budget_slack_findings_names_budgets_that_can_no_longer_fail() -> None:
    """A runtime budget only ever moves one way on its own: a violation forces a
    raise, and nothing reports when the raise stopped being needed. This repo's
    `check-coverage` reached 55000ms against a 7835ms observed max that way. The
    slack advisory closes that loop — it is the only signal a budget emits other
    than "raise me"."""
    lib = check_runtime_budget.runtime_budget_lib
    checked = [
        # 7.0x — the real check-coverage case.
        {"label": "check-coverage", "budget_ms": 55000, "max_recent_elapsed_ms": 7835},
        # Under the factor: honest, must stay silent.
        {"label": "run-quality-read-only", "budget_ms": 90000, "max_recent_elapsed_ms": 69616},
        # Sub-threshold budget: jitter dominates, so a ratio here is noise.
        {"label": "charness-version", "budget_ms": 500, "max_recent_elapsed_ms": 20},
        # No sample yet: nothing to compare against.
        {"label": "never-run", "budget_ms": 30000, "max_recent_elapsed_ms": None},
    ]
    findings = lib.budget_slack_findings(checked)
    assert [f["label"] for f in findings] == ["check-coverage"]
    assert findings[0]["slack_ratio"] == 7.0
    # Pinned as a LITERAL, not as `int(7835 * HEADROOM)`. Restating production's own
    # expression asserts only that the plumbing runs: it passes for any headroom value
    # and for any change to the arithmetic, and it is why the advisory silently
    # proposed 10969 while `--suggest-budgets` proposed 11000 for the same input.
    # 1.4 * 7835 = 10969, rounded up to the 500ms step the sizing module owns.
    assert findings[0]["suggested_budget_ms"] == 11000


def test_budget_slack_advisory_renders_every_number_needed_to_act(tmp_path: Path) -> None:
    """The advisory's whole job is to be acted on — the handoff instruction is
    literally "act on SLACK lines from check_runtime_budget.py". An operator can
    only do that from the default human output, and only if the line carries all
    four numbers: which budget, what it is now, what the worst recent run actually
    took, and what to set it to. `budget_slack_findings` returning the right dict is
    not enough; the rendered line is the operator-facing surface, so it is what has
    to be pinned."""
    signals = {
        "commands": {
            "check-coverage": {
                "latest": {"elapsed_ms": 7835, "status": "pass"},
                "median_recent_elapsed_ms": 7000,
                "max_recent_elapsed_ms": 7835,
            }
        }
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"check-coverage": 55000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr

    assert "Budget slack (advisory: these budgets can no longer fail):" in result.stdout
    slack_lines = [line for line in result.stdout.splitlines() if line.startswith("SLACK")]
    assert len(slack_lines) == 1, result.stdout
    line = slack_lines[0]
    assert "check-coverage" in line
    assert "budget 55000ms" in line
    assert "worst recent 7835ms" in line
    assert "(7.0x)" in line
    lib = check_runtime_budget.runtime_budget_lib
    # Literal, for the same reason as above: the operator acts on this exact number,
    # and it must be the one `--suggest-budgets` would emit for the same sample.
    assert "consider 11000ms" in line

    # In-process witness for the same renderer. The subprocess assertions above only
    # reach `_render_slack` while the coverage harness's `COVERAGE_PROCESS_START` is
    # inherited by the child; a later edit that hands this `run_script` call an
    # explicit `env=` dict would silently stop measuring it. This call cannot drift
    # that way.
    assert lib._render_slack(
        {
            "label": "check-coverage",
            "budget_ms": 55000,
            "max_recent_elapsed_ms": 7835,
            "slack_ratio": 7.0,
            "suggested_budget_ms": 11000,
        }
    ) == line

    # An honest budget renders no advisory at all, so the section is a signal
    # rather than permanent furniture in the output.
    quiet_repo = seed_runtime_budget_repo(
        tmp_path / "quiet", budgets={"check-coverage": 12000}, signals=signals
    )
    quiet = run_script(SCRIPT, "--repo-root", str(quiet_repo), "--runtime-profile", "default")
    assert quiet.returncode == 0, quiet.stderr
    assert "SLACK" not in quiet.stdout
    assert "Budget slack" not in quiet.stdout


def test_budget_slack_advisory_never_changes_exit_code(tmp_path: Path) -> None:
    """Retuning a budget is reversible work, so the advisory forces the question
    and leaves the judgment to the operator (north star P1/P5). It must never fail
    the gate on its own."""
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 100000},
        signals={
            "commands": {
                "pytest": {
                    "latest": {"elapsed_ms": 1000, "status": "pass"},
                    "median_recent_elapsed_ms": 1000,
                    "max_recent_elapsed_ms": 1200,
                }
            }
        },
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    slack = payload["budget_slack_findings"]
    assert [f["label"] for f in slack] == ["pytest"]
    assert payload["violations"] == []


def test_suggest_budgets_emits_paste_ready_block_for_unconfigured_profile(tmp_path: Path) -> None:
    """The way out of a `not configured in runtime_budget_profiles` block is derivable.

    A profile with samples but no budgets hard-blocks the gate, and the only fix is a
    budgets block whose every value has to be read out of runtime-signals.json by
    hand -- ~18 labels, which is how the aarch64 profile came to ship eight bars
    below already-observed runs. The samples that block the gate are the same samples
    a bar should be drawn from, so the gate derives the block instead of describing it.
    """
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets=None,
        budget_profiles={"ci": {"budgets": {"pytest": 500}}},
        signals={
            "profiles": {
                "local-linux-x86_64-4cpu": {
                    "commands": {
                        "pytest": {
                            "samples": 3,
                            "latest": {"elapsed_ms": 9000},
                            "max_recent_elapsed_ms": 10000,
                        },
                        "ruff": {"samples": 3, "latest": {"elapsed_ms": 300}, "max_recent_elapsed_ms": 320},
                        # Recorded exactly once, so `max_recent_elapsed_ms` never got
                        # written. Without the `latest` fallback this label silently
                        # drops out of the block instead of getting a bar.
                        "specdown": {"latest": {"elapsed_ms": 5000}},
                        "never-ran": {"max_recent_elapsed_ms": None},
                    }
                }
            }
        },
    )

    blocked = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "local-linux-x86_64-4cpu")
    assert blocked.returncode == 1
    # The pointer names the profile that just failed. Without it, an operator paste
    # re-derives from the MACHINE and files a wrong-hardware block under this heading.
    assert "--runtime-profile local-linux-x86_64-4cpu --suggest-budgets" in blocked.stderr

    suggested = run_script(
        SCRIPT, "--repo-root", str(repo), "--runtime-profile", "local-linux-x86_64-4cpu", "--suggest-budgets"
    )
    assert suggested.returncode == 0, suggested.stderr
    block = yaml.safe_load(suggested.stdout)
    # 1.4x the worst observed run, rounded up to a legible step: a bar that absorbs
    # variance and still trips a 2x regression. `specdown` is present only because the
    # single-sample fallback fired (1.4 * 5000 = 7000).
    assert block == {
        "runtime_budget_profiles": {
            "local-linux-x86_64-4cpu": {"budgets": {"pytest": 14000, "ruff": 500, "specdown": 7000}},
        }
    }
    # A label with no usable sample gets no bar: an invented number is worse than none.
    assert "never-ran" not in suggested.stdout
    # Evidence DEPTH travels with each number. A bar from one sample and a bar from
    # twenty read identically once committed, and the 3x slack advisory can never
    # tell them apart afterwards.
    assert "pytest: 14000  # n=3, worst 10000ms" in suggested.stdout
    assert "specdown: 7000  # n=1, worst 5000ms" in suggested.stdout
    assert "THIN EVIDENCE (n<3), size these by judgment: specdown" in suggested.stdout
    # Provenance is the source, not the profile id: a `command_timing_log` with no
    # `profile` field matches every profile, so the heading alone can mislead.
    assert "from 3 label(s) in runtime-signals.json" in suggested.stdout


def test_suggest_budgets_source_is_a_token_matching_the_enforcement_report() -> None:
    """The two halves of the sizing/enforcement seam must not name the same fact in
    two vocabularies. `evaluate` already reports a `commands_source` token, so sizing
    returns the same tokens and keeps the sentence fragment in the renderer — a caller
    that wants to refuse a timing-log-derived block compares a token, not prose."""
    sizing = check_runtime_budget.runtime_budget_sizing_lib
    enforcement_tokens = {"runtime_signals", "command_timing_log", "none"}

    assert set(sizing.COMMANDS_SOURCE_LABELS) == enforcement_tokens
    rendered = sizing.format_budget_suggestion(
        "local-test",
        {"pytest": {"budget_ms": 1000, "worst_observed_ms": 700, "samples": 4}},
        commands_source="command_timing_log",
    )
    assert "in the repo-declared command_timing_log at" in rendered
    # The raw token never reaches the operator-facing header.
    assert "command_timing_log at" not in rendered.replace("the repo-declared command_timing_log at", "")


def test_suggest_budgets_refuses_machine_readable_output_modes(tmp_path: Path) -> None:
    """The comment-carrying fragment refuses the ordinary report modes."""
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 1000}, signals=None)

    for mode in ("--summary", "--detail"):
        result = run_script(SCRIPT, "--repo-root", str(repo), "--suggest-budgets", mode)
        assert result.returncode == 2, f"{mode}: {result.stdout}"
        assert "cannot be combined" in result.stderr


def test_suggest_budgets_reports_when_the_profile_has_no_samples(tmp_path: Path) -> None:
    """No samples means no derivation. Say so instead of emitting an empty block."""
    repo = seed_runtime_budget_repo(tmp_path, budgets=None, signals=None)

    result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "ci", "--suggest-budgets")

    assert result.returncode == 1
    assert "no recorded samples" in result.stderr


def test_recorder_does_not_define_a_second_profile_derivation() -> None:
    """The profile id is a contract between writer and reader: whatever the recorder
    stamps is what the budget gate looks budgets up under. A second copy could drift
    and silently point them at different machines -- which is exactly what happened
    when the affinity fix had to be applied twice, in lockstep, to stay consistent.
    """
    import inspect

    from scripts import record_quality_runtime

    source = Path(inspect.getsourcefile(record_quality_runtime.machine_runtime_profile) or "")
    assert source.name == "runtime_profile_lib.py", (
        "record_quality_runtime must consume the quality skill's profile derivation, "
        f"not define its own (resolved to {source})"
    )
    assert "def machine_runtime_profile" not in Path(record_quality_runtime.__file__).read_text(encoding="utf-8")
