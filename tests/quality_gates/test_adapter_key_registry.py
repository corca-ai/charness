"""A declared adapter key resolves to a NAMED reader, or to a typed gap.

The regression fixture that shapes this whole module is
`test_setup_adapter_keys_stay_clean`. The obvious implementation -- ask
the shared loader whether it knows the key -- was refuted before it was built, because
`.agents/setup-adapter.yaml` carries setup keys the shared loader has never heard
of. A loader-scoped key set calls those correct declarations typos on day one, on the one surface whose
job is to stop a false signal. If a future change reintroduces that approach, that test
is what fails.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from .support import ROOT

sys.path.insert(0, str(ROOT))

from scripts.adapter_key_registry import (  # noqa: E402
    EXCLUDED_READERS,
    _is_reader_file,
    associated_modules,
    audit_registry,
    find_readers,
    iter_reader_files,
    resolve_declared_keys,
    resolve_key,
    survey,
)
from scripts.adapter_lib import load_yaml_file  # noqa: E402

# These are setup declarations owned by the setup adapter reader, not by the shared
# adapter loader. Keeping the fixture to live fields prevents a retired policy field
# from becoming a reason to preserve the policy machinery.
SETUP_MULTI_READER_KEYS = ("surfaces",)


def _repo_adapters() -> list[Path]:
    return sorted(ROOT.glob(".agents/*-adapter.yaml"))


@pytest.mark.parametrize("key", SETUP_MULTI_READER_KEYS)
def test_setup_adapter_keys_stay_clean(key: str) -> None:
    """THE regression fixture for the refuted approach.

    Each of these resolves to a named reader that is NOT the shared loader --
    `skills/public/setup/scripts/setup_adapter.py` reads them. Asserting the state
    alone would not be enough: a resolver that classified everything as `reader` would
    pass. So the reader list must be non-empty and must actually contain the module that
    owns them.
    """
    declared = load_yaml_file(ROOT / ".agents/setup-adapter.yaml")
    assert key in declared, f"{key} is the fixture; if setup-adapter.yaml dropped it, re-pick the fixture"

    resolution = resolve_key(
        ROOT, key, associated=associated_modules(ROOT, ".agents/setup-adapter.yaml")
    )

    assert resolution.state == "reader", f"{key} is a correct declaration and must not read as {resolution.state}"
    assert resolution.readers, f"{key} resolved to `reader` with no named reader, which is not an answer"
    assert "skills/public/setup/scripts/setup_adapter.py" in resolution.readers


def test_a_typo_resolves_to_unknown_rather_than_passing_silently() -> None:
    """The defect this exists to catch: today a misspelled key is silently defaulted."""
    resolution = resolve_key(ROOT, "prose_wrap_policz")

    assert resolution.state == "unknown"
    assert resolution.readers == ()
    assert resolution.detail.strip()


def test_a_real_key_and_its_typo_do_not_resolve_the_same_way() -> None:
    """Direction, not presence. If both resolved to `reader`, or both to `unknown`, the
    resolver would be returning a constant and every other test here would still pass."""
    assert resolve_key(ROOT, "prose_wrap_policy").state == "reader"
    assert resolve_key(ROOT, "prose_wrap_policz").state == "unknown"


@pytest.mark.parametrize("key", ["x-vendor-thing", "host_extensions"])
def test_namespaced_extensions_are_typed_not_flagged(key: str) -> None:
    """An extension key has no reader in THIS repo by design; reporting it as unknown
    would flag a legal declaration, which is the wolf-crier this goal forbids."""
    assert resolve_key(ROOT, key).state == "extension"


def test_a_text_asserted_key_is_not_reported_as_read(tmp_path: Path) -> None:
    """`presence checked` and `value read` are different facts and must not render alike.

    A module that greps the adapter's raw text for `"some_key:"` proves the LINE exists.
    It never parses the value, so an empty or nonsense value passes it. Collapsing that
    into `reader` is the false green this goal exists to remove.
    """
    module = tmp_path / "scripts" / "fake_snippet_validator.py"
    module.parent.mkdir(parents=True)
    module.write_text('REQUIRED = ("some_declared_key:",)\n', encoding="utf-8")

    parsing, asserting = find_readers(tmp_path, "some_declared_key", files=[module])

    assert parsing == ()
    assert asserting == ("scripts/fake_snippet_validator.py",)
    assert resolve_key(tmp_path, "some_declared_key", files=[module]).state == "text-asserted"


def test_an_inert_output_literal_is_not_reported_as_a_value_reader(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "fake_output.py"
    module.parent.mkdir(parents=True)
    module.write_text('DEFAULTS = {"some_declared_key": 3}\n', encoding="utf-8")

    parsing, asserting = find_readers(tmp_path, "some_declared_key", files=[module])

    assert parsing == ()
    assert asserting == ()


def test_a_parsing_reader_outranks_a_text_assertion(tmp_path: Path) -> None:
    module = tmp_path / "scripts" / "fake_parser.py"
    module.parent.mkdir(parents=True)
    module.write_text('value = data["some_declared_key"]\n', encoding="utf-8")

    assert resolve_key(tmp_path, "some_declared_key", files=[module]).state == "reader"


def test_the_instrument_does_not_count_itself_as_a_reader() -> None:
    """Caught on this module's first real run.

    `adapter_key_registry.py`'s own docstring quotes an adapter key as an example, so the
    scan matched itself and reported that key as owned -- the instrument manufacturing
    the evidence it then reports. That is the same self-referential shape this goal
    exists to eliminate, so it is pinned rather than just fixed.
    """
    assert "scripts/adapter_key_registry.py" in EXCLUDED_READERS
    assert not any(str(path).endswith("adapter_key_registry.py") for path in iter_reader_files(ROOT))


def test_the_generated_plugin_mirror_is_not_counted_as_a_second_reader() -> None:
    """Counting the mirror would double every key's reader count and make a
    single-reader key look shared.

    Asserted twice on purpose. The scan-level assertion is what actually matters, but a
    mutation showed it holds via `READER_ROOTS` alone -- deleting the `plugins` guard
    changed nothing, so the guard was unpinned and would have rotted into dead code that
    only mattered the day someone added a root. The second assertion pins the guard.
    """
    assert not any("plugins" in path.parts for path in iter_reader_files(ROOT))
    assert _is_reader_file(ROOT / "scripts" / "adapter_lib.py") is True
    assert _is_reader_file(ROOT / "plugins" / "charness" / "scripts" / "adapter_lib.py") is False


def test_the_checked_in_registry_is_not_stale() -> None:
    """The anti-rot check, and the reason the registry is allowed to exist.

    Without it, the registry would be exactly what this module detects: a declaration
    asserting a reader that nobody verifies.
    """
    assert audit_registry(ROOT) == []


def test_the_registry_audit_refuses_an_entry_the_tree_does_not_support(tmp_path: Path, monkeypatch) -> None:
    """Constructed, not trusted: `audit_registry` returning `[]` on a clean tree proves
    nothing unless it also returns findings on a dirty one."""
    from scripts import adapter_key_registry

    monkeypatch.setattr(adapter_key_registry, "DYNAMIC_READER_KEYS", {"ghost_key": "scripts/does_not_exist.py"})
    monkeypatch.setattr(adapter_key_registry, "RETIRED_KEYS", {"repo": "", })

    problems = adapter_key_registry.audit_registry(ROOT)

    assert any("does not exist" in problem for problem in problems)
    assert any("still read it" in problem for problem in problems), "a 'retired' key the tree still reads must be refused"
    assert any("carries no reason" in problem for problem in problems)


def test_every_key_declared_in_this_repo_resolves_to_a_reader_or_a_typed_gap() -> None:
    """The measurement, kept executable rather than written down as a count.

    227 declared keys across 18 adapters at the time of writing: 74 shared-core, 152
    reader, 1 text-asserted, 0 unknown. The one text-asserted key is
    `comparison_command_templates` in the chatbot-benchmark adapter -- declared,
    grepped for as a raw line, and never parsed by anything.

    This asserts the SHAPE, not the numbers: no unknown keys, and every non-gap state
    naming at least one reader. Pinning the totals would make it fail on any legitimate
    adapter edit, which is how a measurement becomes noise and then gets deleted.
    """
    unknown: list[str] = []
    unnamed: list[str] = []
    for path in _repo_adapters():
        declared = load_yaml_file(path)
        if not isinstance(declared, dict):
            continue
        for resolution in resolve_declared_keys(ROOT, declared):
            if resolution.state == "unknown":
                unknown.append(f"{path.name}:{resolution.key}")
            elif resolution.state in ("reader", "shared-core", "text-asserted") and not resolution.readers:
                unnamed.append(f"{path.name}:{resolution.key}")

    assert unknown == [], (
        "adapter key(s) declared in this repo resolve to no reader. Either a reader was "
        f"deleted or the declaration is a typo -- both need a decision: {unknown}"
    )
    assert unnamed == [], f"resolved to a reader state without naming a reader: {unnamed}"


def test_a_resolver_that_builds_its_path_still_owns_its_adapter() -> None:
    """The inverted bias, caught by measurement before shipping.

    Most skill resolvers never contain their adapter's path -- the shared helper composes
    `.agents/{skill_id}-adapter.yaml` from the skill id. Seeding ownership on exact
    literals alone reported nine CORRECT `release-adapter.yaml` declarations as unread,
    which is the false-typo signal this goal's Non-Goals forbid.
    """
    associated = associated_modules(ROOT, ".agents/release-adapter.yaml")

    assert "skills/public/release/scripts/resolve_adapter.py" in associated
    rel = ".agents/release-adapter.yaml"
    states = {r.state for r in resolve_declared_keys(ROOT, load_yaml_file(ROOT / rel), adapter_relative=rel)}
    assert "reader-elsewhere" not in states, "a real adapter's own declarations must not read as unreconciled"


def test_an_injected_reader_is_still_associated() -> None:
    """`scripts/setup_inspect_lib.py` receives its adapter loader as a CALLABLE PARAMETER
    and names neither the adapter path nor its owner. Only the transitive closure over
    module references keeps it in scope; without it, correct setup declarations would
    read as unreconciled."""
    assert "scripts/setup_inspect_lib.py" in associated_modules(ROOT, ".agents/setup-adapter.yaml")


def test_an_example_adapter_agrees_with_the_adapter_it_exemplifies() -> None:
    """A verdict that contradicts itself on identical evidence is not a verdict.

    `skills/public/setup/adapter.example.yaml` is a template for
    `.agents/setup-adapter.yaml`. Before examples inherited the real adapter's
    association, `surfaces` was `reader` in one and `reader-elsewhere` in the other --
    same key, same readers, opposite answers -- and the difference silently inflated the
    example-adapter gap count that the operator's warn-vs-refuse decision depends on.
    """
    shared = SETUP_MULTI_READER_KEYS
    real_rel, example_rel = ".agents/setup-adapter.yaml", "skills/public/setup/adapter.example.yaml"
    real = {r.key: r.state for r in resolve_declared_keys(ROOT, load_yaml_file(ROOT / real_rel), adapter_relative=real_rel)}
    example = {
        r.key: r.state
        for r in resolve_declared_keys(ROOT, load_yaml_file(ROOT / example_rel), adapter_relative=example_rel)
    }

    for key in shared:
        assert real[key] == example[key] == "reader", f"{key}: real={real[key]} example={example.get(key)}"


def test_the_survey_reports_rather_than_refuses() -> None:
    """The warn-vs-refuse tier is the operator's call: the population that matters
    is consumer adapters this repo has never seen. The survey must therefore return
    findings, not raise or exit nonzero on them -- it currently has 24 (23
    `reader-elsewhere` plus 1 `text-asserted`).

    That count is prose and is deliberately NOT asserted: pinning it here would make every
    new adapter a test edit. It said 21 until round-2 review flagged the disagreement with
    the 23 recorded elsewhere, which is the hazard of an unpinned number -- so it is now
    stated with its breakdown, and the adapter WHITELIST above is what actually holds the
    line."""
    result = survey(ROOT)

    assert result["gaps"], "this repo has known gaps; a survey reporting none is broken, not clean"
    assert all(gap["detail"].strip() for gap in result["gaps"])


def test_association_stays_a_small_fraction_of_the_repo() -> None:
    """The decisive missing assertion, and the reason the collision surface shipped.

    Every seed in this module was justified by a measurement of UNDER-reporting; none was
    accompanied by a measurement of OVER-reporting, and that asymmetry is exactly how the
    defect recurred. A mechanism whose job is to NARROW a verdict needs a narrowness test,
    not only a non-emptiness test.

    The concrete failure this bounds: 16 skills each ship a `resolve_adapter.py`, and the
    closure once matched on bare module basename -- so every module mentioning
    "resolve_adapter" was associated with EVERY skill adapter, at 15-22% of the repo.
    That is association by name collision, the same defect as the verdict by name
    collision this module exists to remove.
    """
    total = len(iter_reader_files(ROOT))
    oversized = {
        str(path.relative_to(ROOT)): len(associated_modules(ROOT, str(path.relative_to(ROOT))))
        for path in ROOT.glob(".agents/*-adapter.yaml")
    }
    oversized = {rel: size for rel, size in oversized.items() if size > 0.10 * total}

    assert oversized == {}, (
        f"association covers more than 10% of {total} modules for: {oversized}. "
        "A `reader` verdict means little at that breadth; find the collision."
    )


def test_one_skills_modules_are_not_associated_with_another_skills_adapter() -> None:
    """The explicit cross-skill exclusion. A fraction bound alone can be satisfied while
    still mixing two skills together, so the specific contamination is named."""
    release = associated_modules(ROOT, ".agents/release-adapter.yaml")

    assert "skills/public/release/scripts/resolve_adapter.py" in release
    for foreign in (
        "skills/public/hitl/scripts/render_report.py",
        "skills/public/retro/scripts/plan_retro_run.py",
        "skills/public/quality/scripts/check_runtime_budget.py",
    ):
        assert foreign not in release, f"{foreign} belongs to another skill and must not read release's adapter"


def test_a_conventional_path_alone_does_not_fabricate_an_owner(tmp_path: Path, monkeypatch) -> None:
    """Existence is not association.

    `_convention_owners` used to accept any file sitting at the conventional path. A stub
    or repurposed resolver would then fabricate an owner and drag its whole closure in
    behind it. The candidate must also NAME the skill, which is the same reconciliation
    `audit_registry` already applies to the registry's own entries.
    """
    from scripts import adapter_key_registry

    (tmp_path / "skills/public/ghost/scripts").mkdir(parents=True)
    (tmp_path / "skills/public/ghost/scripts/resolve_adapter.py").write_text("VALUE = 'unrelated'\n", encoding="utf-8")
    monkeypatch.setattr(adapter_key_registry, "_EDGES_CACHE", {})
    monkeypatch.setattr(adapter_key_registry, "_LITERALS_CACHE", {})

    assert adapter_key_registry._convention_owners(tmp_path, ".agents/ghost-adapter.yaml") == set()


def test_a_retired_key_says_retired_rather_than_unknown(monkeypatch) -> None:
    """`RETIRED_KEYS` is empty, so this path had no coverage and no live subject.

    The distinction it exists for is real: an operator still declaring a withdrawn key
    deserves "this was removed", not "this looks like a typo". Constructed, because an
    empty registry proves nothing about the branch that reads it.
    """
    from scripts import adapter_key_registry

    monkeypatch.setattr(adapter_key_registry, "RETIRED_KEYS", {"old_key": "withdrawn in v2; use new_key"})
    resolution = adapter_key_registry.resolve_key(ROOT, "old_key")

    assert resolution.state == "retired"
    assert "withdrawn in v2" in resolution.detail


def test_a_dynamic_reader_key_resolves_to_its_registered_owner(monkeypatch) -> None:
    """The registry's other branch, also without a live subject. It exists for readers
    that build the key name at runtime, which a literal scan cannot see."""
    from scripts import adapter_key_registry

    monkeypatch.setattr(adapter_key_registry, "DYNAMIC_READER_KEYS", {"built_key": "scripts/adapter_lib.py"})
    resolution = adapter_key_registry.resolve_key(ROOT, "built_key")

    assert resolution.state == "reader"
    assert resolution.readers == ("scripts/adapter_lib.py",)


def test_dynamic_reader_audit_uses_owner_existence_as_its_static_floor(tmp_path: Path, monkeypatch) -> None:
    from scripts import adapter_key_registry

    owner = tmp_path / "scripts" / "owner.py"
    owner.parent.mkdir(parents=True)
    owner.write_text('REQUIRED = ("built_key:",)\n', encoding="utf-8")
    monkeypatch.setattr(adapter_key_registry, "DYNAMIC_READER_KEYS", {"built_key": "scripts/owner.py"})
    monkeypatch.setattr(adapter_key_registry, "RETIRED_KEYS", {})

    assert adapter_key_registry.audit_registry(tmp_path) == []


def test_an_unparseable_module_is_skipped_rather_than_failing_the_survey(tmp_path: Path) -> None:
    """One module that will not parse must not take down the classification of every key.

    The fallback is deliberate, so it is pinned: a syntax error in some unrelated script
    should cost that script's contribution, not the whole verdict.
    """
    from scripts import adapter_key_registry

    broken = tmp_path / "scripts" / "broken.py"
    broken.parent.mkdir(parents=True)
    broken.write_text("def (((\n", encoding="utf-8")

    assert adapter_key_registry._literals(broken) == frozenset()
    assert adapter_key_registry._import_names(broken) == frozenset()
    assert adapter_key_registry.find_readers(tmp_path, "anything", files=[broken]) == ((), ())


def test_the_survey_cli_runs_and_emits_parseable_yaml() -> None:
    """The CLI is the only callable surface this module has. An entry point nobody
    executes is an instrument nobody runs, which is the shape this goal targets."""
    import subprocess
    import sys

    import yaml

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "adapter_key_registry.py"), "--repo-root", str(ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr[-2000:]
    payload = yaml.safe_load(completed.stdout)
    assert payload["adapters"] >= 28
    assert payload["registry_problems"] == []


def test_the_commit_gate_refuses_an_adapter_that_is_not_a_mapping(tmp_path: Path) -> None:
    """A list-shaped adapter is still refused, and the reason is honest.

    This started as a test for a `must parse to a mapping` branch. Writing it proved the
    branch was UNREACHABLE -- this repo's loader parses a top-level list to `{}` -- so the
    dead branch was deleted rather than covered. What is pinned is the property that
    actually matters: the gate refuses, and says the true thing about why.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("gate_probe", ROOT / "scripts" / "validate_adapters.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    probe = tmp_path / ".agents" / "probe-adapter.yaml"
    probe.parent.mkdir(parents=True)
    probe.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(gate.ValidationError) as excinfo:
        gate.validate_adapter_yaml(probe)
    assert "version is required" in str(excinfo.value)


def test_an_adapter_with_no_owner_associates_nothing(tmp_path: Path) -> None:
    """The no-owner early return, and the honest floor of this whole mechanism.

    An adapter nothing claims must associate NOTHING, so every key it declares falls to
    `reader-elsewhere` or `unknown` rather than borrowing some unrelated module's
    parsing. If this returned a non-empty set, scoping would silently stop being scoping
    for exactly the files that need it most.
    """
    assert associated_modules(tmp_path, ".agents/nobody-claims-this-adapter.yaml") == frozenset()
