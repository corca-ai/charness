# Quality Review
Date: 2026-08-18
Title: Repo-wide posture regeneration after the stale 2026-08-14 record

## Scope

Target boundary: repo-wide posture question — regenerate the quality record the handoff
named stale (it asserted #619/#620 open; both are closed). No target skill.

Ambient repo findings: docs-graph `link_only_lines` at 171 over its 167 ratchet, repaired
in-run (four handoff link lines got a holdings phrase, commit `9e1865e45`);
`check-lesson-evaluation-continuity` fails on this session's own just-declared lesson
receipt — as designed until this session's retro claims it.

## Surface Contract Review

- semantic coverage: partial — the standing read-only gate lane was observed as an
  operator would (streamed lifecycle, failure-log recovery, final receipt).
- surface: the `run-quality.sh --read-only` operator lifecycle and its failure receipts.
- owner: `scripts/run-quality.sh` owns lane order and receipt; per-check owners own verdicts.
- projections: streamed CHECK/BATCH lines, the final summary line, and
  `.charness/quality-failure-logs/<check>.log` recovery bodies.
- state scope: one repo checkout per run; failure logs persist across runs.
- transitions: pass, fail-with-retained-log, advisory-on-green; timeout/kill not exercised.
- proof boundary: one full `--read-only` run at HEAD, both failure logs read back, and
  the repaired check re-run to green.
- unexamined axes: full and `--review` lanes, pre-push hook on a real push, non-Linux
  runners, and the release-inclusive lane.

## Current Gates

- Read-only lane: 93 passed, 2 failed at HEAD; after the docs-graph repair the residual
  failure is only the expected self-referential continuity one.
- Maintainer-local enforcement disposition: present — canonical final gate
  `scripts/run-quality.sh`, enforced in clones via checked-in `.githooks` plus
  `python3 scripts/validate_maintainer_setup.py --repo-root .` (green this run).
- Security green: gitleaks ~70 MB no leaks; supply-chain validated. Regenerable-facts:
  259 files clean, 13 exemptions all with recorded reasons. CLI probes and doctor green
  at v6.0.1; `web-fetch` is the one missing optional binary.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile local-linux-x86_64-36cpu. <!-- reproduction-source -->
- runtime hot spots: run-quality-full 234s latest / 144s median vs 420s budget; pytest
  118.3s latest / 109.4s median / 130.9s max vs 120s budget — five recent samples
  (2026-08-16..17) already exceed the budget.
- coverage gate: read-only lane green after the in-run docs-graph repair except the
  expected continuity failure; full and release lanes not run (not-run, not covered).
- evaluator depth: deterministic gates only; Cautilus is eval-only ask-before-run and no
  behavior-eval question was in scope.

## Healthy

- Hook-enforced final gate with per-check failure-log retention and a named recovery path.
- Ratchet-shaped doc gates (docs-graph, dup baseline) that only tighten, with rotation
  accepts recorded as advisories instead of silent baseline rewrites.
- Lesson loop: 26/26 eligible retros carry dispositions; the one open violation is this
  session's own in-flight receipt.

## Weak

- pytest lane has already breached its 120s budget in five recent samples (max 130.9s,
  all passing runs); the budget claim and the measured lane disagree today.
- docs-graph failing at HEAD: the commit-time layer cannot see broad-lane regressions — by design, but it left main red for a day.
- 24 of 43 active lessons have no anchored evidence — exposure counts only, so their lifecycle (graduate/rewrite/archive) is undecidable from the ledger today.

## Missing

- No consumer-side proof this cycle for public-skill routing changes: none shipped in scope, so no dogfood row was owed; named so green is not read as consumer coverage.

## Deferred

- 72 Python files in the length warn band (advisory, none over the 480 hard limit); split-on-concept remains the standing remedy.
- Doc-duplicate family between `skills/public/achieve/scripts/goal_artifact_template.md`
  and `skills/public/handoff/scripts/templates/auto_draft_goal.md` (~28 removable lines) —
  single-sourcing deferred to a slice that owns both skills.

## Advisory

- structural review result: `capability_needed`=an honest current posture record;
  strongest centers are the hook-enforced lane and adapter-routed inventories; strengthen
  next the ledger's anchored-evidence coverage (24/43 unanchored), without which
  lifecycle is undecidable — command: `./scripts/render_lesson_lifecycle_review.py --repo-root .`.
- prose review result: the ergonomics inventory reports `finding_status=heuristics_present`
  over `checked_skill_count=22` with `prose_review_status=required`; this pass answers it
  at spot level, not a full 22-skill prose read: `subcheck_counts` are dominated by
  `host_surface_reference` (59, mostly adapter examples per finding-level review_context),
  `argparse_missing_help` (3, quality scripts) is real minor debt, and `core_overfill`
  and `package_issue_anchor` are both 0.
- Lesson lifecycle judged on anchors, not recurrence (evidence: same lifecycle command):
  `changed-line-proof-before-broad-quality` failed twice while already in prose at the
  failure point — strengthen-binding; `premise-not-checked-against-source` transfers to
  code paths, fails on prose claims (five anchors) — rewrite to name the prose-claim arm.

## Delegated Review

- Delegated Review: executed — one bounded read-only round (angles: false-or-overstated
  claims, stale-fact carryover) via `bounded-reviewer` over this record's draft and its
  evidence files. Verdict: BLOCKERS PRESENT, three, all repaired in place: understated
  pytest numbers (118.3s/109.4s vs the drafted 114s/108s), a "before the budget
  breaches" framing falsified by five over-budget samples in the draft's own cited
  source, and one line calling the lane "green" against the gate section's residual
  continuity failure. Boundary fingerprint verify: `ok: true`, `drift: []`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not
  re-delegated — no slow-gate scope change is recommended by this review.

## Commands Run

- `./scripts/run-quality.sh --read-only`; `python3 scripts/check_docs_graph.py`
  (fail 171 → pass 167 after repair)
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --detail`;
  `.../check_regenerable_facts.py --repo-root .`;
  `.../inventory_skill_ergonomics.py --repo-root . --summary`;
  `./scripts/render_lesson_lifecycle_review.py --repo-root .`
- `python3 scripts/validate_maintainer_setup.py --repo-root .`; `python3 scripts/doctor.py`;
  `./scripts/check-secrets.sh`; `python3 scripts/check_supply_chain.py --repo-root .`;
  `./charness --help`; `./charness doctor --help`; `./charness --version`

## Recommended Next Quality Moves

- active anchor the unanchored lessons at scoring time — capability_needed=decidable
  lesson lifecycle; next_center=ledger anchored-evidence coverage; transformation=require
  an `anchor` field on new score events; proof_boundary=anchored count rising in the
  lifecycle review command; enforcement_posture=advisory.
- active resolve the pytest budget breach — capability_needed=a budget that states the
  truth; next_center=runtime-signals drift visibility; transformation=inspect suite
  overlap first, then relevel 120s with a recorded reason if the width is intentional;
  proof_boundary=no over-budget recent samples; enforcement_posture=advisory.
- active propose graduation for `changed-line-proof-before-broad-quality` via
  `python3 scripts/record_contract_graduation_proposal.py` — capability_needed=order
  enforcement where prose failed twice; next_center=prepush focused-coverage lane;
  transformation=planner-emitted step ordering; proof_boundary=two anchored evidence
  sessions recorded; enforcement_posture=describe-first.
- passive single-source the achieve/handoff goal template family — no-gate because the
  dup baseline already tracks it as an accepted family until a slice owns both skills.

## History

- [Monitored execution primitive and the release lane's silent quality gate](./2026-08-14-quality-review.md)
- [Portable proof-path learning review](./history/2026-07-19-portable-proof-path-learning-review.md)
