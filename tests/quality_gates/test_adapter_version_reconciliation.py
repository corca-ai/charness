"""Every adapter resolver reconciles a declared `version` against the one it speaks.

The defect this pins: 16 of 17 resolver sites hand-copied a `version` check that only
asked "is it an int?", then wrote the answer into the resolved payload as authoritative.
A repo could declare `version: 9` and every one of those 16 echoed 9 back as if the
reader had honoured it -- a declaration no executable reader ever reconciled.

These tests are deliberately CONSTRUCTED-INPUT tests, not presence tests. Each case
builds the declaration that should be refused and asserts both halves: that the refusal
fires, AND that the unsupported value does not survive into the resolved payload. A test
that only asserted "some error was raised" would pass on a resolver that refused for an
unrelated reason, and one that only asserted the error string would pass on a resolver
that errored and echoed the bad version anyway.

The second defect, measured later: refusing the version and then honoring its SIBLINGS.
15 of the 18 sites did, so a `version: 9` adapter still selected the artifact directory a
gate reads, the repo identity it reports, and the line ceilings #640 made adapter-owned --
a declaration steering a reader through a schema no reader read. Two families had a
bespoke test for this; the parametrized containment pair below is the census-wide form,
with a liveness control so a row cannot pass by sharing no field with the probe.

One row is weaker than the rest and says so at its call site: the `validate_adapters_gate`
row drives a gate that RAISES rather than returning a payload, so its payload assertions
are satisfied by values the harness synthesizes. Its error assertions are real.

Blind class, measured rather than guessed:

* This measures RESOLVERS. A consumer that reads a correctly-contained payload and then
  acts on the defaults in it is a different failure, and it was a real one -- the retro
  gate reported `Validated 0` exit 0, the debug gate raised a ceiling it was told to
  lower. `tests/quality_gates/test_adapter_version_refusal_is_loud.py` drives the six
  surfaces repaired for it; `VERDICT_CONSUMERS` below names readers that honor someone
  else's verdict and is an inventory, not a coverage claim.
* `CONTAINMENT_PROBE` declares no MAPPING-typed field, so `proof_semantics` -- whose
  whole surface is `proof_levels`, `acceptance_map`, `gap_policy` -- is covered here only
  for `repo` and `language`. `issue`'s backend and `capability_catalog`'s registry flag
  are covered by bespoke tests instead (in this file, and in
  `tests/test_capability_catalog.py`). A row's containment is only as strong as what the
  probe can express at it. The liveness test asserts only that SOME probe field reached a
  row, so a row carried solely by `repo`/`language` renders green while proving little
  about its steering surface -- it names the reached set in its failure message, which
  helps when it fails and not when it passes.
* Nothing here sees an adapter whose version this reader SPEAKS but whose fields mean
  something else.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

from .support import ADAPTER_LIB, ROOT

sys.path.insert(0, str(ROOT))

# (label, module path, entrypoint name). The label is the resolver family; the number of
# rows here is the "how many sites are covered" count. 18 sites driven here, 4 exempt --
# 22 reconciling sites in total. The exemptions are listed in EXEMPT_SITES with the test
# that drives each instead; none of them is absent.
#
# Both numbers are ASSERTED below rather than left as prose. They were already wrong when
# this was read fresh -- the prose count had drifted from EXEMPT_SITES, so the stated
# total was never either sum. On the file whose own thesis is "a count is only as honest
# as its denominator", the denominator had rotted with nothing to catch it.
SITES: tuple[tuple[str, str, str], ...] = (
    ("announcement", "scripts/announcement_adapter_lib.py", "validate_announcement_adapter_data"),
    ("critique", "scripts/critique_adapter_lib.py", "validate_adapter_data"),
    ("narrative", "scripts/narrative_adapter_lib.py", "validate_narrative_adapter_data"),
    ("proof_semantics", "scripts/proof_semantics_adapter_lib.py", "validate_adapter_data"),
    ("simple_skill", "scripts/simple_skill_adapter_lib.py", "validate_simple_adapter_data"),
    ("achieve", "skills/public/achieve/scripts/achieve_adapter_policy.py", "validate_adapter_data"),
    ("create-skill", "skills/public/create-skill/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("debug", "skills/public/debug/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("gather", "skills/public/gather/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("hitl", "skills/public/hitl/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("hotl", "skills/public/hotl/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("impl", "skills/public/impl/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("issue", "skills/public/issue/scripts/resolve_adapter.py", "load_adapter"),
    ("capability_catalog", "scripts/capability_catalog_sources.py", "load_adapter"),
    ("quality", "scripts/quality_adapter_lib.py", "validate_quality_adapter_data"),
    ("release", "skills/public/release/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("retro", "skills/public/retro/scripts/resolve_adapter.py", "validate_adapter_data"),
    ("validate_adapters_gate", "scripts/gates/validate_adapters.py", "validate_adapter_yaml"),
)

# Sites that DO reconcile a version but cannot be driven by `_resolve`'s call shapes: each
# either returns a non-canonical payload or raises instead of returning one. They belong
# here with the test that drives them rather than silently missing from SITES -- an absent
# row and an exempt row are different facts and must not render the same. #574 was filed
# because these readers were absent from every census; being absent from this one too is
# the same defect wearing the repair's clothes.
EXEMPT_SITES: tuple[tuple[str, tuple[str, ...], tuple[str, ...], str], ...] = (
    (
        "setup_inspect",
        ("skills/public/setup/scripts/setup_adapter.py",),
        ("tests/quality_gates/test_setup_inspect_adapters.py::"
         "test_setup_inspect_refuses_unsupported_adapter_before_surface_overrides",),
        "returns (data, path, warnings) with dict-shaped warnings, not the canonical "
        "(resolved, errors) pair; the driving test asserts the inspect surface and "
        "resolve_adapter agree on one file.",
    ),
    (
        "quality_bootstrap",
        ("scripts/quality_bootstrap_lib.py",),
        ("tests/quality_gates/test_quality_bootstrap.py::"
         "test_quality_bootstrap_refuses_unsupported_adapter_without_rewriting_it",),
        "raises BootstrapValidationError instead of returning a payload.",
    ),
    (
        "cli_skill_surface_gate",
        ("scripts/gates/check_cli_skill_surface.py",),
        ("tests/quality_gates/test_cli_skill_surface.py::"
         "test_cli_skill_surface_refuses_an_adapter_version_it_does_not_speak",),
        "is a gate, not a resolver: it returns a blocked verdict payload rather than "
        "(resolved, errors). It reads the quality adapter raw because it needs "
        "`cli_skill_surface_probe_commands` and `product_surfaces`, both trust-boundary "
        "fields -- the first selects subprocesses, the second can switch the gate off.",
    ),
    (
        "worktree_doctor",
        ("scripts/worktree/worktree_doctor_lib.py",),
        ("tests/charness_cli/test_worktree_doctor.py::"
         "test_manifest_version_is_reconciled_by_the_shared_check",),
        "validates `.agents/worktree-adapter.yaml`, whose `prepare.commands[].argv` this "
        "tool executes, and prefixes every error with `manifest.` so its own fixtures keep "
        "their wording; the prefix is why `_version_errors` cannot match it.",
    ),
)

# Readers that HONOR a version verdict someone else rendered rather than rendering one.
# They are not reconciling sites and are deliberately not counted above -- but they are
# the surface where a correct refusal gets thrown away, so they are named rather than
# left invisible.
VERDICT_CONSUMERS: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "regenerable_facts_gate",
        ("skills/public/quality/scripts/check_regenerable_facts.py",),
        ("tests/quality_gates/test_regenerable_facts.py",),
    ),
)

# Adapter filename per file-reading site, for the `load_adapter` call shape below.
_ADAPTER_FILENAMES: dict[str, str] = {
    "issue": "issue-adapter.yaml",
    "capability_catalog": "capability-catalog-adapter.yaml",
}

_LOADED: dict[str, Any] = {}


def _module(path: str) -> Any:
    if path not in _LOADED:
        name = "version_probe_" + path.replace("/", "_").replace("-", "_").removesuffix(".py")
        spec = importlib.util.spec_from_file_location(name, ROOT / path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _LOADED[path] = module
    return _LOADED[path]


def _scalar(value: Any) -> str:
    """One declared value as YAML. The rendering is load-bearing: a bare `1` legitimately
    parses back as an int, so the string case must be written quoted or the fixture tests
    the loader's coercion instead of the resolver's version contract. Scalars only --
    this repo's YAML reader is hand-rolled, and a flow sequence here would measure the
    parser rather than the contract under test."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def _render(declared: dict[str, Any]) -> str:
    """The declaration as YAML. Lists render as block sequences, which is the shape a
    real adapter uses and the shape this repo's hand-rolled reader parses -- a flow
    sequence would measure the parser instead of the contract."""
    rendered: list[str] = []
    for key, value in declared.items():
        if isinstance(value, list):
            rendered.append(f"{key}:\n" + "".join(f"  - {_scalar(item)}\n" for item in value))
        else:
            rendered.append(f"{key}: {_scalar(value)}\n")
    return "".join(rendered)


