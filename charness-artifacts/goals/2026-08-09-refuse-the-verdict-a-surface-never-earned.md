# Achieve Goal: Refuse the verdict a surface never earned, and shrink the surface every session pays for

Status: active
Created: 2026-08-09
Activation: `/goal @charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 3 — `setup` wiring for the stance. Slices 1, 1b and 2 are DONE.
- Slice 2's premise was REFUTED by measurement, and the slice became the repair
  that refutation exposed. The probe does not cost 21s: 1.6s standalone, 5.5–6.0s
  in-gate, whole suite green in ~75s. The 21,650ms sample WAS the 20s deadline —
  `check-cli-skill-surface` recorded its own timeout as the probe's cost and
  reported a starved probe as `probe failed ... exited 124`, i.e. a verdict about
  a CLI it never observed. That is this goal's class, and it is what shipped.
- Next action: slice 3 — seed `regenerable_facts` in `skills/public/setup/` so a
  fresh consumer repo ends ARMED rather than `NOT CONFIGURED`.
- Delivery is no longer blocked: the pre-push gate runs green (exit 0). The push
  itself is NOT taken and is NOT standing-approved; ask per push.
- Critique and broad proof do not re-fire within one unchanged intent — update
  this when the intent changes, not per commit (meaningful-slice-cadence).
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

**The class.** Four open issues are one defect wearing four faces: a proof surface renders a verdict over a scope or a baseline it never established. Not a wrong answer — an answer about something the surface never looked at. The predecessor goal (`charness-artifacts/goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md`, complete, shipped as `v4.0.0`) closed this class at the REPORTING layer: surfaces stopped claiming they had observed what they had not. This goal closes it one layer down, at the COMPARISON layer: a surface that cannot compare its inputs must say so instead of returning a verdict anyway.

**`#565` is first, because it is the tool.** A mutation sweep is hand-authored inline per slice and nothing verifies that its own baseline is a real passing run, so a broken harness reports every mutant `killed` and reads exactly like a clean sweep. One measured false result: `python3 -m pytest -q $T` with two space-separated paths in `T`, which zsh does not word-split, so pytest received one nonexistent path, exited non-zero, and all nine mutants recorded as `killed`. Re-run correctly, three of nine had SURVIVED. Re-confirmed LIVE during the 2026-08-08 audit: the same word-split defect recurred in a command verifying an audit charge, an hour after the issue was filed. A green sweep is a verdict about other code, so a sweep that cannot fail is a gate that cannot fail. The helper's two load-bearing properties are already known: refuse to report a kill unless the unmutated baseline first reported a PASSING TEST COUNT, and restore even when the test command raises. Every later slice's proof depends on this, which is why building it second would mean proving the rest with the harness this goal exists to replace.

**`#563` is the same class, but the issue's framing is wrong by one word and the slice is SMALLER than filed.** The issue says "the GATE reports clean over a scope that excludes where drift is live". It is not a gate. `run-quality.sh:766` and `.githooks/pre-push` both invoke `check_title_slug_drift.py` WITHOUT `--strict`, and `main` ends `return 1 if drift and args.strict else 0` — so it always exits 0, everywhere it runs. It is an advisory `WARN:` line, and deliberately: commit `78a1790b` (2026-06-19) demoted it in a buy-vs-build triage on north-star P1 grounds, because doc rename-residue guards REVERSIBLE in-session work, recording "Demote, do not delete: the signal stays visible." That decision is durable and this goal does not re-litigate it.

So **widening the scan roots buys nothing on its own** — it adds five advisory lines to an ~85-gate run, which is precisely the failure `#546` is about. Two real defects survive that reframe, and both are this goal's class rather than a scope change:

1. It prints `no title-slug drift in 72 files` — a clean-sounding sentence that never names WHICH 72. `charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md` is a completed goal on exactly this shape.
2. `_content_words` (line 34) is `re.sub(r"[^a-z0-9]+", " ", text.lower())` — it silently DELETES every non-ASCII character, so a Korean H1 reduces to the English boilerplate `Achieve Goal:` alone. Traced live: `Achieve Goal: 현재 열린 17개 이슈를 …` yields exactly `['achieve', 'goal']`, and neither word appears in any slug, so the intersection is structurally zero whether or not the document drifted. The tool states something false about a document it never read, and it does so as a function of the title's LANGUAGE.

**OPERATOR DECISION, taken during shaping: delete the checker rather than repair it.** The case for repair was never strong. It reports 0 findings on its default scope today; its entire history is two commits (created, then demoted); no record anywhere shows it catching a real rename; and both surviving defects are in a surface that renders no verdict and blocks nothing. Repairing a heuristic that has never been observed to earn its place is the rulebook growth this goal declines elsewhere for `#564`. `78a1790b`'s "demote, do not delete: the signal stays visible" was a June decision made when the tool was untested by time; the operator has now overruled it with a year of no observed effect, and `#521`'s NO-OBSERVED-EFFECT question is answered here for this one surface by precedent rather than in general.

**Deletion is an irreversible-boundary act and the slice is bigger than `rm`.** Measured at shaping time: **14 live surfaces reference it** outside `charness-artifacts/` — `scripts/run-quality.sh`, `.githooks/pre-push`, `scripts/staged_commit_gate_plan.py`, the `skills/shared/scripts/` shim, six test modules, `docs/public-skill-dogfood.json`, `docs/conventions/validator-timing-layers.md`, and `docs/conventions/operating-contract.md`. Three of those are **public skill prose that ships to consumer repos and instructs an agent to RUN the script**: `skills/public/critique/references/rename-critique.md`, `skills/public/critique/references/angle-selection.md`, and `skills/public/quality/references/proposal-flow.md` — the same lines `#478` already flagged. Deleting the script and leaving that prose reproduces exactly the defect the `2026-08-03-repair-the-commands-the-skills-tell-agents-to-run` goal existed to fix. So the rename-residue ANGLE survives in `critique` as a question a reader answers by judgment; only the mechanical evidence command goes. That is P3 applied honestly: keep the principle, drop the tool that enumerated it.

