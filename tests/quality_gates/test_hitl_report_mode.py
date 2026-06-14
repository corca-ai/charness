from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _assert_no_repo_absolute_path(payload: object, repo: Path) -> None:
    rendered = json.dumps(payload, ensure_ascii=False)
    assert str(repo.resolve()) not in rendered


def test_hitl_report_mode_does_not_turn_suggestions_into_default_approval(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "cautilus-review",
                "title": "Cautilus Review",
                "agent_next_step": "Apply only explicit human decisions.",
                "items": [
                    {
                        "id": "claim-1",
                        "question": "Should the claim be accepted?",
                        "why": "The next agent may otherwise treat a recommendation as approval.",
                        "suggested_decision": "approve",
                        "evidence_links": [{"label": "Report", "path": "report.md"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(packet))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert payload["reviewed_item_count"] == 0
    assert decisions["items"] == []
    assert decisions["dropped_unreviewed_item_ids"] == ["claim-1"]
    assert 'value="unreviewed" checked' in html
    assert "Suggested action" in html
    assert "Apply only explicit human decisions." in html
    assert "Report" in html
    assert "Defaults stay unreviewed" in html
    _assert_no_repo_absolute_path(payload, repo)
    _assert_no_repo_absolute_path(decisions, repo)


def test_hitl_report_mode_saves_only_touched_decisions_and_explains_tables(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    review = repo / "review.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "table-review",
                "title": "Table Review",
                "items": [
                    {
                        "id": "matrix-1",
                        "question": "Which row needs follow-up?",
                        "why": "The reviewer should not have to decode the table unaided.",
                        "suggested_decision": "approve",
                        "table": [
                            {"Claim": "routing", "Status": "weak", "Reason": "missing evidence"},
                            {"Claim": "storage", "Status": "ok", "Reason": "artifact linked"},
                        ],
                    },
                    {
                        "id": "matrix-2",
                        "question": "Should this stay deferred?",
                        "why": "Untouched items should not become approvals.",
                        "suggested_decision": "approve",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    review.write_text(
        json.dumps({"items": [{"id": "matrix-1", "decision": "request_changes", "comment": "Fix routing."}]}),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(packet),
        "--review-input",
        str(review),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert [item["id"] for item in decisions["items"]] == ["matrix-1"]
    assert decisions["items"][0]["decision"] == "request_changes"
    assert decisions["items"][0]["suggested_decision"] == "approve"
    assert decisions["items"][0]["suggestion_display_only"] is True
    assert decisions["items"][0]["table_rows"] == [
        {"Claim": "routing", "Status": "weak", "Reason": "missing evidence"},
        {"Claim": "storage", "Status": "ok", "Reason": "artifact linked"},
    ]
    assert decisions["dropped_unreviewed_item_ids"] == ["matrix-2"]
    assert "Claim: routing; Status: weak; Reason: missing evidence" in html
    assert "<summary>Raw table</summary>" in html
    _assert_no_repo_absolute_path(payload, repo)
    _assert_no_repo_absolute_path(decisions, repo)


def test_hitl_report_mode_orders_adaptive_queue_by_decision_leverage(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-order",
                "adaptive_queue": True,
                "items": [
                    {
                        "id": "a",
                        "question": "Review A?",
                        "source_order": 1,
                        "priority": {"leverage": "low", "context_cost": "low", "reason": "Later tie item."},
                    },
                    {
                        "id": "b",
                        "question": "Review B?",
                        "source_order": 2,
                        "blocks": ["c"],
                        "priority": {"leverage": "high", "risk": "high", "rule_seed": True},
                        "why_next": "Sets the rule for later cards.",
                    },
                    {
                        "id": "c",
                        "question": "Review C?",
                        "source_order": 3,
                        "priority": {"leverage": "medium"},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(packet))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert payload["current_queue_order"] == ["b", "c", "a"]
    assert decisions["queue_state"]["current_queue_order"] == ["b", "c", "a"]
    assert "Sets the rule for later cards." in html
    assert html.index('data-item-id="b"') < html.index('data-item-id="c"') < html.index('data-item-id="a"')


def test_hitl_report_mode_reprioritizes_remaining_items_from_review_effects(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    review = repo / "review.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-review",
                "adaptive_queue": True,
                "items": [
                    {
                        "id": "a",
                        "question": "Review A?",
                        "source_order": 1,
                        "tags": ["docs"],
                        "priority": {"leverage": "medium"},
                    },
                    {
                        "id": "b",
                        "question": "Review B?",
                        "source_order": 2,
                        "tags": ["routing"],
                        "priority": {"leverage": "high", "rule_seed": True},
                    },
                    {
                        "id": "c",
                        "question": "Review C?",
                        "source_order": 3,
                        "tags": ["routing"],
                        "priority": {"leverage": "low"},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    review.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "b",
                        "decision": "request_changes",
                        "comment": "Routing claims need direct evidence.",
                        "queue_effects": [{"type": "boost_tag", "tag": "routing"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(packet),
        "--review-input",
        str(review),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert payload["current_queue_order"] == ["c", "a"]
    assert payload["review_queue_item_count"] == 2
    assert [item["id"] for item in decisions["items"]] == ["b"]
    assert decisions["items"][0]["queue_effects"][0]["type"] == "boost_tag"
    assert decisions["dropped_unreviewed_item_ids"] == ["a", "c"]
    assert 'data-item-id="b"' not in html
    assert html.index('data-item-id="c"') < html.index('data-item-id="a"')


def test_hitl_report_mode_restart_recommendation_stays_display_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    review = repo / "review.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-restart",
                "adaptive_queue": True,
                "items": [
                    {
                        "id": "rule",
                        "question": "Does this rule invalidate the queue?",
                        "source_order": 1,
                        "priority": {"leverage": "high", "rule_seed": True},
                    },
                    {"id": "old-a", "question": "Review old A?", "source_order": 2},
                    {"id": "old-b", "question": "Review old B?", "source_order": 3},
                ],
            }
        ),
        encoding="utf-8",
    )
    review.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "rule",
                        "decision": "request_changes",
                        "comment": "The implementation should change before these cards are meaningful.",
                        "queue_effects": [
                            {
                                "type": "recommend_restart",
                                "superseded_item_ids": ["old-a", "old-b"],
                                "reason": "Accepted feedback invalidates the remaining old implementation review.",
                                "recommended_next_step": "Apply the fix, then restart HITL.",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(packet),
        "--review-input",
        str(review),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    decisions = json.loads((repo / payload["decisions_path"]).read_text(encoding="utf-8"))
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert payload["queue_status"] == "invalidation_recommended"
    assert payload["current_queue_order"] == []
    assert decisions["queue_state"]["queue_recommendation"]["suggestion_display_only"] is True
    assert decisions["queue_state"]["queue_recommendation"]["requires_human_queue_decision"] is True
    assert decisions["superseded_unreviewed_item_ids"] == ["old-a", "old-b"]
    assert decisions["dropped_unreviewed_item_ids"] == []
    assert [item["id"] for item in decisions["items"]] == ["rule"]
    assert "Restart recommendation" in html
    assert "Apply the fix, then restart HITL." in html


def test_hitl_report_mode_rejects_adaptive_items_without_stable_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-missing-id",
                "adaptive_queue": True,
                "items": [{"question": "Missing ID?", "priority": {"leverage": "high"}}],
            }
        ),
        encoding="utf-8",
    )

    result = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(packet))

    assert result.returncode == 1
    assert "stable explicit `id`" in result.stderr


def test_hitl_report_mode_rejects_blank_adaptive_item_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-blank-id",
                "adaptive_queue": True,
                "items": [{"id": "   ", "question": "Blank ID?", "priority": {"leverage": "high"}}],
            }
        ),
        encoding="utf-8",
    )

    result = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(packet))

    assert result.returncode == 1
    assert "stable explicit `id`" in result.stderr


def test_hitl_report_mode_rejects_stale_review_input_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    review = repo / "review.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-stale-review",
                "adaptive_queue": True,
                "items": [{"id": "current", "question": "Current item?"}],
            }
        ),
        encoding="utf-8",
    )
    review.write_text(json.dumps({"items": [{"id": "old", "decision": "approve"}]}), encoding="utf-8")

    result = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(packet),
        "--review-input",
        str(review),
    )

    assert result.returncode == 1
    assert "unknown item id(s): old" in result.stderr


def test_hitl_report_mode_rejects_queue_effects_without_human_judgment(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    review = repo / "review.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "adaptive-effect-only",
                "adaptive_queue": True,
                "items": [{"id": "current", "question": "Current item?", "tags": ["routing"]}],
            }
        ),
        encoding="utf-8",
    )
    review.write_text(
        json.dumps(
            {"items": [{"id": "current", "queue_effects": [{"type": "boost_tag", "tag": "routing"}]}]}
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(packet),
        "--review-input",
        str(review),
    )

    assert result.returncode == 1
    assert "must include an explicit decision or comment" in result.stderr


def test_hitl_report_mode_rejects_duplicate_ids_and_sanitizes_report_html(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    duplicate_packet = repo / "duplicate.json"
    unsafe_packet = repo / "unsafe.json"
    duplicate_packet.write_text(
        json.dumps({"items": [{"id": "same", "question": "One"}, {"id": "same", "question": "Two"}]}),
        encoding="utf-8",
    )
    unsafe_packet.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "x</script><script>alert(1)</script>",
                        "question": "Is this safe?",
                        "evidence_links": [{"label": "Bad", "href": "javascript:alert(1)"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    duplicate = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(duplicate_packet),
    )
    unsafe = run_script(
        "skills/public/hitl/scripts/render_report.py",
        "--repo-root",
        str(repo),
        "--input",
        str(unsafe_packet),
    )

    assert duplicate.returncode == 1
    assert "duplicate item id" in duplicate.stderr
    assert unsafe.returncode == 0, unsafe.stderr
    payload = json.loads(unsafe.stdout)
    html = (repo / payload["html_path"]).read_text(encoding="utf-8")
    assert 'href="javascript:' not in html
    assert "querySelectorAll(\".card\")" in html
    assert "x&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html


# --- #361: kill the surviving render_report.py main() mutants ------------------


def test_render_report_output_uses_two_space_indent(tmp_path: Path) -> None:
    # #361: the rendered queue JSON is printed with 2-space indent. Kills
    # render_report.py:49 NumberReplacer on `indent=2` (every other assertion does
    # json.loads on stdout, which is indent-agnostic).
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "session_id": "s",
                "title": "T",
                "agent_next_step": "Apply only explicit human decisions.",
                "items": [
                    {
                        "id": "claim-1",
                        "question": "q?",
                        "why": "w",
                        "suggested_decision": "approve",
                        "evidence_links": [{"label": "R", "path": "r.md"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo), "--input", str(packet))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert result.stdout.rstrip("\n") == json.dumps(payload, ensure_ascii=False, indent=2)
    assert '\n  "' in result.stdout  # a top-level key indented by exactly two spaces


def test_render_report_requires_repo_root_and_input(tmp_path: Path) -> None:
    # #361: `--repo-root` and `--input` are required. Kills render_report.py:30 and :31
    # ReplaceTrueWithFalse on `required=True` — argparse exits 2 when either is omitted
    # (the mutant would let a None path through to an uncaught crash, returncode 1).
    repo = tmp_path / "repo"
    repo.mkdir()
    packet = repo / "packet.json"
    packet.write_text(json.dumps({"session_id": "s", "title": "T", "items": []}), encoding="utf-8")
    missing_repo_root = run_script("skills/public/hitl/scripts/render_report.py", "--input", str(packet))
    assert missing_repo_root.returncode == 2
    missing_input = run_script("skills/public/hitl/scripts/render_report.py", "--repo-root", str(repo))
    assert missing_input.returncode == 2
