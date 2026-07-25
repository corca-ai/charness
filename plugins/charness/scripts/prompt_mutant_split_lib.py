"""Pure prompt-surface splitting: markdown text in, mutation units out.

Split off from `prompt_mutant_lib.py` along that module's own stated seam --
"pure splitter + git-plumbing helpers" -- when the splitter grew paragraph
granularity. This half does no I/O and touches no git: given the text of one
markdown file it returns the units a mutant could remove. The plumbing that turns
a selected unit into a throwaway commit stays in `prompt_mutant_lib.py`.

A "unit" is one markdown section: a heading line (any level) plus its body up
to the next heading of the SAME OR HIGHER level -- so a `###` nested under a
`##` is folded into the `##` unit's own content, while the `###` heading also
gets its own (finer-grained, independently selectable) unit. Because of that
nesting, the file-reassembly (lossless) invariant holds only over the
TOP-LEVEL units (those not nested inside another unit in the same file) plus
the preamble: those spans are contiguous and non-overlapping and tile the
whole file. Nested units are additional, finer-grained entries for selection,
not part of that flat tiling -- and so are paragraph units.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from artifact_naming_lib import slugify
from prompt_mutant_files_lib import skill_plugin_root

_HEADING_RE = re.compile(r"^(#{1,6})(\s+.*)?$")
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


class PromptMutantError(RuntimeError):
    pass


GRANULARITIES = ("section", "paragraph")


class _FenceTracker:
    """Tracks whether the scanner is currently inside a fenced code block.

    Both scanners in this module need the same answer for the same reason: a `#`
    inside a fence is not a heading, and a blank line inside a fence is not a
    paragraph break. Closing requires a marker of the same character and at least
    the opening run length, per CommonMark.
    """

    def __init__(self) -> None:
        self._char: str | None = None
        self._len = 0

    @property
    def inside(self) -> bool:
        return self._char is not None

    def consume(self, stripped: str) -> bool:
        """Feed one line (already stripped of its newline). Return True when the
        line is a fence delimiter, which both callers skip rather than inspect."""
        match = _FENCE_RE.match(stripped.lstrip())
        if not match:
            return False
        marker = match.group(1)
        if self._char is None:
            self._char, self._len = marker[0], len(marker)
        elif marker[0] == self._char and len(marker) >= self._len:
            self._char, self._len = None, 0
        return True


def _fence_aware_blocks(lines: list[str], start_idx: int, end_idx: int) -> list[tuple[int, int]]:
    """Blank-line-separated blocks within `lines[start_idx:end_idx]`, as 0-based
    half-open index pairs.

    Fence-aware for the same reason `split_units` is: a blank line inside a fenced
    code block is content, not a separator, and splitting there would produce a
    mutant that deletes half a code block -- a malformed-markdown arm rather than a
    meaning-removal arm. A block of only whitespace is not a unit and is dropped;
    its lines still belong to the enclosing section, so nothing is lost from the
    section-level tiling.
    """
    blocks: list[tuple[int, int]] = []
    fence = _FenceTracker()
    block_start: int | None = None
    for idx in range(start_idx, end_idx):
        stripped = lines[idx].rstrip("\r\n")
        if fence.consume(stripped):
            if block_start is None:
                block_start = idx
            continue
        if not fence.inside and not stripped.strip():
            if block_start is not None:
                blocks.append((block_start, idx))
                block_start = None
            continue
        if block_start is None:
            block_start = idx
    if block_start is not None:
        blocks.append((block_start, end_idx))
    return blocks


def _frontmatter_end(lines: list[str], start_idx: int, end_idx: int) -> int:
    """Index just past a leading `---` ... `---` YAML block, else `start_idx`."""
    if start_idx >= end_idx or lines[start_idx].rstrip("\r\n") != "---":
        return start_idx
    for idx in range(start_idx + 1, end_idx):
        if lines[idx].rstrip("\r\n") == "---":
            return idx + 1
    return start_idx


def _leaf_spans(lines: list[str], headings: list[tuple[int, int, str]]) -> list[tuple[int, int, int]]:
    """Non-overlapping (start, end, heading_position) spans that tile the file.

    Unlike the section units -- where a `###` span is nested inside its `##` span --
    a leaf span runs from one heading to the NEXT heading of any level. That makes
    every line belong to exactly one leaf, so paragraph units derived from leaves
    cannot double-count a line that two nested sections both own. `heading_position`
    is -1 for the preamble.
    """
    spans: list[tuple[int, int, int]] = []
    preamble_end = headings[0][0] if headings else len(lines)
    spans.append((0, preamble_end, -1))
    for position, (idx, _level, _title) in enumerate(headings):
        end_idx = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        spans.append((idx, end_idx, position))
    return spans


def split_units(text: str, granularity: str = "section") -> list[dict]:
    """Split `text` into section units: one `preamble` unit (content before the
    first heading, always present) followed by one unit per heading line, in
    document order. Each unit's `content` is the exact contiguous slice of
    `text` it owns (0-based line slice `lines[start:end]`), so re-slicing the
    original text at those boundaries is exact -- never re-derived from a hash
    or a fuzzy match. `heading_level` is 0 for the preamble. `top_level` is
    True for the preamble and for headings not nested inside another unit in
    this file (see module docstring); only `top_level` units tile the file
    losslessly.

    With `granularity="paragraph"`, every section unit above is still emitted --
    the coarse arm stays selectable -- and blank-line-separated blocks inside each
    leaf span are emitted as ADDITIONAL finer units (`unit_kind="paragraph"`,
    `top_level=False`). They are derived from leaf spans rather than section spans
    so no line is claimed by two paragraphs, and they carry their owning leaf
    section's `heading_path`: a paragraph is located by which section it argues
    inside, not by an index that shifts when a neighbour is edited."""
    if granularity not in GRANULARITIES:
        # Validated here, not only in `build_split_manifest`: library callers and the
        # `generate` path reach this directly, and an unrecognized value silently
        # falling through to section behaviour would run a whole experiment at the
        # wrong granularity and produce a plausible-looking manifest.
        raise PromptMutantError(
            f"unsupported granularity: {granularity!r} (expected one of {', '.join(GRANULARITIES)})"
        )
    lines = text.splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []  # (0-based line index, level, title)
    fence = _FenceTracker()
    for idx, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        if fence.consume(stripped) or fence.inside:
            continue
        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            title = (heading_match.group(2) or "").strip()
            headings.append((idx, level, title))

    units: list[dict] = []
    preamble_end = headings[0][0] if headings else len(lines)
    units.append(
        {
            "heading_level": 0,
            "heading_path": ["preamble"],
            "start_line": 1,
            "end_line": preamble_end,
            "content": "".join(lines[0:preamble_end]),
            "top_level": True,
            "unit_kind": "section",
        }
    )

    ancestors: list[tuple[int, str]] = []
    heading_paths: list[list[str]] = []
    for position, (idx, level, title) in enumerate(headings):
        end_idx = len(lines)
        for later_idx, later_level, _later_title in headings[position + 1 :]:
            if later_level <= level:
                end_idx = later_idx
                break
        while ancestors and ancestors[-1][0] >= level:
            ancestors.pop()
        top_level = not ancestors
        heading_path = [ancestor_title for _level, ancestor_title in ancestors] + [title]
        units.append(
            {
                "heading_level": level,
                "heading_path": heading_path,
                "start_line": idx + 1,
                "end_line": end_idx,
                "content": "".join(lines[idx:end_idx]),
                "top_level": top_level,
                "unit_kind": "section",
            }
        )
        heading_paths.append(heading_path)
        ancestors.append((level, title))

    if granularity == "paragraph":
        units.extend(_paragraph_units(lines, headings, heading_paths))
    return units


def _paragraph_units(
    lines: list[str],
    headings: list[tuple[int, int, str]],
    heading_paths: list[list[str]],
) -> list[dict]:
    paragraphs: list[dict] = []
    for start_idx, end_idx, position in _leaf_spans(lines, headings):
        if position < 0:
            owning_path = ["preamble"]
            owning_level = 0
            # Skip YAML frontmatter. Removing it does not remove a claim -- it makes
            # the skill fail to register at all, so the arm reads as a strong
            # DETECTED while proving nothing about whether the prose was
            # load-bearing. The section-level preamble unit has the same defect, but
            # paragraph granularity would otherwise mint it as a clean, inviting
            # standalone target.
            body_start = _frontmatter_end(lines, start_idx, end_idx)
        else:
            owning_path = list(heading_paths[position])
            owning_level = headings[position][1]
            # The heading line itself is the section unit's business; a paragraph
            # unit that swallowed it would delete the heading and reparent every
            # following paragraph when applied.
            body_start = start_idx + 1
        for block_start, block_end in _fence_aware_blocks(lines, body_start, end_idx):
            paragraphs.append(
                {
                    "heading_level": owning_level,
                    "heading_path": owning_path,
                    "start_line": block_start + 1,
                    "end_line": block_end,
                    "content": "".join(lines[block_start:block_end]),
                    "top_level": False,
                    "unit_kind": "paragraph",
                }
            )
    return paragraphs


def reassemble_top_level(units: list[dict]) -> str:
    """Concatenate the `top_level` units of one file's `split_units` output, in
    order -- the lossless-reassembly proof: this must equal the original text
    byte-for-byte."""
    return "".join(unit["content"] for unit in units if unit["top_level"])


def unit_content_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_unit_id(file_relpath: str, heading_path: list[str], content: str) -> str:
    digest = unit_content_sha256(content)
    slug = "/".join(slugify(part) for part in heading_path)
    return f"{file_relpath}#{slug}@{digest[:10]}"


def units_for_file(file_relpath: str, text: str, granularity: str = "section") -> list[dict]:
    """`split_units(text)` decorated with the stable `unit_id` and `file` every
    downstream consumer (manifest output, mutant construction) keys off."""
    entries = []
    for unit in split_units(text, granularity):
        content = unit["content"]
        entries.append(
            {
                "unit_id": build_unit_id(file_relpath, unit["heading_path"], content),
                "file": file_relpath,
                "heading_path": unit["heading_path"],
                "heading_level": unit["heading_level"],
                "start_line": unit["start_line"],
                "end_line": unit["end_line"],
                "content_sha256": unit_content_sha256(content),
                "content": content,
                "top_level": unit["top_level"],
                "unit_kind": unit["unit_kind"],
            }
        )
    return entries


# --- split manifest (used by the `split` CLI subcommand) --------------------


def build_split_manifest(repo_root: Path, skill: str, granularity: str, list_files, read_file) -> dict:
    """Assemble the `split` subcommand's manifest. `list_files(repo_root, skill)`
    and `read_file(repo_root, relpath)` are injected so this same builder
    serves both the worktree-backed `split` CLI and (via a ref-bound closure)
    a baseline-ref-aware split for `generate`."""
    if granularity not in GRANULARITIES:
        raise PromptMutantError(
            f"unsupported granularity: {granularity!r} (expected one of {', '.join(GRANULARITIES)})"
        )
    file_pairs = list_files(repo_root, skill)
    if not file_pairs:
        raise PromptMutantError(f"no SKILL.md found for skill {skill!r} under {skill_plugin_root(skill)}")
    files_out = []
    units_out = []
    for plugin_relpath, public_relpath in file_pairs:
        text = read_file(repo_root, plugin_relpath)
        if text is None:
            continue
        for entry in units_for_file(plugin_relpath, text, granularity):
            units_out.append(
                {
                    "unit_id": entry["unit_id"],
                    "file": entry["file"],
                    "public_sibling": public_relpath,
                    "heading_path": entry["heading_path"],
                    "heading_level": entry["heading_level"],
                    "start_line": entry["start_line"],
                    "end_line": entry["end_line"],
                    "content_sha256": entry["content_sha256"],
                    "unit_kind": entry["unit_kind"],
                }
            )
        files_out.append({"path": plugin_relpath, "public_sibling": public_relpath})
    return {"skill": skill, "granularity": granularity, "files": files_out, "units": units_out}


