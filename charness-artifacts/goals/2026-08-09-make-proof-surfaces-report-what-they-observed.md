# Achieve Goal: Make proof surfaces report only what they observed

Status: active
Created: 2026-08-09
Activation: `/goal @charness-artifacts/goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 6 — render `describe_goal_closeout_shape`'s floors from live constants.
- Current slice intent: slices 1-2 are DONE. The reviewable-intent unit now in
  progress is writing the overlap matrix that is the stated PREMISE for
  promoting awiki, then promoting it on the connectivity metrics. Critique and
  broad proof do not re-fire within one unchanged intent — update this when the
  intent changes, not per commit (meaningful-slice-cadence).
- Next action: delete the hardcoded `>= 30 chars` / `~20+ chars` literals and
  render them from the live constants, with a test that moves a constant and
  asserts the rendered text follows.
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

Every proof surface in this repo should say what it actually observed, and stay silent about what it did not. Four surfaces currently break that, in two directions, and this goal repairs all four and then ships them as a major release.

**Direction 1 — a surface that observes nothing and reports clean.** The docs graph has never been checked. `awiki lint -root docs -recursive` exits 1 today with `documents=40 orphans=7 islands=0 link_only_lines=229` (measured this session), and no gate consumes it. The manifest landed at `c772f147` (#566 step 1); nothing reads it.

**Direction 2 — surfaces that report a verdict they did not observe.** Three of them, all the same disease, and the north star already named it: P3 says an enumerated list *"rots and still misses the case it never listed."*

- `goal_artifact_phase_routing` decides what work a goal did by keyword-matching its prose, then REFUSES `Status: complete` on the guess. Demonstrated wrong in BOTH directions: real debug work written in plain English does not trigger, while the word `hypothesis` in passing does, and an `airport gate` metaphor triggers the quality route.
- `describe_goal_closeout_shape` states in its own docstring that it *"never re-declares the contract... rendered from the LIVE enforced constants, so the surfaced shape cannot drift from the gate"* — and hardcodes `>= 30 chars` and `~20+ chars` at lines 103, 115, 272. One constant edit silently stales six operator-facing strings. The module that documents the cure has the disease.
- `validate_attention_state_visibility` scans docstrings for status vocabulary, so English prose using a banned word trips a gate about exit-zero states. Two recorded instances now: #302's `silently-skipped`, and a parsing docstring in this session.

**The generative pattern is one thing: RESTATEMENT instead of RENDERING.** Every defect found this session is one source of truth restated elsewhere and drifting — five cloned cue matchers, `MIN_OPTOUT_REASON` in three modules, a verbatim duplicate trigger predicate, the hardcoded constants above, one routing rule written three times for three executors, and an awiki install note contradicted by the repo's own generated lock. The cure is already invented here: `describe_goal_closeout_shape` renders from live constants and `check_doc_authoring_preflight` *"REUSES each real validator -- it never forks their logic."* It is applied unevenly, including inside itself.

The handoff planner is the sharpest instance and is repaired first, because it changes how everything after it is authored: it asks the MODEL to retype the user's message into a regex classifier, so a paraphrase gets classified instead of the request. A deterministic classifier fed model-authored prose is not deterministic; it launders a judgment through a regex.

The release is a MAJOR bump, `3.5.0` -> `4.0.0`, decided by the operator.

## Non-Goals

- **NOT a consumer-facing awiki gate.** Operator decision: `run-quality.sh` in
  this repo only. awiki does not enter the shipped consumer quality contract and
  no installing repo is required to have it. Adoption stays opt-in through the
  manifest.
- **NOT a sweep of every enumerated list in the repo.** Four named surfaces, each
  with demonstrated wrong output. A general hunt for keyword lists is the kind of
  unbounded scope that produced the bloat the north star diagnoses.
- **NOT #523.** The `AGENTS.md` reduction is a different concern.
- **NOT a docs rewrite.** Slice 2 links pages into the graph; it does not
  restructure, merge, or rewrite their contents.
- **NOT a claim about doc QUALITY.** Reachability is not accuracy.
- **NOT a widening of awiki's scan root.** Measured and rejected: `-root .` gives
  3564 documents / 2884 orphans / `largest_component_ratio=0.1496`.

## Boundaries

- **Every gate must be green BEFORE it is promoted, never after.** Applies first
  to awiki and then to any floor this goal rewrites. If a slice cannot reach
  green honestly, stop and report — do NOT promote with a baseline exception, an
  ignore list, or a lowered floor.
- **A weakened floor revokes the push grant.** `--no-verify`, a disarmed check,
  or a shrunk gate scope forfeits the release. Restated here because this goal
  ends at a push and rewrites four floors, which is exactly where that pressure
  lands.
- **Four of the eight slices author or change a PROOF SURFACE**, which the north
  star classifies as IRREVERSIBLE: a wrong pass ships to every consuming repo,
  other agents act on its green, and a fail-open gate is silent by construction.
  Each of those slices owes a fresh-eye round, and the second round that reads
  the repairs.
- **Replacing a guess with a declaration must not silently weaken the floor.**
  Slice 5 removes a content guess; if the replacement lets a goal close that the
  old floor would have refused, that is a regression to name, not a simplification
  to celebrate.
- External side-effect scope: the release and push are approved for the FINAL
  bundle only, once every prior slice is green. Phase-scoped, does not carry
  forward. No per-slice pushing; remote CI runs once over the final bundled state.
- The already-unpushed range rides out with this release. Its content is not
  re-litigated here, and the release notes must not imply this goal produced it.

## User Acceptance

- `awiki lint -root docs -recursive` reports `orphans=0 islands=0` with
  `largest_component_ratio=1.0000`. **AMENDED 2026-08-09 by operator decision**,
  after the original "exits 0" criterion was measured unreachable: awiki's exit
  code also fails on `link_only_lines`, of which this repo has 229 — and 139 of
  those are its own 80-column prose wrapping putting a link alone on a physical
  line, not context-free links. Proven on a 2-page synthetic wiki: zero orphans
  plus one bare bullet link still exits 1, and lint has no rule-selection flag.
  Reaching exit 0 would mean reflowing ~224 lines across 28 files, which
  Non-Goals forbids. The gate therefore asks the CONNECTIVITY question awiki's
  own manifest says it is for, and says out loud that it does not judge
  link-only style. The link-only rule is worth pursuing (operator), just not as
  this gate and not by a reflow sweep.
- `bash scripts/run-quality.sh` shows the docs-graph check present, named, and
  passing — not silently absent.
- Rename `awiki` off PATH, re-run: the gate reports the check NOT-RUN with a
  named reason rather than passing quietly.
- A goal artifact whose Slice Log says `Traced the failure to an off-by-one`
  is treated the same as one that says `root-cause` — the routing floor no longer
  depends on which words the author happened to choose.
- `grep -n '30 chars' skills/public/achieve/scripts/describe_goal_closeout_shape.py`
  returns nothing: the number is rendered, not typed.
- A Python docstring may contain the English word "skipped" without tripping the
  attention-state gate, while a genuine exit-zero `skipped` status still does.
- Ask the handoff planner for the constraints on a surface BEFORE writing into
  it, and get the rules — not a judgment on content that does not exist yet.

## Agent Verification Plan

### Low-Cost Checks

- `awiki lint -root docs -recursive` exit code and summary line, per slice.
- `python3 scripts/validate_integrations.py --repo-root .` after manifest edits.
- `python3 scripts/check_doc_links.py` stays green as new links are added.
- `bash .githooks/pre-commit` at each commit boundary.
- Targeted pytest for each rewritten floor, run before the broad gate.

### High-Confidence Checks

- Full `bash scripts/run-quality.sh`, redirected to a file and read whole (never
  piped through `tail`/`head`), at each slice boundary.
- **Every rewritten floor keeps a test for the case it exists to catch.** Slice 5
  replaces a content guess with a declaration, and the risk is a floor that stops
  refusing anything: a goal that crossed a phase boundary and recorded NO routing
  must still be refused. Pin that as a test before the swap, not as a judgment
  after it. Replaying the old and new trigger over the checked-in goal artifacts
  is a cheap way to see what moved, but it is a diagnostic — the test is the
  contract.
- A deliberate NEGATIVE test per gate: make it fail on purpose, observe red,
  revert. A gate never observed failing is not known to work.
- Fresh-eye bounded review on each proof-surface slice, plus the second round
  that reads the repairs.
- `charness tool doctor awiki --repo-root .` after tightening the advisory
  policies, confirming an ordinary machine does not become a blocking failure.

### External Or Live Proof

- Release publication (`3.5.0` -> `4.0.0`) and `git push`, final bundle only.
- Remote CI verdict read back through a DIFFERENT observer and a DIFFERENT
  evidence channel than the push exit code. A green push is not a green build.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | DONE. Handoff planner: delete the natural-language keyword layer in favour of explicit `--intent`, add a rules-without-a-target mode to the docs preflight, and move the constraint forecast into `required_reads` | FIRST because it changes how every later slice is authored — the rest of this goal writes into gated surfaces, and this is what lets an author know the rule before the gate says no | `--intent` is the only routing path; preflight prints rules for an empty draft; a handoff/doc draft passes its gates on the first try | done |
| 2 | DONE. Build the docs index hub and link the 7 orphans into the graph | awiki cannot be promoted red, and the missing hub is the structural gap — not the seven pages | `orphans=0 islands=0 ratio=1.0000` measured; negative test observed red; hub adds ZERO link-only lines; `check_doc_links.py` still green | done |
| 3 | DONE. Write the `check_doc_links.py` vs awiki overlap matrix | It is the stated PREMISE for promotion and an unmet `#518` clause; a prior handoff forbade replacement claims without it | A command-level matrix naming what each tool does and does not answer, every row measured, with runnable reproductions | done |
| 4 | DONE. Promote awiki: add the gate to `run-quality.sh`, tighten the advisory doctor/version policies together, and register `awiki` in charness's own `dependencies.json` | The graph is green and the premise is written, so the gate can now hold | `PASS docs-graph` named in the summary; FAIL and UNPROVEN both observed through the runner; doctor still `ok`; two review rounds | done |
| 5 | DONE. `goal_artifact_phase_routing`: replace the content GUESS with a declaration the author makes; the gate checks the declaration's form, not what work happened | It is teeth on a keyword guess that is wrong in both directions, and it ships to all five consumer repos | Replay over 185 checked-in goals: 156 quality + 47 debug triggers dropped, ZERO gained, `impl`/`issue` unchanged — every change is the prose guess ceasing to fire. Both recorded false positives pinned as tests | done |
| 6 | `describe_goal_closeout_shape`: render `MIN_OPTOUT_REASON` and the queue floor from the live constants instead of typing them | The module that documents the cure has the disease, and one constant edit stales six operator-facing strings | No literal floor numbers left in the file; a test that changes the constant and asserts the rendered text follows | pending |
| 7 | `validate_attention_state_visibility`: separate a status VALUE from English prose so a docstring may use the word | Two recorded false positives (#302, and this session) is a rot pattern, not bad luck | The recorded false positives pass; a genuine exit-zero `skipped` status still fails | pending |
| 8 | Release `4.0.0` and push | The operator scoped the push to ride with this release | Release artifact, push, and a remote CI verdict from a distinct observer and channel | pending |

## Operator Decision Queue

- Decision: RESOLVED 2026-08-09 — the release is a MAJOR bump, `3.5.0` -> `4.0.0`
- Owner: operator (answered during shaping)
- Why deferred: not deferred; recorded so slice 8 does not re-ask
- Unblock action: none outstanding
- Revisit trigger: none. Release-note wording is explicitly NOT a gate on this
  goal; do not reopen this as a drafting question.

Nothing else is queued, and two items that were queued here have been removed
because they were not operator decisions:

- **`dependencies.json` membership is already settled** by the internal-gate
  decision, and asking again was a mistake. The file is `repo_root`-scoped —
  charness's own — and a consumer gets its own copy seeded by `setup`. Its only
  effect is a `staged: true|false` flag on tool-recommendation payloads. It
  reaches no consumer, so it cannot conflict with keeping adoption opt-in.
  Slice 4 registers `awiki` there as a plain consequence of charness's own gate
  consuming it.
- **"Acceptable verdict change" was invented ceremony.** Whether the rewritten
  routing floor still refuses what it should is a TEST, not a judgment call, and
  it belongs in the verification plan. Moved there.

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

Phases: quality — this run's recorded work crossed the quality-gate boundary (a new `docs-graph` lane, three rewritten floors); no debug phase was entered, because nothing here started from an unexplained failure.
Routing: impl — selected from installed skill metadata; the slices are code, docs, and gate-config changes against a stated contract, which `impl` owns, and it loads `prove` at its own stop gate. `quality` owns the gate-design review in slices 4-7, `release` owns slice 8, and `issue` stages the `#566`/`#567` closeouts; each is routed at its own boundary rather than pre-declared here.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — four consequential decisions were put to the operator during shaping and answered. (1) awiki gate scope: CHARNESS-INTERNAL ONLY, because a consumer-facing gate is the hard-to-reverse direction. (2) Orphan disposition: a docs index hub, after measuring that three of seven orphans are scan-scope artifacts. (3) Goal scope: WIDENED from awiki-only to the four proof surfaces — I argued against this on single-subject grounds and withdrew the objection, because the widened set has a truer shared subject (a surface reporting only what it observed) and it describes a MAJOR bump far better than awiki plus unrelated edits would. (4) Release: MAJOR, `3.5.0` -> `4.0.0`, approved for the final bundle only and conditional on every gate being green by its own strength; release-note DRAFTING is explicitly not a gate on this goal. The remaining irreversible-boundary item — remote CI readback through a distinct observer and channel — is planned, not proven.

## Slice Log

### Slice 5 — the routing floor declares instead of guessing (done)

- The two prose guesses are DELETED. `_DEBUG_RECORD` (hypothesis|root-cause|rca)
  and `_QUALITY_RECORD` (quality|gate|validator|pytest) decided what work a goal
  DID by matching words, then refused `Status: complete` on the guess. Measured
  first: the quality guess fired on 157 of 185 checked-in goals, mostly on the
  word "gate" — a trigger that fires on 85% of a corpus is describing the repo's
  vocabulary, not discriminating between goals.
- `impl` and `issue` were KEPT, because neither is a prose guess: both read a
  structural record the author wrote (`What changed:`/`Commits:`, a literal
  `closes #N`). Only what was actually broken changed.
- The author now declares `Phases:` in `## Coordination Cues`, and the floor
  checks the declaration's FORM. The declaration is FORCED for goals created from
  2026-08-09 that record work — otherwise trading the guess for an optional
  declaration would hand every author a silent bypass. A gate may force a
  question; it may not declare completion.
- **Corpus replay:** 156 quality + 47 debug triggers dropped, ZERO gained, and
  `impl`/`issue` moved for no goal. Every change is the same rule ceasing to
  fire. This is a WEAKENING for those goals and is named as one, not celebrated.
- **Dogfooding caught the repair carrying its own disease.** The first draft
  searched the declaration's VALUE for phase names, so this goal's own
  `Phases: quality — ... no debug phase was entered` DECLARED debug. The value is
  now read as a token list, and everything after the separator is the author's
  reason. Pinned by a test.
- The tests that pin what the floor exists to catch were written BEFORE the swap
  and pass on both sides, so a floor that stopped refusing anything would have
  been visible rather than celebrated as a simplification.
- Non-claim: `issue_closeout_triggered`'s close-keyword arm still reads recorded
  work, but it requires a literal `closes #N` — a declaration of intent, not a
  topic guess — and it is shared with the coordination floor, so it is out of
  this slice's scope by the goal's own no-sweep boundary.

### Slice 4 — the docs-graph gate (done)

- `scripts/check_docs_graph.py` is a named `docs-graph` lane in `run-quality.sh`.
  It gates CONNECTIVITY (`orphans`, `islands`), reuses the runner's existing
  `UNESTABLISHED_EXIT=3` -> UNPROVEN channel rather than inventing one, and names
  what it did NOT judge on every run, including the passing one.
- All three arms observed through the real runner, not just the script:
  `PASS docs-graph` in the summary; a planted orphan produced
  `FAIL docs-graph` naming `unreachable: stray-check`; a `PATH` without awiki
  produced `UNPROVEN docs-graph` and a summary reading "established nothing".
- **The slice plan's "tighten the advisory doctor/version policies" step was
  measured WRONG and not done.** `doctor_policy: required` makes any machine
  without awiki a `blocking-install-needed` doctor failure (measured: exit 1),
  which the same plan's verification forbids. A non-advisory version policy would
  block a maintainer who merely upgrades awiki. Neither buys safety: the risk is
  handled at the point of CONSUMPTION, where the lane reports UNPROVEN on the
  actual breakage instead of on a version number. The manifest note that told a
  future session to tighten them is replaced with the measurement.
- Two bounded review rounds, boundary fingerprint verified clean before each
  repair. Round one found a REAL fail-open: no `documents` floor, so an empty
  scan root passes vacuously — confirmed live, an empty root prints
  `ok ... documents=0` and EXITS 0. It also found the return code discarded, a
  `float()` crash that would render FAIL on an unobserved graph, and that the
  passing fixture was INVENTED with no captured `ok` run in the repo.
- Round two caught the same invented-fixture defect one level down: the
  `// island=1` block header was my belief, not a capture. Now captured. Three
  real awiki outputs live in `tests/fixtures/` and drive the tests.
- Round-two repairs are accepted unreviewed per the two-round cap.

### Slice 3 — the overlap matrix (done)

- [docs/docs-graph-checks.md](../../docs/docs-graph-checks.md) states the split in
  one sentence: `check_doc_links.py` asks "does this reference RESOLVE?" per link;
  `awiki lint` asks "is this page REACHABLE?" per graph. Neither is a superset.
- **Measured, not asserted, and one row inverts the obvious assumption:**
  `awiki lint` reports `ok` on a link to a page that does not exist. Broken links
  are invisible to it, surfaced only by the separate `awiki wanted` and framed as
  a page you might want to create. An empty stub likewise only moves
  `content_coverage`; lint still passes. The rules that actually FAIL are orphan,
  island, and link-only-line.
- That is the promotion premise in one fact: before the index hub, seven pages
  were unreachable while `check_doc_links.py` was correctly green, because every
  link resolved. The green gate was answering a different question honestly.
- The runnable reproductions were executed verbatim from the page and reproduce
  the documented numbers exactly (`content_coverage=0.6667`, `islands=1
  ratio=0.6000`).
- The page builds its example brackets from shell variables, because this repo's
  link gate validates markdown links inside fenced blocks too and the fixtures
  deliberately link to files that must not exist. Written literally, the page
  would fail the gate it documents.

### Slice 2 — docs index hub (done)

- `docs/README.md` groups all 40 pages by the question each one answers, so the
  seven orphans are reachable without already knowing their filenames. Measured
  after: `documents=41 orphans=0 islands=0 largest_component_ratio=1.0000`.
- **The stated remedy's premise failed, and the check caught it before the
  slice was shaped around it.** "Link the orphans, then awiki exits 0" is false:
  exit 0 also requires `link_only_lines=0`. Proven on a synthetic 2-page wiki
  (zero orphans + one bare bullet link still exits 1) and by the absent
  rule-selection flags. Of this repo's 229, 139 are its own 80-column wrapping
  putting a link alone on a physical line. Operator amended the acceptance
  criterion to the connectivity metrics.
- The hub adds **zero** link-only lines. Measured, then repaired: a first draft
  added 3, because a long path pushed the description onto the next physical
  line. The rule is line-based, so a few words before the link satisfy it.
- Negative test observed: an unlinked `docs/stray-check.md` moved the count to
  `orphans=1` and named the page, then reverted to 0.
- Passed `check_doc_authoring_preflight`, `check_doc_links`, and markdownlint on
  the FIRST try, which is slice 1's own acceptance criterion demonstrated.

### Slice 1 — declared routing + rules-before-authoring (done)

- **Deleted, not tuned.** `--invocation-text` and `chunked_routing_lib.should_fire_chunker`
  (with both pattern lists and the trigger fixture test) are gone. Routing is
  declared: `--intent {auto,chunked_routing,pickup,refresh}`, the structural
  `--invoked-directly`, and a new `--pickup-target` declaration replacing the
  "does the invocation text pin one task?" guess.
- **The undeclared run now says so.** `--intent auto` with no structural signal
  resolves to `judge_from_user_request` AND returns a `judge_the_user_request`
  next action. Round-one review caught that it otherwise fell through to
  `refresh_handoff` — a worse guess than the regex, because unconditional and on
  the writing side.
- **Rules without a target.** `check_doc_authoring_preflight.py` with no `--path`
  prints the rules, owned by the new `scripts/doc_authoring_rules.py`. Every line
  is rendered: a live constant, or the verdict the owning validator returns when
  probed with a sample. Three remedy sentences were extracted into
  `check_doc_links.py` constants so the gate and the forecast cannot say
  different things.
- **The forecast moved into `required_reads`**, gated on whether the resolved
  next action WRITES the artifact — not on the intent, which left a pickup sent
  to prune a bloated artifact briefed by nothing (round-two finding).
- Two bounded review rounds ran, both unnamed `bounded-reviewer` spawns, boundary
  fingerprint verified clean before each repair. Round one: 2 blockers (the
  fall-through above; stale doc claims naming the deleted regex and fixture as
  live mechanism) plus 6 lesser. Round two: no blockers, 2 fixed findings (an
  uncorrected sibling claim in the claim-fidelity registry; a repair test that
  would still pass if its repair were reverted). Round-two repairs are accepted
  unreviewed per the two-round cap.
- **Claim narrowed on review.** "No routing decision is inferred from prose" is
  false as stated: `chunked_routing_parser` still keyword-filters entries out of
  the ARTIFACT's prose. The true claim is that nothing is inferred from the
  user's message. The artifact is an observable; a retyped message is not.
- **Non-claim carried forward:** the `pickup` and `pickup-ambiguous` eval arms no
  longer discriminate (the planner cannot observe a "pinned task" any more, and
  the scenario cannot declare one at bootstrap). Annotated in both spec and
  registry, discrimination moved to unit tests, re-scoping filed as follow-up.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design north star](../../docs/design-north-star.md) — read while shaping, and
   it did not merely bless this goal, it NAMED it. **P3**: an enumerated list
   *"rots and still misses the case it never listed"* — which is the exact defect
   in three of the four surfaces here. **The boundary section**: authoring or
   changing a proof surface is IRREVERSIBLE, because a fail-open gate is silent
   by construction and ships to every consuming repo; that is why four slices owe
   two review rounds. **P5**: a gate may force a question, it may not declare
   completion — which is why slice 5 replaces a guess with a declaration rather
   than with a better guess. The counter-warning applies too: *"what this does
   not license is a gate that checks gates"*, so none of these slices may be
   repaired by adding a new gate on top.
