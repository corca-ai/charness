# Achieve Lifecycle

`achieve` runs one goal as three phases: **before** (shape and save), **during**
(slice and record), **after** (prove and reflect). The goal artifact is the
single durable surface across all three so a compacted or interrupted run can be
audited from one file.

## Before

Start from prose, not from an already perfect goal. Shaping happens here, in the
Before-phase (invoked via `/achieve`), never at `/goal` activation. Interview
only until the work has enough shape to save a reviewable goal artifact.
Establish:

- desired outcome
- non-goals and boundaries
- user-visible acceptance proof
- low-cost agent verification
- high-confidence or high-cost verification
- per-slice expected proof cost and expected test-duplication pressure, so a
  slice that adds or expands tests states up front whether it is likely to push
  a broad duplicate/length/pressure gate toward its threshold
- slice sequence
- critique plan
- when the goal resolves a tracked issue: the `debug` root-cause step for a
  bug-class issue (planned *before* the fix slice) and the closeout
  close-via-`issue` step (`Close #N` on the fix/closeout commit) — see
  `references/coordination.md` *Resolving A Tracked Issue*
- stop conditions
- reporting expectations

Ask a small number of high-leverage questions. Do not interrogate the user for
detail that a strong default or the request wording already settles.

### Mode disambiguation

One mode question is high-leverage often enough to call out: is this an
**artifact-only** goal draft (shape and save, then stop) or an
**implementation-continuation** run (the user expects slices to execute once
activated)? When the selector or prose is genuinely ambiguous between the two,
ask at least one question to resolve it before saving — a wrong assumption here
either strands a draft the user wanted executed or starts executing a draft the
user wanted only reviewed. When a strong default settles it (the prose names the
mode), state the assumed mode in the artifact and the response instead of
asking. The mode is a shaping-time intent question only; it never licenses
auto-execution, because `/goal` (pursue) and `/achieve` (shape) are separate
operator actions. This is the before-phase question-discipline contract.

### Anti-anchoring probe

For each value confirmed by the user, inherited from issue framing, or
pulled from prior session memory, test whether the value is one of a known
system axis (host, provider, environment, profile, locale, runtime, tier)
before locking the design. Record the result on each value:

- `axis: <name>` when the system already varies on that axis somewhere
  else (adapter, preset, profile, integration manifest), or
- `single-point: <reason>` when the value really is a singleton.

A confirmed value with neither record is over-anchored. This preserves the
confirmed-input over-anchoring lesson: one confirmed model name must not become
a global default when the repo runs on multiple hosts.

When the repo is known to vary on a host/provider/environment axis, do
**not** offer an `AskUserQuestion` that frames the value as a global
`confirm <value-X>` vs `defer to host` binary. Offer the family shape
instead (one option per axis instance), or ask the axis question first.

A `critique` Before-phase pass may pick the
[`confirmed-input over-anchoring`](../../critique/references/confirmed-input-over-anchoring.md)
angle to verify the probe ran honestly.

### Portability self-test

A goal artifact must be readable by a fresh session without the saving
session's working memory. Before saving the artifact at status `draft`,
the Before-phase records three durable sections inline (already present
in the template):

- `## Context Sources` — retros, prior goal artifacts, issue numbers,
  recent-lessons surfaces; what a fresh session follows first.
- `## Interview Decisions` — for each user question: the family
  considered, the chosen value, and the rejected-alternatives reason.
  This applies the anti-anchoring lesson to the artifact itself.
- `## Plan Critique Findings` — blockers folded into Boundaries /
  Verification / Slice Plan, over-worry raised but not folded, and
  reviewer provenance. Preserves the reasoning so a fresh session does
  not have to re-run critique to verify the folded revisions.

`check_goal_artifact.py` enforces these on every goal regardless of
size. A goal that genuinely has nothing for a section keeps the heading
and writes `N/A — <reason>`. The old size/marker exemption was removed:
its full-text `Single-slice goal:` scan was poisoned by prose merely describing
the marker, and the template already seeds all three headings, so the exemption
was both unsafe and redundant.

When shaping an auto-drafted skeleton, overwrite its
`To be filled by the achieve Before-phase` placeholder lines with the real
content — a leftover marker leaves the goal reading as unshaped to the
pursue-readiness check, which would make `/goal` fail-fast on an
actually-shaped goal.

Save the artifact with `upsert_goal.py` at status `draft`. Tell the user the
file is inert until they run the activation command. The skill does **not** start
executing slices on its own — activation is the user's explicit decision.

