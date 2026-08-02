# Issue 478 resolution
Date: 2026-08-02

## Decision Under Review

Closing #478 after dispositioning its seven sites three ways (shim / relabel /
drop), and whether that close can be made without implying the class is closed.

## Failure Angles

- **A close reads as class-closure.** #478's own history is a set that grew from
  3 to 4 to 7 as each pass widened its denominator; a close that says "all seven
  resolved" makes the next enumeration start from a false zero.
- **The prevention field overclaims.** A blocking gate exists, but it may cover
  the previous issue's shape rather than this one's.
- **`<authoring-repo>/` renames rather than repairs** for the pointer sites.
- **The fix carries the class it fixes** — the measurement that found these was
  `.py`-anchored, and so was the gate shipped alongside it.

## Counterweight Pass

Real blockers, folded: the prevention scope, the class-vs-sites framing, and the
`.py` anchor (fixed rather than deferred — it was one character, and deferring
the known blind spot that produced site 6 would have been the fifth measured
instance of shipping the class you are repairing). Over-worry raised and NOT
folded: that `<authoring-repo>/` is charness-specific vocabulary appearing in
prose shipped to unrelated repos. True, but the alternative is a 404, and the
placeholder at least routes the reader correctly.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: https://github.com/corca-ai/charness/issues/479 | action: file-issue | note: at least eleven further confirmed instances of the enclosing class are live, including broken links in the shipped mirror that check_doc_links never scans; filed so the next pass does not restart from zero | follow-up: https://github.com/corca-ai/charness/issues/479
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/inventory_skill_script_references.py:61 | action: fix | note: the gate was still `.py`-anchored, the exact blind spot that hid site 6 from every earlier pass; anchor removed, 402 -> 416 references now scanned
- F3 | bin: act-before-ship | evidence: strong | ref: tests/test_skill_script_references.py:107 | action: fix | note: a floor pinned at least one live `<repo-root>/scripts/` reference in real prose forever, so correctly converting the last one would have failed the suite — removed, the synthetic fixtures already prove the classifier arm fires
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/inventory_skill_script_references.py:227 | action: document | note: the gate does NOT block #478's shape and never did; `<repo-root>/scripts/X` naming a real authoring-repo script is deliberately advisory, and the ledger says so rather than claiming prevention it does not have
- F5 | bin: over-worry | evidence: moderate | ref: skills/public/setup/references/default-surfaces.md:125 | action: defer | note: `<authoring-repo>/` leaves the consumer unable to open the file; deliberate — a permalink would give the affordance and is the recorded follow-up

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only typed subagent; Read/Grep/Glob only)
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, session-model inheritance per the Claude Code host split
- Host exposure state: applied
- Application state: host-confirmed: the spawn returned a full findings report in-band and self-reported its envelope as Read/Grep/Glob only
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — a bounded `bounded-reviewer` subagent, delegated before the
close call. Reviewer-boundary window `issue-478-causal`; snapshot and verify both
`clean`, no drift, verify run the moment it returned.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the tree at HEAD 8fd1397f plus the issue body and its two comments, handed to the reviewer inline. -->

## Boundary Ownership

- Producer: skill prose authors, who name a path without local evidence of whose tree it is in.
- Consumer: an agent in a consuming repo following that prose.
- Owning surface: `docs/conventions/authoring-preflight.md`'s placeholder vocabulary, plus the resolver that makes each spelling checkable.
- Verdict: escalated-to-issue-spec

## What the review changed

The reviewer did not ratify the fix. Three things in this closeout are its work:

1. **The class is not closed, and the ledger now says so.** It swept axes no
   earlier pass had — non-`.py` targets, `<repo-root>/` at non-script paths, bare
   `scripts/…` prose, and markdown LINKS — and found eleven-plus live instances,
   two of which are #477's depth class in the shipped mirror where
   `check_doc_links` does not look. Filed as #479.
2. **The prevention claim was traced and cut down.** Walking
   `_classify_repo_root_form` shows none of the seven would have been blocked
   while live: they land in `AUTHORING_REPO`, which is not actionable by design.
   The gate's contribution was an advisory note a human then adjudicated — real
   value, not a gate.
3. **The `.py` anchor was fixed rather than deferred.** Site 6 existed only
   because every measurement was `.py`-only, and the gate shipped in the same
   session still was. One character.

## Non-claims

- This critique reviewed reasoning and swept for siblings statically. It did not
  execute anything, and it does not prove any listed sibling would fail at
  runtime — only that its path does not resolve for a consumer.
- `<authoring-repo>/` fixes the CLAIM, not the affordance: a consumer still
  cannot open those three files.