def _resolve_declared(
    label: str, path: str, entry: str, declared: dict[str, Any], tmp_path: Path
) -> tuple[dict[str, Any], list[str]]:
    """Run one resolver family against a whole DECLARED mapping and return
    ``(resolved payload, errors)``. The three call shapes below are the resolvers' own
    signatures; nothing about the version contract varies with them.

    Takes the mapping rather than a bare version because the version verdict and what the
    reader may honor ALONGSIDE it are one contract, and the sibling half cannot be
    exercised through a version-only fixture."""
    module = _module(path)
    function: Callable[..., Any] = getattr(module, entry)
    if entry == "load_adapter":
        # This site validates only through a real file, so the declaration has to be
        # rendered as YAML.
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        # The filename is per-site, not per-entrypoint: two resolver families share the
        # `load_adapter` name and read different adapter files, so writing one hardcoded
        # name would leave the other reading an absent file and passing vacuously.
        (agents_dir / _ADAPTER_FILENAMES[label]).write_text(_render(declared), encoding="utf-8")
        report = function(tmp_path)
        return report["data"], report["errors"]
    if entry == "validate_adapter_yaml":
        # The commit-time gate RAISES instead of returning a payload, and it reads a real
        # file. It is included here because it renders a version verdict on adapters --
        # and for adapter files without a per-skill resolver it is the ONLY one that does.
        module_error = getattr(module, "ValidationError")
        probe = tmp_path / ".agents" / "probe-adapter.yaml"
        probe.parent.mkdir(parents=True, exist_ok=True)
        # `repo` LAST, so a probe carrying its own `repo` cannot displace the harness's
        # required field. The other order reads fine today only because this row is
        # excluded from the containment probe; it would silently hand the gate the
        # attacker string the moment anyone included it.
        probe.write_text(_render({**declared, "repo": "probe"}), encoding="utf-8")
        # NOTE: for THIS row the payload half of each assertion is synthesized below,
        # not observed. The gate raises instead of returning a payload, so it has no
        # resolved dict to echo a bad version into; only the error half is real evidence.
        try:
            function(probe)
        except module_error as exc:
            # Strip the `<path>: ` prefix so the wording assertions read the same message
            # every other site produces.
            return {}, [part.strip() for part in str(exc).split(":", 1)[-1].split(";")]
        return dict(declared), []
    if label == "simple_skill":
        resolved, errors, _ = function(dict(declared), repo_root=ROOT, output_dir="charness-artifacts/probe")
        return resolved, errors
    resolved, errors, _ = function(dict(declared), ROOT)
    return resolved, errors


