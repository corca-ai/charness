# Achieve Goal: Make the docs graph a checked surface, then release it

Status: draft
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-make-the-docs-graph-a-checked-surface.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-08-make-the-docs-graph-a-checked-surface.md` after confirming the draft is
  still intended.
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

Promote `awiki` from a declared integration to a REAL gate in this repo, and cut the release that carries it.

The manifest landed at `c772f147` (#566 step 1). It declares the binary and nothing consumes it. This goal closes the gap the operator named: the docs graph is currently an unchecked surface, and `awiki lint -root docs -recursive` exits 1 today.

The ordering is forced and is the whole design: the gate must be GREEN BEFORE it is promoted. Promoting first would light a red gate on day one and create pressure to weaken the floor to get past it, which is the exact condition that revokes a push grant.

Measured this session, not transcribed: `documents=40 orphans=7 islands=0 link_only_lines=229 largest_component_ratio=0.8250`.

The orphan set is NOT seven undiscoverable pages. Three of the seven (`docs/agent-task-envelope.md`, `docs/narrative-announcement-boundary.md`, `docs/retro-self-improvement-spec.md`) are linked from repo-root `AGENTS.md`/`CLAUDE.md` and are orphans only because awiki's scan root is `docs`. Widening the root is not the escape: `awiki lint -root .` reports 3564 documents, 2884 orphans, `largest_component_ratio=0.1496`, which is not a gate. `docs/` stays the scan root, and the repair is the hub that does not exist -- there is no `docs/index.md`.

Operator decisions already taken, recorded so a later session does not relitigate them: the gate is CHARNESS-INTERNAL ONLY (`run-quality.sh`, not the shipped consumer quality contract), and the orphan disposition is a new `docs/index.md` hub rather than scattered body links.

## Non-Goals

- **NOT a consumer-facing gate.** The operator scoped this to `run-quality.sh`
  in this repo only. `awiki` does not enter the shipped consumer quality
  contract, gets no `quality`-skill gate lane that runs in installing repos, and
  no consumer is required to install it. Consumers may still adopt it through
  the manifest; that is opt-in.
- **NOT a docs rewrite.** The orphan repair links pages into the graph. It does
  not restructure, merge, split, or rewrite the seven documents' contents.
- **NOT #523.** The `AGENTS.md` reduction is a separate concern with a different
  shape, and bundling a deletion into a gate-promotion release would make the
  release's blast radius unreadable.
- **NOT a claim about doc QUALITY.** Reachability is not accuracy. A graph with
  zero orphans says every page can be found, and says nothing about whether any
  page is correct or current.
- **NOT a widening of the scan root.** Measured and rejected — see `## Goal`.

## Boundaries

- **The gate must be green BEFORE promotion, never after.** Promotion order is
  the load-bearing constraint of this goal. If a slice cannot reach `exit 0`
  honestly, the correct move is to stop and report, NOT to promote with a
  baseline exception, an ignore list, or a lowered floor.
- **A weakened floor revokes the push grant.** `--no-verify`, disarming a check,
  or shrinking a gate's scope to reach green forfeits the release. This is the
  repo contract, restated here because this goal ends at a push and is therefore
  exactly where that pressure lands.
- **awiki must stay degradable for anyone who lacks it.** The binary is installed
  on this machine and is NOT in `integrations/tools/dependencies.json`. If
  promotion requires adding it there, that is a real decision about what a
  contributor must install — surface it, do not slip it in.
- External side-effect scope: the release and push are approved for the FINAL
  bundle of this goal only, once every prior slice is green. That approval is
  phase-scoped and does not carry forward. No per-slice pushing; remote CI is
  run once over the final bundled state.
- The 76 commits already unpushed at activation ride out with this release. Their
  content is not re-litigated here, but the release notes must not imply this
  goal produced them.

## User Acceptance

- Run `awiki lint -root docs -recursive` from the repo root and see **exit 0**
  with `orphans=0 islands=0`.
- Run `bash scripts/run-quality.sh` and see the docs-graph check present, named,
  and passing in the summary — not silently absent.
- Temporarily rename the `awiki` binary off PATH, re-run the gate, and see it
  report the check as NOT-RUN with a named reason rather than passing quietly.
  This is the check that the gate cannot produce a false green.
- Open `docs/index.md` and reach any of the seven previously-orphaned pages from
  it.
- Read the release notes and find the docs-graph gate described in terms of what
  it now protects.

## Agent Verification Plan

### Low-Cost Checks

- `awiki lint -root docs -recursive` exit code and summary line, per slice.
- `python3 scripts/validate_integrations.py --repo-root .` after any manifest edit.
- `python3 scripts/check_doc_links.py` — the existing link-validity gate must stay
  green while new links are added; the two checks are complementary, not
  substitutes.
- `bash .githooks/pre-commit` at each commit boundary.

### High-Confidence Checks

- Full `bash scripts/run-quality.sh`, redirected to a file and read whole (never
  piped through `tail`/`head`), at each slice boundary.
