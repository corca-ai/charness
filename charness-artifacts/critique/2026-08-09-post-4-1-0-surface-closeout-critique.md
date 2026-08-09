# Post-v4.1.0 surface closeout critique: #523, #566

Date: 2026-08-09
Classification: deferred-work
Fresh-eye satisfaction: parent-delegated
Verdict: both CLOSABLE — #523 as scoped, #566 after the arming gap its reviewer found was repaired.

## Decision Under Review

Whether two surface-shape issues are closable after v4.1.0 (`cd7ab479`). Both were
judged by bounded read-only fresh-eye subagents instructed to REFUSE the close.
`reviewer_boundary_fingerprint.py` verified `clean` around the review window.

## #523 — the always-loaded root surface carried contract prose, not routing

CLOSABLE as scoped. Measured directly rather than read off the slice record:

| surface | at filing | before repair | now |
| --- | --- | --- | --- |
| `AGENTS.md` bytes | 16,918 | 15,806 | **9,425** |
| `AGENTS.md` lines | 132 | 129 | **96** |

The gap between the issue's 16,918 and the repair's 15,806 baseline is drift between
filing and repair, not a lost reduction; the reduction against the repair's own
baseline is -40% bytes / -33 lines.

The content moved rather than vanished, and the targets are reachable: `AGENTS.md:59-66`
routes to `docs/conventions/operating-contract.md#external-side-effect-discipline`,
where the moved detail is richer than what the root carried (issue-close floor,
push non-approval, grant revocation, per-phase grants); `AGENTS.md:53-55` routes to
`agent-docs-policy.md#dynamic-workflow-standing-request`. The reviewer found no
deleted-content evidence.

The release note's claim that the "full delegated-review authorization block" was
PRESERVED is verified, not assumed: the `## Subagent Delegation` block hashes
identically before and after the repair —
`700faa514836dc84672eb79e3616c01bf6b64e74dd0a79cfd1812b4ed80ccba4` in both. That
block is now ~44% of the file, deliberately.

The issue's one comment (read at closeout) reinforces rather than widens the ask: it
cites `ceal-cli` at 8,460 chars as the working example of "layering, not deletion" —
rules at the root, reasons in linked docs. charness at 9,425 sits in that band. The
comment's own table also lists the 1,105-char sibling; that comparison is explicitly
declined, and the file structurally cannot reach it while the delegation block stays
inline. #523's ASK (route to contract owners) is met; #523's COMPARISON is not, and
the close says so.

Named gap, not a blocker: there is no executable cap on root-surface size
(`check_doc_authoring_preflight.py:95-110` registers only the handoff length surface),
while several checks push toward ADDING root prose. The always-loaded surface has a
ratchet in the growth direction and none in the shrink direction, so this reduction is
unratcheted and the same issue can be refiled. Partial protection does exist against
the worst regression: `setup_agent_docs_fresh_eye_lib.py:131,139,148` and
`validate_critique_artifacts.py:288-311` would catch a silent DROP of the delegated-review
authorization, though not a shrink.

## #566 — docs checked for link validity, never as a graph

CLOSABLE after repair. The acceptance boundary is the operator's own re-scope one hour
after filing, read at closeout: the issue's framing was withdrawn ("charness had
already gone further than the issue implies"), and the tracked ask became (1) an awiki
integration manifest so consumers can declare it, (2) the `#518` quality-adapter half
decided SEPARATELY, and (3) keeping the transferable prose lesson.

Step 1 landed (`integrations/tools/awiki.json`). Beyond the re-scoped ask, a real
reachability gate now exists: `scripts/check_docs_graph.py` gates on `orphans` and
`islands` only, names the offending pages, gives island-specific remedy distinct from
orphan remedy, and explicitly does NOT judge link resolution. The failure mode the
reviewer hunted for — a root set so wide that orphans are impossible by construction —
is absent: awiki computes undirected connected components, so an unlinked page is an
isolated vertex and fails. The recorded 7 orphans are gone: the live lane now reports
`documents=42 orphans=0 islands=0`.

