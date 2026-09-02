"""`write_artifact_path` means ONE thing, and says whether writing destroys anything.

#548. FOUR modules implemented the same pointer-resolution rule, three of them emitting the
`write_artifact_path` / `write_artifact_role` pair from separate code:

- `scripts/core/scaffold_artifact_lib.py` (quality, handoff, ideation, retro scaffolds) — now the
  single owner
- `scripts/artifacts/resolve_artifact_path.py` (debug and the generic path)
- `skills/public/quality/scripts/resolve_quality_artifact.py`
- `scripts/artifacts/inventory_current_pointer_layouts.py` — the fourth, which the duplicate-ratchet
  gate surfaced while the first three were being consolidated; it reports on pointer layouts,
  so a drift there would make the inventory disagree with the payloads it inventories

Nothing forced the copies to agree, so the key came to mean different things depending on
which producer a skill happened to call. `#538` is the recorded instance: `quality/SKILL.md`
said "write the dated `write_artifact_path`" while that path was the PREVIOUS review's file,
and because the filename is dated nothing afterwards would have looked wrong.

Two properties are pinned here, and the first is the one the goal's own boundary demands of
any consolidation — a test that fails if the consumers diverge again:

1. No consumer keeps a private copy of the rule, and the runnable ones agree.
2. The payload states the CONSEQUENCE of writing, not only the location. Role
   `current_pointer_target` is true and reads as neutral; `write_artifact_effect` says
   whether that target already holds content.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module
from tests.quality_gates.support import ROOT

_scaffold_lib = import_repo_module(
    ROOT / "scripts/core/scaffold_artifact_lib.py", "scripts.core.scaffold_artifact_lib"
)
_resolve_quality_artifact = import_repo_module(
    ROOT / "skills/public/quality/scripts/resolve_quality_artifact.py",
    "skills.public.quality.scripts.resolve_quality_artifact",
)
_scaffold_debug = import_repo_module(
    ROOT / "skills/public/debug/scripts/scaffold_debug_artifact.py",
    "skills.public.debug.scripts.scaffold_debug_artifact",
)
_scaffold_critique = import_repo_module(
    ROOT / "skills/public/critique/scripts/scaffold_critique_artifact.py",
    "skills.public.critique.scripts.scaffold_critique_artifact",
)
_scaffold_retro = import_repo_module(
    ROOT / "skills/public/retro/scripts/scaffold_retro_artifact.py",
    "skills.public.retro.scripts.scaffold_retro_artifact",
)


def _seed_resolved_debug_pointer(repo: Path) -> Path:
    """A debug current pointer whose record is marked resolved, so the followup branch fires."""
    # Real adapter schema: top-level `output_dir` and an `artifact_class` the resolver
    # accepts. The first version of this fixture used `schema_version:` plus a nested `data:`
    # and an invented class, so every producer silently fell back to inferred repo defaults
    # and the fixture only APPEARED to configure the output directory — the
    # fixture-supplies-its-own-premise family this slice's sibling issue is about.
    _seed_adapter(repo, "debug")
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text(
        "# Demo\n\n## Interrupt Decision\n\n- Resolution: resolved\n", encoding="utf-8"
    )
    (debug_dir / "latest.md").symlink_to(target.name)
    return target


def _producer_payloads(tmp_path: Path) -> dict[str, dict[str, object]]:
    """Every producer that names a write target, each in its own seeded repo."""
    payloads: dict[str, dict[str, object]] = {}

    quality_repo = tmp_path / "quality"
    _seed_pointer(quality_repo, "symlink_to_existing")
    _seed_adapter(quality_repo, "quality")
    payloads["quality:current"] = _resolve_quality_artifact.payload_for(
        quality_repo, slug="quality review", intent="current", artifact_date=dt.date(2026, 1, 3)
    )
    payloads["quality:current"]["_repo_root"] = quality_repo
    payloads["quality:record"] = _resolve_quality_artifact.payload_for(
        quality_repo, slug="quality review", intent="record", artifact_date=dt.date(2026, 1, 3)
    )
    payloads["quality:record"]["_repo_root"] = quality_repo

    debug_repo = tmp_path / "debug"
    _seed_resolved_debug_pointer(debug_repo)
    payloads["debug:resolved-followup"] = _scaffold_debug.payload_for(debug_repo, title=None)
    payloads["debug:resolved-followup"]["_repo_root"] = debug_repo

    for label, module, output in (
        ("critique", _scaffold_critique, "critique"),
        ("retro", _scaffold_retro, "retro"),
    ):
        repo = tmp_path / label
        _seed_adapter(repo, output)
        payloads[label] = module.payload_for(repo, title="Probe")
        payloads[label]["_repo_root"] = repo

    return payloads


def _seed_adapter(repo: Path, skill_id: str, *, artifact_class: str = "history") -> None:
    """Write an adapter the skill's own resolver actually accepts.

    `artifact_class` is one of the three the repo defines (`current`, `history`, `rolling`), and
    `history` is the one that supports dated records — the class `debug` itself declares;
    `output_dir` is top-level, not nested. Getting this wrong does not fail loudly — the
    resolver reports `valid: false` and the producer falls back to inferred defaults, so a
    wrong fixture still passes while proving nothing about adapter-configured output.
    """
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / f"{skill_id}-adapter.yaml").write_text(
        f"version: 1\nrepo: fixture\noutput_dir: charness-artifacts/{skill_id}\n"
        f"artifact_class: {artifact_class}\n",
        encoding="utf-8",
    )


def _seed_pointer(repo: Path, case: str) -> Path:
    out = repo / "charness-artifacts" / "quality"
    out.mkdir(parents=True, exist_ok=True)
    pointer = out / "latest.md"
    if case == "regular_file":
        pointer.write_text("# Current\n", encoding="utf-8")
    elif case == "symlink_to_existing":
        target = out / "2026-01-02-quality-review.md"
        target.write_text("# A finished review\n", encoding="utf-8")
        pointer.symlink_to(target.name)
    elif case == "symlink_to_missing":
        pointer.symlink_to("2026-01-02-quality-review.md")
    return pointer


# Spellings that resolve a symlink. `os.readlink(` alone was too narrow to be the guard it
# claimed to be: `Path.readlink()` is the idiom used elsewhere in this repo, so the easiest
# way to reintroduce a private copy was also the one the check could not see.
_SYMLINK_RESOLUTION_SPELLINGS = (
    "os.readlink(",
    ".readlink()",
    "os.path.realpath(",
    "from os import readlink",
)
_OWNER_REL = "scripts/core/scaffold_artifact_lib.py"
# How a module may legitimately obtain the write-target facts: by stamping them, by using the
# owner's shared record shape, or by being the owner.
_FACT_ROUTES = (
    "with_write_target_facts(",
    "dated_record_payload(",
    "write_target_facts(",
    "current_pointer_payload(",
    # The records-only shape, which resolves the path by subject and then delegates to
    # `dated_record_payload` for the facts — one hop further from the owner than the routes
    # above, and still the owner's code doing the stamping.
    "subject_scoped_record_payload(",
    # A planner may ECHO the scaffold payload's fact rather than recompute it; that is the
    # correct thing for a surface that reports someone else's write target.
    '"write_artifact_effect"',
)


# Roots scanned for producers. `skills/support` and `skills/shared` are included because the
# repo's older sibling gate (`tools/check_current_pointer_writes.py`) records that omitting
# `skills/shared` once produced a clean report over a scope that excluded a real violation.
_PRODUCER_ROOTS = ("scripts", "skills/public", "skills/support", "skills/shared")
# How a module can emit the key. Both literal spellings, AND the delegation calls -- because
# the two scaffolds this issue is actually about (`scaffold_quality_artifact.py`,
# `scaffold_debug_artifact.py`) build their payload by delegation and never spell the key at
# all, so a literal-only predicate excluded the issue's own subjects. That was the first
# version of this guard, and a bounded round caught it.
_KEY_LITERALS = (
    '"write_artifact_path":',
    "'write_artifact_path':",
    "write_artifact_path=write_artifact_path",
)
_DELEGATED_PAYLOAD_CALLS = (
    "current_pointer_payload(",
    "dated_record_payload(",
    "with_write_target_facts(",
    # The subject-identity slice added a fourth delegation, and the sweep's population fell
    # from eleven producers to eight the moment three families started routing through it.
    # The floor below is what caught that; a sweep whose population silently shrinks reports
    # clean over the producers it stopped seeing.
    "subject_scoped_record_payload(",
)
# A payload key built by string assembly would evade any literal scan. The sibling gate
# records this exact escape (an `f"latest.{ext}"` slipped a verbatim-filename scan), so the
# sweep refuses rather than reporting clean over a scope it cannot see.
_DYNAMIC_KEY_SHAPES = ('payload[f"write_artifact', "payload[f'write_artifact")


def _modules_naming_a_write_target() -> dict[str, str]:
    """DERIVED FROM THE TREE, never hand-listed.

    Two earlier versions of this guard were the defect one level up. The first kept a
    hand-maintained producer list — the same shape as `scaffold_debug_artifact`'s
    hand-maintained key list, which is how the two new facts went stale — and it was already
    missing four producers. The second globbed but matched only a dict-literal key, so it
    excluded every producer that builds its payload by DELEGATION, which is both scaffolds the
    issue names. A guard whose population is a proxy for the real one is this repo's recurring
    trap; it is now selected by literal OR delegation call.
    """
    found: dict[str, str] = {}
    for root in _PRODUCER_ROOTS:
        root_path = ROOT / root
        if not root_path.is_dir():
            continue
        for path in sorted(root_path.rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            for shape in _DYNAMIC_KEY_SHAPES:
                assert shape not in source, (
                    f"{path.relative_to(ROOT)} assembles the write-target key name dynamically; "
                    "this sweep cannot see such a producer, so widen it rather than trusting it"
                )
            # A PRODUCER emits the key; a CONSUMER only reads it back out.
            # `inventory_current_pointer_layouts.py` reports other skills' write targets and
            # owes no facts of its own, so reading the key is deliberately not enough.
            emits_key = any(literal in source for literal in _KEY_LITERALS)
            # No `write_artifact_path` requirement here on purpose: `scaffold_quality_artifact.py`
            # returns `current_pointer_payload(...)` and never mentions the key, which is
            # precisely why a literal-only sweep excluded it.
            builds_by_delegation = "def payload_for(" in source and any(
                call in source for call in _DELEGATED_PAYLOAD_CALLS
            )
            if emits_key or builds_by_delegation:
                found[str(path.relative_to(ROOT))] = source
    return found


def test_no_module_resolves_a_pointer_symlink_except_the_owner() -> None:
    """The consolidation's structural guard: a re-grown private copy fails here.

    Comparing outputs would pass on the day a copy is reintroduced with identical behaviour
    and only start failing once it drifted — which is the window this defect lived in. So the
    invariant is structural: resolving a current pointer belongs to one module.

    Honest about its reach: it greps for the spellings above, so a copy that reimplements the
    rule some other way evades it. A bounded round found exactly that — a copy derived from
    the published pointer keys rather than from `readlink` — so this is a ratchet against the
    likely regression, not a proof.
    """
    owner = (ROOT / _OWNER_REL).read_text(encoding="utf-8")
    assert any(spelling in owner for spelling in _SYMLINK_RESOLUTION_SPELLINGS), (
        "the owner no longer resolves the symlink; re-anchor this test"
    )

    for relative, source in _modules_naming_a_write_target().items():
        if relative == _OWNER_REL:
            continue
        for spelling in _SYMLINK_RESOLUTION_SPELLINGS:
            assert spelling not in source, (
                f"{relative} resolves a pointer symlink itself ({spelling}) instead of calling "
                "scaffold_artifact_lib; that is the second owner this consolidation removed"
            )


def test_every_module_naming_a_write_target_routes_through_the_owner_for_the_facts() -> None:
    """Structural half of "every payload says what writing would destroy".

    Behavioural coverage below can only reach producers a test can seed. This reaches all of
    them, and fails when a NEW producer is added without the facts — the regression the
    hand-maintained list could not see.
    """
    for relative, source in _modules_naming_a_write_target().items():
        if relative == _OWNER_REL:
            continue
        assert any(route in source for route in _FACT_ROUTES), (
            f"{relative} names a write_artifact_path but never routes through "
            f"scaffold_artifact_lib for the write-target facts; one of {_FACT_ROUTES} is "
            "how a payload says whether writing there destroys content"
        )


def test_the_owner_stays_importable_with_no_package_context() -> None:
    """`scaffold_ideation_artifact.py` loads the owner by file path with no package context.

    So the owner must import only the standard library. This was stated in a docstring as
    load-bearing and guarded by nothing, which is the shape this goal is about.
    """
    source = (ROOT / "scripts/core/scaffold_artifact_lib.py").read_text(encoding="utf-8")
    # `import scripts.x` is the most natural second spelling of the exact failure mode this
    # guards, and the first version of the list missed it.
    forbidden = (
        "from runtime_bootstrap",
        "import runtime_bootstrap",
        "import_repo_module",
        "from scripts.",
        "import scripts.",
        "spec_from_file_location",
    )
    for token in forbidden:
        assert token not in source, (
            f"scaffold_artifact_lib.py now imports repo machinery ({token}); the ideation "
            "scaffold loads it with spec_from_file_location and would fail"
        )


def test_every_scaffold_payload_says_what_writing_would_destroy(tmp_path: Path) -> None:
    """Behavioural guard with teeth, across every producer that names a write target.

    The earlier version of this compared the layout inventory against the owner, which was a
    tautology once the inventory became a one-line delegation to it. This runs the real
    producers instead, and each one must carry both facts.
    """
    for producer, payload in _producer_payloads(tmp_path).items():
        assert "write_artifact_target_exists" in payload, f"{producer} omits the existence fact"
        assert "write_artifact_effect" in payload, f"{producer} omits the effect fact"
        expected = (
            "overwrite_existing_content"
            if (payload["_repo_root"] / str(payload["write_artifact_path"])).exists()
            else "create_new_file"
        )
        assert payload["write_artifact_effect"] == expected, (
            f"{producer} reports {payload['write_artifact_effect']!r} for a target whose "
            "on-disk state says otherwise"
        )


def test_the_debug_resolved_followup_reports_the_FRESH_target_not_the_old_one(
    tmp_path: Path,
) -> None:
    """The one branch where the effect key was deterministically false.

    `scaffold_debug_artifact.payload_for` builds the current-pointer payload and then swaps in
    a fresh-record target through a FIXED key list. The facts were computed before the swap
    and were not in that list, so this branch reported `overwrite_existing_content` for a path
    the code guarantees does not exist -- while `debug/SKILL.md` told the agent to trust it.
    The fix recomputes from the final value, so a future key cannot go stale the same way.
    """
    repo = tmp_path / "repo"
    _seed_resolved_debug_pointer(repo)

    payload = _scaffold_debug.payload_for(repo, title=None)

    assert payload["write_artifact_role"] == "durable_record"
    assert (repo / str(payload["write_artifact_path"])).exists() is False
    assert payload["write_artifact_target_exists"] is False
    assert payload["write_artifact_effect"] == "create_new_file"


def test_the_pair_of_write_target_facts_says_whether_a_write_destroys_content(
    tmp_path: Path,
) -> None:
    """#548's actual harm: the payload said WHERE, never whether anything was already there."""
    repo = tmp_path / "repo"
    pointer = _seed_pointer(repo, "symlink_to_existing")
    existing = pointer.parent / "2026-01-02-quality-review.md"

    facts = _scaffold_lib.write_target_facts(repo, str(existing.relative_to(repo)))
    assert facts == {
        "write_artifact_target_exists": True,
        "write_artifact_effect": "overwrite_existing_content",
    }

    fresh = _scaffold_lib.write_target_facts(
        repo, "charness-artifacts/quality/2026-01-03-quality-review.md"
    )
    assert fresh == {
        "write_artifact_target_exists": False,
        "write_artifact_effect": "create_new_file",
    }


