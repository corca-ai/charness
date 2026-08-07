"""The armed WARN tier: an unreconciled declared key reaches an operator (`#530`).

`v3.5.0` made a declaration answerable but armed nothing, so the original symptom -- a
typo'd key passing as `valid: true, errors: []` -- was still what an operator saw. These
tests own the arming, and the thing they have to work around is that **`unknown` fires
ZERO times across this repo's 445 declared keys**. A green suite here would therefore
prove nothing about whether the warning can fire at all, so the warned input is
CONSTRUCTED rather than observed, and `test_the_real_command_warns_on_a_constructed_typo`
goes through the actual CLI as a subprocess rather than calling the library.

The tier's SCOPE is the other half. `WARN_STATES` is `unknown` alone; `reader-elsewhere`
is deliberately excluded on measured evidence (13% association residue, one instance in a
shipped example). `test_reader_elsewhere_is_reported_but_never_warned` is the fixture that
fails if a later change widens the tier without re-measuring.
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

SETUP_ADAPTER = ".agents/setup-adapter.yaml"
# The same four keys `#530`'s causal review named, re-asserted against the ARMED tier
# rather than against the resolver. Arming is a separate surface: the resolver could keep
# classifying them correctly while the warn pass reported them anyway.
SETUP_MULTI_READER_KEYS = ("defaults_version", "policy_sources", "recommendation_sets", "surfaces")


def test_the_real_command_warns_on_a_constructed_typo(tmp_path: Path) -> None:
    """The acceptance criterion, proven end to end through `validate_adapters.py`.

    A constructed repo, not this one: this repo has no `unknown` key, so the only honest
    way to show the warning fires is to build the input that reaches it. The adapter
    carries two shared-core keys and one typo, so the test also shows the warning is
    SELECTIVE -- it names the typo and stays silent about `version` and `repo`.

    Run as a subprocess on purpose. The criterion is "operator-visible through a real
    command, not just a library return value", and only the process boundary proves the
    exit code, the stderr stream, and the summary line at once.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text(
        "version: 1\nrepo: constructed\nsurfacs: []\n", encoding="utf-8"
    )
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
    assert "1 unreconciled declared key(s)." in completed.stdout, completed.stdout


def test_a_clean_repo_still_states_the_count(tmp_path: Path) -> None:
    """"Checked, clean" must be distinguishable from "never ran".

    This repo's own run prints `0 unreconciled declared key(s).`, and that zero is the
    whole reason the tier is safe to ship. If the summary reported the count only when it
    was non-zero, an operator reading a green would be back where `#530` started.
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
    assert "0 unreconciled declared key(s)." in completed.stdout, completed.stdout
    assert "WARNING" not in completed.stderr


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
    """
    adapters = sorted(ROOT.glob(".agents/*-adapter.yaml")) + sorted(ROOT.glob(".agents/cautilus-adapters/*.yaml"))
    findings = unreconciled_keys(ROOT, adapters)
    assert findings == [], f"unreconciled declared keys appeared: {findings}"


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
