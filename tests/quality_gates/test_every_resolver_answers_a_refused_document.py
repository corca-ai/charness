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

WHAT IT DELIBERATELY DOES NOT ASSERT: a uniform exit code. Measured at the repair,
fourteen resolvers exit 0 with `valid: false` and two (`critique`, `issue`) exit 1, on the
same input. That divergence predates this change, is not what made a consumer guard blind,
and normalising sixteen CLI exit codes is a behavior change for every caller that branches
on them. It is RECORDED below rather than asserted away — see
`test_the_exit_code_divergence_is_recorded_rather_than_asserted_uniform`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts import adapter_version_verdict

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


def _resolve(resolver: Path, tmp_path: Path, document: str) -> tuple[dict, subprocess.CompletedProcess]:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / f"{_skill(resolver)}-adapter.yaml").write_text(document, encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(resolver), "--repo-root", str(repo)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )
    payload = yaml.safe_load(done.stdout) if done.stdout.strip() else None
    return (payload if isinstance(payload, dict) else {}), done


def _resolve_without_adapter(resolver: Path, tmp_path: Path) -> tuple[dict, subprocess.CompletedProcess]:
    """The opt-in baseline: a repo that declared nothing. Writing an EMPTY document instead
    is a different input entirely -- the file exists, so `found` is True and the resolver is
    reporting on a document rather than on its absence."""
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    done = subprocess.run(
        [sys.executable, str(resolver), "--repo-root", str(repo)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )
    payload = yaml.safe_load(done.stdout) if done.stdout.strip() else None
    return (payload if isinstance(payload, dict) else {}), done


def test_the_resolver_roster_is_complete():
    """A glob that matched fewer resolvers would make every parametrized case below pass by
    not existing. Sixteen is the count `#673` measured; the assertion is `>=` because adding
    a public skill must not silently drop it from this sweep."""
    assert len(RESOLVERS) >= 16, [str(path.relative_to(ROOT)) for path in RESOLVERS]


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_a_refused_parse_renders_a_verdict_and_never_a_traceback(resolver: Path, tmp_path: Path):
    payload, done = _resolve(resolver, tmp_path, REFUSED_PARSE)
    assert "Traceback" not in done.stderr, done.stderr
    assert payload, f"no rendered payload: {done.stdout!r} {done.stderr!r}"
    assert payload["found"] is True
    assert payload["valid"] is False
    # The payload must still be the reader's own inferred defaults, not absent: that is the
    # state every consumer guard is written against.
    assert isinstance(payload.get("data"), dict) and payload["data"]


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_the_parse_refusal_door_is_reachable(resolver: Path, tmp_path: Path):
    """`adapter_version_verdict.parse_refused` answered False for five resolvers, for
    inputs it was written to catch, because they raised instead of recording."""
    payload, _ = _resolve(resolver, tmp_path, REFUSED_PARSE)
    assert adapter_version_verdict.parse_refused(payload.get("errors")), payload.get("errors")
    assert adapter_version_verdict.declarations_unhonored(payload.get("errors"))


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_the_dropped_line_door_is_reachable(resolver: Path, tmp_path: Path):
    """`declarations_dropped` reads `warnings`, which the bare loader discarded entirely --
    so a repo's declaration could vanish with `errors: []` and `valid: true`."""
    payload, done = _resolve(resolver, tmp_path, DROPPED_LINE)
    assert "Traceback" not in done.stderr, done.stderr
    assert adapter_version_verdict.declarations_dropped(payload), payload.get("warnings")


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_a_speakable_well_formed_document_is_honored(resolver: Path, tmp_path: Path):
    """The polarity control. Without it every assertion above is satisfied by a resolver
    that refuses everything, which is the shape this repo has shipped before."""
    payload, done = _resolve(resolver, tmp_path, "version: 1\nrepo: demo\n")
    assert "Traceback" not in done.stderr, done.stderr
    assert payload["found"] is True
    assert payload["valid"] is True, payload.get("errors")
    assert not adapter_version_verdict.declarations_unhonored(payload.get("errors"))
    assert not adapter_version_verdict.declarations_dropped(payload)
    # Against a repo with NO adapter at all, not against a hard-coded field. `issue` renders
    # no `repo` key, so asserting one made this control pass for fifteen resolvers and fail
    # for the sixteenth on the test's own assumption rather than on any behavior.
    absent, _ = _resolve_without_adapter(resolver, tmp_path / "empty")
    assert absent["found"] is False
    assert payload["found"] != absent["found"]


@pytest.mark.parametrize("resolver", RESOLVERS, ids=_skill)
def test_the_exit_code_divergence_is_recorded_rather_than_asserted_uniform(resolver: Path, tmp_path: Path):
    """`#673`'s acceptance says "non-zero exit", and this repair did NOT deliver that half.

    Fourteen resolvers exit 0 with `valid: false`; `critique` and `issue` exit 1. That
    divergence predates the parse-refusal repair, is not what made a consumer guard blind,
    and normalising it changes behavior for every caller that branches on the exit code.
    Pinning the current split here means a change in either direction is a diff to
    `NON_ZERO_EXIT_SKILLS`, not a silence — which is the honest form of a residual.
    """
    _payload, done = _resolve(resolver, tmp_path, REFUSED_PARSE)
    expected = 1 if _skill(resolver) in NON_ZERO_EXIT_SKILLS else 0
    assert done.returncode == expected, f"{_skill(resolver)} exited {done.returncode}"
