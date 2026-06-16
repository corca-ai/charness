"""After-phase closeout-evidence parsing and gating for goal artifacts.

Split out of ``goal_artifact_lib.py`` so the artifact module stays under the
single-file line gate; the closeout-evidence contract (Retro + Host log probe
binding to the shared closeout helper) is also a separable concept.

The near-identical sibling/shared-module loader boilerplate lives in the cohesive
leaf ``goal_artifact_closeout_loaders.py`` (loaded + re-bound below) so this
wrapper stays focused on parsing and the gate logic and both files keep real
headroom under the single-file line gate.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_local_module(module_name: str):
    """Load a sibling achieve-script module by name via filesystem spec.

    Self-contained (no ``from scripts.`` import, no ``sys.modules`` registration)
    so it resolves both in the working tree and the installed plugin export.
    """
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside goal_artifact_closeout_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The sibling/shared-module loaders live in a cohesive leaf. Re-bound here so the
# established ``ce._load_shared_helper`` / ``ce._load_sibling_*`` surface — including
# the monkeypatch (``check_complete_evidence`` calls the module-global
# ``_load_shared_helper``) and the fail-closed ImportError tests — is unchanged.
_loaders = _load_local_module("goal_artifact_closeout_loaders")
_load_shared_helper = _loaders._load_shared_helper
_load_sibling_disposition = _loaders._load_sibling_disposition
_load_sibling_early_close_report = _loaders._load_sibling_early_close_report
_load_sibling_metric_window = _loaders._load_sibling_metric_window
_load_sibling_coordination_floors = _loaders._load_sibling_coordination_floors
_load_sibling_phase_routing = _loaders._load_sibling_phase_routing
_load_sibling_closeout_delegation = _loaders._load_sibling_closeout_delegation
_load_sibling_adapter_policy = _loaders._load_sibling_adapter_policy
_mask_fences = _load_local_module("goal_artifact_markdown").mask_fences


# After-phase evidence names. The achieve closeout requires a checked-in retro
# artifact plus a host-log probe output; either may be skipped with an
# enum-valid reason (see ``check_prescribed_skill_executed_lib.ALLOWED_SKIP_REASONS``).
CLOSEOUT_EVIDENCE_NAMES = ("retro_artifact", "host_log_probe")

# Disposition rung 1b: in-scope goals must also
# carry a bound ``Disposition review: <path>`` line proving a fresh-eye
# disposition review *ran* (or a ``skipped: host-blocked-subagent: <detail>``).
# Grandfathered goals do not require it — the name is appended to the required
# set only when ``disposition_gate_applies`` (threaded in ``check_complete_evidence``).
DISPOSITION_REVIEW_EVIDENCE = "disposition_review"

# Retro H2 sections whose substance must be narrated to the user, not just
# persisted to the retro file. The After-phase gate surfaces which of these the
# retro actually contains so the closeout response can transport them.
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
    r"^[ \t>]*(Retro|Host[- ]log[- ]probe|Disposition[- ]review|Early[- ]close[- ]report)\s*:\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)

# Activation line points at the goal's own file: ``/goal @<repo-rel-path>``.
# The basename minus the date prefix is the goal slug, the strongest binding
# token for the closeout's evidence files.
_ACTIVATION_PATH = re.compile(
    r"^[\s>*-]*Activation\s*:\s*`?\s*/goal\s+@?([^`\s]+)",
    re.MULTILINE | re.IGNORECASE,
)
_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_LEADING_NUMERIC_CLUSTER = re.compile(r"^\d+(?:[-_]\d+)*")

# Literal scaffold placeholders the goal-artifact template seeds visibly under
# ``## Final Verification`` (e.g. ``Retro: TODO — fill or skip``). The template
# makes the closeout obligation visible from the start of a run, but an
# *untouched* placeholder must never be read as satisfied evidence: a value that
# is, or begins with, one of these markers is dropped at parse time so the
# evidence name falls back to ``missing`` and the complete flip is refused. This
# is the non-weakening guard for the seeded placeholders — relying on
# "the path TODO does not exist" alone would be fragile (a repo could happen to
# carry a file literally named ``TODO``/``TBD``).
_PLACEHOLDER_MARKER = re.compile(r"^(?:(?:TODO|TBD|FIXME)\b|<[^>\n]*>)", re.IGNORECASE)


def is_placeholder_value(value: str) -> bool:
    """True when ``value`` is (or starts with) a literal scaffold placeholder.

    Used to refuse an untouched template ``TODO``/``<path>``/``TBD`` evidence
    line at parse time. A real repo-relative path never starts with one of these
    tokens, so this cannot reject a legitimately-bound evidence path.
    """
    return _PLACEHOLDER_MARKER.match(value.strip()) is not None


def derive_goal_tokens(text: str) -> list[str]:
    """Extract distinctive binding tokens identifying this goal.

    The tokens are matched against each evidence file's basename/content so a
    closeout cannot satisfy the gate by citing an unrelated pre-existing
    artifact. Returns ``[]`` when the goal identity is not derivable
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
    sections the closeout response must narrate to the user. This is an
    affordance, not a gate: it does not block the flip.
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


