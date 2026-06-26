from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from tests.repo_copy import ROOT

CLI = ROOT / "charness"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


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
    ordered = [*bin_dirs, Path(sys.executable).resolve().parent, Path("/usr/bin"), Path("/bin")]
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


def _current_charness_release_tag() -> str:
    version = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
    return f"v{version}"


def make_release_fixture(tmp_path: Path, *, charness_tag: str | None = None) -> Path:
    fixture = tmp_path / "release-fixtures.json"
    resolved_charness_tag = charness_tag or _current_charness_release_tag()
    fixture.write_text(
        json.dumps(
            {
                "corca-ai/charness": {
                    "tag_name": resolved_charness_tag,
                    "html_url": f"https://github.com/corca-ai/charness/releases/tag/{resolved_charness_tag}",
                    "published_at": "2026-04-12T00:00:00Z",
                    "assets": [{"name": "charness"}],
                },
                "corca-ai/cautilus": {
                    "tag_name": "v1.2.3",
                    "html_url": "https://github.com/corca-ai/cautilus/releases/tag/v1.2.3",
                    "published_at": "2026-04-10T00:00:00Z",
                    "assets": [{"name": "cautilus-linux-amd64.tar.gz"}],
                },
                "corca-ai/nose": {
                    "tag_name": "v0.4.0",
                    "html_url": "https://github.com/corca-ai/nose/releases/tag/v0.4.0",
                    "published_at": "2026-06-04T00:00:00Z",
                    "assets": [{"name": "nose-cli-installer.sh"}],
                },
                "cli/cli": {
                    "tag_name": "v2.90.1",
                    "html_url": "https://github.com/cli/cli/releases/tag/v2.90.1",
                    "published_at": "2026-04-08T00:00:00Z",
                    "assets": [{"name": "gh_2.90.1_linux_amd64.tar.gz"}],
                },
                "vercel-labs/agent-browser": {
                    "tag_name": "v0.25.3",
                    "html_url": "https://github.com/vercel-labs/agent-browser/releases/tag/v0.25.3",
                    "published_at": "2026-04-07T02:11:00Z",
                    "assets": [{"name": "agent-browser-x86_64-unknown-linux-gnu.tar.gz"}],
                },
                "gitleaks/gitleaks": {
                    "tag_name": "v8.27.2",
                    "html_url": "https://github.com/gitleaks/gitleaks/releases/tag/v8.27.2",
                    "published_at": "2026-04-06T00:00:00Z",
                    "assets": [{"name": "gitleaks_8.27.2_linux_x64.tar.gz"}],
                },
                "corca-ai/specdown": {
                    "tag_name": "v0.47.2",
                    "html_url": "https://github.com/corca-ai/specdown/releases/tag/v0.47.2",
                    "published_at": "2026-04-05T01:03:46Z",
                    "assets": [{"name": "specdown_0.47.2_linux_amd64.tar.gz"}],
                },
                "charmbracelet/glow": {
                    "tag_name": "v2.1.2",
                    "html_url": "https://github.com/charmbracelet/glow/releases/tag/v2.1.2",
                    "published_at": "2026-04-09T20:31:45Z",
                    "assets": [{"name": "glow_2.1.2_Linux_arm64.tar.gz"}],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return fixture


def make_support_sync_fixture(tmp_path: Path) -> Path:
    fixture_root = tmp_path / "support-fixtures"
    mappings: dict[str, str] = {}
    tool_layouts = {
        "cautilus": ("corca-ai/cautilus@main", "skills/cautilus-agent"),
        "agent-browser": ("vercel-labs/agent-browser@main", "skills/agent-browser"),
        "specdown": ("corca-ai/specdown@main", "cmd/specdown/skills/specdown"),
    }
    for tool_id, (repo, skill_subpath) in tool_layouts.items():
        skill_root = fixture_root / tool_id / skill_subpath
        skill_root.mkdir(parents=True, exist_ok=True)
        skill_root.joinpath("SKILL.md").write_text(f"---\nname: {tool_id}\ndescription: \"fixture\"\n---\n\n# {tool_id}\n", encoding="utf-8")
        mappings[repo] = str(fixture_root / tool_id)
    fixture_path = tmp_path / "support-sync-fixtures.json"
    fixture_path.write_text(json.dumps(mappings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return fixture_path


def rewrite_seeded_home_paths(home_root: Path, *, old_home_root: Path) -> None:
    old = str(old_home_root)
    new = str(home_root)
    text_paths = (
        home_root / ".local" / "state" / "charness" / "install-state.json",
        home_root / ".local" / "state" / "charness" / "host-state.json",
        home_root / ".local" / "state" / "charness" / "version-state.json",
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
    script.write_text((FIXTURES / "fake_claude.py").read_text(encoding="utf-8"), encoding="utf-8")
    script.chmod(0o755)
    return script
def make_fake_codex(tmp_path: Path, *, fail_plugin_install: bool = False) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "codex"
    script.write_text((FIXTURES / "fake_codex.py").read_text(encoding="utf-8"), encoding="utf-8")
    if fail_plugin_install:
        script.with_name(".codex-fail-plugin-install").write_text("1\n", encoding="utf-8")
    script.chmod(0o755)
    return script
@pytest.fixture(scope="session")
def seeded_managed_home(
    tmp_path_factory: pytest.TempPathFactory, seeded_charness_git_repo: Path
) -> dict[str, Path]:
    from tests.repo_copy import clone_seeded_charness_repo
    from tests.seed_cache import get_or_build

    def build(staging: Path) -> None:
        source_root = staging / "source"
        source_root.mkdir()
        source_repo = clone_seeded_charness_repo(source_root, seeded_charness_git_repo)
        home_root = staging / "home"
        fake_claude = make_fake_claude(staging)
        env = os.environ.copy()
        env["HOME"] = str(home_root)
        env["PATH"] = build_test_path(fake_claude.parent)
        env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(make_support_sync_fixture(staging))
        init_result = run_cli(
            "init", "--home-root", str(home_root), "--repo-url", str(source_repo), env=env
        )
        assert init_result.returncode == 0, init_result.stderr

    seed_root = get_or_build("managed-home-seed", build)
    return {"home_root": seed_root / "home"}
def clone_seeded_managed_home(
    tmp_path: Path, seeded_home_root: Path, *, share_source_checkout: bool = False
) -> tuple[Path, dict[str, str]]:
    home_root = tmp_path / "home"
    source_rel = Path(".agents") / "src" / "charness"
    ignore = None
    if share_source_checkout:
        source_parts = source_rel.parts

        def ignore_source_checkout(src: str, names: list[str]) -> set[str]:
            try:
                rel_parts = Path(src).relative_to(seeded_home_root).parts
            except ValueError:
                return set()
            if rel_parts == source_parts[:-1] and source_parts[-1] in names:
                return {source_parts[-1]}
            return set()

        ignore = ignore_source_checkout
    shutil.copytree(seeded_home_root, home_root, ignore=ignore)
    if share_source_checkout:
        source_link = home_root / source_rel
        source_link.parent.mkdir(parents=True, exist_ok=True)
        try:
            source_link.symlink_to((seeded_home_root / source_rel).resolve(), target_is_directory=True)
        except OSError:
            shutil.copytree(seeded_home_root / source_rel, source_link)
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
    shutil.copy2(FIXTURES / "fake_agent_browser.py", script)
    script.chmod(0o755)
    return script


def make_fake_npm_agent_browser(tmp_path: Path) -> tuple[Path, Path]:
    npm_prefix = tmp_path / "npm-global"
    bin_dir = npm_prefix / "bin"
    package_bin = npm_prefix / "lib" / "node_modules" / "agent-browser"
    bin_dir.mkdir(parents=True, exist_ok=True)
    package_bin.mkdir(parents=True, exist_ok=True)
    npm_script = tmp_path / "bin" / "npm"
    npm_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURES / "fake_npm_agent_browser.py", npm_script)
    npm_script.with_suffix(".json").write_text(
        json.dumps({"npm_prefix": str(npm_prefix), "bin_dir": str(bin_dir), "fixtures": str(FIXTURES)}, indent=2) + "\n",
        encoding="utf-8",
    )
    npm_script.chmod(0o755)
    browser_impl = package_bin / "agent-browser-linux-x64"
    shutil.copy2(FIXTURES / "fake_agent_browser.py", browser_impl)
    browser_impl.chmod(0o755)
    browser_link = bin_dir / "agent-browser"
    browser_link.symlink_to(browser_impl)
    return npm_script, browser_link


def make_fake_update_all_toolchain(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    cargo = bin_dir / "cargo"
    shutil.copy2(FIXTURES / "fake_cargo_update_all.py", cargo)
    cargo.with_suffix(".json").write_text(
        json.dumps({"bin_dir": str(bin_dir), "fixtures": str(FIXTURES)}, indent=2) + "\n",
        encoding="utf-8",
    )
    cargo.chmod(0o755)

    uv = bin_dir / "uv"
    shutil.copy2(FIXTURES / "fake_uv_update_all.py", uv)
    uv.with_suffix(".json").write_text(
        json.dumps({"bin_dir": str(bin_dir), "fixtures": str(FIXTURES)}, indent=2) + "\n",
        encoding="utf-8",
    )
    uv.chmod(0o755)
    return bin_dir


def make_fake_go_specdown(tmp_path: Path) -> tuple[Path, Path]:
    gopath = tmp_path / "go"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    go_script = bin_dir / "go"
    go_script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import os
            import pathlib
            import sys

            gopath = pathlib.Path({str(gopath)!r})
            gobin = os.environ.get("GOBIN")
            install_root = pathlib.Path(gobin) if gobin else gopath / "bin"
            install_root.mkdir(parents=True, exist_ok=True)
            args = sys.argv[1:]
            if args == ["env", "GOPATH"]:
                print(str(gopath))
                raise SystemExit(0)
            if args == ["install", "github.com/gitleaks/gitleaks/v8@latest"]:
                for target in (install_root / "gitleaks", pathlib.Path({str(bin_dir)!r}) / "gitleaks"):
                    target.write_text(
                        "#!/usr/bin/env python3\\n"
                        "import sys\\n"
                        "args = sys.argv[1:]\\n"
                        "if args == ['version']:\\n"
                        "    print('gitleaks version 8.27.2')\\n"
                        "elif args == ['help']:\\n"
                        "    print('gitleaks help')\\n"
                        "else:\\n"
                        "    print('gitleaks')\\n",
                        encoding="utf-8",
                    )
                    target.chmod(0o755)
                print("installed gitleaks")
                raise SystemExit(0)
            if args == ["install", "github.com/charmbracelet/glow/v2@latest"]:
                for target in (install_root / "glow", pathlib.Path({str(bin_dir)!r}) / "glow"):
                    target.write_text(
                        "#!/usr/bin/env python3\\n"
                        "import sys\\n"
                        "args = sys.argv[1:]\\n"
                        "if args == ['--version']:\\n"
                        "    print('glow version 2.1.2')\\n"
                        "elif args == ['--help']:\\n"
                        "    print('glow help')\\n"
                        "else:\\n"
                        "    print('glow')\\n",
                        encoding="utf-8",
                    )
                    target.chmod(0o755)
                print("installed glow")
                raise SystemExit(0)
            if args == ["install", "github.com/corca-ai/specdown/cmd/specdown@latest"]:
                print("installed specdown")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    go_script.chmod(0o755)
    specdown_script = gopath / "bin" / "specdown"
    specdown_script.parent.mkdir(parents=True, exist_ok=True)
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
    return go_script, specdown_script