def _resolve(label: str, path: str, entry: str, version: Any, tmp_path: Path) -> tuple[dict[str, Any], list[str]]:
    return _resolve_declared(label, path, entry, {"version": version}, tmp_path)


def _version_errors(errors: list[str]) -> list[str]:
    return [error for error in errors if error.startswith("version must be")]


@pytest.mark.parametrize(("label", "path", "entry"), SITES, ids=[site[0] for site in SITES])
def test_unsupported_integer_version_is_refused_and_not_echoed(label, path, entry, tmp_path) -> None:
    resolved, errors = _resolve(label, path, entry, 9, tmp_path)
    assert _version_errors(errors) == ["version must be 1"], f"{label} accepted version 9: {errors}"
    assert resolved.get("version") != 9, f"{label} echoed the unsupported version back as authoritative"


def test_simple_adapter_does_not_honor_sibling_fields_after_version_refusal(tmp_path: Path) -> None:
    simple = _module("scripts/simple_skill_adapter_lib.py")

    resolved, errors, _warnings = simple.validate_simple_adapter_data(
        {
            "version": 9,
            "repo": "attacker-selected-repo",
            "output_dir": "attacker-selected-output",
        },
        repo_root=tmp_path,
        output_dir="safe-output",
    )

    assert errors == ["version must be 1"]
    assert resolved["repo"] == tmp_path.name
    assert resolved["output_dir"] == "safe-output"


