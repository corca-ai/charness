from __future__ import annotations

import importlib.util
import subprocess
from dataclasses import dataclass
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
                "  id: acme-github",
                "  binary: acme",
                "  commands:",
                "    auth_check:",
                "      - acme",
                "      - github",
                "      - auth",
                "      - status",
                "    release_view:",
                "      - acme",
                "      - github",
                "      - release",
                "      - view",
                "      - '{tag}'",
                "    release_create:",
                "      - acme",
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
    assert backend["id"] == "acme-github"
    assert backend["binary"] == "acme"
    assert backend["commands"]["release_view"] == ["acme", "github", "release", "view", "{tag}"]


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


@pytest.mark.parametrize("adapter_relpath", [".agents/release-adapter.yaml", ".codex/release-adapter.yaml"])
def test_release_adapter_preflight_maps_real_host_changes_to_focused_test(
    tmp_path: Path, adapter_relpath: str
) -> None:
    repo = tmp_path / "repo"
    adapter_path = repo / adapter_relpath
    adapter_path.parent.mkdir(parents=True)
    (repo / "skills" / "public" / "release" / "scripts").mkdir(parents=True)
    (repo / "tests" / "quality_gates").mkdir(parents=True)
    (repo / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py").write_text(
        "print('ok')\n",
        encoding="utf-8",
    )
    (repo / "tests" / "quality_gates" / "test_release_real_host.py").write_text(
        "def test_ok(): pass\n",
        encoding="utf-8",
    )
    adapter_path.write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "real_host_checklist:",
                "- Verify old tool.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "tag", "v0.1.0"], cwd=repo, check=True, capture_output=True, text=True)
    adapter_path.write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "real_host_checklist:",
                "- Verify tokei.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    preflight = _load_release_module("publish_release_preflight")
    payload = preflight.release_adapter_preflight_payload(
        repo,
        release_content_paths=[adapter_relpath],
        previous_version="0.1.0",
    )

    assert payload["status"] == "required"
    assert payload["adapter_paths"] == [adapter_relpath]
    assert "real_host_checklist" in payload["changed_fields"]
    assert ["python3", "skills/public/release/scripts/resolve_adapter.py", "--repo-root", "."] in payload["commands"]
    assert ["pytest", "tests/quality_gates/test_release_real_host.py", "-q"] in payload["commands"]


@dataclass
class _FakeCompleted:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def test_release_adapter_preflight_blocks_on_focused_failure(tmp_path: Path) -> None:
    preflight = _load_release_module("publish_release_preflight")
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        return _FakeCompleted(returncode=1, stderr="focused failure")

    payload = {
        "status": "required",
        "commands": [["pytest", "tests/quality_gates/test_release_real_host.py", "-q"]],
    }

    with pytest.raises(SystemExit) as exc:
        preflight.run_release_adapter_preflight(tmp_path, payload, run_command=fake_run)

    assert calls == [["pytest", "tests/quality_gates/test_release_real_host.py", "-q"]]
    assert "release adapter focused preflight blocked publish before mutation" in str(exc.value)


def test_release_adapter_warns_when_non_gh_backend_lacks_commands(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "release_backend:",
                "  id: acme-github",
                "  binary: acme",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    assert any("release_backend.id=acme-github" in warning for warning in payload["warnings"])


def test_backend_command_uses_template_when_provided() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {
        "id": "acme-github",
        "binary": "acme",
        "commands": {"release_view": ["acme", "github", "release", "view", "{tag}"]},
    }

    command = helpers.backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
    )

    assert command == ["acme", "github", "release", "view", "v1.2.3"]


def test_backend_command_falls_back_to_default_for_gh() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    command = helpers.backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
    )

    assert command == ["gh", "release", "view", "v1.2.3"]


def test_backend_command_errors_on_non_gh_without_template() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "acme-github", "binary": "acme", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(backend, "release_create", ["gh", "release", "create"])

    assert "acme-github" in str(exc.value)
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
        "id": "acme-github",
        "binary": "acme",
        "commands": {
            "release_view": ["acme", "release", "view", "{tag}", "--audit", "{audit_id}"],
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
