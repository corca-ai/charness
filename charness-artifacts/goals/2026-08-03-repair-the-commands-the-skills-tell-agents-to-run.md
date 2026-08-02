# Achieve Goal: Repair the commands the skills tell agents to run

Status: complete
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: all four lanes complete, pushed as `ac39c9f5`, remote CI green.
- Current slice intent: repair the counted 13 broken command references,
  disposition the charness-script references, and ship the resolution check as
  a non-blocking advisory. One unchanged intent across all three lanes, so
  critique fired once per lane boundary rather than per commit
  (meaningful-slice-cadence).
- Next action: none — goal complete. Follow-ups live in #477 / #478 and in
  `## Operator Decision Queue`.
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

A shipped skill tells an agent to run a command. **13 of those commands cannot
run**, in this repo or any other: the reference says
`<repo-root>/scripts/<name>.py` while the file lives in
`skills/public/<skill>/scripts/<name>.py`. An agent that follows the instruction
literally gets "No such file or directory".

Measured 2026-08-02, statically, over every `.md` under `skills/public`,
`skills/shared`, `skills/support`:

| form | count | state |
| --- | --- | --- |
| `$SKILL_DIR/...` (inside the skill package) | 91 | **0 resolution failures** |
| `<repo-root>/scripts/X.py`, file actually in the skill package | **13** | **broken here AND everywhere** |
| `<repo-root>/scripts/X.py`, file is a charness repo script | 9 | resolves here, unresolved in a consuming repo |
| referenced file that exists nowhere | **0** | — |

Concentration: `announcement` 4, `quality` 3, `setup` 2, `narrative` 2,
`gather` 1, `retro`/others 1.

This is the same class as #471/#475/#476 — a rule that cannot fire where it was
written — but for the first time it is **statically decidable and already
counted**. No agent testimony, no host, no temp repo: the file is there or it is
not.

The 2026-08-02 sweep had this in its hands and let it go. Verifiers refuted the
"inert" claims by showing that `inventory-dispatch.md` dispatches the SAME
script via `$SKILL_DIR`, which proves a DIFFERENT path works — not the one the
document told the agent to run. Taking that refutation at face value is the
error this goal repairs.

## Non-Goals

- **Not building an installed-layout / temp-repo proof channel.** It was the
  previous draft's Lane A and the measurement made it unnecessary for THIS
  defect class: a static grep found all 13 in seconds, and a consumer repo would
  cost far more while telling us the same thing.
- **Not answering whether the 91 `$SKILL_DIR` scripts EXECUTE** in a repo with
  no adapter and no charness `scripts/`. Existence and executability are
  different claims. There is no evidence either way today; it is recorded as the
  named follow-up, not smuggled in.
- **Not rewriting how skills reference scripts.** `$SKILL_DIR` already works for
  91 references; the 13 are typos against that working convention, not a design
  problem.
- **Not arming a blocking gate on first sight.** Floor-Addition Restraint: this
  check is cheap and static, which makes a gate tempting — the call gets made
  explicitly in Lane C with the recurrence evidence, not assumed.
- Not the E-cluster, not D41–D49.

## Boundaries

- **External side-effect scope — APPROVED BY THE OPERATOR 2026-08-02, all three
  items, for this goal.** (1) `git push` to `main` plus the `quality-core` runs
  it triggers. (2) Filing issues for what Lane B cannot resolve. (3) Closing an
  issue a lane fully resolves — still through the close path's floor, with a
  DELEGATED resolution critique running BEFORE the close call; the approval
  covers the decision to close, never the evidence floor.
  The agent had recommended a narrower grant (push blanket, issues case-by-case,
  no closing this goal) on the grounds that issue creation is the one action
  GitHub cannot undo. The operator chose the wider grant; recorded so a later
  session reads this as a deliberate call rather than an unexamined default.
  **This approval is scoped to THIS goal and does not carry to the next one.**
  NOT in scope at all: a release publish, a tag, a version bump, or any
  `cautilus evaluate` run.
- In scope: the 13 broken command references, the 9 charness-script references,
  the shipped `plugins/charness/` mirror of every touched file, and regression
  tests.
- In scope (repairs): the 13 are unambiguous — the file exists, the path is
  wrong, and correcting it refuses nothing new. The 9 are NOT unambiguous and
  are a judgement call (Lane B).
- Stop conditions: (1) if correcting a reference changes what a skill DOES
  rather than where it points, stop and treat it as a design change. (2) If any
  repair would newly refuse a checked-in artifact or newly APPLY a floor to
  repos previously outside it, it becomes an operator decision (D49). (3) If
  Lane C starts growing past a single static check, cut it back to the
  measurement.
- **Cut order if short: C, then B, never A.** A is the counted defect.

## User Acceptance

- **Lane A**: all 13 references point at a path that resolves, verified by
  re-running the same static measurement that found them, with the count going
  13 → 0 and the denominator restated. A regression test asserts that
  `<repo-root>/scripts/X.py` and `$SKILL_DIR/...` references in shipped skill
  surfaces resolve — so this cannot silently come back.
  **Scope of that test, stated because the sentence above is easy to read as
  total coverage** (carve-outs surfaced by the closeout-claims review): it
  covers `skills/<public|support>/*` and `plugins/*/skills|support/*` in both
  layouts. It does NOT check `$SKILL_DIR` targets in `skills/shared` prose
  (undecidable there — `$SKILL_DIR` is whichever skill included the file; 4 such
  references exist and were confirmed by hand), targets containing `<`/`>`
  placeholders, non-`.py` targets such as `check-links-internal.sh`, or bare
  `scripts/X.py` outside a `## References` bullet. The shipped-layout half is a
  ratchet against known findings, not an every-reference assertion.