2. [authoring-preflight convention](../../docs/conventions/authoring-preflight.md)
   — its opening sentence is slice 1's whole justification: *"Know the
   deterministic constraint before you author into a gated surface, so an existing
   gate does not catch an avoidable rework cycle after the fact."* The contract
   already exists and was not discoverable from the surface where authoring
   happens.
3. [issue #566](https://github.com/corca-ai/charness/issues/566) as CORRECTED in
   its comments — step 1 landed at `c772f147`; slices 2-4 are step 2.
4. [issue #567](https://github.com/corca-ai/charness/issues/567) — the handoff
   planner findings that slice 1 repairs.
5. The superseded awiki-only draft, readable at
   `git show 2f569520:charness-artifacts/goals/2026-08-08-make-the-docs-graph-a-checked-surface.md`.
   It was never activated and is removed rather than left to join the fifteen
   stale draft/active goals already on disk. Its slice ordering and orphan
   analysis are carried forward here intact; only the scope widened.
6. [issue #518 reconciliation contract](../spec/2026-08-07-issue-518-quality-declaration-reconciliation-contract.md)
   — owns the declaration-to-verdict lifecycle a promoted gate must satisfy, and
   holds the quality-dependency clause still unmet after `#566` step 1.
7. [captured awiki fixture](../quality/fixtures/awiki-0.5.0-docs-lint.json) — the
   frozen 0.5.0 observation. Its `final_consumer` is `null`, which is what slice 4
   changes.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

**Q1 — goal scope.** Options: awiki-only ending at the release; awiki plus the
proof-surface repairs; awiki plus `#523`. **Chosen: awiki plus the proof-surface
repairs.** I initially argued for awiki-only on the grounds that a release whose
scope spans unrelated work cannot be described honestly, and I WITHDREW that
objection: the widened set has a truer shared subject than the narrow one did —
a surface reporting only what it observed — and it explains a MAJOR bump far
better than awiki plus unrelated edits would have. `#523` stays out because it is
a prose deletion with no relation to that subject.

**Q2 — orphan disposition.** Options: investigate then propose; link everything;
baseline-except the current seven. **Chosen: investigate first**, which produced
the finding that reframed the slice — three of seven are scan-scope artifacts and
no index hub exists. The baseline-exception route was rejected explicitly: it
enshrines the broken state as the floor.

**Q3 — awiki gate scope.** Options: internal only; ship in the consumer quality
contract. **Chosen: internal only** — the reversible direction. It can be widened
later once this repo has actually run it.

**Q4 — how to repair the routing floor.** Options: declaration-based; structural
signals (changed paths, commits, artifacts); measure first. **Chosen:
declaration-based.** Structural signals were rejected as a better GUESS rather
than a different kind of answer — they would still infer intent from evidence the
author did not choose. The known cost is that a silent author weakens the floor,
which is why slice 5 carries a corpus replay and an explicit operator decision on
acceptable verdict change.

**Not asked, and deliberately so:** whether to widen awiki's scan root. MEASURED
rather than debated — `-root .` gives 2884 orphans over 3564 documents.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this goal artifact; the four repaired proof surfaces
  (`plan_handoff_run.py` + `chunked_routing_lib.py`, `goal_artifact_phase_routing.py`,
  `describe_goal_closeout_shape.py`, `validate_attention_state_visibility.py`);
  the `run-quality.sh` awiki lane; the docs index hub and the seven linked pages;
  the overlap matrix; and issues `#566` / `#567`. Retro, packet, reviewer, and
  lock records are terminal evidence, not reviewed inputs.
- Frozen target: commit slices 1-7 first, then bind the closeout packet to that
  exact commit SHA. Any later edit to a reviewed input invalidates packet identity
  and the lock and requires rebinding — including a docs edit, since the index hub
  is a reviewed input here.
- Fresh-eye: a bounded `bounded-reviewer` subagent, spawned unnamed, in a distinct
  agent context. Four slices change verdict logic on a proof surface, so each owes
  a SECOND round that reads the repairs. Snapshot the reviewer boundary fingerprint
  before each round and VERIFY IT BEFORE APPLYING ANY REPAIR — verifying after
  repairs makes the drift unattributable, which happened twice this session.
- Verification lock: `bash scripts/run-quality.sh` redirected to a file and read
  whole; per-check evidence under `.charness/quality-failure-logs/`. The awiki lane
  must be NAMED in the summary, not merely absent-and-green. Each rewritten floor
  additionally carries its corpus-replay diff as lock evidence.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status
  and release/push bookkeeping outside the reviewed identity. The remote CI verdict
  is terminal evidence gathered AFTER the push, from a different observer and
  channel than the push exit code.

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

Run these yourself; none requires trusting this run's report.

1. `awiki lint -root docs -recursive` — expect `orphans=0 islands=0` and
   `largest_component_ratio=1.0000` on the summary line. It still exits 1, on
   `link_only_lines` alone; that is the amended criterion above, not a failure
   of this goal, and the gate in step 2 reads the metrics rather than the exit
   code.
2. `bash scripts/run-quality.sh > /tmp/q.txt 2>&1; grep -n 'awiki\|docs-graph' /tmp/q.txt`
   — the lane must appear BY NAME. A gate you cannot find is not a gate you have.
3. Break it on purpose: add an unlinked `docs/stray-check.md`, re-run step 1,
   expect non-zero naming `stray-check`, then delete it. This is the only step
   that proves the gate can fail.
4. `PATH=/nonexistent:$PATH bash scripts/run-quality.sh 2>&1 | grep -i awiki` —
   with the binary gone the run must say the check did not run, and must not
   report a clean docs verdict.
5. Write a goal Slice Log saying `Traced the failure to an off-by-one` and confirm
   the routing floor treats it as debug work; write `the airport gate example` and
   confirm it does NOT demand a quality route.
6. `grep -n '30 chars' skills/public/achieve/scripts/describe_goal_closeout_shape.py`
   — expect no output.
7. Add a Python docstring containing the word "skipped" to any `scripts/` file and
   confirm the attention-state gate stays green; then add a real exit-zero
   `"skipped"` status value and confirm it goes red.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