def test_the_quality_scaffold_payload_admits_it_would_overwrite_a_finished_review(
    tmp_path: Path,
) -> None:
    """The composed verdict, not only the module that computes it.

    This is the exact shape of `#538`: the pointer resolves to a completed dated review, so
    `write_artifact_path` is a destructive target. The payload an agent reads must say so.
    """
    repo = tmp_path / "repo"
    _seed_pointer(repo, "symlink_to_existing")

    payload = _resolve_quality_artifact.payload_for(
        repo, slug="quality review", intent="current", artifact_date=dt.date(2026, 1, 3)
    )

    assert payload["write_artifact_role"] == "current_pointer_target"
    assert (
        payload["write_artifact_path"] == "charness-artifacts/quality/2026-01-02-quality-review.md"
    )
    assert payload["write_artifact_target_exists"] is True
    assert payload["write_artifact_effect"] == "overwrite_existing_content"

    # The record intent is the safe one, and must be distinguishable WITHOUT reading the role.
    record = _resolve_quality_artifact.payload_for(
        repo, slug="quality review", intent="record", artifact_date=dt.date(2026, 1, 3)
    )
    assert record["write_artifact_effect"] == "create_new_file"
    assert record["write_artifact_target_exists"] is False


#: `not a green light` was an anchor here until the producer stopped handing back the previous
#: review's file: the sentence it protected told an agent to distrust the scaffold's own write
#: path, and that instruction became false rather than merely stale. Its replacement anchors
#: the fact an agent must now read instead — `write_artifact_subject_match` — plus the
#: `unknown` state, which is the one that asserts nothing and must not read as a green light.
_EFFECT_PROSE_ANCHORS = {
    "skills/public/quality/SKILL.md": (
        "write_artifact_effect",
        "write_artifact_subject_match",
        "unknown",
        "--intent record",
        # DIRECTIONAL, not presence-only. A bounded round pointed out that dropping
        # `not a green light` left the quality entry with four anchors a compaction could
        # satisfy while flipping the instruction to "trust `write_artifact_path`". These two
        # are the polarity: what is forbidden, and the single state that lifts it.
        "Do NOT",
        "only `match`",
    ),
    "skills/public/debug/SKILL.md": (
        "write_artifact_effect",
        "overwrite_existing_content",
        "create_new_file",
        "not exhaustive",
        "write_artifact_subject_match",
        "refused_write_artifact_path",
    ),
}


