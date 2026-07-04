"""In-process coverage for `skills/public/quality/scripts/skill_text_quality_lib.py`.

The two callers of this library (`skill_ergonomics_lib.py` /
`standing_doc_provenance_lib.py`) are exercised only through their own
higher-level gate suites on well-formed repo fixtures, so
`_add_argument_calls_missing_help`'s parse-failure guard and
`argparse_missing_help_findings`'s `__pycache__` skip never fire there. These
tests call the library directly.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "skill_text_quality_lib.py"


def _load():
    spec = importlib.util.spec_from_file_location("skill_text_quality_lib_inproc", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tqlib = _load()


def test_add_argument_calls_missing_help_returns_empty_on_syntax_error(tmp_path: Path) -> None:
    # ast.parse raises SyntaxError on malformed source; the scan must return an
    # empty finding list rather than propagate the parse failure.
    broken = tmp_path / "broken.py"
    broken.write_text("def broken(:\n    pass\n", encoding="utf-8")
    assert tqlib._add_argument_calls_missing_help(broken) == []


def test_argparse_missing_help_findings_skips_pycache_dir(tmp_path: Path) -> None:
    repo_root = tmp_path
    skill_dir = repo_root / "skills" / "public" / "demo"
    scripts_dir = skill_dir / "scripts"
    pycache_dir = scripts_dir / "__pycache__"
    pycache_dir.mkdir(parents=True)
    (pycache_dir / "stale.py").write_text(
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--x')\n",
        encoding="utf-8",
    )
    # Without the `__pycache__` skip this would report one finding (the
    # add_argument call above has no help=); the skip must keep it empty.
    assert tqlib.argparse_missing_help_findings(repo_root, skill_dir) == []


def test_argparse_missing_help_findings_reports_real_script_violation(tmp_path: Path) -> None:
    repo_root = tmp_path
    skill_dir = repo_root / "skills" / "public" / "demo"
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "real.py").write_text(
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--x')\n",
        encoding="utf-8",
    )
    findings = tqlib.argparse_missing_help_findings(repo_root, skill_dir)
    assert len(findings) == 1
    assert findings[0]["path"] == "skills/public/demo/scripts/real.py"
