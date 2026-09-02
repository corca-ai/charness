from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.script_loader import load_script_module
from tools.rewrite_script_preambles import REPO_SCRIPT_SHIM, _rewrite_source

ROOT = Path(__file__).resolve().parents[2]


def test_script_preamble_rewrite_is_idempotent() -> None:
    source = "from __future__ import annotations\n\nfrom runtime_bootstrap import repo_root_from_script\n"

    rewritten, replacements = _rewrite_source(source)
    second, second_replacements = _rewrite_source(rewritten)

    assert replacements == 1
    assert second_replacements == 0
    assert second == rewritten
    assert "from scripts.runtime_bootstrap import repo_root_from_script" in rewritten
    assert REPO_SCRIPT_SHIM in rewritten


@pytest.mark.boundary_contract(
    reason="prove a nested repository script resolves its root in a real child process"
)
def test_nested_script_resolves_repo_root_directly_and_in_process(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    nested = repo / "scripts" / "a" / "b"
    nested.mkdir(parents=True)
    (repo / "scripts" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "adapter_lib.py").write_text("", encoding="utf-8")
    (repo / "scripts" / "runtime_bootstrap.py").write_text(
        (ROOT / "scripts" / "runtime_bootstrap.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    script = nested / "x.py"
    script.write_text(
        "import sys\nfrom pathlib import Path\n\n"
        + REPO_SCRIPT_SHIM
        + "\n\nfrom scripts.runtime_bootstrap import repo_root_from_script\n"
        + "print(repo_root_from_script(__file__))\n",
        encoding="utf-8",
    )

    expected = str(repo.resolve())
    direct = subprocess.run(
        ["python3", "scripts/a/b/x.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    assert direct.returncode == 0, direct.stderr
    assert direct.stdout.strip() == expected

    load_script_module("nested_packaging_foundation_x", script)
    assert capsys.readouterr().out.strip() == expected
