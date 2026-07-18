# Spec: Evidence-Bound Gajae-Code Pattern Adoption

Status: planned; implementation has not started.

## Problem

`../gajae-code` contains useful workflow, efficiency, protocol, and release
patterns, but copying its runtime would make Charness less portable and would add
rules at reversible boundaries. Charness needs a selected sequence that closes
real escape paths first, reuses current owners, and measures optimization before
changing defaults or CI scope.

Source review:
`charness-artifacts/gather/2026-07-19-gajae-code-pattern-review.md`.

## Capability Contract

A Charness maintainer can take one bounded adoption slice at a time, know which
existing surface owns it, and prove both the intended gain and the north-star
boundary. The plan must distinguish:

- a current correctness bug from a speculative optimization;
- deterministic fixture evidence from sampled or unavailable runtime evidence;
- a review/release receipt from terminal truth;
- portable concepts from Gajae-Code's Bun, TUI, tmux, and npm machinery.

## Current Slice And Dependency Order

### Slice 1 — Bound Codex app-server responses

Owner: the root `charness` CLI app-server cache-refresh helper and
`tests/charness_cli/test_codex_cache_refresh.py`.

- Immediately before each request (`initialize` and `plugin/install`), compute
  one monotonic absolute deadline and pass it through a narrow
  `wait_for_response_id(expected_id, deadline)` wrapper. Do not build a generic
  JSON-RPC client.
- Accept only the matching response ID. Well-formed notifications and unrelated
  IDs may be ignored only until that same absolute deadline; no notification
  count policy is added without a separate resource-pressure failure.
- Malformed input and EOF fail immediately. A matching JSON-RPC error stays
  attached to its request phase. Internally preserve `timeout`,
  `invalid-payload`, `eof`, `initialize-error`, and `plugin-install-error` as
  distinct causes.
- Preserve the public failure envelope (`status: failed`, existing `reason`, and
  `error`) unless a compatibility review approves an additive detail field. The
  negative fixtures assert the cause text and that no cache-refresh success is
  emitted; they do not require a new public enum.
- Keep YAML as the operator-facing default. Internal JSON-RPC wire messages are
  protocol data, not a reason to reintroduce JSON CLI output.

Why first: this is a concrete boundedness bug in current Charness, not an
optimization hypothesis.

### Slice 2 — Bind durable critique to the reviewed snapshot

Owner: critique artifact scaffold/validator and parent orchestration receipt,
with `scripts/critique_packet_lib.py` as input producer and the existing
parent-side reviewer fingerprint helper retained for reviewer isolation.

- Add `reviewed_input_identity` beside each verdict in the durable critique
  artifact/receipt. It contains the exact packet-byte SHA-256, ordered declared
  reviewed paths plus their content digests, base `HEAD`, and the staged,
  unstaged, and declared-untracked digests scoped to those paths.
- The prepare-packet library produces the identity when it supplies review
  input; the critique artifact validator consumes it. The prepare packet is not
  itself the verdict store.
- A later difference in a declared component makes the verdict stale and
  inapplicable, not retroactively invalid. Unrelated paths do not stale it.
- Reuse the current fingerprint implementation; do not create a second shared
  worktree scanner.
- Require snapshot binding only for full critique and irreversible closeout,
  not every reversible local review.

Why second: it strengthens P4/P5 and makes the existing fresh-eye mechanism
durable before more evidence schemas depend on review claims.

### Slice 3 — Formalize the release observer record

Owner: release helper/artifact renderer and a versioned schema under the release
surface.

- Keep `payload.distinct_channel_verification` as the canonical channel
  observation. Generate one durable `charness.release_observer.v1` record after
  post-publish install refresh that embeds or derives that observation and adds
  expected version/tag/commit, remote readback, installed readback, and
  non-claims. It must not create a parallel observer verdict.
- The release helper owns the generator and schema validator. The release
  artifact renderer consumes or digest-binds that same record; do not maintain
  two manually divergent truths.
- The durable record is internal program-consumed JSON. Operator-facing CLI
  output remains YAML-first.
