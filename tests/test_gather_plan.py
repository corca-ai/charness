from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from tests.quality_gates.support import run_script

PLAN = "skills/public/gather/scripts/gather_plan.py"
ROOT = Path(__file__).resolve().parents[1]


def load_plan_module():
    spec = importlib.util.spec_from_file_location("gather_plan_under_test", ROOT / PLAN)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gather_plan_exposes_twitter_exact_source_contract(tmp_path) -> None:
    result = run_script(
        PLAN,
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://x.com/acme/status/1799999999999999999",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "gather.run_plan.v1"
    assert payload["route"]["route_id"] == "twitter-syndication"
    assert payload["exact_source"]["required"] is True
    assert payload["exact_source"]["substitution_policy"] == "never_as_original"
    assert payload["exact_source"]["terminal_verdicts"] == [
        "exact-fetched",
        "exact-blocked",
        "exact-unavailable",
    ]
    assert payload["next_action"]["command"][:3] == [
        "python3",
        "$SKILL_DIR/scripts/gather_public_url.py",
        "--repo-root",
    ]


def test_gather_plan_helper_fallbacks(monkeypatch) -> None:
    module = load_plan_module()
    assert module._source_kind("README.md") == "local_or_unknown"
    assert module._exact_source_contract("direct-then-fallback") == {
        "required": False,
        "owner": "support/web-fetch",
        "terminal_verdicts": [],
    }
    monkeypatch.setattr(module.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)
    try:
        module._load_resolve_adapter()
    except ImportError as exc:
        assert "resolve_adapter.py" in str(exc)
    else:
        raise AssertionError("expected ImportError")


def test_gather_plan_prefers_reddit_feed_route(tmp_path) -> None:
    result = run_script(
        PLAN,
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://www.reddit.com/r/python/",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["route"]["route_id"] == "reddit-feed"
    assert payload["exact_source"]["owner"] == "support/web-fetch/reddit_source"
    assert payload["exact_source"]["route_order"] == [
        "rss-feed",
        "json-endpoint",
        "direct-page",
    ]
    assert payload["exact_source"]["substitution_policy"] == (
        "preserve_source_url_and_do_not_present_search_results_as_the_source"
    )
    assert any(read["path"] == "../../support/web-fetch/references/routing-table.md" for read in payload["required_reads"])


def test_gather_plan_resolves_support_route_in_exported_plugin_layout(tmp_path: Path) -> None:
    user_repo = tmp_path / "user_repo"
    user_repo.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "plugins" / "charness" / "skills" / "gather" / "scripts" / "gather_plan.py"),
            "--repo-root",
            str(user_repo),
            "--url",
            "https://www.reddit.com/r/python/",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["route"]["route_id"] == "reddit-feed"
    assert payload["exact_source"]["owner"] == "support/web-fetch/reddit_source"


def test_exported_gather_plan_honors_github_adapter_mode(tmp_path: Path) -> None:
    user_repo = tmp_path / "user_repo"
    (user_repo / ".agents").mkdir(parents=True)
    (user_repo / ".agents" / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  github:\n    mode: host-mediated\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "plugins" / "charness" / "skills" / "gather" / "scripts" / "gather_plan.py"),
            "--repo-root",
            str(user_repo),
            "--url",
            "https://github.com/corca-ai/charness",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["route"]["route_id"] == "github-host-mediated"
