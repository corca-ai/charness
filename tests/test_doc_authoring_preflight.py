"""Unit tests for the aggregate doc-authoring preflight (scripts/check_doc_authoring_preflight.py).

The preflight forecasts, in one pass, the constraints an author otherwise
discovers by failing one commit gate at a time. These tests pin three
properties the goal requires:

  - a broken fixture surfaces every violation class in ONE call;
  - a clean fixture is silent;
  - the forecast does NOT drift from the real gates (it reuses them);
  - it stays a non-blocking affordance (absent from the blocking commit gate).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = "scripts/check_doc_authoring_preflight.py"
_pf = import_repo_module(__file__, "scripts.check_doc_authoring_preflight")
_handoff = import_repo_module(__file__, "scripts.validate_handoff_artifact")
_doc_links = import_repo_module(__file__, "scripts.check_doc_links")
_inline_code = import_repo_module(__file__, "scripts.check_markdown_inline_code")
_advisories = import_repo_module(__file__, "scripts.slice_closeout_advisories")
_rules = import_repo_module(__file__, "scripts.doc_authoring_rules")

_BROKEN_FIXTURE = (
    "# Demo Handoff\n"
    "\n"
    "- dash bullet\n"
    "+ plus bullet\n"  # MD004: inconsistent list marker
    "\n"
    "See `scripts/real_target.py` for the entrypoint.\n"  # backticked pathy ref
    "\n"
    "A wrapped `inline code\n"
    "span` here.\n"  # wrapped inline-code span
    "\n"
) + "".join(f"filler line {i}\n" for i in range(1, 71))  # push well past the 70-line cap

_CLEAN_FIXTURE = (
    "# Demo Handoff\n"
    "\n"
    "A clean paragraph with no wrapped spans, no mixed bullets, and no\n"
    "backticked file references.\n"
    "\n"
    "- one bullet\n"
    "- two bullet\n"
)


def _seed_repo(tmp_path: Path, body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(ROOT / ".markdownlint-cli2.jsonc", repo / ".markdownlint-cli2.jsonc")
    # A real tracked file so the backticked pathy ref resolves to an artifact.
    (repo / "scripts" / "real_target.py").write_text("x\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text(body, encoding="utf-8")
    return repo


def _run_script(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(ROOT / PREFLIGHT), "--repo-root", str(repo), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_broken_fixture_surfaces_all_classes_in_one_pass(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _BROKEN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")

    rules = {row["rule"] for row in report.markdownlint["findings"]}
    assert "MD004" in rules, f"markdownlint should forecast MD004; saw {rules}"
    assert report.wrapped_inline_code, "wrapped inline-code span not surfaced"
    assert any(
        row["kind"] == "backticked-ref" and row["detail"] == "scripts/real_target.py"
        for row in report.doc_links
    ), f"backticked pathy ref not surfaced: {report.doc_links}"
    assert report.length["over"], "length cap breach not surfaced"
    assert report.blocked


def test_length_cap_is_read_live_from_the_owning_validator(tmp_path: Path) -> None:
    # No-drift: the forecast cap must equal the gate's live constant, never a
    # hand-copied number.
    repo = _seed_repo(tmp_path, _BROKEN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")
    assert report.length["cap"] == _handoff.MAX_CONTENT_LINES


def test_clean_fixture_is_silent(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")
    assert not report.blocked
    assert not report.markdownlint["findings"]
    assert not report.wrapped_inline_code
    assert not report.doc_links
    assert not report.length["over"]


def test_raw_line_count_surface_forecasts_through_validate_max_lines(tmp_path: Path, monkeypatch) -> None:
    # Every surface registered today declares its own counting/checking pair, so
    # the raw-line fallback (`count_attr`/`check_attr` left None) has no live
    # caller. It is the default a NEW capped surface inherits, so it is pinned
    # here rather than left to be discovered by the first author who omits both.
    surface = _pf.LengthSurface(
        name="synthetic",
        module="scripts.validate_handoff_artifact",
        constant="MAX_CONTENT_LINES",
        label="synthetic artifact",
        matches=lambda rel: rel == "docs/synthetic.md",
    )
    monkeypatch.setattr(_pf, "_length_surfaces", lambda repo_root: (surface,))
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    doc = repo / "docs" / "synthetic.md"

    doc.write_text("x\n" * (_handoff.MAX_CONTENT_LINES + 40), encoding="utf-8")
    over = _pf.collect_length(repo, doc, "docs/synthetic.md", None)
    assert over["surface"] == "synthetic"
    assert over["cap"] == _handoff.MAX_CONTENT_LINES
    assert over["current"] == _handoff.MAX_CONTENT_LINES + 40
    assert over["over"] is True
    assert "synthetic artifact" in (over["detail"] or "")

    doc.write_text("x\n" * 3, encoding="utf-8")
    under = _pf.collect_length(repo, doc, "docs/synthetic.md", None)
    assert under["over"] is False
    assert under["detail"] is None


def test_general_doc_has_no_enforced_length_cap(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    (repo / "docs" / "guide.md").write_text(_CLEAN_FIXTURE, encoding="utf-8")
    report = _pf.build_report(repo, "docs/guide.md", None)
    assert report.length["surface"] is None
    assert report.length["over"] is False


def _gate_verdict_in_process(module: object, argv: list[str]) -> int:
    """Run a gate's real ``main()`` IN-PROCESS (no subprocess boundary) and
    return its verdict (0 pass / 1 fail). This is the independent gate path the
    no-drift cross-check compares the forecast against, while staying in-process
    so it is not a boundary-bypass candidate."""
    saved = sys.argv
    sys.argv = argv
    try:
        return module.main()  # type: ignore[attr-defined]
    except _doc_links.ValidationError:
        return 1
    finally:
        sys.argv = saved


def _real_gate_doc_links(repo: Path) -> int:
    return _gate_verdict_in_process(_doc_links, ["check_doc_links", "--repo-root", str(repo)])


def _real_gate_inline_code(repo: Path) -> int:
    return _gate_verdict_in_process(
        _inline_code, ["check_markdown_inline_code", "--repo-root", str(repo), "--path", "docs/handoff.md"]
    )


def _real_gate_markdownlint(repo: Path) -> int | None:
    cmd = _pf._resolve_markdownlint_cmd()
    if cmd is None:
        return None
    return subprocess.run(
        [*cmd, "--no-globs", "docs/handoff.md"],
        cwd=repo, check=False, capture_output=True, text=True,
    ).returncode


def test_no_drift_broken_fixture_matches_real_gate_verdicts(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _BROKEN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")

    # doc-link forecast fires iff the real check_doc_links gate fails.
    assert bool(report.doc_links) == (_real_gate_doc_links(repo) != 0)
    # wrapped-inline forecast fires iff the real inline-code gate fails.
    assert bool(report.wrapped_inline_code) == (_real_gate_inline_code(repo) != 0)
    # markdownlint forecast fires iff the real markdownlint engine fails.
    ml = _real_gate_markdownlint(repo)
    if ml is not None:
        assert bool(report.markdownlint["findings"]) == (ml != 0)
    # length forecast fires iff the file exceeds the gate's live cap, counted
    # the way the gate counts it (content lines, not raw file length).
    lines = (repo / "docs" / "handoff.md").read_text(encoding="utf-8").splitlines()
    counted = _handoff.content_lines(lines)
    assert report.length["current"] == len(counted)
    assert report.length["over"] == (len(counted) > _handoff.MAX_CONTENT_LINES)


def test_no_drift_clean_fixture_passes_every_real_gate(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    report = _pf.build_report(repo, "docs/handoff.md", "handoff")
    assert not report.blocked
    assert _real_gate_doc_links(repo) == 0
    assert _real_gate_inline_code(repo) == 0
    ml = _real_gate_markdownlint(repo)
    if ml is not None:
        assert ml == 0


def test_cli_exit_code_blocks_on_broken_silent_on_clean(tmp_path: Path) -> None:
    broken = _seed_repo(tmp_path / "b", _BROKEN_FIXTURE)
    assert _run_script(broken, "--path", "docs/handoff.md", "--as-surface", "handoff").returncode == 1
    clean = _seed_repo(tmp_path / "c", _CLEAN_FIXTURE)
    assert _run_script(clean, "--path", "docs/handoff.md", "--as-surface", "handoff").returncode == 0


def test_non_blocking_affordance_guard() -> None:
    # The preflight must stay an affordance, never a precondition: it cannot be
    # wired into the blocking commit-gate plan. (An ADVISORY pointer in the slice
    # closeout is fine; a blocking gate member is not.) Guards Boundaries: "a
    # goal/doc must still commit without running it."
    gate_plan = (ROOT / "scripts" / "staged_commit_gate_plan.py").read_text(encoding="utf-8")
    assert "check_doc_authoring_preflight" not in gate_plan, (
        "doc-authoring preflight must not be a blocking commit-gate member"
    )
    doc = (_pf.__doc__ or "").lower()
    assert "affordance" in doc and "not a gate" in doc


def test_slice_advisory_fires_on_doc_edit_only(capsys) -> None:
    # The S2 discoverability wiring: a slice that edits a general docs/**/*.md
    # gets a non-blocking ADVISORY pointing at the preflight; an unrelated edit
    # stays silent.
    _advisories.advise_doc_surface_preflight(ROOT, ["docs/handoff.md", "scripts/foo.py"])
    fired = capsys.readouterr().err
    assert "check_doc_authoring_preflight.py --path docs/handoff.md" in fired
    assert "ADVISORY" in fired

    _advisories.advise_doc_surface_preflight(ROOT, ["scripts/foo.py", "skills/public/x/SKILL.md"])
    assert capsys.readouterr().err == ""


def test_preflight_forecasts_the_handoff_regenerable_fact_rule(tmp_path: Path) -> None:
    """This rule lived ONLY in `validate_handoff_artifact`'s error string, so it was
    visible only AFTER writing the thing it forbids — which is how a version literal
    reached a handoff draft twice. Briefing a surface's constraints before the edit is
    exactly what this aggregate exists for, and it was not carrying this one.
    """
    repo = _seed_repo(
        tmp_path,
        "# Demo Handoff\n"
        "\n"
        "Shipped v9.9.9 and pinned 9f3a1c2 this session.\n"
        "\n"
        "A `v9.9.9` in code and a 1.4x ratio are not version claims.\n",
    )

    report = _pf.build_report(repo, "docs/handoff.md", "handoff")

    literals = {row["literal"] for row in report.regenerable_facts}
    assert "v9.9.9" in literals
    assert "9f3a1c2" in literals
    assert report.blocked
    # Inline code and a bare ratio must not fire, or the forecast would disagree with
    # the gate about WHAT counts — which is why it reuses the validator's own patterns
    # and scrubbing rather than restating them.
    assert all(row["line"] == 3 for row in report.regenerable_facts), report.regenerable_facts
    assert all(row["replacement"] for row in report.regenerable_facts)


def test_the_forecast_agrees_with_the_gate_on_the_regenerable_rule(tmp_path: Path) -> None:
    """Drift check, in both directions: what the forecast blocks the gate must refuse,
    and what the forecast calls clean the gate must accept."""
    repo = _seed_repo(tmp_path, "# Demo Handoff\n\nShipped v9.9.9.\n")
    doc = repo / "docs" / "handoff.md"

    assert _pf.build_report(repo, "docs/handoff.md", "handoff").regenerable_facts
    try:
        _handoff.validate_no_regenerable_facts(doc)
        raise AssertionError("the gate accepted a version literal the forecast blocked")
    except _handoff.ValidationError:
        pass

    doc.write_text("# Demo Handoff\n\nCarry `git describe --tags --abbrev=0` instead.\n", encoding="utf-8")
    assert _pf.build_report(repo, "docs/handoff.md", "handoff").regenerable_facts == []
    _handoff.validate_no_regenerable_facts(doc)


def test_the_regenerable_rule_is_the_handoffs_not_every_docs(tmp_path: Path) -> None:
    """Falsifiable counterpart: a version in an ordinary doc is legitimate and must not
    be forecast as a block, or the affordance becomes noise everywhere."""
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    (repo / "docs" / "notes.md").write_text("# Notes\n\nThis documents v9.9.9.\n", encoding="utf-8")

    report = _pf.build_report(repo, "docs/notes.md", None)

    assert report.regenerable_facts == []


def test_a_version_inside_a_fenced_block_is_not_a_transcribed_fact(tmp_path: Path) -> None:
    """A fenced block carries the COMMAND this rule asks the author to write instead,
    so scanning it would refuse the replacement it just recommended. The gate skips
    fences for that reason and the forecast must skip them identically, or it would
    send the author back to edit the fix."""
    repo = _seed_repo(
        tmp_path,
        "# Demo Handoff\n"
        "\n"
        "Carry the command:\n"
        "\n"
        "```bash\n"
        "git describe --tags --abbrev=0   # prints v9.9.9 today\n"
        "```\n",
    )

    report = _pf.build_report(repo, "docs/handoff.md", "handoff")

    assert report.regenerable_facts == []
    _handoff.validate_no_regenerable_facts(repo / "docs" / "handoff.md")


def test_the_regenerable_forecast_reaches_the_operator_facing_text(tmp_path: Path) -> None:
    """The findings list is not what an author reads — `format_human` is. Asserting only
    the payload leaves the rendering that carries the remedy unproven, which is the same
    'tested the data, not the verdict the reader sees' gap this preflight exists to close.
    """
    repo = _seed_repo(tmp_path, "# Demo Handoff\n\nShipped v9.9.9.\n")
    rendered = _pf.format_human(_pf.build_report(repo, "docs/handoff.md", "handoff"))

    assert "regenerable-facts: BLOCK (1 finding(s))" in rendered
    assert "line 3" in rendered
    assert "a release or tool version" in rendered
    # the remedy must survive into the text, not just the payload
    assert "git describe --tags --abbrev=0" in rendered

    # The clean branch renders too. Use an ORDINARY doc: passing as_surface=None for
    # docs/handoff.md still resolves the handoff surface from the PATH, so that would
    # have asserted the clean line while exercising the block branch.
    (repo / "docs" / "notes.md").write_text("# Notes\n\nDocuments v9.9.9.\n", encoding="utf-8")
    clean = _pf.format_human(_pf.build_report(repo, "docs/notes.md", None))
    assert "regenerable-facts: clean" in clean


def test_a_path_outside_the_repo_is_refused_by_name(tmp_path: Path) -> None:
    """The refusal branch survived a shared-helper extraction with no test on it.

    `resolve_within_repo` returns None for anything it cannot place inside the repo,
    and this surface's disposition is to RAISE — the doc preflight cannot forecast
    constraints for a file the repo does not own, and quietly forecasting the wrong
    surface's rules would be worse than refusing."""
    repo = _seed_repo(tmp_path, _CLEAN_FIXTURE)
    outside = tmp_path / "elsewhere.md"
    outside.write_text("# Outside\n", encoding="utf-8")

    with pytest.raises(_pf.PreflightError) as excinfo:
        _pf.build_report(repo, str(outside), None)

    assert "outside repo root" in str(excinfo.value)
    assert str(outside) in str(excinfo.value)


