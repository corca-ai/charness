"""After-phase closeout-evidence parsing and gating for goal artifacts.

Split out of ``goal_artifact_lib.py`` so the artifact module stays under the
single-file line gate; the closeout-evidence contract (Retro + Host log probe
binding to the shared closeout helper) is also a separable concept.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_shared_helper():
    """Load the repo-owned shared closeout-evidence helper.

    Resolution walks parent directories until ``scripts/`` is found, so the
    helper stays portable across the working tree and any installed export.
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")


# After-phase evidence names. The achieve closeout requires a checked-in retro
# artifact plus a host-log probe output; either may be skipped with an
# enum-valid reason (see ``check_prescribed_skill_executed_lib.ALLOWED_SKIP_REASONS``).
CLOSEOUT_EVIDENCE_NAMES = ("retro_artifact", "host_log_probe")

# #253 rung 1b: in-scope goals (Created >= the disposition rule date) must also
# carry a bound ``Disposition review: <path>`` line proving a fresh-eye
# disposition review *ran* (or a ``skipped: host-blocked-subagent: <detail>``).
# Grandfathered goals do not require it — the name is appended to the required
# set only when ``disposition_gate_applies`` (threaded in ``check_complete_evidence``).
DISPOSITION_REVIEW_EVIDENCE = "disposition_review"

# Retro H2 sections whose substance must be narrated to the user, not just
# persisted to the retro file (#233 F2). The After-phase gate surfaces which of
# these the retro actually contains so the closeout response can transport them.
NARRATION_REQUIRED_SECTIONS = (
    "Waste",
    "Critical Decisions",
    "Next Improvements",
    "Sibling Search",
)

