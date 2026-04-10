#!/usr/bin/env python3
"""Convert a public Notion page to a local Markdown file.

Usage:
    python3 notion-to-md.py <notion_url> [output_path]

Supported URL formats:
    https://workspace.notion.site/Title-{32hex}
    https://www.notion.so/Title-{32hex}
    https://www.notion.so/{32hex}
    32-character hex string (bare page ID)

Requirements: Python 3.7+, no external dependencies.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://www.notion.so/api/v3/loadPageChunk"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 notion-to-md/1.0",
    "Accept": "application/json",
}
HTTP_TIMEOUT = 30
MAX_RETRIES = 3
MAX_CHUNKS = 50


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def parse_notion_url(url: str) -> str:
    """Extract page ID from a Notion URL and return as UUID format."""
    raw = url.strip().rstrip("/")
    raw = urllib.parse.urlparse(raw).path if raw.startswith("http") else raw
    clean = raw.replace("-", "")
    match = re.search(r"([0-9a-f]{32})\s*$", clean, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"Cannot extract page ID from: {url}\n"
            "Supported formats:\n"
            "  https://workspace.notion.site/Title-{32hex}\n"
            "  https://www.notion.so/Title-{32hex}\n"
            "  32-character hex string"
        )

    hex_id = match.group(1).lower()
    return f"{hex_id[:8]}-{hex_id[8:12]}-{hex_id[12:16]}-{hex_id[16:20]}-{hex_id[20:]}"


def _api_request(payload: dict) -> dict:
    """POST to Notion v3 API with retry and timeout."""
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(API_URL, data=data, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503) and attempt < MAX_RETRIES - 1:
                wait = 2**attempt
                eprint(f"  HTTP {error.code}, retrying in {wait}s...")
                time.sleep(wait)
                continue
            if error.code in (401, 403):
                raise RuntimeError(
                    "Page not accessible. Ensure the page is published to the web "
                    "via Share > Publish in Notion."
                ) from error
            raise RuntimeError(f"HTTP error {error.code}: {error.reason}") from error
        except urllib.error.URLError as error:
            if attempt < MAX_RETRIES - 1:
                wait = 2**attempt
                eprint(f"  Network error, retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"Network error: {error.reason}") from error

    raise RuntimeError("Max retries exceeded")


def fetch_page(page_id: str) -> tuple:
    """Fetch all blocks for a page with automatic pagination."""
    eprint("Fetching page...")
    block_map = {}
    cursor = {"stack": []}
    chunk_number = 0

    while chunk_number < MAX_CHUNKS:
        payload = {
            "page": {"id": page_id},
            "limit": 100,
            "cursor": cursor,
            "chunkNumber": chunk_number,
            "verticalColumns": False,
        }
        resp = _api_request(payload)

        blocks = resp.get("recordMap", {}).get("block", {})
        for block_id, block_data in blocks.items():
            value = block_data.get("value")
            if value:
                block_map[block_id] = value

        next_cursor = resp.get("cursor", {})
        if not next_cursor.get("stack"):
            break
        cursor = next_cursor
        chunk_number += 1

    if chunk_number >= MAX_CHUNKS:
        eprint(f"  Warning: reached max {MAX_CHUNKS} chunks, some content may be missing.")

    page_block = block_map.get(page_id, {})
    title_arr = page_block.get("properties", {}).get("title")
    page_title = render_rich_text(title_arr)

    eprint(f"  Fetched {len(block_map)} blocks")
    return block_map, page_title


def render_rich_text(title_array) -> str:
    """Convert Notion rich text array to Markdown inline text."""
    if not title_array:
        return ""

    parts = []
    for segment in title_array:
        if not segment or not isinstance(segment, list):
            continue

        text = segment[0] if segment else ""
        if not isinstance(text, str):
            continue

        formats = segment[1] if len(segment) > 1 else []

        if not formats:
            parts.append(text)
            continue

        is_bold = False
        is_italic = False
        is_code = False
        is_strike = False
        link_url = None

        for fmt in formats:
            if not isinstance(fmt, list) or not fmt:
                continue
            code = fmt[0]
            if code == "b":
                is_bold = True
            elif code == "i":
                is_italic = True
            elif code == "c":
                is_code = True
            elif code == "s":
                is_strike = True
            elif code == "a" and len(fmt) > 1:
                link_url = fmt[1]

        if is_code:
            result = f"`{text}`"
        else:
            result = text
            if is_bold and is_italic:
                result = f"***{result}***"
            elif is_bold:
                result = f"**{result}**"
            elif is_italic:
                result = f"*{result}*"
            if is_strike:
                result = f"~~{result}~~"

        if link_url and link_url.startswith(("http://", "https://")):
            result = f"[{result}]({link_url})"

        parts.append(result)

    return "".join(parts)


def convert_table(table_block: dict, block_map: dict) -> str:
    """Convert a table block and its row children to GFM table."""
    fmt = table_block.get("format", {})
    col_order = fmt.get("table_block_column_order", [])
    has_header = fmt.get("table_block_column_header", False)
    content_ids = table_block.get("content", [])

    if not col_order or not content_ids:
        return ""

    rows = []
    for row_id in content_ids:
        row_block = block_map.get(row_id, {})
        props = row_block.get("properties", {})
        cells = []
        for col_id in col_order:
            cell_val = render_rich_text(props.get(col_id))
            cell_val = cell_val.replace("|", "\\|").replace("\n", "<br>")
            cells.append(cell_val)
        rows.append(cells)

    if not rows:
        return ""

    lines = []
    num_cols = len(col_order)

    if has_header and rows:
        header = rows[0]
        while len(header) < num_cols:
            header.append("")
        lines.append("| " + " | ".join(header[:num_cols]) + " |")
        lines.append("| " + " | ".join(["---"] * num_cols) + " |")
        rows = rows[1:]
    else:
        lines.append("| " + " | ".join([""] * num_cols) + " |")
        lines.append("| " + " | ".join(["---"] * num_cols) + " |")

    for row in rows:
        while len(row) < num_cols:
            row.append("")
        lines.append("| " + " | ".join(row[:num_cols]) + " |")

    return "\n".join(lines) + "\n"


def _children(block: dict) -> list:
    return block.get("content", []) or []


def _format_todo(text: str, checked: bool) -> str:
    return f"- [{'x' if checked else ' '}] {text}"


def _format_toggle(summary: str, child_md: str) -> str:
    if child_md.strip():
        return f"<details>\n<summary>{summary}</summary>\n\n{child_md.strip()}\n</details>\n"
    return f"<details>\n<summary>{summary}</summary>\n</details>\n"


def convert_block(block_id: str, block_map: dict, indent_level: int = 0) -> str:
    """Convert a single block and descendants to Markdown."""
    block = block_map.get(block_id)
    if not block:
        return ""

    block_type = block.get("type")
    props = block.get("properties", {})
    fmt = block.get("format", {})
    children = _children(block)
    title = render_rich_text(props.get("title"))
    indent = "  " * indent_level

    if block_type == "page":
        lines = []
        for child_id in children:
            child_md = convert_block(child_id, block_map, indent_level)
            if child_md:
                lines.append(child_md.rstrip())
        return ("\n\n".join(lines) + "\n") if lines else ""

    if block_type in {"text", "paragraph"}:
        return f"{indent}{title}" if title else ""
    if block_type == "header":
        return f"{indent}# {title}"
    if block_type == "sub_header":
        return f"{indent}## {title}"
    if block_type == "sub_sub_header":
        return f"{indent}### {title}"
    if block_type == "bulleted_list":
        item = f"{indent}- {title}" if title else f"{indent}-"
        child_parts = [convert_block(child_id, block_map, indent_level + 1) for child_id in children]
        child_parts = [part for part in child_parts if part]
        if child_parts:
            return item + "\n" + "\n".join(child_parts)
        return item
    if block_type == "numbered_list":
        item = f"{indent}1. {title}" if title else f"{indent}1."
        child_parts = [convert_block(child_id, block_map, indent_level + 1) for child_id in children]
        child_parts = [part for part in child_parts if part]
        if child_parts:
            return item + "\n" + "\n".join(child_parts)
        return item
    if block_type == "to_do":
        checked = bool(block.get("properties", {}).get("checked", [["No"]])[0][0] == "Yes")
        item = f"{indent}{_format_todo(title, checked)}"
        child_parts = [convert_block(child_id, block_map, indent_level + 1) for child_id in children]
        child_parts = [part for part in child_parts if part]
        if child_parts:
            return item + "\n" + "\n".join(child_parts)
        return item
    if block_type == "quote":
        return f"{indent}> {title}"
    if block_type == "code":
        language = fmt.get("code_wrap") or ""
        return f"{indent}```{language}\n{title}\n{indent}```"
    if block_type == "divider":
        return f"{indent}---"
    if block_type == "callout":
        icon = fmt.get("page_icon") or "Note"
        return f"{indent}> **{icon}:** {title}".rstrip()
    if block_type == "toggle":
        child_md = "\n\n".join(
            part.rstrip()
            for part in (convert_block(child_id, block_map, indent_level) for child_id in children)
            if part
        )
        return f"{indent}{_format_toggle(title or 'Details', child_md).rstrip()}"
    if block_type == "image":
        source = (
            block.get("properties", {}).get("source", [[None]])[0][0]
            or fmt.get("display_source")
            or fmt.get("block_cover_position")
        )
        caption = render_rich_text(props.get("caption")) or "image"
        return f"{indent}![{caption}]({source})" if source else f"{indent}![{caption}]()"
    if block_type == "bookmark":
        link = block.get("properties", {}).get("link", [[None]])[0][0]
        if link:
            label = title or link
            return f"{indent}- [{label}]({link})"
        return ""
    if block_type == "table":
        return f"{indent}{convert_table(block, block_map).rstrip()}"
    if block_type in {"column_list", "column"}:
        parts = [convert_block(child_id, block_map, indent_level) for child_id in children]
        parts = [part for part in parts if part]
        return "\n\n".join(parts)

    if children:
        rendered_children = [convert_block(child_id, block_map, indent_level + 1) for child_id in children]
        rendered_children = [part for part in rendered_children if part]
        if title and rendered_children:
            return f"{indent}{title}\n" + "\n".join(rendered_children)
        if rendered_children:
            return "\n".join(rendered_children)

    return f"{indent}{title}" if title else f"{indent}<!-- missing block: {block_type} -->"


def blocks_to_markdown(page_id: str, block_map: dict) -> str:
    """Render the full page to Markdown with a metadata header."""
    page = block_map.get(page_id, {})
    title = render_rich_text(page.get("properties", {}).get("title")) or "Untitled"

    body = convert_block(page_id, block_map).strip()
    source_url = page.get("format", {}).get("display_source") or page.get("format", {}).get("page_cover_position")

    parts = [f"# {title}", ""]
    if source_url:
        parts.extend(
            [
                "> Notion page archive",
                f"> Source: {source_url}",
                "",
            ]
        )
    if body:
        parts.append(body)
        parts.append("")
    return "\n".join(parts)


def sanitize_filename(name: str) -> str:
    """Turn title into a filesystem-safe basename."""
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE).strip().lower()
    name = re.sub(r"[-\s]+", "-", name)
    return name[:80] or "notion-page"


def resolve_workspace_root() -> str:
    """Best-effort workspace root used for output path validation."""
    env_root = os.environ.get("PWD")
    if env_root:
        return os.path.realpath(env_root)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return os.path.realpath(result.stdout.strip())
    except OSError:
        pass

    return os.path.realpath(os.getcwd())


def resolve_default_output_dir() -> str:
    """Default output dir for CLI usage without explicit output path."""
    workspace_root = resolve_workspace_root()
    return os.path.join(workspace_root, "skill-outputs", "gather")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0 if sys.argv[1:] and sys.argv[1] in ("-h", "--help") else 1)

    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        page_id = parse_notion_url(url)
        eprint(f"  Page ID: {page_id}")

        block_map, page_title = fetch_page(page_id)

        if not output_path:
            filename = sanitize_filename(page_title) + ".md"
            output_dir = resolve_default_output_dir()
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)

        real_path = os.path.realpath(output_path)
        workspace_root = resolve_workspace_root()
        if not (real_path == workspace_root or real_path.startswith(workspace_root + os.sep)):
            raise ValueError(f"Output path must be within workspace root: {output_path}")

        markdown = blocks_to_markdown(page_id, block_map)

        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(markdown)

        eprint(f"  Saved: {output_path} ({len(markdown)} bytes)")

    except (ValueError, RuntimeError) as error:
        eprint(f"Error: {error}")
        sys.exit(1)
    except KeyboardInterrupt:
        eprint("\nAborted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
