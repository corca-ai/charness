"""Behavioral pins for degradation and fallback arms that shipped unasserted.

Every test here names a way one of these surfaces is *asked to keep working when
its input is wrong*: a note whose derived block was hand-edited into an
unparseable shape, a helper imported from the flat exported layout instead of the
`scripts` package, a subprocess carrier whose stdout is not YAML, a validator run
against an adapter it must refuse. Those arms are the ones a reader trusts
without ever seeing them run, which is exactly why they need assertions that go
red when the behaviour changes rather than assertions that a line executed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

from tests.dsl import Repo, run_at
from tests.module_eviction import evict_module
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

CLAIMS = load_script_module(
    "coverage_debt_release_notes_claims",
    ROOT / "skills/public/release/scripts/release_notes_claims.py",
)
ROUTE_PUBLIC_FETCH = load_script_module(
    "coverage_debt_route_public_fetch",
    ROOT / "skills/support/web-fetch/scripts/route_public_fetch.py",
)
PREPARE_PACKET = load_script_module(
    "coverage_debt_critique_prepare_packet",
    ROOT / "skills/public/critique/scripts/prepare_packet.py",
)
NORMALIZE_HOST_DOCS = load_script_module(
    "coverage_debt_normalize_host_docs", ROOT / "skills/public/setup/scripts/normalize_host_docs.py"
)
BUILD_RETRO_INDEX = load_script_module(
    "coverage_debt_build_retro_lesson_selection_index",
    ROOT / "scripts/lessons/build_retro_lesson_selection_index.py",
)


# --- release_notes_claims: what a hand-edited derived block is reported as -----

SURFACE: dict[str, object] = {
    "id": "demo-surface",
    "question": "How many demo scripts declare a JSON flag?",
    "count": 2,
    "items": ["scripts/one.py", "scripts/two.py"],
    "scanned": 3,
    "unscanned": [],
}


def _notes(*bodies: str) -> str:
    """A release note carrying ``bodies`` inside one well-formed derived block."""
    joined = "\n\n".join(bodies)
    return f"# Notes\n\n{CLAIMS.BLOCK_BEGIN}\n\n{joined}\n\n{CLAIMS.BLOCK_END}\n"


def _findings(
    text: str, surfaces: list[dict[str, object]] | None = None
) -> list[dict[str, object]]:
    return CLAIMS.audit_notes_text(text, [SURFACE] if surfaces is None else surfaces)


def test_an_end_marker_before_the_begin_marker_is_named_as_malformed() -> None:
    """A note whose two block markers are inverted must be reported as malformed.

    Both markers are present exactly once, so the count checks pass and the code
    reaches a slice whose end index precedes its start. Without this arm the
    reader gets an empty slice — i.e. "every surface is missing" — which sends the
    operator regenerating surfaces instead of fixing the one swapped comment.
    """
    text = f"# Notes\n\n{CLAIMS.BLOCK_END}\n\nbody\n\n{CLAIMS.BLOCK_BEGIN}\n"

    body, findings = CLAIMS.extract_block_body(text)

    assert body is None
    assert [(f["kind"], f["direction"]) for f in findings] == [
        ("malformed-derived-block", "unresolvable")
    ]
    assert "appears before" in findings[0]["detail"]


def test_a_surface_the_tree_does_not_derive_is_reported_as_an_over_claim() -> None:
    """A block describing a surface nothing derives is an over-claim, not noise.

    A renamed or invented surface is a claim the tree cannot support, and the
    release contract acts on the over-claim direction specifically. Reporting it
    as `unresolvable` would drop it out of the count the publish gate reads.
    """
    text = _notes(
        CLAIMS.render_surface_chunk(SURFACE),
        CLAIMS.render_surface_chunk({**SURFACE, "id": "ghost-surface"}),
    )

    findings = _findings(text)

    unknown = [f for f in findings if f["kind"] == "surface-unknown"]
    assert [(f["surface"], f["direction"]) for f in unknown] == [("ghost-surface", "over-claim")]
    assert "nothing in this tree derives" in unknown[0]["detail"]


def test_a_chunk_disagreeing_only_in_prose_is_a_contradiction_not_a_claim_direction() -> None:
    """Same count, same items, different question text: neither over nor under.

    Direction is a statement about how many things the note claims. A hand-edited
    `question:` changes no quantity, so calling it `over-claim` would inflate the
    number the release contract singles out with an edit that claims nothing.
    """
    edited = CLAIMS.render_surface_chunk(SURFACE).replace(
        "How many demo scripts declare a JSON flag?", "How many demo scripts were rewritten?"
    )

    findings = _findings(_notes(edited))

    assert [(f["kind"], f["direction"]) for f in findings] == [
        ("surface-disagrees", "contradiction")
    ]


def test_a_chunk_whose_count_is_unreadable_is_a_contradiction_not_a_direction() -> None:
    """`count: twelve` yields no comparable number, so no direction can be claimed.

    Guessing a direction from an unparseable count would report a fabricated
    over- or under-claim; the honest answer is that the note and the tree cannot
    be compared at all.
    """
    edited = CLAIMS.render_surface_chunk(SURFACE).replace("count: 2", "count: twelve")

    findings = _findings(_notes(edited))

    assert [(f["kind"], f["direction"]) for f in findings] == [
        ("surface-disagrees", "contradiction")
    ]
    assert CLAIMS._count_in_chunk(edited) is None


def test_a_chunk_rendered_as_one_json_line_is_still_compared_by_count_and_items() -> None:
    """A JSON-bodied chunk must still yield its count and items, not read as empty.

    The block is generated as YAML today, but a chunk that arrived as a single
    JSON object (an older or foreign renderer) has to be READ, or every such note
    silently reports count `None` and lands in the undirected `contradiction`
    bucket while actually over-claiming.
    """
    mark = f"<!-- claim-surface: {SURFACE['id']} -->"
    payload = {**SURFACE, "count": 5, "items": ["scripts/one.py", "scripts/ghost.py"]}
    chunk = mark + "\n" + json.dumps(payload)

    assert CLAIMS._count_in_chunk(chunk) == 5
    assert CLAIMS._chunk_items(chunk) == ["scripts/one.py", "scripts/ghost.py"]

    findings = _findings(_notes(chunk))

    assert [(f["kind"], f["direction"]) for f in findings] == [("surface-disagrees", "over-claim")]


def test_a_json_chunk_whose_items_are_not_a_list_reads_as_no_items() -> None:
    """A JSON body with a non-list `items` must degrade to "no items known".

    `_chunk_items` feeds a set difference. Returning the raw scalar would raise
    inside the audit and take down the whole publish gate over one malformed
    chunk instead of reporting that chunk.
    """
    mark = f"<!-- claim-surface: {SURFACE['id']} -->"
    chunk = mark + "\n" + json.dumps({**SURFACE, "items": "scripts/one.py"})

    assert CLAIMS._chunk_items(chunk) == []
    # Count still agrees and no item can be shown to be extra, so the audit says
    # the chunk disagrees without inventing a claim direction.
    assert [(f["kind"], f["direction"]) for f in _findings(_notes(chunk))] == [
        ("surface-disagrees", "contradiction")
    ]


def test_an_unparseable_json_chunk_body_yields_no_count_and_no_items() -> None:
    """A brace-wrapped line that is not JSON must not be parsed optimistically.

    Half-parsing a corrupted body is how a note gets credited with a count it
    never carried; the reader must fall back to "unknown" and let the audit
    report a plain disagreement.
    """
    mark = f"<!-- claim-surface: {SURFACE['id']} -->"
    chunk = mark + "\n{ not: json, at: all }"

    assert CLAIMS._chunk_json(chunk) is None
    assert CLAIMS._count_in_chunk(chunk) is None
    assert CLAIMS._chunk_items(chunk) == []
    assert CLAIMS._chunk_json("count: 2\nitems:\n- a\n") is None


def test_a_json_chunk_that_is_not_an_object_is_rejected() -> None:
    """A JSON array line is not a surface payload and must not be read as one."""
    assert CLAIMS._chunk_json('<!-- x -->\n{"a": 1}') == {"a": 1}
    assert CLAIMS._chunk_json("[1, 2]") is None


def test_a_marker_whose_count_is_not_a_number_is_reported_without_a_direction() -> None:
    """`{{claim:s.count=twelve}}` disagrees, but in no measurable direction.

    The marker is the authored digit a reader believes. When it is not a digit at
    all, the audit must still refuse the note while declining to guess whether it
    over- or under-claims.
    """
    block = _notes(CLAIMS.render_surface_chunk(SURFACE))
    text = block + "\nWe found {{claim:demo-surface.count=twelve}} of them.\n"
    marker_line = len(block.splitlines()) + 2

    findings = [f for f in _findings(text) if f["kind"] == "marker-disagrees"]

    assert [(f["direction"], f["line"]) for f in findings] == [("contradiction", marker_line)]
    assert "the tree says `2`" in findings[0]["detail"]


def test_a_zero_padded_marker_count_disagrees_without_claiming_a_direction() -> None:
    """`count=02` over a tree count of 2 differs textually but claims no more.

    Rendering it as an over- or under-claim would put a formatting difference into
    the direction tally the release contract acts on.
    """
    text = (
        _notes(CLAIMS.render_surface_chunk(SURFACE))
        + "\nWe found {{claim:demo-surface.count=02}}.\n"
    )

    findings = [f for f in _findings(text) if f["kind"] == "marker-disagrees"]

    assert [f["direction"] for f in findings] == ["contradiction"]


def test_a_marker_claiming_fewer_than_the_tree_has_is_named_an_under_claim() -> None:
    """The two measurable directions stay distinguishable, in both spellings."""
    under = _notes(CLAIMS.render_surface_chunk(SURFACE)) + "\n{{claim:demo-surface.count=1}}\n"
    over = _notes(CLAIMS.render_surface_chunk(SURFACE)) + "\n{{claim:demo-surface.count=9}}\n"

    assert [f["direction"] for f in _findings(under) if f["kind"] == "marker-disagrees"] == [
        "under-claim"
    ]
    assert [f["direction"] for f in _findings(over) if f["kind"] == "marker-disagrees"] == [
        "over-claim"
    ]


def test_unreadable_notes_are_reported_as_a_finding_rather_than_raising(tmp_path: Path) -> None:
    """A notes path that cannot be read must become a finding, not a traceback.

    The publish gate renders findings; an OSError escaping here would abort the
    run with a stack trace instead of the one line telling the operator which
    path it could not read.
    """
    findings = CLAIMS.audit_notes_file(tmp_path, tmp_path)

    assert [(f["kind"], f["direction"], f["surface"]) for f in findings] == [
        ("notes-unreadable", "unresolvable", None)
    ]
    assert str(tmp_path) in findings[0]["detail"]
    assert CLAIMS.finding_lines(findings)[0].startswith("[unresolvable] notes-unreadable:")


def test_the_claims_module_refuses_to_load_without_its_runtime_bootstrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Relocated outside the tree, the module must say WHICH helper is missing.

    Every public skill script resolves its runtime by walking ancestors for
    `skill_runtime_bootstrap.py`. A copy that lands outside the package (a
    half-finished export, a file copied to a consuming repo) must fail with that
    name rather than with an opaque `NoneType` attribute error.
    """
    stray = tmp_path / "somewhere" / "release_notes_claims.py"
    stray.parent.mkdir(parents=True)
    monkeypatch.setattr(CLAIMS, "__file__", str(stray))

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        CLAIMS._load_skill_runtime_bootstrap()


