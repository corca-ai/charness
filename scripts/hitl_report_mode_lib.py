from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from scripts.hitl_adaptive_queue_lib import (
    first_int,
    first_string,
    item_uses_adaptive_metadata,
    normalize_priority,
    normalize_review_input,
    order_items,
    source_order_queue_state,
    string_list,
    uses_adaptive_rendering,
    validate_review_input_ids,
)

TABLE_ROW_LIMIT = 4


class ReportModeError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReportModeError(f"{label} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReportModeError(f"{label} is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ReportModeError(f"{label} must be a JSON object: {path}")
    return data


def portable_path(repo_root: Path, value: str) -> str:
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return value


def safe_href(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme and parsed.scheme not in {"file", "http", "https"}:
        return ""
    return value


def normalize_evidence(repo_root: Path, raw: object) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        return []
    links: list[dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        if isinstance(item, str):
            href = safe_href(portable_path(repo_root, item))
            links.append({"label": href or f"Evidence {index}", "href": href})
            continue
        if not isinstance(item, dict):
            continue
        href_value = item.get("href") or item.get("path") or item.get("url")
        if not isinstance(href_value, str) or not href_value.strip():
            continue
        href = safe_href(portable_path(repo_root, href_value.strip()))
        label = str(item.get("label") or item.get("title") or href_value)
        links.append({"label": label, "href": href})
    return links


def normalize_table(raw: object) -> list[dict[str, str]]:
    raw_rows = raw.get("rows") if isinstance(raw, dict) else raw
    if not isinstance(raw_rows, list):
        return []
    rows: list[dict[str, str]] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            continue
        row = {key.strip(): "" if value is None else str(value) for key, value in raw_row.items() if key.strip()}
        if row:
            rows.append(row)
    return rows


def explain_table(rows: list[dict[str, str]]) -> str:
    summaries: list[str] = []
    for row in rows[:TABLE_ROW_LIMIT]:
        cells = [f"{key}: {value}" for key, value in row.items() if value]
        if cells:
            summaries.append("; ".join(cells))
    remaining = len(rows) - len(summaries)
    suffix = f" Plus {remaining} more row(s)." if remaining > 0 else ""
    return " ".join(summaries) + suffix


def normalize_items(repo_root: Path, packet: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = packet.get("items")
    if not isinstance(raw_items, list):
        raise ReportModeError("report packet must contain an `items` list")
    packet_next_step = first_string(packet.get("agent_next_step"), packet.get("next_agent_step"))
    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            raise ReportModeError(f"items[{index - 1}] must be an object")
        table_rows = normalize_table(raw_item.get("table") or raw_item.get("evidence_table"))
        explicit_item_id = first_string(raw_item.get("id"), raw_item.get("card_id"))
        has_explicit_id = bool(explicit_item_id)
        item_id = first_string(explicit_item_id, default=f"item-{index}")
        if item_uses_adaptive_metadata(raw_item, packet) and not has_explicit_id:
            raise ReportModeError("adaptive report items must declare stable explicit `id` values")
        if item_id in seen_ids:
            raise ReportModeError(f"report packet contains duplicate item id `{item_id}`")
        seen_ids.add(item_id)
        priority = normalize_priority(raw_item.get("priority"))
        items.append(
            {
                "id": item_id,
                "adaptive": item_uses_adaptive_metadata(raw_item, packet),
                "source_order": first_int(raw_item.get("source_order"), default=index),
                "depends_on": string_list(raw_item.get("depends_on") or priority.get("depends_on")),
                "blocks": string_list(raw_item.get("blocks") or priority.get("blocks")),
                "tags": string_list(raw_item.get("tags")),
                "priority": priority,
                "why_next": first_string(
                    raw_item.get("why_next"),
                    raw_item.get("score_explanation"),
                    priority.get("reason"),
                ),
                "question": first_string(
                    raw_item.get("question"),
                    raw_item.get("review_question"),
                    raw_item.get("title"),
                    default=f"Review item {index}",
                ),
                "why": first_string(raw_item.get("why"), raw_item.get("why_it_matters")),
                "explanation": first_string(
                    raw_item.get("explanation"),
                    raw_item.get("plain_language_summary"),
                    raw_item.get("summary"),
                    default=explain_table(table_rows),
                ),
                "agent_next_step": first_string(
                    raw_item.get("agent_next_step"),
                    raw_item.get("next_agent_step"),
                    default=packet_next_step,
                ),
                "suggested_decision": first_string(
                    raw_item.get("suggested_decision"),
                    raw_item.get("recommended_decision"),
                    raw_item.get("suggested_action"),
                ),
                "evidence_links": normalize_evidence(repo_root, raw_item.get("evidence_links") or raw_item.get("evidence")),
                "table_rows": table_rows,
            }
        )
    return items


def build_decisions(
    packet: dict[str, Any],
    items: list[dict[str, Any]],
    review_input: dict[str, dict[str, Any]],
    queue_state: dict[str, Any],
) -> dict[str, Any]:
    reviewed_items: list[dict[str, Any]] = []
    dropped_ids: list[str] = []
    superseded_ids = set(queue_state["superseded_unreviewed_item_ids"])
    for item in items:
        submitted = review_input.get(item["id"], {})
        decision = submitted.get("decision", "unreviewed")
        comment = submitted.get("comment", "")
        queue_effects = submitted.get("queue_effects", [])
        if item["id"] in superseded_ids:
            continue
        if decision == "unreviewed" and not comment and not queue_effects:
            dropped_ids.append(item["id"])
            continue
        reviewed_items.append(
            {
                "id": item["id"],
                "decision": decision,
                "comment": comment,
                "question": item["question"],
                "explanation": item["explanation"],
                "agent_next_step": item["agent_next_step"],
                "evidence_links": item["evidence_links"],
                "table_rows": item["table_rows"],
                "suggested_decision": item["suggested_decision"],
                "suggestion_display_only": True,
                "queue_effects": queue_effects,
            }
        )
    return {
        "schema_version": 2,
        "source_packet_id": first_string(packet.get("id"), packet.get("session_id")),
        "generated_at": utc_now(),
        "items": reviewed_items,
        "dropped_unreviewed_item_ids": dropped_ids,
        "superseded_unreviewed_item_ids": queue_state["superseded_unreviewed_item_ids"],
        "queue_state": queue_state,
    }


def render_link(link: dict[str, str]) -> str:
    if not link["href"]:
        return f"<li><span>{html.escape(link['label'])}</span></li>"
    return f'<li><a href="{html.escape(link["href"], quote=True)}">{html.escape(link["label"])}</a></li>'


def render_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return ""
    headers = list(dict.fromkeys(key for row in rows for key in row))
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body = []
    for row in rows:
        body.append("".join(f"<td>{html.escape(row.get(header, ''))}</td>" for header in headers))
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(f'<tr>{row}</tr>' for row in body)}</tbody></table>"


def render_card(item: dict[str, Any], index: int) -> str:
    item_id = html.escape(item["id"], quote=True)
    links = "\n".join(render_link(link) for link in item["evidence_links"]) or "<li>No evidence links supplied.</li>"
    table_html = render_table(item["table_rows"])
    table_details = f"<details><summary>Raw table</summary>{table_html}</details>" if table_html else ""
    why_next = html.escape(item["why_next"] or "Packet order tie-breaker.")
    radio_rows = [
        ("unreviewed", "Unreviewed"),
        ("approve", "Approve"),
        ("request_changes", "Request changes"),
        ("comment_only", "Comment only"),
        ("defer", "Defer"),
    ]
    radios = "\n".join(
        f'<label><input type="radio" name="decision-{index}" value="{value}"'
        f'{" checked" if value == "unreviewed" else ""}> {label}</label>'
        for value, label in radio_rows
    )
    return f"""
<article class="card" data-item-id="{item_id}">
  <header><span class="item-id">{item_id}</span><h2>{html.escape(item["question"])}</h2></header>
  <p class="why-next"><strong>Why this is next:</strong> {why_next}</p>
  <p class="why">{html.escape(item["why"])}</p>
  <p class="explanation">{html.escape(item["explanation"])}</p>
  <dl>
    <dt>Suggested action</dt><dd>{html.escape(item["suggested_decision"] or "None")}</dd>
    <dt>Agent next step</dt><dd>{html.escape(item["agent_next_step"])}</dd>
  </dl>
  {table_details}
  <details><summary>Evidence</summary><ul>{links}</ul></details>
  <fieldset><legend>Decision</legend>{radios}</fieldset>
  <label class="comment">Comment<textarea name="{item_id}-comment" rows="4"></textarea></label>
</article>"""


def render_queue_recommendation(queue_state: dict[str, Any]) -> str:
    recommendation = queue_state.get("queue_recommendation")
    if not isinstance(recommendation, dict):
        return ""
    superseded = ", ".join(recommendation.get("superseded_item_ids", [])) or "None"
    return f"""
<article class="card queue-recommendation" data-queue-status="invalidation_recommended">
  <header><span class="item-id">queue</span><h2>Restart recommendation</h2></header>
  <p class="why-next"><strong>Decision needed:</strong> Continue this queue, or stop and restart after applying accepted feedback?</p>
  <p>{html.escape(recommendation.get("reason", ""))}</p>
  <dl>
    <dt>Suggested action</dt><dd>{html.escape(recommendation.get("recommended_next_step", ""))}</dd>
    <dt>Superseded</dt><dd>{html.escape(superseded)}</dd>
    <dt>Requires approval</dt><dd>Yes</dd>
  </dl>
</article>"""


def render_html(packet: dict[str, Any], items: list[dict[str, Any]], decisions_path: str, queue_state: dict[str, Any]) -> str:
    title = html.escape(first_string(packet.get("title"), packet.get("name"), default="HITL Decision Queue"))
    summary = html.escape(first_string(packet.get("summary"), packet.get("intro")))
    next_step = html.escape(first_string(packet.get("agent_next_step"), packet.get("next_agent_step")))
    queue_recommendation = render_queue_recommendation(queue_state)
    cards = queue_recommendation + "\n".join(render_card(item, index) for index, item in enumerate(items, start=1))
    output_name = html.escape(Path(decisions_path).name, quote=True)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; line-height: 1.45; }}
body {{ margin: 0; background: #f7f7f4; color: #171717; }}
main {{ max-width: 760px; margin: 0 auto; padding: 20px 14px 96px; }}
h1 {{ font-size: 1.6rem; margin: 0 0 8px; }} .intro {{ margin: 0 0 18px; color: #434343; }}
.card {{ background: #fff; border: 1px solid #d8d8d2; border-radius: 8px; padding: 16px; margin: 0 0 14px; }}
.item-id {{ color: #666; font-size: .85rem; }} h2 {{ font-size: 1.1rem; margin: 4px 0 8px; }}
dl {{ display: grid; grid-template-columns: 120px 1fr; gap: 6px 12px; }} dt {{ font-weight: 650; }} dd {{ margin: 0; }}
fieldset {{ border: 1px solid #d8d8d2; border-radius: 8px; display: grid; gap: 8px; margin: 14px 0; }}
textarea {{ box-sizing: border-box; width: 100%; margin-top: 6px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: .92rem; }}
th, td {{ border: 1px solid #d8d8d2; padding: 6px; text-align: left; vertical-align: top; }} th {{ background: #eeeeea; }}
.save {{ position: fixed; inset: auto 0 0; background: #171717; color: #fff; padding: 12px 14px; }}
.save-inner {{ max-width: 760px; margin: 0 auto; display: flex; align-items: center; gap: 12px; }}
button {{ min-height: 40px; padding: 0 14px; border: 0; border-radius: 6px; font-weight: 650; }} .save small {{ color: #ddd; }}
</style></head><body><main><h1>{title}</h1><p class="intro">{summary}</p><p><strong>Agent next step:</strong> {next_step}</p>{cards}</main>
<footer class="save"><div class="save-inner"><button type="button" id="download">Save review JSON</button>
<small>Defaults stay unreviewed; suggested actions are display-only.</small></div></footer>
<script>
document.getElementById("download").addEventListener("click", () => {{
  const packet = {{items: []}};
  for (const card of document.querySelectorAll(".card")) {{
    const id = card.dataset.itemId || "";
    const decision = card.querySelector('input[type="radio"]:checked')?.value || "unreviewed";
    const comment = card.querySelector("textarea")?.value || "";
    if (decision !== "unreviewed" || comment.trim()) packet.items.push({{id, decision, comment}});
  }}
  const blob = new Blob([JSON.stringify(packet, null, 2) + "\\n"], {{type: "application/json"}});
  const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = "{output_name}";
  link.click(); URL.revokeObjectURL(link.href);
}});
</script></body></html>
"""


def default_output_paths(repo_root: Path, packet: dict[str, Any], runtime_dir: str) -> tuple[Path, Path]:
    session_id = first_string(packet.get("session_id"), packet.get("id"), default="hitl-report")
    safe_session_id = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in session_id)
    output_dir = repo_root / runtime_dir / safe_session_id
    return output_dir / "review.html", output_dir / "review-decisions.json"


def repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def render_report(
    *,
    repo_root: Path,
    input_path: Path,
    output_html: Path | None,
    output_decisions: Path | None,
    review_input_path: Path | None,
    runtime_dir: str = ".charness/hitl/runtime",
) -> dict[str, Any]:
    packet = load_json(input_path, "report packet")
    items = normalize_items(repo_root, packet)
    default_html, default_decisions = default_output_paths(repo_root, packet, runtime_dir)
    html_path = output_html or default_html
    decisions_path = output_decisions or default_decisions
    review_input = load_json(review_input_path, "review input") if review_input_path else None
    normalized_review_input = normalize_review_input(review_input)
    validate_review_input_ids(items, normalized_review_input)
    if uses_adaptive_rendering(packet, items, normalized_review_input):
        ordered_items, queue_state = order_items(items, normalized_review_input)
    else:
        ordered_items = sorted(items, key=lambda item: (item["source_order"], item["id"]))
        queue_state = source_order_queue_state(items, normalized_review_input)
    decisions = build_decisions(packet, items, normalized_review_input, queue_state)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(packet, ordered_items, decisions_path.name, queue_state), encoding="utf-8")
    decisions_path.write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "html_path": repo_relative(html_path, repo_root),
        "decisions_path": repo_relative(decisions_path, repo_root),
        "item_count": len(items),
        "review_queue_item_count": len(ordered_items),
        "reviewed_item_count": len(decisions["items"]),
        "dropped_unreviewed_count": len(decisions["dropped_unreviewed_item_ids"]),
        "queue_status": queue_state["status"],
        "current_queue_order": queue_state["current_queue_order"],
        "superseded_unreviewed_count": len(queue_state["superseded_unreviewed_item_ids"]),
    }