# The fields a misversioned -- or hostile -- adapter would use to STEER a reader rather
# than merely misdescribe itself.
#
# The identity/path block came first and is the weakest half: at three rows it was the
# ONLY thing live, so one resolver proved that `repo` was contained on a resolver whose
# real surface is command templates this repo shells out to. The command-list and
# boolean block below exists because of that -- a probe that reaches only identity
# strings is a probe that cannot see the fields worth containing. Two booleans in
# particular disarm a gate by being present: `require_derived_release_claims` and
# `require_explicit_apply` both default TRUE, so `false` is the value that matters.
#
# Deliberately no MAPPING-typed fields (`issue_backend`, `gather_provider`,
# `packet_sections`, `scaffold`). They are covered by the bespoke tests in this file and
# in `tests/test_capability_catalog.py`; expressing them here would need per-family
# shapes, and a wrong shape measures a type refusal rather than containment.
CONTAINMENT_PROBE: dict[str, Any] = {
    "repo": "attacker-selected-repo",
    "language": "attacker-selected-language",
    "output_dir": "attacker-selected-output",
    "artifact_dir": "attacker-selected-artifact-dir",
    "default_org": "attacker-selected-org",
    "max_artifact_lines": 4321,
    "max_content_lines": 4321,
    "eval_test_command": "attacker-selected-eval-command",
    "gate_commands": ["attacker-selected-gate-command"],
    "preflight_commands": ["attacker-selected-preflight-command"],
    "cli_skill_surface_probe_commands": ["attacker-selected-probe-command"],
    "required_release_surfaces": ["attacker-selected-surface"],
    "trusted_skill_roots": ["attacker-selected-root"],
    "discussion_deploy_vocab": ["attacker-selected-vocab"],
    "landing_danger_checks": ["attacker-selected-check"],
    "require_derived_release_claims": False,
    "require_explicit_apply": False,
}

# Every SITES row except the commit-time gate, which raises instead of returning a
# resolved payload -- the harness synthesizes its dict, so a containment assertion there
# would be an assertion about the fixture. Its own containment is that it refuses the
# whole file, proven by the wording tests above.
CONTAINMENT_SITES = tuple(site for site in SITES if site[0] != "validate_adapters_gate")


