# Achieve Lifecycle — After

Part of achieve's three-phase lifecycle contract; see `lifecycle.md` for
the overview and `lifecycle-before.md` / `lifecycle-during.md` for the rest.

## After

### Closeout preflight (describe-first)

Before drafting the closeout sections (`## Auto-Retro`, `## Final Verification`,
and the `## Coordination Cues` evidence lines), get the full required-evidence
shape for *this* goal in one pass instead of discovering it by failing the
`complete` flip one rejection at a time:

- run the skill-local `describe_goal_closeout_shape.py --goal-path <artifact>`:
  it reads *this* goal and emits the goal-conditional missing-line set — only the
  floors this goal triggers (including the runtime-conditional `keep` floors a
  static catalog cannot name: disposition rungs 1a/1b/1e, the section-placeholder
  floor, closeout-delegation, timebox) and which are still unmet — then appends
  the enforced FORMS (skip-reason enum, goal-slug binding, disposition and
  `Routing:` / `Gather:` / `Release:` / `Issue closeout:` forms) for filling them,
  rendered live from `check_goal_artifact.py`'s constants. Use the skill-local
  script, not the authoring-repo `scripts/check_artifact_surface_preflight.py`
  dispatcher, so the step stays portable to a consumer repo.

Fill every surfaced line once, then verify once with `check_goal_artifact.py`
(still the authoritative complete-flip gate; the describe is an authoring
affordance, never a precondition). This is the commit-gate *aggregate, don't
fix-one-rejection-at-a-time* principle (the `mutate → sync → verify → publish`
rule earlier in this file, where a rejected commit gate triggers the aggregate
rather than serial single-gate fixes) applied to the closeout-evidence gate —
`achieve`'s own most-repeated authoring-churn source. The `--goal-path` mode (A2)
folds the previously-separate dry `check_goal_artifact.py` preview into the one
describe call by reusing the live `check_complete_evidence` + timebox reports.
Honest scope: the proof-mismatch and mutable-HEAD floors stay the flip gate's
job, outside the describe view, so `check_goal_artifact.py` is still the verify.

At completion the goal artifact should contain:

- final self-verification against the original goal
- final quality gate results, including the full broad duplicate/length/pressure
  gate when the run added or expanded tests; if that gate fails, classify the
  failure as new-slice-local (introduced by this run's slices) or
  accumulated-suite debt (pre-existing pressure the run pushed past threshold),
  and name the smallest next structural cleanup rather than only reporting the
  failing percentage
- high-confidence or high-cost verification results, or an explicit statement
  that they were not run
- residual risks and non-claims
- concrete user verification instructions
- user-decision-needed items that are truly unresolved for this goal. Do not
  include routine publication/push prompts by default; `achieve` already names
  publication and remote-closeout non-claims separately, and repeating a known
  operator surface is noise unless the user asked for that decision.
- when the goal resolved a tracked issue: its close is *staged* through `issue`
  — the default-branch commit/PR body carries `Close #N` so the maintainer's
  push auto-closes it (it is still OPEN at `achieve` closeout); `achieve` does
  not push or close out-of-band (see `references/coordination.md` *Resolving A
  Tracked Issue*)
- issue-resolution carrier publication and lifecycle/audit artifact
  publication are separate surfaces. After the carrier is pushed and GitHub
  state is verified, later goal, retro, or handoff updates are lifecycle
  artifacts unless they are required by the carrier itself; do not force a
  second docs-only issue-closeout push for them.
- an automatic retro focused on reducing time, tokens, and waste next time, and
  a closeout report that names the actual waste from this run instead of only
  summarizing implementation changes
- for timeboxed goals that stop before the reserve window, a user-facing early
  close report with three explicit sections: why early closeout was chosen, what
  decisions now need the user, and what waste/retro findings explain the gap.
  A final message that only says "No safe next slice" is incomplete because the
  user still needs the decision and waste context.
- the resolved `achieve` adapter policy for closeout publication and Auto-Retro
  disposition. Missing adapters default to `audit-only`; found invalid adapters
  block completion. The adapter, not host-loaded memory, owns whether the normal
  closeout default is `audit-only`, `handoff-only`, or a publish-capable carrier,
  and it binds direct-commit issue closeout to the `issue` skill's
  `validate-closeout-draft --carrier direct-commit --commit-message-file`
  rehearsal contract.
- an efficiency summary when host evidence exists: measured signals (for
  example elapsed time, token snapshots, compactions, tool-call counts, or
  subagent count), proxy signals (for example repeated VCS/check commands,
  polling, and high-output reads), unavailable signals, and which costs were
  necessary safety cost versus reducible waste. Cached input alone is not a
  waste conclusion.
- for long goals with available timestamps, a `Host metric window:` evidence
  line (`started_at=<ISO> completed_at=<ISO>` plus exactly one of
  `codex_session_file=<path>` / `claude_session_file=<path>`) and a host probe
  produced with `probe_host_logs.py --goal-path <artifact>`, so the closeout
  can separate goal-window signals from thread-wide pressure.
- a closeout narration that surfaces the retro's `## Waste`,
  `## Critical Decisions`, `## Next Improvements`, and `## Sibling Search`
  (when present) sections inline in the user-facing response — the retro
  file is the durable copy, the user-facing message is the transport.
  "Persisted at `<path>`" alone repeats the closeout-transport failure pattern.
  The After-phase evidence gate now surfaces a `narration_required_sections`
  list naming exactly which of these sections the cited retro contains —
  narrate each one inline.
  Narration itself stays a prose contract (a hard transcript gate would
  over-fire); the list is the affordance, not a blocker.
- an `Operator Decision Queue:` line in the user-facing final report, with each
  queued operator-only decision or `none — <reason>`. Decision-needed items must
  not be collapsed into generic residual-risk prose.

Run `check_goal_artifact.py` before declaring completion so the required
sections, status, and activation line are all present. Flip the status to
`complete` only after the final report separates what was proven from what
remains the user's responsibility to verify.

For timebox mode, `upsert_goal.py --status complete` and
`check_goal_artifact.py` enforce the closeout boundary. A goal with
`Done-early policy: continue_next_improvement` cannot flip to `complete` before
`Activation time + Timebox - Closeout reserve` unless the artifact records a
valid early-close reason, at least two `Next slice candidate:` ledger lines, and
a valid `Outcome sufficiency check:` line under `## Final Verification`. This
catches the failure mode where the agent declares the macro target done early
and ignores the user's time budget or closes with low yield without saying so.
When such an early-close reason is recorded, the After-phase evidence gate also
requires `Early close report: <path>` so the closeout cannot pass without a
report for the user.

Mutable `HEAD` claims are live-state claims, not durable proof by themselves.
When a goal artifact says `current HEAD`, `HEAD is`, or equivalent and also
names an immutable SHA, `check_goal_artifact.py` compares that SHA to local
`git rev-parse HEAD`. If the SHA is intentionally historical, say so on the
same line; otherwise prefer recording the executed command with `--head-sha HEAD`
plus the current `git log origin/main..HEAD` context.

Host-level goal completion is downstream of the artifact, never a substitute
for it. Before calling a host status tool such as `update_goal(status=complete)`,
the checked-in goal artifact must already read `Status: complete` and
`check_goal_artifact.py --goal-path <artifact>` must pass. If the host tool and
the artifact disagree, the artifact is the source of truth and the closeout is
not complete.

### Post-Checkpoint Commit Classification

When a goal includes a live apply, restart, deployment smoke, or other
behavioral checkpoint before the final commit, the After-phase closeout must
make `HEAD != live` legible instead of forcing a blind re-apply. Record:

- the live checkpoint source hash or artifact that was actually applied/smoked;
- the current `HEAD`;
- each commit after the checkpoint classified as `runtime-affecting`,
  `test-only`, or `audit-doc-only`.

Classify conservatively. Code, config, prompt, generated runtime surfaces, and
spec changes are `runtime-affecting`. Tests and CI harness changes are
`test-only` when they cannot affect live behavior. Goal logs, retros, probes,
handoff updates, and proof artifacts are `audit-doc-only`. Any uncertain commit is
`runtime-affecting`. The final user-facing report can then say which
post-checkpoint commits require re-apply consideration and which only explain
why the repository `HEAD` differs from the live instance.

### Improvement disposition

The retro's value is realized only if its improvements change something. The
loop has three rungs — capture (the retro artifact + `recent-lessons.md`
digest), surface (the digest is a pull surface other sessions are told to
read), and apply — and only the first two are automatic. Application does not
happen on its own: a prose `Next Improvement` left in the retro decays out of
the digest (recency half-life + slot limits) and is, in practice, lost unless a
later session both reads it and chooses to act.

So the After-phase must **close the loop, not widen it**. At closeout, give
every improvement the retro or the run surfaced an explicit disposition — one
of exactly two:

- **applied-in-session**: converted to *teeth* this run — a gate, hook,
  validator, test, or code/contract change — and committed. Teeth self-apply on
  the next run; prose does not. Prefer this when the improvement is small enough
  to land now or names a recurrence a future session would otherwise repeat.
- **filed-as-issue**: a tracked `issue` (via the `issue` skill / adapter
  backend) so the next session picks it up from the live backlog the handoff
  chunker reasons over. Prefer this when the improvement is real but larger than
  the current goal's scope, or needs its own design.

Which of the two — apply now vs file for next session — is the **agent's
judgment**, weighing the improvement's size against the current goal's scope.
What is **not** optional: leaving an improvement as prose-only retro memory is
not a valid disposition. Record each improvement's outcome in the Auto-Retro
section as `applied: <what landed>` or `issue #N`, so a fresh session can audit
that the loop was closed. (This rule is itself the applied form of the lesson
that `achieve` captured improvements but never closed the apply rung.)

The two forms above are **per-improvement**: each improvement that exists is
applied or filed. A goal may instead assert, once, that *no actionable
improvement exists to disposition* — an explicit
`Retro dispositions: none — <reason>` line inside `## Auto-Retro` (≥30 chars,
mirroring the skip discipline). This is a **per-goal** assertion at a different
scope, not a third escape box: it is a factual claim the fresh-eye reviewer can
**falsify** (it reads the retro and contradicts a false "none"). Use it only
when the retro genuinely surfaced nothing to act on.

### Disposition Gate - Two Rungs

The disposition rule above earns teeth from two complementary rungs, each doing
only what it is good at (the gate-and-intelligence split). A deterministic
false-positive is worse than a false-negative — it trains token-theater — so the
deterministic teeth stay narrow and ungameable, and the substantive judgment is
made by an agent and recorded for a human, never by a regex.

- **Rung 1 — deterministic floor** (in `goal_artifact_disposition.py`, run by the
  After-phase evidence gate). Two ungameable, offline, clone-safe checks:
  - *block-the-blank*: refuse the `complete` flip when the cited retro lists
    actionable `## Next Improvements` but the goal's `## Auto-Retro` is blank and
    no opt-out is recorded. Emptiness only — it never classifies prose.
  - *review-ran evidence*: require a bound `Disposition review:` line (below).
    This is **presence/binding-only by design**: it proves a fresh-eye review
    *ran* and binds to this goal; it never inspects the review's content. A
    future maintainer must not tighten it into a content classifier — that
    re-imports the prose word-list trap one level up.
  - *recurrence-lineage*: an `issue #N` disposition in `## Auto-Retro` must carry
    a recurrence-lineage marker (`recurs:`/`recurrence:`/`lineage:`/`novel:` +
    non-empty), so a re-file of a known recurring class cannot silently launder as
    a fresh narrow issue. **Presence/enum only** — the floor checks the marker is
    present, never whether a `novel:` claim is *true* (that is rung 2's call). It is
    required uniformly on every issue-routed disposition (deciding *which* issues
    "look recurring" would itself be the classifier the guardrail forbids); some
    rote `novel:` is the accepted cost. Same grandfather-by-`Created`-date shape as
    the other rungs.
  - *structural-follow-up destination*: when the cited retro names a *transferable*
    waste item (a `## Sibling Search` trigger), `## Auto-Retro` must carry a
    `Structural follow-up:` line whose value is one of four destinations —
    `applied: <gate/hook/validator/test/contract change>` /
    `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` /
    `none — <reason>` — so "recorded in recent-lessons" can no longer be mistaken
    for a structural fix. The vocabulary's single source is
    `../../../shared/references/retro-issue-destination-split.md` (shared with the
    retro waste-sibling-scan so the two never drift). **Presence/form-enum only** — the floor checks a valid
    destination line is present, never whether the chosen destination is the right
    one (that is rung 2's call). Inert unless transferable waste is named (no
    over-fire); same grandfather-by-`Created`-date shape as the other rungs.
- **Rung 2 — the fresh-eye disposition review** (the intelligence). The
  After-phase already mandates a bounded fresh-eye closeout review; this gives
  that reviewer an added mandate: read the cited retro's `## Next Improvements`
  and the goal's `## Auto-Retro`, and record a **per-improvement verdict** —
  for each improvement, dispositioned (`applied:` / `issue <id>` / explicit-none)
  or undispositioned — into a review artifact the `Disposition review:` line
  binds. This is the substantive call a regex cannot make (polarity, "filed" vs
  "not filed", narration-vs-action). It is **non-deterministic by nature** — made
  visible and auditable for a human, not a hidden pass — and near-zero marginal
  cost because it scopes an already-required review rather than adding an agent.
  The reviewer's three substantive mandates — falsifying `novel:` recurrence-
  lineage claims, classifying the structural-follow-up destination, and (at an
  issue-bundle closeout) confirming each closed issue's behavior through an
  evidence channel distinct from the bundle-level readback — are the
  reviewer-facing brief at
  `../../../shared/references/disposition-reviewer-brief.md`; hand the reviewer
  that brief, not this mega-reference.

**Honest limit.** The deterministic floor proves the *process* ran (a review
exists and binds) and catches the unambiguous *blank*; it never scores whether a
non-empty Auto-Retro genuinely disposed each improvement. That substantive
judgment is rung 2's and the human's. A fully-deterministic *substantive* check
is infeasible — a prose word-list over-fires or passes pure narration (proven on
the live corpus) — so the deterministic-check requirement is satisfied as a
deterministic floor **plus** a recorded intelligent review, named honestly, not
as a quiet scope-narrowing. Narration stays a non-blocking affordance while
review-*existence* is blocking, for one principled reason: you can ungameably
check "is there a bound `Disposition review:` line" (offline, clone-safe), but a
hard transcript gate on whether the agent narrated substance would over-fire.

### After-phase evidence gate

`upsert_goal.py --status complete` now refuses the flip unless the goal
artifact body carries two evidence lines (anywhere; the parser scans the
whole body):

- `Retro: <path>` — a checked-in retro artifact under
  `charness-artifacts/retro/` produced by running the `retro` skill this
  run, **or** `Retro: skipped: <enum>: <detail>`.
- `Host log probe: <path>` — a JSON file containing
  `probe_host_logs.py` output (e.g.,
  `charness-artifacts/probe/<date>-<slug>.json`), **or**
  `Host log probe: skipped: <enum>: <detail>`. The allowed skip-reason enum and
  its minimum length are not restated here — they are rendered live from the
  validator by `describe_goal_closeout_shape.py` (*Closeout preflight* above),
  the single source for this and every other closeout-evidence FORM.
- `Disposition review: <path>` — **for in-scope goals only** (see
  grandfather rule below) — the fresh-eye disposition-review artifact (rung 2),
  e.g. under `charness-artifacts/critique/`, **or**
  `Disposition review: skipped: host-blocked-subagent: <detail>` on a host that
  cannot spawn the reviewer (graceful degradation to rung 1 only). A
  `host-blocked-subagent` skip on a host that demonstrably *can* spawn is itself
  an audit-flag for the human reader, not a clean pass.
- `Early close report: <path>` — when `## Final Verification` records
  `No safe next slice:` or `Early close rationale:`. This is a checked-in,
  goal-bound report for the user containing the early-stop rationale,
  user-decision-needed items, and waste/retro findings. No skip form is
  supported; if the agent can record an early-close reason, it can write the
  report.

The `## Auto-Retro` blank check (rung 1a) and the `Disposition review:`
requirement (rung 1b) fire only for goals **`Created:` on or after the rule
landing date (inclusive)**. A goal shaped before the rule existed had no chance
to plan its Auto-Retro/review around it, so keying on `Created` (not completion
date) grandfathers exactly the in-flight goals; a
missing/malformed `Created:` fails **closed** (the gate applies) so a goal cannot
dodge both rungs by corrupting one line. Grandfathering is clone-safe (in-file
content, not mtime).

`check_goal_artifact.py` runs the same check post-flip when the goal's
status is already `complete`, so the gate stays visible from both
directions. (A goal closed before the rule but `Created` on/after the landing
date is in-scope and shows a rung-1b diagnostic on re-check, but is never
*re-refused*: the flip-guard only fires on a non-`complete` → `complete`
transition.) The
contract lives at the authoring-repo-internal
`<repo-root>/docs/prescribed-skill-closeout-contract.md`.

A cited evidence file must also **bind** to this goal: file
presence is necessary but not sufficient, so each evidence path's
basename or content must reference the goal's identity (its slug or the
issue numbers parsed from the `Activation:` line). A closeout that points
`Retro:` at an unrelated pre-existing artifact is refused with a
`binding_failures` entry. Binding is clone-safe (basename/content tokens,
not mtime — a fresh checkout resets every file's mtime).

### Coordination floors — routing + gather + release + issue

Presence-only closeout floors give *teeth* to routing-cue boundaries the prose
cue under-serves, wired through the same After-phase evidence gate. Each fires
only when its trigger is present, and is satisfied by a step line in
`## Coordination Cues` (a real reference or an explicit opt-out):

- **phase-routing floor** — when recorded work sections show implementation
  (`What changed:` / `Commits:`), bug/RCA/debug cues, quality-gate cues, or
  issue-closeout cues, the run must record a `Routing:` line that names
  `find-skills` and the routed skill (`impl`, `debug`, `quality`, or `issue`),
  or `Routing: n/a — <reason>` (≥30 chars). This floor is presence-only: it
  proves `achieve` coordinated the owner skill boundary, not that the prose route
  was semantically perfect.
- **gather floor** — when `## Context Sources` names an external source (an
  `http(s)://` URL; Slack / Notion / Google-Docs / Drive links and bare web URLs
  all qualify), the run must record a `Gather: <ref>` step or a
  `Gather: n/a — <reason>` opt-out (≥30 chars). `CLAUDE.md` mandates routing
  external sources through `gather`; a goal shaped from an external URL that never
  gathered it is the gap this closes.
- **release floor** — when the run's *recorded work* names a release surface (a
  version bump or install-manifest edit — detected by precise path/action tokens
  such as `bump_version` / `publish_release` / `marketplace.json` /
  `charness-artifacts/release/`, never the bare word "release"), the run must
  record a `Release: <ref>` step or a `Release: n/a — <reason>` opt-out.
- **issue-closeout floor** — when `## Context Sources` names a tracked/GitHub
  issue, or recorded work sections (`## Slice Log` / `## Final Verification`)
  carry a close keyword such as `Close #N`, the run must record an
  `Issue closeout: <ref>` step or an
  `Issue closeout: n/a — <reason>` opt-out.

All are presence/binding-only (they never classify whether prose is "good
enough"), scoped to `## Coordination Cues` so a goal that merely *describes* a
step line in prose cannot falsely satisfy them, and **grandfathered by
`Created` date**. Gather/release apply to goals Created on or after the
gather/release rule landing date; issue closeout and phase routing apply to
goals Created on or after their own landing dates. A missing/malformed `Created`
fails closed. The floors fire at the `complete` flip (`upsert_goal.py`) and
post-flip (`check_goal_artifact.py`), like the disposition gate. `impl`,
`debug`, `quality`, `gather`, `release`, and `issue` stay useful standalone —
these are operator-side cues `achieve` plans into the artifact, never
`achieve`-only branches in those skills.

### Closeout-state taxonomy

Final closeout proof is not one bit. Name the level a goal actually reached so
"complete" never implies external proof that did not run. The six levels, from
local to fully external:

1. `impl-local` — implementation and local deterministic checks complete.
2. `carrier` — the closeout carrier (direct commit / PR body / release commit)
   is validated and staged (`issue_tool.py validate-closeout-draft`).
3. `pushed-ci` — the carrier is pushed and remote CI is verified.
4. `instance-synced` — the running instance reflects the change (applied /
   restarted / redeployed, per the consumer's deployment model).
5. `live` — provider / live proof reached (a real provider roundtrip).
6. `issue-closed` — the tracked GitHub issue's `CLOSED` state is verified.

These levels do not subsume each other. `instance-synced` (4) proves runtime
deployment state and `issue-closed` (6) proves GitHub `CLOSED` state, but neither
is `live` (5) behavior proof for an issue whose acceptance surface is a
provider/connector behavior. For an issue-bundle closeout, the per-issue behavior
binding lives in the disposition review's distinct-channel confirmation
(*Disposition Gate - Two Rungs*, the irreversible-boundary mandate), not in a
bundle-level deployment/`CLOSED` readback standing in for every issue.

A **standalone** goal owns all reached levels itself and names any skipped level
as an explicit non-claim (Honest Proof Discipline below). This is the strict
default and is unchanged.

### Orchestrated closeout (orchestrator/sub-goal proof delegation)

When an operator runs a larger **orchestrator** goal that queues sub-goals and
wants the external-proof boundary owned once at the end, a sub-goal may close at
`impl-local`/`carrier` and *delegate* the later levels — but only explicitly,
to a *named* orchestrator, never by silent omission. This is **opt-in**: a goal
with no `## Closeout Delegation` section, or `Closeout mode: standalone`, keeps
the strict standalone default (the non-weakening constraint).

A goal opts in with a `## Closeout Delegation` section. `references/goal-artifact.md`
*Closeout Delegation* owns the section's exact FORM and the two invariants
`check_goal_artifact.py` enforces at the `complete` flip (and post-flip) — a
sub-goal must name a named orchestrator and at least one delegated-proof item;
an orchestrator must resolve every checklist item — so delegated proof stays
machine-visible and the orchestrator cannot silently forget it. The sub-goal
records its honest stop as a non-claim under a `Closeout state:` line (for
example, `impl-local / carrier complete; rest delegated`); the pattern never
lets a delegated proof be claimed as run when it was not.