- **Lane B**: each of the 9 charness-script references carries a recorded
  disposition — `repointed` / `documented as authoring-repo-only` /
  `issue #N` — and the artifact says which, with the reason. A reader can tell
  a deliberate authoring-repo reference from an unnoticed one.
- **Lane C**: the advisory fires on a broken reference and is pinned by a test
  proving it can never change an exit code, plus a counted answer to "how did 13
  accumulate" — that count is the evidence a future blocking promotion needs,
  and its absence is why the gate was not taken now.
- **Every figure carries `<value> — <source>`**, and every count states its
  denominator AND when it was taken.
- **Non-claim carried in writing**: this proves the referenced paths RESOLVE. It
  does not prove the scripts run correctly in a consuming repo — that is the
  named follow-up.

## Agent Verification Plan

### Low-Cost Checks

- **Re-run the measurement before and after, and record WHEN.** The before-count
  is 13/91/9/0 taken 2026-08-02 after the previous goal's fold.
- **Distinguish `<repo-root>/` from `$SKILL_DIR/` in every query.** Conflating
  them produced a wrong 33/55 first count in the session that shaped this goal;
  the corrected split is 13/91/9/0. A measurement that cannot tell the two apart
  will report noise as signal.
- **A refutation that proves a DIFFERENT path works is not a refutation.** That
  is exactly how the 2026-08-02 sweep lost these 13.
- Targeted `pytest` AND `ruff check` in the same breath.
- Sync `plugins/` mirrors before validators (`mutate -> sync -> verify`).
- Obey the dup-ratchet edit advisory when it fires rather than deferring to the
  closeout aggregate.
- File the issue first, then write its number into prose.

### High-Confidence Checks

- One bounded fresh-eye round per slice; **TWO for Lane C if it wires a check
  that renders a verdict**, round 2 reading the REPAIRED surface.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify`
  the MOMENT the reviewer returns, before any parent write.
- **Adversarial verification defaulting to refuted on every Lane B disposition**
  — and this time, reject a refutation that merely names another working path.
- A closeout-claims review by a DISTINCT observer before the complete flip.
- **Build test inputs from source constants, never by retyping.**

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers — **only after the approval
  in `## Boundaries` is granted** — confirmed per P4 by a different observer AND
  a different channel than the push exit code.
- Expect the pre-push changed-line mutation lane to refuse if new branches are
  added; cover them as they are written.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | DONE — Repoint the 13 broken command references and pin them with a regression test over ALL shipped skill surfaces | 13 counted commands an agent is told to run and cannot; unambiguous, refuses nothing new, and the file already exists at the right place | Before/after count 13 → 0 from the same query, the test, synced mirrors | complete |
| B | DONE — Disposition the 9 charness-script references: repoint, document as authoring-repo-only, or file | They resolve here and not in a consuming repo, which is the #475 shape — but unlike the 13 they may be deliberate, so each needs a judgement recorded | A per-reference disposition table with reasons; issues for what is not resolved | complete |
| C | DONE — Wire the static path-resolution check as a NON-BLOCKING advisory (operator-decided 2026-08-02), count how the 13 accumulated, and record the recurrence evidence a later gate decision would need | An advisory is the restraint checklist's default on a first finding; the recurrence count is what a blocking promotion requires and nobody has taken it | The advisory firing on a broken reference, a test pinning it cannot change an exit code, the accumulation count with its method, and the deferred gate call written down | complete |
| D | DONE — Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green | complete |

## Operator Decision Queue

- Decision: should `plan_risk_interrupt.py` run inside installed plugins at all? Filed as #477 rather than repaired, because the fix would make a command that has NEVER run in an installed plugin start running for every `impl` and `spec` invocation.
- Owner: operator
- Why deferred: it is a behaviour change, not a path typo, so this goal's stop condition (1) routes it out of scope. Every other lane completed without it.
- Unblock action: decide between repointing to a layout-independent form and deleting the call outright; both options and the layout arithmetic are in #477.
- Revisit trigger: the next slice that touches `impl`/`spec` SKILL.md, or any report of a missing risk-interrupt in an installed host.