@pytest.mark.parametrize(
    ("label", "path", "entry"), CONTAINMENT_SITES, ids=[site[0] for site in CONTAINMENT_SITES]
)
def test_no_declared_sibling_survives_a_version_refusal(label, path, entry, tmp_path) -> None:
    """The census-wide half of the version contract, which the two bespoke tests around it
    could only assert for their own family.

    Measured when this was written: 15 of the 18 reconciling sites refused the version and
    then honored every sibling anyway, so a `version: 9` adapter still selected
    `output_dir`, `repo`, `language` and the debug/quality line ceilings. Only
    `simple_skill`, `issue` and `capability_catalog` contained. A version the reader cannot
    interpret says nothing about what its siblings MEAN, so honoring them is a declaration
    steering a gate through a schema no reader read.

    Asserted as equality against the version-only payload rather than field by field, so
    a field the site DERIVES into a differently-named key is covered too. That is
    schema-agnostic on the OUTPUT side only: a field this probe never declares cannot
    appear in either payload, so `CONTAINMENT_PROBE` still has to name a site's steering
    fields, and the liveness test below is what forces that to stay true.

    The error list is asserted EXACTLY, not filtered through `_version_errors`. Filtering
    let a resolver refuse the version and then go on reading and type-checking every
    sibling -- reporting `output_dir must be a string` about a schema it just said it
    could not read. Exact equality is available here precisely because containment means
    no sibling is read, and it is what makes the documented "the only error is the
    version refusal" an assertion rather than a claim.
    """
    contained, errors = _resolve_declared(
        label, path, entry, {"version": 9, **CONTAINMENT_PROBE}, tmp_path
    )
    bare, _ = _resolve_declared(label, path, entry, {"version": 9}, tmp_path)

    assert errors == ["version must be 1"], f"{label} read siblings past the version refusal: {errors}"
    honored = {key: value for key, value in contained.items() if bare.get(key) != value}
    assert not honored, f"{label} honored declared fields after refusing the version: {honored}"


@pytest.mark.parametrize(
    ("label", "path", "entry"), CONTAINMENT_SITES, ids=[site[0] for site in CONTAINMENT_SITES]
)
def test_the_containment_probe_actually_steers_every_site_it_covers(label, path, entry, tmp_path) -> None:
    """The polarity control for the containment test, and the reason it is not vacuous.

    Nothing in the containment assertion distinguishes "this site refused the probe" from
    "none of these field names exist in this site's schema". A row whose schema shares no
    field with the probe would pass containment forever while proving nothing, and would
    keep passing after the containment was removed. So each row must show at least one
    probe field reaching its resolved payload on a version it DOES speak. A failure here
    means the probe needs that site's own steering field added -- not that the site is
    contained.
    """
    steered, _ = _resolve_declared(label, path, entry, {"version": 1, **CONTAINMENT_PROBE}, tmp_path)
    bare, _ = _resolve_declared(label, path, entry, {"version": 1}, tmp_path)

    reached = {key: value for key, value in steered.items() if bare.get(key) != value}
    assert reached, (
        f"no CONTAINMENT_PROBE field reaches {label}'s resolved payload on a supported "
        f"version, so its containment row proves nothing; add a field this site honors. "
        f"Probe fields offered: {sorted(CONTAINMENT_PROBE)}"
    )


def test_issue_adapter_does_not_honor_backend_or_target_after_version_refusal(tmp_path: Path) -> None:
    issue = _module("skills/public/issue/scripts/resolve_adapter.py")
    adapter = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 9\n"
        "default_org: attacker\n"
        "default_repo: target\n"
        "issue_backend:\n  id: hostile\n  binary: hostile-provider\n",
        encoding="utf-8",
    )

    report = issue.load_adapter(tmp_path)

    assert report["errors"] == ["version must be 1"]
    assert report["data"]["default_org"] == "corca-ai"
    assert report["data"]["default_repo"] is None
    assert report["data"]["issue_backend"]["id"] == "gh"


