"""A declared adapter key resolves to a NAMED reader, or to a typed gap.

The regression fixture that shapes this whole module is
`test_the_four_multi_reader_setup_keys_stay_clean`. The obvious implementation -- ask
the shared loader whether it knows the key -- was refuted before it was built, because
`.agents/setup-adapter.yaml` carries four correct keys the shared loader has never heard
of. A loader-scoped key set calls those four typos on day one, on the one surface whose
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
    audit_registry,
    find_readers,
    iter_reader_files,
    resolve_declared_keys,
    resolve_key,
)
from scripts.adapter_lib import load_yaml_file  # noqa: E402

# The four keys `#530`'s posted causal review named. They are CORRECT declarations that
# the shared `simple_skill` loader does not know.
SETUP_MULTI_READER_KEYS = ("defaults_version", "policy_sources", "recommendation_sets", "surfaces")


def _repo_adapters() -> list[Path]:
    return sorted(ROOT.glob(".agents/*-adapter.yaml")) + sorted(ROOT.glob(".agents/cautilus-adapters/*.yaml"))


@pytest.mark.parametrize("key", SETUP_MULTI_READER_KEYS)
def test_the_four_multi_reader_setup_keys_stay_clean(key: str) -> None:
    """THE regression fixture for the refuted approach.

    Each of these resolves to a named reader that is NOT the shared loader --
    `skills/public/setup/scripts/setup_adapter.py` reads all four. Asserting the state
    alone would not be enough: a resolver that classified everything as `reader` would
    pass. So the reader list must be non-empty and must actually contain the module that
    owns them.
    """
    declared = load_yaml_file(ROOT / ".agents/setup-adapter.yaml")
    assert key in declared, f"{key} is the fixture; if setup-adapter.yaml dropped it, re-pick the fixture"

    resolution = resolve_key(ROOT, key)

    assert resolution.state == "reader", f"{key} is a correct declaration and must not read as {resolution.state}"
    assert resolution.readers, f"{key} resolved to `reader` with no named reader, which is not an answer"
    assert "skills/public/setup/scripts/setup_adapter.py" in resolution.readers


def test_a_typo_resolves_to_unknown_rather_than_passing_silently() -> None:
    """The defect this exists to catch: today a misspelled key is silently defaulted."""
    resolution = resolve_key(ROOT, "policy_sourcez")

    assert resolution.state == "unknown"
    assert resolution.readers == ()
    assert resolution.detail.strip()


def test_a_real_key_and_its_typo_do_not_resolve_the_same_way() -> None:
    """Direction, not presence. If both resolved to `reader`, or both to `unknown`, the
    resolver would be returning a constant and every other test here would still pass."""
    assert resolve_key(ROOT, "policy_sources").state == "reader"
    assert resolve_key(ROOT, "policy_sourcez").state == "unknown"


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


def test_the_key_scoped_gap_is_pinned_rather_than_hidden() -> None:
    """Pins the instrument's OWN known defect, so it cannot be forgotten or re-measured
    away.

    Resolution is key-scoped, not (file, key)-scoped. `.agents/cautilus-adapters/
    chatbot-benchmark.yaml` has no parsing reader -- `scripts/cautilus_adapter_lib.py`
    loads the SINGULAR `.agents/cautilus-adapter.yaml` -- yet most of its keys resolve to
    that module because the names collide with its field list. Its three
    `*_command_templates` siblings are declared together, are read by nothing, and are
    graded differently for that reason alone.

    An earlier version of this file asserted `comparison_command_templates` was the only
    text-asserted key in the repo, which reads as a property and is really an artifact of
    which names happen to collide. That assertion is replaced by this one: the DISCREPANCY
    is the fact worth pinning, and it should fail when the key-scoping gap is repaired --
    at which point all three siblings should agree.
    """
    declared = load_yaml_file(ROOT / ".agents/cautilus-adapters/chatbot-benchmark.yaml")
    states = {r.key: r.state for r in resolve_declared_keys(ROOT, declared)}

    siblings = ("comparison_command_templates", "held_out_command_templates", "full_gate_command_templates")
    assert all(key in states for key in siblings)
    assert len({states[key] for key in siblings}) == 2, (
        "the three sibling keys now agree. If key-scoping was repaired, replace this test "
        "with one asserting all three resolve to the same honest state; do not widen it."
    )
    assert states["comparison_command_templates"] == "text-asserted"
    assert states["held_out_command_templates"] == "reader", (
        "this verdict is the DEFECT, not the contract: no module parses this file at all"
    )
