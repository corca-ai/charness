from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .support import ROOT


def _load_gather_module(name: str):
    module_path = ROOT / "skills" / "public" / "gather" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"gather_{name}", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gather_adapter_defaults_all_sources_to_direct_cli(tmp_path: Path) -> None:
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    provider = payload["data"]["gather_provider"]
    assert set(provider) == {"github", "google_workspace", "slack", "notion"}
    for source, entry in provider.items():
        assert entry == {"mode": "direct-cli"}, source


def test_gather_adapter_parses_per_source_modes(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "gather_provider:",
                "  github:",
                "    mode: host-mediated",
                "  google_workspace:",
                "    mode: 'none'",
                "  slack:",
                "    mode: direct-cli",
                "  notion:",
                "    mode: host-mediated",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    provider = payload["data"]["gather_provider"]
    assert provider["github"]["mode"] == "host-mediated"
    assert provider["google_workspace"]["mode"] == "none"
    assert provider["slack"]["mode"] == "direct-cli"
    assert provider["notion"]["mode"] == "host-mediated"


def test_gather_adapter_rejects_unknown_mode(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  slack:\n    mode: bogus\n",
        encoding="utf-8",
    )
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is False
    assert any("gather_provider.slack.mode" in err for err in payload["errors"])


def test_gather_adapter_rejects_unknown_source(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  pinterest:\n    mode: direct-cli\n",
        encoding="utf-8",
    )
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is False
    assert any("gather_provider.pinterest" in err for err in payload["errors"])


def _run_advise(tmp_path: Path) -> dict[str, object]:
    script = ROOT / "skills" / "public" / "gather" / "scripts" / "advise_google_workspace_path.py"
    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_advise_google_workspace_path_stops_under_none(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  google_workspace:\n    mode: 'none'\n",
        encoding="utf-8",
    )

    payload = _run_advise(tmp_path)
    assert payload["provider_mode"] == "none"
    assert payload["doctor_status"] == "skipped"
    assert "missing-capability" in payload["operator_prompt"]


def test_advise_google_workspace_path_routes_under_host_mediated(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  google_workspace:\n    mode: host-mediated\n",
        encoding="utf-8",
    )

    payload = _run_advise(tmp_path)
    assert payload["provider_mode"] == "host-mediated"
    assert payload["doctor_status"] == "skipped"
    assert "host" in payload["operator_prompt"].lower()