- Fresh-eye bounded review at the promotion slice. Gate promotion is verdict
  logic on a proof surface, so it owes the second review round that reads the
  repairs.
- `charness tool doctor awiki --repo-root .` after tightening the advisory
  policies, confirming the tightened policy does not turn an ordinary machine
  into a `blocking-failure`.
- A deliberate NEGATIVE test: introduce a throwaway orphan page, confirm the gate
  goes red, then remove it. A gate never observed failing is not known to work.

### External Or Live Proof

- Release publication and `git push`, at the final bundle only.
- Remote CI verdict read back through a DIFFERENT observer and a DIFFERENT
  evidence channel than the push exit code. A green push is not a green build.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Build `docs/index.md` as the docs hub and link the 7 orphans into the graph | The gate cannot be promoted red, and the hub is the missing structure — not the seven pages | `awiki lint -root docs -recursive` exit 0, `orphans=0`; `check_doc_links.py` still green | pending |
| 2 | Write the `check_doc_links.py` vs awiki overlap matrix | It is the stated PREMISE for promotion and an unmet `#518` clause; a prior handoff forbade replacement claims without it | A command-level matrix committed under `docs/`, naming what each tool does and does not answer | pending |
| 3 | Promote: add the gate to `run-quality.sh`, tighten the advisory doctor/version policies together, decide `dependencies.json` membership | The graph is green and the premise is written, so the gate can now hold | Gate named and passing in the quality summary; negative test observed red; doctor still `ok`; fresh-eye round + round 2 | pending |
| 4 | Release and push | The operator scoped the push to ride with this release | Release artifact, push, and a remote CI verdict from a distinct observer and channel | pending |

## Operator Decision Queue

- Decision: whether `awiki` joins `integrations/tools/dependencies.json`, making a
  Rust toolchain (or a release-binary install) a stated requirement for anyone
  running this repo's full quality gate
- Owner: operator
- Why deferred: it does not block slices 1-2, and the honest answer depends on
  how the gate behaves when the binary is ABSENT, which slice 3 establishes
- Unblock action: answer `yes, declare it` or `no, keep it optional and let the
  gate report not-run`
- Revisit trigger: slice 3, at the moment the gate lane is written

- Decision: whether the release is a version bump or a re-cut of the existing
  candidate, given 76 unrelated commits ride out with it
- Owner: operator
- Why deferred: it is a release-shape question, not a gate question, and slices
  1-3 are unaffected either way
- Unblock action: name the version, or say "carry the existing candidate scope"
- Revisit trigger: slice 4, before any publish command runs

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
- **Successor goal step** — required at EVERY completion, not conditionally. Add
  a `Successor goal:` line naming the next goal artifact this run's lessons
  designed, or write `Successor goal: n/a — <reason>` to say out loud that none
  is wanted. The closing goal is the only place that still holds what the session
  measured about this repo's real shape; a completion that does not spend it
  throws that away, and the next session re-derives it.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

Routing: impl — selected from installed skill metadata; slices 1-3 are code, docs, and gate-config changes against a stated contract, which is what `impl` owns, and it loads `prove` at its own stop gate for the closeout ledger. `quality` owns the slice-3 gate design review, `release` owns slice 4, and `issue` stages the `#566` closeout; each is routed at its own boundary rather than pre-declared here.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — three consequential decisions were put to the operator during shaping and answered. (1) Gate scope: CHARNESS-INTERNAL ONLY, not the shipped consumer quality contract — chosen because a consumer-facing gate is hard to reverse and would force every installing repo to install awiki or degrade. (2) Orphan disposition: a new `docs/index.md` hub, not scattered body links — chosen after measuring that three of the seven orphans are scan-scope artifacts and that no hub exists. (3) Release and push: approved for the FINAL bundle of this goal only, conditional on every gate being green by its own strength; a weakened floor forfeits it. The remaining irreversible-boundary item, remote CI readback through a distinct observer and channel, is planned in `## Agent Verification Plan` and is not yet proven.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design north star](../../docs/design-north-star.md) — the governing standard,
   read while shaping. Two facets bear directly on this goal. **Teeth belong only
   where a wrong answer escapes**: an unchecked docs graph lets an unreachable
   page ship unnoticed, which is a real escape, so a gate is warranted — but the
   same principle is why the gate stays internal rather than being pushed into
   every consumer, where it would add teeth without a matching escape. **A gate
   may force a question; it may not declare completion**: a green docs-graph gate
   claims reachability and nothing about accuracy, and the release notes must not
   overstate it. The irreversible boundaries crossed are the release publish and
   the push, so each owes confirmation through a different observer and a
   different evidence channel than the command that performed it.
