"""A consolidation ledger states its POPULATION and its REMOVALS separately.

The measured defect, and it is a frequency finding rather than a supposition:
closeout ledger arithmetic was the blocking resolution-critique finding in THREE
of four consecutive closeouts, always the same way -- the owner counted among the
things consolidated. `four implementations, three consolidated` where four
existed, one was the owner that stayed, and two private copies were removed.

One sentence carrying two numbers invites that. The reader cannot tell whether
`three consolidated` means "three were removed" or "three were folded into the
survivor, of which one IS the survivor", and the writer does not notice which one
they meant. Separate labeled counts make the ambiguity unwritable: a population
of 4 and 2 removals are two facts, and nobody has to subtract.

WHY A SHAPE RULE AND NOT A PROSE PARSER. The goal that owns this repair forbids a
gate an operator would learn to ignore, and parsing an arithmetic claim out of
English -- deciding whether `four implementations, three consolidated` is
actually WRONG -- is the surest way to build one. This floor never checks the
arithmetic. It checks that the two numbers were stated as two numbers, which is
a shape the writer controls and a reviewer can verify at a glance.

AND IT ONLY FIRES ON A COUNTING CLAIM. A sibling-search field that says
`decision: no siblings; proof: repo-wide grep, zero hits` asserts no population
arithmetic, so nothing is required of it. The trigger is a number standing next
to a consolidation verb -- the exact shape that failed three times.
"""
from __future__ import annotations

import re

#: A number (digit or small word) within a short span of a consolidation verb.
#: Bounded to one sentence-ish span so a count in one clause and a verb three
#: sentences later is not read as one claim.
_NUMBER_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
#: A COUNT, not merely a numeral. A hash-prefixed issue reference, an ISO date,
#: and a `file.py:<line>` citation are all numbers an ordinary ledger is full of.
#:
#: The boundaries exclude only the JOINING forms, and that distinction is the
#: round-2 repair: the first cut excluded a numeral followed by any `.`, which
#: also excluded every count that ENDS A SENTENCE -- where counts most often sit.
#: `Four sibling sites; bundled 3.` then passed silently, which is the exact
#: ambiguity this floor exists to refuse. A `.` before a DIGIT is a version or
#: decimal; a `.` before space or end-of-line is punctuation.
_NUMBER = rf"(?<![#\w:.-])(?:\d+|{'|'.join(_NUMBER_WORDS)})(?![\w:-]|\.\d)"