- Preserve distinct observer plus distinct channel. A valid record is populated
  evidence, not terminal green.

Why third: it converts a successful ad hoc release artifact into a reusable
boundary contract. Slices 2 and 3 are independently schedulable after Slice 1;
their order is maintenance priority, not a technical dependency.

### Slice 4 — Normalize advisory efficiency evidence

Owner: existing skill-efficiency A/B aggregation and session-audit reporting.

- Extend the existing A/B `results.json` and renderer rather than create an
  all-purpose evidence framework. A cost delta is `comparable` only when corpus
  identity, signal class, reconstruction status, and applicable model/parser
  identities match; otherwise render `incomparable` and no delta.
- Keep it advisory. It may inform a default change but must not block ordinary
  reversible work.
- Reuse the current outcome-grade/pass-rate fields beside every cost reduction
  so doing less cannot masquerade as efficiency.

Why fourth: a shared evidence language must precede optimization decisions.

## Probe Questions And Governance

1. Can `run-quality.sh` expose a deterministic `plan`/`explain` payload from the
   existing surfaces manifest without changing selected CI work?
2. Across at least ten representative local/CI samples, is planning or test
   execution actually on the critical path, and which tasks dominate it?
3. Does a canonical affected plan conservatively fall back to the full owner
   suite for unknown and cross-cutting paths?
4. Do real long-running Charness goals exhibit stale claims, conflicting status
   writers, or expensive state reconstruction that justify goal receipts,
   leases, or dependency fields?
5. Does an availability-gated real Codex app-server probe reveal protocol fields
   or lifecycle behavior not represented by the fake server?

| Questions | Owner | Writeback | Promotion rule |
| --- | --- | --- | --- |
| 1–3 | `quality` | `## Probe Outcomes` in this spec | affected-CI only after deterministic explain output, conservative fallback, and at least ten representative runtime samples show a material critical path |
| 4 | `achieve` | `## Probe Outcomes` in this spec | receipts/leases only after a recorded stale claim, conflicting state writer, or repeated reconstruction cost |
| 5 | root CLI control-plane owner | `## Probe Outcomes` in this spec | real-host contract change only when an availability-gated probe finds a fake-server gap |

An additional local-only session-index probe may build a disposable SQLite
prototype beside `scripts/codex_session_audit_*`. Its exit record must show
measured current scan cost, an unchanged scan parsing zero new bytes, safe
truncate/parser-version handling, and no raw tool-result retention. Promote a
production index only when that measured cost is material; otherwise delete the
prototype and retain no index.

## Probe Outcomes

None yet. Record command, corpus/source identity, result, and promotion decision
here before moving any probe into `Current Slice And Dependency Order`.

## Fixed Decisions

- The north star remains authoritative: judgment for reversible work; teeth only
  where wrong success escapes or where a stable machine form is required.
- Use current Charness owners before adding a framework: app-server helper,
  critique packet/fingerprint, release renderer, A/B report, and session audit.
- New public CLI output remains YAML-first. JSON may remain an internal wire or
  durable schema where another program is the consumer.
- Efficiency evidence is advisory and correctness-adjacent.
- Affected-CI selection cannot narrow CI until an explain-only probe and runtime
  samples justify it.
- D18 remains out of scope unless explicitly reopened.

## Deferred Decisions

- Goal JSONL receipts, typed steering, task leases, dependencies, and evidence
  taxonomy reopen only on the Question 4 recorded failure trigger.
- Shared batch cache identity or purpose-trimmed child prompts reopen only when
  the host/provider exposes the needed support and comparable child token traces.
- Real-host app-server proof as a release-time trigger reopens only after the
  Question 5 probe finds a fake-server gap; begin as an opt-in diagnostic.

## Non-Goals

- Replacing host-native multi-agent orchestration with tmux or a Charness worker
  runtime.
- Reducing the public skill catalog to Gajae-Code's four workflows.
- Importing TUI sanitization, Bun process hooks, TypeScript conventions, npm
  tarball closure, or a detached RPC-session registry.