**`#546` is the class in its purest form: a bar that cannot fail.** `skills/public/quality/scripts/runtime_budget_lib.py` `_checked_entry` returns `status="no-sample"`, collected into `missing_samples` and rendered `WARN <label>: no sample yet (budget <n>ms)`. `check_runtime_budget.py` `main` returns nonzero only for `profile_config_errors` and `violations`; `missing_samples` is never consulted and so cannot affect the exit code. `runtime_visibility_lib` fires only when the budgets dict is entirely empty, not when one declared bar has no sample. A label that is renamed, or conditionally queued and then never queued, keeps its bar in the adapter forever — the bar reads as protection in review because someone deliberately sized it, while the gate has no way to fail on it. The sibling case IS armed (samples but no `budgets` block is a hard block), so the asymmetry looks accidental rather than decided. The issue's own honest note is that nobody can currently answer "how many committed bars are unenforceable on this machine", so that number is the first thing this slice measures — the direction is chosen from the count, not before it.

**`#564` is RE-SCOPED, not implemented as filed.** The issue is real: a repair's proof calls the repaired function directly instead of through the caller that should invoke it, so deleting the CALL SITE leaves the suite green while the repair is dead in production — three measured instances in one goal, one per slice, none visible to careful reading of the diff. But its proposed remedy, a new step in the goal template's `## Agent Verification Plan`, was reconsidered on P3 grounds by BOTH `charness-artifacts/audit/2026-08-08-open-issue-opinion.md` and the superseded draft `charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md`: it is rulebook growth, and the preference recorded in both is to let `#565`'s tool ask the question. This goal honors that. `recent-lessons.md` carries two never-written lines wanting to land in the goal template — a sweep states its baseline test COUNT before its first mutant, and at least one mutant per repair deletes the CALL SITE. Both become BEHAVIOR of the `#565` helper rather than prose in a template a reader may skip. `#564` closes on the tool, or is re-scoped on the issue with that reasoning recorded.

**`#523` is here for a different reason, deliberately named.** The four above are internal proof surfaces. The 2026-08-08 audit's headline thesis — that this repo had been improving itself rather than its users — was mostly REFUTED and must not be inherited. What SURVIVED refutation is one prioritization instruction: work drifted after `#516` from consumer defects to internal proof surfaces, and the next pick should be consumer-facing. `#523` is that pick and the opinion file's top rank: the root always-loaded surface carries contract prose rather than routing. Measured this session at 15,806 bytes (the issue says 16.9KB — it has already moved, so re-measure rather than trusting either figure), `CLAUDE.md` a symlink to it, nine top-level sections. `## Subagent Delegation` is LOAD-BEARING and must survive any cut intact — that constraint is inherited from the handoff and is not this goal's to relax. Including it means this goal is explicitly NOT single-class; the honest framing is four slices closing one class plus one slice paying the consumer-facing debt, not five slices of one thing.

**Amended mid-run: the stance slice, and why it belongs here.** Partway through,
the operator set a standing stance — a number in forward-looking prose is banned
by default; carry the COMMAND that produces it, and when that command is
EXPENSIVE carry the command AND a link to the checked-in artifact holding its
output, because telling every future reader to re-run a multi-minute gate moves
the cost onto all of them. It is the same class as the rest of this goal: prose
asserting a value nobody re-established. It was built rather than deferred, and
recorded as slice 1b, because a goal artifact that omits the largest thing that
happened under it is itself a surface claiming more than it observed.

Registering its adapter key exposed `#530` LIVE — the quality resolver dropped an
unknown key with `valid: true`, `errors: []`, and no warning — which is the root
defect of
[the declaration-to-verdict goal](./2026-08-07-repair-declaration-to-verdict-at-root.md),
recorded there. That goal and this one are the SAME FAMILY, and six artifacts
currently claim `Status: active`. Deciding whether to fold, sequence, or retire
them is queued for the operator rather than taken here.

**What this goal does NOT re-derive.** The two-round rule for verdict-logic slices is measured on two independent goals — eighteen blockers across ten rounds, then thirty-two across four — with the same property both times: every blocker was in a REPAIR, never in a first diagnosis. It is settled and lives in `recent-lessons.md`. Slices 1-4 all change verdict logic on proof surfaces, so plan the second round as a known cost; do not re-measure whether it is worth it.

## Non-Goals

- **Not a bloat-reduction goal.** The 7-day audit's structural charges were
  largely refuted. `#523` is in scope as a consumer-facing routing repair, not as
  evidence that the repo is over-invested in itself. Anything reading as "cut
  because it is big" is out.
- **Not a MUTATION sweep.** The superseded draft planned one with the new helper
  over already-shipped repairs. Its scope was unbounded and its only product was
  more internal test coverage. It stays cut. Slice 4's census is a different
  animal and is deliberately in scope: its population is FIXED and enumerable
  (the ~90 labels `run-quality.sh` queues), its product is a decision table for
  an open `question`-labelled issue rather than more coverage, and it takes no
  deletions itself.
- **Slice 4 deletes nothing.** It measures, refutes, and ranks. Acting on the
  ranking is the operator's, per `## Operator Decision Queue`.
- **Not a new rule in the goal template.** `#564`'s filed remedy is explicitly
  declined; see `## Goal`. If slice 2 concludes the tool cannot carry the
  question, that is a finding to record, not a licence to add the prose line.
- **Not renaming the three Korean-titled goal artifacts.** English stays
  canonical for filename slugs; the repair is in the checker.
- Not a release. No version bump, tag, or publish belongs to this goal.
- Not `#568` / `#569` / `#518` / `#515` / `#547` / `#561`. Named in
  `## Backlog Recount` with reasons.

## Boundaries

- **`## Subagent Delegation` in `AGENTS.md` is load-bearing and survives slice 5
  intact.** It is the surface that authorizes the bounded-reviewer spawns this
  goal's own slices depend on. Cutting or summarizing it would disarm the review
  discipline in the same edit that claims to improve routing. Inherited
  constraint, not this goal's to relax.
- **Slices 1-4 change verdict logic on proof surfaces**, so each owes TWO
  bounded-review rounds, the second reading the REPAIRS. Cap is two; round-2
  repairs are recorded as accepted-unreviewed. Verify the reviewer boundary
  fingerprint BEFORE applying repairs, or the drift is unattributable.
- **Slice 5 is a prompt-surface change**, so it owes the `recent-lessons.md` read
  and the same two rounds.