#: Explicit VERB FORMS, enumerated rather than stem-plus-optional-suffix.
#:
#: The vocabulary is taken from the AUTHORING SURFACE that produces these
#: sentences (`../references/causal-review.md`: "which siblings were BUNDLED into
#: this commit and which were DEFERRED") plus this repo's checked-in closeout
#: corpus -- not from the one measured sentence. Round-1 review found the first
#: cut written from that sentence alone, so the verb the reference literally
#: instructs authors to use was invisible.
#:
#: Round 2 then found the WIDENING carried its own defect twice over. A shared
#: `(?:e|es|ed|ing|ion|ions)?` suffix set cannot inflect these stems: `dropped`,
#: `unified` and `removals` were all invisible, and `unif` could match no real
#: English word at all -- a comment-shaped no-op inside a proof surface. And
#: bare `inlin`/`drop` over-matched ordinary ledger prose (`inline code
#: comments`, `drop-in copies`), refusing ledgers that asserted ZERO
#: consolidation. Enumerating the forms costs a few lines and has neither failure.
_CONSOLIDATION_VERB = (
    r"(?:consolidat(?:e|es|ed|ing|ion|ions)"
    r"|remov(?:e|es|ed|ing|al|als)"
    r"|delet(?:e|es|ed|ing|ion|ions)"
    r"|dedup(?:e|es|ed|ing|licate|licated|lication)"
    r"|collaps(?:e|es|ed|ing)"
    r"|fold(?:s|ed|ing)"
    r"|merg(?:e|es|ed|ing)"
    r"|bundl(?:e|es|ed|ing)"
    r"|absorb(?:s|ed|ing)"
    r"|subsum(?:e|es|ed|ing)"
    r"|prun(?:e|es|ed|ing)"
    r"|retir(?:e|es|ed|ing)"
    r"|eliminat(?:e|es|ed|ing)"
    # INFLECTED forms only. Bare `drop` matched `drop-in copies`, refusing a
    # ledger that asserted zero consolidation; `dropped`/`drops` cannot.
    r"|drop(?:s|ped|ping)"
    # `unif*` was NAMED as a known miss in the round-2 comment above and then
    # never added to the list the comment sits on -- so `Four implementations,
    # three unified.` passed a floor built to refuse exactly that ambiguity,
    # while the synonym `consolidated` was refused. A defect a comment records
    # and the code does not carry is the same shape as a record nobody re-read.
    r"|unif(?:y|ies|ied|ying|ication|ications))"
)
#: Bounded to a clause: `.`/`;`/newline end the span. There is no character cap.
#: The previous `{0,80}` was a fitted constant with no contract behind it -- a
#: count separated from its verb by 81 characters slipped the floor. The clause
#: boundary is the real bound, and widening here fails CLOSED: a wider match
#: means the floor APPLIES more often, never that it passes more often.
_CLAUSE = r"[^.;\n]*"
_COUNTING_CLAIM = re.compile(
    rf"(?i){_NUMBER}{_CLAUSE}\b{_CONSOLIDATION_VERB}\b"
    rf"|\b{_CONSOLIDATION_VERB}\b{_CLAUSE}{_NUMBER}"
)

#: `label: <number>` -- the labels that name HOW MANY THERE WERE. `found` and
#: `total` were removed after round-1 review: they are generic tool-output words,
#: so `matches found: 12` silently became the population and the report DISPLAYED
#: a grep hit count as the verdict's first number.
_POPULATION_LABEL = r"(?:populations?|implementations?|instances?|copies|sites|call sites)"
#: ...and the labels that name HOW MANY WENT AWAY. Disjoint from the above on
#: purpose: a single label cannot satisfy both halves.
#:
#: Kept IN STEP with the verb list, which round 2 found it was not. Widening the
#: trigger while leaving the labels behind refused an author who had done exactly
#: what the floor asks -- `Population: 4 call sites; pruned: 2` -- and told them
#: to state a number they had already stated. That is the arbitrary refusal at an
#: irreversible boundary that `_labeled_count` below warns about, rebuilt one
#: field over.
_REMOVED_LABEL = (
    r"(?:removed|removals?|deleted|consolidated|merged|folded|collapsed|bundled"
    r"|pruned|retired|absorbed|subsumed|eliminated|deduplicated|dropped|unified)"
)


def _labeled_count(text: str, label_pattern: str) -> str | None:
    """The number a label carries, in digits OR words.

    Round-1 review: accepting `four` as a COUNTING CLAIM while requiring `4` in
    the LABEL refused an author who had done exactly the right thing — two facts,
    two labels, no subtraction — for a reason with no motivation behind it. An
    arbitrary refusal at an irreversible boundary is how a gate earns a
    route-around.
    """
    match = re.search(
        rf"(?i)\b{label_pattern}\b[ \t]*[:=][ \t]*(\d+|{'|'.join(_NUMBER_WORDS)})\b", text
    )
    return match.group(1) if match else None


