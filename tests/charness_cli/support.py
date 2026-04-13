from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "charness"
REPO_COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".venv",
    "node_modules",
    "history",
)
def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
def run_cli_in_repo(repo_root: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo_root / "charness"), *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
def build_test_path(*bin_dirs: Path) -> str:
    ordered = [*bin_dirs, Path(sys.executable).resolve().parent]
    git_binary = shutil.which("git")
    if git_binary is not None:
        ordered.append(Path(git_binary).resolve().parent)
    unique: list[str] = []
    seen: set[str] = set()
    for path in ordered:
        value = str(path)
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return os.pathsep.join(unique)
def make_repo_copy(tmp_path: Path) -> Path:
    repo_copy = tmp_path / "repo"
    shutil.copytree(ROOT, repo_copy, ignore=REPO_COPY_IGNORE)
    return repo_copy
def make_git_repo_copy(tmp_path: Path) -> Path:
    repo_copy = make_repo_copy(tmp_path)
    subprocess.run(["git", "init"], cwd=repo_copy, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo_copy, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo_copy,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_copy, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "seed repo copy"],
        cwd=repo_copy,
        check=True,
        capture_output=True,
        text=True,
    )
    return repo_copy
def make_release_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "release-fixtures.json"
    fixture.write_text(
        json.dumps(
            {
                "corca-ai/charness": {
                    "tag_name": "v0.1.0",
                    "html_url": "https://github.com/corca-ai/charness/releases/tag/v0.1.0",
                    "published_at": "2026-04-12T00:00:00Z",
                    "assets": [{"name": "charness"}],
                },
                "corca-ai/cautilus": {
                    "tag_name": "v1.2.3",
                    "html_url": "https://github.com/corca-ai/cautilus/releases/tag/v1.2.3",
                    "published_at": "2026-04-10T00:00:00Z",
                    "assets": [{"name": "cautilus-linux-amd64.tar.gz"}],
                },
                "vercel-labs/agent-browser": {
                    "tag_name": "v0.25.3",
                    "html_url": "https://github.com/vercel-labs/agent-browser/releases/tag/v0.25.3",
                    "published_at": "2026-04-07T02:11:00Z",
                    "assets": [{"name": "agent-browser-x86_64-unknown-linux-gnu.tar.gz"}],
                },
                "corca-ai/specdown": {
                    "tag_name": "v0.47.2",
                    "html_url": "https://github.com/corca-ai/specdown/releases/tag/v0.47.2",
                    "published_at": "2026-04-05T01:03:46Z",
                    "assets": [{"name": "specdown_0.47.2_linux_amd64.tar.gz"}],
                },
                "googleworkspace/cli": {
                    "tag_name": "v0.22.5",
                    "html_url": "https://github.com/googleworkspace/cli/releases/tag/v0.22.5",
                    "published_at": "2026-03-31T18:53:24Z",
                    "assets": [{"name": "google-workspace-cli-x86_64-unknown-linux-gnu.tar.gz"}],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return fixture
def rewrite_seeded_home_paths(home_root: Path, *, old_home_root: Path) -> None:
    old = str(old_home_root)
    new = str(home_root)
    text_paths = (
        home_root / ".local" / "share" / "charness" / "install-state.json",
        home_root / ".local" / "share" / "charness" / "host-state.json",
        home_root / ".local" / "share" / "charness" / "version-state.json",
        home_root / ".claude" / "plugins" / "known_marketplaces.json",
        home_root / ".claude" / "plugins" / "installed_plugins.json",
        home_root / ".local" / "bin" / "claude-charness",
    )
    for path in text_paths:
        if not path.is_file():
            continue
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
def make_fake_claude(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "claude"
    script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            import sys
            from pathlib import Path

            home = Path(os.environ["HOME"])
            plugins_root = home / ".claude" / "plugins"
            plugins_root.mkdir(parents=True, exist_ok=True)
            known_marketplaces_path = plugins_root / "known_marketplaces.json"
            installed_plugins_path = plugins_root / "installed_plugins.json"

            def load_json(path: Path, default):
                if not path.exists():
                    return default
                return json.loads(path.read_text(encoding="utf-8"))

            def save_json(path: Path, payload):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

            def ensure_marketplace(name: str, source: str):
                data = load_json(known_marketplaces_path, {})
                data[name] = {
                    "source": {"source": "path", "path": source},
                    "installLocation": str(home / ".claude" / "plugins" / "marketplaces" / name),
                }
                save_json(known_marketplaces_path, data)

            def ensure_installed(plugin_ref: str):
                plugin, marketplace = plugin_ref.split("@", 1)
                data = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
                plugins = data.setdefault("plugins", {})
                install_path = home / ".claude" / "plugins" / "cache" / marketplace / plugin / "local"
                install_path.mkdir(parents=True, exist_ok=True)
                plugins[plugin_ref] = [
                    {
                        "scope": "user",
                        "installPath": str(install_path),
                        "version": "local",
                        "installedAt": "2026-04-11T00:00:00.000Z",
                        "lastUpdated": "2026-04-11T00:00:00.000Z",
                    }
                ]
                save_json(installed_plugins_path, data)

            def uninstall(plugin_ref: str):
                data = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
                plugins = data.setdefault("plugins", {})
                plugins.pop(plugin_ref, None)
                save_json(installed_plugins_path, data)

            args = sys.argv[1:]
            if args == ["--version"]:
                print("fake-claude 0.0.0")
                raise SystemExit(0)
            if args[:3] == ["plugins", "marketplace", "add"]:
                ensure_marketplace("corca-charness", args[-1])
                raise SystemExit(0)
            if args[:3] == ["plugins", "marketplace", "update"]:
                raise SystemExit(0)
            if args[:3] == ["plugins", "marketplace", "remove"]:
                data = load_json(known_marketplaces_path, {})
                data.pop(args[-1], None)
                save_json(known_marketplaces_path, data)
                raise SystemExit(0)
            if args[:2] == ["plugins", "install"]:
                ensure_installed(args[-1])
                raise SystemExit(0)
            if args[:2] == ["plugins", "update"]:
                ensure_installed(args[-1])
                raise SystemExit(0)
            if args[:2] == ["plugins", "enable"]:
                raise SystemExit(0)
            if args[:2] == ["plugins", "uninstall"]:
                uninstall(args[-1])
                raise SystemExit(0)
            if args[:2] == ["plugins", "list"]:
                data = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
                print("Installed plugins:")
                print("")
                for plugin_ref, entries in data.get("plugins", {}).items():
                    version = entries[0].get("version", "local")
                    print(f"  ❯ {plugin_ref}")
                    print(f"    Version: {version}")
                    print("    Scope: user")
                    print("    Status: ✔ enabled")
                    print("")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script
def make_fake_codex(tmp_path: Path, *, fail_plugin_install: bool = False) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "codex"
    template = textwrap.dedent(
        """#!/usr/bin/env python3
import json
import os
import shutil
import sys
from pathlib import Path

FAIL_PLUGIN_INSTALL = __FAIL_PLUGIN_INSTALL__

def load_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))

def plugin_source_from_marketplace(marketplace_path: Path, plugin_name: str):
    data = load_json(marketplace_path, {})
    marketplace_name = data.get("name")
    for plugin in data.get("plugins", []):
        if isinstance(plugin, dict) and plugin.get("name") == plugin_name:
            source = plugin.get("source", {})
            raw_path = source.get("path")
            if isinstance(raw_path, str):
                source_path = (marketplace_path.parent.parent.parent / raw_path.removeprefix("./")).resolve()
                return marketplace_name, source_path
    raise SystemExit(2)

def plugin_version(source_path: Path):
    manifest_path = source_path / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path, {})
    version = manifest.get("version")
    return version if isinstance(version, str) and version else "local"

def install_plugin(codex_home: Path, marketplace_path: Path, plugin_name: str):
    marketplace_name, source_path = plugin_source_from_marketplace(marketplace_path, plugin_name)
    version = plugin_version(source_path)
    target = codex_home / "plugins" / "cache" / marketplace_name / plugin_name / version
    base_root = target.parent
    if base_root.exists():
        shutil.rmtree(base_root)
    shutil.copytree(source_path, target)
    config_path = codex_home / "config.toml"
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    plugin_key = f"{plugin_name}@{marketplace_name}"
    if f'[plugins."{plugin_key}"]' not in existing:
        existing = existing.rstrip() + ("\\n\\n" if existing.strip() else "") + f'[plugins."{plugin_key}"]\\nenabled = true\\n'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(existing, encoding="utf-8")
    return version

args = sys.argv[1:]
if args == ["--help"]:
    print("Codex CLI")
    raise SystemExit(0)
if args[:3] == ["app-server", "--listen", "stdio://"]:
    codex_home = Path(os.environ["CODEX_HOME"])
    for raw in sys.stdin:
        message = json.loads(raw)
        method = message.get("method")
        req_id = message.get("id")
        if method == "initialize":
            print(json.dumps({
                "id": req_id,
                "result": {"serverInfo": {"name": "fake-codex-app-server", "version": "0.0.0"}, "capabilities": {}},
            }), flush=True)
            continue
        if method == "notifications/initialized":
            continue
        if method == "plugin/install":
            if FAIL_PLUGIN_INSTALL:
                print(json.dumps({
                    "id": req_id,
                    "error": {"code": -32000, "message": "forced plugin/install failure"},
                }), flush=True)
                continue
            params = message.get("params", {})
            version = install_plugin(codex_home, Path(params["marketplacePath"]), params["pluginName"])
            print(json.dumps({
                "id": req_id,
                "result": {"authPolicy": "ON_INSTALL", "appsNeedingAuth": [], "version": version},
            }), flush=True)
            continue
    raise SystemExit(0)
raise SystemExit(0)
"""
    ).replace('__FAIL_PLUGIN_INSTALL__', repr(fail_plugin_install))
    script.write_text(template, encoding="utf-8")
    script.chmod(0o755)
    return script
@pytest.fixture(scope="module")
def seeded_managed_home(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    seed_root = tmp_path_factory.mktemp("managed-home-seed")
    source_root = seed_root / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root = seed_root / "home"
    fake_claude = make_fake_claude(seed_root)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    init_result = run_cli("init", "--home-root", str(home_root), "--repo-url", str(source_repo), env=env)
    assert init_result.returncode == 0, init_result.stderr
    return {"home_root": home_root}
def clone_seeded_managed_home(tmp_path: Path, seeded_home_root: Path) -> tuple[Path, dict[str, str]]:
    home_root = tmp_path / "home"
    shutil.copytree(seeded_home_root, home_root)
    rewrite_seeded_home_paths(home_root, old_home_root=seeded_home_root)
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    return home_root, env
def make_fake_agent_browser(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "agent-browser"
    script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("agent-browser 0.25.3")
                raise SystemExit(0)
            if args == ["--help"]:
                print("agent-browser")
                raise SystemExit(0)
            if args == ["upgrade"]:
                print("upgraded")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script
def make_fake_brew_specdown(tmp_path: Path) -> tuple[Path, Path]:
    brew_root = tmp_path / "linuxbrew"
    bin_dir = brew_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    brew_script = bin_dir / "brew"
    brew_script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--prefix"]:
                print({str(brew_root)!r})
                raise SystemExit(0)
            if args == ["upgrade", "corca-ai/tap/specdown"]:
                print("upgraded specdown")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    brew_script.chmod(0o755)
    specdown_script = bin_dir / "specdown"
    specdown_script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["version"]:
                print("0.47.2")
                raise SystemExit(0)
            if args == ["run", "-help"]:
                print("Usage: specdown run", file=sys.stderr)
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    specdown_script.chmod(0o755)
    return brew_script, specdown_script
def make_fake_npm_gws(tmp_path: Path) -> tuple[Path, Path]:
    npm_prefix = tmp_path / "npm-global"
    bin_dir = npm_prefix / "bin"
    package_bin = npm_prefix / "lib" / "node_modules" / "@googleworkspace" / "cli"
    bin_dir.mkdir(parents=True, exist_ok=True)
    package_bin.mkdir(parents=True, exist_ok=True)
    npm_script = tmp_path / "bin" / "npm"
    npm_script.parent.mkdir(parents=True, exist_ok=True)
    npm_script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["prefix", "-g"]:
                print({str(npm_prefix)!r})
                raise SystemExit(0)
            if args == ["install", "-g", "@googleworkspace/cli@latest"]:
                print("updated @googleworkspace/cli")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    npm_script.chmod(0o755)
    gws_impl = package_bin / "run-gws.js"
    gws_impl.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("gws 0.18.1")
                print("This is not an officially supported Google product.")
                raise SystemExit(0)
            if args == ["auth", "--help"]:
                print("login")
                raise SystemExit(0)
            if args == ["auth", "status"]:
                print(json.dumps({"token_valid": True}))
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    gws_impl.chmod(0o755)
    gws_link = bin_dir / "gws"
    gws_link.symlink_to(gws_impl)
    return npm_script, gws_link
