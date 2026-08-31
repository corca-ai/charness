from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

from .repo_shapes import install_two_commit_repo
from .support import run_script

SCRIPT = "skills/public/quality/scripts/check_changed_line_coverage.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _rev(repo: Path, ref: str = "HEAD") -> str:
    return subprocess.run(
        ["git", "rev-parse", ref], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _write_adapter(repo: Path, eligible_globs: list[str]) -> None:
    lines = [
        "version: 1",
        "repo: testrepo",
        "output_dir: charness-artifacts/quality",
        "changed_line_mutation_gate:",
        "  coverage_json: cov.json",
    ]
    if eligible_globs:
        lines.append("  eligible_globs:")
        lines += [f"    - {g}" for g in eligible_globs]
    else:
        lines.append("  eligible_globs: []")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    """Install the shared two-commit checkout used by coverage-gate tests."""
    repo, base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {"pkg/foo.py": "a = 1\nb = 2\nc = 3\n"},
        {"pkg/foo.py": "a = 1\nb = 2\nc = 3\nd = 4\n"},
        first_message="base",
        second_message="add line 4",
    )
    return repo, base


def _write_coverage(repo: Path, *, missing: list[int], executed: list[int]) -> None:
    # coverage.py's own report format, not this gate's output surface: still JSON.
    (repo / "cov.json").write_text(
        json.dumps({"files": {"pkg/foo.py": {"executed_lines": executed, "missing_lines": missing}}}),
        encoding="utf-8",
    )


def _stamp(repo: Path, base: str) -> None:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--stamp-marker")
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["fingerprint"]


def test_flags_uncovered_changed_line(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        "HEAD",
        real_process=True,
    )
    assert result.returncode == 1, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == ["pkg/foo.py"]


def test_passes_when_changed_line_covered(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[], executed=[1, 2, 3, 4])
    _stamp(repo, base)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert payload["changed_pool_files"] == ["pkg/foo.py"]


def test_inert_when_no_eligible_globs(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, [])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["inert"] is True


def test_stale_coverage_skips_non_blocking(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    # No marker stamped => coverage is treated as stale => non-blocking skip.
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert "stale" in payload["reason"]


def test_no_base_sha_is_non_blocking(tmp_path: Path) -> None:
    repo, _ = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", "")
    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["ok"] is True


def test_invalid_adapter_fails_closed(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nchanged_line_mutation_gate: not-a-mapping\n", encoding="utf-8"
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base)
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert any("changed_line_mutation_gate must be a mapping" in e for e in payload["adapter_errors"])
    assert payload["verdict"] == "adapter-invalid"


def test_a_head_that_is_not_the_checked_out_head_is_unestablished_not_a_pass(tmp_path: Path) -> None:
    """Parent-reproduced false green: a stale head silently emptied the range.

    Coverage is read from the LIVE worktree while the change set is diffed against
    `--head-sha`, so a head that is not the checked-out HEAD makes the mapping and
    the measurement describe different trees. `base..base` is empty, so the gate
    reported `verdict: ok` ("no eligible changed files in this range") and exit 0
    over a tree it had just been failing -- and the payload never named the head
    it used.

    The repo-local sibling (`scripts/changed_line_run_trust.py:probe_run_trust`)
    has refused this since it was written; the portable gate had no counterpart
    and its only guard, `_false_green_warning`, returns early on exactly this case.
    """
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)

    # Same repo, same base: an honest run blocks on the uncovered changed line.
    honest = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base)
    assert honest.returncode == 1, honest.stdout + honest.stderr
    assert yaml.safe_load(honest.stdout)["blocking"] == ["pkg/foo.py"]

    # A third commit, so there is a head that is BOTH stale and the end of a
    # non-empty range. `base..stale_head` still touches pkg/foo.py, which is the
    # refusable case; an empty range is the other arm and exits 0 by design.
    stale_head = _rev(repo)
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add line 5")

    stale = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", stale_head)
    assert stale.returncode == 3, stale.stdout + stale.stderr
    payload = yaml.safe_load(stale.stdout)
    # `ok: True` on purpose: a could-not-judge is not a coverage failure, and exit
    # 3 is the bucket that says so. Collapsing it onto exit 1 is what made this
    # arrive at a consumer's CI as "your changed lines are uncovered".
    assert payload["ok"] is True
    assert payload["unestablished"] is True
    assert "is not the checked-out HEAD" in payload["reason"]

    # There is one output channel now, so the verdict WORD has to carry what the
    # `UNESTABLISHED:`/`OK:` prefixes used to: a could-not-judge run must not
    # narrate itself as a pass even though `blocking` is empty and `ok` is True.
    assert payload["verdict"] == "unestablished"
    assert payload["analyzed_head"] == stale_head


