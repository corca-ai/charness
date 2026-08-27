# Goal Artifact

The goal artifact is a compact, reviewable activation record for one autonomous
goal run. After approval it keeps intent and binding; provider state carries
routine progress.

## Location

```text
charness-artifacts/goals/<yyyy-mm-dd-slug>.md
```

This is operational harness state, not product docs: safe to commit with other
Charness artifacts, and outside manually maintained documentation. The location
is fixed for the first version.

## Shape

```markdown
# Achieve Goal: <title>

Status: draft | active | blocked | complete | superseded
Created: <date>
Activation: `/goal @charness-artifacts/goals/<file>.md`
Timebox: <duration, when user supplied a work budget>
Activation time: <ISO timestamp when the active run starts>
Closeout reserve: <duration reserved for final proof and closeout>
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names the
  reviewable-intent unit in progress and the commits it spans; critique and broad
  proof do not re-fire within one unchanged intent — update it when the intent
  changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/<file>.md` after
  confirming the draft is still intended.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`; do not use it as a
  second progress tracker.

## Goal

Keep this section short: outcome, boundaries, and why this goal exists. The
goal is not the phase notebook.

## Operating Principles

Every new goal carries a compact operating frame near the top. When a failure
appears, stop treating it as a transient symptom: run `debug`, identify the
pattern and pattern of patterns with 5-whys, and record the structural repair or
tracked follow-up. A retry may be part of evidence gathering, never the root
cause. The goal also states that phase detail belongs in linked spec files.

## Phase Specifications

Each phase has one checked-in file at
`charness-artifacts/specs/<goal-slug>/<phase-slug>/spec.md`. It must state the
objective, in/out scope, completion criteria, exact verification method and
receipt, dependencies, and non-claims. The goal links every phase file from
this section; the spec is the phase's source of truth while the goal retains
only a concise status/control-panel summary.

## Non-Goals

## Boundaries

## User Acceptance

What the user can do to verify completion directly.

## Agent Verification Plan

### Low-Cost Checks

### High-Confidence Checks

### External Or Live Proof

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Backlog Recount

- Counted:
- Claims:
- Not claimed:

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

The FIRST entry is the repo's governing design standard, always. A goal is
shaped by deciding where teeth belong and which boundaries are irreversible,
and those are exactly the standard's questions — consulting it at closeout
instead is consulting it after the decisions it governs were already taken.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
```

## Helper Scripts

Use the helpers instead of hand-editing the markdown; they preserve manual
content and avoid timestamp-only churn. Resolve `$SKILL_DIR` per
`../../../shared/references/bootstrap-resolution.md` first.

**Prose must not cross a shell.** It cites identifiers, so it carries backticks,
and a shell expands those BEFORE the helper starts — the artifact is written with
words missing and the run still reports success. Two safe channels: build `argv`
as a list with no shell, or use `--fields-file <json>`, which both
`upsert_goal.py` and `append_slice_log.py` accept. The flag forms below are shown
for the FIELD NAMES and stay valid for short identifier-free values.

`upsert_goal.py`'s prose fields are `title` and `goal-body`. `--slug`, `--date`
and `--status` stay flags because each has a shape rule: the status is a closed
enum, the date is anchored, and the slug is resolved with `slugify` and rejected
only when no usable characters survive. A usable slug may be coerced into the
filename form rather than preserving the caller's spelling. See `SKILL.md` and
`lifecycle-during.md`.

```bash
# Scaffold a new goal (status draft), or update only the status of an existing one.
# Write the JSON with a file tool; a goal body cites identifiers, and --goal-body
# typed into a shell arrives with words missing under a `created` verdict.
cat > /tmp/goal-fields.json <<'JSON'
{"title": "Acme 184 push confidence",
 "goal-body": "Make the accumulated local commits safe to push."}
JSON
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug acme-184-push-confidence --fields-file /tmp/goal-fields.json

# Append one slice report to the Slice Log.
# Use --test-pressure when the slice adds or expands tests, to carry a cheap
# duplicate-pressure sample forward instead of rediscovering the debt at closeout.
cat > /tmp/slice-fields.json <<'JSON'
{
  "name": "Inventory local risk",
  "objective": "Map the full unpushed surface",
  "verification": "git diff --stat origin/main..HEAD",
  "test-pressure": "adjacent duplicates 23.2% vs 22% gate; +2 runtime tests this slice"
}
JSON
python3 "$SKILL_DIR/scripts/append_slice_log.py" --repo-root . \
  --slug acme-184-push-confidence --date 2026-05-26 \
  --fields-file /tmp/slice-fields.json

# Flip status as the run progresses (draft -> active -> blocked/complete/superseded).
# No title needed: an existing artifact's heading and body are never rewritten.
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug acme-184-push-confidence --status active

# Check required sections, status, and activation line before completion.
python3 "$SKILL_DIR/scripts/check_goal_artifact.py" --repo-root . \
  --slug acme-184-push-confidence --date 2026-05-26
```

