from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from .support import ROOT


def _load_release_module(name: str):
    module_path = ROOT / "skills" / "public" / "release" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"release_{name}", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_adapter_defaults_to_gh_backend(tmp_path: Path) -> None:
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    backend = payload["data"]["release_backend"]
    assert backend == {"id": "gh", "binary": "gh", "commands": None}


def test_release_adapter_parses_custom_backend(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "release_backend:",
                "  id: ceal-github",
                "  binary: ceal",
                "  commands:",
                "    auth_check:",
                "      - ceal",
                "      - github",
                "      - auth",
                "      - status",
                "    release_view:",
                "      - ceal",
                "      - github",
                "      - release",
                "      - view",
                "      - '{tag}'",
                "    release_create:",
                "      - ceal",
                "      - github",
                "      - release",
                "      - create",
                "      - '{tag}'",
                "      - '--title'",
                "      - '{title}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    backend = payload["data"]["release_backend"]
    assert backend["id"] == "ceal-github"
    assert backend["binary"] == "ceal"
    assert backend["commands"]["release_view"] == ["ceal", "github", "release", "view", "{tag}"]


def test_release_adapter_preserves_fresh_checkout_probes(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "fresh_checkout_probes:",
                "- npm run claims:evidence-state:check",
                "- npm run generated:drift:check",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    assert payload["data"]["fresh_checkout_probes"] == [
        "npm run claims:evidence-state:check",
        "npm run generated:drift:check",
    ]


def test_release_adapter_rejects_invalid_fresh_checkout_probes(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "fresh_checkout_probes:",
                "- npm run ok",
                "- 12",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is False
    assert "fresh_checkout_probes must be a list of strings" in payload["errors"]


def test_release_adapter_warns_when_non_gh_backend_lacks_commands(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "release_backend:",
                "  id: ceal-github",
                "  binary: ceal",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    assert any("release_backend.id=ceal-github" in warning for warning in payload["warnings"])


def test_backend_command_uses_template_when_provided() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {
        "id": "ceal-github",
        "binary": "ceal",
        "commands": {"release_view": ["ceal", "github", "release", "view", "{tag}"]},
    }

    command = helpers.backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
    )

    assert command == ["ceal", "github", "release", "view", "v1.2.3"]


def test_backend_command_falls_back_to_default_for_gh() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    command = helpers.backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
    )

    assert command == ["gh", "release", "view", "v1.2.3"]


def test_backend_command_errors_on_non_gh_without_template() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "ceal-github", "binary": "ceal", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(backend, "release_create", ["gh", "release", "create"])

    assert "ceal-github" in str(exc.value)
    assert "release_create" in str(exc.value)


def test_backend_command_rejects_caller_sub_outside_op_allowlist() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(
            backend,
            "release_view",
            ["gh", "release", "view", "{tag}"],
            tag="v1.2.3",
            title="not allowed for view",
        )

    assert "title" in str(exc.value)
    assert "release_view" in str(exc.value)


def test_backend_command_rejects_adapter_template_with_unknown_placeholder() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {
        "id": "ceal-github",
        "binary": "ceal",
        "commands": {
            "release_view": ["ceal", "release", "view", "{tag}", "--audit", "{audit_id}"],
        },
    }

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(
            backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
        )

    assert "audit_id" in str(exc.value)
    assert "unknown placeholders" in str(exc.value)


def test_backend_command_rejects_unknown_op() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(backend, "rogue_op", ["gh", "release", "list"])

    assert "rogue_op" in str(exc.value)
    assert "OP_PLACEHOLDERS" in str(exc.value)
