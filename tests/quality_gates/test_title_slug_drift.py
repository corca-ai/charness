from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .support import ROOT, run_script

SCRIPT = "scripts/check_title_slug_drift.py"


def _load_drift_lib():
    module_path = ROOT / "scripts" / "check_title_slug_drift.py"
    spec = importlib.util.spec_from_file_location("check_title_slug_drift", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_detects_cautilus_style_rename_drift(tmp_path: Path) -> None:
    drifted = _write(
        tmp_path / "projection-contract.spec.md",
        "# How The Views Relate\n\nBody.\n",
    )
    lib = _load_drift_lib()
    drift = lib.find_drift([drifted])

    assert len(drift) == 1
    assert drift[0]["path"] == str(drifted)
    assert drift[0]["title"] == "How The Views Relate"


def test_accepts_aligned_title_and_slug(tmp_path: Path) -> None:
    aligned = _write(
        tmp_path / "names-and-keys.spec.md",
        "# Names And Keys\n\nBody.\n",
    )
    lib = _load_drift_lib()
    drift = lib.find_drift([aligned])

    assert drift == []


def test_skips_structural_h1_when_slug_carries_concept(tmp_path: Path) -> None:
    structural = _write(
        tmp_path / "external-seam-risk-interrupt.md",
        "# Problem\n\nBody.\n",
    )
    lib = _load_drift_lib()
    drift = lib.find_drift([structural])

    assert drift == []


def test_skips_structural_slug_when_h1_carries_concept(tmp_path: Path) -> None:
    structural_slug = _write(
        tmp_path / "skills" / "demo" / "SKILL.md",
        "# Demo Workflow Concept\n\nBody.\n",
    )
    lib = _load_drift_lib()

    assert lib.find_drift([structural_slug]) == []


def test_skips_files_with_no_h1(tmp_path: Path) -> None:
    no_h1 = _write(tmp_path / "fragment.md", "Plain text without a heading.\n")
    lib = _load_drift_lib()

    assert lib.find_drift([no_h1]) == []


def test_strict_mode_returns_nonzero_when_drift_present(tmp_path: Path) -> None:
    _write(tmp_path / "old-name.spec.md", "# Brand New Concept\n\n")

    result = run_script(SCRIPT, "--strict", "--json", str(tmp_path))

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["checked"] == 1
    assert len(payload["drift"]) == 1


def test_default_mode_returns_zero_with_advisory_text(tmp_path: Path) -> None:
    _write(tmp_path / "old-name.spec.md", "# Brand New Concept\n\n")

    result = run_script(SCRIPT, str(tmp_path))

    assert result.returncode == 0, result.stderr
    # The WARN: prefix is what run-quality.sh:294 surfaces non-blocking, so the
    # advisory posture is visible even though the gate no longer exits 1.
    assert "WARN: title-slug drift" in result.stdout
