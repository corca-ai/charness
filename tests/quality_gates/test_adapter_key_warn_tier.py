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
    SHARED_CORE_OWNER,
    associated_modules,
    find_readers,
    iter_reader_files,
    resolve_key,
    survey,
)
from scripts.adapter_lib import load_yaml_file  # noqa: E402
from scripts.adapter_warn_tier import (  # noqa: E402
    WARN_STATES,
    reader_corpus_established,
    unreconciled_keys,
)
from scripts.validate_adapters import iter_adapter_yaml, iter_warn_scope_adapters  # noqa: E402

SETUP_ADAPTER = ".agents/setup-adapter.yaml"


def establish_reader_corpus(tmp_path: Path, *, reads: tuple[str, ...] = ()) -> Path:
    """Give a constructed tree the one thing the key tier needs before it may speak.

    Every constructed-repo test in this file used to run against a tree with no
    `scripts/`or `skills/` at all, which is why the ORIGINAL note on
    `test_the_real_command_warns_on_a_constructed_typo` had to disclaim its own result:
    with an empty reader corpus every non-shared-core key resolves `unknown`, so the
    warning fired for a reason that had nothing to do with the key being wrong. Those
    tests were green THROUGH the consumer-repo false-positive path, which is why none of
    them caught it.

    `reads` writes a module that genuinely parses each named key, so a constructed fixture
    can now hold a correct key and a typo side by side and show the tier separating them --
    the discrimination the old note said could only be proven against the real tree.
    """
    (tmp_path / SHARED_CORE_OWNER).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / SHARED_CORE_OWNER).write_text("# stand-in for the shared adapter core\n", encoding="utf-8")
    if reads:
        body = "".join(f'    value = data["{key}"]\n' for key in reads)
        (tmp_path / "scripts/reader.py").write_text(f"def read(data):\n{body}", encoding="utf-8")
    return tmp_path


# The same four keys `#530`'s causal review named, re-asserted against the ARMED tier
# rather than against the resolver. Arming is a separate surface: the resolver could keep
# classifying them correctly while the warn pass reported them anyway.
SETUP_MULTI_READER_KEYS = ("defaults_version", "policy_sources", "recommendation_sets", "surfaces")


