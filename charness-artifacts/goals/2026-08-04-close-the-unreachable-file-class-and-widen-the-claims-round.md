# Achieve Goal: Close the unreachable-file class and widen the claims round

Status: complete
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: DONE — all slices complete, pushed, CI green on the pushed SHA.
- Current slice intent: **Arm the decidable axes of the unreachable-file class
  and repair their members.** A–D are complete under this one intent (E landed
  before activation), which is why one two-round bounded critique covers them
  rather than one per slice. The intent changes at F, which is closeout.
- Next action: none for this goal. Two operator decisions wait in
  `## Operator Decision Queue` (close #479? is `bootstrap-resolution.md:175` a
  defect?); neither blocks anything shipped.
- Commits (slices A—D landed as one reviewable bundle, then three closeout
  commits): `39b6139b` (the gates, the 12+6 repairs, the `parents[N]` invariant,
  the sweep, the retro, the claims review), `5aade9b4` (dup-ratchet rotations),
  `6c22cedc` (recent-lessons digest regen), `d0d63eed` (the three branches the
  changed-line lane named, plus its boundary exemption). Pushed
  `d52582db..d0d63eed`.
- **Remote CI verified on `d0d63eed` by a different observer AND a different
  channel than the push exit code** (P4): `gh api
  repos/corca-ai/charness/commits/<sha>/check-runs` reports
  `Core deterministic gates: completed/success` and
  `Changed-line mutation coverage (push/PR mirror): completed/success`;
  `gh run list` independently reports the same run `completed success` (15m5s).
  Note the combined-status API is not the channel to use here — it returns
  `pending`/`total_count: 0` for every commit in this repo because it publishes
  check-runs, and that is not a pending check.
- Landed so far: A1 12→0 (gated by `check_plugin_doc_links.py`), A2 6→0 (gated
  inside `check_doc_links.py`), A3 3 of 4 repaired + 1 deferred with a trigger,
  A4 29 dispositioned as deliberately-not-gated, `parents[N]` invariant pinned
  by a test and the dead-and-wrong eleventh site removed, #479 carries its
  per-instance disposition, #480 filed.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Two items the operator named after the previous run, both structural rather than
repairs.

