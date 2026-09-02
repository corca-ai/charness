#!/usr/bin/env python3
"""Which late-family artifacts `check_spec_evidence_durability.py` BINDS.

The gate scans citations; this module answers whether a given artifact in the
later-added families is enforced or a frozen record that is counted instead.
Two channels: the filename date against the enforcement anchor, and a sibling
Goal Binding whose hash freezes a Goal Draft's exact bytes. The advisory that
reports the frozen count lives here too, because its wording IS the scope rule
read back to the operator.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

#: The repo's ONE owner of an artifact's effective grandfathering date. Imported
#: rather than reimplemented: a second date reader on a second proof surface is
#: how the two would come to disagree about which artifacts a floor binds.
_scope = import_repo_module(__file__, "scripts.review.critique_enforcement_scope")

#: The date this widening landed. A doc in `LATE_DOC_GLOBS` is enforced when its
#: FILENAME dates it on or after this; earlier ones are grandfathered. A doc whose
#: filename carries no readable date is enforced whatever its body says -- see
#: `is_enforced_late_doc` for why only that channel grandfathers.
ENFORCED_FROM = date(2026, 8, 22)


def is_enforced_late_doc(doc: Path, text: str) -> bool:
    """Whether a `LATE_DOC_GLOBS` artifact is inside the enforced window.

    Delegates to `critique_enforcement_scope.observed_date`, this repo's ONE
    owner of "the artifact's effective date for grandfathering": the LATER of the
    in-body `Date:` line and the leading `YYYY-MM-DD` of the filename. Not
    mtime and not commit date -- either of those moves when a frozen record is
    touched for an unrelated reason, and the record would drift into enforcement
    without its content changing.

    **An UNDATABLE doc is ENFORCED, not exempt**, and that direction is the whole
    correctness of this function. The first cut read it the other way, and a
    fresh-eye round found the hole: 68 checked-in artifacts in these families
    carry no parseable date, 64 of them in `critique/` and `retro/`, and they are
    overwhelmingly one-shot `*-packet.md` review artifacts -- the files that carry
    the MOST run-output citations, undated by this repo's own naming convention.
    So the exemption was not date-bounded debt that shrinks as history recedes; it
    was an unbounded hole that GROWS with every new packet, opened by omitting a
    filename convention nothing validates. One live violation was already sitting
    in it.

    That reading is not a novel judgement -- it is the rule this repo already
    wrote down twice, after measuring the same mistake:
    `critique_enforcement_scope.observed_date`'s own docstring says callers "must
    NOT treat `None` as fail-open by default", and `validate_critique_artifacts`
    records that its first cut exempted undated artifacts and "handed back the
    whole of C4 through the one input the rule names as never fail-open".

    There is deliberately NO allowlist. Fail-closed leaves exactly three citations
    to resolve across all 68 filename-undated docs, and each is a genuine
    reproduction source that the `<!-- reproduction-source -->` marker already
    exists to label. An exemption list would be larger than the problem.

    **Only the FILENAME channel grandfathers, and `text` is deliberately unused
    for that decision.** The first fail-closed cut delegated to
    `observed_date`, which is `max(body_date, filename_date)` -- and a round-2
    reviewer showed that repair carried a narrowed form of the class it fixed.
    `observed_date`'s safety argument is corroboration: when both channels parse,
    an artifact is exempt only if they agree it is old. Its own docstring records
    the residual -- "an undated filename with a back-dated body is therefore still
    exempt" -- and mitigates it with "the scaffold always emits both".

    That mitigation inverts on THIS corpus. The population here is *defined* by
    having no filename date, so the author-written body line is not a corroborating
    channel, it is the only one. One line, `Date: 2020-01-01`, in the first five
    lines of a new review packet bought a permanent exemption. Four checked-in docs
    already take their date from the body alone, one of them `critique/latest.md` --
    a rolling pointer whose content is replaced while its body date is
    author-maintained, which is exactly the grows-not-shrinks shape the fail-closed
    repair was raised about.

    So the delegation is kept for what it is good at and dropped where its argument
    does not hold: `date_from_filename` is a name nobody edits while rewriting a
    doc's body, and an artifact that wants grandfathering must be NAMED old. This
    also sidesteps a second pre-existing hole the reviewer found in the body
    channel -- `date_from_body` does not strip display fences, so a packet that
    merely QUOTES another artifact's `Date:` header reads the quotation as its own
    claim. That is filed rather than fixed here; this gate simply stops depending
    on it.

    `text` stays in the signature because a future channel (a front-matter field, a
    committed-date corroboration) belongs here and not at the call site.

    **The second channel is the Goal Binding, and it is a hash, not a date.** A
    Goal Draft whose exact bytes an immutable `*.binding.json` records is a frozen
    record in the strictest sense this repo has: the binding writer refuses to
    rewrite a bound draft, and every Goal Run read checks the draft's SHA-256
    against the binding before it trusts the run. Editing such a draft to satisfy
    this gate would break the run's identity to make a checker happy, the exact
    inversion the date anchor exists to refuse. So a bound draft is COUNTED in the
    advisory like a pre-anchor record. This is not an allowlist and not an
    author-written date: it holds only while the bytes on disk hash to what the
    binding froze, and a draft edited after binding is enforced again.
    """
    if binding_freezes(doc):
        return False
    observed = _scope.date_from_filename(doc)
    if observed is None:
        return True
    return observed >= ENFORCED_FROM


GOAL_BINDING_KIND = "charness.goal-binding/v1"
GOAL_BINDING_SUFFIX = ".binding.json"


def binding_freezes(doc: Path) -> bool:
    """Does a sibling Goal Binding hash exactly these bytes of `doc`?

    The binding sits beside the draft as `<stem>.binding.json` and names the
    draft's SHA-256 under `draft.sha256`. Anything short of an exact match -- no
    sibling, unreadable JSON, another kind, a stale hash -- reads as NOT frozen,
    so the only way to earn the exemption is to leave the bound bytes alone.
    """
    if doc.suffix != ".md":
        return False
    binding = doc.with_name(doc.name[: -len(".md")] + GOAL_BINDING_SUFFIX)
    if not binding.is_file():
        return False
    try:
        payload = json.loads(binding.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(payload, dict) or payload.get("kind") != GOAL_BINDING_KIND:
        return False
    draft = payload.get("draft")
    if not isinstance(draft, dict) or not isinstance(draft.get("sha256"), str):
        return False
    return hashlib.sha256(doc.read_bytes()).hexdigest() == draft["sha256"]


def grandfathered_advisory(grandfathered: int) -> str | None:
    """The excluded-citation count, described as the population it actually is.

    Reported, never silent: a gate that quietly excludes part of its own scope
    reads as "covered everything" when it did not.

    The wording is load-bearing and an earlier cut got it wrong in a way a fresh
    eye caught. It said the excluded citations "remain in artifacts dated before
    <date>" and that "new artifacts in those families are enforced" -- and both
    clauses were false for the undated subset, which was neither dated-before
    anything nor enforced when new. That merged two populations with opposite
    half-lives (one shrinking as history recedes, one growing with every new
    packet) into a single number nobody could read as either. Undated docs are
    now enforced, so the count describes ONE population again and the sentence
    can say what it is.
    """
    if not grandfathered:
        return None
    return (
        f"ADVISORY (evidence durability): {grandfathered} citation(s) to gitignored "
        f"targets remain in artifacts whose FILENAME date precedes {ENFORCED_FROM.isoformat()} "
        "or whose exact bytes a sibling Goal Binding hashes; they are frozen records "
        "and are counted, not rewritten. Every artifact in those families whose "
        "filename dates it on or after that -- and every artifact whose FILENAME "
        "carries no readable date at all, whatever its body says -- is enforced."
    )
