from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DECISION_VALUES = ("unreviewed", "approve", "request_changes", "comment_only", "defer")
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


def first_string(*values: object, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


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
        item_id = first_string(raw_item.get("id"), raw_item.get("card_id"), default=f"item-{index}")
        if item_id in seen_ids:
            raise ReportModeError(f"report packet contains duplicate item id `{item_id}`")
        seen_ids.add(item_id)
        items.append(
            {
                "id": item_id,
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


def normalize_review_input(review_input: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if review_input is None:
        return {}
    raw_items = review_input.get("items")
    if isinstance(raw_items, dict):
        iterable = [dict(value, id=item_id) for item_id, value in raw_items.items() if isinstance(value, dict)]
    elif isinstance(raw_items, list):
        iterable = raw_items
    elif isinstance(review_input.get("decisions"), dict):
        iterable = [
            dict(value, id=item_id)
            for item_id, value in review_input["decisions"].items()
            if isinstance(value, dict)
        ]
    else:
        iterable = []
    normalized: dict[str, dict[str, str]] = {}
    for item in iterable:
        if not isinstance(item, dict):
            continue
        item_id = first_string(item.get("id"))
        decision = first_string(item.get("decision"), default="unreviewed")
        if item_id and decision not in DECISION_VALUES:
            raise ReportModeError(f"review input item `{item_id}` has unsupported decision `{decision}`")
        if item_id:
            normalized[item_id] = {"decision": decision, "comment": first_string(item.get("comment"), item.get("notes"))}
    return normalized


def build_decisions(packet: dict[str, Any], items: list[dict[str, Any]], review_input: dict[str, dict[str, str]]) -> dict[str, Any]:
    reviewed_items: list[dict[str, Any]] = []
    dropped_ids: list[str] = []
    for item in items:
        submitted = review_input.get(item["id"], {})
        decision = submitted.get("decision", "unreviewed")
        comment = submitted.get("comment", "")
        if decision == "unreviewed" and not comment:
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
            }
        )
    return {
        "schema_version": 1,
        "source_packet_id": first_string(packet.get("id"), packet.get("session_id")),
        "generated_at": utc_now(),
        "items": reviewed_items,
        "dropped_unreviewed_item_ids": dropped_ids,
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


def render_html(packet: dict[str, Any], items: list[dict[str, Any]], decisions_path: str) -> str:
    title = html.escape(first_string(packet.get("title"), packet.get("name"), default="HITL Decision Queue"))
    summary = html.escape(first_string(packet.get("summary"), packet.get("intro")))
    next_step = html.escape(first_string(packet.get("agent_next_step"), packet.get("next_agent_step")))
    cards = "\n".join(render_card(item, index) for index, item in enumerate(items, start=1))
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
    decisions = build_decisions(packet, items, normalize_review_input(review_input))
    html_path.parent.mkdir(parents=True, exist_ok=True)
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(packet, items, decisions_path.name), encoding="utf-8")
    decisions_path.write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "html_path": repo_relative(html_path, repo_root),
        "decisions_path": repo_relative(decisions_path, repo_root),
        "item_count": len(items),
        "reviewed_item_count": len(decisions["items"]),
        "dropped_unreviewed_count": len(decisions["dropped_unreviewed_item_ids"]),
    }