- `#546`'s direction is chosen from its measured count, not before it. If the
  count of unenforceable bars on this machine is zero, arming the gate is
  unproven work and the slice reports that instead of shipping a bar nobody can
  trip.
- **Slice 3 is a DELETION — irreversible under the north star's own list — so the
  bar is completeness, not tests passing.** A green suite after deleting a check
  proves nothing; the suite was green with the check doing nothing. The proof is
  that no surface still points at it, and that includes the three public skill
  reference docs a consumer repo reads.
- **Slice 4's census may not delete anything, and its no-effect verdicts are
  adversarially attacked before they are believed.** A census agent's "this check
  cannot fail" is exactly the class of unverified verdict this goal exists to
  stop; it does not get an exemption for being ours.
- **No gate may be armed without first being observed FAILING.** A gate never
  seen red is not known to work. Every armed surface here owes a deliberate
  negative test.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

What the user can do to verify completion directly — the OUTCOMES, not the
verification cadence. Whichever line of `## Active Operating Frame` states when
broad or expensive proof runs (`Gate cadence:` in the charness default frame; a
consumer adapter may seed its own) is the one owner of that answer. Restating it
here creates a second owner, and an agent reading its own acceptance criteria
obeys the acceptance criteria: one measured session paid roughly two and a half
hours re-running a 12-minute suite that way. Name what is true when the goal is
done, and point at `## Active Operating Frame` for when it is proven.

When this goal is done, all of the following are true:

1. A repo-owned mutate-and-restore helper exists. Handed a deliberately broken
   test command, it REFUSES to report any kill and names the broken baseline;
   handed a real one, it states the baseline passing test COUNT before its first
   mutant. It restores the mutated file even when the test command raises.
2. `grep -rn check_title_slug_drift skills/ scripts/ tests/ docs/ .githooks/`
   returns nothing, `bash scripts/run-quality.sh` is green one check lighter, and
   the `critique` rename-residue angle still asks its question in prose without
   naming a script that no longer exists. Nothing in a consumer's checkout tells
   an agent to run a deleted file.
3. There is a table naming, for every check `run-quality.sh` queues, whether it
   CAN fail, what it reports today, and whether anything records it catching a
   real defect — with each no-effect claim having survived a deliberate attempt
   to refute it. The count of unenforceable runtime budget bars (`#546`) is one
   row of that table rather than a separate hunt.
4. `#565`, `#563`, `#546` are closed or explicitly re-scoped with the reason on
   the issue. `#564` is closed on the tool or re-scoped with the declined-remedy
   reasoning recorded. `#521` has the census posted to it as the concrete
   evidence its question was missing.
5. `AGENTS.md` is smaller and routes rather than legislates, with
   `## Subagent Delegation` byte-identical, and every moved contract reachable
   from where it went.

## Agent Verification Plan

A mutation sweep in this goal states its baseline test COUNT before its first
mutant, and at least one mutant per repair deletes the CALL SITE rather than the
body. Both are the predecessor's measured misses; from slice 1 onward the helper
enforces them so this paragraph stops being the thing that has to remember.

### Low-Cost Checks

- `python3 -m pytest -q <the touched test modules>` at commit boundaries.
- After slice 3: `grep -rn 'check_title_slug_drift\|check-title-slug-drift'
  skills/ scripts/ tests/ docs/ .githooks/` returns nothing, and
  `grep -c queue_selected scripts/run-quality.sh` is one lower than the recorded
  96. A residual reference is the whole failure mode of this slice.
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root .`
  with its exit code recorded, as the `#546` row of the slice 4 census.
- `python3 "$SKILL_DIR/scripts/check_goal_artifact.py"` after each artifact edit.

### High-Confidence Checks

- **Negative test per armed surface, mandatory.** Slice 1: a sweep whose baseline
  command is broken must refuse, and a mutant that survives must be reported as
  survived. Slice 3 is a DELETION, so its negative test runs the other way — the
  full quality suite must be green afterwards and a deliberately planted stale
  reference must still be caught by whatever surface owns dangling references.
  Slice 4: the census's own no-effect claims must each survive an adversarial
  refutation attempt, and the refuter defaults to "refuted" when uncertain,
  because deleting a working gate is the expensive error.
- **Call-site mutants.** For every repair, one mutant deletes the CALL SITE, not
  the body — the predecessor's three false-green instances were all invisible to
  body-only mutation.
- Two bounded-review rounds per slice 1-5, the second reading the repairs.
- `bash scripts/run-quality.sh` at slice and bundle boundaries per
  `Gate cadence:`, redirected to a file and grepped — never piped through
  `tail`/`head`.

### External Or Live Proof

- `issue_tool.py validate-closeout-draft` and `verify-closeout --expect-state CLOSED`
  through the adapter for each issue this goal closes, with the `Behavior #N:`
  verdict naming a channel distinct from the one that produced the fix.
- A delegated resolution critique per closed issue, BEFORE the close call.
- No push, no release, no remote CI is claimed by this goal. If a push is later
  granted, its remote-CI verdict is read back through a different observer and
  channel than the push exit code.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `#565` — repo-owned mutate-and-restore helper that refuses a kill without a passing baseline test count, and restores on raise | It is the TOOL every later slice's proof depends on | Helper + tests; a broken-baseline run that REFUSES; a real run naming its baseline count; a restore-on-raise test | **DONE** |
