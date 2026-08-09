from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script, write_executable

_check_cli_skill_surface = import_repo_module(
    ROOT / "scripts/check_cli_skill_surface.py",
    "scripts.check_cli_skill_surface",
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


def test_cli_skill_surface_is_not_applicable_without_product_combo_or_inferred_skill(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nproduct_surfaces:\n- installable_cli\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "not_applicable"


def test_cli_skill_surface_flags_inferred_combo_without_adapter_fields(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(tmp_path, adapter_body="version: 1\nproduct_surfaces: []\n")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")

    payload = json.loads(result.stdout)
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
    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert payload["probe_commands"] == ["./demo --help", "./demo doctor --json"]


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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    write_executable(repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n")
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.1"

    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json", env=env)
    payload = json.loads(result.stdout)

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


def test_cli_skill_surface_retries_a_starved_probe_before_concluding(tmp_path: Path) -> None:
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
                "- python3 scripts/flaky.py doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    # Hangs on the first invocation only, exactly like a probe starved by a
    # concurrent sibling; the marker makes the second run cheap and passing.
    write_executable(
        repo / "scripts" / "flaky.py",
        "#!/usr/bin/env python3\n"
        "import pathlib, time\n"
        "marker = pathlib.Path(__file__).with_name('flaky.marker')\n"
        "if not marker.exists():\n"
        "    marker.write_text('1')\n"
        "    time.sleep(600)\n",
    )
    env = os.environ.copy()
    # Generous on purpose: the second attempt pays a cold CPython start, and
    # this test runs inside the very gate whose contention it is asserting
    # tolerance of. A tight budget here would make the starve test starve.
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "10"

    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json", env=env)
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 2


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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    write_executable(repo / "scripts" / "broken.py", "#!/usr/bin/env python3\nraise SystemExit(2)\n")

    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json")
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 1
    assert any("exited 2" in blocker for blocker in payload["blockers"])


def test_cli_skill_surface_blocks_direct_agent_browser_runtime_probes(tmp_path: Path, monkeypatch, capsys) -> None:
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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "Unsafe CLI plus skill probe `agent-browser open https://example.com`" in "\n".join(payload["blockers"])


def test_cli_skill_surface_blocks_wrapped_agent_browser_runtime_probes(tmp_path: Path, monkeypatch, capsys) -> None:
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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    blockers = "\n".join(payload["blockers"])
    assert "env FOO=1 agent-browser open https://example.com" in blockers
    assert "bash -c 'agent-browser screenshot /tmp/page.png'" in blockers


def test_cli_skill_surface_reports_missing_skill_path_adapter_weakness(tmp_path: Path, monkeypatch, capsys) -> None:
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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")

    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert "cli_skill_surface_skill_paths is empty" in "\n".join(payload["adapter_weaknesses"])


def test_cli_skill_surface_skips_irrelevant_release_change(tmp_path: Path, monkeypatch, capsys) -> None:
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
        "--json",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "skipped"


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
        assert stdout, f"the check produced no stdout; rc={process.returncode} stderr={stderr[-400:]}"
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
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    return repo


def test_cli_skill_surface_separates_a_real_124_exit_from_an_unobserved_probe(tmp_path: Path) -> None:
    """A command that ANSWERS 124 is a blocker; only an unread verdict is unobserved.

    124 is the code this check synthesizes for its own deadline, so a probe that
    exits 124 on its own is the one input that tells a returncode-keyed
    implementation apart from a `timed_out`-keyed one.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/exits124.py doctor --json")
    write_executable(repo / "scripts" / "exits124.py", "#!/usr/bin/env python3\nraise SystemExit(124)\n")

    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json")
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["returncode"] == 124
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 1
    assert any("exited 124" in blocker for blocker in payload["blockers"])


def test_cli_skill_surface_survives_a_probe_whose_grandchild_holds_the_pipe(tmp_path: Path) -> None:
    """The deadline must bind even when a grandchild inherits the output pipe.

    `subprocess.run(timeout=)` kills only the direct child and then drains with
    NO deadline, so this shape hangs the check forever. Nothing above it -- not
    `run-quality.sh`, not the pre-push hook -- puts a wall clock around a label,
    so the gate would hang rather than refuse.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/orphan.py doctor --json")
    write_executable(
        repo / "scripts" / "orphan.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys\n"
        # The grandchild inherits stdout/stderr and outlives the parent.
        "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'])\n"
        "print('partial verdict before the hang')\n"
        "sys.stdout.flush()\n"
        "import time; time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "1"

    result = _run_bounded_in_own_session(
        "scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json", env=env
    )
    assert result is not None, "the check did not bound its own probe deadline; it hung on the orphan-held pipe"
    payload = json.loads(result)

    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    # Partial output captured before the deadline is EVIDENCE, not noise: it is
    # what tells a reader the command was mid-verdict rather than never started.
    assert "partial verdict before the hang" in payload["probe_results"][0]["stdout_preview"]


def test_cli_skill_surface_bounds_the_drain_when_the_grandchild_escapes_the_group(tmp_path: Path) -> None:
    """The drain deadline must bind when killing the group cannot reach the holder.

    Killing the probe's process group reaps the ordinary grandchild, which makes
    the drain return instantly and leaves `DRAIN_TIMEOUT_SECONDS` unexercised --
    a mutation sweep confirmed the deadline could be deleted with the suite
    green. A grandchild that calls `setsid()` escapes the group, still holds the
    inherited pipe, and is the input that makes the deadline load-bearing.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/escapee.py doctor --json")
    write_executable(
        repo / "scripts" / "escapee.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        # start_new_session puts the grandchild in its OWN session, so killpg on
        # the probe's group never reaches it; it keeps the pipe open regardless.
        "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'], start_new_session=True)\n"
        "time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "1"

    started = time.monotonic()
    result = _run_bounded_in_own_session(
        "scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json", env=env
    )
    elapsed = time.monotonic() - started

    assert result is not None, "the drain was unbounded; the escaped grandchild held the pipe open forever"
    payload = json.loads(result)
    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    # 2 attempts x (1s deadline + <=5s drain) plus interpreter start. The upper
    # bound is what proves the drain deadline fired rather than the outer bound.
    assert elapsed < 25, f"drain deadline did not bind: {elapsed:.1f}s"


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
        f"m = import_repo_module({str(ROOT / 'scripts/check_cli_skill_surface.py')!r}, 'scripts.check_cli_skill_surface')\n"
        # No start_new_session: the child SHARES this process's group, so an
        # unguarded killpg would take this process down with it.
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'],\n"
        "                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)\n"
        "m._kill_group_and_drain(child)\n"
        # One-sided otherwise: 'we were not killed' also holds when nothing
        # was killed at all, which leaks the child and proves half the property.
        "assert child.poll() is not None, 'the child was never reaped'\n"
        "print('SURVIVED', flush=True)\n",
        encoding="utf-8",
    )

    process = subprocess.Popen(
        [sys.executable, str(probe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True
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


def test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out(tmp_path: Path) -> None:
    """Partial evidence must survive the DRAIN deadline, not just the probe deadline.

    Round 2 found the two existing fixtures each covered one half: the orphan
    probe prints but its grandchild is reaped, so the drain succeeds and never
    exercises the discard; the escapee probe defeats the drain but prints
    nothing. Crossing them -- a probe that prints AND leaves an escaped
    grandchild holding the pipe -- is the input that reaches the discard, which
    is where the original defect had been reintroduced one call deeper.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/loud_escapee.py doctor --json")
    write_executable(
        repo / "scripts" / "loud_escapee.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'], start_new_session=True)\n"
        "print('partial verdict that must survive the drain')\n"
        "sys.stdout.flush()\n"
        "time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "1"

    result = _run_bounded_in_own_session(
        "scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json", env=env
    )
    assert result is not None, "the check hung instead of bounding its drain"
    payload = json.loads(result)

    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    assert "partial verdict that must survive the drain" in payload["probe_results"][0]["stdout_preview"]
