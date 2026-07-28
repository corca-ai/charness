# Empty scope remainder D7 D9 D10 E5
Date: 2026-07-28

## Decision Under Review

Fixing D7, D9, D10 and E5 — the remainder of the bug hunt's own suggested
cross-cutting family: **an empty or unestablished scope must not return PASS.**
D7 returned one verdict for four different worlds. D9 scanned a scope missing
`skills/shared` and could not see a computed pointer name. D10 had two silent
early-returns that turned a stale claim into a pass. E5 reported 100% coverage
over zero observations and silently excused sub-threshold files.

## Failure Angles

- **Naming the scope is not the same as showing it.** A payload field nobody
  renders is the same silence with more JSON. Bit exactly: D7's new
  `evaluation_scope` never reached the release artifact, which kept asserting an
  evaluation that had not happened.
- **Fail-closed on a value type breaks the caller.** Bit: `coverage: None`
  reached a `<` comparison and produced a traceback instead of a refusal.
- **A detector that covers the example it wrote down, not the one that occurs.**
  Bit twice: D9's computed detector handled the inline form while the repo writes
  the two-statement form, and handled `"latest" + suffix` while the shape that
  occurs puts the literal on the right.
- **The fix for a silent exemption reintroduces one a layer down.** Bit: unmeasured
  files landed in the exemption bucket at `coverage: 1.0` and were therefore
  excluded from the very list documenting what the threshold hides.
- **Widening a matcher to close a blind spot creates false positives.** Checked
  and refuted by measurement.

## Counterweight Pass

- Two blockers and four findings from the bounded reviewer, every one reproduced
  by execution before repair. The two blockers are the ones that mattered: E5's
  fix broke its own gate, and D7's scope stopped at the payload.
- Deliberately added beyond the reported defect: a `schema_version` gate on the
  capability catalog, because "regenerate the catalog" is the wrong instruction
  for a catalog written by a schema this validator does not read — an
  unestablished-scope verdict of exactly the kind D10 is about.
- Over-worry, measured and dismissed: that D9's stem-level prefilter would flag
  real code. The prefilter emits no findings at all — it only selects files for
  the AST scan — and a whole-tree sweep of every `latest`-bearing f-string and
  concatenation under the four scan roots produced nothing. Recorded as a
  negative result rather than quietly dropped.
- Accepted: the vocabulary is applied per-surface rather than through a shared
  helper. Public skills reach repo-internal `scripts/` only through the skill
  runtime loader, and a 20-line helper does not earn a new cross-boundary
  dependency; the VALUES are shared, the keys name what each surface scoped.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_coverage.py:425 | action: fix | note: E5's `coverage: None` reached `summary["coverage"] < args.min_coverage` and produced `TypeError: '<' not supported between instances of 'NoneType' and 'float'` — a traceback where the gate has its own error type; the headline change had no test at all, which is why it shipped
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_artifact_sections.py:337 | action: fix | note: `real_host_lines` branched on `required` alone, so the release artifact asserted "No configured trigger matched this slice" over a record whose scope was `empty` — an evaluation that never ran, claimed at the publish boundary; D8's failure mode inside the D7 fix
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_current_pointer_writes.py:200 | action: fix | note: the computed detector saw only the single-expression form, missing `target = out / f"latest.{ext}"` then `target.write_text(...)` — the idiom this repo writes, and one whose LITERAL twin the gate already handled
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/check_current_pointer_writes.py:156 | action: fix | note: the `BinOp` branch inspected only `left`, but left-associative parsing puts the pointer-ish literal of `str(out) + "/latest." + ext` permanently on the right, so the fix covered its own docstring example and not the occurring shape
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/check_coverage_lib.py:47 | action: fix | note: unmeasured files carry `coverage: 1.0` from the per-file formula, so filing them under the small-file exemption recorded them as perfectly covered and kept them out of `exempt_below_floor` — the fix for a silent exemption reintroducing one a layer down
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/validate_current_pointer_freshness.py:284 | action: fix | note: `_load_json` swallows read and parse errors and returns `{}`, so an unreadable catalog was reported as a shape problem — the right refusal with the wrong remedy; a `schema_version` gate was also absent, so a future schema would read as a malformed current one
- F7 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/scripts/check_real_host_proof.py:153 | action: fix | note: the bare key `scope` lands on the same dict `plan_release_run` stamps `evidence_scope` onto, where the two words mean unrelated things; renamed `evaluation_scope`
- F8 | bin: over-worry | evidence: strong | ref: scripts/check_current_pointer_writes.py:62 | action: document | note: the concern that the stem-level prefilter would flag real code was measured and refuted — the prefilter selects files and emits no findings, and a whole-tree sweep found no live false positive
- F9 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_current_pointer_writes.py:288 | action: defer | note: the gate's own payload reports `status: clean` without recording how many files it scanned, so "clean" still does not say over what; a scanned-count field would make the scope establishable on this surface too

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only agent), one spawn over the family since all four are the same defect class.
- Requested spawn fields: subagent_type=bounded-reviewer, scope prompt naming the highest-risk direction per fix and explicitly inviting the reviewer to name commands it could not run; no host addressing name; session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: Claude Code accepted the `bounded-reviewer` spawn and returned findings inline; `reviewer_boundary_fingerprint.py verify` reported `ok: true` with `drift: []`.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — a bounded read-only reviewer ran in a separate agent
context and listed eight commands it needed. The parent ran all of them. Two
converted reasoning into blockers, two confirmed detector gaps, and one — the
predicted false-positive sweep — refuted the reviewer's own hypothesis, which is
recorded as a negative result rather than dropped.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: four independent gates that each rendered a verdict — real-host proof, current-pointer writes, capability-catalog freshness, control-plane coverage.
- Consumer: the publish path and the quality gate that read those verdicts as clearance, plus the release artifact a human reads at closeout.
- Owning surface: each gate owns naming its own scope, because the scope is only knowable where the check runs; the artifact renderer owns SHOWING it, which is where the D7 fix was still incomplete.
- Verdict: owned-correctly
