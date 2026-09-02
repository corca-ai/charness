from __future__ import annotations

from pathlib import Path

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT


def _load_gather_module(name: str):
    module_path = ROOT / "skills" / "public" / "gather" / "scripts" / f"{name}.py"
    return load_script_module(f"gather_{name}", module_path)


def test_gather_adapter_defaults_are_public_source_only(tmp_path: Path) -> None:
    # gather is public-source only: the credentialed org providers (slack, notion)
    # are removed entirely, not merely defaulted off. github stays direct-cli (dev
    # tooling reaching public content); google_workspace defaults to `none` (no
    # repo-owned CLI → host-mediated/export/browser, never a credentialed default).
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    provider = payload["data"]["gather_provider"]
    assert set(provider) == {"github", "google_workspace"}
    assert provider["github"] == {"mode": "direct-cli"}
    assert provider["google_workspace"] == {"mode": "none"}


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


def test_gather_adapter_rejects_unknown_mode(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  github:\n    mode: bogus\n",
        encoding="utf-8",
    )
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is False
    assert any("gather_provider.github.mode" in err for err in payload["errors"])


def test_gather_adapter_rejects_credentialed_org_sources(tmp_path: Path) -> None:
    # Slack/Notion are no longer valid gather sources: acquiring credentialed org
    # data is the consuming runtime's capability/connector responsibility, so
    # declaring one is a parser error rather than a silent opt-in.
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  slack:\n    mode: host-mediated\n",
        encoding="utf-8",
    )
    resolve = _load_gather_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is False
    assert any("gather_provider.slack" in err for err in payload["errors"])


def _run_advise(tmp_path: Path) -> dict[str, object]:
    script = ROOT / "skills" / "public" / "gather" / "scripts" / "advise_google_workspace_path.py"
    result = run_loaded_script_main(
        str(script),
        _load_gather_module("advise_google_workspace_path"),
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


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