| 1b | **Unplanned, operator-driven, DONE:** the regenerable-fact stance — forward-looking prose carries the COMMAND, not one run's output; expensive commands carry the command AND a linked artifact. Contract clause, a portable gate shipping through `quality`, adapter key, and consumer docs | It arrived mid-goal as a standing operator stance and was built rather than deferred. Recorded here because the plan below is meaningless if the artifact pretends it did not happen | Contract section; gate + tests, mutation-proven; adapter key registered (which exposed `#530` live); `adapter.example.yaml` and the adapter-contract reference | **DONE** |
| 2 | **Premise REFUTED, and repaired as the class it exposed.** The probe never cost 21s (1.6s alone, 5.5–6.0s in-gate); the 21,650ms sample WAS the 20s deadline. `check-cli-skill-surface` reported a starved probe as `probe failed ... exited 124` — a verdict over a CLI it never observed. Repaired: retry once, report a timeout as `unobserved` (never a `blocker`), preserve partial output, bound the drain, kill the probe's own group only | Delivery looked blocked and was not. The measurement cost one command; believing the recorded number cost a prior session a push cycle | Gate green, exit 0, `check-cli-skill-surface` PASS at 6.0s; 16 tests; two bounded rounds, both DEFECTIVE; every safety property mutation-killed; budget NOT widened | **DONE** |
| 3 | **`setup` wiring for the stance.** A new consumer repo gets `regenerable_facts` seeded with sensible surfaces, and `setup` states the stance where a human choosing skills will read it | Without it the stance reaches only repos that hand-edit their quality adapter. `skills/public/setup/` has ZERO references today, so the portable half is unbuilt and the gate's `NOT CONFIGURED` path is the only thing a consumer would ever see | `setup` seeds the key; a fresh-repo run ends with the gate ARMED rather than `NOT CONFIGURED`; the stance readable from a consumer-facing surface | pending |
| 3b | **Folded in from the retired declaration-to-verdict goal: `#530`.** Sixteen of seventeen adapter resolvers accept ANY `version` and write it back as authoritative; exactly one compares against a supported value. Replace the hand-copied blocks with one shared contract check, and refuse an unknown key instead of dropping it | Measured LIVE on 2026-08-09 on a resolver that goal had not reached: a new `regenerable_facts` key was dropped with `valid: true`, `errors: []`, no warning, and the gate silently ran on defaults. Found by a consumer of the contract, never by a gate. Slice 1b had to hand-write the seventeenth block, so the goal is now paying the tax it exists to remove | One shared check in `scripts/adapter_lib.py`; an unsupported `version` refused at every site; an unknown key refused rather than dropped; the `regenerable_facts` validator folded into the shared seam | pending |
| 4 | `#564` — re-scope onto slice 1's helper: make the call-site question the tool's behaviour, not a template rule; close or re-scope the issue | The filed remedy was declined on P3 grounds by two durable records; the defect is still real | Call-site mutant support exercised against a known-dead repair; issue closed or re-scoped with the declined-remedy reasoning on it | pending |
| 5 | `#563` — DELETE `check_title_slug_drift.py` and every wiring that points at it, repairing the three public-skill prose sites rather than orphaning them | Operator-decided: an advisory heuristic that renders no verdict, with no recorded catch, is not worth repairing | The script and its shim gone; hooks and gate-plan clean; the six test modules updated; the three skill reference docs no longer naming a deleted script; a green quality run one check lighter | pending |
| 6 | `#521` + `#546` — re-verify the census's two survivors with a reviewer independent of the workflow agents, measure `#546`'s `missing_samples` subset, post both to `#521` | The census answers `#521` with evidence it never had; a census is itself a verdict surface and does not get an exemption | Reviewer confirmation or refutation of `check-public-doc-coupling`; the `#546` count; the census posted to `#521`; NO deletions taken here | pending |
| 7 | `#523` — split `AGENTS.md` into routing vs contract, `## Subagent Delegation` byte-identical | The audit's one surviving instruction is consumer-facing work, and this is its top-ranked pick | Before/after byte counts from a command, not transcribed; `## Subagent Delegation` diff empty; every moved contract reachable from its new home | pending |

**Consolidated 2026-08-09 to ONE active goal.** Six artifacts read `Status:
active`; five are now `complete` with a retirement note naming why. Three were
untouched since June, one was a duplicate planning layer over the same backlog,
and the fifth —
[repair-declaration-to-verdict-at-root](./2026-08-07-repair-declaration-to-verdict-at-root.md)
— was the same family as this goal and is FOLDED, its live `#530` work carried in
as slice 3b. Read that file for its measured premise; the plan lives here.

**Re-shaped 2026-08-09, after slice 1 and an unplanned stance slice landed.** The
original plan was written before the regenerable-fact stance existed and did not
survive contact: two slices are done, and the two most valuable remaining units
were not in it at all. Slice 2 is first because it is the only one that blocks
delivery of every other slice — a goal that keeps building while twelve commits
cannot leave the machine is optimising the wrong end. Slice 3 is second because
the stance's whole purpose was to reach consuming repos and that half is unbuilt.

Slices 1/1b are done. Slice 2 unblocks delivery; slice 3 makes the stance
portable; slices 4-5 close the false-baseline half of the class; slice 6 asks
whether slice 5 was one instance or a population; slice 7 pays the
consumer-facing debt last, because its blast radius is every future session and
it should land on a tree the rest has already proven.

**Slice 4 measures and ranks; it does not delete.** One granted deletion is not a
deletion mandate. The census output is a table plus a recommendation the operator
acts on, and `#521` is where the general question gets answered.

**Expected proof cost and duplication pressure.** Slices 1-2 add a helper plus
its tests — the highest duplication-pressure pair here, because a mutate-and-restore
harness invites near-identical per-case tests; sample duplicate pressure when
slice 1's tests land rather than at the bundle. Slices 3-4 expand existing test
modules and should be near-neutral. Slice 5 adds no tests and may reduce prose
gate load. Two bounded-review rounds on five slices is the dominant fixed cost
and is planned, not discovered.

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: 33 open issues on 2026-08-09 via
  `gh issue list --repo corca-ai/charness --state open --limit 200`.
- Claims: `#565`, `#564` (re-scoped), `#563` (closed by DELETION, not repair),
  `#546` (as one row of slice 4's census), `#521` (the census is the evidence its
  question was opened without), `#523`.
- Not claimed: `#560` — closable now and handled as Tier 0 pre-work OUTSIDE this
  goal, because it needs only its closeout floor run, not a slice. `#567` — its
  problem 1 was already fixed by the predecessor's slice 1 (no keyword branching
  survives in `plan_handoff_run.py`), so it needs a re-scope, also Tier 0
  pre-work; its problem 2 claim that docs is the only surface without a
  rules-before-authoring mode is UNVERIFIED and contradicted by
  `plan_handoff_run.py:206-216`, so it must be measured before anyone builds
  against it. `#568`, `#569` — debt created by the predecessor goal; real, small,
  and deliberately left so this goal is not the predecessor's cleanup crew.
  `#518`, `#515`, `#514` — consumer-owned false-green classes carrying
  consumer-repo evidence; they need that owner in the loop and repeated goals
  have declined them for exactly that reason. `#561`, `#547` — operator
  decisions, not work; carried forward unresolved. `#534` — a prior goal built it
  green, REFUTED it, and reverted in full; re-scope from the refutation, never
  from the title. `#566` — step 1 done, step 2 was the predecessor goal;
  `#518`'s quality-dependency clause on it is still unmet and stays visible
  there. Remainder unclaimed for capacity.

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