def _normalize_evidence_name(label: str) -> str:
    label = label.strip().lower()
    if label == "retro":
        return "retro_artifact"
    if re.fullmatch(r"host[- ]log[- ]probe", label):
        return "host_log_probe"
    if _early_close_report.is_report_label(label):
        return EARLY_CLOSE_REPORT_EVIDENCE
    return label.replace(" ", "_").replace("-", "_")


def parse_closeout_evidence(text: str) -> dict[str, dict[str, str]]:
    """Extract closeout evidence lines from ``## Final Verification``.

    Returns ``{name: {"kind": "evidence"|"skip", "value": <path-or-reason>}}``.
    A value that starts with ``skipped:`` (case-insensitive) is treated as a
    skip and the remaining text is the reason; otherwise the value is a
    repo-relative or absolute path to the evidence file.
    """
    masked = _mask_fences(text)
    headings = list(_H2.finditer(masked))
    if headings:
        final_verification = None
        for index, heading in enumerate(headings):
            if heading.group(1).strip() != "Final Verification":
                continue
            body_start = masked.find("\n", heading.start())
            body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
            final_verification = masked[body_start + 1 if body_start != -1 else heading.end():body_end]
            break
        if final_verification is None:
            return {}
        masked = final_verification
    parsed: dict[str, dict[str, str]] = {}
    for match in _EVIDENCE_LINE.finditer(masked):
        name = _normalize_evidence_name(match.group(1))
        raw_value = match.group(2).strip()
        if not raw_value:
            continue
        skip_match = re.match(r"^skipped\s*:\s*(.+)$", raw_value, re.IGNORECASE)
        if skip_match:
            parsed[name] = {"kind": "skip", "value": skip_match.group(1).strip()}
        elif is_placeholder_value(raw_value):
            # An untouched template placeholder (``TODO``/``<path>``/``TBD``) is
            # dropped so the name falls back to ``missing``; the seeded scaffold
            # line can never be mistaken for satisfied evidence.
            continue
        else:
            parsed[name] = {"kind": "evidence", "value": raw_value}
    return parsed


_disposition = _load_sibling_disposition()
disposition_gate_applies = _disposition.disposition_gate_applies
apply_disposition_rungs = _disposition.apply_disposition_rungs

_early_close_report = _load_sibling_early_close_report()
EARLY_CLOSE_REPORT_EVIDENCE = _early_close_report.EARLY_CLOSE_REPORT_EVIDENCE

_coordination = _load_sibling_coordination_floors()
apply_coordination_floors = _coordination.apply_coordination_floors

_phase_routing = _load_sibling_phase_routing()
apply_phase_routing_floor = _phase_routing.apply_phase_routing_floor

_closeout_delegation = _load_sibling_closeout_delegation()
apply_closeout_delegation = _closeout_delegation.apply_closeout_delegation

_section_placeholders = _load_local_module("goal_artifact_section_placeholders")
_operator_queue = _load_local_module("goal_artifact_operator_queue")

_metric_window = _load_sibling_metric_window()
metric_window_attention = _metric_window.metric_window_attention

_adapter_policy = _load_sibling_adapter_policy()


def _apply_evidence_binding(helper, report: dict[str, Any], text: str) -> None:
    tokens = derive_goal_tokens(text)
    binding_failures: list[dict[str, Any]] = []
    for entry in report["satisfied"]:
        if entry.get("via") != "evidence":
            continue
        path = Path(entry["path"])
        if not tokens:
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
        binding_failures.append({"name": entry["name"], "path": entry["path"], "reason": reason})
    report["binding_tokens"] = tokens
    report["binding_failures"] = binding_failures
    if binding_failures:
        report["ok"] = False


