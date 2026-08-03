# Achieve Lifecycle — During

Part of achieve's three-phase lifecycle contract; see `lifecycle.md` for
the overview and `lifecycle-before.md` / `lifecycle-after.md` for the rest.

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

For Charness-maintained repos, the generated active frame names the concrete
gate cadence: pre-lock slices run `run_slice_closeout.py --skip-broad-pytest`;
final or bundle proof records the verification lock and reruns with
`--verification-lock` before claiming broad pytest evidence.

### External-side-effect approval is phase-scoped

Operator approval for an external side effect — publish, push, remote CI watch,
or live apply — is scoped to the phase or bundle that requested it, and does
**not** carry forward to a later phase. When an approved publish/CI/apply lane
completes and the run continues into done-early or test-only quality slices, the
per-slice verification cadence is **local by default**: prove each slice
locally, batch the remote proof, and run remote CI once over the final bundled
state. Do not re-enter the publish/push/CI-watch loop on every later slice on
the strength of the earlier lane's approval — that silent carry-forward burns
the operator's time and noises the audit trail. Per-slice remote publication is
assumed **only** when the operator explicitly asks for it, or when a slice is
itself runtime-affecting and requires earlier publication to be proven (see
*Post-Checkpoint Commit Classification*). When in doubt about whether a later
phase still carries the earlier approval, treat it as not carried and ask.

Fresh-eye slice critique should receive a bounded slice review packet rather
than the entire historical goal by default. Include the slice intent, changed
files and owning/generated surfaces, expected invariants, tests/proof already
run, non-claims, out-of-scope lines, and the specific reviewer questions.
Critique cadence is risk-boundary based, not commit-based: one standalone
fresh-eye critique covers a coherent substantial slice or bundle, and another is
needed only when later edits introduce a new workflow, prompt, public-skill,
validator, export, release, issue-closeout, compatibility, host-proof, rename,
deletion, or migration risk. Mandatory premortem is inside this cadence, not an
exception: it fires once per slice-intent boundary, not per commit. The slice-unit
definition, the premortem↔cadence resolution, and the proof/artifact cadence
behind this rule are owned by
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md). Final closeout review can then read across slices
for cross-slice drift and Auto-Retro disposition instead of redoing every slice
review.

**A goal of three or more slices also runs a bounded GOAL-CLAIMS review at its
midpoint.** Slice critique puts a fresh eye on each repair; this one reads the
goal artifact's per-row CLAIMS against the owning records and the commits, which
is a different question and needs a different packet: "does the Slice Log claim
match what the record says and what the commit did." A goal artifact is a verdict
surface — downstream sessions plan against its assertions rather than against the
code — and leaving it reviewed only at closeout is what let one goal write five
slices of claims against an acceptance criterion none of them met. Catching a
claims defect once costs one round; catching it at closeout costs re-writing every
artifact the defect touched. It does not replace the closeout disposition review,
and a two-slice goal keeps the closeout round alone.

`run_slice_closeout.py` auto-surfaces two recurring-trap signals so they are
workflow affordances, not agent memory: a **length-headroom advisory** for any
changed gated file already near its limit (`limit − current`; choose a new
module over appending before the hard gate fires), and — via the
`check_staged_mirror_drift.py` pre-commit gate — a **hard block** when exported
source is staged without its regenerated `plugins/` mirror. Both are
owned by the authoring-repo-internal
`<authoring-repo>/docs/conventions/implementation-discipline.md`.

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

### Coordination cues (owner-skill routing)

The goal template seeds a `## Coordination Cues` section the agent fills *during*
the run — not a phase→skill map baked into `achieve`. Defer *which* skill answers
a phase or boundary to installed skill metadata/model judgment, and record the
selected owner skill and basis. Use the read-only catalog only when hidden
support or integration availability is unclear. `achieve` owns the slot and the
two closeout floors below. Seeding the cue in the artifact (where the agent
reads it mid-run), not only in a reference read once at `/achieve` shaping, is
deliberate: a read-once role table is inert exactly when the cue would fire, and
an inline map would be a staler copy.

