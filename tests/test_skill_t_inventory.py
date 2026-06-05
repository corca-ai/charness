from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.skill_t_inventory_lib import (
    TIER_C_AWAITING,
    TIER_C_POPULATED,
    build_inventory,
    list_public_skill_ids,
    render_inventory_markdown,
    write_inventory,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _make_minimal_repo(tmp_path: Path, skill_ids: list[str]) -> Path:
    repo = tmp_path / "repo"
    public = repo / "skills" / "public"
    public.mkdir(parents=True)
    for skill_id in skill_ids:
        skill_dir = public / skill_id
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill_id}\n---\n# {skill_id}\n",
            encoding="utf-8",
        )
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    return repo


def _seed_retro(repo: Path, *, name: str, body: str) -> None:
    (repo / "charness-artifacts" / "retro" / name).write_text(body, encoding="utf-8")


def _seed_lesson_index(repo: Path, candidates: list[dict]) -> None:
    payload = {
        "schema_version": 1,
        "kind": "retro-lesson-selection-index",
        "candidates": candidates,
    }
    (repo / "charness-artifacts" / "retro" / "lesson-selection-index.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_list_public_skill_ids_skips_dirs_without_skill_md(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    public = repo / "skills" / "public"
    public.mkdir(parents=True)
    (public / "good").mkdir()
    (public / "good" / "SKILL.md").write_text("# good\n", encoding="utf-8")
    (public / "skipme").mkdir()
    (public / "skipme" / "README.md").write_text("# skipme\n", encoding="utf-8")
    assert list_public_skill_ids(repo) == ["good"]


def test_build_inventory_rows_match_public_skills(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    payload = build_inventory(repo)
    assert payload["version"] == 1
    assert payload["kind"] == "skill-t-mechanism-inventory"
    assert payload["tier_c_marker"] == TIER_C_AWAITING
    assert [row["skill_id"] for row in payload["skills"]] == ["alpha", "beta"]
    for row in payload["skills"]:
        assert row["lesson_cite_chain"]["tier"] == "B"
        assert row["lesson_cite_chain"]["retro_artifacts"] == []
        assert row["lifecycle_survival"]["tier"] == "B+"
        assert row["lifecycle_survival"]["max_source_count"] == 0
        assert row["anchor_wiring"]["orthogonal_to_t_tier"] is True
        assert row["anchor_wiring"]["anchors"] == []
        assert row["tier_c_events"]["status"] == TIER_C_AWAITING
        assert row["tier_c_events"]["event_count"] == 0
        assert row["tier_c_events"]["event_types"] == {}


def test_lesson_cite_chain_picks_up_decorated_skill_markers(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    _seed_retro(
        repo,
        name="2026-05-01-alpha-trap.md",
        body="# trap\n\n- The `alpha` skill missed a closeout step.\n",
    )
    _seed_retro(
        repo,
        name="2026-05-02-shared.md",
        body="# shared\n\n- `alpha` and `beta` both hit it.\n",
    )
    payload = build_inventory(repo)
    by_id = {row["skill_id"]: row for row in payload["skills"]}
    assert by_id["alpha"]["lesson_cite_chain"]["retro_artifact_count"] == 2
    assert by_id["beta"]["lesson_cite_chain"]["retro_artifact_count"] == 1


def test_lifecycle_survival_reads_lesson_index(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    _seed_lesson_index(
        repo,
        [
            {
                "lesson": "The `alpha` skill missed a closeout step.",
                "source_count": 3,
                "age_days": 5,
            },
            {
                "lesson": "Unrelated lesson with no markers.",
                "source_count": 7,
                "age_days": 0,
            },
        ],
    )
    payload = build_inventory(repo)
    row = payload["skills"][0]
    assert row["lifecycle_survival"]["matched_lesson_count"] == 1
    assert row["lifecycle_survival"]["max_source_count"] == 3
    assert row["lifecycle_survival"]["freshest_age_days"] == 5


def test_anchor_wiring_picks_up_anchor_names(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    skill_dir = repo / "skills" / "public" / "alpha"
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "lens.md").write_text(
        "Atul Gawande discipline; Barbara Minto structure.\n",
        encoding="utf-8",
    )
    payload = build_inventory(repo)
    anchors = payload["skills"][0]["anchor_wiring"]["anchors"]
    assert "Gawande" in anchors
    assert "Minto" in anchors


def test_tier_c_populated_when_events_reference_skill(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    storage = repo / ".charness" / "t-events"
    storage.mkdir(parents=True)
    (storage / "lesson_cited.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_type": "lesson_cited",
                        "timestamp": "2026-05-09T12:00:00Z",
                        "lesson_path": "charness-artifacts/retro/x.md",
                        "citing_skill": "alpha",
                    }
                ),
                json.dumps(
                    {
                        "event_type": "lesson_cited",
                        "timestamp": "2026-05-09T12:00:01Z",
                        "lesson_path": "charness-artifacts/retro/y.md",
                        "citing_skill": "alpha",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    payload = build_inventory(repo)
    row = payload["skills"][0]
    assert row["tier_c_events"]["status"] == TIER_C_POPULATED
    assert row["tier_c_events"]["event_count"] == 2
    assert row["tier_c_events"]["event_types"] == {"lesson_cited": 2}


def test_tier_c_event_types_keyed_by_row_event_type_not_filename_stem(
    tmp_path: Path,
) -> None:
    """Rotated jsonl files must not pollute the event_types breakdown.

    Rotation produces names like ``lesson_cited.20260509T120000Z.jsonl``.
    The breakdown must group them under the row's ``event_type`` value, not
    the filename stem, so Tier C readers stay stable across rotations.
    """
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    storage = repo / ".charness" / "t-events"
    storage.mkdir(parents=True)
    base = json.dumps(
        {
            "event_type": "lesson_cited",
            "timestamp": "2026-05-09T12:00:00Z",
            "lesson_path": "charness-artifacts/retro/x.md",
            "citing_skill": "alpha",
        }
    )
    (storage / "lesson_cited.jsonl").write_text(base + "\n", encoding="utf-8")
    (storage / "lesson_cited.20260509T120000Z.jsonl").write_text(
        base + "\n", encoding="utf-8"
    )
    payload = build_inventory(repo)
    row = payload["skills"][0]
    assert row["tier_c_events"]["status"] == TIER_C_POPULATED
    assert row["tier_c_events"]["event_count"] == 2
    assert row["tier_c_events"]["event_types"] == {"lesson_cited": 2}


def test_tier_c_remains_awaiting_for_unrelated_skill(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    storage = repo / ".charness" / "t-events"
    storage.mkdir(parents=True)
    (storage / "lesson_cited.jsonl").write_text(
        json.dumps(
            {
                "event_type": "lesson_cited",
                "timestamp": "2026-05-09T12:00:00Z",
                "lesson_path": "charness-artifacts/retro/x.md",
                "citing_skill": "alpha",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    payload = build_inventory(repo)
    by_id = {row["skill_id"]: row for row in payload["skills"]}
    assert by_id["alpha"]["tier_c_events"]["status"] == TIER_C_POPULATED
    assert by_id["beta"]["tier_c_events"]["status"] == TIER_C_AWAITING


def test_write_inventory_is_byte_deterministic(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    out = repo / "out"
    paths_one = write_inventory(repo, out)
    first_json = paths_one["json"].read_text(encoding="utf-8")
    first_md = paths_one["markdown"].read_text(encoding="utf-8")
    paths_two = write_inventory(repo, out)
    assert paths_two["json"].read_text(encoding="utf-8") == first_json
    assert paths_two["markdown"].read_text(encoding="utf-8") == first_md


def test_render_markdown_includes_each_skill_row(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    payload = build_inventory(repo)
    md = render_inventory_markdown(payload)
    for skill_id in ("alpha", "beta"):
        assert f"| `{skill_id}` |" in md
    assert "awaiting events" in md
    assert "tier-c-events (placeholder)" in md


def _run_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate_skill_t_inventory.py"),
            "--repo-root",
            str(repo),
        ],
        capture_output=True,
        text=True,
    )


def test_validator_passes_on_freshly_built_inventory(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    write_inventory(repo)
    result = _run_validator(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["skill_count"] == 2


def test_validator_fails_when_row_missing(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha", "beta"])
    write_inventory(repo)
    inventory_path = repo / "charness-artifacts" / "skill-t-mechanism" / "inventory.json"
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    payload["skills"] = [row for row in payload["skills"] if row["skill_id"] != "beta"]
    inventory_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    result = _run_validator(repo)
    assert result.returncode != 0
    payload_out = json.loads(result.stdout)
    assert payload_out["valid"] is False
    assert any("missing rows" in e for e in payload_out["errors"])


def test_validator_fails_when_tier_c_marker_inconsistent(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    write_inventory(repo)
    inventory_path = repo / "charness-artifacts" / "skill-t-mechanism" / "inventory.json"
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    payload["skills"][0]["tier_c_events"]["event_count"] = 5
    inventory_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    result = _run_validator(repo)
    assert result.returncode != 0
    out = json.loads(result.stdout)
    assert out["valid"] is False
    assert any("awaiting events" in e for e in out["errors"])


def test_validator_fails_when_top_kind_wrong(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    write_inventory(repo)
    inventory_path = repo / "charness-artifacts" / "skill-t-mechanism" / "inventory.json"
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    payload["kind"] = "wrong-kind"
    inventory_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    result = _run_validator(repo)
    assert result.returncode != 0
    out = json.loads(result.stdout)
    assert any("unexpected kind" in e for e in out["errors"])


def test_validator_fails_when_inventory_absent(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path, ["alpha"])
    result = _run_validator(repo)
    assert result.returncode != 0
    out = json.loads(result.stdout)
    assert out["valid"] is False
    assert any("inventory not found" in e for e in out["errors"])
