# Goal Artifact

The goal artifact is a reviewable activation artifact and the living scratchpad
for one autonomous goal run.

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

Status: draft | active | blocked | complete
Created: <date>
Activation: `/goal @charness-artifacts/goals/<file>.md`
Timebox: <duration, when user supplied a work budget>
Activation time: <ISO timestamp when the active run starts>
Closeout reserve: <duration reserved for final proof and closeout>
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/<file>.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

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

## Coordination Cues

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

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

```bash
# Scaffold a new goal (status draft), or update only the status of an existing one.
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug ceal-184-push-confidence --title "Ceal 184 push confidence" \
  --goal-body "Make the accumulated local commits safe to push."

# Append one slice report to the Slice Log.
# Use --test-pressure when the slice adds or expands tests, to carry a cheap
# duplicate-pressure sample forward instead of rediscovering the debt at closeout.
python3 "$SKILL_DIR/scripts/append_slice_log.py" --repo-root . \
  --slug ceal-184-push-confidence --date 2026-05-26 --name "Inventory local risk" \
  --objective "Map the full unpushed surface" --verification "git diff --stat origin/main..HEAD" \
  --test-pressure "adjacent duplicates 23.2% vs 22% gate; +2 runtime tests this slice"

# Flip status as the run progresses (draft -> active -> blocked/complete).
python3 "$SKILL_DIR/scripts/upsert_goal.py" --repo-root . \
  --slug ceal-184-push-confidence --title "Ceal 184 push confidence" --status active

# Check required sections, status, and activation line before completion.
python3 "$SKILL_DIR/scripts/check_goal_artifact.py" --repo-root . \
  --slug ceal-184-push-confidence --date 2026-05-26
```

`upsert_goal.py` never overwrites an existing artifact body; on a second call it
only rewrites the `Status:` line, and only when the value changed (the result
carries a note so a caller expecting a new file can tell). The slice number in
`append_slice_log.py` is derived from the existing `### Slice N:` headings, so
reports stay ordered without a counter argument.

The `Slice Plan` table is hand-maintained planning intent; no helper updates its
`Status` column. The `Slice Log` (appended by `append_slice_log.py`) is the
execution source of truth. Keep the plan table for the up-front sequence and let
the log record what actually happened.

The `Active Operating Frame` is the current-state control panel, not another
archive. Update it at activation and before/after substantial slices so a
compacted session can continue from the top of the file without rereading the
entire historical log. Completed detail belongs in the Slice Log, Final
Verification, and Auto-Retro sections.

## Timebox Fields

Add the timebox fields only when the user gives a fixed duration. `Timebox:`,
`Activation time:`, `Closeout reserve:`, and
`Done-early policy: continue_next_improvement` make the budget enforceable:
before the closeout reserve begins, completion is blocked unless the artifact
records `No safe next slice:`, `Early close rationale:`, or a supported
`Stop condition:` with a concrete reason under `## Final Verification`. These
lines are plain markdown so a fresh session can continue the clock without host
memory. When an early-close reason is recorded, `## Final Verification` must
also include `Early close report: <path>` pointing at a checked-in report that
explains why the run stopped early, what decisions require the user, and what
waste/retro findings should shape the next run.

When changing the goal artifact shape, update every goal producer that emits a
new artifact, not only the primary `achieve` template. The current producer
contract is pinned by the authoring-repo-internal
`tests/quality_gates/test_goal_artifact_producers.py`.

## Closeout Delegation (optional, orchestrated mode)

A goal stays **standalone** by default — it owns all closeout proof itself and
needs no extra section. A goal only adds `## Closeout Delegation` when it runs in
orchestrated mode (`references/lifecycle.md` *Orchestrated closeout*). Absence of
the section, or `Closeout mode: standalone`, keeps the strict standalone default.

A **sub-goal** that delegates external proof to a named orchestrator:

```markdown
## Closeout Delegation

- Closeout mode: orchestrated
- Orchestrator goal: charness-artifacts/goals/<date>-<orchestrator-slug>.md
- Closeout state: impl-local / carrier complete
- Delegated proof:
  - pushed-ci — orchestrator owns the final main push + CI watch
  - live — orchestrator runs the provider roundtrip
  - issue-closed — orchestrator verifies #<N> CLOSED after push
```

An **orchestrator** goal that owns the delegated proof carries a checklist; every
item must be resolved (`verified`, `skipped: <reason>`, or `issue #N`) before the
goal can flip to `complete`:

```markdown
## Closeout Delegation

- Closeout mode: orchestrator
- Delegated proof checklist:
  - pushed-ci — verified: CI green on <sha> (<run-url>)
  - applied-restarted — skipped: apply deferred to next window — operator directed
  - live — verified: provider roundtrip observed <ts>
  - issue-closed — issue #<N>
```

`check_goal_artifact.py` enforces this in
`goal_artifact_closeout_delegation.py`: an orchestrated sub-goal must name the
orchestrator and list ≥1 delegated item; an orchestrator must resolve every
checklist item. The check is presence/resolution-based — it proves the delegated
proof is recorded and (for the orchestrator) accounted for, not that the prose is
"good enough". The taxonomy tokens (`impl-local`, `carrier`, `pushed-ci`,
`applied-restarted`, `live`, `issue-closed`) are the shared vocabulary, not a
required exact match.

The gate does **not** verify that the named orchestrator goal file exists or that
its checklist actually covers the sub-goal's delegated items — that substantive
call is the fresh-eye disposition review's job, the same rung-1 (deterministic
floor proves the wiring) / rung-2 (intelligence judges substance) split the
disposition gate uses. The deterministic floor stays narrow and ungameable on
purpose; tightening it into a cross-goal existence/coverage validator would
re-import the brittleness the floor philosophy avoids.

## Metrics Honesty

Slice and final metrics use host-agnostic shallow signals. Prefer
`retro`'s `probe_host_logs.py` for token / turn / tool-call availability rather
than asserting counts the host log does not expose. Deep per-session counting is
Codex-specific and best-effort; record `Metrics: when available` instead of
fabricating numbers. Keep measured counts, proxy signals, and unavailable
signals separate. Cached input by itself is a context-pressure signal, not a
waste conclusion.

For long goals, record a goal-window evidence line when the host exposes enough
timing data:

```text
Host metric window: started_at=<ISO> completed_at=<ISO> codex_session_file=<path>
```

Record it with the helper rather than hand-editing, so the probe sees a complete
window instead of silently reporting `absent`:

```bash
python3 "$SKILL_DIR/scripts/record_metric_window.py" --goal-path <artifact> \
  --started-at <ISO> --completed-at <ISO> --codex-session-file <host adapter path>
```

The host adapter supplies the timestamps and rollout-file path it can prove; the
portable helper only writes them, idempotently, under `## Final Verification`.
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
python3 "$SKILL_DIR/scripts/probe_host_logs.py" --goal-path <artifact> --format markdown
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
`scripts/goal_metrics_render_lib.render_broad_gate_attestation`. The structure
has no `command` field by design, so a host (e.g. Ceal) can attest its own
exact-state gate without weakening pushed-state proof and without leaking the
provider CLI invocation into staged docs.