Stop and ask the user when an unexpected blocker, an evidence conflict, or a
policy/product decision appears that cannot be resolved autonomously. Flip the
status to `blocked`, record the blocker and the paths already attempted, and
hand the decision back rather than guessing. When test-duplication pressure is
the blocker or relevant context, cite the latest `Test duplication pressure`
sample in the blocked record so the user and any resumed session inherit it
instead of rediscovering it.

### Remaining-boundary matrix before `blocked`

`blocked` is a whole-goal status, not a per-lane one. One blocked boundary
(GitHub publication awaiting approval) does not block a goal that still has a
runnable lane (a repo-preauthorized instance apply/restart). Before flipping a
goal to `blocked`, render a `## Remaining Boundary Matrix` that classifies
**every** external/live proof lane the goal mentions — GitHub publication / PR /
issue-close, repo-preauthorized apply/restart (with `--boundary-reason` and
pre/post readbacks), Slack/provider writes, and each HOTL entry.

`references/goal-artifact.md` *Remaining Boundary Matrix* owns the line form,
the classification-token enum, and the enforced no-runnable-contradiction rule
(`goal_artifact_blocked_matrix.py`, grandfathered by `Created` date, re-surfaced
post-flip by `check_goal_artifact.py`) — render one matrix line per lane there
before flipping to `blocked`.

### Slice-Boundary Continuation

At every slice boundary, use the goal's own learning to pick the next slice
before considering closeout. The priority order is:

- newly discovered waste, fragile coupling, or quality/test-time debt from the
  slice just completed, when a small structural fix is safe;
- the next item already in the Slice Plan or active operating frame;
- safe work from handoff/open issues that advances the macro goal family;
- an explicit stop record when the remaining work is unsafe, decision-heavy, or
  would exceed the closeout reserve.

Safe structural deletion and larger cleanup are allowed when the evidence says
the test or coupling no longer pays for itself, especially for overlong pytest
files, release-only sentinels, and source-guard-level tests. If the choice is
unsafe or product/policy-bound, file or record it instead of burning the timebox
on a risky guess. If the macro goal is already satisfied and no planned work
remains, continue with the safest handoff/open-issue improvement until the
closeout reserve begins.

Continuation crosses a side-effect boundary, not just a work boundary. When the
just-completed phase carried an external publish/CI/apply approval and the next
chosen slice is done-early or test-only quality continuation, that earlier
approval does **not** transfer to the new slice. Verify the continuation slice
**locally by default** and defer remote proof to one final bundled CI run; do
not push and watch CI per slice unless the operator explicitly asked or the
continuation slice is runtime-affecting. Re-scope the approval to the new phase
rather than inheriting it silently.

### Prose never crosses a shell

`append_slice_log.py` and `upsert_goal.py` both take their prose through
`--fields-file <json>`. That is not a convenience: goal and slice prose cites
identifiers, so it is full of backticks, and a shell performs command substitution
on a quoted argument **before the helper's process starts**. What arrives is
well-formed text with words missing. The helper exits 0 and reports `"appended"` or
`"created"`, and the surface it just damaged is the durable record a compacted or
resumed session reads to learn what happened — or, for `upsert_goal.py --goal-body`,
the `## Goal` section that says what the goal IS. No validation inside the helper
can catch it — by the time `argv` exists, there is nothing left to compare against.

Only genuinely free prose needs the file. `upsert_goal.py`'s prose keys are `title`
and `goal-body`; its `--slug`, `--date` and `--status` stay flags because each one
REFUSES a damaged value instead of absorbing it — the status is a closed enum, the
date is anchored, and a slug is rejected unless it already equals the kebab-case
form that becomes the filename. Building `argv` as a list protects prose from the
shell but not from these shape rules, so the helper applies them to the value
whatever channel delivered it.

Two safe channels, one unsafe one:

- **safe** — `--fields-file <path>` with the JSON written by a file tool.
- **safe** — building `argv` yourself as a list, with no shell in between.
- **unsafe** — per-field flags typed into a shell command line. They remain for
  short, identifier-free values; anything citing code should use the file.

An unknown key in the fields file is REFUSED rather than ignored, because a typo'd
field name in a file whose effect the caller cannot see is the same silent loss one
layer up. This rule generalizes: any helper documented with a shell-quoted prose
argument has an unguardable lossy channel in front of it.