def evaluate(siblings_value: str | None) -> dict:
    """Whether a counting sibling-search ledger states both numbers separately.

    Returns ``applies``/``ok``/``reason`` plus the two parsed counts, so a caller
    can show what it read rather than only that it refused. ``applies: False``
    means no counting claim was made -- never a silent pass.
    """
    text = (siblings_value or "").strip()
    if not text or not _COUNTING_CLAIM.search(text):
        return {
            "applies": False,
            "ok": True,
            "reason": (
                "not applicable: the sibling-search ledger makes no counting claim, so there "
                "is no population arithmetic to state separately"
            ),
            "population": None,
            "removed": None,
        }
    population = _labeled_count(text, _POPULATION_LABEL)
    removed = _labeled_count(text, _REMOVED_LABEL)
    if population is not None and removed is not None:
        return {
            "applies": True,
            "ok": True,
            "reason": f"population and removals stated separately ({population} / {removed})",
            "population": population,
            "removed": removed,
        }
    absent = [
        name
        for name, value in (("population", population), ("removed", removed))
        if value is None
    ]
    return {
        "applies": True,
        "ok": False,
        "reason": (
            "consolidation ledger states a count without separating population from removals; "
            "missing a labeled `<label>: <number>` for: "
            + ", ".join(absent)
            + ". One sentence carrying both numbers is how `four implementations, three "
            "consolidated` gets written when four existed, one was the OWNER that stayed, and "
            "two copies were removed -- the blocking finding in three of four consecutive "
            "closeouts. State them as two numbers (e.g. `population: 4; removed: 2`) so the "
            "owner cannot be counted among the removals. This does NOT check your arithmetic, "
            "only that the two facts are two facts."
        ),
        "population": population,
        "removed": removed,
    }


#: The sibling-search ledger must SAY what it decided and SHOW what proved it.
#: Kept here with the counting rule rather than at the call site: both are rules
#: about what one field must state, and one home is what stops them drifting.
_DECISION = re.compile(r"(?i)\bdecision\b")
_PROOF = re.compile(r"(?i)\bproof\b")


def missing_sibling_ledger_fields(siblings_value: str | None, substantive=bool) -> list[str]:
    """Every shape rule the sibling-search ledger fails, not just the first.

    Empty/absent is NOT this function's refusal -- the caller's substantive-value
    check already owns "the field is missing", and reporting it twice would name
    one defect as two.
    """
    missing: list[str] = []
    value = (siblings_value or "").strip()
    # `_has_substantive_value`, not truthiness: a PLACEHOLDER (`TBD`) is
    # non-empty, so the caller already reports it as a missing field and adding
    # a second finding names one defect twice. Round-2 review.
    if substantive(value) and not (
        _DECISION.search(value) and _PROOF.search(value)
    ):
        missing.append("siblings_decision_and_proof")
    if not evaluate(siblings_value)["ok"]:
        missing.append("siblings_separate_population_and_removal_counts")
    return missing


#: The author-facing statement of every sibling-ledger shape rule, keyed by the
#: finding id the validator emits. `describe_closeout_draft_shape` renders from
#: THIS rather than hand-typing the rules, because that module's own contract is
#: that it never re-declares a rule -- and it had already accumulated one
#: hand-typed copy, which is how a draft filled straight from it can fail the
#: check it was written to pass. Round-1 review found the new rule missing there
#: entirely and the drift guard structurally unable to see it.
SIBLING_RULE_DESCRIPTIONS = {
    "siblings_decision_and_proof": (
        "bug `Siblings:` must name BOTH a decision and proof"
    ),
    "siblings_separate_population_and_removal_counts": (
        "a bug `Siblings:` that makes a COUNTING claim ('three consolidated') must state "
        "population and removals as two labeled numbers (`population: 4; removed: 2`), so the "
        "owner cannot be counted among the removals"
    ),
}


def rule_reason(siblings_value: str | None, finding_id: str) -> str | None:
    """The specific, author-facing reason behind one finding id.

    Exists because the blocking carrier had nothing to say. The library built a
    six-line diagnosis and the only consumer read `["ok"]` and dropped it, so an
    author stopped at the pre-commit boundary got one unexplained snake_case
    token -- on the one surface that can stop a commit. Round-1 review, and the
    same class is already commented as measured in
    `<repo-root>/scripts/gates/check_issue_closeout_commit_msg.py`.
    """
    if finding_id == "siblings_separate_population_and_removal_counts":
        report = evaluate(siblings_value)
        return None if report["ok"] else report["reason"]
    return SIBLING_RULE_DESCRIPTIONS.get(finding_id)
