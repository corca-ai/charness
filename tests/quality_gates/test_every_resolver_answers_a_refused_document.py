"""All sixteen public resolvers answer a malformed adapter the same way.

ONE test over every resolver, replacing the per-family branches three test files carried.
Those branches were honest — they recorded that `quality`, `critique`, `narrative`,
`achieve` and `create-skill` let a parser refusal out as a raw traceback while the other
eleven recorded it — but a test that BRANCHES on which resolver family it is talking to
cannot notice when the families converge or diverge again. This asserts the shared shape
and lets the resolver list come from the filesystem.

WHAT THIS PROVES, in the vocabulary the consumer guards actually use. `adapter_version_verdict`
refuses on the CONDITION "this reader honored nothing the repo declared" and reaches it
through three doors: `version_refused` (an unspeakable `version`), `parse_refused` (a
document the parser would not read), and `declarations_dropped` (a line silently dropped).
The first was always reachable everywhere. The other two key on `errors` and `warnings`
respectively, so a resolver that RAISED before either existed made both structurally dead
for its skill's consumers — the guard had a blind arm and no test could see it, because the
resolver never returned. These tests ask the predicates directly rather than matching
message text, so a wording change cannot silently satisfy them.

WHAT IT DELIBERATELY DOES NOT ASSERT: a uniform exit code. Fourteen resolvers exit 0 with
`valid: false` and two (`critique`, `issue`) exit 1, on the same input.

AND THIS CHANGE MOVED FOUR OF THEM, which a first draft of this docstring wrongly called a
divergence that "predates this change". Before `#673`, `achieve`, `create-skill`,
`narrative` and `quality` exited NON-ZERO on a refused parse -- by tracebacking. Making them
render a verdict made them exit 0, and a bounded review found that a consumer keyed on
exactly that: `scripts/artifacts/resolve_artifact_path.py` treated the subprocess return code as its
only protection and began resolving a charness default over a repo that declared otherwise.
That consumer is guarded on the CONDITION now. The exit codes themselves are still not
normalised -- that is a behavior change for every caller that branches on them -- so the
split is PINNED in `NON_ZERO_EXIT_SKILLS` and a move in either direction is a diff rather
than a silence. The real-process smoke below keeps that delivery contract visible while the
semantic matrix runs in-process.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.adapters import adapter_version_verdict
from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]
RESOLVERS = sorted((ROOT / "skills" / "public").glob("*/scripts/resolve_adapter.py"))

# A construct `adapter_lib._reject_unsupported_scalar` refuses outright, and a stray indent
# `_parse_block` silently drops. One per door.
REFUSED_PARSE = "version: !!int 9\nrepo: demo\n"
DROPPED_LINE = "version: 1\n  repo: demo\n"

# The two resolvers that exit non-zero on a `valid: false` payload. Recorded from a
# measurement at the repair, not from reading the code, and pinned so a change in either
# direction shows up as a diff to this list rather than as silence.
NON_ZERO_EXIT_SKILLS = frozenset({"critique", "issue"})


def _skill(resolver: Path) -> str:
    return resolver.parents[1].name


def _resolver_module(resolver: Path) -> object:
    return load_script_module(f"resolver_refusal_{_skill(resolver)}", resolver)


def _write_adapter(resolver: Path, tmp_path: Path, document: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / f"{_skill(resolver)}-adapter.yaml").write_text(document, encoding="utf-8")
    return repo


def _resolve_subprocess(
    resolver: Path, tmp_path: Path, document: str
) -> tuple[dict, subprocess.CompletedProcess]:
    repo = _write_adapter(resolver, tmp_path, document)
    done = subprocess.run(
        [sys.executable, str(resolver), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    payload = yaml.safe_load(done.stdout) if done.stdout.strip() else None
    return (payload if isinstance(payload, dict) else {}), done


def _resolve_in_process(resolver: Path, tmp_path: Path, document: str) -> tuple[dict, object]:
    repo = _write_adapter(resolver, tmp_path, document)
    done = run_loaded_script_main(
        str(resolver), _resolver_module(resolver), "--repo-root", str(repo)
    )
    payload = yaml.safe_load(done.stdout) if done.stdout.strip() else None
    return (payload if isinstance(payload, dict) else {}), done


def _resolve_without_adapter_in_process(resolver: Path, tmp_path: Path) -> tuple[dict, object]:
    """The opt-in baseline: a repo that declared nothing. Writing an EMPTY document instead
    is a different input entirely -- the file exists, so `found` is True and the resolver is
    reporting on a document rather than on its absence."""
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    done = run_loaded_script_main(
        str(resolver), _resolver_module(resolver), "--repo-root", str(repo)
    )
    payload = yaml.safe_load(done.stdout) if done.stdout.strip() else None
    return (payload if isinstance(payload, dict) else {}), done


# The SET, not a count. A `>= 15` floor does not deliver what a roster assertion must: there
# are twenty public skills and fifteen resolvers, so a resolver renamed or moved out of
# `skills/public/*/scripts/resolve_adapter.py` at the same time any new skill gains one keeps
# the count at fifteen and silently drops the regressed row from every sweep below. Naming
# them turns that into a diff, which is the same argument `NON_ZERO_EXIT_SKILLS` makes.
EXPECTED_RESOLVER_SKILLS = frozenset(
    {
        "achieve",
        "announcement",
        "create-skill",
        "critique",
        "debug",
        "gather",
        "hitl",
        "hotl",
        "impl",
        "issue",
        "narrative",
        "quality",
        "release",
        "retro",
        "setup",
    }
)


def test_the_resolver_roster_is_complete():
    """A glob that matched fewer resolvers would make every parametrized case below pass by
    not existing."""
    assert {_skill(path) for path in RESOLVERS} == EXPECTED_RESOLVER_SKILLS


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
@pytest.mark.boundary_contract(
    reason="exact per-resolver exit-code and stderr contract for a refused adapter document"
)
def test_a_refused_parse_renders_a_verdict_and_never_a_traceback(resolver: Path, tmp_path: Path):
    """One real process smoke; the remaining assertions use in-process calls."""
    payload, done = _resolve_subprocess(resolver, tmp_path, REFUSED_PARSE)
    assert "Traceback" not in done.stderr, done.stderr
    assert payload, f"no rendered payload: {done.stdout!r} {done.stderr!r}"
    assert payload["found"] is True
    assert payload["valid"] is False
    expected = 1 if _skill(resolver) in NON_ZERO_EXIT_SKILLS else 0
    assert done.returncode == expected, f"{_skill(resolver)} exited {done.returncode}"
    # The payload must still be the reader's own inferred defaults, not absent: that is the
    # state every consumer guard is written against.
    assert isinstance(payload.get("data"), dict) and payload["data"]


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_the_parse_refusal_door_is_reachable(resolver: Path, tmp_path: Path):
    """`adapter_version_verdict.parse_refused` answered False for five resolvers, for
    inputs it was written to catch, because they raised instead of recording."""
    payload, _ = _resolve_in_process(resolver, tmp_path, REFUSED_PARSE)
    assert adapter_version_verdict.parse_refused(payload.get("errors")), payload.get("errors")
    assert adapter_version_verdict.declarations_unhonored(payload.get("errors"))


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_the_dropped_line_door_is_reachable(resolver: Path, tmp_path: Path):
    """`declarations_dropped` reads `warnings`, which the bare loader discarded entirely --
    so a repo's declaration could vanish with `errors: []` and `valid: true`."""
    payload, done = _resolve_in_process(resolver, tmp_path, DROPPED_LINE)
    assert "Traceback" not in done.stderr, done.stderr
    assert adapter_version_verdict.declarations_dropped(payload), payload.get("warnings")


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_a_speakable_well_formed_document_is_honored(resolver: Path, tmp_path: Path):
    """The polarity control, and it proves POLARITY only.

    Without it every assertion above is satisfied by a resolver that refuses everything,
    which is a shape this repo has shipped. What it does NOT prove is that any declared
    value reached the payload: a resolver that reads the file and honors no key passes all
    six sweep cases. That property is per-skill and is asserted per-skill --
    `test_quality_readers_version_refusal` and `test_narrative_impl_version_refusal` both
    check honored VALUES. Said out loud because the first version of this docstring read as
    if the sweep covered it."""
    payload, done = _resolve_in_process(resolver, tmp_path, "version: 1\nrepo: demo\n")
    assert "Traceback" not in done.stderr, done.stderr
    assert payload["found"] is True
    assert payload["valid"] is True, payload.get("errors")
    assert not adapter_version_verdict.declarations_unhonored(payload.get("errors"))
    assert not adapter_version_verdict.declarations_dropped(payload)
    # Against a repo with NO adapter at all, not against a hard-coded field. `issue` renders
    # no `repo` key, so asserting one made this control pass for fifteen resolvers and fail
    # for the sixteenth on the test's own assumption rather than on any behavior.
    absent, _ = _resolve_without_adapter_in_process(resolver, tmp_path / "empty")
    assert absent["found"] is False
    assert payload["found"] != absent["found"]
