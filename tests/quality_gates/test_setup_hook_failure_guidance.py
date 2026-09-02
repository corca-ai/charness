from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts import setup_hook_failure_visibility_lib as visibility
from scripts.setup_hook_failure_visibility_lib import inspect_hook_failure_visibility

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]
SOURCE_REF = ROOT / "skills/public/setup/references/hook-failure-visibility.md"
PLUGIN_REF = ROOT / "plugins/charness/skills/setup/references/hook-failure-visibility.md"
SOURCE_INSPECTOR = ROOT / "skills/public/setup/scripts/inspect_repo.py"
PLUGIN_INSPECTOR = ROOT / "plugins/charness/skills/setup/scripts/inspect_repo.py"


def _write_lefthook(repo: Path, text: str) -> dict[str, object]:
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "lefthook.yml").write_text(text, encoding="utf-8")
    return inspect_hook_failure_visibility(repo)


@pytest.mark.boundary_contract(
    reason="prove the generated setup inspector mirror runs from its installed layout while source calls stay in-process"
)
def _run_inspector(script: Path, repo: Path) -> dict[str, object]:
    result = run_script(str(script), "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    # `inspect_repo.py` emits YAML since the `--json` removal; YAML is a JSON superset,
    # so this also parses the compact-JSON fallback used when PyYAML is unavailable.
    return yaml.safe_load(result.stdout)["hook_failure_visibility"]


def test_hook_failure_guidance_is_mirrored_and_names_the_contract() -> None:
    source = SOURCE_REF.read_text(encoding="utf-8")
    assert PLUGIN_REF.read_text(encoding="utf-8") == source
    assert "pre-commit" in source and "pre-push" in source
    for marker in (
        "pre-commit.commands.<id>",
        "pre-push.commands.<id>",
        "fail_text",
        "logs/pre-push-quality-failure.log",
        "provision a stable stage-specific log directory before the hook runs",
        "fail_text` is self-contained",
        "send the operator to normal output",
        "truncation can hide",
        "final visible ordering as a consumer acceptance check",
        "Do not pipe a state-changing hook or gate through `tail`, `head`",
        "pipefail",
        "hook_failure_visibility",
        "live-verification-required",
    ):
        assert marker in source


def test_reader_names_a_missing_fail_text_on_the_exact_consumer_command(tmp_path: Path) -> None:
    payload = _write_lefthook(
        tmp_path,
        "pre-push:\n  commands:\n    quality:\n      run: ./scripts/run-quality.sh\n",
    )

    assert payload["state"] == "action-required"
    assert payload["summary"] == {"command_count": 1, "commands_with_gaps": 1, "gap_count": 1}
    assert payload["commands"] == [
        {
            "stage": "pre-push",
            "command_id": "quality",
            "run": "./scripts/run-quality.sh",
            "fail_text": None,
            "advertised_log_paths": [],
            "redirected_output_paths": [],
            "manual_reconciliation": [],
            "gaps": ["fail-text-missing"],
        }
    ]


def test_reader_refuses_to_turn_static_shape_into_a_live_pass(tmp_path: Path) -> None:
    payload = _write_lefthook(
        tmp_path,
        "\n".join(
            [
                "pre-push:",
                "  commands:",
                "    quality:",
                "      run: ./scripts/run-quality.sh > logs/pre-push-quality-failure.log 2>&1",
                '      fail_text: "PUSH BLOCKED by quality; read logs/pre-push-quality-failure.log before retrying"',
            ]
        )
        + "\n",
    )

    assert payload["state"] == "live-verification-required"
    assert payload["summary"] == {"command_count": 1, "commands_with_gaps": 0, "gap_count": 0}
    assert payload["live_verification"]["required"] is True
    assert all(token not in payload["state"] for token in ("pass", "clean"))
    assert "final terminal ordering" in payload["non_claims"][0]


def test_reader_reconciles_advertised_log_stderr_and_temporary_path(tmp_path: Path) -> None:
    payload = _write_lefthook(
        tmp_path,
        "\n".join(
            [
                "pre-commit:",
                "  commands:",
                "    lint:",
                "      run: ./lint.sh > logs/other.log",
                '      fail_text: "COMMIT BLOCKED by lint; read /tmp/lint.log before retrying"',
            ]
        )
        + "\n",
    )

    assert payload["state"] == "action-required"
    assert payload["commands"][0]["gaps"] == [
        "advertised-log-not-redirected-by-command",
        "advertised-log-is-temporary",
        "stderr-not-redirected-to-advertised-log",
    ]


def test_reader_tracks_shell_redirection_order_and_equivalent_stderr_forms(tmp_path: Path) -> None:
    reversed_order = _write_lefthook(
        tmp_path / "reversed",
        "pre-push:\n  commands:\n    quality:\n"
        "      run: ./gate 2>&1 > logs/failure.log\n"
        "      fail_text: PUSH BLOCKED; read logs/failure.log\n",
    )
    assert reversed_order["commands"][0]["gaps"] == ["stderr-not-redirected-to-advertised-log"]

    for name, redirect in (
        ("separate", "> logs/failure.log 2> logs/failure.log"),
        ("append", ">> logs/failure.log 2>> logs/failure.log"),
        ("duplicate", "> logs/failure.log 2>&1"),
        ("combined", "&> logs/failure.log"),
    ):
        payload = _write_lefthook(
            tmp_path / name,
            "pre-push:\n  commands:\n    quality:\n"
            f"      run: ./gate {redirect}\n"
            "      fail_text: PUSH BLOCKED; read logs/failure.log\n",
        )
        assert payload["state"] == "live-verification-required", (name, payload)
        assert payload["commands"][0]["gaps"] == [], (name, payload)


def test_reader_does_not_treat_a_command_without_run_as_complete(tmp_path: Path) -> None:
    payload = _write_lefthook(
        tmp_path,
        "pre-push:\n  commands:\n    quality:\n"
        "      fail_text: PUSH BLOCKED; read output above; do not retry blind\n",
    )

    assert payload["state"] == "action-required"
    assert payload["commands"][0]["gaps"] == ["run-missing"]


def test_reader_requires_manual_reconciliation_for_compound_shell_and_pipelines(
    tmp_path: Path,
) -> None:
    for name, run, expected in (
        (
            "redirect-before-gate",
            "echo warmup > logs/failure.log 2>&1; ./gate",
            ["compound-command"],
        ),
        (
            "disabled-pipefail",
            "set +o pipefail; ./gate | tail -n 20",
            ["compound-command", "pipeline"],
        ),
    ):
        payload = _write_lefthook(
            tmp_path / name,
            "pre-push:\n  commands:\n    quality:\n"
            f"      run: {run}\n"
            "      fail_text: PUSH BLOCKED; read logs/failure.log\n",
        )
        assert payload["state"] == "manual-reconciliation-required", (name, payload)
        assert payload["commands"][0]["gaps"] == [], (name, payload)
        assert payload["commands"][0]["manual_reconciliation"] == expected


def test_reader_does_not_parse_quoted_or_commented_operators_as_shell_control(
    tmp_path: Path,
) -> None:
    payload = _write_lefthook(
        tmp_path,
        "pre-push:\n  commands:\n    quality:\n"
        "      run: 'printf \"a|b\" # set +o pipefail; ignored'\n"
        "      fail_text: PUSH BLOCKED; read output above; do not retry blind\n",
    )

    assert payload["state"] == "live-verification-required"
    assert payload["commands"][0]["gaps"] == []
    assert payload["commands"][0]["manual_reconciliation"] == []


def test_shell_reader_keeps_ambiguous_shell_constructs_out_of_a_static_verdict() -> None:
    assert visibility._normalized_path("././logs/failure.log") == "logs/failure.log"

    comment_view, _comment_quoted, comment_valid = visibility._shell_code_view(
        "./gate # an ignored comment\n./next"
    )
    assert comment_valid is True and "ignored" not in comment_view

    escaped_view, escaped_quoted, escaped_valid = visibility._shell_code_view('printf "a\\"b"')
    assert escaped_valid is True and escaped_quoted
    assert visibility._shell_constructs(escaped_view, escaped_quoted, escaped_valid) == []

    for command, expected in (
        ("./gate 'unterminated", "unclosed-quote"),
        ("./gate &", "background-command"),
        ("echo $(date)", "command-substitution"),
        ("sh -c 'echo one; echo two'", "embedded-shell-command"),
    ):
        view, quoted, valid = visibility._shell_code_view(command)
        assert expected in visibility._shell_constructs(view, quoted, valid)


def test_reader_types_malformed_command_rows_and_stage_configs(tmp_path: Path) -> None:
    non_mapping = visibility._command_row("pre-push", "quality", [])
    assert non_mapping["gaps"] == ["command-entry-not-mapping"]

    malformed = visibility._command_row("pre-push", "quality", {"run": 7, "fail_text": 8})
    assert malformed["gaps"] == ["run-not-string", "fail-text-not-string"]

    missing_pointer = visibility._command_row(
        "pre-push", "quality", {"run": "./gate", "fail_text": "quality stopped"}
    )
    assert missing_pointer["gaps"] == [
        "fail-text-does-not-name-stage",
        "fail-text-has-no-next-evidence-action",
    ]
    blank = visibility._command_row("pre-push", "quality", {"run": "./gate", "fail_text": " "})
    assert blank["gaps"] == ["fail-text-blank"]

    invalid = _write_lefthook(
        tmp_path / "invalid",
        "pre-commit: []\npre-push:\n  commands: []\n",
    )
    assert invalid["state"] == "invalid-config"
    assert invalid["config_errors"] == [
        "pre-commit must be a mapping",
        "pre-push.commands must be a mapping",
    ]

    root_invalid = _write_lefthook(tmp_path / "root-invalid", "[]\n")
    assert root_invalid["state"] == "invalid-config"
    assert root_invalid["config_errors"] == ["Lefthook config root must be a mapping"]

    no_commands = _write_lefthook(tmp_path / "no-commands", "pre-push: {}\n")
    assert no_commands["state"] == "no-applicable-hook-commands"


def test_default_source_and_plugin_inspectors_carry_the_reader_verdict(tmp_path: Path) -> None:
    broken = tmp_path / "broken"
    _write_lefthook(
        broken,
        "pre-push:\n  commands:\n    quality:\n      run: ./scripts/run-quality.sh\n",
    )
    shaped = tmp_path / "shaped"
    _write_lefthook(
        shaped,
        "pre-push:\n  commands:\n    quality:\n"
        "      run: ./gate > logs/failure.log 2>&1\n"
        "      fail_text: PUSH BLOCKED by quality; read logs/failure.log\n",
    )

    for script in (SOURCE_INSPECTOR, PLUGIN_INSPECTOR):
        broken_payload = _run_inspector(script, broken)
        shaped_payload = _run_inspector(script, shaped)
        assert broken_payload["state"] == "action-required"
        assert broken_payload["commands"][0]["gaps"] == ["fail-text-missing"]
        assert shaped_payload["state"] == "live-verification-required"
        assert shaped_payload["live_verification"]["required"] is True


def test_reader_refuses_invalid_yaml_without_command_verdicts(tmp_path: Path) -> None:
    payload = _write_lefthook(tmp_path, "pre-push: [\n")

    assert payload["state"] == "invalid-config"
    assert payload["config_errors"]
    assert payload["commands"] == []
    assert payload["live_verification"]["required"] is False


def test_reader_types_absence_without_claiming_other_hook_managers(tmp_path: Path) -> None:
    payload = inspect_hook_failure_visibility(tmp_path)

    assert payload["state"] == "no-lefthook-config"
    assert payload["summary"]["command_count"] == 0
    assert "Husky and simple-git-hooks" in payload["non_claims"][0]
