"""The armed WARN tier: an unreconciled declared key reaches an operator (`#530`).

`v3.5.0` made a declaration answerable but armed nothing, so the original symptom -- a
typo'd key passing as `valid: true, errors: []` -- was still what an operator saw. These
tests own the arming, and the thing they have to work around is that **`unknown` fires
ZERO times across this repo's 445 declared keys**. A green suite here would therefore
prove nothing about whether the warning can fire at all, so the warned input is
CONSTRUCTED rather than observed, and `test_the_real_command_warns_on_a_constructed_typo`
goes through the actual CLI as a subprocess rather than calling the library.

The tier's SCOPE is the other half, and it has two axes that round-1 review showed are
easy to confuse. WHICH STATES: `WARN_STATES` is `unknown` alone; `reader-elsewhere` is
deliberately excluded on measured evidence (13% association residue, one instance in a
shipped example), pinned by `test_reader_elsewhere_is_reported_but_never_warned`. WHICH
FILES: the tier reads `iter_warn_scope_adapters`' 37 adapters, deliberately wider than the
18 `.agents/` files the REFUSING checks read, because shipped examples are what consumers
copy -- pinned by `test_the_warn_scope_covers_shipped_examples`. The first cut armed 18
while reporting 37's zero, and no test noticed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .support import ROOT

sys.path.insert(0, str(ROOT))

from scripts.adapter_key_registry import (  # noqa: E402
    WARN_STATES,
    associated_modules,
    resolve_key,
    survey,
    unreconciled_keys,
)
from scripts.adapter_lib import load_yaml_file  # noqa: E402
from scripts.validate_adapters import iter_adapter_yaml, iter_warn_scope_adapters  # noqa: E402

SETUP_ADAPTER = ".agents/setup-adapter.yaml"
# The same four keys `#530`'s causal review named, re-asserted against the ARMED tier
# rather than against the resolver. Arming is a separate surface: the resolver could keep
# classifying them correctly while the warn pass reported them anyway.
SETUP_MULTI_READER_KEYS = ("defaults_version", "policy_sources", "recommendation_sets", "surfaces")


def test_the_real_command_warns_on_a_constructed_typo(tmp_path: Path) -> None:
    """The acceptance criterion, proven end to end through `validate_adapters.py`.

    A constructed repo, not this one: this repo has no `unknown` key, so the only honest
    way to show the warning fires is to build the input that reaches it. What this proves
    is the PLUMBING -- that a reachable `unknown` becomes a named, reasoned, operator-visible
    line on stderr with a zero exit and a counted summary. It does NOT prove the tier can
    tell a typo from a correct key; see the note in the body for why, and the real-tree
    tests below for where that is proven.

    Run as a subprocess on purpose. The criterion is "operator-visible through a real
    command, not just a library return value", and only the process boundary proves the
    exit code, the stderr stream, and the summary line at once.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text(
        "version: 1\nrepo: constructed\nsurfacs: []\n", encoding="utf-8"
    )
    # NOTE, so this test is not read as proving more than it does: `tmp_path` has no
    # `scripts/`or `skills/` tree, so EVERY non-shared-core key resolves `unknown` here.
    # The silence about `version`/`repo` therefore proves the `SHARED_CORE_KEYS` early
    # return, not that the tier can tell a typo from a correct key. That discrimination is
    # proven over the real tree by `test_this_repo_warns_about_nothing` and
    # `test_the_four_multi_reader_setup_keys_survive_arming`.
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    # WARN, not refuse. The operator chose the tier; a non-zero exit here would be a
    # different decision shipped under the same name.
    assert completed.returncode == 0, completed.stderr
    # Count the lines rather than substring-search the stream: the constructed repo lives
    # under `tmp_path`, so a path component could satisfy a bare `"repo" not in stderr`
    # check by accident and the selectivity claim would go unproven.
    warned = [line for line in completed.stderr.splitlines() if line.startswith("WARNING ")]
    assert len(warned) == 1, completed.stderr
    assert "`surfacs`" in warned[0], warned[0]
    # The REASON, not just the name. A mutation that reported the key twice and dropped
    # the detail survived every other assertion here, which would have shipped a warning
    # an operator could not act on -- and "unreconciled" is exactly the word that needs
    # explaining, since a typo and a deleted reader look identical from the gate.
    assert "no module in scripts/ or skills/ reads it" in warned[0], warned[0]
    # The count is in the summary, so a clean run is a CLAIM rather than silence.
    assert "1 unreconciled declared key(s) across 1 declaring file(s)." in completed.stdout, completed.stdout


