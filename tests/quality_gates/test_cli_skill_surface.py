from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
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
        "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", env=env
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


def _run_bounded_in_own_session(*args: str, env: dict[str, str], limit: float = 30.0) -> str | None:
    """Run the check under a bound that does NOT depend on the code under test.

    `subprocess.run(timeout=)` is not usable here: it kills only the direct child
    and then drains with no deadline, which is the exact defect this test exists
    to catch, so a regressed check would hang the SUITE instead of failing it.
    Returns stdout, or None when the check blew the bound.
    """
    process = subprocess.Popen(
        [sys.executable, *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=limit)
        assert stdout, (
            f"the check produced no stdout; rc={process.returncode} stderr={stderr[-400:]}"
        )
        return stdout
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        try:
            process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        return None


def _probe_repo(tmp_path: Path, command: str) -> Path:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                f"- {command}",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )
    return repo


def _recorded_pids(path: Path) -> list[int]:
    if not path.is_file():
        return []
    return [int(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_controlled_pipe_holder(repo: Path) -> Path:
    holder = repo / "scripts" / "pipe_holder.py"
    write_executable(
        holder,
        "#!/usr/bin/env python3\n"
        "import os, signal, sys, time\n"
        "from pathlib import Path\n"
        "stop_path, exit_dir = map(Path, sys.argv[1:])\n"
        "pid = os.getpid()\n"
        "def finish(*_args):\n"
        "    exit_dir.mkdir(parents=True, exist_ok=True)\n"
        "    (exit_dir / str(pid)).write_text('exited\\n', encoding='utf-8')\n"
        "    raise SystemExit(0)\n"
        "signal.signal(signal.SIGTERM, finish)\n"
        "deadline = time.monotonic() + 5.0\n"
        "while not stop_path.exists() and time.monotonic() < deadline:\n"
        "    time.sleep(0.01)\n"
        "finish()\n",
    )
    return holder


def _owned_process_is_running(pid: int, identity: str) -> bool:
    process = subprocess.run(
        ["ps", "-o", "stat=,args=", "-p", str(pid)],
        check=False,
        capture_output=True,
        text=True,
    )
    fields = process.stdout.strip().split(maxsplit=1)
    if process.returncode != 0 or len(fields) != 2:
        return False
    state, argv = fields
    return not state.startswith("Z") and identity in argv


def _stop_recorded_children(
    pid_log: Path, stop_path: Path, exit_dir: Path
) -> tuple[list[int], list[int], list[int]]:
    stop_path.write_text("stop\n", encoding="utf-8")
    pids = _recorded_pids(pid_log)
    identity = str(stop_path)
    deadline = time.monotonic() + 6.0
    while time.monotonic() < deadline:
        survivors = [pid for pid in pids if _owned_process_is_running(pid, identity)]
        if not survivors:
            break
        time.sleep(0.01)
    exited = [pid for pid in pids if (exit_dir / str(pid)).is_file()]
    survivors = [pid for pid in pids if _owned_process_is_running(pid, identity)]
    return pids, exited, survivors


def test_cli_skill_surface_separates_a_real_124_exit_from_an_unobserved_probe(
    tmp_path: Path,
) -> None:
    """A command that ANSWERS 124 is a blocker; only an unread verdict is unobserved.

    124 is the code this check synthesizes for its own deadline, so a probe that
    exits 124 on its own is the one input that tells a returncode-keyed
    implementation apart from a `timed_out`-keyed one.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/exits124.py doctor --json")
    write_executable(
        repo / "scripts" / "exits124.py", "#!/usr/bin/env python3\nraise SystemExit(124)\n"
    )

    result = run_script(
        "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes"
    )
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["returncode"] == 124
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 1
    assert any("exited 124" in blocker for blocker in payload["blockers"])


@pytest.mark.boundary_contract(
    reason="child-exit-on-parent-death: a real probe process and grandchild must be bounded and reaped"
)
def test_cli_skill_surface_survives_a_probe_whose_grandchild_holds_the_pipe(tmp_path: Path) -> None:
    """The deadline must bind even when a grandchild inherits the output pipe.

    `subprocess.run(timeout=)` kills only the direct child and then drains with
    NO deadline, so this shape hangs the check forever. Nothing above it -- not
    `run-quality.sh`, not the pre-push hook -- puts a wall clock around a label,
    so the gate would hang rather than refuse.
    """
    pid_log = tmp_path / "orphan-pids.txt"
    stop_path = tmp_path / "stop-orphans"
    exit_dir = tmp_path / "orphan-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/orphan.py doctor --json")
    holder = _write_controlled_pipe_holder(repo)
    write_executable(
        repo / "scripts" / "orphan.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        # The grandchild inherits stdout/stderr and outlives the parent.
        f"child = subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}])\n"
        f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as stream: stream.write(str(child.pid) + '\\n')\n"
        "print('partial verdict before the hang')\n"
        "sys.stdout.flush()\n"
        "time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.5"

    try:
        result = _run_bounded_in_own_session(
            "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", env=env
        )
        recorded_pids = _recorded_pids(pid_log)
        production_survivors = [
            pid for pid in recorded_pids if _owned_process_is_running(pid, str(stop_path))
        ]
    finally:
        cleanup_pids, _, cleanup_survivors = _stop_recorded_children(pid_log, stop_path, exit_dir)
    assert result is not None, (
        "the check did not bound its own probe deadline; it hung on the orphan-held pipe"
    )
    assert recorded_pids, "the fixture never established an inherited pipe holder"
    assert not production_survivors, "the production group kill left an ordinary descendant running"
    assert not cleanup_survivors, "the fixture failed to clean every recorded descendant"
    payload = yaml.safe_load(result)

    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    assert len(recorded_pids) == payload["probe_results"][0]["attempts"]
    # Partial output captured before the deadline is EVIDENCE, not noise: it is
    # what tells a reader the command was mid-verdict rather than never started.
    assert "partial verdict before the hang" in payload["probe_results"][0]["stdout_preview"]


@pytest.mark.boundary_contract(
    reason="child-exit-on-parent-death: an escaped grandchild must not defeat the process-group drain deadline"
)
def test_cli_skill_surface_bounds_the_drain_when_the_grandchild_escapes_the_group(
    tmp_path: Path,
) -> None:
    """The drain deadline must bind when killing the group cannot reach the holder.

    Killing the probe's process group reaps the ordinary grandchild, which makes
    the drain return instantly and leaves the guard's post-kill drain unexercised --
    a mutation sweep confirmed the deadline could be deleted with the suite
    green. A grandchild that calls `setsid()` escapes the group, still holds the
    inherited pipe, and is the input that makes the deadline load-bearing.
    """
    pid_log = tmp_path / "escapee-pids.txt"
    stop_path = tmp_path / "stop-escapees"
    exit_dir = tmp_path / "escapee-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/escapee.py doctor --json")
    holder = _write_controlled_pipe_holder(repo)
    write_executable(
        repo / "scripts" / "escapee.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        # start_new_session puts the grandchild in its OWN session, so killpg on
        # the probe's group never reaches it; it keeps the pipe open regardless.
        f"child = subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}], start_new_session=True)\n"
        f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as stream: stream.write(str(child.pid) + '\\n')\n"
        "time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.5"

    started = time.monotonic()
    try:
        result = _run_bounded_in_own_session(
            "scripts/gates/check_cli_skill_surface.py",
            "--repo-root",
            str(repo),
            "--run-probes",
            env=env,
        )
        elapsed = time.monotonic() - started
    finally:
        escaped_pids, exited_pids, survivors = _stop_recorded_children(pid_log, stop_path, exit_dir)

    assert result is not None, (
        "the drain was unbounded; the escaped grandchild held the pipe open forever"
    )
    assert escaped_pids, "the fixture never established an escaped pipe holder"
    assert exited_pids == escaped_pids, "the fixture failed to stop every escaped pipe holder"
    assert not survivors
    payload = yaml.safe_load(result)
    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    assert len(escaped_pids) == payload["probe_results"][0]["attempts"]
    # The guard's post-kill drain is five seconds per attempt. Two probe attempts
    # therefore remain bounded well below fifteen seconds.
    assert elapsed < 15, f"post-kill drain did not bind: {elapsed:.1f}s"


@pytest.mark.boundary_contract(
    reason="signal behavior: group cleanup must not signal a process group the probe does not own"
)
def test_kill_group_and_drain_never_signals_a_group_the_probe_does_not_own(tmp_path: Path) -> None:
    """Guard against the probe SIGKILLing the whole quality run.

    `os.getpgid(child)` returns the SHARED group when the child is not a group
    leader, so an unguarded `killpg` reaps every sibling check, the runner, and
    the shell. That is not hypothetical: a mutant flipping `start_new_session`
    to False did exactly that three times during this slice, killing the sweep
    mid-run and leaving the tree mutated.

    The scenario runs in its OWN session so a regression kills only that
    subprocess instead of this suite -- the containment is the point.
    """
    probe = tmp_path / "self_signal.py"
    probe.write_text(
        "import subprocess, sys, time\n"
        f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
        "from runtime_bootstrap import import_repo_module\n"
        f"m = import_repo_module({str(ROOT / 'scripts/core/subprocess_guard.py')!r}, 'scripts.core.subprocess_guard')\n"
        # No start_new_session: the child SHARES this process's group, so an
        # unguarded killpg would take this process down with it.
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'],\n"
        "                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)\n"
        "m._kill_tree(child)\n"
        # One-sided otherwise: 'we were not killed' also holds when nothing
        # was killed at all, which leaks the child and proves half the property.
        "child.wait(timeout=5)\n"
        "assert child.poll() is not None, 'the child was never reaped'\n"
        "print('SURVIVED', flush=True)\n",
        encoding="utf-8",
    )

    process = subprocess.Popen(
        [sys.executable, str(probe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.communicate()
        raise AssertionError("kill-and-drain hung on a group it does not own")

    assert "SURVIVED" in stdout, (
        "kill-and-drain signalled a process group it does not own; "
        f"rc={process.returncode} stderr={stderr[-400:]}"
    )


@pytest.mark.boundary_contract(
    reason="child-exit-on-parent-death: escaped descendants must be cleaned while preserving partial output"
)
def test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out(
    tmp_path: Path,
) -> None:
    """Partial evidence must survive the DRAIN deadline, not just the probe deadline.

    Round 2 found the two existing fixtures each covered one half: the orphan
    probe prints but its grandchild is reaped, so the drain succeeds and never
    exercises the discard; the escapee probe defeats the drain but prints
    nothing. Crossing them -- a probe that prints AND leaves an escaped
    grandchild holding the pipe -- is the input that reaches the discard, which
    is where the original defect had been reintroduced one call deeper.
    """
    pid_log = tmp_path / "loud-escapee-pids.txt"
    stop_path = tmp_path / "stop-loud-escapees"
    exit_dir = tmp_path / "loud-escapee-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/loud_escapee.py doctor --json")
    holder = _write_controlled_pipe_holder(repo)
    write_executable(
        repo / "scripts" / "loud_escapee.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        f"child = subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}], start_new_session=True)\n"
        f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as stream: stream.write(str(child.pid) + '\\n')\n"
        "print('partial verdict that must survive the drain')\n"
        "sys.stdout.flush()\n"
        "time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.5"
    try:
        result = _run_bounded_in_own_session(
            "scripts/gates/check_cli_skill_surface.py",
            "--repo-root",
            str(repo),
            "--run-probes",
            env=env,
        )
    finally:
        escaped_pids, exited_pids, survivors = _stop_recorded_children(pid_log, stop_path, exit_dir)
    assert result is not None, "the check hung instead of bounding its drain"
    assert escaped_pids, "the fixture never established an escaped pipe holder"
    assert exited_pids == escaped_pids, "the fixture failed to stop every escaped pipe holder"
    assert not survivors
    payload = yaml.safe_load(result)

    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    assert len(escaped_pids) == payload["probe_results"][0]["attempts"]
    assert (
        "partial verdict that must survive the drain"
        in payload["probe_results"][0]["stdout_preview"]
    )


def test_cli_skill_surface_names_the_unobserved_probe_in_its_only_output(tmp_path: Path) -> None:
    """The output must say UNOBSERVED, not look like a failure.

    `run-quality.sh` invokes this check with no format selector, and after the
    `--json` removal the YAML payload is the only thing an operator ever reads.
    The defect this pins misnamed a probe that never answered as one that
    failed; the distinction now has to live in the payload, because there is no
    second rendering left to carry it.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/hang.py doctor --json")
    write_executable(
        repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n"
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.2"

    result = run_script(
        "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", env=env
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unobserved"
    assert any("verdict NOT OBSERVED" in item for item in payload["unobserved"])
    # The word that misled a whole session must not appear for a probe that
    # merely never answered -- in the payload or anywhere else on the surface.
    assert payload["blockers"] == []
    assert "probe failed" not in result.stdout
    assert "probe failed" not in result.stderr
