"""The public-fetch router refuses an unhonored gather declaration instead of routing
`github.com` by a path the repo did not sanction.

Row 23 of slice 5, and the flip runs in the PERMISSIVE direction on an external-fetch
boundary. Measured at `e1c93ba17`: a repo declaring `gather_provider.github.mode: none` —
"this repo has no GitHub path" — resolved to `direct-cli` under `version: 9`, routing
`github.com` to `github-grant-or-cli` instead of `github-missing-capability`. The repo
said it had no path; the router offered to take one.

The module's `except Exception -> "direct-cli"` fallback is deliberately left in place. A
missing gather resolver or an unloadable module is not "the repo declared something this
reader ignored", and degrading there keeps web fetch working in a checkout that ships no
gather skill. The guard fires only where a declaration exists and was not honored.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .support import ROOT

ROUTES = "skills/support/web-fetch/scripts/route_public_fetch_routes.py"

DECLARED = """version: {v}
repo: demo
gather_provider:
  github:
    mode: {mode}
"""


def _repo(tmp_path: Path, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "gather-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _module(name: str):
    from tests.script_main import load_script_module

    return load_script_module(name, ROOT / ROUTES)


@pytest.mark.parametrize("mode", ["none", "host-mediated"])
@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_an_unhonored_declaration_refuses_rather_than_rerouting(
    tmp_path: Path, mode: str, version: str
) -> None:
    module = _module(f"web_fetch_routes_refusal_{mode}_{version.replace('!', 'x').replace(' ', '')}")
    repo = _repo(tmp_path, DECLARED.format(v=version, mode=mode))
    with pytest.raises(SystemExit) as excinfo:
        module.resolve_github_mode(repo)
    assert "gather-adapter.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    ("mode", "route"),
    [("none", "github-missing-capability"), ("host-mediated", "github-host-mediated")],
)
def test_a_speakable_version_routes_by_what_the_repo_declared(
    tmp_path: Path, mode: str, route: str
) -> None:
    """The polarity control, asserting the ROUTE and not just the mode.

    `none -> github-missing-capability` is the arm that matters: under a refused version
    it became `github-grant-or-cli`, which is the router offering a path the repo said it
    did not have.
    """
    module = _module(f"web_fetch_routes_control_{mode}")
    repo = _repo(tmp_path, DECLARED.format(v="1", mode=mode))
    resolved = module.resolve_github_mode(repo)
    assert resolved == mode
    assert module.route_id_for_host("github.com", github_mode=resolved) == route


def test_no_adapter_at_all_still_degrades_rather_than_refusing(tmp_path: Path) -> None:
    """The fallback this guard deliberately does NOT take over.

    A repo with no gather adapter has declared nothing, so there is nothing to dishonor —
    and web fetch has to keep working in a checkout that ships no gather skill. The
    module's own `except Exception -> direct-cli` arm covers the missing-resolver and
    unloadable-module cases for the same reason.
    """
    module = _module("web_fetch_routes_no_adapter")
    assert module.resolve_github_mode(_repo(tmp_path, None)) == "direct-cli"


def test_a_null_repo_root_is_unchanged(tmp_path: Path) -> None:
    """`resolve_github_mode(None)` short-circuits before any adapter work and must stay
    that way; the guard sits after that early return."""
    module = _module("web_fetch_routes_null_root")
    assert module.resolve_github_mode(None) == "direct-cli"


def test_an_ordinary_invalid_field_is_not_refused(tmp_path: Path) -> None:
    """`valid: false` from an unrelated bad field must NOT refuse, and the declared mode
    must still be honored — asserting both halves, because an exception-free run alone
    passes equally for a guard that refuses nothing beside a resolver that honors
    nothing."""
    module = _module("web_fetch_routes_ordinary_invalid")
    adapter = DECLARED.format(v="1", mode="none").replace("repo: demo", "repo: demo\npreset_version: 3")
    assert module.resolve_github_mode(_repo(tmp_path, adapter)) == "none"