def test_the_real_command_warns_on_a_constructed_typo(tmp_path: Path) -> None:
    """The acceptance criterion, proven end to end through `validate_adapters.py`.

    A constructed repo, not this one: this repo has no `unknown` key, so the only honest
    way to show the warning fires is to build the input that reaches it. This proves the
    PLUMBING -- a reachable `unknown` becomes a named, reasoned, operator-visible line on
    stderr with a zero exit and a counted summary -- and, since the corpus is now
    established, it also proves DISCRIMINATION: `surfaces` is read by a module in the
    fixture and stays silent while `surfacs` warns, in the same file, in one run.

    The earlier version of this test could not make that second claim and said so. It ran
    against a tree with no reader corpus, where every non-shared-core key resolves
    `unknown` -- so it passed through the same false-positive path that made the shipped
    tier warn on three CORRECT keys in a consumer repo.

    Run as a subprocess on purpose. The criterion is "operator-visible through a real
    command, not just a library return value", and only the process boundary proves the
    exit code, the stderr stream, and the summary line at once.
    """
    establish_reader_corpus(tmp_path, reads=("surfaces",))
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text(
        "version: 1\nrepo: constructed\nsurfaces: []\nsurfacs: []\n", encoding="utf-8"
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
    # The discrimination claim, asserted rather than assumed: the correctly-spelled
    # sibling is in the same file and must NOT appear.
    assert "`surfaces`" not in warned[0], warned[0]
    # The REASON, not just the name. A mutation that reported the key twice and dropped
    # the detail survived every other assertion here, which would have shipped a warning
    # an operator could not act on -- and "unreconciled" is exactly the word that needs
    # explaining, since a typo and a deleted reader look identical from the gate.
    assert "no module in scripts/ or skills/ reads it" in warned[0], warned[0]
    # The count is in the summary, so a clean run is a CLAIM rather than silence.
    assert "1 unreconciled declared key(s) across 1 declaring file(s); 0 uninterpreted line(s)." in completed.stdout, completed.stdout


def test_a_clean_repo_still_states_the_count(tmp_path: Path) -> None:
    """"Checked, clean" must be distinguishable from "never ran".

    This repo's own run prints `0 unreconciled declared key(s) across 37 declaring
    file(s).`, and that zero is the whole reason the tier is safe to ship. If the summary
    reported the count only when it was non-zero, an operator reading a green would be
    back where `#530` started -- and if it reported the count without the file scope, a
    clean-across-18 would be indistinguishable from a clean-across-37, which is exactly
    the defect round-1 review found in this function's first cut.
    """
    establish_reader_corpus(tmp_path)
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text("version: 1\nrepo: constructed\n", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "0 unreconciled declared key(s) across 1 declaring file(s); 0 uninterpreted line(s)." in completed.stdout, completed.stdout
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
    establish_reader_corpus(tmp_path, reads=("chunk_policy",))
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text("version: 1\nrepo: constructed\n", encoding="utf-8")
    example = tmp_path / "skills/public/handoff/adapter.example.yaml"
    example.parent.mkdir(parents=True)
    example.write_text("version: 1\nrepo: my-repo\nchunk_policy: {}\nchunk_polcy: {}\n", encoding="utf-8")

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
    assert "1 unreconciled declared key(s) across 2 declaring file(s); 0 uninterpreted line(s)." in completed.stdout, completed.stdout


def test_the_warn_scope_reaches_the_flattened_installed_layout(tmp_path: Path) -> None:
    """The layout CONSUMERS receive, which this repo's own tree cannot exercise.

    The export flattens `skills/public/<id>/` to `skills/<id>/`, so `ADAPTER_GLOBS`'
    `skills/public/*/adapter.example.yaml` matches nothing in an installed tree. Round-2
    review caught that: the widening's stated purpose is "shipped examples are what
    consumers copy", and without the flattened pattern the warn scope finds zero of them
    in exactly the layout consumers get -- while the summary still prints a confident file
    count that is accurate about what it read and useless for the population named.

    Adding the pattern is unobservable from this repo (`skills/` here holds `public/`,
    `shared/`, `support/`, so it matches nothing), which is precisely why the proof has to
    be a constructed tree. `iter_resolvers` already carries the same dual-layout handling.
    """
    establish_reader_corpus(tmp_path, reads=("chunk_policy",))
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/example-adapter.yaml").write_text("version: 1\nrepo: constructed\n", encoding="utf-8")
    example = tmp_path / "skills/handoff/adapter.example.yaml"
    example.parent.mkdir(parents=True)
    example.write_text("version: 1\nrepo: my-repo\nchunk_policy: {}\nchunk_polcy: {}\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    warned = [line for line in completed.stderr.splitlines() if line.startswith("WARNING ")]
    assert len(warned) == 1, completed.stderr
    assert "skills/handoff/adapter.example.yaml" in warned[0], warned[0]
    assert "1 unreconciled declared key(s) across 2 declaring file(s); 0 uninterpreted line(s)." in completed.stdout, completed.stdout


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

    result = unreconciled_keys(ROOT, [ROOT / SETUP_ADAPTER])
    # Empty findings has TWO causes under `WarnTierResult`, and this fixture is worthless
    # against the one it was written for unless the corpus was actually established. Round 2
    # caught this passing vacuously if `reader_corpus_established` ever regressed at ROOT.
    assert result.scope_established, "no corpus means this fixture proves nothing about arming"
    warned = {finding["key"] for finding in result.findings}
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
    result = unreconciled_keys(ROOT, iter_warn_scope_adapters(ROOT))
    assert result.scope_established, "this repo IS the reader corpus; an unestablished verdict here is a bug"
    assert result.findings == [], f"unreconciled declared keys appeared: {result.findings}"
    assert result.uninterpreted == [], f"adapter lines this repo could not parse: {result.uninterpreted}"


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

    # BOTH example families, named separately. Round 2 caught the first version asserting
    # `len(examples) >= 15` against 16 `skills/public/` + 3 `integrations/` files: dropping
    # the `integrations/*` glob entirely left 16 and passed, so the tier could have gone
    # back to claiming a scope it never read -- this slice's own blocker at reduced scale.
    # A threshold that survives deleting a whole family is not a scope assertion.
    public_examples = {path for path in scope if path.startswith("skills/public/")}
    integration_examples = {path for path in scope if path.startswith("integrations/")}
    assert len(public_examples) == 16, sorted(public_examples)
    assert len(integration_examples) == 3, sorted(integration_examples)
    assert len(scope) == 37, f"the measured warn population changed: {len(scope)}"
    # And the gate's own narrower validation scope must still be a strict subset, so this
    # widening never silently pulls a template into the REFUSING checks.
    assert {str(path.relative_to(ROOT)) for path in iter_adapter_yaml(ROOT)} < scope


def test_reader_elsewhere_is_reported_but_never_warned() -> None:
    """The tier boundary, on real data rather than a constructed case.

    `.agents/cautilus-adapters/chatbot-benchmark.yaml` is the strongest instance in the
    repo: `survey` types eleven of its keys as gaps (10 `reader-elsewhere` + 1 `text-asserted`), and the warn tier must stay silent about
    every one. Excluding `reader-elsewhere` is not squeamishness -- 3 of its 23 instances
    are association residue where the reader genuinely does read the file through dynamic
    dispatch, and one of those ships inside `skills/public/handoff/adapter.example.yaml`,
    so arming it would greet every new consumer with a wrong warning.
    """
    benchmark = ROOT / ".agents/cautilus-adapters/chatbot-benchmark.yaml"
    reported = [gap for gap in survey(ROOT)["gaps"] if gap["adapter"].endswith("chatbot-benchmark.yaml")]
    assert len(reported) == 11, f"fixture moved: expected 11 reported gaps, got {len(reported)}"
    assert {gap["state"] for gap in reported} <= {"reader-elsewhere", "text-asserted"}

    result = unreconciled_keys(ROOT, [benchmark])
    assert result.scope_established, "silence from an unestablished corpus would prove nothing here"
    assert result.findings == [], "the warn tier must not reach reported-but-unarmed states"


def test_a_consumer_repo_gets_no_key_verdict_at_all(tmp_path: Path) -> None:
    """The defect this tier SHIPPED, pinned as the regression it is.

    `find_readers` scans `<repo_root>/scripts` and `<repo_root>/skills`. A consumer's
    readers are in the installed plugin, which `_is_reader_file` excludes by design, so
    the corpus is empty and every non-shared-core key fell to `unknown`. Measured through
    the SHIPPED mirror before the repair: a fixture declaring `gate_commands`,
    `product_surfaces` and `startup_probes` -- three correct, documented, required charness
    keys -- drew three `is unknown` WARNINGs. That is a ~100% false-positive rate in the
    population the widening was justified by, from a module whose own design memo refused
    to arm `reader-elsewhere` at 13% for being a wolf-crier.

    The fix is a refusal to claim, not a new capability: the tier says it could not
    establish the corpus and renders no key verdict. `version`/`repo` are excluded from the
    fixture deliberately -- they are `SHARED_CORE_KEYS` and were silent even while broken,
    so including them would let this test pass on the old behaviour.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\ngate_commands: []\nproduct_surfaces: []\nstartup_probes: []\n",
        encoding="utf-8",
    )
    assert not reader_corpus_established(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    for key in ("gate_commands", "product_surfaces", "startup_probes"):
        assert f"`{key}`" not in completed.stderr, completed.stderr
    # Silence is not the fix either -- that would make "clean" and "never ran"
    # indistinguishable, which is the confusion this whole tier was built to end. The
    # unestablished scope has to be SAID.
    assert "adapter key reconciliation did not run" in completed.stderr, completed.stderr
    assert "declared keys not reconciled (reader corpus not established)" in completed.stdout, completed.stdout
    # And specifically NOT the clean-bill-of-health phrasing.
    assert "unreconciled declared key(s)" not in completed.stdout, completed.stdout


def test_an_over_indented_key_is_reported_even_with_no_reader_corpus(tmp_path: Path) -> None:
    """The commonest real YAML typo, on the one channel a consumer repo can still answer.

    One stray leading space and the loader drops the line entirely, so the key never
    reaches `declared` and NO widening of `WARN_STATES` could ever reach it -- the tier
    printed `0 unreconciled declared key(s)` over a file whose key it had never seen. The
    loader already recorded the drop; `unreconciled_keys` threw the evidence away by
    calling `load_yaml_file` instead of `load_yaml_file_report`.

    Asserted in an UNESTABLISHED tree on purpose. This is a fact about the parse, not about
    any reader, so it must survive the scope guard -- otherwise the guard above would have
    cost consumers the one verdict that still works for them, and the net change would be a
    loss.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents/quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\n  covrage_floor: 90\n", encoding="utf-8"
    )
    assert not reader_corpus_established(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    dropped = [line for line in completed.stderr.splitlines() if "covrage_floor" in line]
    assert len(dropped) == 1, completed.stderr
    assert "was not interpreted (over-indented line)" in dropped[0], dropped[0]
    # The consequence, not just the fact. "line 3 was not interpreted" tells an operator
    # nothing actionable without "the field it meant to set is serving an inferred default".
    assert "serving an inferred default" in dropped[0], dropped[0]
    assert "1 uninterpreted line(s)." in completed.stdout, completed.stdout


def test_the_scope_guard_keys_on_the_shared_core_owner_not_on_file_count(tmp_path: Path) -> None:
    """A count would answer the wrong question, and every consumer would satisfy it.

    "Is there Python under `scripts/`?" is true of most consumer repos while none of them
    holds the readers this tier reasons about. The predicate has to name the module that
    DEFINES the adapter contract, which is the same module `shared-core` already names as
    owner -- so this asserts an unrelated `scripts/` tree does NOT establish the corpus,
    and that adding the shared core alone does.
    """
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/unrelated.py").write_text("VALUE = 'gate_commands'\n", encoding="utf-8")
    assert not reader_corpus_established(tmp_path), "an unrelated scripts/ tree must not count as the corpus"

    (tmp_path / SHARED_CORE_OWNER).write_text("# stand-in\n", encoding="utf-8")
    assert reader_corpus_established(tmp_path)


def test_a_tree_under_plugins_is_not_an_established_corpus(tmp_path: Path) -> None:
    """The blocker round 1 found: the guard's first cut checked a PROXY, not the corpus.

    `_is_reader_file` drops any path with a `plugins` component, so under
    `--repo-root <...>/plugins/charness` the shared core is `is_file()` while every
    candidate reader is excluded -- corpus empty, guard satisfied, tier confident. Measured
    on the real exported tree before the repair: **126** false WARNINGs reported as
    `126 unreconciled declared key(s) across 19 declaring file(s)`, over correct shipped
    examples. The repair had reproduced the defect it removed, at a larger scale than the
    original, on the layout closest to what consumers install.

    `test_exported_validate_adapters_runs_from_flattened_layout` runs exactly this root and
    asserts only the exit code, so the suite could not have caught it: this test asserts the
    property that one does not.

    Both halves matter. `is_file()` must be true (or the old proxy would pass this
    vacuously) while the corpus stays empty -- that combination is the whole bug.
    """
    root = tmp_path / "plugins/charness"
    (root / "scripts").mkdir(parents=True)
    (root / SHARED_CORE_OWNER).write_text("# stand-in\n", encoding="utf-8")
    assert (root / SHARED_CORE_OWNER).is_file(), "the discarded proxy must be TRUE here, or this proves nothing"

    assert not reader_corpus_established(root), "a plugins-rooted tree has no visible reader corpus"

    (root / ".agents").mkdir()
    (root / ".agents/quality-adapter.yaml").write_text(
        "version: 1\nrepo: exported\ngate_commands: []\n", encoding="utf-8"
    )
    result = unreconciled_keys(root, [root / ".agents/quality-adapter.yaml"])
    assert not result.scope_established
    assert result.findings == [], f"a plugins-rooted run must render no key verdict, got {result.findings}"

    # Through the CLI, because the REASON an operator reads is rendered there and round 2
    # found the library-only assertion above could not see it. The first message said the
    # shared core was "not readable", which is false at this root -- the file is present and
    # packaging REQUIRES it; it is EXCLUDED. An operator acting on "not readable" would hunt
    # a missing file that is not missing.
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_adapters.py"), "--repo-root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "is unknown" not in completed.stderr, completed.stderr
    assert "excluded from the reader corpus" in completed.stderr, completed.stderr
    assert "path component: plugins" in completed.stderr, completed.stderr
    assert "not readable" not in completed.stderr, completed.stderr


def test_the_warn_tier_module_is_not_counted_as_a_reader() -> None:
    """Splitting a module moves its literals; it does not move them out of scan range.

    `adapter_warn_tier.py`'s docstring names `gate_commands`, `product_surfaces` and
    `startup_probes` as the measured false-positive set, and `find_readers` counts any
    string constant equal to a key as a parse -- docstrings included, by its own KNOWN
    LIMIT. Without an `EXCLUDED_READERS` entry this file would report itself as their
    owner: the instrument manufacturing the evidence it then reports, which is the trap
    `adapter_key_registry.py` hit on its own first run and recorded.

    Asserted against `iter_reader_files`, not against the constant, so adding the name to
    `EXCLUDED_READERS` while breaking the exclusion mechanism cannot pass this.
    """
    scanned = {str(path.relative_to(ROOT)) for path in iter_reader_files(ROOT)}
    assert "scripts/adapter_warn_tier.py" not in scanned, "the armed tier must not be its own reader"
    assert "scripts/adapter_key_registry.py" not in scanned

    for key in ("gate_commands", "product_surfaces", "startup_probes"):
        readers = find_readers(ROOT, key)[0]
        assert "scripts/adapter_warn_tier.py" not in readers, f"{key} resolved to the tier's own docstring"


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
