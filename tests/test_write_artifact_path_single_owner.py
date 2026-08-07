"""`write_artifact_path` means ONE thing, and says whether writing destroys anything.

#548. FOUR modules implemented the same pointer-resolution rule, three of them emitting the
`write_artifact_path` / `write_artifact_role` pair from separate code:

- `scripts/scaffold_artifact_lib.py` (quality, handoff, ideation, retro scaffolds) — now the
  single owner
- `scripts/resolve_artifact_path.py` (debug and the generic path)
- `skills/public/quality/scripts/resolve_quality_artifact.py`
- `scripts/inventory_current_pointer_layouts.py` — the fourth, which the duplicate-ratchet
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

from runtime_bootstrap import import_repo_module
from tests.quality_gates.support import ROOT

_scaffold_lib = import_repo_module(ROOT / "scripts/scaffold_artifact_lib.py", "scripts.scaffold_artifact_lib")
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
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "schema_version: 1\nartifact_class: current_pointer_with_records\ndata:\n  output_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text("# Demo\n\n## Interrupt Decision\n\n- Resolution: resolved\n", encoding="utf-8")
    (debug_dir / "latest.md").symlink_to(target.name)
    return target


def _producer_payloads(tmp_path: Path) -> dict[str, dict[str, object]]:
    """Every producer that names a write target, each in its own seeded repo."""
    payloads: dict[str, dict[str, object]] = {}

    quality_repo = tmp_path / "quality"
    _seed_pointer(quality_repo, "symlink_to_existing")
    (quality_repo / ".agents").mkdir(parents=True, exist_ok=True)
    (quality_repo / ".agents" / "quality-adapter.yaml").write_text(
        "schema_version: 1\nartifact_class: current_pointer_with_records\ndata:\n  output_dir: charness-artifacts/quality\n",
        encoding="utf-8",
    )
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
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / f"{output}-adapter.yaml").write_text(
            f"schema_version: 1\nartifact_class: records_only\ndata:\n  output_dir: charness-artifacts/{output}\n",
            encoding="utf-8",
        )
        payloads[label] = module.payload_for(repo, title="Probe")
        payloads[label]["_repo_root"] = repo

    return payloads


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
_OWNER_REL = "scripts/scaffold_artifact_lib.py"
# How a module may legitimately obtain the write-target facts: by stamping them, by using the
# owner's shared record shape, or by being the owner.
_FACT_ROUTES = (
    "with_write_target_facts(",
    "dated_record_payload(",
    "write_target_facts(",
    "current_pointer_payload(",
    # A planner may ECHO the scaffold payload's fact rather than recompute it; that is the
    # correct thing for a surface that reports someone else's write target.
    '"write_artifact_effect"',
)


def _modules_naming_a_write_target() -> dict[str, str]:
    """DERIVED FROM THE TREE, never hand-listed.

    The first version of this guard kept a hand-maintained list of producers — which is the
    same defect one level up: a producer added later silently falls outside the list and ships
    green, exactly as the two new keys fell outside `scaffold_debug_artifact`'s hand-maintained
    key list. A bounded round found the list already missing four producers. Globbing means a
    new one cannot be added without this test seeing it.
    """
    found: dict[str, str] = {}
    for root in ("scripts", "skills/public"):
        for path in sorted((ROOT / root).rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            # A PRODUCER emits the key into a payload; a CONSUMER only reads it back out.
            # The distinction matters: `inventory_current_pointer_layouts.py` reports other
            # skills' write targets and owes no facts of its own. Producers are matched by the
            # dict-literal key form, or by passing it to the owner's shared record shape.
            produces = '"write_artifact_path":' in source or "write_artifact_path=write_artifact_path" in source
            if produces:
                found[str(path.relative_to(ROOT))] = source
    assert len(found) >= 8, f"the sweep found suspiciously few producers: {sorted(found)}"
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
    source = (ROOT / "scripts/scaffold_artifact_lib.py").read_text(encoding="utf-8")
    forbidden = ("from runtime_bootstrap", "import runtime_bootstrap", "import_repo_module", "from scripts.")
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


def test_the_debug_resolved_followup_reports_the_FRESH_target_not_the_old_one(tmp_path: Path) -> None:
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


def test_the_pair_of_write_target_facts_says_whether_a_write_destroys_content(tmp_path: Path) -> None:
    """#548's actual harm: the payload said WHERE, never whether anything was already there."""
    repo = tmp_path / "repo"
    pointer = _seed_pointer(repo, "symlink_to_existing")
    existing = pointer.parent / "2026-01-02-quality-review.md"

    facts = _scaffold_lib.write_target_facts(repo, str(existing.relative_to(repo)))
    assert facts == {
        "write_artifact_target_exists": True,
        "write_artifact_effect": "overwrite_existing_content",
    }

    fresh = _scaffold_lib.write_target_facts(repo, "charness-artifacts/quality/2026-01-03-quality-review.md")
    assert fresh == {
        "write_artifact_target_exists": False,
        "write_artifact_effect": "create_new_file",
    }


def test_the_quality_scaffold_payload_admits_it_would_overwrite_a_finished_review(tmp_path: Path) -> None:
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
    assert payload["write_artifact_path"] == "charness-artifacts/quality/2026-01-02-quality-review.md"
    assert payload["write_artifact_target_exists"] is True
    assert payload["write_artifact_effect"] == "overwrite_existing_content"

    # The record intent is the safe one, and must be distinguishable WITHOUT reading the role.
    record = _resolve_quality_artifact.payload_for(
        repo, slug="quality review", intent="record", artifact_date=dt.date(2026, 1, 3)
    )
    assert record["write_artifact_effect"] == "create_new_file"
    assert record["write_artifact_target_exists"] is False