# --- route_public_fetch: the bounded walk for the shared YAML renderer ---------


def test_the_web_fetch_yaml_renderer_walk_stays_bounded_and_names_what_it_wanted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Outside any charness tree the walk must stop and name the missing helper.

    The bound is the point: an unbounded climb would eventually find a
    `scripts/yaml_output.py` in the CONSUMING repository and execute it. Refusing
    after five ancestors keeps a foreign file from being loaded and tells the
    operator exactly which helper was expected.
    """
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    monkeypatch.setattr(ROUTE_PUBLIC_FETCH, "SCRIPT_DIR", deep)

    with pytest.raises(ImportError, match=r"scripts/yaml_output.py not found within 5 ancestors"):
        ROUTE_PUBLIC_FETCH.load_yaml_output()


def test_a_yaml_renderer_candidate_with_no_loader_ends_the_walk_with_the_named_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When a found candidate yields no import spec, refuse — never dereference it.

    The next statements use `spec.loader`, so a `None` spec would surface as an
    `AttributeError` from deep inside a fetch route. The named ImportError is the
    outcome a caller already knows how to read.
    """
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)

    with pytest.raises(ImportError, match=r"scripts/yaml_output.py not found within 5 ancestors"):
        ROUTE_PUBLIC_FETCH.load_yaml_output()


