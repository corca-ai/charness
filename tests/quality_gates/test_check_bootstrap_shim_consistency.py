from __future__ import annotations

import importlib
import json
import textwrap
from pathlib import Path

from .support import run_script

shim_gate = importlib.import_module("scripts.check_bootstrap_shim_consistency")

SCRIPT = "scripts/check_bootstrap_shim_consistency.py"
DRIFTED_SHIM = textwrap.dedent(
    '''\
    def _load_skill_runtime_bootstrap():
        bootstrap = next(
            (ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()),
            None,
        )
        if bootstrap is None:
            raise ImportError("skill_runtime_bootstrap.py not found")
        return SimpleNamespace(**runpy.run_path(str(bootstrap)))
    '''
)
HEADER = "import runpy\nfrom pathlib import Path\nfrom types import SimpleNamespace\n\n\n"


def _seed_repo(tmp_path: Path, *, drifted: bool) -> Path:
    repo = tmp_path / "repo"
    scripts_dir = repo / "skills" / "public" / "demo" / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "canonical_helper.py").write_text(
        HEADER + shim_gate.CANONICAL_SHIM + "\n", encoding="utf-8"
    )
    body = DRIFTED_SHIM if drifted else shim_gate.CANONICAL_SHIM + "\n"
    (scripts_dir / "second_helper.py").write_text(HEADER + body, encoding="utf-8")
    return repo


def test_reports_drifted_copy_and_exits_nonzero(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=True)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "drift"
    assert payload["checked_files"] == 2
    assert payload["drifted"] == ["skills/public/demo/scripts/second_helper.py"]


def test_clean_tree_exits_zero(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 0
    assert "2 copies match the canonical block" in result.stdout


def test_fix_rewrites_to_canonical_and_round_trips(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=True)
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix", "--json")
    assert fix_result.returncode == 0
    payload = json.loads(fix_result.stdout)
    assert payload["fixed"] == ["skills/public/demo/scripts/second_helper.py"]
    rewritten = (repo / "skills/public/demo/scripts/second_helper.py").read_text(encoding="utf-8")
    assert shim_gate.CANONICAL_SHIM in rewritten
    recheck = run_script(SCRIPT, "--repo-root", str(repo))
    assert recheck.returncode == 0


def test_nested_drifted_copy_is_reported_not_rewritten(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    nested = repo / "scripts" / "nested_holder.py"
    nested.parent.mkdir(parents=True)
    nested.write_text(
        HEADER + "def outer():\n" + textwrap.indent(DRIFTED_SHIM, "    "),
        encoding="utf-8",
    )
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix", "--json")
    assert fix_result.returncode == 1
    payload = json.loads(fix_result.stdout)
    assert payload["unfixable"] == ["scripts/nested_holder.py"]
    assert textwrap.indent(DRIFTED_SHIM, "    ").rstrip() in nested.read_text(encoding="utf-8")


def test_fix_is_safe_with_form_feed_before_the_shim(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    target = repo / "skills" / "public" / "demo" / "scripts" / "second_helper.py"
    target.write_text(
        HEADER + 'PAGE_BREAK = "before\x0cafter"\nKEEP_ME = 1\n\n' + DRIFTED_SHIM,
        encoding="utf-8",
    )
    # splitlines-based splicing would treat the \x0c as a line break, shift
    # the window, and delete real statements while reporting success.
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix", "--json")
    assert fix_result.returncode == 0
    rewritten = target.read_text(encoding="utf-8")
    assert "KEEP_ME = 1" in rewritten
    assert shim_gate.CANONICAL_SHIM in rewritten
    recheck = run_script(SCRIPT, "--repo-root", str(repo))
    assert recheck.returncode == 0


def test_fix_rewrites_two_module_level_shims_in_one_file(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    target = repo / "skills" / "public" / "demo" / "scripts" / "second_helper.py"
    target.write_text(HEADER + DRIFTED_SHIM + "\n\n" + DRIFTED_SHIM, encoding="utf-8")
    fix_result = run_script(SCRIPT, "--repo-root", str(repo), "--fix", "--json")
    assert fix_result.returncode == 0
    rewritten = target.read_text(encoding="utf-8")
    assert rewritten.count(shim_gate.CANONICAL_SHIM) == 2


def test_failure_message_names_the_deliberate_evolution_path(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=True)
    result = run_script(SCRIPT, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "CANONICAL_SHIM" in result.stderr


def test_name_prefix_collision_is_not_scanned(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, drifted=False)
    holder = repo / "scripts" / "module_loader.py"
    holder.parent.mkdir(parents=True, exist_ok=True)
    holder.write_text(
        "def _load_skill_runtime_bootstrap_module():\n    return None\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["checked_files"] == 2