2. [issue #566](https://github.com/corca-ai/charness/issues/566) — as CORRECTED
   in its own comments, not as originally filed. Step 1 (the manifest) landed at
   `c772f147`; this goal is step 2. Its non-claims instruct re-verifying the
   transcribed orphan count before acting, which was done.
3. [issue #518 reconciliation contract](../spec/2026-08-07-issue-518-quality-declaration-reconciliation-contract.md)
   — owns the declaration-to-verdict lifecycle a promoted gate must satisfy, and
   contains the quality-dependency clause still unmet after step 1.
4. [captured awiki fixture](../quality/fixtures/awiki-0.5.0-docs-lint.json) — the
   frozen 0.5.0 observation, checked by `scripts/check_quality_tool_fixtures.py`.
   Its `final_consumer` is `null`, which is precisely what this goal changes.
5. [open-issue opinion](../audit/2026-08-08-open-issue-opinion.md) — ranked this
   work second, and says explicitly that it carries no authority and that four of
   its positions were corrected by the operator within one session. Argue with
   it; do not inherit it.
6. `../craken-agents/docs/documentation.md` — a sibling repo that does NOT install
   charness, so a shape comparison only. Its transferable half is the DISCLOSURE
   discipline: it states in prose exactly which lanes and hooks do not run its
   docs graph check. That is the honest inverse of a false green.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

**Q1 — goal scope.** Options: awiki-only ending at the release; awiki plus the
cheap closeout items (`#560`, handoff refresh); awiki plus `#523`. **Chosen:
awiki-only.** Rejected the bundles because a release whose scope spans a gate
promotion AND an unrelated prose deletion cannot be described honestly in one set
of release notes, and because a single-subject arc keeps the proof clean. The
cheap items are not abandoned — they are handled outside this goal.

**Q2 — orphan disposition.** Options: investigate first then propose; link
everything with no exceptions; register the current seven as a baseline exception
and gate only new orphans. **Chosen: investigate first**, which then produced the
finding that reframed the whole slice — three of seven are scan-scope artifacts,
and no `docs/index.md` exists. Rejected the baseline-exception route explicitly:
it enshrines the broken state as the floor, which is the shape the sibling repo's
own exception table warns about by demanding a per-row removal condition.

**Q3 — gate scope.** Options: charness-internal only; ship it in the consumer
quality contract. **Chosen: internal only.** Rejected consumer-facing because it
is the hard-to-reverse direction: every installing repo would need awiki or a
degrade path, and the manifest already lets any consumer opt in. Internal-first
is the reversible order — it can be widened later once this repo has run it.

**Q4 — orphan repair shape.** Options: a `docs/index.md` hub; body links in
existing pages; per-document judgment. **Chosen: the hub.** The absence of any
index is the structural gap, and it fixes the three scan-scope orphans as a side
effect. Rejected pure body-linking because it leaves the docs tree with no entry
point, and rejected per-document judgment as a longer slice for a marginal gain
over the hub.

**Not asked, and deliberately so:** whether to widen awiki's scan root. It was
MEASURED rather than debated — `-root .` gives 2884 orphans over 3564 documents,
which settles it without an interview question.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this goal artifact; `integrations/tools/awiki.json`; the
  `run-quality.sh` gate lane added in slice 3; `docs/index.md` and the seven
  linked pages; the slice-2 overlap matrix; and issue `#566`. Retro, packet,
  reviewer, and lock records are terminal evidence, not reviewed inputs.
- Frozen target: commit slices 1-3 first, then bind the closeout packet to that
  exact commit SHA. Any later edit to a reviewed input invalidates packet
  identity and the lock, and requires rebinding — including a docs edit, since
  `docs/index.md` is a reviewed input here.
- Fresh-eye: a bounded `bounded-reviewer` subagent, spawned unnamed, in a
  different agent context. Slice 3 changes verdict logic on a proof surface, so
  it owes a SECOND round that reads the repairs. The reviewer boundary is
  fingerprint-snapshotted before each round and VERIFIED BEFORE any repair is
  applied, so drift is attributable.
- Verification lock: `bash scripts/run-quality.sh` redirected to a file and read
  whole; evidence under `.charness/quality-failure-logs/` for any failing check.
  The docs-graph lane must be named in the summary, not merely absent-and-green.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status
  and release/push bookkeeping outside the reviewed identity. The remote CI
  verdict is terminal evidence gathered AFTER the push and must come from a
  different observer and channel than the push exit code.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

Run these yourself; none of them requires trusting this run's report.

1. `awiki lint -root docs -recursive; echo "exit=$?"` from the repo root —
   expect `exit=0` and `orphans=0 islands=0` on the summary line.
2. `bash scripts/run-quality.sh > /tmp/q.txt 2>&1; echo $?; grep -n 'awiki\|docs-graph' /tmp/q.txt`
   — the lane must appear BY NAME. A gate you cannot find in the summary is not a
   gate you have.
3. Break it on purpose: `printf '# Stray\n\nunlinked.\n' > docs/stray-check.md`,
   re-run step 1, expect a NON-zero exit naming `stray-check`, then
   `rm docs/stray-check.md`. This is the only step that proves the gate can fail.
4. `PATH=/nonexistent:$PATH bash scripts/run-quality.sh 2>&1 | grep -i awiki` —
   with the binary unavailable the run must say the check did not run, and must
   not report a clean docs verdict.
5. Open `docs/index.md` and confirm you can reach `agent-task-envelope`,
   `proof-semantics-adapter`, and `prompt-mutation-policy` from it.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