def test_a_stale_head_over_an_empty_range_discloses_instead_of_blocking(tmp_path: Path) -> None:
    """Exit 0, because refusing an empty scope is an incoherent blocker.

    `check_changed_line_mutation_coverage.py` reached this the hard way and wrote
    down why: exit 3's contract scopes it to a NON-EMPTY changed set, and refusing
    before the changed set is known let a push be stopped with the reason "no
    eligible files changed" -- on the gate whose credibility is the whole point.

    But the disclosure must not vanish with the refusal. The empty scope belongs to
    the ANALYZED head, not to this tree, and a bare `verdict: ok` is exactly the
    false green this arm exists to close -- so the reason is carried on the report
    and shouted on stderr, even though the exit code is 0.
    """
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", base)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload.get("unestablished") is None
    # Untouched on purpose: consumers prefix-match this to recognise an empty scope.
    assert payload["reason"] == "no eligible changed files in this range"
    assert "is not the checked-out HEAD" in payload["analyzed_head_not_checked_out_head"]
    assert "ANALYZED head's, not this tree's" in result.stderr, result.stderr
    # The verdict word is `ok` here by design, so the head it judged has to travel
    # with it: an `ok` that does not name a non-default head IS the false green.
    assert payload["verdict"] == "ok"
    assert payload["analyzed_head"] == base


def test_an_unresolvable_head_refuses_instead_of_crashing(tmp_path: Path) -> None:
    """`_false_green_warning` used to re-raise `GitUnavailable` after `run_gate`
    had already built the UNESTABLISHED report, so the process died with a
    traceback: the operator got no parseable payload at all. Exit 1, not 3 --
    leniency granted because the head is a different tree must not be inherited
    by a head the gate could not resolve at all."""
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "nosuchref")
    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["verdict"] == "unestablished"
    assert "Traceback" not in result.stderr, result.stderr


def test_an_annotated_tag_on_head_is_not_treated_as_a_different_tree(tmp_path: Path) -> None:
    """One resolver, not two. The scope check peeled with `^{commit}` while
    `_false_green_warning` used a bare `rev-parse`, so an annotated tag on the
    checked-out commit read as the same head here and a different head there --
    clearing the run to a verdict while the guard against an uncommitted-changes
    false green silently switched itself off."""
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)
    _git(repo, "tag", "-a", "v1", "-m", "release")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "v1")
    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload.get("unestablished") is None
    assert payload["blocking"] == ["pkg/foo.py"]
    # The RESOLVED commit, not the tag name, is what gets recorded and reported --
    # both on the raw report and on the verdict block the old human line carried.
    assert payload["resolved_head_sha"] == _rev(repo)
    assert payload["verdict"] == "fail"
    assert payload["analyzed_head"] == _rev(repo)


def test_an_env_supplied_head_is_refused_and_named_the_same_way(tmp_path: Path) -> None:
    """The head can arrive from `$MUTATION_HEAD_SHA`, not just from the CLI.

    That is the shape the scheduled mutation workflow produces (it exports the
    range for the whole sampler step), so an operator who never typed `--head-sha`
    could still get a verdict over a range nobody asked for. The refusal must be
    identical, and the analyzed head must be named next to the verdict word --
    not only buried in the raw report fields.
    """
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])
    _write_coverage(repo, missing=[4], executed=[1, 2, 3])
    _stamp(repo, base)

    stale_head = _rev(repo)
    (repo / "pkg" / "foo.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "add line 5")

    env = {**os.environ, "MUTATION_HEAD_SHA": stale_head}
    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base, env=env)
    assert result.returncode == 3, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["verdict"] == "unestablished"
    assert payload["analyzed_head"] == stale_head

    # The workflow's own shape -- head EQUALS the checked-out HEAD -- still renders
    # a real verdict, so the refusal is scoped to the mismatch and not to the env.
    head = _rev(repo)
    _stamp(repo, base)
    matching = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base,
                          env={**os.environ, "MUTATION_HEAD_SHA": head})
    assert matching.returncode == 1, matching.stdout + matching.stderr
    matching_payload = yaml.safe_load(matching.stdout)
    assert matching_payload["verdict"] == "fail"
    assert matching_payload["analyzed_head"] == head