# --- rules mode (no target) --------------------------------------------------
#
# The gap this closes: every check here is content-driven, so before the rules
# mode existed an author could only learn a rule by first breaking it, and one
# rework cycle was structurally guaranteed. These tests pin that the rules are
# RENDERED from the owning validators rather than restated -- a rules mode that
# types out its own copy of the rules is the drift it exists to prevent.


def test_rules_mode_answers_with_no_target_at_all() -> None:
    result = _run_script(ROOT, "--as-surface", "handoff")

    assert result.returncode == 0, result.stderr
    assert "RULES" in result.stdout
    # The point of the mode: no `--path`, and still a rule for each class.
    for expected in ("length:", "regenerable-facts:", "link form:", "backticked file references:"):
        assert expected in result.stdout, f"missing rule class {expected}: {result.stdout}"


def test_rules_mode_renders_the_length_cap_live(monkeypatch: pytest.MonkeyPatch) -> None:
    # Drift proof: move the owning constant and the rendered rule must follow.
    monkeypatch.setattr(_handoff, "MAX_CONTENT_LINES", 4321)
    rules = _rules.build_rules(ROOT, "handoff")

    assert rules["length"]["cap"] == 4321
    assert "4321" in _rules.format_rules_human(rules)


def test_rules_mode_renders_the_regenerable_classes_live(monkeypatch: pytest.MonkeyPatch) -> None:
    import re as _re

    monkeypatch.setattr(
        _handoff,
        "REGENERABLE_PATTERNS",
        ((_re.compile(r"\bv\d+\.\d+\.\d+\b"), "a fabricated class", "run the fabricated command"),),
    )
    rendered = _rules.format_rules_human(_rules.build_rules(ROOT, "handoff"))

    assert "a fabricated class" in rendered
    assert "run the fabricated command" in rendered