# The ``Disposition[- ]review`` arm is load-bearing (round-3 B1): adding the name
# to CLOSEOUT-style requirements alone would silently drop the line here, so a
# bound review line would never be parsed and every in-scope goal would be
# refused. ``_normalize_evidence_name`` maps the captured label to
# ``disposition_review`` automatically.
_EVIDENCE_LINE = re.compile(
    r"^[\s>*-]*(Retro|Host[- ]log[- ]probe|Disposition[- ]review)\s*:\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# Activation line points at the goal's own file: ``/goal @<repo-rel-path>``.
# The basename minus the date prefix is the goal slug, the strongest binding
# token for the closeout's evidence files (#233 F1).
_ACTIVATION_PATH = re.compile(
    r"^[\s>*-]*Activation\s*:\s*`?\s*/goal\s+@?([^`\s]+)",
    re.MULTILINE | re.IGNORECASE,
)
_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_LEADING_NUMERIC_CLUSTER = re.compile(r"^\d+(?:[-_]\d+)*")


def derive_goal_tokens(text: str) -> list[str]:
    """Extract distinctive binding tokens identifying this goal.

    The tokens are matched against each evidence file's basename/content so a
    closeout cannot satisfy the gate by citing an unrelated pre-existing
    artifact (#233 F1). Returns ``[]`` when the goal identity is not derivable
    (e.g., a malformed Activation line); the caller then opts out of binding.
    """
    match = _ACTIVATION_PATH.search(text)
    if not match:
        return []
    stem = Path(match.group(1)).name
    if stem.endswith(".md"):
        stem = stem[:-3]
    slug = _DATE_PREFIX.sub("", stem)
    if not slug:
        return []
    tokens = [slug]
    numeric = _LEADING_NUMERIC_CLUSTER.match(slug)
    if numeric and numeric.group(0) != slug:
        tokens.append(numeric.group(0))
    return tokens


def narration_sections_present(retro_text: str) -> list[str]:
    """Return which ``NARRATION_REQUIRED_SECTIONS`` the retro file contains.

    Used to surface, at flip-to-complete time, exactly which substantive retro
    sections the closeout response must narrate to the user (#233 F2). This is
    an affordance, not a gate: it does not block the flip.
    """
    masked = _mask_fences(retro_text)
    present: list[str] = []
    for section in NARRATION_REQUIRED_SECTIONS:
        pattern = re.compile(
            rf"^#{{1,6}}\s+{re.escape(section)}\b",
            re.MULTILINE | re.IGNORECASE,
        )
        if pattern.search(masked):
            present.append(section)
    return present


def _mask_fences(text: str) -> str:
    """Mirror of ``goal_artifact_lib._mask_fences`` so this module stays
    self-contained without a circular sibling import.
    """
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    if in_fence:
        return text
    return "".join(masked)


def _normalize_evidence_name(label: str) -> str:
    label = label.strip().lower()
    if label == "retro":
        return "retro_artifact"
    if re.fullmatch(r"host[- ]log[- ]probe", label):
        return "host_log_probe"
    return label.replace(" ", "_").replace("-", "_")


def parse_closeout_evidence(text: str) -> dict[str, dict[str, str]]:
    """Extract ``Retro:`` and ``Host log probe:`` lines from the goal body.

    Returns ``{name: {"kind": "evidence"|"skip", "value": <path-or-reason>}}``.
    A value that starts with ``skipped:`` (case-insensitive) is treated as a
    skip and the remaining text is the reason; otherwise the value is a
    repo-relative or absolute path to the evidence file.
    """
    masked = _mask_fences(text)
    parsed: dict[str, dict[str, str]] = {}
    for match in _EVIDENCE_LINE.finditer(masked):
        name = _normalize_evidence_name(match.group(1))
        raw_value = match.group(2).strip()
        if not raw_value:
            continue
        skip_match = re.match(r"^skipped\s*:\s*(.+)$", raw_value, re.IGNORECASE)
        if skip_match:
            parsed[name] = {"kind": "skip", "value": skip_match.group(1).strip()}
        else:
            parsed[name] = {"kind": "evidence", "value": raw_value}
    return parsed


def _load_sibling_disposition():
    """Load the sibling #253 improvement-disposition gate module.

    Kept in its own file (a separable concept, like this module was split from
    ``goal_artifact_lib.py``) so neither file approaches the single-file line
    gate. This module depends on it; the dependency is one-directional (the
    disposition module is a leaf), so there is no circular import.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_disposition",
        Path(__file__).resolve().parent / "goal_artifact_disposition.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_disposition.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sibling_coordination_floors():
    """Load the sibling gather/release coordination-floor module.

    A leaf like the disposition module (no sibling imports), kept separate so
    this wrapper stays under the single-file line gate. One-directional: this
    module depends on it, never the reverse.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_coordination_floors",
        Path(__file__).resolve().parent / "goal_artifact_coordination_floors.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_coordination_floors.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_disposition = _load_sibling_disposition()
disposition_gate_applies = _disposition.disposition_gate_applies
apply_disposition_rungs = _disposition.apply_disposition_rungs

_coordination = _load_sibling_coordination_floors()
apply_coordination_floors = _coordination.apply_coordination_floors


def check_complete_evidence(repo_root: Path, text: str) -> dict[str, Any]:
    """Run the shared closeout-evidence helper for an ``achieve`` After-phase.

    The wrapper extracts ``Retro:``, ``Host log probe:``, and (for in-scope
    goals) ``Disposition review:`` lines from the goal artifact body and feeds
    them as evidence/skip arguments to the portable ``check`` function. The
    wrapper supplies the contract; the helper is the gate.
    """
    helper = _load_shared_helper()
    parsed = parse_closeout_evidence(text)
    # #253 rung 1b: require the review-ran evidence line only for in-scope goals
    # (grandfather-by-Created gates BOTH rungs — else a grandfathered goal would
    # still be refused for a Disposition review line it never had).
    in_scope = disposition_gate_applies(text)
    required = list(CLOSEOUT_EVIDENCE_NAMES)
    if in_scope:
        required.append(DISPOSITION_REVIEW_EVIDENCE)
    evidence: dict[str, str] = {}
    skips: dict[str, str] = {}
    for name, payload in parsed.items():
        if payload["kind"] == "evidence":
            evidence[name] = payload["value"]
        else:
            skips[name] = payload["value"]
    report = helper.check(
        repo_root=repo_root,
        required=required,
        evidence=evidence,
        skips=skips,
        kind="achieve-after",
    )

    # F1 binding: a present file is necessary but not sufficient — each
    # satisfied evidence file must also bind to this goal's identity, else a
    # closeout could cite any pre-existing retro/probe in the repo.
    tokens = derive_goal_tokens(text)
    binding_failures: list[dict[str, Any]] = []
    for entry in report["satisfied"]:
        if entry.get("via") != "evidence":
            continue
        path = Path(entry["path"])
        if not tokens:
            # Fail closed: a goal that cites evidence files but whose identity
            # is not derivable from its `Activation:` line cannot bind them.
            # A bare `Activation:` substring satisfies check_goal but must not
            # silently disable binding (that one-line shape would reopen F1).
            reason = (
                "goal identity not derivable from the Activation line; cannot "
                "bind this evidence file to the goal"
            )
        else:
            binds, detail = helper.evidence_binds_to_context(path, tokens=tokens)
            reason = detail
            if binds:
                entry["binding"] = reason
                continue
        entry["binding"] = reason
        binding_failures.append(
            {"name": entry["name"], "path": entry["path"], "reason": reason}
        )
    report["binding_tokens"] = tokens
    report["binding_failures"] = binding_failures
    if binding_failures:
        report["ok"] = False

    # F2 affordance: surface which substantive retro sections must travel with
    # the user-facing closeout (not just persist to the file). Non-blocking.
    narration: list[str] = []
    for entry in report["satisfied"]:
        if entry["name"] != "retro_artifact" or entry.get("via") != "evidence":
            continue
        retro_path = Path(entry["path"])
        try:
            retro_text = retro_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            retro_text = ""
        narration = narration_sections_present(retro_text)
    report["narration_required_sections"] = narration

    # #253 rung 1a: deterministic block-the-blank floor (grandfathered by Created
    # date; substance is rung 2's job). Rung 1b (the disposition_review line) is
    # already enforced above via the ``required`` set; 1a fires independently so a
    # rung-1b skip on a subagent-blocked host still leaves the blank check active.
    apply_disposition_rungs(report, text, in_scope)

    # Coordination floors (gather + release): presence-only closeout evidence for
    # the two find-skills-routing boundaries the prose cue under-serves. Mirrors
    # the disposition floor — grandfathered by Created, block-the-blank at the
    # flip, explicit opt-out valve. Independent of the disposition scope (its own
    # rule date), so it runs unconditionally; the module no-ops when inert.
    apply_coordination_floors(report, text)

    return report
