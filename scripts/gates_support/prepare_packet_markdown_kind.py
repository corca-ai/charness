from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

PREPARE_PACKET_KIND_LINE_RE = re.compile(r"^- \*\*Kind\*\*:\s*`(?P<kind>[^`]+)`\s+\(v\d+\)$")


def _nonempty_lines(text_or_lines: str | Sequence[str]) -> list[str]:
    if isinstance(text_or_lines, str):
        lines = text_or_lines.splitlines()
    else:
        lines = list(text_or_lines)
    return [line.strip() for line in lines if line.strip()]


def prepare_packet_markdown_kind(
    path: Path,
    text_or_lines: str | Sequence[str],
    *,
    expected_title_re: re.Pattern[str],
) -> str | None:
    """Return the prepare-packet `kind` for a rendered markdown packet, else None.

    Recognition is intentionally narrow and producer-owned: the file must use a
    `*-packet.md` filename, open with the rendered `# ... Prepare Packet` title,
    and carry the envelope `Kind` line near the top. Validators compare the
    returned kind against their expected producer value, so a renamed record or a
    packet with the wrong envelope kind still fails its record-floor checks.
    """
    if not path.name.endswith("-packet.md"):
        return None
    nonempty_lines = _nonempty_lines(text_or_lines)
    if not nonempty_lines or not expected_title_re.match(nonempty_lines[0]):
        return None
    for line in nonempty_lines[1:8]:
        match = PREPARE_PACKET_KIND_LINE_RE.match(line)
        if match:
            return match.group("kind")
    return None


def is_prepare_packet_markdown_kind(
    path: Path,
    text_or_lines: str | Sequence[str],
    *,
    expected_kind: str,
    expected_title_re: re.Pattern[str],
) -> bool:
    return prepare_packet_markdown_kind(
        path,
        text_or_lines,
        expected_title_re=expected_title_re,
    ) == expected_kind


def file_is_prepare_packet_markdown_kind(
    path: Path, *, expected_kind: str, expected_title_re: re.Pattern[str]
) -> bool:
    return path.is_file() and is_prepare_packet_markdown_kind(
        path,
        path.read_text(encoding="utf-8"),
        expected_kind=expected_kind,
        expected_title_re=expected_title_re,
    )