**Queued at shaping time — three on `check_title_slug_drift.py`, all raised by
the operator's own "should this be code at all?" question during shaping.**

**RESOLVED at shaping time by the operator — recorded, not re-openable by an
agent.** All three `check_title_slug_drift.py` questions (widen the roots, arm
`--strict`, or delete) collapsed into one answer: **delete it.** The widening and
arming questions are moot. `78a1790b`'s "demote, do not delete" is overruled with
the operator's reason on record: the signal has been visible for a year and
nothing ever acted on it, so keeping it visible was buying nothing. See `## Goal`
for the deletion's real cost — 14 live referencing surfaces, three of them public
skill prose that ships to consumers telling an agent to run it.

**Still open and genuinely operator-only:**

- Decision: which NO-OBSERVED-EFFECT census survivors, if any, get deleted?
  - Owner: operator
  - Why deferred: slice 4 MEASURES the population and ranks it; it does not
    delete. The title-slug deletion was decided on a specific tool the operator
    had read. Generalizing that to N other checks from a census table would be
    an agent inferring a deletion mandate from one granted instance, and
    deletion is an irreversible-boundary act under the north star.
  - Unblock action: read slice 4's ranked table and name which tier ships.
  - Revisit trigger: slice 4 closeout.
- Decision: six goal artifacts claim `Status: active`; which survive?
  - Owner: operator
  - Why deferred: three are from June and almost certainly stale, but "stale" is
    a judgement about intent that the artifacts cannot settle. The two live ones
    — this goal and
    [repair-declaration-to-verdict-at-root](./2026-08-07-repair-declaration-to-verdict-at-root.md)
    — are the same family, and folding them is a scope decision, not bookkeeping.
  - Unblock action: name which stay active; the rest flip to `complete` or
    `blocked` with a reason.
  - Revisit trigger: before any further `/goal` activation.
- Decision: `#561` is RESOLVED — retire the equality pin and convert D47's quoted
  figures to the command that regenerates them. Recorded 2026-08-09 under the
  regenerable-fact stance, which makes the pin scaffolding for a practice the
  stance forbids. Execution is unscheduled; it is a natural companion to slice 3.
- Decision: `#547` is RESOLVED — close as superseded. Its premise died with
  `#562`: `stamp_inspection` no longer stamps a per-locator digest, and the live
  inspection's locators carry no `sha256` at all, so there are no digests for a
  re-stamp to launder. Execution (the close, through the floor) is unscheduled.


- Decision: `#561`'s equality-versus-invariant probe pin, and `#547`'s re-scope.
  - Owner: D47's owner / operator
  - Why deferred: inherited unresolved from two predecessor goals; both costs
    are already measured and recorded there. This goal carries them forward
    rather than adopting them.
  - Unblock action: answer on the respective issues.
  - Revisit trigger: any goal that claims either issue.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Phases** — name the phases this run's recorded work crossed, e.g.
  `Phases: debug, quality`, or `Phases: n/a — <reason>` when it crossed none. YOU
  say this; the floor used to infer it by matching words in your prose and was
  wrong in both directions — plain-English debug work did not register, while the
  word "gate" in an unrelated sentence demanded a quality route.
- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / issue work (both detected from records you wrote) and every
  phase you declared above need this `Routing:` evidence or a
  `Routing: n/a — <reason>` opt-out.
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

- `Phases: <declared phases, or n/a — why none were crossed>`
- `Routing: <skill> — <why this phase needs it>`

Shaped at Before-phase; update as the run crosses each boundary:

- `Phases: debug, impl, quality, issue`
- `Routing: charness:debug — slice 2 began as a cost investigation and became a root-cause one; the recorded 21s was the gate's own timeout, so the falsifiable hypothesis had to be tested before any repair was shaped.`
- `Routing: charness:impl + charness:quality — the repair is verdict logic on a proof surface, so it owed mutation proof per repaired property and two bounded review rounds, the second reading the repairs.`
- `Routing: charness:issue — #573 filed under the standing approval for a defect measured three times during this slice.`
- `Issue closeout: n/a — slice 2 closes no tracked issue; #573 was FILED, not resolved. #565/#563/#546/#564/#521/#523 remain open to later slices.`
- `Gather: n/a — every source is in-repo (issues via the gh adapter, artifacts, git history); no external URL or credentialed source was read.`
- `Release: n/a — this goal takes no version bump, tag, or publish; the 4.0.0 release belongs to the predecessor goal.`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED — four consequential decisions were settled with the operator during shaping. (1) **Direction**: the operator chose the false-green cluster over the consumer-facing tier, then chose to add `#523` back, so this goal is deliberately not single-class. (2) **`#563` becomes a DELETION**: the operator asked whether the checker should be code at all; measurement showed it is advisory, exits 0 everywhere, reports 0 findings on its default scope, and has two lifetime commits, and the operator decided to delete rather than repair — overruling `78a1790b`'s "demote, do not delete" with a year of no observed effect. Deletion is on the north star's irreversible list, which is why its completeness bar is in `## Boundaries`. (3) **Slice 4 census added**: the operator asked whether many such checks exist; a Sonnet-backed dynamic workflow with adversarial refutation was the requested instrument. It ranks and does not delete. (4) **Issue closes**: this goal intends to close tracked issues, each through the full closeout floor with a delegated resolution critique before the close call. No live/prod proof, no push, and no release is claimed.

## Slice Log

### Slice 1: Slice 1 -- #565: a mutation sweep runner that cannot report a kill it did not earn