def test_rules_mode_headline_is_the_validators_own_sentence() -> None:
    # The rationale for the regenerable rule lives ONLY inside the validator's
    # error message, so the headline is obtained by making the validator raise --
    # not by typing a second copy of the sentence here.
    rules = _rules.build_rules(ROOT, "handoff")

    assert "goes stale in place" in rules["regenerable_facts"]["verdict"]
    assert rules["regenerable_facts"]["verdict"] in _rules.format_rules_human(rules)


def test_rules_mode_renders_the_tree_marker_class_it_could_not_reach() -> None:
    # `unmarked-tree` / `portable-absolute` fire only INSIDE a portable skill
    # package, so a probe that never supplies one silently omits the class whose
    # mis-remediation costs two gate cycles.
    rules = _rules.build_rules(ROOT, "handoff")
    tree_rows = [row for row in rules["backticked_refs"] if row["inside_package"]]

    assert tree_rows, "no probe classified a token inside a portable package"
    assert any(row["reason"] in _doc_links.TREE_MARKER_REASONS for row in tree_rows)
    assert any(row["remedy"] == _doc_links.TREE_MARKER_REMEDY for row in tree_rows)


def test_rules_mode_covers_the_classes_that_need_no_backtick_or_link() -> None:
    # A doc can be blocked by a bare internal markdown ref or a documented
    # command naming a missing script without containing either of the forms the
    # probes above classify.
    rendered = _rules.format_rules_human(_rules.build_rules(ROOT, "handoff"))

    assert _doc_links.BARE_INTERNAL_REF_REMEDY in rendered
    assert _doc_links.MISSING_COMMAND_TARGET_REMEDY in rendered