@pytest.mark.parametrize(("label", "path", "entry"), SITES, ids=[site[0] for site in SITES])
def test_boolean_version_is_refused_as_a_non_integer(label, path, entry, tmp_path) -> None:
    """`isinstance(True, int)` is True, and this repo's YAML loader coerces a bare
    `true` to `True`. Before the shared check, `version: true` therefore read as a valid
    integer version at ALL 17 sites -- including the single one that did compare against
    a supported value."""
    resolved, errors = _resolve(label, path, entry, True, tmp_path)
    assert _version_errors(errors) == ["version must be an integer"], f"{label} accepted a boolean version: {errors}"
    assert resolved.get("version") is not True, f"{label} echoed a boolean version back as authoritative"


@pytest.mark.parametrize(("label", "path", "entry"), SITES, ids=[site[0] for site in SITES])
def test_non_integer_version_is_refused(label, path, entry, tmp_path) -> None:
    resolved, errors = _resolve(label, path, entry, "1", tmp_path)
    assert _version_errors(errors) == ["version must be an integer"], f"{label} accepted a string version: {errors}"
    assert resolved.get("version") != "1", f"{label} echoed a string version back as authoritative"


@pytest.mark.parametrize(("label", "path", "entry"), SITES, ids=[site[0] for site in SITES])
def test_supported_version_stays_clean(label, path, entry, tmp_path) -> None:
    """The polarity control. Every adapter shipped in this repo declares `version: 1`, so
    a check that refused the supported value would break every one of them -- and each
    refusal test above would still pass, because they only assert that a refusal fires."""
    resolved, errors = _resolve(label, path, entry, 1, tmp_path)
    assert _version_errors(errors) == [], f"{label} refused the supported version: {errors}"
    assert resolved.get("version") == 1


@pytest.mark.parametrize(
    "adapter_name",
    ["probe-adapter.yaml", "critique-adapter.yaml",
     "retro-adapter.yaml", "quality-adapter.yaml"],
)
def test_the_commit_gate_requires_a_declared_version_for_every_adapter_name(adapter_name, tmp_path) -> None:
    """The filename-specific rows are the point.

    `validate_adapter_yaml` dispatches on filename, and two of those branches
    (`critique-adapter.yaml`) RETURN before the rest of the
    function runs. With the version floor below them, those two files skipped it entirely
    while the gate read as though it covered every adapter -- and their resolvers treat an
    absent version as legal, correctly for a resolver, so nothing else refused it either.
    A probe file with a generic name cannot see that: it matches no branch.
    """
    gate = _module("scripts/gates/validate_adapters.py")
    probe = tmp_path / ".agents" / adapter_name
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("repo: probe\n", encoding="utf-8")

    with pytest.raises(gate.ValidationError) as excinfo:
        gate.validate_adapter_yaml(probe)
    assert "version is required" in str(excinfo.value)


def test_the_shared_check_writes_the_accepted_version_itself() -> None:
    """Proves the ACCEPT branch, which the per-site polarity test cannot.

    Every resolver's `infer_defaults` already seeds `version: 1`, so all 18 of the 18
    sites `resolved["version"] == 1` holds whether or not the shared check writes
    anything -- deleting its `else: validated[field] = value` branch entirely would
    leave those assertions green. Passing an EMPTY dict is the only way to observe the
    write, so the branch is pinned here rather than relied on there.
    """
    validated: dict[str, Any] = {}
    errors: list[str] = []
    ADAPTER_LIB.validate_adapter_version({"version": 1}, validated, errors)
    assert (validated, errors) == ({"version": 1}, [])