def _retro_narration_for_satisfied(report: dict[str, Any]) -> list[str]:
    for entry in report["satisfied"]:
        if entry["name"] != "retro_artifact" or entry.get("via") != "evidence":
            continue
        retro_path = Path(entry["path"])
        try:
            retro_text = retro_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            retro_text = ""
        return narration_sections_present(retro_text)
    return []


def _attach_adapter_policy(report: dict[str, Any], repo_root: Path) -> None:
    policy = _adapter_policy.closeout_policy_report(repo_root)
    report["achieve_adapter_policy"] = policy
    if not policy["valid"]:
        report["ok"] = False


def check_complete_evidence(repo_root: Path, text: str) -> dict[str, Any]:
    """Run the shared closeout-evidence helper for an ``achieve`` After-phase.

    The wrapper extracts ``Retro:``, ``Host log probe:``, and (for in-scope
    goals) ``Disposition review:`` lines from the goal artifact body and feeds
    them as evidence/skip arguments to the portable ``check`` function. The
    wrapper supplies the contract; the helper is the gate.
    """
    helper = _load_shared_helper()
    parsed = parse_closeout_evidence(text)
    # Disposition rung 1b: require the review-ran evidence line only for in-scope goals
    # (grandfather-by-Created gates BOTH rungs — else a grandfathered goal would
    # still be refused for a Disposition review line it never had).
    in_scope = disposition_gate_applies(text)
    required = list(CLOSEOUT_EVIDENCE_NAMES)
    if in_scope:
        required.append(DISPOSITION_REVIEW_EVIDENCE)
    if _early_close_report.report_required(text):
        required.append(EARLY_CLOSE_REPORT_EVIDENCE)
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
    _early_close_report.reject_skip(report)
    _early_close_report.apply_report_shape(report)

    # F1 binding: a present file is necessary but not sufficient — each
    # satisfied evidence file must also bind to this goal's identity, else a
    # closeout could cite any pre-existing retro/probe in the repo.
    _apply_evidence_binding(helper, report, text)

    # F2 affordance: surface which substantive retro sections must travel with
    # the user-facing closeout (not just persist to the file). Non-blocking.
    report["narration_required_sections"] = _retro_narration_for_satisfied(report)

    # Disposition rung 1a: deterministic block-the-blank floor (grandfathered by Created
    # date; substance is rung 2's job). Rung 1b (the disposition_review line) is
    # already enforced above via the ``required`` set; 1a fires independently so a
    # rung-1b skip on a subagent-blocked host still leaves the blank check active.
    apply_disposition_rungs(report, text, in_scope)

    # Coordination floors: presence-only closeout evidence for find-skills
    # routing boundaries the prose cue under-serves. Mirrors
    # the disposition floor — grandfathered by Created, block-the-blank at the
    # flip, explicit opt-out valve. Independent of the disposition scope (its own
    # rule date), so it runs unconditionally; the module no-ops when inert.
    apply_coordination_floors(report, text)
    apply_phase_routing_floor(report, text)

    # Orchestrator/sub-goal closeout-proof delegation. Opt-in via a
    # `## Closeout Delegation` section; an absent section or `Closeout mode:
    # standalone` is untouched, so the strict standalone default stays the hard
    # default. Orchestrated sub-goals must name an orchestrator + list delegated
    # items; orchestrator goals must resolve every delegated checklist item.
    apply_closeout_delegation(report, text)

    # Final-status placeholder floor: a complete goal cannot carry a section
    # whose first real body line still says it is pending/TODO/TBD.
    _section_placeholders.apply_final_status_placeholder_floor(report, text)

    # Created-gated queue floor: new goals must either render queued
    # operator-only decisions or record an explicit empty-queue reason.
    _operator_queue.apply_operator_queue_floor(report, text)

    # Metric-window affordance: surface whether a goal-scoped `Host metric window:` line
    # was recorded so an absent window is visible at flip-to-complete rather than
    # silently reported thread-wide. Strictly non-blocking — it never touches
    # report["ok"] — because a host that lacks timestamps legitimately records
    # the documented `unavailable` case instead.
    report["metric_window"] = metric_window_attention(text)

    # Adapter seam: publication and Auto-Retro policy are repo-owned
    # configuration with safe audit-only fallback when absent. A found but
    # invalid adapter blocks completion so closeout does not silently ignore the
    # repo's declared publication contract.
    _attach_adapter_policy(report, repo_root)

    return report
