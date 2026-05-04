from __future__ import annotations

import pytest

pytest_plugins = ["tests.quality_gates.support", "tests.charness_cli.support"]


@pytest.fixture(autouse=True)
def _disable_plugin_fallback_manifests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