### Activation-closeout clarity

The before-phase response must make activation impossible to miss. Close it with
an explicit checklist the operator can act on without rereading:

- `Goal file:` — the saved artifact path under `charness-artifacts/goals/`.
- `Activation:` — the exact `/goal @<path>` line to run.
- the inert-until-`/goal` status stated in one sentence (nothing runs until
  the user activates).

`check_goal_artifact.py` already fails closed when the artifact body is missing
its `Activation:` line; this closeout checklist is the response-side counterpart
so the operator-facing handoff is as clear as the artifact contract.

### Activation = Pursue Only

`/goal @<artifact>` is **pure pursue**: it runs the During loop on the goal as
given and never shapes. Shaping is the Before-phase's job (invoked via
`/achieve`); whoever runs `/goal` is responsible for handing it a shaped goal.

Before pursuing, confirm the goal is shaped with
`check_goal_artifact.py --pursue-ready --goal-path <artifact>`. If it is
**unshaped** (the Before-phase placeholder marker is still present — e.g. a raw
handoff-chunker auto-draft that was never `/achieve`'d), **fail-fast**: refuse to
pursue and route the operator to the Before-phase (`/achieve @<artifact>`). Do
**not** shape the goal inside `/goal` — that would put shaping back into the
pursue path, the exact responsibility blur this boundary removes.

### Consequential Discussion Before Activation

Structural readiness is not enough when the goal contains consequential
defaults. Before reporting an artifact as ready for `/goal`, surface a
non-empty `Discuss before activation:` summary when `Non-Goals`, `Boundaries`,
`Agent Verification Plan`, `Interview Decisions`, or `Plan Critique Findings`
contain decisions about live/prod proof, issue close/split, broad bundled scope,
irreversible side effects, or proof-level non-claims. The deterministic
`--pursue-ready` gate distinguishes this from placeholder shaping: such a goal
is shaped, but not operator-ready, until the discussion summary is visible before
the Slice Log and explicitly marked resolved, confirmed, or approved. A visible
summary is a floor, not completion: before offering activation or reporting the
goal ready, bring those items into the transcript and resolve or explicitly ask
about them. Helper output separates `shape_ready` from `activation_ready`;
`pursue_ready` is the activation-ready signal and must be false while
consequential discussion is only surfaced.

## During

The goal artifact becomes the working scratchpad for the active run. Do not use
`handoff` as the mid-goal memory surface while a goal is active.

Activation runs only after the pursue-readiness check passes (see
*Activation = pursue only*). When the run begins (the user has activated the
goal), flip the status to `active` with `upsert_goal.py --status active`; move
it to `blocked` or `complete` as the run state changes.

Keep `## Active Operating Frame` as the short current-state control panel:
current slice, next action, verification cadence, slice-review packet, and the
archival boundary. Update it at activation and around substantial slice
boundaries. Do not make a compacted session reread the whole `## Slice Log` to
learn what to do next; the log is the archive, while the frame is the active
prompt surface.

After each slice, append a slice report with `append_slice_log.py`:

- objective and why this slice was chosen now
- commits or files changed
- alternatives rejected
- targeted verification (cheap, deterministic)
- test-duplication pressure: when the slice adds or expands tests, a cheap
  duplicate-pressure sample (the repo's duplicate/length gate run in sample or
  report mode), so accumulated suite debt stays visible at the slice boundary
  instead of surfacing only at final closeout
- critique findings
- off-goal findings filed through `issue`
- lessons to carry into the next slice
- a token / time / tool-call snapshot when available

Use the planned verification cadence instead of ad hoc reruns: cheap
deterministic checks at commit boundaries cover the changed surface; slice
boundaries get higher-cost proof and fresh-eye critique when required; final
closeout gets the broad/live proof named in the artifact. A previously passed
check does not need to rerun until its covered surface changed, unless a policy
gate or the slice plan names it as a boundary proof. The cheap
duplicate-pressure sample is the exception that stays slice-local: it is a
sample, not the full broad gate, and it carries the test-debt signal forward in
the goal artifact so a compacted or resumed session does not rediscover the same
late blocker.

Fresh-eye slice critique should receive a bounded slice review packet rather
than the entire historical goal by default. Include the slice intent, changed
files and owning/generated surfaces, expected invariants, tests/proof already
run, non-claims, out-of-scope lines, and the specific reviewer questions.
Critique cadence is risk-boundary based, not commit-based: one standalone
fresh-eye critique covers a coherent substantial slice or bundle, and another is
needed only when later edits introduce a new workflow, prompt, public-skill,
validator, export, release, issue-closeout, compatibility, host-proof, rename,
deletion, or migration risk. Final closeout review can then read across slices
for cross-slice drift and Auto-Retro disposition instead of redoing every slice
review.

`run_slice_closeout.py` auto-surfaces two recurring-trap signals so they are
workflow affordances, not agent memory: a **length-headroom advisory** for any
changed gated file already near its limit (`limit − current`; choose a new
module over appending before the hard gate fires), and — via the
`check_staged_mirror_drift.py` pre-commit gate — a **hard block** when exported
source is staged without its regenerated `plugins/` mirror. Both are
owned by the authoring-repo-internal
`<repo-root>/docs/conventions/implementation-discipline.md`.

The commit-time gate family (ruff, `check_python_lengths`,
`validate_attention_state_visibility`, `check-markdown`, mirror-drift,
`validate_skills`, `check_doc_links`) is a **distinct verification surface from
the unit suite** — none of those gates run under `pytest`, so a green `pytest` is
necessary but not commit-ready. In the `mutate → sync → verify → publish` rhythm
the **verify step before a commit is `run_slice_closeout.py` (the pre-commit gate
aggregate), not the unit suite**. And the reactive trigger: if a commit *is*
rejected by one of these gates, run the aggregate to surface **all** of them at
once rather than fix-and-retry one rejection at a time — serial single-gate
rejections after a green suite are pure waste the aggregate removes.

### Coordination cues (find-skills routing)

The goal template seeds a `## Coordination Cues` section the agent fills *during*
the run — not a phase→skill map baked into `achieve`. Defer *which* skill answers
a phase or boundary to `find-skills`' recommendation engine — `--recommend-for-task`,
or `--recommendation-role <runtime|validation> --next-skill-id <skill>` — and
record the route it returns. `achieve` owns the
slot and the two closeout floors below; `find-skills` owns the recommendation
content. Seeding the cue in the artifact (where the agent reads it mid-run), not
only in a reference read once at `/achieve` shaping, is deliberate: a read-once
role table is inert exactly when the cue would fire, and an inline map would
duplicate find-skills' shipped engine as a staler copy.

Stop and ask the user when an unexpected blocker, an evidence conflict, or a
policy/product decision appears that cannot be resolved autonomously. Flip the
status to `blocked`, record the blocker and the paths already attempted, and
hand the decision back rather than guessing. When test-duplication pressure is
the blocker or relevant context, cite the latest `Test duplication pressure`
sample in the blocked record so the user and any resumed session inherit it
instead of rediscovering it.

## After

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
- an automatic retro focused on reducing time, tokens, and waste next time
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
  line (`started_at=<ISO> completed_at=<ISO> codex_session_file=<path>`) and a
  host probe produced with `probe_host_logs.py --goal-path <artifact>`, so the
  closeout can separate goal-window signals from thread-wide pressure.
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

Run `check_goal_artifact.py` before declaring completion so the required
sections, status, and activation line are all present. Flip the status to
`complete` only after the final report separates what was proven from what
remains the user's responsibility to verify.

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

### Post-Apply Checkpoint Classification

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
  run, **or** `Retro: skipped: <enum>: <detail>` with the enum from
  `host-blocked-subagent`, `host-log-not-exposed`, `evaluator-unavailable`
  and ≥40 chars total (free-text "host limit" is rejected).
- `Host log probe: <path>` — a JSON file containing
  `probe_host_logs.py` output (e.g.,
  `charness-artifacts/probe/<date>-<slug>.json`), **or**
  `Host log probe: skipped: <enum>: <detail>`.
- `Disposition review: <path>` — **for in-scope goals only** (see
  grandfather rule below) — the fresh-eye disposition-review artifact (rung 2),
  e.g. under `charness-artifacts/critique/`, **or**
  `Disposition review: skipped: host-blocked-subagent: <detail>` on a host that
  cannot spawn the reviewer (graceful degradation to rung 1 only). A
  `host-blocked-subagent` skip on a host that demonstrably *can* spawn is itself
  an audit-flag for the human reader, not a clean pass.

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

## Honest Proof Discipline

Borrow W. Edwards Deming's Plan-Do-Study-Act emphasis on the *study* step:
measure the result against the original prediction before claiming the goal is
met. A run that skips the comparison has done activity, not achievement.

Never claim provider, live, or release proof when only local deterministic
checks ran. If a proof level was skipped, the final report must say so.