def test_the_web_fetch_yaml_renderer_loads_from_the_real_tree() -> None:
    """The happy path still resolves, so the refusal tests above pin a real bound."""
    assert callable(ROUTE_PUBLIC_FETCH.load_yaml_output().render_yaml)


# --- closeout_refusal_lib: the flat exported layout has no `scripts` package ---


class _BlockScriptsPackage:
    """A meta-path finder that makes `scripts.*` unimportable, deterministically.

    Filtering `sys.path` is not enough: whether `scripts` is reachable depends on what
    other tests have already imported and on how the runner was invoked, so the same
    test took the try arm in one run and the fallback arm in another. A finder that
    refuses the name outright does not depend on any of that.
    """

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts" or fullname.startswith("scripts."):
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_the_closeout_refusal_lib_still_emits_refusals_in_the_flat_layout(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Imported without the `scripts` package, the refusal shape must be unchanged.

    The exported plugin ships these helpers flat, side by side, with no package root --
    so the package-qualified import fails there. If the sibling fallback were broken,
    every refusal in the issue capture/freeze/crosswalk lane would become an
    ImportError at the moment it needed to say no.

    The arm taken is NOT observable from the loaded module: the repo's bootstrap
    aliases `scripts.yaml_output` and `yaml_output` to one module object, so
    `emit_yaml.__module__` reads the same either way. What makes this test pin the
    fallback is the finder below, which guarantees the try arm raises.
    """
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    monkeypatch.setattr(sys, "meta_path", [_BlockScriptsPackage()] + sys.meta_path)
    for name in [
        n for n in list(sys.modules) if n in ("scripts", "yaml_output") or n.startswith("scripts.")
    ]:
        evict_module(monkeypatch, name)

    spec = importlib.util.spec_from_file_location(
        "coverage_debt_flat_closeout_refusal_lib",
        ROOT / "scripts" / "review" / "closeout_refusal_lib.py",
    )
    assert spec is not None and spec.loader is not None
    flat = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flat)

    exit_code = flat.emit_refusal(
        "issue-freeze", flat.RefusalError("stale_freeze", "the freeze is stale")
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert yaml.safe_load(captured.out) == {
        "ok": False,
        "error": "stale_freeze",
        "detail": "the freeze is stale",
    }
    assert "issue-freeze: REFUSED (stale_freeze) the freeze is stale" in captured.err


def test_the_critique_packet_runner_refuses_an_invalid_adapter_before_writing(
    tmp_path: Path,
) -> None:
    """An adapter with a malformed field must stop the run and report the errors.

    The packet is the input a fresh-eye reviewer reads. Building one from a
    partly-parsed adapter would hand the reviewer sections the adapter never
    validly declared, so the runner exits nonzero and writes nothing.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "critique-adapter.yaml").write_text(
        "version: 1\nrepo: rt\npacket_sections: not-a-list\n", encoding="utf-8"
    )

    result = run_loaded_script_main(
        "prepare_packet.py", PREPARE_PACKET, "--repo-root", str(tmp_path), "--slug", "invalid"
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["error"] == "critique adapter invalid"
    assert payload["adapter"]["errors"] == ["packet_sections must be a list"]
    assert not (tmp_path / "charness-artifacts" / "critique").exists()


def test_the_host_doc_normalizer_reports_its_plan_on_stdout_without_writing(tmp_path: Path) -> None:
    """A plan-only run must emit the machine-readable actions and touch nothing.

    The runner is the surface `setup` reads before deciding to execute. A plan
    that printed nothing (or wrote the files anyway) would make the dry run
    useless as a decision input.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_loaded_script_main(
        "normalize_host_docs.py", NORMALIZE_HOST_DOCS, "--repo-root", str(repo)
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "planned"
    assert [action["action"] for action in payload["actions"]] == [
        "write_agents",
        "create_claude_symlink",
    ]
    assert not (repo / "AGENTS.md").exists()
    assert not (repo / "CLAUDE.md").exists()


# --- build_retro_lesson_selection_index: the check and preview verdicts --------

_RETRO_ADAPTER = {
    "version": 1,
    "repo": "demo",
    "language": "en",
    "output_dir": "charness-artifacts/retro",
    "summary_path": "charness-artifacts/retro/recent-lessons.md",
    "evidence_paths": [],
    "metrics_commands": [],
}

_RETRO_ARTIFACT = """# Session Retro
Date: 2026-04-15

## Context

- Context should stay source-linked.

## Waste

- Plugin export was verified too late.

## Next Improvements

- workflow: Validate committed state directly.
"""


def _retro_repo(tmp_path: Path, *, refresh: bool = True) -> Path:
    repo = (
        Repo()
        .adapter("retro", _RETRO_ADAPTER)
        .file("charness-artifacts/retro/2026-04-15-slice.md", _RETRO_ARTIFACT)
        .build(tmp_path)
    )
    if refresh:
        # `--check` compares the index AND the digest it was derived with, so the
        # digest has to exist before a passing check is meaningful.
        run_at(repo, "skills/public/retro/scripts/refresh_recent_lessons.py").ok()
    return repo


def _retro_index(repo: Path, *flags: str):
    return run_loaded_script_main(
        "build_retro_lesson_selection_index.py",
        BUILD_RETRO_INDEX,
        "--repo-root",
        str(repo),
        *flags,
        cli_error_types=(FileNotFoundError, ValueError),
    )


def test_the_retro_index_check_verdict_names_validation_not_a_write(tmp_path: Path) -> None:
    """`--check` must report `validated` over the same population `--write` wrote.

    Both verdicts of this one command were copied from each other, so the risk is
    a check arm that reports the write arm's status — an operator reading
    `written` after a read-only run has been told the index was refreshed when it
    was not.
    """
    repo = _retro_repo(tmp_path)
    write_result = _retro_index(repo, "--write")
    assert write_result.returncode == 0, write_result.stderr

    check_result = _retro_index(repo, "--check")
    assert check_result.returncode == 0, check_result.stderr

    written = yaml.safe_load(write_result.stdout)
    checked = yaml.safe_load(check_result.stdout)
    assert written["status"] == "written"
    assert checked["status"] == "validated"
    assert checked["index_path"] == written["index_path"]
    assert checked["source_artifact_count"] == written["source_artifact_count"] == 1
    assert checked["candidate_count"] == written["candidate_count"]


def test_the_retro_index_check_refuses_when_the_committed_index_drifted(tmp_path: Path) -> None:
    """`--check` must fail once the on-disk index no longer matches the sources.

    Without this, `validated` would be a status the command can print regardless
    of what the file on disk says.
    """
    repo = _retro_repo(tmp_path)
    _retro_index(repo, "--write")
    index_path = repo / yaml.safe_load(_retro_index(repo, "--check").stdout)["index_path"]

    index_path.write_text("candidates: []\n", encoding="utf-8")

    assert _retro_index(repo, "--check").returncode == 1


def test_the_retro_index_preview_emits_the_candidate_payload_without_writing(
    tmp_path: Path,
) -> None:
    """With no flag the command previews the derived payload and writes nothing.

    The preview is what a session reads before deciding to refresh. Emitting the
    write-arm summary instead of the candidates, or writing the index as a side
    effect of a read, would make the default invocation unusable as a preview.
    """
    repo = _retro_repo(tmp_path, refresh=False)
    index_path = repo / "charness-artifacts" / "retro" / "lesson-selection-index.json"

    result = _retro_index(repo)

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["source_artifact_count"] == 1
    assert "candidates" in payload
    assert "status" not in payload
    assert not index_path.exists()
