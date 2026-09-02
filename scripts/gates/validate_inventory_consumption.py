#!/usr/bin/env python3

"""Fail when a quality inventory is cited in `## Commands Run` but the artifact body
does not engage with any of its declared non-headline review-state fields.

Issue #145 enriched several quality helpers with review-state fields beyond the
`status` / `heuristics` headline so consumers could form judgment. The
consumer-side contract did not yet exist: an artifact could cite the inventory
and still summarize only the headline. This validator closes that loop.

The contract only applies to artifacts dated on or after ENFORCED_FROM_DATE.
Earlier artifacts are frozen retros — rewriting them to fit a later gate would
be Goodhart's law (and the original reviewer never had this contract).

Contract source: skills/public/quality/references/inventory-consumer-fields.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
# The residual measure already exists in this repo, for sweep row S3's stub half. Reusing
# it rather than writing a third copy is not only DRY: the first cut here counted every
# surviving character, so a QUOTED stub (`"n/a"`) scored exactly the floor, and it stripped
# only the field under test, so a line naming three declared fields engaged all three with
# zero observations. `_bound_residual_chars` counts alphanumerics only and removes every
# token longest-first, which is what closes both.
from scripts.gates import check_prescribed_skill_executed_lib as _residual_lib  # noqa: E402
from scripts.core.repo_path_display import display_path as _display_path  # noqa: E402

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_process

DEFAULT_ARTIFACT_PATH = "charness-artifacts/quality/latest.md"
DEFAULT_CONSUMER_FIELDS_PATH = "skills/public/quality/references/inventory-consumer-fields.json"
INVENTORY_FILE_RE = re.compile(r"inventory_[A-Za-z0-9_]+\.py")
COMMANDS_RUN_HEADER = "## Commands Run"
ARTIFACT_DATE_RE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
ENFORCED_FROM_DATE = date(2026, 5, 13)
SKILL_ERGONOMICS_INVENTORY = "inventory_skill_ergonomics.py"
PROSE_REVIEW_RESULT_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:prose[\s-]+review\s+result)\s*:",
)
# floor-addition-restraint: this tightens an existing skill-ergonomics citation
# contract after a quality dogfood run passed with inventory compliance but no
# target-skill structural judgment. It does not add a new artifact section.
STRUCTURAL_REVIEW_RESULT_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:structural[\s-]+review\s+result)\s*:",
)
TARGET_BOUNDARY_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?Target boundary\s*:")
AMBIENT_REPO_FINDINGS_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?Ambient repo findings\s*:")
# Stub vocabulary: a value that names no observation. `n/a` against a field is the
# artifact declining to engage, spelled as engagement.
STUB_VALUE_RE = re.compile(r"^(n/?a|none|nil|tbd|todo|unknown|skipped|-{1,3}|\?)$", re.IGNORECASE)
# Multi-word stubs. The per-token filter below can never match a phrase — `not` and
# `applicable` are separate tokens, neither a stub — so `not applicable` scored 13 and
# passed. This vocabulary is matched against the whole normalized value first.
STUB_PHRASE_RE = re.compile(
    r"^(n/?a|none|nil|tbd|todo|unknown|skipped|not applicable|nothing|none found|"
    r"no findings|not checked|not reviewed|no change[sd]?|same as above|see above)"
    r"[\s.;,!]*$",
    re.IGNORECASE,
)
# Sweep row S10: engagement was `\b<field>\b` presence anywhere in the body, so five
# `Target boundary: n/a` stubs satisfied the contract. A mention counts only when the
# line carries something BEYOND the field name and a stub token — the same rule that
# closed S3 ("evidence must say something beyond the identity it was checked against"),
# applied one surface over.
#
# The floor is 5, and it is a measured number rather than a defended one. Over the
# checked-in quality artifacts the lowest real label value scores 7 and a bare `n/a`
# scores 0, so 5 sits under the corpus minimum with margin. The corpus size moves with
# every quality write, so it is NOT transcribed here — read `artifacts` in the probe.
# Re-runnable with
# `measure_inventory_consumption_floor.py --floor N`, recorded at
# `charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json`: at floor 5
# nothing is refused; at floor 20, 11 citations drop below their requirement and 46 label
# values fall under the floor. An earlier draft of this comment claimed floor 20 was also
# free — the probe refutes it, which is this file's own class one level up.
#
# What this does NOT close, stated because the measurement says so plainly:
#
#   * An explicit negation is not a stub. `I did not read scope_status or finding_status
#     at all.` scores 18 after every declared field is stripped — above the floor. This
#     refuses a stub, not a lie, which is sweep row S11's class.
#   * A field whose NAME is an ordinary English word defeats the floor entirely. The
#     declaration file gives `inventory_nose_clones.py` fields such as `scope_status`,
#     `requested_paths`, `ranking`, `family_count`, `families`, and `notes`; the real
#     corpus line `- Runtime hotspot ranking excludes samples older than 14 days` engages
#     `ranking` on incidental prose. MEASURED, and re-derivable — run
#     `scripts/gates/measure_inventory_marker_rule.py` against
#     `charness-artifacts/probe/2026-08-01-inventory-marker-rule.json`. Read the counts
#     from the probe's measured fields — `field_mentions_presence_only`,
#     `field_mentions_clearing_todays_floor`, `field_mentions_without_a_marker`, and
#     `citations_refused_by_the_marker_rule` — rather than from this comment. Requiring a
#     marker (`field=`, `field:`, `` `field` ``) would refuse the sampled incidental
#     cases, though not all of them, since a marker can appear in prose too. It is
#     deferred as D47.
#     Deliberately not transcribed: this comment carried `190 / 182 / 29 / 3 refused
#     citations across 2 artifacts` for two refresh cycles after the probe moved, and
#     before that a 51-of-169 hand count. The numbers change on every quality write; the
#     probe path does not.
#
# The first cut of this floor did not even refuse a stub: it counted every surviving
# character, so `"n/a"` scored exactly the floor, and it stripped only the field under
# test, so a line naming three declared fields engaged all three. Both are closed above.
MIN_ENGAGEMENT_RESIDUAL_CHARS = 5
_PUNCTUATION_RE = re.compile(r"[`*_\-\[\]()#>|:,.]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact-path", type=Path, default=None)
    parser.add_argument("--consumer-fields-path", type=Path, default=None)
    return parser.parse_args()


def residual_chars(line: str, label: str, other_labels: tuple[str, ...] = ()) -> int:
    """Alphanumerics left on ``line`` after removing every label and every stub token.

    This is the "says something beyond the identity" measure, and it removes ALL the
    labels rather than only the queried one: a line reading
    `scope_status, finding_status, prose_review_status` otherwise scored each field
    against the other two field names and engaged all three while observing nothing.
    """
    normalized = " ".join(line.split())
    if STUB_PHRASE_RE.match(re.sub(r"^[^0-9A-Za-z]+", "", normalized)):
        return 0
    # ORDER MATTERS. Labels are stripped from the RAW text first: `_PUNCTUATION_RE` turns
    # `_` into a space, so running it first would break `scope_status` into two words that
    # no longer match the label token — which is how a bare enumeration of three field
    # names scored 41 instead of 0 on the first attempt at this fix.
    stripped = normalized
    for token in sorted({t for t in (label, *other_labels) if t}, key=len, reverse=True):
        stripped = re.sub(re.escape(token), " ", stripped, flags=re.IGNORECASE)
    without_stubs = " ".join(
        part for part in _PUNCTUATION_RE.sub(" ", stripped).split() if not STUB_VALUE_RE.match(part)
    )
    # The shared alphanumeric counter, so a punctuation-heavy line does not score as prose.
    return _residual_lib._bound_residual_chars(without_stubs, [])


def _engages(body: str, field: str, all_fields: tuple[str, ...]) -> bool:
    """True when at least one mention of ``field`` carries a value beyond its own name.

    ``all_fields`` is the inventory's full declared list; every one of them is stripped
    before counting, so other field names cannot stand in for content.
    """
    others = tuple(f for f in all_fields if f != field)
    pattern = re.compile(rf"\b{re.escape(field)}\b")
    return any(
        pattern.search(line)
        and residual_chars(line, field, others) >= MIN_ENGAGEMENT_RESIDUAL_CHARS
        for line in body.splitlines()
    )


def _labelled_line_engages(body: str, label_re: re.Pattern[str]) -> bool:
    """True when a `Label:` line exists AND the value AFTER the colon says something.

    The skill-ergonomics floors below tested only for the label's presence, so
    `Target boundary: n/a` satisfied them. The value is what has to carry weight, so the
    residual is measured over the remainder of the line, not over the label. A value may
    continue on the next line, which is why the corpus minimum for a real label is 7
    rather than 0.
    """
    for match in label_re.finditer(body):
        line_end = body.find("\n", match.end())
        value = body[match.end() :] if line_end == -1 else body[match.end() : line_end]
        if residual_chars(value, "") >= MIN_ENGAGEMENT_RESIDUAL_CHARS:
            return True
    return False


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return run_process(["git", *args], cwd=repo_root, timeout_seconds=15)
    except OSError:
        return None


def commit_state(repo_root: Path, path: Path) -> tuple[str, date | None]:
    """How git dates ``path``: ``("dated", d)`` / ``("uncommitted", head_date)`` /
    ``("dirty", head_date)`` / ``("unavailable", None)``.

    The three non-``dated`` states used to collapse into one ``None``, which took the
    NOT-CORROBORATED arm and exempted the artifact — so the S9 attack survived on the
    path where it matters most, a freshly authored file that has not been committed yet.
    That is the state EVERY artifact is in when this gate runs before the commit.

    Honest limits, recorded so a later reader does not upgrade this: `%cs` is the
    committer date, which `GIT_COMMITTER_DATE` can forge, so this is a channel the
    artifact does not author — not an unforgeable one. And in a shallow (`fetch-depth: 1`)
    checkout every file's last commit is the tip, which would flip genuinely frozen
    pre-contract artifacts into false refusals; this gate runs only from `run-quality.sh`
    today, never in a CI job, and adding it to one needs `fetch-depth: 0`.
    """
    head = _git(repo_root, "log", "-1", "--format=%cs")
    if head is None or head.returncode != 0:
        return "unavailable", None
    try:
        head_date = date.fromisoformat(head.stdout.strip()) if head.stdout.strip() else None
    except ValueError:
        head_date = None

    status = _git(repo_root, "status", "--porcelain", "--", str(path))
    if status is None or status.returncode != 0:
        # The one channel that used to fall through on failure, which let an `index.lock`
        # or a submodule pathspec turn a dirty artifact back into "Corroborated".
        return "unavailable", None
    if status.stdout.strip():
        # Tracked-and-modified or untracked. Either way the bytes on disk are not the
        # bytes git dated, so a "corroborated" verdict would affirm content git never saw.
        code = status.stdout.lstrip()
        never_committed = code.startswith("?") or code.startswith("A")
        return ("uncommitted" if never_committed else "dirty"), head_date

    result = _git(repo_root, "log", "-1", "--format=%cs", "--", str(path))
    if result is None or result.returncode != 0:
        return "unavailable", None
    stamp = result.stdout.strip()
    if not stamp:
        # git works and the repo has commits; this file was simply never committed.
        return "uncommitted", head_date
    try:
        return "dated", date.fromisoformat(stamp)
    except ValueError:
        return "unavailable", None


def _split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"_preamble": []}
    current = "_preamble"
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            current = line.rstrip()
            sections.setdefault(current, [])
            continue
        sections[current].append(line)
    return {header: "\n".join(lines) for header, lines in sections.items()}


def _skill_ergonomics_failures(
    inventory: str, body_without_commands: str, all_fields: tuple[str, ...]
) -> list[str]:
    field_checks = [
        (
            "prose_review_status",
            "body does not engage with `prose_review_status`; skill ergonomics inventory "
            "output is not a prose-review result.",
        ),
    ]
    checks = [
        (
            TARGET_BOUNDARY_RE,
            "body has no `Target boundary:` line outside the command log carrying a value; a stub "
            "such as `n/a` is the artifact declining to engage, spelled as engagement.",
        ),
        (
            AMBIENT_REPO_FINDINGS_RE,
            "body has no `Ambient repo findings:` line outside the command log carrying a value; a stub "
            "such as `n/a` is the artifact declining to engage, spelled as engagement.",
        ),
        (
            PROSE_REVIEW_RESULT_RE,
            "body has no `prose review result:` line outside the command log carrying a value; a stub "
            "such as `n/a` is the artifact declining to engage, spelled as engagement.",
        ),
        (
            STRUCTURAL_REVIEW_RESULT_RE,
            "body has no `structural review result:` line outside the command log carrying a value; a stub "
            "such as `n/a` is the artifact declining to engage, spelled as engagement.",
        ),
    ]
    return [
        f"inventory `{inventory}` is cited in `{COMMANDS_RUN_HEADER}` but the artifact {message}"
        for field, message in field_checks
        if not _engages(body_without_commands, field, all_fields)
    ] + [
        f"inventory `{inventory}` is cited in `{COMMANDS_RUN_HEADER}` but the artifact {message}"
        for pattern, message in checks
        if not _labelled_line_engages(body_without_commands, pattern)
    ]


def _exemption_verdict(
    repo_root: Path, artifact_path: Path, relative: str, artifact_text: str
) -> int | None:
    """`0` to skip as exempt, `1` to refuse the exemption, `None` to run the floors.

    Extracted from ``main`` because the four corroboration arms are one concept, and
    inlining them pushed ``main`` past the repo's complexity limit.
    """
    match = ARTIFACT_DATE_RE.search(artifact_text)
    if match is None:
        return None
    try:
        artifact_date = date.fromisoformat(match.group(1))
    except ValueError:
        # `Date: 2026-13-45` matches the digit shape and is not a date. Treating it as
        # absent keeps the floors running; raising here was a false RED.
        return None
    if artifact_date >= ENFORCED_FROM_DATE:
        return None
    state, committed = commit_state(repo_root, artifact_path)
    if state in {"uncommitted", "dirty"} and committed is not None:
        if committed >= ENFORCED_FROM_DATE:
            what = (
                "has never been committed"
                if state == "uncommitted"
                else "has uncommitted modifications"
            )
            print(
                f"{relative}: the `Date:` line claims {artifact_date.isoformat()}, which "
                f"would exempt this artifact, but the file {what}, so git has not seen "
                f"these bytes — and the repository's most recent commit is "
                f"{committed.isoformat()}, on or after the contract start "
                f"({ENFORCED_FROM_DATE.isoformat()}). Content authored under the "
                "contract does not exempt itself by declaring an earlier date.",
                file=sys.stderr,
            )
            return 1
        # The whole repository predates the contract, so there is nothing to refuse — but
        # HEAD's date says nothing about THIS file's bytes, which git has not seen. Only
        # the `dated` arm below may say "Corroborated".
        print(
            f"Artifact {relative} dated {artifact_date.isoformat()} "
            f"predates contract start ({ENFORCED_FROM_DATE.isoformat()}); skipped. NOT "
            f"CORROBORATED: the file is not committed as it stands, and the repository's "
            f"most recent commit ({committed.isoformat()}) also predates the contract, so "
            "nothing here observed these bytes."
        )
        return 0
    if state == "unavailable" or committed is None:
        # A check that did not run is not a check that passed, so this is NOT silently
        # upgraded to a refusal either — the pre-existing behavior stands and says why.
        print(
            f"Artifact {relative} dated {artifact_date.isoformat()} "
            f"predates contract start ({ENFORCED_FROM_DATE.isoformat()}); skipped. NOT "
            "CORROBORATED: git could not date this file (not a repository, or no git "
            "binary), so the exemption rests on the artifact's own `Date:` line."
        )
        return 0
    if committed < ENFORCED_FROM_DATE:
        print(
            f"Artifact {relative} dated {artifact_date.isoformat()} "
            f"predates contract start ({ENFORCED_FROM_DATE.isoformat()}); skipped. "
            f"Corroborated: last committed {committed.isoformat()}."
        )
        return 0
    print(
        f"{relative}: the `Date:` line claims {artifact_date.isoformat()}, which would "
        f"exempt this artifact from the inventory-consumption contract, but git records "
        f"its most recent commit as {committed.isoformat()} — on or after the contract "
        f"start ({ENFORCED_FROM_DATE.isoformat()}). An artifact written or rewritten "
        "under the contract does not exempt itself by declaring an earlier date. Fix the "
        "`Date:` line, or engage with the cited inventories.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    artifact_path = (args.artifact_path or (repo_root / DEFAULT_ARTIFACT_PATH)).resolve()
    consumer_fields_path = (
        args.consumer_fields_path or (repo_root / DEFAULT_CONSUMER_FIELDS_PATH)
    ).resolve()

    if not artifact_path.is_file():
        print(f"{artifact_path}: not found", file=sys.stderr)
        return 1
    if not consumer_fields_path.is_file():
        print(f"{consumer_fields_path}: not found", file=sys.stderr)
        return 1

    artifact_text = artifact_path.read_text(encoding="utf-8")
    relative = _display_path(artifact_path, repo_root)
    verdict = _exemption_verdict(repo_root, artifact_path, relative, artifact_text)
    if verdict is not None:
        return verdict
    sections = _split_sections(artifact_text)
    commands_run = sections.get(COMMANDS_RUN_HEADER, "")
    body_without_commands = "\n".join(
        block for header, block in sections.items() if header != COMMANDS_RUN_HEADER
    )

    raw = json.loads(consumer_fields_path.read_text(encoding="utf-8"))
    inventories: dict[str, dict] = raw.get("inventories", {})

    cited = sorted(set(INVENTORY_FILE_RE.findall(commands_run)))
    failures: list[str] = []
    declared_consumed: list[str] = []

    for inventory in cited:
        entry = inventories.get(inventory)
        if entry is None:
            continue
        fields: list[str] = entry.get("non_headline_fields") or []
        if not fields:
            continue
        engaged = [
            field for field in fields if _engages(body_without_commands, field, tuple(fields))
        ]
        required = 2 if len(fields) >= 2 else 1
        if len(engaged) < required:
            declaration_relative = _display_path(consumer_fields_path, repo_root)
            failures.append(
                f"inventory `{inventory}` is cited in `{COMMANDS_RUN_HEADER}` but the artifact "
                f"body engages with {len(engaged)} of its declared non-headline fields "
                f"({', '.join(fields)}); contract requires ≥{required} distinct field(s). Cite "
                f"observations that use at least {required} of those fields, or remove the "
                f"citation if the inventory was not actually consumed. Declaration source: "
                f"{declaration_relative}."
            )
        else:
            declared_consumed.append(inventory)
        if inventory == SKILL_ERGONOMICS_INVENTORY:
            failures.extend(
                _skill_ergonomics_failures(inventory, body_without_commands, tuple(fields))
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    if declared_consumed:
        print(
            f"Validated inventory consumption for {len(declared_consumed)} declared inventory "
            f"citation(s) in {relative}."
        )
    else:
        print(f"No declared inventory citations found in {relative}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
