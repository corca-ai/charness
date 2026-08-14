"""Chunked routing reports resolvable-ness FACTS per backlog entry (#459).

An entry is planned against long after it was written; its cited paths may have
moved and its cited issues may have been closed. Before this, staleness surfaced
only when someone happened to open the cited file -- i.e. after a slice plan
already existed against it.

All offline: provider state lookups run through an injected runner stub, so no
live tracker call is made.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "public" / "handoff" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def staleness():
    return _load("chunked_routing_staleness")


@pytest.fixture(scope="module")
def lib():
    return _load("chunked_routing_lib")


@pytest.fixture(scope="module")
def backend():
    return _load("chunked_routing_issue_backend")


# --- path resolvability ---------------------------------------------------


def test_missing_paths_reports_only_the_paths_that_no_longer_exist(staleness, tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "here.md").write_text("x", encoding="utf-8")
    result = staleness.missing_paths(
        tmp_path, ("docs/here.md", "docs/gone.md", "scripts/also-gone.py")
    )
    assert result == ("docs/gone.md", "scripts/also-gone.py")


def test_a_cited_directory_counts_as_existing(staleness, tmp_path):
    # A backlog line legitimately names a surface, not always a file.
    (tmp_path / "skills" / "public" / "handoff").mkdir(parents=True)
    assert staleness.missing_paths(tmp_path, ("skills/public/handoff/",)) == ()


def test_paths_outside_the_repo_root_are_skipped_not_reported(staleness, tmp_path):
    # The chunker has no basis to call an out-of-tree reference stale, and
    # reporting one would fire on every entry citing an upstream fragment.
    assert staleness.missing_paths(tmp_path, ("../elsewhere/gone.md",)) == ()


def test_no_repo_root_means_no_path_claims(staleness):
    assert staleness.missing_paths(None, ("docs/gone.md",)) == ()


# --- issue state ----------------------------------------------------------


def _state_runner(states: dict[int, str]):
    def run(argv):
        number = int(next(part for part in argv if part.isdigit()))
        if number not in states:
            raise RuntimeError("no such issue")
        return {"number": number, "state": states[number]}

    return run


def test_resolve_issue_states_skips_the_numbers_already_known_open(staleness):
    calls: list[list[str]] = []

    def run(argv):
        calls.append(argv)
        return {"number": 451, "state": "CLOSED"}

    states = staleness.resolve_issue_states(
        "acme/repo", [449, 451], known_open=(449,), runner=run
    )
    assert states == {449: "OPEN", 451: "CLOSED"}
    # 449 was already proven open by the listing, so it costs no provider call.
    assert len(calls) == 1


def test_unresolvable_issue_is_unknown_and_never_reported_closed(staleness):
    states = staleness.resolve_issue_states(
        "acme/repo", [9999], runner=_state_runner({})
    )
    assert states == {9999: "UNKNOWN"}
    assert staleness.closed_issues((9999,), states) == ()


def test_closed_issues_reports_only_non_open_non_unknown(staleness):
    states = {448: "CLOSED", 459: "OPEN", 9999: "UNKNOWN"}
    assert staleness.closed_issues((448, 459, 9999), states) == (448,)


def test_a_non_github_open_state_is_never_reported_closed(staleness):
    # Closed is an allow-list, not "anything that is not OPEN". GitLab says
    # `opened`, Linear says `started`/`backlog`, Jira says `In Progress`; under a
    # deny-list every one of those live issues would be reported stale.
    states = {1: "OPENED", 2: "STARTED", 3: "IN PROGRESS", 4: "BACKLOG", 5: "REOPENED"}
    assert staleness.closed_issues(tuple(states), states) == ()
    # ...and each is reported as UNRESOLVED rather than silently treated as open.
    assert staleness.unresolved_issues(tuple(states), states) == ()


def test_recognized_closed_vocabularies_are_reported_closed(staleness):
    states = {1: "CLOSED", 2: "DONE", 3: "RESOLVED", 4: "MERGED", 5: "COMPLETED"}
    assert staleness.closed_issues(tuple(states), states) == (1, 2, 3, 4, 5)


def test_partial_resolution_is_legible_as_partial(staleness, lib):
    # 19 of 20 lookups failed and one came back CLOSED. Without the unresolved
    # count this renders as `issue_states_checked: true, closed_issue_count: 1`
    # and reads as a clean check.
    numbers = tuple(range(1, 21))
    states = {n: ("CLOSED" if n == 1 else "UNKNOWN") for n in numbers}
    entry = lib.HandoffEntry(index=1, title="t", body="b", referenced_issues=numbers)
    annotated = staleness.annotate_entries([entry], repo_root=None, issue_states=states)
    assert annotated[0].closed_issues == (1,)
    assert len(annotated[0].unresolved_issues) == 19
    summary = staleness.staleness_summary(
        annotated, paths_checked=False, issue_states_checked=True
    )
    assert summary["closed_issue_count"] == 1
    assert summary["unresolved_issue_count"] == 19


def test_unresolved_is_empty_when_the_check_never_ran(staleness, lib):
    # `unresolved` means "asked and not answered". Never-asked is reported by
    # issue_states_checked, not by marking every cited issue unresolved.
    entry = lib.HandoffEntry(index=1, title="t", body="b", referenced_issues=(1, 2))
    annotated = staleness.annotate_entries([entry], repo_root=None, issue_states=None)
    assert annotated[0].unresolved_issues == ()


def test_an_unresolvable_path_is_skipped_not_crashed(staleness, tmp_path):
    # A symlink loop makes resolve() raise. That is our failure to resolve, not
    # evidence the citation is stale, and it must not abort the whole parse.
    loop = tmp_path / "loop"
    loop.symlink_to(loop)
    assert staleness.missing_paths(tmp_path, ("loop/x.md",)) == ()


def test_non_gh_backend_without_a_state_command_yields_unknown(backend):
    assert (
        backend.issue_state(
            "acme/repo", 1, backend={"id": "acme", "binary": "acme", "commands": {}}
        )
        is None
    )


def test_declared_backend_state_command_is_used_verbatim(backend):
    seen: list[list[str]] = []

    def run(argv):
        seen.append(argv)
        return {"number": 7, "state": "closed"}

    state = backend.issue_state(
        "acme/repo",
        7,
        backend={"id": "acme", "binary": "acme", "commands": {"view_state": ["show", "{repo}", "{number}"]}},
        runner=run,
    )
    assert seen == [["acme", "show", "acme/repo", "7"]]
    assert state == "CLOSED"


# --- annotation + summary -------------------------------------------------


def test_annotate_entries_fills_both_fact_fields(staleness, lib, tmp_path):
    entry = lib.HandoffEntry(
        index=1,
        title="stale entry",
        body="body",
        referenced_paths=("docs/gone.md",),
        referenced_issues=(451,),
    )
    annotated = staleness.annotate_entries(
        [entry], repo_root=tmp_path, issue_states={451: "CLOSED"}
    )
    assert annotated[0].missing_paths == ("docs/gone.md",)
    assert annotated[0].closed_issues == (451,)
    # Facts only: the entry itself survives, unranked and undropped.
    assert annotated[0].title == "stale entry"


def test_summary_distinguishes_not_checked_from_nothing_stale(staleness, lib):
    entry = lib.HandoffEntry(index=1, title="t", body="b", referenced_issues=(451,))
    unchecked = staleness.annotate_entries([entry], repo_root=None, issue_states=None)
    summary = staleness.staleness_summary(
        unchecked, paths_checked=False, issue_states_checked=False
    )
    assert summary["paths_checked"] is False
    assert summary["issue_states_checked"] is False
    assert summary["closed_issue_count"] == 0


def test_issue_source_seam_resolves_states_through_the_injected_runner(staleness, tmp_path):
    # Proves the wiring, not just the staleness module: the same adapter/target
    # resolution the open-issue listing uses also serves the state lookup, so no
    # second provider literal was introduced.
    states, diagnostic = staleness.resolve_states_for_repo(
        REPO_ROOT, [448, 459], known_open=(459,), runner=_state_runner({448: "CLOSED"})
    )
    assert diagnostic is None
    assert states == {448: "CLOSED", 459: "OPEN"}


def test_unresolvable_tracker_reports_a_diagnostic_and_no_states(staleness, tmp_path):
    # A bare directory has no git remote and no issue adapter, so target
    # resolution fails; the caller must learn "not run", never "nothing closed".
    states, diagnostic = staleness.resolve_states_for_repo(tmp_path, [448])
    assert states == {}
    assert diagnostic is not None and diagnostic["stage"]


def test_issue_state_lookup_refuses_invalid_adapter_before_provider(staleness, tmp_path):
    adapter = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 7\n"
        "issue_backend:\n  id: hostile\n  binary: hostile-provider\n",
        encoding="utf-8",
    )
    provider_called = False

    def runner(argv):
        nonlocal provider_called
        provider_called = True
        return {}

    states, diagnostic = staleness.resolve_states_for_repo(
        tmp_path, [448], runner=runner
    )

    assert states == {}
    assert provider_called is False
    assert diagnostic == {
        "stage": "load_issue_adapter",
        "provider_attempted": False,
        "type": "InvalidAdapter",
        "message": "version must be 1",
    }


# --- pipeline carriage ----------------------------------------------------


def test_from_dict_round_trips_the_fact_fields(lib):
    entry = lib.HandoffEntry(
        index=3,
        title="t",
        body="b",
        referenced_paths=("docs/gone.md",),
        referenced_issues=(451,),
        missing_paths=("docs/gone.md",),
        closed_issues=(451,),
    )
    assert lib.HandoffEntry.from_dict(entry.to_dict()) == entry


def test_chunk_proposal_packet_carries_the_facts_to_the_agent(lib):
    entry = lib.HandoffEntry(
        index=1,
        title="t",
        body="b",
        referenced_paths=("docs/gone.md",),
        referenced_issues=(451,),
        missing_paths=("docs/gone.md",),
        closed_issues=(451,),
    )
    packet = lib.build_chunk_proposal_packet(
        [entry], staleness={"paths_checked": True, "issue_states_checked": False}
    )
    # The checked-flags must reach the packet the proposing agent reads. Without
    # them an empty `closed_issues` asserts "no closed issues" for a check that
    # structurally cannot have run.
    assert packet["staleness"] == {"paths_checked": True, "issue_states_checked": False}
    source = packet["sources"][0]
    assert source["missing_paths"] == ["docs/gone.md"]
    assert source["closed_issues"] == [451]


def test_parser_cli_reports_a_missing_path_without_dropping_the_entry(tmp_path):
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "handoff.md").write_text(
        "\n".join(
            [
                "# Handoff",
                "",
                "## Next Session",
                "",
                "1. **Real work.** Fix [the thing](../docs/gone.md), tracked as #451.",
                "2. **Other work.** Touch `docs/handoff.md` instead.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python3",
            str(SCRIPTS / "parse_handoff_entries.py"),
            "--repo-root",
            str(repo),
            "--handoff-path",
            str(repo / "docs" / "handoff.md"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["staleness"]["paths_checked"] is True
    # No tracker call without --with-issues, so the issue half is NOT CHECKED
    # rather than silently reported as clean.
    assert payload["staleness"]["issue_states_checked"] is False
    entries = {entry["title"]: entry for entry in payload["entries"]}
    assert len(entries) == 2, "a stale-path entry must not be dropped"
    stale = next(entry for entry in payload["entries"] if "Real work" in entry["title"])
    assert stale["missing_paths"] == ["docs/gone.md"]
    assert stale["closed_issues"] == []
    fresh = next(entry for entry in payload["entries"] if "Other work" in entry["title"])
    assert fresh["missing_paths"] == []


def test_the_checked_flags_survive_the_whole_pipeline_to_the_packet(tmp_path):
    """parse -> propose_merges -> prepare_chunk_packet keeps `staleness`.

    The per-entry facts are only readable alongside the flags that say whether
    each check ran, so a stage that drops the summary hands the proposing agent a
    clean bill of health it never earned.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "handoff.md").write_text(
        "# Handoff\n\n## Next Session\n\n1. **Work.** Fix [it](../docs/gone.md).\n",
        encoding="utf-8",
    )

    def run(script: str, args: list[str], stdin: str | None = None) -> str:
        result = subprocess.run(
            ["python3", str(SCRIPTS / script), *args],
            cwd=REPO_ROOT,
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        return result.stdout

    parsed = run(
        "parse_handoff_entries.py",
        ["--repo-root", str(repo), "--handoff-path", str(repo / "docs" / "handoff.md")],
    )
    merged = run("propose_merges.py", [], parsed)
    packet = yaml.safe_load(run("prepare_chunk_packet.py", ["--repo-root", str(repo)], parsed))

    assert yaml.safe_load(merged)["staleness"]["paths_checked"] is True
    assert packet["staleness"]["paths_checked"] is True
    assert packet["staleness"]["issue_states_checked"] is False
    assert packet["sources"][0]["missing_paths"] == ["docs/gone.md"]
