# Issue 526 resolution critique
Date: 2026-08-07

## Decision Under Review

Resolving issue #526 by teaching `check_skill_ownership_overlap.py` to report unconsumed
waivers as a stale-allowlist advisory — the posture the repo already stated and built for
its sibling allowlist — and deleting the two entries measured stale, rather than only
deleting the two entries.

## Failure Angles

- **Cleaning without closing.** Removing the two stale lines fixes today and leaves the
  allowlist exactly as able to accumulate tomorrow, which is the actual complaint.
- **Removing a live waiver.** If either entry were still produced by the scanner, deleting
  it turns a declared boundary into a gate violation.
- **Over-claiming what "stale" means.** The scan is scope-limited; "this scan no longer
  produces the overlap" is not the same statement as "the code no longer has it".
- **Advisory that nobody reads.** An advisory printed by a checker that no broad gate runs
  is a line in a log, not a channel.
- **Violation vs advisory.** The sibling repo treats dangling exceptions as violations.

## Counterweight Pass

- Advisory is the right level HERE, and the reason is the scan's own scope: it reads only
  top-level `.py`/`.md` under each skill, so a violation-level verdict would fail a
  correct repo on a scanner blind spot. `ceal-agent` can afford violation level because it
  judges a complete input; this checker judges a deliberately narrow file set.
- Both removals verified dead by the delegated critique, and the second one instructively:
  `setup:artifact:spec`'s mention still EXISTS at
  `skills/public/setup/scripts/templates/t_events_adapter.yaml:7`, invisible to the scan
  twice over (non-recursive `iterdir`, and `.yaml` not in the suffix set). It cannot become
  a violation, but it disproves the tidy reading of "stale".
- The teeth are the standing-pytest pin, not the advisory. Said plainly rather than
  claiming the gate surfaces it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_skill_ownership_overlap.py:131 | action: fix | note: the advisory asserted the waiver "describes a boundary the code no longer has", which is false for one of the two entries removed in this very slice; reworded to claim only what the scan proves and to prompt a re-check before deletion
- F2 | bin: act-before-ship | evidence: moderate | ref: scripts/check_skill_ownership_overlap.allowlist.txt:1 | action: fix | note: the retirement posture lived only in code comments, so the next reader had no way to know entries get retired; stated in the header the way the sibling allowlist states it, which is what made this framable as scope rather than a new rule
- F3 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_skill_ownership_overlap.py:162 | action: fix | note: the pin was a bare equality assert, so the operator it fires for would see a dict dump and no remedy; added the remedy and the scan-scope caveat
- F4 | bin: over-worry | evidence: strong | ref: scripts/check_skill_surface_preflight.py:357 | action: document | note: the preflight captures this checker's stdout into a 1000-char `stdout_tail` and advisories print first, so they truncate first — latent at today's volume, and the pin is the real channel regardless
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_skill_ownership_overlap.py:29 | action: defer | note: `parse_allowlist` returns a set of triples, so two lines differing only in `<reason>` collapse and cannot be individually flagged; accurate today because all 25 are distinct

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (`.claude/agents/bounded-reviewer.md`).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, session-model inheritance per the per-host split for Claude Code hosts.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported read-only Read/Grep/Glob and returned findings inline.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One delegated read-only reviewer ran the resolution critique before the
close. Recorded deviation: the causal-review-before-design round was NOT run separately for
this issue. The issue body already carried a reproduced, line-cited diagnosis and named the
in-repo canonical sibling the fix copies, and the session was at its context limit. That is
a real reduction in review depth for this issue and is stated rather than hidden.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer read the worktree directly. The
binding floor is therefore not turned on for this artifact. -->

## Boundary Ownership

- Producer: `scripts/check_skill_ownership_overlap.py`, which owns the overlap scan and now the staleness verdict.
- Consumer: the maintainer reading the allowlist as documentation, and the standing pytest pin.
- Owning surface: the skill-ownership gate.
- Verdict: single-surface

## Non-Claims

- The allowlist is NOT claimed accurate. A waiver's textual coupling can exist while the
  scan cannot see it (proved by `setup:artifact:spec`), and the converse is possible.
- No surviving waiver's `<reason>` was audited for still being true.
- Stale waivers are not prevented from being ADDED, only surfaced once unconsumed.
- Installed/downstream repos get the advisory only; they have no pin.
- The class "allowlists that only grow" is not fixed repo-wide — this covers one allowlist.