- Objective: Build the repo-owned mutate-and-restore helper #565 asks for: refuse to report a kill unless the unmutated baseline first reported a PASSING TEST COUNT, and restore even when the test command raises. Every later slice's proof depends on it, so it goes first.
- Why this approach: Hand-authored inline sweeps were the norm and one reported NINE FALSE KILLS (zsh does not word-split an unquoted parameter, so pytest got one nonexistent path, exited non-zero, and all nine mutants read as `killed`; three of nine had actually SURVIVED). The parent hand-rolled the same harness five times earlier in this session, including a manual `cp` restore -- the premise was measured, not assumed.
- Commits:
- What changed: scripts/mutate_and_restore.py (new), tests/quality_gates/test_mutate_and_restore.py (new, 26 tests), charness-artifacts/quality/dup-review.json (two idiom-sized families classified intentional).
- Alternatives rejected:
- Targeted verification: 26 tests pass. Dogfooded through its own CLI against its own repairs: baseline stated first (26 passed), 4 of 5 mutants killed including a CALL-SITE mutant, 1 refused because the mutation broke the run rather than being caught -- the round-1 repair working in production. ruff clean; python-lengths clean; dup-ratchet clean.
- Test duplication pressure: Two new files; dup-ratchet surfaced exactly two new families, both idiom-sized (parallel 2-line property accessors, and the repo's standard CLI error-exit shape shared with check_skill_surface_preflight.py). Both classified `intentional` with reasons rather than restructured, because collapsing either would couple independently-owned surfaces for no behavioural gain.
- Critique: TWO delegated bounded rounds, both returned DEFECTIVE on first read; seven blockers total. Round 1: the `killed` verdict rested on a bare non-zero exit (#565's own defect one level in -- a syntax error from the replacement, a collection error, or a crashed runner all exit non-zero with nothing caught); `invalidate_bytecode` was scoped to the sweep process's interpreter while `test_command` is arbitrary; a failure between the write and the bytecode drop left the tree mutated with the pristine bytes in a dead local; and the test guarding the restore property passed even with `apply_mutation` made a no-op, confirmed by mutation before repair. Round 2, reading the repairs: `SURVIVED` still returned on a bare exit-0 with no scope accounting; `parse_passed` scanned the whole transcript for `no tests ran` and this runner's OWN test file contains that literal, so a real kill became a refusal on the very file it was dogfooded against; and the exit-1 collision between a crash and `survivors found` was never actually fixed. Repairs: verdicts read the SUMMARY LINE only, both KILLED and SURVIVED require the run to account for the baseline count, errors are checked after failures so a teardown-error beside a real failure is still a kill, crashes exit 3, and containment/missing-key refusals were added. Boundary fingerprints clean (parent-attributed) around both windows.
- Off-goal findings: Filed #570 during this session's #567 closeout (chunked-routing runs briefed on a surface they must not write). Nothing new filed by this slice.
- Lessons carried forward: A same-length mutant is invisible to CPython's bytecode cache: `a + b` -> `a * b` keeps the source SIZE identical, and a .pyc is validated by size plus mtime truncated to whole SECONDS, so stale bytecode ran and a real mutant reported SURVIVED. Found by the suite before either reviewer. The first regression test for it was itself a false green -- it passed with the guard deleted, for timing reasons -- and had to be replaced with a call-site assertion. Fixture arithmetic matters too: `add(2, 2) == 4` lets the `+` -> `*` mutant survive because 2+2 == 2*2.
- Metrics:


### Slice 2: the push was never blocked by cost, and the check said otherwise

- Objective: unblock delivery. The handoff said `check-cli-skill-surface`'s
  `doctor.py` probe needed ~21s against a 20s budget, "measured identically on
  the pre-session tree, so it is cost rather than a regression".
- What measurement found: the premise is false. The probe runs in **1.6s**
  standalone and **5.5-6.0s** inside the full gate; the whole suite is green in
  ~75s and the pre-push gate exits 0. Per-capability timing totals ~1.2s across
  14 capabilities, none network-bound under `--skip-release-probe`. The recorded
  21,650ms sample was the 20s deadline plus overhead - the check had recorded ITS
  OWN TIMEOUT as the probe's cost. 4x CPU oversubscription reproduces only 3.9s,
  so even contention does not reach 21s; it was a tail starve under
  `run-quality.sh`'s ~85-way unbounded fan-out (`queue_timed` backgrounds every
  queued check with `&`).
- Why the slice still shipped code: the episode IS this goal's class. A probe
  that never returned was reported as `CLI plus skill probe failed: ... exited
  124` and folded into `blockers` - a verdict about a CLI the check never
  observed. That message is why a session concluded the probe was expensive and
  left twelve commits unpushed.
- What changed: `scripts/check_cli_skill_surface.py` - a timeout is retried once
  (`PROBE_ATTEMPTS = 2`), then reported in a separate `unobserved` list, never as
  a `blocker`; partial output captured before the deadline is preserved as
  evidence; the probe runs in its own session and is reaped by process group
  under a bounded drain. `tests/quality_gates/test_cli_skill_surface.py` - 11 to
  16 tests. Generated mirror `plugins/charness/scripts/check_cli_skill_surface.py`
  re-synced and verified byte-identical with `cmp`.
- **The floor was NOT loosened.** `main()` still returns 1 for `unobserved`, so a
  starved probe still refuses the push. The probe timeout env var and the runtime
  budgets are untouched - widening was the one forbidden move and was not taken.
- Targeted verification: 16 tests pass. Mutation sweeps via
  `scripts/mutate_and_restore.py`, each stating its baseline passing count,
  killed the `timed_out` routing, the `_kill_group_and_drain` CALL SITE, the
  retry bound, the `unobserved` status selection, `main()`'s refusing set, the
  partial-output preservation, the bytes decode, the drain deadline,
  `start_new_session=True`, and `killpg(process.pid)` vs `killpg(getpgid(...))`.
- Critique: TWO delegated bounded rounds, both DEFECTIVE. Round 1: a
  `TimeoutExpired` does not mean "no verdict" (a child can exit while a
  grandchild holds the pipe) and the old code discarded the partial output; the
  drain was unbounded, so the gate would HANG rather than refuse, with no wall
  clock anywhere above it; `unestablished` collided with `run-quality.sh`'s own
  opposite meaning (exit 3, does not fail the run) and was renamed `unobserved`;
  the 124 boundary was untested; the retry test's 300ms budget was itself
  starve-sensitive. Round 2, reading the repairs, found the repair had
  **reintroduced its own class one call deeper**: the drain's own timeout path
  discarded `TimeoutExpired.output`, and neither existing fixture crossed the two
  halves needed to reach it. Both fingerprint windows verified clean,
  parent-attributed.
- Non-claims: the retry is proven only against a synthetic first-call-hangs
  fixture, never a real in-gate starve. `run-quality.sh`'s ~85-way fan-out is
  untouched. 2 attempts and a 5s drain are not proven to be the right numbers.
  The `unobserved` path has never fired in a real gate run. The containment
  `process.kill()` in the `finally` survived mutation - no fixture builds a probe
  that re-parents its own group - and is labelled UNPROVEN in the source rather
  than claimed as covered. A retried starve costs ~26s against an 11,000ms budget
  for this label; `check_runtime_budget` compares a recent MEDIAN, so one spike is
  normally absorbed, but this was not measured.
- Off-goal findings: filed **#573** - `scripts/mutate_and_restore.py` restores on
  a raising test command but NOT when the sweep process itself is killed. Hit
  three times in this slice; twice the residue was a CALL-SITE deletion, and once
  it survived a `git status` check and three targeted greps because the file was
  already legitimately modified. Found only when a behavioural measurement
  disagreed with the code as read.
- Lessons carried forward: a gate that records its own timeout as an elapsed time
  teaches the next reader a false cost, and prose repeating that number launders
  it into a fact - exactly what slice 1b's regenerable-fact stance exists to stop.
  And `os.killpg(os.getpgid(child), SIGKILL)` is a loaded gun in any gate: when
  `start_new_session` does not apply it names the SHARED group, and it SIGKILLed
  the sweep, pytest, and the parent shell three times here.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [docs/design-north-star.md](../../docs/design-north-star.md), read while
   SHAPING. Three facets bear directly. **P1 (default to judgment on reversible
   work)** is why `check_title_slug_drift.py` was advisory in the first place and
   why deleting it is coherent rather than a reversal — the tool was already
   judged not to warrant teeth, and a year later it had not earned prose either.
   **P3 (principle over rulebook)** decides `#564` against its own filed remedy
   and decides what survives the slice-3 deletion: the rename-residue question
   stays as an angle a reader answers, the enumerating tool goes. **P4/P5** set
   the teeth: the boundary list explicitly includes "authoring or changing a
   proof surface" and "deletions", so slices 1-4 are all irreversible-boundary
   work, each owing a distinct second observer rather than a green suite. The
   standard's own warning against "a gate that checks gates" is why slice 4
   produces a table and a recommendation rather than a new meta-gate.
2. `charness-artifacts/goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md`
   — the predecessor, complete, shipped as `v4.0.0`. Its `## Slice Log` carries
   what each of its eight slices measured, and its closeout recorded
   `Successor goal: n/a`, which is why this goal was shaped fresh from the
   tracker rather than inherited.
3. `charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md`
   — SUPERSEDED by this artifact. Read it for its narrowing (the mutation sweep
   is cut, `#564`'s remedy is declined, `#565` survives), which this goal adopts.
4. `charness-artifacts/audit/2026-08-08-open-issue-opinion.md` — read as OPINION,
   which it insists on itself. Its headline "the repo over-invests in itself"
   thesis was refuted; its one surviving instruction (next pick consumer-facing)
   is why `#523` is slice 5. Four of its positions were corrected by the operator
   within one session, so verify anything taken from it.
5. `charness-artifacts/retro/recent-lessons.md` — the two never-written lines
   this goal converts into tool behavior instead of template prose, and the
   "planned items were premises, not debt" trap that caught three items during
   this shaping.
6. Issues `#565`, `#564`, `#563`, `#546`, `#521`, `#523`, plus `#560`/`#567` as
   named Tier 0 pre-work outside the goal.
7. Commit `78a1790b` — the buy-vs-build triage that demoted the title-slug
   checker to advisory, and the decision slice 3 overrules with the operator on
   record.
8. [charness-artifacts/audit/2026-08-09-no-observed-effect-census.md](../audit/2026-08-09-no-observed-effect-census.md)
   — run at shaping time, 11 Sonnet agents. Read it for two things beyond its
   headline: the 4-of-6 adversarial refutation rate, and its own `## Non-claims`,
   which record that the 84 `earns-its-place` verdicts were never independently
   verified.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which direction should the next goal take?** Family considered: the
  false-green cluster; the consumer-facing surface tier (`#523`/`#518`/`#515`);
  Tier 0 closes only; repaying the predecessor's own debt (`#568`/`#569`).
  Chosen: the false-green cluster, then widened by the operator to include
  `#523`. Rejected-alternatives reason: the cluster's issues each carry a
  MEASURED instance rather than a hypothesis, which is why it outranked the
  consumer tier on evidence — but the audit's surviving instruction pointed
  consumer-facing, and the operator resolved that tension by taking both rather
  than letting one silently win. `single-point: this is a scope choice for one
  repo's backlog, not a value that varies on any host/provider/profile axis.`
- **Should `check_title_slug_drift.py` exist as code at all?** Family
  considered: repair in place (name the scope, add `undecidable`); widen the scan
  roots; arm `--strict`; delete. Chosen: delete. Rejected-alternatives reason:
  repair was the default until measurement showed the surface renders no verdict
  at all (always exit 0), reports 0 findings on its default scope, and has two
  commits in its lifetime with no recorded catch — repairing it would have been
  the rulebook growth this goal declines for `#564` one section earlier.
  `axis: enforcement posture — the repo genuinely varies here (advisory vs
  strict vs absent), and 78a1790b shows the same tool has occupied two of the
  three positions, so "delete" is a third point on a real axis rather than a
  singleton.`
- **Should the three Korean-titled goal artifacts be renamed to English?**
  Family considered: rename them; teach the checker non-Latin titles; declare
  `undecidable`; delete the checker. Chosen: moot under deletion, but the
  operator's stated constraint stands as a durable design rule — English is
  canonical for filename slugs, and charness must not couple a surface's
  CORRECTNESS to a document's language. Rejected-alternatives reason: renaming
  would have made the artifacts serve the tool. `axis: locale — the repo already
  authors artifacts in both Korean and English, so any future title-reading
  surface must vary on this axis, not assume ASCII.`
- **Is the title-slug case one instance or a population?** Family considered:
  assume it is isolated; add a census slice; defer the census to a later goal.
  Chosen: census slice, run as a Sonnet dynamic workflow with adversarial
  refutation, ranking only. Rejected-alternatives reason: "probably many" was a
  suspicion, and the goal's own class forbids acting on a verdict nobody
  established; deferring it would lose the context in which the question was
  asked. `single-point: the census population is this repo's own run-quality.sh
  queue.`

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Shaping-time findings, self-raised and folded before saving. A delegated plan
critique has NOT yet run against this artifact and is the first thing activation
owes.

- **Folded (blocker): three planned items were premises, not debt.** Checked
  against the tree during shaping rather than trusting the handoff: the handoff's
  named pickup (slice 8, the 4.0.0 release) was already DONE; `#567`'s problem 1
  was already fixed by the predecessor's slice 1; `#560` was already built. All
  three moved out of the slice plan — two into Tier 0 pre-work, one deleted. This
  is the `recent-lessons.md` repeat trap firing exactly as recorded.
- **Folded (blocker): `#564`'s filed remedy was already rejected by two durable
  records.** The first draft of this plan shaped a slice around writing that
  remedy into the goal template. `## Goal` now declines it and routes the
  question into `#565`'s tool. The Change Discipline rule this violated fires at
  DESIGN time, one phase earlier than the rest of implementation discipline.
- **Folded (blocker): `#563`'s issue framing calls it a "gate" and it is not
  one.** The first plan widened its scan roots, which would have added advisory
  noise and fixed nothing. Measurement reframed the slice twice — first to a
  report-honesty repair, then to a deletion on the operator's call.
- **Folded (blocker): the census would have been a second false verdict.** A
  fan-out agent asserting "this check cannot fail" is precisely the unverified
  verdict this goal exists to stop. Adversarial refutation with a
  default-to-refuted bias became a boundary rather than an optional nicety.
  Evidence it was needed, now measured twice over: a crude regex proxy run during
  shaping produced a "14 checks cannot fail" list that included `pytest` and
  `dup-ratchet`, both of which obviously can (discarded); and when the real
  census ran, **the adversarial pass refuted 4 of 6 candidates**, including two
  where the classifier read `main()`'s returns and missed an uncaught
  `JSONDecodeError` that exits nonzero. A single-pass census would have
  recommended deleting four working surfaces.
- **Folded (blocker): the census overstated its own baseline, and its own agent
  caught it.** The synthesis prompt asserted title-slug had "already been
  deleted"; it has not — the decision is recorded in a `draft` goal with an empty
  slice log. Recorded in the census artifact's own correction section. A census
  looking for surfaces that claim more than they observed must not do it itself.
- **Raised, NOT folded: the census's 84 `earns-its-place` verdicts are
  unverified.** Only the 6 candidates were attacked, so a check wrongly CLEARED
  would not have been caught. Not folded because the bias runs in the safe
  direction for a deletion question — false negatives keep working gates alive.
  Named in the census's `## Non-claims` so nobody later reads it as a clean bill
  of health for 90 checks.
- **Raised, NOT folded (over-worry): "the goal is not single-class."** True —
  slice 5 is consumer-facing while 1-4 are internal proof surfaces. Considered
  splitting into two goals. Not folded: the operator explicitly asked for both,
  and `## Goal` names the seam out loud rather than pretending a false unity.
- **Raised, NOT folded (over-worry): "deleting a check weakens the suite."**
  The suite was already green with this check doing nothing; its removal changes
  no verdict anywhere. The real risk is residual references, which is why slice
  3's bar is completeness rather than a green run.
- **Reviewer provenance: none yet.** Every finding above is self-raised during
  shaping. Two bounded rounds per slice are planned in `## Boundaries`, and a
  delegated plan critique against this artifact has not run.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this artifact; issues `#565`, `#564`, `#563`, `#546`, `#521`,
  `#523`; the slice-4 census table once written; and
  `charness-artifacts/quality/latest.md` at closeout. Retro, packet, reviewer,
  and lock records are terminal evidence and are NOT semantic inputs.
- Frozen target: commit slices 1-5 first, then bind the closeout packet to that
  exact SHA. Any later edit to a semantic input above requires rebinding — the
  predecessor paid a regeneration cycle for exactly this.
- Fresh-eye: bounded `bounded-reviewer` subagents in a different agent context,
  spawned WITHOUT a host addressing/team name. Two rounds per slice 1-5 (the
  second reads the repairs), plus a delegated resolution critique per closed
  issue BEFORE its close call. The `Behavior #N:` verdict for each close names a
  channel distinct from the one that produced the fix. Reviewer boundary
  fingerprint snapshot/verify runs around each review, BEFORE repairs are
  applied.
- Verification lock: `python3 scripts/run_slice_closeout.py` per slice
  (`--skip-broad-pytest` pre-lock), and the final bundle with
  `--verification-lock`; `bash scripts/run-quality.sh` redirected to a file,
  never piped through `tail`/`head`. Evidence under `.charness/` and the slice
  ledger.
- Complete flip: record packet, reviewer, and lock evidence first; then write
  terminal status and bookkeeping OUTSIDE the reviewed identity. Prove
  `Status: complete` plus a passing `check_goal_artifact.py` on the checked-in
  artifact before any host-level completion call.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

Found during shaping, before activation:

- The handoff's `## Workflow Trigger` named slice 8 of a goal that was already
  complete and pushed, so a bare pickup would have re-run a finished release.
  Handoff refresh is Tier 0 pre-work.
- The superseded draft goal `2026-08-10-close-the-gap-between-a-repair-and-its-caller.md`
  cites `docs/handoff.md` for "which four charges broke and how to re-measure
  them", but the handoff has been rewritten since and no longer carries them.
  They survive only in `charness-artifacts/audit/2026-08-08-open-issue-opinion.md`.
  A durable record pointing at a rewritten pointer is its own small class; not
  filed yet.
- `#567`'s problem 2 ("the docs surface is the only one with no
  rules-before-authoring mode") is contradicted by `plan_handoff_run.py:206-216`,
  which has one. Unverified either way; must be measured before anyone builds
  against it.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
