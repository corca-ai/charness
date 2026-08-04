"""Deliberate absence — the adapter's vocabulary for "this field is missing on purpose".

Absence alone cannot carry intent. `field not in raw` reads identically whether the
operator never set the field or deliberately cut it, so a generator that defaults on
absence refills both cases. That is the #481 loss: a repo that had removed
`coverage_floor_policy` (because it uses neither lefthook nor CI) got it back on the
next bootstrap, pointing at files that do not exist.

`deliberately_absent` makes the second case sayable, and it carries the rationale in
the SAME place as the signal. That pairing is the point: the rationale used to live in
a YAML comment, which is the one part of the file a re-serializer cannot keep, so the
only record of the intent died in the same pass that overrode it.

    deliberately_absent:
      coverage_floor_policy: this repo uses neither lefthook nor CI
      security_commands: no repo-owned security helper exists here

An adapter without the field behaves exactly as it did before it existed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import strip_inline_comment

# Fields that describe the adapter itself rather than an optional repo surface.
# Declaring one of these absent would not express a customization, it would produce
# an adapter that cannot be resolved — so it is refused rather than honored.
STRUCTURAL_FIELDS = frozenset(
    "version repo language output_dir preset_id customized_from deliberately_absent".split()
)

FIELD = "deliberately_absent"


def load_deliberately_absent(
    raw: dict[str, Any], adapter_path: Path, known_fields: set[str] | None = None
) -> tuple[dict[str, str], list[str]]:
    """Validate and return the adapter's declared deliberate absences, plus warnings.

    Raises ValueError with a repair instruction; the caller re-raises it as the
    bootstrap's own validation error type.
    """
    if FIELD not in raw:
        return {}, []
    declared = raw.get(FIELD)
    if not isinstance(declared, dict):
        raise ValueError(
            f"{adapter_path}: `{FIELD}` must be a mapping of field name to the reason it is "
            f"absent (got {type(declared).__name__}). Repair the adapter before rerunning bootstrap."
        )
    errors: list[str] = []
    honored: dict[str, str] = {}
    for field, reason in declared.items():
        if not isinstance(field, str) or not field.strip():
            errors.append(f"field name {field!r} is not a non-empty string")
            continue
        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"`{field}` has no reason; a deliberate absence must say why, or a later "
                "reader cannot tell it from an oversight"
            )
            continue
        if field in STRUCTURAL_FIELDS:
            errors.append(f"`{field}` is structural and cannot be declared absent")
            continue
        if field in raw:
            errors.append(
                f"`{field}` is declared absent but is also set in this adapter; remove one "
                "of the two so the intent is unambiguous"
            )
            continue
        honored[field] = reason.strip()
    if errors:
        rendered = "; ".join(errors)
        raise ValueError(
            f"{adapter_path}: invalid `{FIELD}`; {rendered}. Repair the adapter before rerunning bootstrap."
        )
    # A misspelled field name is honored as a silent no-op: the declaration looks
    # right in the file and the real field keeps getting refilled forever, which is
    # the exact confusion this vocabulary exists to end. It stays a warning rather
    # than an error because declaring a consumer-owned field absent is legal.
    warnings: list[str] = []
    if known_fields:
        unrecognized = sorted(field for field in honored if field not in known_fields)
        if unrecognized:
            warnings.append(
                f"`{FIELD}` names {len(unrecognized)} field(s) this bootstrap does not "
                f"generate: {', '.join(unrecognized)}. If one is a typo, the field it was "
                "meant to name is still being refilled from defaults."
            )
    return honored, warnings


def count_comment_lines(text: str) -> int:
    """Count lines carrying a YAML comment — the surface a re-serializer silently drops.

    Trailing comments count too. They are just as destroyed by a rewrite as a full-line
    one, and a repo that annotates fields in place would otherwise get a rewrite that
    reports losing nothing.
    """
    return sum(1 for line in text.splitlines() if _line_has_comment(line))


def _line_has_comment(line: str) -> bool:
    """Defer to the parser's own rule rather than re-deriving it.

    A second implementation of "where does the comment start" disagreed with the
    parser on an unquoted value carrying an apostrophe: the parser stripped the
    comment while this counter, tracking that apostrophe as an unclosed quote, saw
    none — so the rewrite destroyed an annotation and reported losing nothing.
    """
    stripped = line.strip()
    if not stripped:
        return False
    return stripped.startswith("#") or strip_inline_comment(stripped) != stripped


def describe_intent_loss(
    existing_text: str | None,
    rendered_text: str,
    field_statuses: dict[str, str],
    *,
    subkey_refills: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Report what an about-to-happen rewrite costs the operator.

    A generator that cannot preserve a customization has to SAY SO. Refusing was
    considered and rejected: the operator does not hand-edit adapters, so refusing
    would push the merge back onto whoever ran the tool. Saying so keeps the merge
    here and still leaves a signal a reader can act on.
    """
    # TWO independent claims, reported independently. Gating them together on the comment
    # count made the refill claim self-silencing: the first rewrite destroys every comment,
    # so from then on the file has none, and a later deletion could be refilled with the
    # tool saying nothing at all. The longer a repo lived with the tool, the quieter the
    # tool got about undoing that repo's decisions.
    #
    # This is not "warn more often". A converged adapter is not rewritten at all, so it
    # stays completely silent; and once a refilled field is written it counts as explicit
    # on the next run, so the refill claim quiets itself as soon as it has been acted on.
    # The signal fires when something was actually reverted, not on a schedule.
    #
    # Only name fields this run actually wrote into the file. `defaulted` covers every
    # field the operator never set, and the renderer drops the empty ones, so listing all
    # of them buries the one or two that matter under ~25 names nobody customized.
    written = {line.split(":", 1)[0] for line in rendered_text.splitlines() if line[:1].isalpha()}
    refilled = sorted(
        field for field, status in field_statuses.items() if status == "defaulted" and field in written
    )
    # SUB-KEY refills, one level below `refilled`. A field the operator KEPT but
    # partially emptied has status `augmented`, never `defaulted`, so the filter above
    # cannot see it and no claim was made at all -- while the field-status line said
    # `preserved`. This is the field-level case exactly, one level down, and worse
    # reported: the top-level one at least changed the file visibly.
    subkey_refills = {
        field: keys
        for field, keys in (subkey_refills or {}).items()
        if keys and field_statuses.get(field) == "augmented" and field in written
    }
    dropped = count_comment_lines(existing_text) if existing_text else 0
    if not refilled and not dropped and not subkey_refills:
        return {}

    report: dict[str, Any] = {}
    claims: list[str] = []
    if refilled:
        report["refilled_fields"] = refilled
        claims.append(
            f"this rewrite refilled {len(refilled)} field(s) from defaults that the adapter did "
            f"not set: {', '.join(refilled)}. If any of them is absent ON PURPOSE, declare it in "
            f"`{FIELD}` — absence alone cannot say so, and every run will refill it again."
        )
    if subkey_refills:
        report["refilled_subkeys"] = {field: list(keys) for field, keys in sorted(subkey_refills.items())}
        for field, keys in sorted(subkey_refills.items()):
            claims.append(
                f"this rewrite refilled {len(keys)} sub-key(s) of `{field}` from defaults that the "
                f"adapter's own block did not set: {', '.join(keys)}. The field is reported "
                f"`augmented`, not `preserved` — it was kept AND added to. `{FIELD}` names whole "
                f"fields only, so it cannot yet say a SUB-key is absent on purpose. Review the "
                f"listed leaves individually; do not drop the whole `{field}` block merely to "
                f"silence this warning, because configured sibling values may carry real intent. "
                f"If the whole field is absent on purpose, declare it in `{FIELD}`; resolution "
                f"still supplies the default VALUE to consumers."
            )
    if dropped:
        report["comments_dropped"] = dropped
        claims.append(
            f"{dropped} comment line(s) in the existing adapter will not survive this rewrite: the "
            "adapter is re-serialized from data, so comments have nowhere to go. If any of them "
            f"recorded WHY a field was removed, move that reason into `{FIELD}` — it is data, so "
            "it survives."
        )
    report["customization_warning"] = " ".join(claims)
    return report
