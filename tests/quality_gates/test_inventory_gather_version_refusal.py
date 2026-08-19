"""Two readers refuse an unhonored adapter declaration instead of answering about the
wrong thing.

Rows 21-22 of slice 5.

`inventory_quality_handoff` gives a CLEAN BILL OF HEALTH on the wrong file. Measured at
`1465689ac`: a repo declaring `output_dir: docs/mine-q` under `version: 9` inventoried
`artifact: charness-artifacts/quality/latest.md` and reported `status: advisory`,
`findings: []`, exit 0 — while the review the repo does keep went uninventoried.

`advise_google_workspace_path` answers a CAPABILITY question, so an unhonored declaration
does not degrade the advice — it DENIES a capability the repo enabled. The same repo
declaring `gather_provider.google_workspace.mode: host-mediated` reported
`provider_mode: none` and told the operator to "stop with a missing-capability
explanation", exit 0.

Both fixtures use block shapes. Four probe records in this slice shipped a polarity
control that could not fail because a published stimulus used a form `adapter_lib` does
not parse into the type its validator needs; the fixtures were right every time, and these
are written from the fixtures.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

# Literal, so the coverage mapper can bind these tests to their sources by name.
INVENTORY = "scripts/inventory_quality_handoff.py"
ADVISOR = "skills/public/gather/scripts/advise_google_workspace_path.py"

QUALITY = "version: {v}\nrepo: demo\noutput_dir: docs/mine-q\n"
GATHER = """version: {v}
repo: demo
gather_provider:
  google_workspace:
    mode: host-mediated
"""


def _repo(tmp_path: Path, *, quality: str | None = None, gather: str | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "mine-q").mkdir(parents=True, exist_ok=True)
    (repo / "charness-artifacts" / "quality").mkdir(parents=True, exist_ok=True)
    # Two reviews with different bodies, so "inventoried the declared one" and
    # "inventoried ours" are distinguishable beyond the path.
    (repo / "docs" / "mine-q" / "latest.md").write_text(
        "# Quality Review\n\nthe declared one\n", encoding="utf-8"
    )
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        "# Quality Review\n\nthe charness default one\n", encoding="utf-8"
    )
    agents = repo / ".agents"
    agents.mkdir(parents=True, exist_ok=True)
    if quality is not None:
        (agents / "quality-adapter.yaml").write_text(quality, encoding="utf-8")
    if gather is not None:
        (agents / "gather-adapter.yaml").write_text(gather, encoding="utf-8")
    return repo


def _run(rel: str, repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / rel), "--repo-root", str(repo), *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_inventory_refuses_rather_than_clearing_the_wrong_file(
    tmp_path: Path, version: str
) -> None:
    result = _run(INVENTORY, _repo(tmp_path, quality=QUALITY.format(v=version)))
    assert result.returncode != 0, result.stdout
    if version == "9":
        assert "quality-adapter.yaml" in result.stderr, result.stderr
        assert "does not speak" in result.stderr, result.stderr
    else:
        # CONVERGED by `#673`: the five bare-loader libraries route through
        # `adapter_lib.read_declared_adapter`, so every resolver RECORDS a parse refusal
        # instead of raising and this door renders one verdict shape everywhere.
        assert "Traceback" not in result.stderr, result.stderr
        assert "quality-adapter.yaml" in result.stderr, result.stderr
        assert "could not be parsed" in result.stderr, result.stderr
    assert "charness-artifacts/quality" not in result.stdout


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_the_advisor_refuses_rather_than_denying_a_declared_capability(
    tmp_path: Path, version: str
) -> None:
    repo = _repo(tmp_path, gather=GATHER.format(v=version))
    result = _run(ADVISOR, repo)
    assert result.returncode == 1, result.stdout
    assert "gather-adapter.yaml" in result.stderr
    assert "provider_mode: none" not in result.stdout


def test_a_speakable_version_answers_about_what_the_repo_declared(tmp_path: Path) -> None:
    """The polarity control. Each expectation appears only when the declaration was
    honored: the declared review path, and the declared provider mode."""
    repo = _repo(tmp_path, quality=QUALITY.format(v="1"), gather=GATHER.format(v="1"))
    inventoried = _run(INVENTORY, repo)
    assert inventoried.returncode == 0, inventoried.stderr
    assert "artifact: docs/mine-q/latest.md" in inventoried.stdout
    advised = _run(ADVISOR, repo)
    assert advised.returncode == 0, advised.stderr
    assert "provider_mode: host-mediated" in advised.stdout


def test_an_explicitly_named_artifact_is_not_refused(tmp_path: Path) -> None:
    """`--artifact` asks the adapter nothing, so the guard sits INSIDE the branch that
    resolves the path from the adapter. Refusing here would break the direct invocation
    the flag exists for."""
    repo = _repo(tmp_path, quality=QUALITY.format(v="9"))
    result = _run(INVENTORY, repo, "--artifact", "docs/mine-q/latest.md")
    assert result.returncode == 0, result.stderr
    assert "artifact: docs/mine-q/latest.md" in result.stdout


def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path) -> None:
    """`valid: false` from one bad field beside honored ones must NOT refuse. The honored
    value is asserted too, so this cannot pass by a guard that refuses nothing AND a
    resolver that honors nothing."""
    repo = _repo(
        tmp_path,
        quality=QUALITY.format(v="1").replace("repo: demo", "repo: demo\npreset_version: 3"),
        gather=GATHER.format(v="1").replace("repo: demo", "repo: demo\npreset_version: 3"),
    )
    inventoried = _run(INVENTORY, repo)
    assert inventoried.returncode == 0, inventoried.stderr
    assert "artifact: docs/mine-q/latest.md" in inventoried.stdout
    advised = _run(ADVISOR, repo)
    assert advised.returncode == 0, advised.stderr
    assert "provider_mode: host-mediated" in advised.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    """Opt-in surfaces."""
    repo = _repo(tmp_path)
    assert _run(INVENTORY, repo).returncode == 0
    assert _run(ADVISOR, repo).returncode == 0
