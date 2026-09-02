from __future__ import annotations

import re
from pathlib import Path

import yaml

from scripts.plugin_export import packaging_lib
from tests.script_main import load_script_module, run_loaded_script_main

PLAN = "skills/public/gather/scripts/gather_plan.py"
ROOT = Path(__file__).resolve().parents[1]


def _export_plugin(tmp_path: Path) -> Path:
    plugin = tmp_path / "plugin"
    manifest = packaging_lib.load_manifest(ROOT, "charness")
    packaging_lib.export_plugin_tree(ROOT, plugin, manifest)
    return plugin


def load_plan_module():
    return load_script_module("gather_plan_under_test", ROOT / PLAN)


def run_plan(module, *args: str):
    return run_loaded_script_main("gather_plan.py", module, *args)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each fragment belongs to its option block, not only usage text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_gather_plan_help_describes_all_options() -> None:
    result = run_plan(load_plan_module(), "--help")

    assert result.returncode == 0, result.stderr
    _assert_help_pairs(
        result.stdout,
        {
            "--repo-root": "Repo root for gather adapter and route resolution.",
            "--url": "Public URL to plan for gathering.",
            "--intent": "Gather intent: single source or collection.",
            "--browser-mode": "When to use a browser fallback.",
        },
    )


def test_gather_plan_exposes_twitter_exact_source_contract(tmp_path) -> None:
    result = run_plan(
        load_plan_module(),
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://x.com/acme/status/1799999999999999999",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["schema_version"] == "gather.run_plan.v1"
    assert payload["route"]["route_id"] == "twitter-syndication"
    assert payload["exact_source"]["required"] is True
    assert payload["exact_source"]["substitution_policy"] == "never_as_original"
    assert payload["exact_source"]["terminal_verdicts"] == [
        "exact-fetched",
        "exact-blocked",
        "exact-unavailable",
    ]
    assert payload["exact_source"]["terminal_categories"] == [
        "acquired",
        "provider-required",
        "auth-browser-required",
        "unsupported",
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
    monkeypatch.setattr(
        module.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None
    )
    try:
        module._load_resolve_adapter()
    except ImportError as exc:
        assert "resolve_adapter.py" in str(exc)
    else:
        raise AssertionError("expected ImportError")


def test_gather_plan_prefers_reddit_feed_route(tmp_path) -> None:
    result = run_plan(
        load_plan_module(),
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://www.reddit.com/r/python/",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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
    assert any(
        read["path"] == "../../support/web-fetch/references/routing-table.md"
        for read in payload["required_reads"]
    )


def test_gather_plan_redirects_provider_hosts_to_advisers(tmp_path) -> None:
    # north star: a Slack/Google Workspace URL is provider-backed, so the planner
    # must hand the judge the right next move instead of silently planning a generic
    # public fetch. Slack is credentialed org data that public-only gather does not
    # acquire; Google Workspace routes to the workspace path adviser. GitHub/public
    # URLs keep the public-fetch next_action.
    module = load_plan_module()
    slack = run_plan(
        module,
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://acme.slack.com/archives/C0/p1700000000000000",
    )
    assert slack.returncode == 0, slack.stderr
    slack_payload = yaml.safe_load(slack.stdout)
    assert slack_payload["source_owner"]["source"] == "slack"
    assert slack_payload["source_owner"]["adviser"] is None
    assert slack_payload["next_action"]["kind"] == "credentialed_source_out_of_scope"
    assert "command" not in slack_payload["next_action"]
    assert "capability/connector" in slack_payload["next_action"]["redirect"]

    gdoc = run_plan(
        module, "--repo-root", str(tmp_path), "--url", "https://docs.google.com/document/d/abc/edit"
    )
    assert gdoc.returncode == 0, gdoc.stderr
    gdoc_payload = yaml.safe_load(gdoc.stdout)
    assert gdoc_payload["source_owner"]["source"] == "google_workspace"
    assert (
        gdoc_payload["next_action"]["command"][1]
        == "$SKILL_DIR/scripts/advise_google_workspace_path.py"
    )

    public = run_plan(
        module, "--repo-root", str(tmp_path), "--url", "https://docs.python.org/3/library/json.html"
    )
    public_payload = yaml.safe_load(public.stdout)
    assert public_payload["source_owner"] is None
    assert public_payload["next_action"]["command"][1] == "$SKILL_DIR/scripts/gather_public_url.py"


def test_gather_plan_resolves_support_route_in_exported_plugin_layout(tmp_path: Path) -> None:
    user_repo = tmp_path / "user_repo"
    user_repo.mkdir()
    plugin = _export_plugin(tmp_path)

    plugin_plan = load_script_module(
        "exported_gather_plan_under_test",
        plugin / "skills" / "gather" / "scripts" / "gather_plan.py",
    )
    result = run_plan(
        plugin_plan,
        "--repo-root",
        str(user_repo),
        "--url",
        "https://www.reddit.com/r/python/",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route"]["route_id"] == "reddit-feed"
    assert payload["exact_source"]["owner"] == "support/web-fetch/reddit_source"


def test_exported_gather_plan_honors_github_adapter_mode(tmp_path: Path) -> None:
    user_repo = tmp_path / "user_repo"
    (user_repo / ".agents").mkdir(parents=True)
    (user_repo / ".agents" / "gather-adapter.yaml").write_text(
        "version: 1\nrepo: demo\ngather_provider:\n  github:\n    mode: host-mediated\n",
        encoding="utf-8",
    )
    plugin = _export_plugin(tmp_path)

    plugin_plan = load_script_module(
        "exported_gather_plan_github_mode_under_test",
        plugin / "skills" / "gather" / "scripts" / "gather_plan.py",
    )
    result = run_plan(
        plugin_plan,
        "--repo-root",
        str(user_repo),
        "--url",
        "https://github.com/corca-ai/charness",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["route"]["route_id"] == "github-host-mediated"