def test_rules_mode_declines_to_probe_rather_than_invent_a_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    # With no tracked path-shaped file to classify, an invented sample would make
    # every link verdict read `broken relative link` -- teaching an author that no
    # link form is accepted. Say nothing instead.
    monkeypatch.setattr(_rules, "_probe_sample", lambda _repo_root: None)
    rules = _rules.build_rules(ROOT, "handoff")

    assert rules["link_shapes"] == []
    assert rules["backticked_refs"] == []
    assert "not probed" in _rules.format_rules_human(rules)


def test_rules_mode_renders_the_backtick_remedy_the_gate_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # The two remedy sentences are single-sourced in check_doc_links so the
    # forecast cannot teach an author a remedy the gate does not offer.
    monkeypatch.setattr(_doc_links, "LINK_FORM_REMEDY", "a fabricated remedy")
    rendered = _rules.format_rules_human(_rules.build_rules(ROOT, "handoff"))

    assert "a fabricated remedy" in rendered


def test_rules_mode_link_verdicts_come_from_the_real_validator() -> None:
    rules = _rules.build_rules(ROOT, "handoff")
    by_shape: dict[str, list[str]] = {}
    for row in rules["link_shapes"]:
        by_shape.setdefault(row["shape"], []).append(row["verdict"])

    # A relative link that resolves is the only accepted form; every other
    # verdict is the gate's own refusal, not a sentence written here.
    assert "ok" in by_shape["relative"]
    assert any("broken relative link" in verdict for verdict in by_shape["relative"])
    assert "use relative links" in by_shape["absolute"][0]
    assert "`./`" in by_shape["bare"][0]


