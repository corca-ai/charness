from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script, write_executable

_check_cli_skill_surface = import_repo_module(
    ROOT / "scripts/gates/check_cli_skill_surface.py",
    "scripts.gates.check_cli_skill_surface",
)


def run_cli_skill_surface(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_cli_skill_surface.py", *args])
    returncode = _check_cli_skill_surface.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def seed_repo(tmp_path: Path, *, adapter_body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir()
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(adapter_body, encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\nUse `demo --help` and `demo doctor --json` for command details.\n",
        encoding="utf-8",
    )
    write_executable(
        repo / "demo",
        "#!/usr/bin/env bash\nset -euo pipefail\nprintf 'demo help --json doctor example registry\\n'\n",
    )
    return repo


def test_cli_skill_surface_is_not_applicable_without_product_combo_or_inferred_skill(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nproduct_surfaces:\n- installable_cli\n",
        encoding="utf-8",
    )
    result = run_script("scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "not_applicable"


def test_cli_skill_surface_refuses_an_adapter_version_it_does_not_speak(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """This reader picks the SUBPROCESSES it runs out of the adapter, so obeying a schema
    version it never reconciled is a harder trust boundary than a resolver echoing a
    field. The refusal has to be `blocked`, not `not_applicable`: `product_surfaces` can
    switch this gate off, so a fail-open here would let an unspeakable adapter silence it.
    """
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 7",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- attacker-selected --help",
            ]
        )
        + "\n",
    )

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "version must be 1" in "\n".join(payload["blockers"])
    # The refused fields must not survive anywhere in the payload: a blocker that still
    # echoed the attacker-selected probe would have honoured it well enough to report it.
    assert "attacker-selected" not in result.stdout
    assert payload.get("probe_commands", []) == []
    assert payload.get("product_surfaces", []) == []


def test_cli_skill_surface_treats_a_non_mapping_adapter_as_no_adapter(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A YAML file that parses to a list carries no `version` to reconcile, so it is
    absent-shaped, not version-refused. Routing it through the version blocker would
    report `version must be 1` about a file that declares nothing."""
    repo = seed_repo(tmp_path, adapter_body="- installable_cli\n- bundled_skill\n")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))

    payload = yaml.safe_load(result.stdout)
    assert "version must be 1" not in json.dumps(payload)
    assert payload["product_surface_source"] == "inferred"


def test_cli_skill_surface_flags_inferred_combo_without_adapter_fields(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(tmp_path, adapter_body="version: 1\nproduct_surfaces: []\n")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["product_surface_source"] == "inferred"
    assert "adapter does not declare `installable_cli`" in "\n".join(payload["adapter_weaknesses"])
    assert "cli_skill_surface_probe_commands is empty" in "\n".join(payload["adapter_weaknesses"])


def test_cli_skill_surface_blocks_declared_combo_without_binary_delegation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="version: 1\nproduct_surfaces:\n- installable_cli\n- bundled_skill\n",
    )
    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "No command-docs file or `--help` probe" in "\n".join(payload["blockers"])


def test_cli_skill_surface_accepts_declared_combo_with_probes_and_docs(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./demo --help",
                "- ./demo doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )
    result = run_script(
        "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes"
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert payload["probe_commands"] == ["./demo --help", "./demo doctor --json"]


def test_cli_skill_surface_reads_consumer_declared_paths(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / "src" / "skills" / "demo").mkdir(parents=True)
    (repo / "src" / "skills" / "demo" / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\nUse the CLI.\n", encoding="utf-8"
    )
    (repo / "src" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./src/demo --help\n", encoding="utf-8"
    )
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\n"
        "product_surfaces:\n  - installable_cli\n  - bundled_skill\n"
        "cli_skill_surface_probe_commands:\n  - ./src/demo --help\n  - ./src/demo doctor --json\n"
        "cli_skill_surface_command_docs:\n  - src/command-docs.yaml\n"
        "cli_skill_surface_skill_paths:\n  - src/skills/demo/SKILL.md\n"
        "cli_skill_surface_change_globs:\n  - src/**\n",
        encoding="utf-8",
    )

    result = run_cli_skill_surface(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--changed-path",
        "src/skills/demo/SKILL.md",
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0
    assert payload["product_surfaces"] == ["installable_cli", "bundled_skill"]
    assert payload["skill_paths"] == ["src/skills/demo/SKILL.md"]
    assert payload["command_docs"] == ["src/command-docs.yaml"]
    assert payload["probe_commands"] == ["./src/demo --help", "./src/demo doctor --json"]
    assert payload["changed_paths"] == ["src/skills/demo/SKILL.md"]


def test_cli_skill_surface_reports_probe_timeout(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- python3 scripts/hang.py doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )
    write_executable(
        repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n"
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.1"

    result = run_script(
        "scripts/gates/check_cli_skill_surface.py",
        "--repo-root",
        str(repo),
        "--run-probes",
        env=env,
    )
    payload = yaml.safe_load(result.stdout)

    # Still refuses -- the floor is unchanged -- but as an UNOBSERVED readiness
    # rather than a failing CLI, and only after both attempts expired.
    assert result.returncode == 1
    assert payload["status"] == "unobserved"
    assert payload["blockers"] == []
    assert payload["probe_results"][0]["returncode"] == 124
    assert payload["probe_results"][0]["timed_out"] is True
    assert payload["probe_results"][0]["attempts"] == _check_cli_skill_surface.PROBE_ATTEMPTS
    assert len(payload["unobserved"]) == 1
    assert "verdict NOT OBSERVED" in payload["unobserved"][0]
    assert "did not close its output within 0.1s on each of 2 attempts" in payload["unobserved"][0]


def test_cli_skill_surface_retries_a_starved_probe_before_concluding(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A probe starved once by gate contention must not be reported at all."""
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./demo doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )
    attempts: list[tuple[Path, str, float]] = []

    def fake_attempt(repo_root: Path, command: str, timeout_seconds: float):
        attempts.append((repo_root, command, timeout_seconds))
        if len(attempts) == 1:
            return {
                "command": command,
                "returncode": 124,
                "stdout_preview": "",
                "stderr_preview": "",
                "timed_out": True,
            }
        return {
            "command": command,
            "returncode": 0,
            "stdout_preview": "ok",
            "stderr_preview": "",
            "timed_out": False,
        }

    monkeypatch.setattr(_check_cli_skill_surface, "_attempt_probe", fake_attempt)
    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--run-probes")
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 2
    assert [command for _repo, command, _timeout in attempts] == [
        "./demo doctor --json",
        "./demo doctor --json",
    ]


def test_cli_skill_surface_probe_timeout_override_is_positive_only(monkeypatch) -> None:
    monkeypatch.delenv(_check_cli_skill_surface.PROBE_TIMEOUT_ENV, raising=False)
    assert (
        _check_cli_skill_surface._probe_timeout_seconds()
        == _check_cli_skill_surface.DEFAULT_PROBE_TIMEOUT_SECONDS
    )

    monkeypatch.setenv(_check_cli_skill_surface.PROBE_TIMEOUT_ENV, "0.125")
    assert _check_cli_skill_surface._probe_timeout_seconds() == 0.125

    for invalid in ("invalid", "0", "-1"):
        monkeypatch.setenv(_check_cli_skill_surface.PROBE_TIMEOUT_ENV, invalid)
        assert (
            _check_cli_skill_surface._probe_timeout_seconds()
            == _check_cli_skill_surface.DEFAULT_PROBE_TIMEOUT_SECONDS
        )


def test_cli_skill_surface_keeps_an_observed_failure_out_of_unobserved(tmp_path: Path) -> None:
    """A CLI that ANSWERS wrongly is a blocker, never an unobserved probe."""
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- python3 scripts/broken.py doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )
    write_executable(
        repo / "scripts" / "broken.py", "#!/usr/bin/env python3\nraise SystemExit(2)\n"
    )

    result = run_script(
        "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes"
    )
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 1
    assert any("exited 2" in blocker for blocker in payload["blockers"])


def test_cli_skill_surface_blocks_direct_agent_browser_runtime_probes(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- agent-browser open https://example.com",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "Unsafe CLI plus skill probe `agent-browser open https://example.com`" in "\n".join(
        payload["blockers"]
    )


def test_cli_skill_surface_blocks_wrapped_agent_browser_runtime_probes(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- env FOO=1 agent-browser open https://example.com",
                "- bash -c 'agent-browser screenshot /tmp/page.png'",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    blockers = "\n".join(payload["blockers"])
    assert "env FOO=1 agent-browser open https://example.com" in blockers
    assert "bash -c 'agent-browser screenshot /tmp/page.png'" in blockers


def test_cli_skill_surface_reports_missing_skill_path_adapter_weakness(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./demo --help",
                "- ./demo doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo))

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert "cli_skill_surface_skill_paths is empty" in "\n".join(payload["adapter_weaknesses"])


def test_cli_skill_surface_skips_irrelevant_release_change(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_change_globs:",
                "- src/**",
                "",
            ]
        ),
    )
    result = run_cli_skill_surface(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--changed-path",
        "docs/notes.md",
    )
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "skipped"