`upsert_goal.py` never overwrites an existing artifact's heading or body; on a
second call it only rewrites the `Status:` line, and only when the value changed
(the result carries a note so a caller expecting a new file can tell). Re-running
with the SAME `title`/`goal-body` is therefore idempotent, but a CHANGED one is
refused rather than silently dropped — edit the artifact directly instead. The
slice number in
`append_slice_log.py` is derived from the existing `### Slice N:` headings, so
reports stay ordered without a counter argument.

At complete-state closeout, no section's first body line may remain a scaffold
or closeout-pending placeholder such as `Pending until`, `TODO`, `TBD`, or
`To be filled`. `check_goal_artifact.py` reports these under
`section_placeholders`; replace the line with the real disposition, proof, or
explicit opt-out before flipping `Status:` to `complete`.

The `Slice Plan` table is hand-maintained planning intent; no helper updates its
`Status` column. The `Slice Log` (appended by `append_slice_log.py`) is the
execution source of truth. Keep the plan table for the up-front sequence and let
the log record what actually happened.

The `Active Operating Frame` is the current-state control panel, not another
archive. Update it at activation and before/after substantial slices so a
compacted session can continue from the top of the file without rereading the
entire historical log. Completed detail belongs in the Slice Log, Final
Verification, Operator Decision Queue, and Auto-Retro sections.

The `Operator Decision Queue` is the standard place to keep operator-only
decisions visible without interrupting safe local work. Add an item when a run
discovers a decision, confirmation, credential action, manual proof step, or
external-boundary approval that only the operator can provide, but that does not
block the current safe slice. Stop only when the decision blocks all safe next
slices. At closeout, render the queue in the final report or record
`none — <reason>` in the section.

## Timebox Fields

Add the timebox fields only when the user gives a fixed duration. `Timebox:`,
`Activation time:`, `Closeout reserve:`, and
`Done-early policy: continue_next_improvement` make the budget enforceable:
before the closeout reserve begins, completion is blocked unless
`## Final Verification` records a concrete early-close reason plus a candidate
ledger and outcome sufficiency check:

```md
Early close rationale: <why this closes before reserve>
Next slice candidate: <candidate> | decision: defer | reason: <why not now>
Next slice candidate: <candidate> | decision: user-decision | reason: <why not now>
Outcome sufficiency check: accepted-low-yield: <why this is still honest to close>
```

These lines are plain markdown so a fresh session can continue the clock without
host memory. The early-close reason may still be `No safe next slice:`,
`Early close rationale:`, or a supported `Stop condition:` line; the candidate
ledger and sufficiency check decide whether that reason is enough before the
reserve window. Valid candidate decisions are `defer`, `blocked`, `unsafe`,
`user-decision`, and `out-of-scope`; `continue` is deliberately invalid before
the reserve window. Valid sufficiency statuses are `sufficient`,
`accepted-low-yield`, and `blocked-by-user-decision`. When an early-close
reason is recorded, `## Final Verification` must also include
`Early close report: <path>` pointing at a checked-in report that explains why
the run stopped early, what decisions require the user, and what waste/retro
findings should shape the next run; the report is required even when the
early stop is correct, because correctness does not remove the communication
duty.

When changing the goal artifact shape, update every goal producer that emits a
new artifact, not only the primary `achieve` template. The current producer
contract is pinned by the authoring-repo-internal
`<authoring-repo>/tests/quality_gates/test_goal_artifact_producers.py`.

## Superseded Record (conditional, before superseded)

`superseded` is the terminal status for a goal that ENDED WITHOUT COMPLETING —
folded into a successor, overtaken, or abandoned with its remainder handed on.
It exists because the contract previously offered only `complete` and `blocked`,
so such a goal had to choose between staying `active` forever and claiming a
completion it never earned. Both lie to the next session; the second lies in the
direction that loses work.

A terminal status that skips the closeout floor and asks for nothing in return
would lose the same work more quietly — a finished-looking artifact with no
successor and no reason. So `superseded` costs exactly one line, and that line is
the thing a reader actually needs:

```markdown
Superseded by: charness-artifacts/goals/<yyyy-mm-dd-slug>.md — <what carried on>
```

`Superseded by: none — <reason>` is accepted, and accepting it is the point: a
goal genuinely abandoned with nothing downstream should be able to say so out
loud rather than be unable to close. A punctuation-only value (`—`) is refused —
a filled-looking empty field is the class this contract's other floors already
learned.

The record is checked by `check_goal_artifact.py` when the status is
`superseded`, and `upsert_goal.py` refuses the flip without it. A superseded
goal also carries a `Retro:` line (or an explicit allowed skip, which is a
non-claim) and uses the deterministic `## Auto-Retro` disposition floor when
that bound retro lists improvements. The complete-evidence floor is deliberately
NOT applied: this goal says it did not complete, so it does not inherit
  complete-only host-log or disposition-review requirements.