**The reviewer's blocker was real and is repaired in this slice.** `docs-graph` was
missing from `.githooks/pre-push` `DOCS_ONLY_LABELS`, so a docs-only push — precisely
the change class that CREATES an orphan — ran a label subset that never included the
reachability lane, and CI runs no awiki step either. The lane's own timing rationale
argued FOR running it at the push boundary ("reachability is a whole-graph property"),
and it addressed only the commit-time layer. `docs-graph` is now in that label set;
measured cost on the docs-only path is 85ms, and on a machine without `awiki` the lane
reports UNPROVEN and blocks nothing.

Second repair from the same review: the PASS line stated no population. A verdict that
does not say WHICH tree it read is the exact class this repo's north star refuses, and
everything outside `docs/` is ungraphed. The renderer now prints
`docs-graph: PASS over docs/ (...)` and adds "any page outside docs/, which this run
never read" to its did-NOT-judge list.

Residual carried into the close, not fixed: the orphan test fixture
(`tests/test_docs_graph_gate.py:33-45`) is hand-written while the island and clean
fixtures are captured from awiki 0.5.0 — and the file's own comment says an invented
fixture proves the branch "against the belief rather than the tool". A real captured
orphan run exists in-repo. No test constructs a real orphan on disk and runs the real
binary.

## Counterweight Pass

The #523 reviewer's strongest refusal was the missing size ratchet. It is a genuine
recurrence risk and it is named in the close, but #523 asked for a shape change, not a
gate; holding the issue open until a cap exists would convert a delivered ask into an
undelivered one.

The #566 blocker was NOT over-worry — a gate that never runs on the change class it
exists for is the same false-green shape the issue's own comment asked the repo to
avoid — so it was repaired rather than dispositioned.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .githooks/pre-push:60 | action: fix | note: docs-graph was absent from DOCS_ONLY_LABELS, so the orphan lane never ran on docs-only pushes; added
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_docs_graph.py:292 | action: fix | note: the PASS line named no scanned population while everything outside docs/ is ungraphed; now stated on the verdict line and in did-NOT-judge
- F3 | bin: valid-but-defer | evidence: strong | ref: scripts/check_doc_authoring_preflight.py:95-110 | action: file-issue | note: no executable cap on the always-loaded root surface, while several checks push toward adding root prose | follow-up: deferred docs/handoff.md#next-session
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests/test_docs_graph_gate.py:33-45 | action: file-issue | note: the orphan fixture is invented while a captured one exists in-repo; no test runs the real binary against a real orphan | follow-up: deferred docs/handoff.md#next-session
- F5 | bin: over-worry | evidence: moderate | ref: AGENTS.md | action: defer | note: charness stays ~8.5x the 1,105-char sibling root; that comparison is declined, not met

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only subagent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, prompt, synchronous
  return; deliberately no host addressing/team `name`.
- Host exposure state: host-defaulted
- Application state: n/a — no per-subagent model or effort override was requested.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: the root instruction surface, and the docs reachability lane plus its arming.
- Consumer: every session that loads the root surface, and every docs-only push.
- Owning surface: `AGENTS.md` owns what it routes; `.githooks/pre-push` owns which lanes
  a push class runs; `check_docs_graph.py` owns stating its own population.
- Verdict: owned-correctly

## Non-Claims

- #523's reduction is unratcheted; no gate prevents the root surface from regrowing.
- #566's `#518` half — whether `awiki lint` becomes a declarable quality-adapter
  surface — was explicitly re-scoped OUT by the operator and is not decided here.
- The docs-graph arming repair is proven by running the docs-only label path locally;
  hosted CI still runs no awiki step, so remote coverage is unchanged and unclaimed.
- The round-2 review of these two repairs was not run; they are recorded as
  accepted-unreviewed.