def test_a_clean_repo_still_states_the_count(tmp_path: Path) -> None:
    """"Checked, clean" must be distinguishable from "never ran".

    This repo's own run prints `0 unreconciled declared key(s) across 37 declaring
    file(s).`, and that zero is the whole reason the tier is safe to ship. If the summary
    reported the count only when it was non-zero, an operator reading a green would be
    back where `#530` started -- and if it reported the count without the file scope, a
    clean-across-18 would be indistinguishable from a clean-across-37, which is exactly
    the defect round-1 review found in this function's first cut.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text("version: 1\nrepo: constructed\n", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "0 unreconciled declared key(s) across 1 declaring file(s)." in completed.stdout, completed.stdout
    assert "WARNING" not in completed.stderr


def test_the_real_command_warns_on_a_typo_in_a_shipped_example(tmp_path: Path) -> None:
    """The WIRING, not the helper -- the gap that survived the first repair.

    `test_the_warn_scope_covers_shipped_examples` asserts `iter_warn_scope_adapters`
    returns the wide set, and a mutation that reverted `main()`'s CALL SITE to
    `iter_adapter_yaml(root)` passed it anyway: the helper was still correct, and the gate
    still read 18 files. That is the round-1 blocker reproduced one level up, and it is why
    this test drives the actual CLI over a constructed tree containing a shipped example.

    The `.agents/` adapter is clean and present on purpose: it keeps the run off the
    `No adapter surfaces found.` early return, so the only thing that can produce a warning
    here is the example being genuinely in the gate's scope.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text("version: 1\nrepo: constructed\n", encoding="utf-8")
    example = tmp_path / "skills/public/handoff/adapter.example.yaml"
    example.parent.mkdir(parents=True)
    example.write_text("version: 1\nrepo: my-repo\nchunk_polcy: {}\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    warned = [line for line in completed.stderr.splitlines() if line.startswith("WARNING ")]
    assert len(warned) == 1, completed.stderr
    assert "skills/public/handoff/adapter.example.yaml" in warned[0], warned[0]
    assert "`chunk_polcy`" in warned[0], warned[0]
    # 2 files: the `.agents/` adapter AND the shipped example. If the call site narrows,
    # this reads 1 and the test fails on the scope rather than on the warning.
    assert "1 unreconciled declared key(s) across 2 declaring file(s)." in completed.stdout, completed.stdout


def test_the_four_multi_reader_setup_keys_survive_arming() -> None:
    """THE regression fixture for the refuted approach, carried across the arming.

    A loader-scoped key set would have called these four correct declarations typos. The
    resolver already refuses to; this asserts the WARN pass does not reintroduce the same
    verdict one layer up, which is this repo's most reliable failure mode -- a fix that
    carries the class it fixed.
    """
    declared = load_yaml_file(ROOT / SETUP_ADAPTER)
    for key in SETUP_MULTI_READER_KEYS:
        assert key in declared, f"{key} is the fixture; if setup-adapter.yaml dropped it, re-pick the fixture"

    warned = {finding["key"] for finding in unreconciled_keys(ROOT, [ROOT / SETUP_ADAPTER])}
    assert warned == set(), f"the setup adapter must warn about nothing, got {sorted(warned)}"


def test_this_repo_warns_about_nothing() -> None:
    """The measured fire rate, pinned so a later change cannot make it noisy unnoticed.

    Arming a warning makes every existing green a claim, so the repo-wide count is part of
    the contract rather than a happy accident. If this fails, either a real unreconciled
    key was introduced (fix the declaration) or the tier widened (re-measure before
    shipping) -- and the failure says which by naming the keys.

    The adapter list comes from `iter_warn_scope_adapters` rather than being re-globbed
    here. Round-1 review caught the earlier version hardcoding the scope: that made this a
    SECOND declaration of which files the tier reads -- the anti-pattern the registry
    module exists to detect -- and it is why the gate's 18-file blind spot was invisible
    from the test side. Widening the gate now widens this test automatically.
    """
    findings = unreconciled_keys(ROOT, iter_warn_scope_adapters(ROOT))
    assert findings == [], f"unreconciled declared keys appeared: {findings}"


def test_the_warn_scope_covers_shipped_examples() -> None:
    """The blocker round 1 found, pinned as a regression fixture.

    The first cut armed `iter_adapter_yaml`'s 18 `.agents/` files while reporting the
    37-adapter measurement's zero -- a check claiming a scope it never read, which is this
    goal's own defect class. Reproduced before repair: a typo'd key in
    `skills/public/handoff/adapter.example.yaml` produced `0 unreconciled declared key(s)`
    with all 40 tests green.

    Shipped examples are the ones that matter: a consumer COPIES them, so a typo in one
    propagates to every repo that adopts it. Asserting the count alone would not catch a
    regression here (both scopes report zero on a clean tree), so this asserts the
    SCOPE -- that example adapters are actually in the set of files read.
    """
    scope = {str(path.relative_to(ROOT)) for path in iter_warn_scope_adapters(ROOT)}
    assert "skills/public/handoff/adapter.example.yaml" in scope, sorted(scope)

    examples = {path for path in scope if path.endswith("adapter.example.yaml")}
    assert len(examples) >= 15, f"shipped examples fell out of the warn scope: {sorted(examples)}"
    # And the gate's own narrower validation scope must still be a strict subset, so this
    # widening never silently pulls a template into the REFUSING checks.
    assert {str(path.relative_to(ROOT)) for path in iter_adapter_yaml(ROOT)} < scope


def test_reader_elsewhere_is_reported_but_never_warned() -> None:
    """The tier boundary, on real data rather than a constructed case.

    `.agents/cautilus-adapters/chatbot-benchmark.yaml` is the strongest instance in the
    repo: `survey` types ten of its keys as gaps, and the warn tier must stay silent about
    every one. Excluding `reader-elsewhere` is not squeamishness -- 3 of its 23 instances
    are association residue where the reader genuinely does read the file through dynamic
    dispatch, and one of those ships inside `skills/public/handoff/adapter.example.yaml`,
    so arming it would greet every new consumer with a wrong warning.
    """
    benchmark = ROOT / ".agents/cautilus-adapters/chatbot-benchmark.yaml"
    reported = [gap for gap in survey(ROOT)["gaps"] if gap["adapter"].endswith("chatbot-benchmark.yaml")]
    assert reported, "fixture moved: this adapter is supposed to be the repo's largest reported gap"
    assert {gap["state"] for gap in reported} <= {"reader-elsewhere", "text-asserted"}

    assert unreconciled_keys(ROOT, [benchmark]) == [], "the warn tier must not reach reported-but-unarmed states"


def test_warn_states_is_exactly_unknown() -> None:
    """Widening the tier must be a deliberate edit with a re-measurement behind it.

    Without this, adding `reader-elsewhere` to `WARN_STATES` is a one-word change that
    passes every other test in this file except the one above -- and it would ship the
    13% false-positive rate the measurement refused.
    """
    assert WARN_STATES == ("unknown",)


def test_skipping_association_does_not_change_the_unknown_verdict() -> None:
    """The optimisation `unreconciled_keys` documents, pinned rather than asserted in prose.

    `resolve_key` reaches `unknown` only when `parsing` is empty, and `scoped` is a subset
    of `parsing`, so the scoped and unscoped answers agree for this state and only for it.
    That equivalence is what lets the warn pass skip the import-graph closure and keep the
    commit-time gate cheap. It does NOT generalise: if `WARN_STATES` ever grows, this test
    stops covering the new state, which is why the test above freezes the tuple.
    """
    for adapter in sorted(ROOT.glob(".agents/*-adapter.yaml")):
        relative = str(adapter.relative_to(ROOT))
        associated = associated_modules(ROOT, relative)
        for key in load_yaml_file(adapter):
            if not isinstance(key, str):
                continue
            scoped = resolve_key(ROOT, key, associated=associated).state
            unscoped = resolve_key(ROOT, key).state
            assert (scoped == "unknown") == (unscoped == "unknown"), (
                f"{relative}:{key} disagrees on `unknown` between scoped ({scoped}) and unscoped ({unscoped})"
            )