def test_supported_version_is_read_at_call_time_not_bound_at_import() -> None:
    """A bump -- or a test proving the bump path -- rebinds the module constant. If
    `supported` were a plain default argument it would have captured the value once at
    import, so the rebind would appear to work and change nothing."""
    validated: dict[str, Any] = {}
    errors: list[str] = []
    original = ADAPTER_LIB.SUPPORTED_ADAPTER_VERSION
    try:
        ADAPTER_LIB.SUPPORTED_ADAPTER_VERSION = 2
        ADAPTER_LIB.validate_adapter_version({"version": 2}, validated, errors)
    finally:
        ADAPTER_LIB.SUPPORTED_ADAPTER_VERSION = original
    assert (validated, errors) == ({"version": 2}, [])


def test_every_repo_local_adapter_declares_the_supported_version() -> None:
    """The blast-radius measurement, kept executable rather than recorded as a claim.

    Slice 1 was safe to arm because every adapter this repo ships already declares
    `version: 1`. If that stops being true, this fails and names the file, instead of the
    refusal firing for the first time in someone's run.
    """
    # `.agents/command-docs.yaml` is deliberately excluded: its `version` belongs to an
    # unrelated schema, and a legitimate bump there would fail this test for a reason
    # that has nothing to do with adapter resolvers.
    patterns = (
        ".agents/*-adapter.yaml",
        "skills/public/*/adapter.example.yaml",
        "integrations/*/adapter.example.yaml",
    )
    declared: dict[str, str] = {}
    for path in sorted(candidate for pattern in patterns for candidate in ROOT.glob(pattern)):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("version:"):
                declared[str(path.relative_to(ROOT))] = line.split(":", 1)[1].strip()
                break
    # Per-pattern, not whole-set: with a single `assert declared` guard, three of four
    # patterns could be typo'd and the fourth alone would keep this green -- a measurement
    # reporting a coverage it no longer has.
    for pattern in patterns:
        assert any(path.startswith(pattern.split("*")[0]) for path in declared), (
            f"pattern {pattern!r} matched no adapter declaring a version; "
            "the pattern is stale, or a shipped adapter lost its version line"
        )
    assert set(declared.values()) == {"1"}, f"not every adapter declares version 1: {declared}"


def test_the_stated_census_counts_match_the_lists() -> None:
    """The denominator, pinned. Prose counts beside a list rot silently, and this file's
    entire claim is a census."""
    assert (len(SITES), len(EXEMPT_SITES)) == (18, 4)


def test_exempt_sites_carry_a_reason() -> None:
    """Presence-only rows are how an exemption list rots into a hiding place."""
    for label, _paths, _tests, reason in EXEMPT_SITES:
        assert reason.strip(), f"exempt site {label} carries no reason"


def _resolve_test_ref(ref: str) -> str | None:
    """Return why ``path::function`` does not resolve, or None when it does."""
    path, _, function = ref.partition("::")
    target = ROOT / path
    if not target.is_file():
        return f"{path} does not exist"
    if function and f"def {function}(" not in target.read_text(encoding="utf-8"):
        return f"{path} has no `def {function}(`"
    return None


def test_every_exempt_site_names_a_test_that_actually_exists() -> None:
    """An exemption's reason is prose; the test it names is the only part that can be
    checked. Without this, a rename turns an exemption into a silent lie on the exact
    surface whose job is to refuse unverified claims -- and the row would still pass the
    non-empty-reason check above."""
    unresolved = [
        (label, ref, problem)
        for label, _paths, refs, _reason in EXEMPT_SITES
        for ref in refs
        if (problem := _resolve_test_ref(ref)) is not None
    ]
    assert not unresolved, f"exempt sites name tests that do not resolve: {unresolved}"
    for label, _paths, refs, _reason in EXEMPT_SITES:
        assert refs, f"exempt site {label} names no driving test"


def test_verdict_consumers_resolve() -> None:
    """The consumer list is not a coverage claim, but a stale path in it would misdescribe
    where a correct refusal can still be discarded."""
    missing = [
        path
        for _label, paths, _tests in VERDICT_CONSUMERS
        for path in paths
        if not (ROOT / path).is_file()
    ]
    assert not missing, f"verdict-consumer paths do not exist: {missing}"