This record is audit traceability, not activation permission. The public
`--pursue-ready` report always sets both `pursue_ready` and `activation_ready` to
`false` for terminal `complete`/`superseded` statuses, including annotated
forms. Its typed `lifecycle` and `readiness_blockers` fields identify the
terminal refusal separately from hollow shaping-section refusal.

## Remaining Boundary Matrix (conditional, before blocked)

A goal adds a `## Remaining Boundary Matrix` section only when it flips to
`blocked` — it is not seeded in every goal. Each external/live proof lane the
goal mentions is one line:

```markdown
## Remaining Boundary Matrix

- Lane: github publish/PR/issue-close | classification: approval-required | next: operator approval to push
- Lane: instance apply/restart | classification: preauthorized-runnable | next: repo preauthorized apply with --boundary-reason + readbacks
- Lane: HOTL roundtrip proof | classification: dispositioned | next: deferred to next window — operator directed
```

Classification tokens: `runnable` / `preauthorized-runnable` / `approved` (the
lane can still make progress under repo policy), `approval-required` /
`read-only` / `blocked` (genuinely cannot proceed now), `verified` /
`dispositioned` (already settled). `check_goal_artifact.py` and
`upsert_goal.py --status blocked` enforce the floor in
`goal_artifact_blocked_matrix.py`: the matrix must name ≥1 validly-classified
lane, and **no lane may be self-classified runnable** — a runnable lane means the
goal should stay `active` and continue it, not block the whole goal. The floor is
presence + no-runnable-contradiction only (Created-date grandfathered); whether a
lane is *truly* runnable is the agent's and the operator's call, not the floor's.
See `references/lifecycle-during.md` *Remaining-boundary matrix before `blocked`*.

## Metrics Honesty

Slice and final metrics use host-agnostic shallow signals. Prefer
`retro`'s `probe_host_logs.py` for token / turn / tool-call availability rather
than asserting counts the host log does not expose. Deep per-session counting is
host-dependent and best-effort; record `Metrics: when available` instead of
fabricating numbers. Keep measured counts, proxy signals, and unavailable
signals separate. Cached input by itself is a context-pressure signal, not a
waste conclusion.

For long goals, record a goal-window evidence line when the host exposes enough
timing data:

```text
Host metric window: started_at=<ISO> completed_at=<ISO> <host>_session_file=<path>
```

The session-file key names the host that produced the session log — exactly one
supported key, `claude_session_file` or `codex_session_file`, per line (a
dual-host line is rejected as ambiguous). Record it with the helper rather than
hand-editing, so the probe sees a complete window instead of silently reporting
`absent`. Use exactly one of the helper's supported host-key forms:

```bash
# Claude project session JSONL
python3 "$SKILL_DIR/scripts/record_metric_window.py" --goal-path <artifact> \
  --started-at <ISO> --completed-at <ISO> --claude-session-file <project session path>
# Codex rollout JSONL
python3 "$SKILL_DIR/scripts/record_metric_window.py" --goal-path <artifact> \
  --started-at <ISO> --completed-at <ISO> --codex-session-file <host adapter path>
```

The host adapter supplies the timestamps and rollout-file path it can prove; the
portable helper only writes them, idempotently, after existing authored content
under `## Final Verification`. Because the authored content remains a contiguous
prefix, it is safe to fill or exact-match-replace that content either before or
after invoking the helper.
Then run the `retro` host-log probe with `--goal-path <artifact>` so host signals
are filtered to that window. If the source lacks timestamps or a session file,
say `unavailable` rather than presenting a thread-wide audit as a goal total.

At flip-to-complete, `check_goal_artifact.py` surfaces a non-blocking
`closeout_evidence.metric_window` signal (`recorded` / `incomplete` / `absent`)
so a forgotten window is visible at the gate instead of silently producing a
thread-wide audit reported as a per-goal total. It never blocks the flip:
a host that genuinely lacks timestamps records `unavailable` instead.

### Standardized closeout metrics block (provider-safe)

Render the measured-vs-proxy closeout summary instead of hand-assembling it, so
every goal narrates the same signals the same way:

```bash
python3 "$SKILL_DIR/../retro/scripts/probe_host_logs.py" --goal-path <artifact> --format markdown
```

The block surfaces the window status verbatim (so an `absent` window cannot
masquerade as a per-goal total), separates measured counts from activity
proxies, and emits only counts, family labels, and result attestations — never a
provider CLI verification command string. This keeps closeout evidence safe to
stage under a provider-boundary scanner that rejects re-advertised provider CLI
commands.

### Broad-gate attestation hook

Exact-state broad-gate proof is recorded as a *result*, not a re-embedded
command. The portable contract is a result triple — `gate` (id), `outcome`
(`PASS`/`FAIL`/…), and `state_ref` (a host-provable exact state such as a commit
SHA with a clean tree) — rendered by
`<plugin-dir>/scripts/goal_metrics_render_lib.py`'s `render_broad_gate_attestation`. The structure
has no `command` field by design, so a host (e.g. Acme) can attest its own
exact-state gate without weakening pushed-state proof and without leaking the
provider CLI invocation into staged docs.