def test_rules_mode_reports_both_inline_code_classes() -> None:
    rules = _rules.build_rules(ROOT, "handoff")
    reasons = {row["reason"] for row in rules["inline_code"]}

    # Rendered by running the real checker over a sample that breaks both, so a
    # class the checker stops reporting stops being taught here.
    assert reasons == {_inline_code.WRAPPED_REASON, _inline_code.UNTERMINATED_REASON}


def test_rules_mode_names_the_capped_surfaces_when_none_is_selected() -> None:
    rules = _rules.build_rules(ROOT, None)

    assert rules["length"]["surface"] is None
    assert "handoff" in rules["length"]["known_surfaces"]
    assert "--as-surface" in _rules.format_rules_human(rules)


def test_rules_mode_refuses_an_unknown_surface_by_name() -> None:
    result = _run_script(ROOT, "--as-surface", "not-a-surface")

    assert result.returncode == 2
    assert "unknown --as-surface" in result.stderr


def test_probe_sample_declines_rather_than_inventing_one(tmp_path: Path) -> None:
    # The repaired function itself, not only its callers: an empty repo offers no
    # tracked path-shaped file, and the old fallback answered with an invented
    # `docs/README.md` that does not exist there.
    (tmp_path / "docs").mkdir()
    assert _rules._probe_sample(tmp_path) is None