def test_help_explains_repo_root_and_offers_no_json_option() -> None:
    """`--repo-root` is still documented; `--json` is gone, not merely undocumented.

    Output is unconditionally YAML now, so a help text that still advertised a
    `--json` toggle would document a flag the parser rejects. Both halves are
    asserted: the surviving option keeps its explanation, and the removed one is
    absent from help AND refused by the parser (argparse exit 2), so an operator
    or script carrying the old invocation fails loudly instead of silently
    getting a different output shape.
    """
    result = run_script(SCRIPT, "--help")
    assert result.returncode == 0, result.stderr
    expected = {
        "--repo-root": "Repository root containing the quality adapter and changed files",
    }
    for option, fragment in expected.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", result.stdout, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", result.stdout[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(result.stdout)
        option_block = re.sub(r"\s+", " ", result.stdout[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"

    assert not re.search(r"^\s*--json\b", result.stdout, re.MULTILINE), result.stdout

    rejected = run_script(SCRIPT, "--json")
    assert rejected.returncode == 2, rejected.stdout + rejected.stderr
    assert "unrecognized arguments: --json" in rejected.stderr, rejected.stderr


def test_a_git_failure_is_unestablished_not_an_empty_change_set(tmp_path: Path) -> None:
    """S25, parent-reproduced: an unresolvable base_sha passed as `ok: true`.

    `_git_lines` collapsed a nonzero git exit to `[]`, so the gate reported "no
    eligible changed files in this range" and never invoked the blocking
    classifier at all. Recorded in the 2026-07-28 triage sweep as high severity;
    reproduced by the parent before this fix, which upgrades it from
    SUBAGENT-CONFIRMED to parent-reproduced.
    """
    repo, base = _seed_repo(tmp_path)
    _write_adapter(repo, ["pkg/**/*.py"])

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", "deadbeef" * 5)

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["unestablished"] is True
    assert "could not establish the changed set" in payload["reason"]

    # And the same run must not narrate itself as a pass. With `blocking` empty,
    # the report fell through to the `ok` verdict while exiting 1.
    assert payload["verdict"] == "unestablished"

    # A resolvable base over the same tree still passes, so the new arm is not
    # simply refusing everything.
    clean = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base)
    assert clean.returncode == 0, clean.stdout + clean.stderr
    clean_payload = yaml.safe_load(clean.stdout)
    assert clean_payload["ok"] is True
    assert clean_payload["verdict"] == "ok"


def test_verdict_renders_one_word_per_report_shape() -> None:
    """The verdict WORD, tested directly -- now a payload field, not a text line.

    `unestablished` reports carry an empty `blocking` list, so before this
    existed they fell through to the `ok` arm while the process exited 1. Each
    arm is asserted here because the shape that produced the wrong word was a
    fall-through, not a wrong branch.
    """
    module = import_repo_module(__file__, "skills.public.quality.scripts.check_changed_line_coverage")
    verdict = module.verdict
    adapter_invalid = verdict({"adapter_errors": ["bad glob"], "blocking": []})
    assert adapter_invalid["verdict"] == "adapter-invalid"
    assert adapter_invalid["verdict_detail"].startswith("quality adapter invalid:")
    inert = verdict({"adapter_errors": [], "inert": True, "blocking": []})
    assert inert["verdict"] == "inert"
    assert "inert" in inert["verdict_detail"]
    assert verdict({"adapter_errors": [], "unestablished": True, "blocking": [], "reason": "git said no"}) == {
        "verdict": "unestablished",
        "verdict_detail": "git said no",
    }
    failing = verdict({"adapter_errors": [], "blocking": ["a.py", "b.py"]})
    assert failing["verdict"] == "fail"
    assert failing["verdict_detail"].startswith("2 changed file(s)")
    assert verdict({"adapter_errors": [], "blocking": [], "reason": "nothing in range"}) == {
        "verdict": "ok",
        "verdict_detail": "nothing in range",
    }


def test_a_git_failure_while_fingerprinting_is_also_unestablished(tmp_path: Path) -> None:
    """The freshness fingerprint reads git too, and had the same collapse.

    Separate call site from the changed-set probe, so it needs its own arm: a
    stale-marker verdict computed from a file set git would not report is a
    freshness claim over a scope that was never read.
    """
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo, base = _seed_repo(tmp_path)
    (repo / "cov.json").write_text('{"files": {}}', encoding="utf-8")

    calls = {"n": 0}

    def flaky(repo_root, args):
        calls["n"] += 1
        # Dispatch on the ARGS, not the call count. Counting made this stub depend
        # on how many `git` calls `run_gate` happens to make before the fingerprint,
        # so adding the analyzed-head resolution silently re-pointed the failure at
        # the changed-set probe and the test asserted the wrong arm's message.
        if args[:2] == ["rev-parse", "--verify"]:
            return ["0" * 40]
        if ".." in args[-1]:  # the changed-set probe succeeds
            return ["pkg/mod.py"]
        raise gate.GitUnavailable("git refused the fingerprint probe")

    original = gate._git_lines
    gate._git_lines = flaky
    try:
        report = gate.run_gate(
            repo,
            {"eligible_globs": ["pkg/**/*.py"], "coverage_json": "cov.json"},
            base_sha=base,
            head_sha="HEAD",
            classify=lambda **k: {"blocking": []},
            load_statement_lines=lambda *a, **k: {},
            marker_path=lambda path: path.with_suffix(".fp"),
        )
    finally:
        gate._git_lines = original

    assert report["ok"] is False
    assert report["unestablished"] is True
    assert "coverage-freshness fingerprint" in report["reason"]


def test_an_unborn_repo_cannot_resolve_head_and_says_so(tmp_path: Path) -> None:
    """`git init` with no commit yet: `HEAD` names no commit.

    Every other arm resolves the REQUESTED head and compares it to `HEAD`, so a
    `HEAD` that does not resolve has to be its own refusal. Reading it as "the
    heads match" would clear a repo with no history to a verdict.
    """
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")

    scope = gate.resolve_head_scope(repo, "HEAD")

    assert scope.resolved is None
    assert scope.mismatch is None
    assert "could not resolve `HEAD`" in scope.error


@pytest.mark.parametrize("head_sha", ["HEAD", "deadbeef"])
def test_a_silent_rev_parse_is_a_refusal_not_an_index_error(tmp_path: Path, head_sha: str) -> None:
    """`_git_lines` returning empty on a zero exit is the defensive case.

    Real `git rev-parse --verify <x>^{commit}` always prints a sha when it exits
    0, so this arm is not reachable through git -- it guards the `_git_lines`
    CONTRACT. Deleting it would not delete the case; it would turn a clean
    refusal into an `IndexError` on `resolved[0]`, which is the same
    could-not-look-reads-as-something shape one layer down.
    """
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo, _ = _seed_repo(tmp_path)
    original = gate._git_lines

    def silent(repo_root, args):
        # `HEAD` resolves for the non-HEAD case, so the second probe is the one
        # under test; the `HEAD` case trips on the first.
        if head_sha != "HEAD" and args[-1] == "HEAD^{commit}":
            return original(repo_root, args)
        return []

    gate._git_lines = silent
    try:
        scope = gate.resolve_head_scope(repo, head_sha)
    finally:
        gate._git_lines = original

    assert scope.resolved is None
    assert scope.mismatch is None
    assert "could not resolve" in scope.error


def test_the_false_green_probe_swallows_a_git_failure_instead_of_killing_the_run(tmp_path: Path) -> None:
    """The warning is advisory; the verdict is not.

    `_git_lines` raises on a nonzero git exit, and this probe runs AFTER the
    report exists, so an unhandled raise here destroyed a verdict the gate had
    already reached -- no verdict word, no parseable payload at all. Losing the
    advisory is the correct trade; losing the verdict is not.
    """
    entry = import_repo_module(__file__, "skills.public.quality.scripts.check_changed_line_coverage")
    gate = entry._gate_lib
    repo, _ = _seed_repo(tmp_path)
    original = gate._git_lines

    def fail_the_worktree_probe(repo_root, args):
        if args[:2] == ["diff", "--name-only"]:
            raise gate.GitUnavailable("git refused the worktree probe")
        return original(repo_root, args)

    gate._git_lines = fail_the_worktree_probe
    try:
        assert entry._false_green_warning(repo, "HEAD", ["pkg/**/*.py"], []) is None
    finally:
        gate._git_lines = original


def test_stamp_marker_refuses_to_certify_a_file_set_it_could_not_read(tmp_path: Path) -> None:
    """Deliberately uncaught: a marker is a freshness CLAIM the consumer trusts."""
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    repo, base = _seed_repo(tmp_path)
    original = gate._git_lines

    def refuse(repo_root, args):
        raise gate.GitUnavailable("git refused")

    gate._git_lines = refuse
    try:
        with pytest.raises(gate.GitUnavailable):
            gate.stamp_marker(
                repo, {"eligible_globs": ["pkg/**/*.py"], "coverage_json": "cov.json"}, base,
                marker_path=lambda path: path.with_suffix(".fp"),
            )
    finally:
        gate._git_lines = original


def test_gate_config_is_the_one_reader_for_both_entry_points() -> None:
    """The producer that stamps the marker and the consumer that checks it must
    be scoped to the same file set, so they read the adapter block through one
    function rather than each unpacking it."""
    gate = import_repo_module(__file__, "skills.public.quality.scripts.changed_line_coverage_gate_lib")
    assert gate.gate_config({"eligible_globs": ["a"], "coverage_json": "c.json", "exclude_globs": ["b"]}) == (
        ["a"], "c.json", ["b"]
    )
    assert gate.gate_config({}) == ([], "", [])
