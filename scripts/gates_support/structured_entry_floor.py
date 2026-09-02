"""The required-fields / unique-id / typed-enum floor over a structured-entry section.

Two artifact families declare machine-readable entries as pipe-delimited bullets —
critique `## Structured Findings` and ideation `## Structured Questions` — and each
had grown the same validation loop: read the section's bullets, parse each entry,
refuse a missing required field, refuse a duplicate id, refuse an out-of-set enum
value. Only the heading, the field names and the allowed sets differed.

The loop is here rather than in `artifact_validator.py` because that module is
inside its length warn band; a shared floor is a new concept, not another line on
an accreting one.

Deliberately NOT owned here: per-family rules with their own grammar. The critique
floor's `action: file-issue` -> `follow-up:` linkage stays at its call site through
``per_entry``, because folding it in would mean carrying one family's conditional
into the other's floor.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
_sections = import_repo_module(__file__, "scripts.core.markdown_sections")
ValidationError = _artifact_validator.ValidationError


def validate_structured_entries(
    path: Path,
    text: str,
    *,
    heading: str,
    required_fields: Iterable[str],
    enum_fields: Mapping[str, Iterable[str]],
    form_hint: str | None = None,
    per_entry: Callable[[dict[str, str], str], None] | None = None,
) -> None:
    """Refuse a malformed structured-entry section; silent when the section is absent.

    An ABSENT section is not a violation here: whether the family requires the
    section at all is a separate floor, and conflating them would make this one
    refuse every artifact that legitimately has no entries.

    ``form_hint`` is appended to the missing-field refusal when the family declares
    a canonical entry form. Describing the whole shape once is what stops an author
    discovering each required field by serial re-runs; a family without a declared
    form says nothing rather than inventing one.

    Entry identity: an entry with no leading id chunk is reported by its ORDINAL
    among the section's bullets (``<entry N>``), not by file line — the two were
    conflated as ``<line N>``, which sends an author to line 3 of the header instead
    of the third structured bullet fifty lines down. Such an entry is not checked for
    duplication, because "several entries with no id" is a missing-id problem, not a
    collision.
    """
    bullets = _sections.section_bullets(text, heading)
    if not bullets:
        return
    required = tuple(required_fields)
    seen_ids: set[str] = set()
    for index, raw in enumerate(bullets, start=1):
        entry = _sections.parse_pipe_entry(raw)
        entry_id = entry.get("id", f"<entry {index}>")
        for field in required:
            if not entry.get(field):
                detail = f"; every entry needs all of {list(required)} — target form: `{form_hint}`" if form_hint else ""
                raise ValidationError(
                    f"{path}: `{heading}` entry {entry_id} missing required field `{field}`{detail}"
                )
        if "id" in entry:
            if entry["id"] in seen_ids:
                raise ValidationError(f"{path}: `{heading}` duplicate id `{entry['id']}`")
            seen_ids.add(entry["id"])
        for field, allowed in enum_fields.items():
            value = entry.get(field, "")
            if value not in set(allowed):
                raise ValidationError(
                    f"{path}: `{heading}` entry {entry_id} has unknown {field} `{value}`; "
                    f"allowed: {sorted(allowed)}"
                )
        if per_entry is not None:
            per_entry(entry, entry_id)