**A. Close the class #477 and #478 were sub-forms of.** Both issues enumerated
and fixed instances of one thing — *shipped prose asserts a file the reader can
reach, and the reader cannot* — and both sets grew during triage because every
enumeration used a denominator narrower than the class. A bounded causal review
before #478's close found **at least eleven further live instances in one pass**,
filed as [#479](https://github.com/corca-ai/charness/issues/479). Two are the
#477 depth class in the shipped mirror, and `check_doc_links.py` does not scan
`plugins/**` at all, which is why they are green today.

The narrower half of the same item: **ten `parents[3]`/`parents[2]` occurrences
in packaged Python are correct only because the exporter's kind-flattening
cancels the `plugins/<pkg>` prefix** — an arithmetic coincidence invisible at
each call site — and an eleventh (`scripts/skill_runtime_bootstrap.py:103`,
`parents[4]`) is already wrong but unreachable behind a correct ancestor walk.
One change to `export_plugin.py`'s skill-tier layout turns all of them into #477
at once.

**B. Widen the closeout-claims round beyond goal closeout — SETTLED BEFORE
ACTIVATION, and already applied.** The operator chose RELEASE (2026-08-02), and
the trigger is now in `release/references/critique-boundary.md` *Claims Review*
plus the operating contract's surface list. Slice E is complete on arrival; what
remains for this goal is only to prove it fires when a release closeout next
runs, which no slice here forces.

The outcome is that a future enumeration of this class starts from a real zero
rather than a measured-with-the-wrong-ruler zero, and that the claims question
fires wherever a closeout record is produced.

## Non-Goals

- **Not repairing all eleven #479 instances by hand.** The point is the checker
  that makes the class decidable; hand-fixing the current members and leaving
  the denominator alone is what produced three rounds of "0 remaining" already.
- **Not re-litigating `<authoring-repo>/` or `<plugin-dir>/`.** The split shipped
  and works; whether `<plugin-dir>/` ever gets its first user is a separate call.
- **Not rewriting `export_plugin.py`'s layout.** The `parents[N]` item is about
  making the invariant STATED, not about changing what the exporter does.
- **Not adding a claims round to every commit.** The unit is a closeout record,
  not a diff.
- Not the E-cluster, not D41–D49.
## Boundaries

- **External side-effect scope.** Issue CREATION is standing per `AGENTS.md`
  `## External Side Effects` — do not ask. `git push` is standing CONDITIONAL ON
  THE GATES: push when pre-push passes, and never weaken or bypass a gate to get
  there; a refusing gate withdraws the approval. **Closing #479 is NOT covered**
  and needs its own grant, as does any release, tag, version bump, or
  `cautilus evaluate` run.
- In scope: `check_doc_links.py`'s scan surface, the new link/contradiction
  checks, the `parents[N]` family, #479's disposition table, one non-`achieve`
  closeout surface, and the `plugins/` mirror of anything touched.
- Stop conditions: (1) if a new check would refuse a LEGITIMATE reference,
  narrow the rule rather than accepting the false positive — the previous run
  shipped two of those into a blocking gate and had to retract the justification;
  (2) if widening the claims round would fire it per-commit rather than per
  closeout record, cut back to the record; (3) if resolving `parents[N]` starts
  changing what the exporter DOES, stop and treat it as a design change.
- **Cut order if short: D, then C.** (E landed before activation.) B is the one that closes the most
  of the class for the least judgment.
- Legacy note on the seeded rule below: external side-effect scope: name which
  phase or bundle any approved publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- **A checker refuses a relative link that escapes the plugin root**, proven by
  a fixture built from the real defect (`plugins/charness/support/README.md:26`
  resolves to `plugins/scripts/`, which exists in no tree). Running it over the
  current tree names the confirmed instances rather than reporting zero.
- **The `<repo-root>` / `authoring-repo-internal` contradiction is caught
  mechanically** — a line asserting a file is authoring-repo-internal while
  using the consumer prefix is a zero-false-positive rule, and five live sites
  prove it fires. **MET, and the bar itself was superseded during the run: five
  was #479's line-anchored count; the widened sentence-scoped ruler found SIX,
  four of which wrap between the phrase and the prefix.** All six are repaired,
  the rule fires on exactly six, and it has zero false positives over 510 files.
  The criterion is over-met, not missed — recorded here rather than silently
  edited, because a bar quietly rewritten to match the result is the failure
  this goal is about.
- **#479 carries a per-instance disposition**: fixed, or recorded with a reason.
  A reader can tell a decision from an omission.
- **The `parents[N]` invariant is either stated in code or documented with its
  revisit trigger**, and the already-wrong eleventh site is resolved either way.
- **The claims round fires at one closeout surface beyond `achieve` goals**, with
  the trigger written where that surface's contract lives — not in prose someone
  has to remember.
- **Every figure carries `<value> — <source>`**, with its denominator and when
  it was taken.
- **Non-claim in writing**: a static checker proves a path does not RESOLVE for
  a consumer. It does not prove the target would fail at runtime, and it does
  not prove the class is exhausted — only that the ruler got wider.

## Agent Verification Plan

### Low-Cost Checks

- **Re-run the sweep BEFORE building anything**, and record the count with its
  date. #479's list was taken 2026-08-02 and the tree has moved since.
- **Widen the denominator before claiming a zero.** Every prior pass reported
  "0 remaining" honestly and was wrong because its ruler was narrower than the
  class: `.py`-only, `scripts/`-only, command-only, `skills/`-only. State the
  ruler next to the count, every time.
- Sync `plugins/` mirrors before validators (`mutate -> sync -> verify`).
- Obey the dup-ratchet edit advisory when it fires, and re-run it after any
  REFACTOR of an already-classified file — fingerprints rotate.
- A new checker owes a fixture built from a REAL confirmed instance, not an
  invented one; the real ones are listed in #479.
### High-Confidence Checks

- **TWO bounded rounds for any slice that changes verdict logic**, round 2
  reading the repairs. Measured five times now, and the last was the sharpest:
  the fix for "a documented command that cannot run" shipped three new ones.
- **A closeout-claims review by a distinct observer** before the completion flip.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the
  MOMENT the reviewer returns, before any parent write.
- **A new checker must be proven to BITE**, by reintroducing a real defect and
  watching it refuse — not by passing on a clean tree.
- Build test inputs from source constants, never by retyping.
### External Or Live Proof

- `git push` to `main` and its CI — standing per `AGENTS.md` **conditional on the
  gates**; a refusing gate withdraws the approval, and never weaken one to reach
  a green push.
- Remote CI confirmed by a different observer AND a different channel than the
  push exit code. The combined-status API returns `pending`/`total_count: 0` for
  every commit here because this repo publishes check-runs; that is not a
  pending check.
- Closing #479 is NOT covered: issue close is per-goal and needs its own grant.
- Explicitly not in this plan: any release publish, tag, version bump, or
  `cautilus evaluate` run.
## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Re-run the sweep with the widened ruler and restate #479's count with its denominator and date | Every prior pass reported an honest zero with a narrow ruler; starting from a stale list would repeat that exactly | A dated count per axis, and the ruler stated beside it | complete |
| B | A checker that refuses a relative link escaping the plugin root, fixture-built from the real `support/README.md` defect | One check, no judgment calls, covers the majority of #479's confirmed instances — and `check_doc_links` does not scan `plugins/**` at all today | The checker refusing the real defect, a test proving it bites, and the confirmed instances named | complete |
| C | Catch the `authoring-repo-internal` + `<repo-root>/` contradiction, and disposition the remaining #479 instances | A line that says a file is authoring-repo-internal while using the consumer prefix is zero-false-positive; five live sites prove it | The rule firing on all five, plus a per-instance disposition table for what it does not cover | complete |
| D | Resolve the `parents[N]` invariant: state it in code or document it with its revisit trigger, and fix the already-wrong eleventh site | Ten sites correct by coincidence is one exporter change from eleven instances of #477 at once | The helper or the documented invariant, and `skill_runtime_bootstrap.py:103` resolved | complete |
| E | DONE BEFORE ACTIVATION — the operator chose RELEASE, and it is recorded in `release/references/critique-boundary.md` *Claims Review* plus the operating contract's surface list | It found five record blockers four code rounds missed, on its first outing; a release record reaches readers outside the session with the least chance of later correction | The trigger in that surface's own contract, not in prose | complete |
| F | Closeout: bundle gate, final verification, claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green | complete |

## Operator Decision Queue

- Decision: close #479, or leave it open on its disposition comment
- Owner: operator
- Why deferred: closing an issue is a standing approval CONDITIONAL ON THE
  CLOSEOUT FLOOR, and this goal's own `## Boundaries` puts #479's close
  explicitly out of scope pending a per-goal grant. The work did not stop
  because the disposition comment is the deliverable the acceptance criteria
  named; the close is a separate call.
- Unblock action: grant the close, and if granted the closeout floor still
  applies (`validate-closeout-draft`, a delegated resolution critique, the
  classification ledger, a `Behavior #N:` verdict on a channel distinct from
  the fix, and `verify-closeout --expect-state CLOSED`)
- Revisit trigger: the next session that picks up this class, or an operator
  reading the disposition comment

- Decision: whether `<repo-root>/skills/support/` in
  `skills/shared/references/bootstrap-resolution.md:175` is a defect
- Owner: operator
- Why deferred: it describes where a consuming repo's support tree lives in a
  split-monorepo layout, so `<repo-root>/` may be correct as written. Deciding
  it requires the open D50 call on whether `<plugin-dir>/` gets a real user,
  which this goal's non-goals put out of scope.
- Unblock action: resolve D50 either way
- Revisit trigger: D50 resolving

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

Routing: achieve — owns the goal lifecycle; slices routed to impl for the gate/test work, quality for the validation-posture and dup-ratchet calls, critique for the two bounded rounds, and issue for #479's disposition and #480's filing
Gather: n/a — every ## Context Sources entry is a repo-local artifact or a GitHub issue in this repo's own tracker, read through gh; no external page or document needed to become a durable local asset
Issue closeout: n/a — #479 is context and carries a per-instance disposition comment (issuecomment-5158882377), but closing it is explicitly OUT OF SCOPE per ## Boundaries and needs its own operator grant; #480 was FILED this run, not closed
Release: n/a — no version bump, no install-manifest edit, and no publish surface was touched; the quality-core.yml step added is CI config, not a release surface

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED 2026-08-02 — the operator named both items
  after the previous run and asked for them to be shaped as a goal for the next
  session. External side effects are already settled by the standing approvals
  in `AGENTS.md` (issue creation unconditional, push conditional on the gates),
  so the only per-goal grant this run might need is closing #479, which is
  explicitly out of scope until asked. Nothing else here is consequential: no
  release surface, no live proof, no issue close, and the one proof-level
  non-claim (a static checker proves non-resolution, not runtime failure) is
  recorded in `## User Acceptance`.
- **This goal is ready to run.**

## Slice Log

### Slice 1: A — restate the count with its ruler

- Objective: Re-run the sweep before building anything, and state the denominator beside every count.
- Why this approach: Three prior passes reported an honest '0 remaining' with a ruler narrower than the class; starting from #479's stale list would repeat that exactly.
- Commits: 39b6139b
- What changed: charness-artifacts/audit/2026-08-04-unreachable-file-denominator-sweep.md (new)
- Alternatives rejected: Hand-repairing #479's listed instances first — feels faster and rebuilds the same false zero.
- Targeted verification: Four axes swept over 510 markdown files, dated 2026-08-04. A1 12 (vs #479's 11); A2 6 source + 6 mirror (vs 5 — #479's ruler was line-anchored and 4 of 6 wrap between the phrase and the prefix); A3 4 (agreement); A4 30 candidates, judgment-bearing. check_doc_links.py's DOC_GLOBS excludes plugins/** entirely: 236 of 510 files (46%) scanned by no link gate.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward: A line-anchored ruler cannot report that it is line-anchored — it under-reported A2 by 3x on the first pass of this very goal.
- Metrics:

### Slice 2: B — arm the plugin-mirror link gate

- Objective: A blocking checker that refuses a relative link a consumer cannot follow, fixture-built from the real defects, plus repair of all 12 instances.
- Why this approach: One check, no judgment calls, covering the majority of #479's confirmed set — and check_doc_links does not scan plugins/** at all.
- Commits: 39b6139b
- What changed: NEW scripts/check_plugin_doc_links.py; NEW tests/quality_gates/test_check_plugin_doc_links.py (16 tests — 14 at the time of the bounded rounds, plus 2 added afterwards when the gate was made to report what it skipped); shared link vocabulary extracted into scripts/markdown_doc_scan.py; check_doc_links.py rewired onto it; run-quality.sh, staged_commit_gate_plan.py, .github/workflows/quality-core.yml, docs/conventions/validator-timing-layers.md; 12 repairs in skills/shared/references/* and skills/support/README.md; dup-review.json (5 families classified intentional); plugins/ mirror
- Alternatives rejected: Widening check_doc_links's DOC_GLOBS to plugins/** — rejected: its other three checks would fire en masse on the mirror. Extending the portable-package link rule to skills/shared — rejected: it measures at the authoring position and cannot see exporter layout transforms like kind-flattening.
- Targeted verification: Gate names all 12 live instances; 12 -> 0 after repair. Bite proven on the LIVE tree by reintroducing plugins/charness/support/README.md's real defect (exit 1) and restoring (exit 0). Parity of the check_doc_links rewire: 27 hand-built edge inputs + every link in the live corpus = 873 links, 0 divergences vs git show HEAD. iter_doc_lines parity: 2802 repo-owned docs, 0 walk changes. run_slice_closeout --skip-broad-pytest completed; dup ratchet clean.
- Test duplication pressure: check_dup_ratchet: clean after extracting the real duplication (classify_link vs validate_link) into markdown_doc_scan; 5 remaining families classified intentional with reasons (script skeleton / entrypoint block / portability preamble, each with 2-14 members, most untouched). Fingerprints rotated twice mid-slice, once after removing an unused import.
- Critique: TWO bounded rounds, both fresh-eye, boundary fingerprint clean around each. Round 1: 1 blocker (the slice deleted check_doc_links.LINK_RE, which check_doc_authoring_preflight.py imported — broad suite was red, and --skip-broad-pytest is why it escaped) + 6 lower findings; all fixed. Round 2 read the repairs and found 3 NEW holes my own repair introduced: per-line scanning missed prose-wrapped links, the fence toggle inverted on mismatched ~~~/backtick markers, and live text after a mid-line --> was dropped. All three reproduced empirically (3/3 predicted exit 0, correct was exit 1), fixed, and pinned by tests.
- Off-goal findings: Filed issue #480 — <authoring-repo>/ is verified only for scripts/ targets, so the docs/ and charness-artifacts/ forms this slice created are checked by nothing.
- Lessons carried forward: The round that reads the REPAIRS is where the class comes back — measured a sixth time, and this time the repair for a false-positive hole opened three false-negative ones. Also: a background test run reported 'exit code 0' while the output showed 10 failures; read the output, not the notification.
- Metrics:

### Slice 3: C — the contradiction rule and #479's disposition table

- Objective: Catch the authoring-repo-internal + <repo-root>/ contradiction mechanically, and give #479 a per-instance disposition.
- Why this approach: A sentence asserting both is self-contradicting whichever half is right, so the verdict needs no judgment — and five live sites proved it fires.
- Commits: 39b6139b
- What changed: iter_authoring_repo_contradictions + iter_prose_blocks + split_block_into_sentences in scripts/check_doc_links.py; 6 tests appended to tests/quality_gates/test_check_doc_links.py; 6 A2 repairs across achieve/critique/handoff/issue references; 2 A3 repairs in skills/shared/references/; #479 disposition comment; plugins/ mirror
- Alternatives rejected: Line-scoped — rejected, it reported 2 of 6. Paragraph-scoped — rejected, it glued two independent bullets in spill-targets.md into a fabricated contradiction. Settled on sentence-within-block: blank lines and list markers end a block.
- Targeted verification: Rule fires on exactly 6 sites, matching the sweep, zero false positives over 510 files. 6 -> 0 after repair. Bite proven on the LIVE tree by reintroducing rename-critique.md:96 (refused, naming line 96) and restoring. A3: 3 of 4 repaired (one was also an A2 instance); the 4th deferred with a named revisit trigger (needs the open D50 call on <plugin-dir>/). A4: 29 sites, all naming a real repo script, deliberately NOT gated — a bare scripts/... in a portable doc may legitimately mean the consumer's own tree, and gating it would ship the false positive the previous run had to retract.
- Test duplication pressure:
- Critique: Covered by the same two bounded rounds as slice B (one unchanged slice intent: arm the decidable axes of one class).
- Off-goal findings:
- Lessons carried forward: The zero-false-positive claim is only as good as the scope boundary: sentence-scoped was right, and the bullet-list case showed paragraph-scoped would have manufactured one.
- Metrics:

### Slice 4: D — the parents[N] invariant

- Objective: State the cancellation invariant executably and resolve the already-wrong eleventh site.
- Why this approach: Ten sites correct only by an arithmetic coincidence are one exporter change from eleven #477 instances at once, and nothing at any call site says so.
- Commits: 39b6139b
- What changed: scripts/skill_runtime_bootstrap.py (parents[4] fallback removed, explicit RuntimeError); NEW tests/quality_gates/test_parents_index_layout_invariant.py (6 tests); docs/conventions/implementation-discipline.md revisit trigger; plugins/ mirror
- Alternatives rejected: A shared plugin_or_repo_root() helper touching ten call sites — rejected as its own slice, per the goal's interview decision. Documentation alone — rejected: a comment does not go red when the exporter's layout changes.
- Targeted verification: Measured that the fallback is DEAD (ancestor walk succeeds for every skill script in both trees, 0 failures) and WRONG (in the mirror parents[4] is plugins/, one level above the plugins/charness the walk correctly returns). Tests bite: reintroducing the fallback fails 2 of 6. Population guard included so the sweep cannot pass on an empty set.
- Test duplication pressure: 6 new tests in a new file; dup ratchet clean.
- Critique: The first version of the AST test grepped the function source and went red on its own docstring explaining the removal — a proxy passing for the thing, caught and rewritten to walk the AST.
- Off-goal findings:
- Lessons carried forward: 'Assert the thing, not a proxy' recurred inside a test written to enforce exactly that discipline.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design-north-star.md](../../docs/design-north-star.md) — P5 governs the new
   checks: teeth only where a wrong answer escapes, and the previous run's
   retracted "false positives are impossible" claim is the cautionary case.
2. [issue #479](https://github.com/corca-ai/charness/issues/479) — the eleven
   confirmed instances, the denominator story, and the cheapest-first direction.
3. [the #478 resolution critique](../critique/2026-08-02-issue-478-resolution.md)
   — where the class-vs-sites distinction and the prevention-scope trace come
   from. Read before assuming the existing gate covers this.
4. [the completed goal](./2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md)
   and its [retro](../retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md)
   — the `parents[N]` revisit trigger, and the claims round's first outing.
5. [operating-contract.md](../../docs/conventions/operating-contract.md)
   *Critique Discipline* — owns the claims round that slice E widens.
6. [authoring-preflight.md](../../docs/conventions/authoring-preflight.md)
   — the placeholder vocabulary the new checks decide against.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

1. **Fix the eleven, or fix the ruler?** Family considered: {hand-repair the
   confirmed instances; build the checks and let them name the set; both; defer}.
   **Chosen: the ruler first, repairs as its output.** Three passes have now
   reported an honest "0 remaining" with a ruler narrower than the class, so
   hand-repairing the current members reproduces exactly that. Rejected:
   hand-repair-first, which feels faster and rebuilds the same false zero.
   Anti-anchoring: `axis: a clean count is evidence about the ruler, not the
   tree`.
2. **How much should the claims round widen?** Family considered: {every commit;
   every closeout record; PR only; leave it at `achieve` goals}. **Chosen: one
   closeout surface beyond goals, chosen during the run.** Per-commit would make
   it ceremony, which is how a floor becomes token theatre. Rejected: leaving it
   alone — it found five blockers on one outing, and PR/release closeouts are
   read by people outside the session. Anti-anchoring: `axis: a step that pays
   once is not a step that pays everywhere`.
3. **`parents[N]`: helper, or documentation?** Family considered: {a shared
   `plugin_or_repo_root()`; document the invariant with a revisit trigger; fix
   only the already-wrong site; nothing}. **Chosen: decide in-goal, with the
   already-wrong site fixed either way.** Ten correct-by-coincidence sites are
   not urgent, and a helper touching ten call sites is its own slice; but
   `skill_runtime_bootstrap.py:103` is wrong today and is cheap. Anti-anchoring:
   `axis: fragile-but-correct and quietly-wrong deserve different urgency`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Plan critique ran BEFORE activation (2026-08-02) and its output is already folded
into `## Boundaries` (the three stop conditions), `## Agent Verification Plan`
(two bounded rounds for verdict-logic slices; a checker must be proven to BITE by
reintroducing a real defect, not by passing on a clean tree), and
`## Interview Decisions`. No plan-level critique was re-run during the run
because the slice intent never changed; the three IN-RUN critique rounds are
recorded in `## Slice Log` and `## Final Verification` instead.

Reviewer provenance for the in-run rounds — all three delegated to bounded
read-only fresh-eye subagents, with `reviewer_boundary_fingerprint.py`
snapshot/verify around each (`clean`, no drift, all three):

1. Code round 1 on the slice B/C surface — 1 blocker + 6 lower findings.
2. Code round 2 reading the REPAIRS — 3 new holes the round-1 repair opened.
3. Closeout claims round on the RECORD — 11 findings, 3 of them record
   blockers, all folded before the completion flip. Its most damaging catch: this
   goal's own measurement artifact still said axis A2 was NOT ARMED after slice C
   had armed it and repaired all 12 sites — the anti-narrow-claim table having
   gone stale in the opposite direction.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- **[#480](https://github.com/corca-ai/charness/issues/480) FILED** — `<authoring-repo>/`
  is verified only for `scripts/` targets. `AUTHORING_REPO_SCRIPT_RE` in
  `inventory_skill_script_references.py` is `scripts/`-anchored, so the `docs/`
  and `charness-artifacts/` forms this goal's own A1 repairs created are resolved
  by nothing. Surfaced by the round-2 bounded reviewer, filed under the standing
  issue-creation approval, and referenced from the comment block in
  `scripts/check_doc_links.py` so the disclosure points at a record.
- **Deferred, not filed:** `skills/shared/references/bootstrap-resolution.md:175`
  (`<repo-root>/skills/support/`). It may be correct as written; deciding needs
  the open D50 call on `<plugin-dir>/`. Carried in `## Operator Decision Queue`
  with an owner and a revisit trigger rather than filed, because there is no
  observed defect to report yet — only an undecidable reading.
- **Deferred, not filed:** a gate that would refuse deleting a module-level name
  another repo module imports. Round 1's blocker was exactly that shape, and the
  round-2 sweep that confirmed no other consumer broke was a human sweep, not a
  gate. Recorded in the retro's `## Sibling Search`; not filed because the
  recurrence is one instance and Floor-Addition Restraint asks for more.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md
Host log probe: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round-claims-review.md

Fresh-eye pass: scripts/check_plugin_doc_links.py — TWO bounded read-only rounds
against the proof-surface classes. Round 1 found a blocker outside the file (the
slice deleted `check_doc_links.LINK_RE`, which `check_doc_authoring_preflight.py`
imported — class (d), a check that silently did not run) plus SIX lower
findings (a closeout claims review caught this line saying five while the slice
log said six; six is correct). Round 2 read the repairs and found THREE class-(d)/(g) holes the round-1
repair had opened: per-line scanning missed prose-wrapped links, a parity fence
toggle inverted on mismatched `~~~`/backtick markers leaving the document tail
falsely fenced, and live text after a mid-line `-->` was dropped. All three were
reproduced empirically (3/3 predicted PASS where refusal was correct), fixed, and
pinned by tests. Class (f) addressed after the reviews: the gate now COUNTS and
reports what it skipped, so a green run cannot read as full coverage.
Fresh-eye pass: scripts/markdown_doc_scan.py — covered by the same two rounds;
round 2's fence and HTML-comment findings live in this file and were fixed here.
Parity re-proven after the change: 2802 repo-owned docs, 0 walk differences.
Fresh-eye pass: tests/quality_gates/test_parents_index_layout_invariant.py — not a
proof surface about other code's correctness; it pins a layout invariant. Its own
first version did hit the proxy trap (it grepped source text and matched its own
docstring) and was rewritten to assert against the AST.

Broad proof: `pytest tests/quality_gates/ tests/test_doc_authoring_preflight.py
tests/test_skill_script_references.py` — **4591 passed, 0 failed** (332s), read
from the run's output file rather than its completion summary, because two
completion summaries this run reported `exit code 0` over runs that had 10 and 4
failures.

## User Verification Instructions

1. **Confirm the two new rules bite, rather than trusting a green tree.**
   Reintroduce either real defect, watch the gate refuse, then restore:
   - `plugins/charness/support/README.md` — change the backticked
     `<authoring-repo>/scripts/sync_support.py` back to a markdown link
     `](../../scripts/sync_support.py)`, then run
     `python3 scripts/check_plugin_doc_links.py --repo-root .` (expect exit 1).
   - `skills/public/critique/references/rename-critique.md` — change
     `<authoring-repo>/docs/design-north-star.md` back to `<repo-root>/...`,
     then run `python3 scripts/check_doc_links.py --repo-root .` (expect exit 1,
     naming line 96).
2. **Read what the gate says it did NOT judge.**
   `python3 scripts/check_plugin_doc_links.py --repo-root .` prints a `skipped:`
   clause on success. A green run that skipped a lot is not the same as one that
   skipped nothing, and the output now says which.
3. **Re-derive the counts** from
   [the sweep](../audit/2026-08-04-unreachable-file-denominator-sweep.md); every
   axis states its ruler, its date, and why it differs from #479's figure.
4. **Read [#479's disposition comment](https://github.com/corca-ai/charness/issues/479)**
   and check that each axis reads as a decision rather than an omission. #479 is
   deliberately still OPEN — closing it is out of scope and needs a grant.
5. **Two operator decisions are waiting** in `## Operator Decision Queue`:
   whether to close #479, and whether `bootstrap-resolution.md:175` is a defect
   (needs the open D50 call).

## Auto-Retro

Retro dispositions: applied: `scripts/check_plugin_doc_links.py` now COUNTS and prints what it skipped on both the pass and the refusal path, declared in `attention-state-visibility.json` and pinned by two tests — a green run can no longer read as full coverage, which is the failure the whole class came from
Retro dispositions: applied: the goal's `## Final Verification` cites the 4591-passed figure with an explicit note that it was read from the run's OUTPUT file, after two separate background runs reported `exit code 0` over runs carrying 10 and 4 failures
Retro dispositions: applied: the retro records that four of those failures were self-inflicted by running a generated-surface sync while the background suite was reading the tree, with the isolation rerun that proved them phantom — so the next session recognises the shape instead of chasing it
Retro dispositions: applied: `tests/quality_gates/test_parents_index_layout_invariant.py` turns the exporter cancellation from a comment into an executable claim with a stated revisit trigger, and `scripts/skill_runtime_bootstrap.py`'s dead-and-wrong `parents[4]` fallback is replaced by an explicit refusal
Retro dispositions: applied: the shared link vocabulary in `scripts/markdown_doc_scan.py` means the two link gates cannot disagree about what a link IS, which is what let the same defect be green in one tree and broken in the other
Retro dispositions: issue #480 (novel: the unreachable-file class this goal closed is about references that do not RESOLVE; #480 is about references that resolve today but are VERIFIED by nothing, which no existing issue covers — #477/#478/#479 are all resolution-failure issues, so this is a sibling axis rather than a re-file of that class): `<authoring-repo>/` is resolved only for `scripts/` targets, so the `docs/` and `charness-artifacts/` forms this goal's own repairs created are verified by nothing; the sibling "refuse deleting a module-level name another module imports" guard — round 1's blocker shape — is recorded on the same issue rather than opening a second thin one
Retro dispositions: accepted-risk: both link gates keep a staged-`.md` commit trigger that does not scope them — a link verdict also flips when the TARGET is renamed, staging no `.md` at all. Recorded in `validator-timing-layers.md` with the counterexample worked through, and compensated by the broad gate plus a new `quality-core.yml` step, rather than widened unilaterally for one gate
Retro dispositions: out-of-scope: axis A4's 29 sites stay ungated by design — a bare `scripts/...` in a portable doc may legitimately mean the consumer's own tree, so gating it would ship the false positive the previous run had to retract. Dispositioned as a measured population on #479 instead

Structural follow-up: applied: `tests/quality_gates/test_check_plugin_doc_links.py` and `tests/quality_gates/test_parents_index_layout_invariant.py` — the retro's `## Sibling Search` names "a gate whose commit-time trigger does not scope its verdict" and "a module-level name deleted out from under a consumer" as the transferable classes; the first is recorded in the timing table with its counterexample, and the second is tracked on issue #480.