- Treating a receipt, digest, validator, or reviewer verdict as terminal success
  at an irreversible boundary.
- Claiming token, latency, or CI speed improvement before comparable evidence.

## Deliberately Not Doing

- No mandatory consensus plan for clear reversible edits.
- No LOC/file-count delegation thresholds.
- No hard default-reduction gate or fixed approval reference.
- No new generic state/lock framework without a second Charness-shaped failure.
- No affected-test selector copied directly from a TypeScript monorepo.

## Constraints

- Every slice remains independently reviewable and can stop without committing
  later slices.
- Batch source changes before syncing generated/plugin surfaces.
- A new blocking floor needs an irreversible/form boundary or recorded
  recurrence; otherwise use an advisory or describe-first surface.
- Prompt/skill changes require the normal Cautilus planner; no evaluation runs
  without its ask-before-run contract.
- Optimization reports must record source class, command, commit/range, corpus,
  and reconstruction limits.

## Success Criteria

| ID | Criterion | Proof level |
| --- | --- | --- |
| SC1 | Notifications or unrelated responses cannot extend either app-server request beyond its own absolute deadline. | unit plus integration fixture |
| SC2 | Malformed, EOF, matching-error, and timeout causes remain distinguishable internally and never yield cache-refresh success while the public envelope stays compatible. | unit |
| SC3 | Changing a declared reviewed input makes its bound critique verdict stale; an unrelated-path change does not. | unit plus repository integration |
| SC4 | Release observer validation rejects missing target identity, observer channel, or explicit unavailable/non-claim disposition. | unit |
| SC5 | Deterministic and live/sample efficiency inputs cannot be compared unless corpus and signal-class rules permit it. | unit |
| SC6 | Every reported efficiency delta keeps correctness/outcome evidence adjacent. | unit plus report fixture |

## Acceptance Checks

- `unit`: fake app-server fixtures cover unrelated messages before a matching
  response, a continuing unrelated-message stream bounded by the original
  deadline, malformed payload, matching error, EOF, and timeout.
- `integration`: the cache-refresh command returns the current YAML public shape
  with typed failure detail and no false success.
- `unit`: critique packet tamper fixtures change one reviewed byte/path and
  invalidate the verdict binding.
- `unit`: release observer schema fixtures cover verified, unavailable, and
  malformed records.
- `unit`: efficiency fixtures reject corpus/model/signal mismatches and retain
  outcome grade beside deltas.
- `manual`: before each slice, record the owner check and non-duplication seam in
  that slice's critique receipt.

## Boundary Ownership

- App-server protocol and child lifecycle: root CLI control-plane adapter.
- Reviewer integrity and verdict binding: `critique`; `prove` only cites it.
- Release public/install observations: `release`, never `prove`.
- Efficiency posture and CI-cost proposals: `quality`; deterministic code stays
  in repo-owned scripts.
- Long-running goal state: `achieve`; host worker runtime remains host-owned.
- Verdict: `owned-correctly` for the plan; implementation must recheck per slice.

## Critique

Full spec critique completed with two bounded angles and a separate
counterweight. It kept Slice 1 first but narrowed it to per-request deadline and
response-ID waiting; moved verdict ownership to the critique artifact; required
the release observer to derive from the existing distinct-channel verdict;
constrained efficiency comparison to the existing A/B contract; moved session
indexing to a measured probe; and added probe owners/reopen triggers. It rejected
a notification-count policy, generic RPC framework, mandatory pipe-buffer test
shape, and unconditional indexing as over-worry/overbuild. Durable review:
`charness-artifacts/critique/2026-07-19-gajae-code-adoption-plan.md`.

## Canonical Artifact

This file is the implementation contract. The gather record is source evidence;
`docs/handoff.md` carries only the pickup pointer.

## First Implementation Slice

Move to `impl` for Slice 1 only: introduce the narrow per-request deadline and
response-ID wait wrapper, add the negative fake-server matrix, and prove the
operator YAML shape plus bounded response wait. Do not bundle the efficiency or
CI probes into that correctness slice.