def test_the_two_skills_still_explain_how_to_read_the_write_target_facts() -> None:
    """The prose is the ONLY surface telling an agent how to act on the two new keys.

    A bounded round pointed out that nothing failed if it disappeared — and that this same
    prose had been rewritten three times and been wrong twice. So the surface with the worst
    track record in the slice was also its least guarded. This does not check that the prose is
    CORRECT (a reviewer judges that); it fails if the explanation is deleted, or if it stops
    naming the hedge and the safe alternative that make it correct.
    """
    for relative, anchors in _EFFECT_PROSE_ANCHORS.items():
        text = " ".join((ROOT / relative).read_text(encoding="utf-8").split())
        for anchor in anchors:
            assert anchor in text, (
                f"{relative} no longer explains {anchor!r}; the write-target facts would be "
                "emitted with no surface telling an agent what to do with them"
            )


def test_the_owner_refuses_to_start_without_the_layout_resolver(tmp_path: Path) -> None:
    """The one path the owner hard-codes must miss loudly, never fall back to a search."""
    import runpy

    owner = runpy.run_path(str(ROOT / "scripts/core/scaffold_artifact_lib.py"))
    with pytest.raises(ImportError, match="scripts/core/repo_layout.py not found"):
        owner["_load_repo_layout"](tmp_path / "nowhere" / "owner.py")