- Decision: should public skill prose be allowed to invoke plugin-level scripts via the `<plugin-dir>/` placeholder? Three references (#478) instruct a consumer to run a charness authoring-repo script.
- Owner: operator
- Why deferred: the scripts ARE exported to the plugin, so `<plugin-dir>/` would resolve — but that is a convention decision about what public skills may depend on, not a typo fix, and the remaining six references in the same family are deliberate and correctly self-scoping.
- Unblock action: pick one of the three options recorded in #478 (repoint, reword as charness-only evidence, or drop the `gather` References bullet).
- Revisit trigger: a consuming repo reporting a `critique` or `gather` command that cannot run.

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

Routing: impl — selected from installed skill metadata for the code-and-docs slices (repointing 14 reference sites, authoring the advisory, and its regression tests); `prove` owns the slice closeout ledger it loads at the stop gate.

Routing: quality — selected for validation posture: the dup-ratchet edit advisory was obeyed at the edit rather than deferred to the closeout aggregate, and the `run-quality.sh` wiring plus its timing-layer classification are quality-contract surfaces.

Routing: issue — selected for the two filings this run produced (#477, #478), each recording the observed problem before proposing a fix.

Routing: critique — selected for the bounded fresh-eye rounds at each lane boundary, run twice for the verdict-rendering surface per the repo's Critique Discipline.

Routing: achieve — goal lifecycle operator, selected from installed skill metadata for a three-lane repair with an operator-decided advisory boundary; quality's dup-ratchet and run-quality wiring were consulted at the edit rather than deferred to closeout; issue owns the two filings (#477, #478); critique ran as bounded fresh-eye rounds at each lane boundary, twice for the verdict-rendering surface.

Gather: n/a — the URLs in `## Context Sources` are GitHub issue links to this same repo's tracker plus in-repo relative paths, all read through `gh`/the local tree; no external page became working context, so there is nothing for `gather` to durably capture.

Release: n/a — no version bump and no install-manifest edit. Regenerating the `plugins/` mirror is a sync surface under the `mutate -> sync -> verify` rhythm, not a release surface.

Issue closeout: n/a — #477 and #478 were CREATED by this run as deferred work and are explicitly not close-intended; #475/#476 appear in `## Context Sources` as context only. No tracked issue is resolved by this goal.

## Discuss Before Activation

- Discuss before activation: RESOLVED — both activation items settled by the
  operator in-transcript on 2026-08-02, and this goal is ready to run.
  (1) APPROVED — external side effects: `git push` to `main` plus the CI it
  triggers, filing new issues, and closing an issue a lane resolves are all
  approved for this goal by the operator, who chose a wider grant than the agent
  recommended. Closes still run through the close path's floor with a delegated
  resolution critique first. Scoped to this goal; does not carry forward. (2) **RESOLVED / DECIDED 2026-08-02** — Lane C ships a
  NON-BLOCKING advisory, not a gate. The operator took the restraint
  checklist's own default: what exists today is one FINDING (13 references), not
  a recorded RECURRENCE, and promotion to a blocking floor waits for the
  recurrence count Lane A produces. Recorded honestly: the usual argument for
  advisory-first — that a floor false-fires and trains token-theater — is WEAK
  here, because this check is fully deterministic and a false positive is
  structurally impossible. The gate was defensible; the restraint rule was
  followed anyway, because this repo's recorded failure is adding floors on
  first sight rather than missing them. **Size is NOT an open item** — this goal
  is materially smaller than the last one: one counted repair set, one
  disposition table, one recorded decision.
- **Both activation items are settled. This goal is ready to run.**
## Slice Log

### Slice 1: Lane A — repoint the 13 broken command references

- Objective: Repoint every <repo-root>/scripts/X.py reference whose file actually lives in the skill package, and pin the repaired state with a regression test over all shipped skill surfaces.
- Why this approach: The 13 are unambiguous: the file exists, the prefix is wrong, and correcting it refuses nothing new. Two forms were used, each matching the sanctioned local convention — a package-relative `scripts/X.py` bullet in a ## References list, and $SKILL_DIR/scripts/X.py in prose. Both are the spellings skill_ergonomics_lib.has_portable_path_ambiguity whitelists.
- Commits:
- What changed: 14 sites / 13 distinct scripts across skills/public/{announcement,gather,narrative}/SKILL.md and skills/public/{quality,setup}/references/*.md; NEW scripts/inventory_skill_script_references.py; NEW tests/test_skill_script_references.py; regenerated plugins/charness/ mirror; 2 intentional families classified in charness-artifacts/quality/dup-review.json.
- Alternatives rejected: Rejected building a temp consuming repo to resolve everything mechanically (the goal's Non-Goal): a static resolution query answered the same question in seconds. Rejected reshaping how skills reference scripts: $SKILL_DIR already works for the large majority; these were typos against that working convention.
- Targeted verification: Before/after static measurement, same query: broken 13 -> 0 in the authoring layout. Regression test proven to BITE by temporarily restoring one real broken reference (skills/public/gather/SKILL.md:152) — it failed naming the exact file, line, and true location, then passed again on restore. pytest tests/test_skill_script_references.py = 15 passed (2026-08-02, after round 2). ruff clean. check_python_lengths clean.
- Test duplication pressure: check_dup_ratchet.py --summary went hard-block (2 new code families) at the edit advisory, not deferred to closeout. Family 5505a8794c55f12d = the new advisory's --repo-root argparse boilerplate vs handoff/prepare_chunk_packet.py; family 8b788ea5965aeef7 had NO member in this diff (pure scan rotation, all three members untouched). Both classified intentional with reasons: a portable skill package must not import repo-level scripts/, and check_documented_command_flags reads the option surface off each script's own parser. Re-ran: status clean, 0 new families.
- Critique: One bounded fresh-eye round (bounded-reviewer, unnamed, read-only), boundary snapshot+verify clean both sides. 12 findings; 9 folded, 3 dispositioned. See Lane A/C critique note in Plan Critique Findings.
- Off-goal findings: Pre-existing dangling-rewrite text at skills/public/quality/references/adapter-contract.md:132-133 ('such as / like'), confirmed present at HEAD before this slice — not introduced here.
- Lessons carried forward: The authoring tree and the shipped plugins/ mirror are DIFFERENT trees, and a reference can resolve in one and not the other. The goal's inherited 13/91/9/0 measurement was taken over the authoring tree only; scanning the mirror found defects that measurement structurally could not see.
- Metrics: 14 reference sites / 13 distinct scripts repaired; measurement re-run before and after with the same query.

### Slice 2: Lane B — disposition the charness-script references

- Objective: Give every <repo-root>/scripts/X.py reference whose file really is a charness repo script a recorded disposition, so a reader can tell a deliberate authoring-repo reference from an unnoticed one.
- Why this approach: Unlike the 13, these are a judgement call: <repo-root>/ is the DOCUMENTED placeholder for a script that only resolves in a consuming repo, so the prefix is not evidence of a mistake. Each needed its context read, not a pattern match.
- Commits:
- What changed: 1 repointed (skills/public/quality/references/adapter-contract.md:496); 2 issues filed (#477, #478); 6 scripts recorded as deliberate authoring-repo-only, unchanged.
- Alternatives rejected: Rejected repointing the whole set to <plugin-dir>/scripts/: the scripts ARE exported there, so it would resolve, but whether public skill prose should invoke plugin-level scripts is a convention decision and not a typo fix. Recorded as the open question in #478 rather than decided unilaterally. Rejected leaving validate_skill_ergonomics as authoring-only: the packaged helper is standalone-runnable with identical output, so the reference resolves in both layouts after repointing and refuses nothing new.
- Targeted verification: Set enumerated from the advisory itself, not by hand: 8 distinct scripts / 15 sites after the repoint (was 9/16). Every context read at its site before dispositioning. The packaged validate_skill_ergonomics.py was RUN standalone (python3 skills/public/quality/scripts/validate_skill_ergonomics.py --repo-root .) and passed, proving the repoint does not depend on the repo-level shim.
- Test duplication pressure:
- Critique: The bounded reviewer's most severe finding was against this lane: validate_skill_ergonomics had been parked in the test's known-exception set under a rationale written for a DIFFERENT defect class. Confirmed and repaired by repointing it and removing it from the set, plus a separate test that this class can never be parked as an exception.
- Off-goal findings: skills/public/setup/references/default-surfaces.md:126 references <repo-root>/scripts/check-links-internal.sh — same family, a .sh so outside the .py measurement. Same illustrative disposition as its two .py neighbours.
- Lessons carried forward: A refutation that exhibits a different working path is not a refutation — but the inverse also holds: a reference sharing a spelling with a real defect is not automatically a defect. Six of these were deliberate and self-describing; only three were phrased as instructions a consumer would actually follow.
- Metrics:

### Slice 3: Lane C — non-blocking advisory and the accumulation mechanism

- Objective: Ship the static path-resolution check as a NON-BLOCKING advisory, pin that it cannot change an exit code, and answer how 13 accumulated.
- Why this approach: Operator decision 2026-08-02 took the restraint checklist's default: one finding is not a recorded recurrence. The answer to 'how did 13 accumulate' turned out to be a mechanism rather than a count, which is stronger evidence for a future gate decision than a number would have been.
- Commits:
- What changed: scripts/inventory_skill_script_references.py (advisory, no --strict flag and no non-zero return path); wired into scripts/run-quality.sh as queue_selected inventory-skill-script-references, whose WARN: prefix run-quality.sh:362 surfaces non-blocking; tests pinning the posture.
- Alternatives rejected: Rejected a blocking gate — defensible here and unusually so, because this check is fully deterministic and a false positive is structurally impossible, but declined per the recorded operator call. Rejected a --strict flag: an escalation flag that exists gets wired into a gate by habit, so the option surface carries none and a test reads the real parser to prove it. Rejected growing the check past one static question (goal stop condition 3): the reviewer's proposal to resolve shared prose against every including skill package is recorded as a follow-up, not built.
- Targeted verification: 15 tests (2026-08-02, after round 2). The exit-code pin runs against a repo that DOES have a broken reference (a zero exit on a clean repo would prove nothing) and asserts the finding was actually emitted. The no-escalation-flag test reads the real argparse parser, replacing an earlier source-grep that had already produced one false failure by matching the docstring EXPLAINING the absence. Live output 2026-08-02, final: `2 of 406 (203 authoring/203 shipped)` — both the filed #477 sites — plus an explicit note that 18 shipped references are unverifiable from this tree.
- Test duplication pressure: CORRECTED at closeout — the ratchet fired TWICE, and only the first was at the edit. First fire (2 families) was handled at the edit per the checklist. The round-2 restructuring of the same file then ROTATED the fingerprints, producing a second hard-block at the closeout aggregate with 3 new families (the repo-wide sys.path bootstrap idiom across 11 files, the argparse pair re-fingerprinted, and a 4-line relative_to guard). All classified intentional with reasons; final status clean, 0 new families. The lesson is that edit-time discipline is necessary and not sufficient: a later refactor of an already-classified file re-opens the question.
- Critique: Round 1 produced 9 folded repairs to this surface. Because the advisory and its tests render verdicts about other code, a SECOND bounded round reading the repaired surface is owed and was run.
- Off-goal findings:
- Lessons carried forward: ACCUMULATION MECHANISM (the recurrence evidence a later blocking promotion needs): the 13 were not missed by accident. <repo-root>/ is a DOCUMENTED portable placeholder in check_doc_links.py:50 — the sanctioned escape for commands that only resolve in a consuming repo — so three silences overlap on exactly that spelling. (1) has_portable_placeholder exempts the prefix by design. (2) iter_unresolved_command_targets skips any candidate containing < or >, which every <repo-root> token does. (3) Inside a portable skill package classify_backtick_token returns None for every token, disabling the backtick reference check entirely. The escape hatch is indistinguishable from a typo, so the defect is invisible BY CONSTRUCTION, not by oversight. That is why prose-only would not have held, and it is the evidence a gate promotion should be argued from.
- Metrics:

## Lane B Dispositions

Every `<repo-root>/scripts/X.py` reference whose file really is a charness repo
script. Set enumerated by `scripts/inventory_skill_script_references.py`
(`status: authoring_repo_script`), 2026-08-02: **9 distinct scripts / 16 sites**
before this lane, **8 / 15** after the one repoint. Final dispositions: 1
repointed, 4 rows routed to issue #478 (7 sites / 6 scripts once the reviewer's
additions are counted, including one `.sh` the `.py`-only measurement never
saw), and 4 upheld as deliberate authoring-repo references.

`<repo-root>/` is the *documented* placeholder for a command that only resolves
in a consuming repo, so the prefix alone is not evidence of a mistake. Each
reference was read at its site.

| script | sites | disposition | reason |
| --- | --- | --- | --- |
| `validate_skill_ergonomics.py` | `quality/references/adapter-contract.md:496` | **repointed** to `$SKILL_DIR/scripts/...` | Named as "the canonical quality path" — an instruction, not a description. The packaged helper is standalone-runnable (run 2026-08-02, identical output), so the repoint resolves in both layouts and refuses nothing new. A repo may still wrap it behind its own entrypoint, which the reworded sentence now says. |
| `check_title_slug_drift.py` | `critique/references/angle-selection.md:117`, `critique/references/rename-critique.md:85` | **issue #478** | Phrased as an instruction to the reader ("Run … as deterministic evidence") inside a skill a consuming repo actually runs. Not repaired in place: the script is exported to the plugin's own scripts dir, so a `<plugin-dir>/` spelling would resolve, but whether public skill prose should invoke plugin-level scripts is a convention call, not a typo fix. |
| `refresh_current_pointer.py` | `gather/SKILL.md:153` | **issue #478** | A `## References` bullet sitting among package-relative bullets, so it reads as an affordance of the skill and is not one for a consumer. |
| `refresh_current_pointer.py` | `gather/references/asset-refresh.md:40` | **authoring-repo-only** | Illustrative comparison only ("mirrors … in shape, not strictly POSIX-atomic"); nothing is instructed to run. |
| `record_rca_event.py` | `shared/references/rca-ledger-append.md:12` | **authoring-repo-only** | Exemplary: the doc itself says the step is "repo-gated, not consumer-facing" and "in any other repo … a silent no-op: do not create the script". The condition is already stated where a reader meets it. |
| `check_supply_chain.py` | `quality/references/security-overview.md:29`, `security-npm.md:14`, `security-pnpm.md:15`, `security-uv.md:15` | **authoring-repo-only** | Per site, not per family: `security-overview.md:29` sits under a "Current `charness` Slice" heading ("`charness` now ships …"); `security-npm.md:14` and `security-uv.md:15` self-scope in the sentence itself ("for the current `charness` bar", "currently owns this offline alignment check for `charness`"). `security-pnpm.md:15` carried NO qualifier — a round-2 reviewer caught that the disposition was unsupported there — so the disposition was EXECUTED rather than asserted: that sentence now carries the same `charness` scoping as its three siblings. |
| `check_supply_chain_online.py` | `quality/references/security-npm.md:20`, `security-pnpm.md:22`, `security-uv.md:25` | **authoring-repo-only** | Like the `check_supply_chain.py` row, the disposition was EXECUTED, not asserted: a closeout-claims reviewer showed that none of the three sentences actually named `charness`, so all three now read "`charness` wraps that path explicitly in …" with their own package manager's command (`npm audit --json`, `pnpm audit --json`, `uv audit --frozen`). Each sits under a "Manual Or Networked Follow-Up" heading that hands the decision to the reader's team. |
| `check_doc_links.py`, `check-links-internal.sh`, `migrate_backtick_file_refs.py` | `setup/references/default-surfaces.md:125`, `:126`, `:127` | **issue #478** | REFUTED by the adversarial pass, which was the only round to reach it. Initially recorded `authoring-repo-only` ("a pointer to an example, not a command"). Three independent grounds against that: nothing in the bullet, sentence, or heading scopes it to `charness`; `See <path>` is imperative and the file IS the payload, with no inline fallback; and every OTHER `<repo-root>/` in this same file denotes the consumer's own file (`:102`, `:107`, `:131`, `:136`), so a reader parses this one identically. Audience is maximally consumer-facing — `setup/SKILL.md:78` loads it when scaffolding docs in a fresh repo. The pass also found `check-links-internal.sh` in the same sentence, which appeared in NO earlier count because the original measurement scanned only `.py`. |
| `validate_skills.py` | `shared/references/binary-preflight.md:173` | **issue #478** | RE-DISPOSITIONED by the closeout-claims review. Initially recorded `authoring-repo-only` ("audience is someone authoring a charness skill"), which does not hold: it is an imperative step in a numbered migration checklist, and the shared reference is cited by the consumer-facing `create-skill` and `create-cli`, whose purpose is authoring skills IN the consumer's repo. Same criterion that routed `check_title_slug_drift.py` to #478; added there as a fourth site. |

### Adversarial pass over this table

The verification plan required "adversarial verification defaulting to refuted
on every Lane B disposition". A closeout-claims reviewer found that pass had not
been run, so it was run: a bounded reviewer re-examined every
`authoring-repo-only` row with the default verdict set to REFUTED, explicitly
instructed that a refutation exhibiting a DIFFERENT working path is not a
refutation.

**Six of seven rows survived; one did not** (`default-surfaces.md`, above), and
the pass found a third broken token in that sentence — `check-links-internal.sh`
— that appeared in no earlier count because the original measurement scanned
only `.py`.

The separating principle it articulated, which no earlier round had stated:
**a site is safe when the reader's executable instruction is satisfiable without
resolving the flagged path** — because the clause is a third-person attribution
(`check_supply_chain*`), a shape comparison (`asset-refresh.md`), or an
existence predicate that is SUPPOSED to fail for a consumer
(`record_rca_event.py`, whose doc says so explicitly). It is broken when the
flagged path IS the deliverable the reader is sent to fetch or run.

Two `authoring-repo-only` reasons were also EXECUTED rather than asserted during
this run, after reviewers showed the cited text did not support them: the
`charness` qualifier now present at `security-pnpm.md:15` and at all three
`check_supply_chain_online.py` sites.

Non-claim for this lane: this records where each reference POINTS and what its
prose intends. It does not prove any of these scripts run correctly in a
consuming repo. The adversarial pass is a reading of prose mood and audience,
not an execution.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — teeth belong
   where a wrong answer escapes. A documented command that cannot run is a wrong
   answer that escapes silently, and this one is statically decidable.
2. [the 2026-08-02 sweep](../audit/2026-08-02-can-this-rule-fire-sweep.md) — it
   HAD these 13 and lost them, because verifiers refuted "inert" by exhibiting a
   different working path. Read `### Refuted cannot-fire claims` before Lane B.
3. [the completed goal](./2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md)
   and its [retro](../retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md)
   — the class, and why round 2 on a repaired surface keeps earning its cost.
4. [issue #475](https://github.com/corca-ai/charness/issues/475) and
   [issue #476](https://github.com/corca-ai/charness/issues/476) — the two closed
   worked examples of "fires here, dead there"; #476's close records why the
   non-retroactive direction was chosen, which Lane B will face again.
5. [implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
   *Floor-Addition Restraint* — Lane C's checklist, and the reason Lane C is a
   decision rather than a foregone conclusion.

## Interview Decisions

1. **Static repair, or an installed-layout proof channel?** Family considered:
   {temp consumer repo that resolves everything mechanically; static reference
   audit; both; neither, hand back}. **Chosen: static.** The draft this replaces
   proposed the consumer-repo channel and called Lane A speculative. The
   measurement settled both halves at once: the defect is REAL (13 counted) and
   the channel is UNNECESSARY for it (a grep found all 13 in seconds). Rejected:
   the channel, for costing far more and telling us the same thing about this
   class. Anti-anchoring: `axis: cost of the instrument vs the finding` — the
   instinct to build a rig is strongest right after a class has embarrassed you,
   and that is when it is least justified.
2. **Are the 13 and the 9 one lane or two?** Family considered: {one sweep; two
   lanes; fix 13 only}. **Chosen: two lanes.** The 13 are unambiguous (file
   exists, path wrong, refuses nothing new); the 9 may be deliberate
   authoring-repo references. Merging them would let a judgement call ride in on
   a typo fix's certainty. Anti-anchoring: `axis: certainty is not uniform`.
3. **Gate the check now?** Family considered: {blocking gate; advisory; prose
   only; decide in-goal}. **Chosen (operator, 2026-08-02): a non-blocking
   advisory**, with a gate reconsidered only after Lane A counts the recurrence.
   A cheap deterministic check that catches a real defect is the most tempting
   possible floor, and this repo's recorded reflex is to add one on first sight.
   Rejected: the gate — defensible here, and unusually so, because the standard
   objection (a floor that false-fires trains token-theater) does not apply to a
   check whose false positives are structurally impossible; it was still declined
   because one finding is not a recurrence. Rejected: prose only, which is what
   let 13 accumulate unnoticed. Anti-anchoring: `axis: teeth timing` — the
   strongest case for teeth is right after the defect embarrasses you, which is
   also when the evidence for permanence is thinnest.

## Public-Skill Validation Review

Five public skills changed (`announcement`, `gather`, `narrative`, `quality`,
`setup`), so the closeout gate required a scenario/dogfood review decision.

**Decision: no scenario coverage change, and no Cautilus run.** Every change to
these five packages is a reference PATH edit — where a documented command points
— with no edit to what any skill instructs, decides, or produces. The single
prose rewordings (`quality/references/adapter-contract.md:496`, plus the
`charness` qualifier added to `security-pnpm.md:15` and to the three
`check_supply_chain_online.py` sentences) name the same helpers with the same
behaviour. `git diff` over the five packages contains no change to a workflow
step, an output shape, or a refusal condition, so no maintained scenario's
expected behaviour moves. Stated precisely, because the looser spelling would
be wrong: the repoint DID edit `adapter-contract.md`, an adapter-contract
reference — it changes which path that sentence names and adds a wrapping
clause. What is unchanged is the SEMANTICS: same rules, same helper, same
behaviour.

A `cautilus evaluate` run is explicitly NOT in this goal's scope
(`## Boundaries`), and this repo is ask-before-run for it. Recorded as a
decision rather than executed proof, and acknowledged with
`run_slice_closeout.py --ack-cautilus-skill-review`.

Non-claim: this is a reasoned decision from the diff's shape, not behavioural
evidence. It does not claim any evaluator scenario was executed for this slice.

## Proof-Surface Disposition

`scripts/inventory_skill_script_references.py` renders a verdict about other
artifacts, so it is a proof surface and its authoring is an irreversible
boundary. Two bounded read-only fresh-eye rounds by distinct agents, each
bracketed by `reviewer_boundary_fingerprint.py` snapshot/verify (both `clean`,
no drift).

Fresh-eye pass: scripts/inventory_skill_script_references.py — two bounded rounds; round 1 raised 12 findings (9 folded), round 2 read the repaired surface and raised 11 more, including two CONFIRMED blockers the first round could not see because the code did not exist yet.

Round 2 is the round that earned its cost, exactly as the repo contract predicts
for verdict-logic changes:

- The round-1 repair that wired the advisory into `run-quality.sh` shipped a
  **gate failure of the class it was fixing** — a check wired to a surface
  without satisfying that surface's own contract. `check_timing_layer_completeness.py`
  requires every `queue_selected` label to carry a verdict row in
  `docs/conventions/validator-timing-layers.md`, and
  `test_every_queued_repo_script_gate_has_a_seeded_harness_stub` requires a
  seeded stub. Both were missing; both CONFIRMED by running them; both repaired.
- The round-1 vacuity guard gated on `skill_packages_scanned` when the vacuity
  condition is `references_scanned` — so a repo with packages but no matching
  prose still printed a clean all-clear, one level down from the case the repair
  addressed.
- `test_no_shipped_reference_is_broken_because_its_file_is_in_the_package` had
  no floor of its own, and the aggregate `>100` floors are dominated by
  `$SKILL_DIR` rows — so it could have passed forever while the candidate
  population it names fell to zero. Now floors the `repo-root` form directly.
- A Lane B disposition reason was unsupported at one of its four cited sites
  (`security-pnpm.md:15` carried no `charness` qualifier). The disposition was
  executed rather than restated.

Non-claim: these two rounds reviewed the surface's LOGIC. Neither round executed
the advisory against a consuming repo, and neither proves the referenced scripts
run correctly there.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

The plan itself was critiqued before activation (see `## Interview Decisions`
and `## Discuss Before Activation`, both resolved by the operator 2026-08-02).
Reviewer provenance for the RUN's three bounded rounds — all `bounded-reviewer`,
read-only, unnamed, each bracketed by `reviewer_boundary_fingerprint.py`
snapshot/verify, all three `clean` with no drift:

1. **Round 1, Lane A+C code** (window `lane-ac-round1`) — 12 findings, 9 folded.
   Most severe: `validate_skill_ergonomics` had been parked in the test's
   known-exception set under a rationale written for a different defect class.
   Folded by repointing it and adding a test so that class can never be parked.
   Raised-but-not-folded (over-worry): a latent basename-collision hazard in the
   shipped-layout classifier that cannot fire today, and a ratchet key that
   omits `line` — both recorded, neither repaired, because the failure needs a
   reference that does not exist.
2. **Round 2, the REPAIRED surface** (window `lane-ac-round2`) — 11 findings,
   including 2 CONFIRMED blockers round 1 could not see because the code did not
   exist yet. Detail in `## Proof-Surface Disposition`.
3. **Closeout-claims review by a distinct observer** (window `closeout-claims`)
   — audited the artifact's CLAIMS rather than its code, and found four that did
   not hold: an unreconciled 13-vs-14 count, a disposition reason false at 3/3
   cited sites, a Slice Log that contradicted its own retro in the flattering
   direction, and a promised Lane B adversarial pass with no recorded evidence.
   All four are repaired above; the fourth was repaired by actually running the
   pass. This round is why the artifact does not read as a clean run.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- **[#477](https://github.com/corca-ai/charness/issues/477)** — `$SKILL_DIR/../../../scripts/plan_risk_interrupt.py`
  in `impl/SKILL.md:41` and `spec/SKILL.md:26` resolves in the authoring tree and
  overshoots the plugin root in the shipped one, and both call sites end in
  `2>/dev/null || true`, so it has silently never run in an installed plugin.
  Filed rather than repaired: repointing would make a never-running command start
  running, which is stop condition (1) — a behaviour change, not a path typo.
  Pinned in `tests/test_skill_script_references.py::KNOWN_SHIPPED_FINDINGS` so
  the count may shrink, never grow.
- **[#478](https://github.com/corca-ai/charness/issues/478)** — the three Lane B
  references phrased as instructions a consuming repo would follow. See the
  disposition table.
- Pre-existing dangling-rewrite text at
  `skills/public/quality/references/adapter-contract.md:132-133` ("such as /
  like", ~95 chars against a file wrapping near 78). Confirmed present at HEAD
  before this run via `git show HEAD:...`, so not introduced here. Not repaired:
  outside this goal's scope and unrelated to script references.
- **Named follow-up, unchanged from the goal's Non-Goals:** whether the
  in-package scripts EXECUTE in a repo with no adapter and no charness
  `scripts/`. Existence and executability are different claims, and this run
  produced no evidence either way.
- **Reviewer proposal, deliberately not built (stop condition 3):** shared prose
  under `skills/shared` uses `$SKILL_DIR/../../shared/...`, which is undecidable
  from the shared root and is therefore skipped by the advisory. A decidable rule
  exists — resolve shared prose against every skill package that includes it and
  require it to resolve in all of them. Four such references exist and all four
  were manually confirmed to resolve in both layouts; building the rule would
  grow Lane C past one static check.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md
Host log probe: charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md
Disposition review: charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md

Executed proof, with its date:

- Static measurement, 2026-08-02, same query before and after: references whose
  file is in the skill package but whose prose says `<repo-root>/scripts/` went
  **13 to 0** in the authoring layout, and **0** in the shipped layout.
  **13 vs 14, reconciled** (a closeout-claims reviewer flagged that the artifact
  used both without saying which was which): the counted unit is **13 distinct
  scripts**, occupying **14 reference sites**, because
  `seed_retro_memory.py` is referenced twice — at
  `setup/references/retro-memory-seam.md:18` and
  `setup/references/greenfield-flow.md:36`. Verified against `HEAD` with
  `git show`. Both figures are correct; every repaired site was one of the
  counted defects, so no scope was added.
  One inherited figure was WRONG and is corrected here: the goal's
  `Concentration` line reads `quality 3 … retro/others 1`, but `git grep` over
  `HEAD` finds no `<repo-root>/scripts/*.py` reference anywhere under
  `skills/public/retro`. The true split is `quality 4` (the three `inventory_*`
  references plus `check_runtime_budget.py`) and `retro/others 0`. The
  mis-attribution was in the measurement this goal inherited, not in the repair.
  Denominator: **406 references scanned (203 authoring / 203 shipped)** across
  **47 scanned package roots** — the tool counts each package once per layout,
  so that is ~23 distinct skill packages seen twice, not 47 skills. 0 docs
  unreadable.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only` →
  **6716 passed, 0 failed, 38.17s** (2026-08-02). Run explicitly because the
  handoff records that a `completed` closeout gate is not broad proof.
- `python3 -m pytest tests/test_skill_script_references.py` → **15 passed**
  (2026-08-02, after the round-2 repairs; 14 test functions, one parametrized ×2).
- `run_slice_closeout.py --verification-lock --ack-cautilus-skill-review
  --produce-mutation-coverage` → `Closeout status: completed`.
- The regression test was proven to BITE, not merely to pass: temporarily
  restoring one real broken reference failed it with the exact file, line, and
  true file location; restoring the repair returned it to green.
- Two bounded fresh-eye rounds by distinct `bounded-reviewer` agents, each
  bracketed by `reviewer_boundary_fingerprint.py` snapshot/verify — both
  `clean`, no drift, no parent-attributed drift.

External proof (approved in `## Boundaries` for this goal):

- `git push origin main` → `9f405a28..ac39c9f5`. The pre-push gate refused
  TWICE before it succeeded, both times correctly, both times from the
  changed-line mutation lane: first naming 5 uncovered changed lines (one of
  which turned out to be DEAD code, deleted rather than tested), then the
  `__main__` entrypoint (covered by a subprocess test rather than a
  `# pragma: no cover`, because "the documented command actually runs" is this
  goal's whole subject). Final pre-push: **83 passed, 0 failed**.
- **Remote CI confirmed per P4 by a different observer AND a different channel
  than the push exit code.** Channel 1, `gh run watch 30741697583 --exit-status`
  → 0. Channel 2, the commit check-runs API, independently:
  `Core deterministic gates: completed/success` and
  `Changed-line mutation coverage (push/PR mirror): completed/success`.
  Channel 3, `git ls-remote origin main` → `ac39c9f5`, matching the pushed SHA.
- Honest reading of one signal that looks bad: the combined-status API returns
  `state: pending` for this commit. That is NOT a pending check — it reports
  `total_count: 0`, and the same call returns `pending`/`0` for the previously
  green `9f405a28`. This repo publishes check-runs, not legacy commit statuses,
  so the combined-status endpoint has nothing to aggregate. Recorded rather than
  quietly dropped, because a green claim resting on an unexplained `pending` is
  exactly the shape this goal exists to distrust.

Non-claims, carried in writing:

- This proves the referenced paths RESOLVE. It does **not** prove the scripts
  run correctly in a consuming repo — that remains the named follow-up.
- No consuming repo, temp repo, or installed host was exercised. Every claim is
  a static file-existence argument over two checked-in trees.
- No `cautilus evaluate` run, no release publish, no tag, no version bump.
- The 2 remaining shipped-layout findings are real and unrepaired by choice
  (#477); they are not a passing verdict.

## User Verification Instructions

Each command is read-only and takes seconds.

1. **The repair, from the same query that found the defect** — expect
   `all 406 (203 authoring/203 shipped) skill script references resolve` to be
   contradicted only by the two filed #477 lines:

   ```bash
   python3 scripts/inventory_skill_script_references.py --repo-root .
   ```

   Expected: `WARN: 2 of 406 …` naming only the two `plan_risk_interrupt.py`
   sites, plus a `note:` that 18 shipped references are unverifiable from here.

2. **The regression test that pins it** (15 tests):

   ```bash
   python3 -m pytest tests/test_skill_script_references.py -q
   ```

3. **Prove the test BITES rather than merely passes** — reintroduce one real
   defect and watch it fail with the exact file, line, and true location:

   ```bash
   sed -i 's|`scripts/advise_google_workspace_path.py`|`<repo-root>/scripts/advise_google_workspace_path.py`|' skills/public/gather/SKILL.md
   python3 -m pytest tests/test_skill_script_references.py -q   # expect 1 failed
   git checkout -- skills/public/gather/SKILL.md
   ```

4. **Confirm the advisory cannot fail a run**, even holding a finding:

   ```bash
   python3 scripts/inventory_skill_script_references.py --repo-root . ; echo "exit=$?"
   ```

   Expected: `exit=0` while `WARN:` lines are printed.

5. **The two open decisions this run deliberately did not take**: issues #477
   and #478 (see `## Operator Decision Queue`).

## Auto-Retro

Retro dispositions: applied: `scripts/inventory_skill_script_references.py` now resolves references against the SHIPPED `plugins/` layout as well as the authoring one, so a check about a shipped surface is measured on the tree that actually ships — the retro's "measured the wrong tree" waste item
Retro dispositions: applied: `tests/test_skill_script_references.py` floors each reference FORM separately (`skill-dir`, `repo-root`, `references-bullet`) instead of one aggregate count, so a test cannot pass while the population it names falls to zero
Retro dispositions: applied: the advisory's no-escalation-flag test reads the real `argparse` parser rather than grepping source text — the proxy-assertion waste item, which had already produced one false failure against its own docstring
Retro dispositions: applied: `docs/conventions/validator-timing-layers.md` and `tests/quality_gates/support.py` now carry the two registrations a new `run-quality.sh` `queue_selected` label owes, closing the round-1 repair's own gate failures
Retro dispositions: issue #477 (novel: first recorded instance of a skill reference whose relative depth is correct in the authoring tree and wrong in the shipped mirror; the sibling scan closed the class at exactly 2 sites)
Retro dispositions: issue #478 (recurs: the #475 "fires here, dead there" class — skill prose instructing a consumer to run an authoring-repo script)
Retro dispositions: accepted-risk: the advisory emits a standing `WARN: 2 of 406` until #477 is decided; suppressing a real, filed defect to keep the gate quiet would make the advisory lie, and the count is ratcheted so it cannot grow silently
Retro dispositions: applied: the Lane B adversarial default-to-refuted pass was actually RUN after a closeout-claims reviewer found it promised-but-skipped; it refuted one more row and surfaced a `.sh` token no `.py`-only count had ever seen, both now in #478
Retro dispositions: applied: the Slice Log's dup-ratchet line was corrected where it contradicted the retro in the flattering direction, and the 13-vs-14 headline was reconciled against `git show HEAD` (13 distinct scripts / 14 sites; `seed_retro_memory.py` is referenced twice)
Retro dispositions: out-of-scope: making the consumer-only escape spelling distinguishable from a typo (the Engelbart counterfactual's T-change) — the highest-leverage item this run surfaced, but a convention change to `check_doc_links.py` rather than a path repair; recorded in the retro's `## Portable Candidate`

Structural follow-up: applied: the two-layout resolution check plus its form-floored regression tests in `tests/test_skill_script_references.py` — the `## Sibling Search` scan closed the transferable class at exactly 2 instances (both filed as #477), and any new instance in either layout is now detected automatically rather than by hand.
