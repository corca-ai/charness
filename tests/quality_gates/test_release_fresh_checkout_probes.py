"""The fresh-checkout probe checker's state vocabulary, and the byte each state earns.

`status: configured` at exit 0 with `probe_results: []` was a release gate
reporting SUCCESS while its own reason string said the probes "were not run":
a caller reading the byte could not tell "checked and clean" from "did not
check". The four states now separate, and the boundary that matters is which of
them carry a probe verdict at all.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

_FRESH = load_script_module(
    "check_fresh_checkout_probes_for_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "check_fresh_checkout_probes.py",
)

_PACKETS = load_script_module(
    "plan_release_run_packets_for_fresh_checkout_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "plan_release_run_packets.py",
)

_ARTIFACT_SECTIONS = load_script_module(
    "publish_release_artifact_sections_for_fresh_checkout_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_artifact_sections.py",
)

_ADAPTER_BASE = "\n".join(
    [
        "version: 1",
        "repo: demo",
        "output_dir: charness-artifacts/release",
        "package_id: demo",
        "packaging_manifest_path: packaging/demo.json",
        "materialized_plugin_root: plugins/demo",
        'sync_command: "true"',
        'quality_command: "true"',
        "",
    ]
)


def _seed_repo(root: Path, probes: list[str]) -> Path:
    """A real git repo with a named branch: `--run-probes` clones it by branch."""
    from .repo_shapes import install_committed_repo

    body = _ADAPTER_BASE
    if probes:
        body += "fresh_checkout_probes:\n" + "".join(f"- {probe!r}\n" for probe in probes)
    return install_committed_repo(
        root,
        {
            ".agents/release-adapter.yaml": body,
            "README.md": "# demo\n",
        },
    )


def _run(*args: str):
    return run_loaded_script_main("check_fresh_checkout_probes.py", _FRESH, *args)


def test_declared_but_not_run_is_unestablished_and_carries_no_probe_verdict(tmp_path: Path) -> None:
    """The escape this closes, asserted three independent ways.

    Exit 3 is `run-quality.sh`'s UNESTABLISHED byte, which that runner renders
    UNPROVEN rather than counting it as a pass. `probe_results` is ABSENT because
    an empty result list is a verdict shape -- "zero failing probes" -- for a run
    that executed none. Fails on revert on every assertion below."""
    repo = _seed_repo(tmp_path / "declared", ["echo probe-a"])

    result = _run("--repo-root", str(repo), "--detail")

    assert result.returncode == _FRESH.UNESTABLISHED_EXIT, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "not_established"
    assert "probe_results" not in payload
    assert payload["fresh_checkout_probes"] == ["echo probe-a"]
    assert "--run-probes" in payload["remediation"]


def test_declared_but_not_run_says_so_in_the_plain_summary_line(tmp_path: Path) -> None:
    """The one-line surface most readers actually read. `configured` described the
    ADAPTER's state, never this run's, and sat next to exit 0."""
    repo = _seed_repo(tmp_path / "declared-plain", ["echo probe-a"])

    result = _run("--repo-root", str(repo))

    assert result.returncode == _FRESH.UNESTABLISHED_EXIT
    assert "not_established" in result.stdout
    assert "not a pass" in result.stdout


def test_running_the_declared_probes_establishes_a_real_answer(tmp_path: Path) -> None:
    """`0` + executed probes is the answer exit 0 is allowed to mean."""
    repo = _seed_repo(tmp_path / "runnable", ["echo probe-a", "echo probe-b"])

    result = _run("--repo-root", str(repo), "--run-probes", "--detail")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "passed"
    assert [entry["returncode"] for entry in payload["probe_results"]] == [0, 0]


def test_a_failing_probe_is_a_blocker_not_an_unestablished_run(tmp_path: Path) -> None:
    """Exit 1 must stay reachable and distinct from 3: a probe that RAN and failed
    is an actionable blocker, not an undetermined verdict."""
    repo = _seed_repo(tmp_path / "failing", ["exit 7"])

    result = _run("--repo-root", str(repo), "--run-probes", "--detail")

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert any("exited 7" in blocker for blocker in payload["blockers"])


def test_a_repo_declaring_no_probes_is_answered_never_refused(tmp_path: Path) -> None:
    """The deliberate opt-out, with and without `--run-probes`.

    A repo that legitimately declares nothing must not start refusing forever:
    `not_configured` is a genuine answer at exit 0, and it keeps `probe_results`
    because zero declared probes really did produce zero results.

    NON-DISCRIMINATING BY DESIGN: this passes before and after the change. It is a
    false-refusal guard on the opt-out path, not bite proof."""
    repo = _seed_repo(tmp_path / "optout", [])

    for extra in ([], ["--run-probes"]):
        result = _run("--repo-root", str(repo), *extra, "--detail")
        assert result.returncode == 0, result.stdout + result.stderr
        payload = yaml.safe_load(result.stdout)
        assert payload["status"] == "not_configured"
        assert payload["probe_results"] == []


def test_the_real_process_entrypoint_returns_the_unestablished_byte(tmp_path: Path) -> None:
    """In-process `main` and a real subprocess must agree on the byte, because the
    release gate packet is a shell command and the shell reads `$?`."""
    repo = _seed_repo(tmp_path / "subprocess", ["echo probe-a"])

    result = subprocess.run(
        [
            sys.executable,
            "skills/public/release/scripts/check_fresh_checkout_probes.py",
            "--repo-root",
            str(repo),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3, result.stdout + result.stderr


def test_the_release_artifact_does_not_render_an_unrun_probe_set_as_a_status(tmp_path: Path) -> None:
    """The artifact a rung-2 human audit reads. `- Fresh-checkout probe status:
    configured.` is a sentence that reads as a satisfied probe run and is not one."""
    lines = _ARTIFACT_SECTIONS.fresh_checkout_lines(
        {"status": "not_established", "fresh_checkout_probes": ["echo probe-a"]}
    )

    assert any("were not run" in line for line in lines)
    assert any("no probe verdict was established" in line for line in lines)
    assert not any("probe status:" in line for line in lines)

    # Falsifiable counterparts: an executed run and a genuine opt-out keep their
    # own sentences.
    assert any(
        "probe status: passed" in line
        for line in _ARTIFACT_SECTIONS.fresh_checkout_lines({"status": "passed"})
    )
    assert any(
        "No repo-declared fresh checkout probes" in line
        for line in _ARTIFACT_SECTIONS.fresh_checkout_lines({"status": "not_configured"})
    )


def test_the_always_release_gate_asks_for_an_established_probe_verdict() -> None:
    """Without `--run-probes` the always-gate can only report UNPROVEN, forever --
    a verdict word nobody reads after the third release. The caller that wants a
    verdict is the one that asks for execution; the checker never decides to."""
    packet = next(
        packet for packet in _PACKETS.gate_packets() if packet["id"] == "fresh-checkout-probes"
    )

    assert "--run-probes" in packet["command"]
