# Achieve Goal: Close the armed changed-line pre-push lane's known holes: pin the hook to the runner (CHARNESS_PRE_PUSH / unexported .githooks/pre-push), stop check_mutation_run_proof calling an empty range provable, tighten fg_warning and the publish refusal's fail-open paths, and land D39/D41 (freshness blind to tests/, mapper blind to bare imports)

Status: active
Created: 2026-07-29
Activation: `/goal @charness-artifacts/goals/2026-07-29-close-the-armed-changed-line-pre-push-lane-s-known-holes-pin.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: ACTIVE — activated 2026-07-29; slice 1 of 5 closed.
- Current slice: slices 1-3 DONE. Slice 4 next: the release publish refusal's fail-open paths.
- Next action: slice 4 — split unreadable-vs-absent `output_dir` in the release publish refusal, and stop a draft whose filename lacks `notes` from being invisible. Absent `output_dir` must STAY publishable: it is the normal state for a repo that drafts no notes.
- Verification cadence: per slice — targeted pytest + `run_slice_closeout.py`
  at the commit boundary; `bash scripts/run-quality.sh` (full) at the bundle
  boundary, after commit so the changed-line verdict is real rather than a
  pre-commit false green.
- Slice review packet: intent, changed files with owning/generated surfaces,
  the invariant the slice claims, the falsifier that was run, non-claims,
  out-of-scope lines, and the open questions. Every slice here changes verdict
  logic on a proof surface, so each owes a SECOND bounded review round reading
  the repaired surface (cap: two rounds; round-2 repairs are recorded as
  accepted-unreviewed).
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Close the armed changed-line pre-push lane's known holes: make the runner
determine push context itself and fail closed rather than depending on
`CHARNESS_PRE_PUSH` from an unexported hook, stop `check_mutation_run_proof`
calling an empty range provable, tighten `changed_line_run_trust`'s
under-approximation and the release publish refusal's fail-open paths, and
report the `run-quality-full` bar the slack advisory cannot see.

**Scope narrowed at shaping (2026-07-29):** the drafted title carries "land
D39/D41" from the source entry. That was decided OUT of scope — see Non-Goals.
The title is left as drafted so the artifact slug stays stable; this paragraph
is the current statement of the goal.

### Source handoff entry #6: D39 / D41

> the armed lane's gaps (freshness blind to `tests/`, mapper blind to bare
> imports). Not urgent.

### Source handoff entry #7: Gaps this session named and did not close

> ranked by how silently each fails, and argued in the
> [unproven-gate](../critique/2026-07-29-unproven-gate-status.md) and
> [publish-escape](../critique/2026-07-29-release-notes-publish-escape.md)
> critiques:
>
> - Nothing pins the hook to the runner: `--refuse-unestablished` keys on
>   `CHARNESS_PRE_PUSH`, set only by the unexported `.githooks/pre-push`, so an old
>   vendored hook drops the push-time teeth with a green console.
> - `check_mutation_run_proof` calls a changed-line claim `provable` on `base_sha`
>   alone, so an empty-range run is a citable green.
> - `fg_warning` under-approximates untrustworthy runs; the publish refusal fails open
>   on an unreadable `output_dir` and on a draft whose filename lacks `notes`; and the
>   `run-quality-full` bar sits under the slack advisory, so nothing reports it.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk.
- **D39 and D41 stay DEFERRED.** Both carry an owner DEFER with an explicit
  reopen trigger in [deferred-decisions.md](../../docs/deferred-decisions.md),
  and neither trigger has demonstrably fired. D39's failure direction is
  self-announcing (stale coverage shows changed lines still uncovered — a loud
  false FAIL, not a false pass); D41's own deferral records that the mapper
  widening over-matches and owes its own two-round review. Landing them here
  would reverse an owner decision under a different banner. Decided at shaping,
  2026-07-29.
- No push to `origin` and no release publish as part of proving this goal. See
  `Discuss before activation:` below.
- Not repairing the five already-escaped one-line release bodies: the owner
  DECLINED that backfill and it is closed, not pending.
- Not adding a ninth advisory anywhere. Every gap here is already advisory-visible
  and was walked past; the repair is teeth or a removed green, not more prose.

## Boundaries

- Reproduced before shaping, each in the tree at `4516729a`:
  - `scripts/run-quality.sh:656` adds `--refuse-unestablished` only when
    `CHARNESS_PRE_PUSH=1`, and `.githooks/pre-push:65,68` is the only setter.
    **Corrected after plan critique:** the hook is not merely unexported, it is
    absent from the export surface entirely (a `find` over `plugins/`,
    `.claude-plugin/`, and `.agents/plugins/` for `pre-push` returns nothing, while
    `plugins/charness/scripts/run-quality.sh:656` ships the READER).
    **Corrected again after probing three real consumer repos (2026-07-29):**
    the whole consumer framing was wrong. `scripts/packaging_lib.py:248-250`
    mirrors the ENTIRE `scripts/` tree into the plugin, and
    `scripts/install-git-hooks.sh` already has a deliberate consumer branch that
    writes ONLY a `commit-msg` wrapper — matched by
    `validate_maintainer_setup.py:42-44`, which expects `pre-commit`/`pre-push`
    only when `is_charness_source_repo`. Probed `../ceal`, `../crill`,
    `../cautilus`: ceal owns `scripts/run-quality.sh` with no `.githooks` and no
    `core.hooksPath`; crill has no `run-quality.sh` at all and manages hooks via
    lefthook; cautilus owns both its runner and its own `.githooks/pre-push`,
    which runs `npm run verify` and a generated-drift check, not charness's
    runner. `CHARNESS_PRE_PUSH` appears in none of the three. **No consumer repo
    runs charness's runner**, so the changed-line lane is a source-repo-only
    surface and the teeth were never downstream to lose.
  - The reachable defect that survives that correction is LOCAL:
    `scripts/validate_maintainer_setup.py:44-56` checks hook file EXISTENCE, not
    content, so deleting the `CHARNESS_PRE_PUSH=1` prefix from
    `.githooks/pre-push` in THIS repo passes validation and silently disarms the
    lane.
  - `scripts/check_mutation_run_proof.py:98-106` — after the `if not base`
    refusal it sets `provable = True` unconditionally. **Corrected after plan
    critique:** the original wording ("a range with no eligible pool file") was
    wrong. `classify_run_proof` takes `claim`, `event`, `base_sha`,
    `conclusion` and nothing else — it has no head SHA, no git access, and no
    notion of a mutation pool, so it structurally cannot see whether the range
    is empty. The real defect is narrower and stated in slice 3.
  - `scripts/changed_line_run_trust.py` — `contaminating_pool_changes` returns
    `[]` for a non-HEAD `--head-sha`, and `_git_lines` turns a git failure into
    `[]`, which every caller reads as "nothing found".
  - `skills/public/release/scripts/audit_public_release_narrative.py:245-267` —
    an unreadable or absent `output_dir` yields no candidates and the arm stays
    silent (the code says so in a comment), and `"notes" in path.stem.lower()`
    makes a draft named `...-release.md` invisible to the refusal.
  - `.agents/quality-adapter.yaml:291` — `run-quality-full: 420000`.
    **Corrected after plan critique: the original premise was inverted.** The
    slack advisory divides by `max_recent_elapsed_ms`, not the median
    (`skills/public/quality/scripts/runtime_budget_lib.py:194-201`), and this
    profile's recorded max is 551850 (`.charness/quality/runtime-signals.json`,
    `local-linux-x86_64-36cpu`). The ratio is 0.76, so the 36cpu bar is BELOW
    its own observed worst run — a false-RED risk on a multi-commit range, the
    opposite of a loose bar. The real invisible bar is
    `local-linux-x86_64-4cpu` at `:447` = 140000 against a max of 99828 from
    n=2 samples dated 2026-07-26, which predate the armed lane's documented
    ~24s-5min added cost entirely.
- In scope: the five surfaces above plus their tests and the plugin mirror under
  `plugins/charness/`.
- Reference-only, not work surfaces:
  [publish-escape critique](../critique/2026-07-29-release-notes-publish-escape.md),
  [unproven-gate critique](../critique/2026-07-29-unproven-gate-status.md)
  (F6/F7 are the open records this goal closes),
  [docs/deferred-decisions.md](../../docs/deferred-decisions.md) (D39/D41 — read
  for context, left deferred).
- The push-context determination was recorded at shaping as
  `axis: consumer-repo install`. **That probe was WRONG and is corrected to
  `single-point: charness source repo`** — measured, not assumed, against
  `../ceal`, `../crill`, and `../cautilus`, none of which runs charness's
  `run-quality.sh` or carries `CHARNESS_PRE_PUSH`. The anti-anchoring probe
  fired in the right direction (it asked whether one clone was being treated as
  the world) and produced the wrong answer, which the sibling-repo evidence
  reversed. Recorded rather than quietly overwritten, because the goal's scope
  was built on the wrong reading for two revisions.
- Consequence: a fix here is allowed to key on this repo's
  `core.hooksPath=.githooks`, because that IS the surface. The earlier
  Boundaries line forbidding exactly that is retracted.
- The runtime budget bar is `axis: machine profile` — `.agents/quality-adapter.yaml`
  carries THREE blocks (`local-linux-x86_64-36cpu:141`,
  `local-linux-x86_64-4cpu:364`, `local-linux-aarch64-4cpu:448`), so any
  advisory change must be evaluated per profile, not from this box's numbers.
  `BUDGET_SLACK_FACTOR` is a single module constant
  (`runtime_budget_lib.py:24`), so widening it is a change across every profile
  and every label at once — the adapter already records two other bars it
  cannot see (`:294-296`, `:493-494`).
- Portable per implementation-discipline: no host-specific assumption; the runner
  must not key on a Claude- or Codex-specific signal.
- Stop conditions: stop and ask if a repair would (a) make the changed-line lane
  block ordinary mid-work runs — that is the failure history being repaired, or
  (b) require a push to `origin` to prove. Name on first discovery; do not guess.

## User Acceptance

The operator can see, without reading code:

1. Deleting the `CHARNESS_PRE_PUSH=1` prefix from `.githooks/pre-push` makes
   `python3 scripts/validate_maintainer_setup.py --repo-root .` FAIL. It passes
   today, which is the defect. Before/after output quoted in the closeout.
   **Revised twice:** this criterion originally described a consumer-repo
   simulation; three real consumer repos showed that scenario cannot occur.
2. A citation of a mutation run as changed-line proof no longer reads
   `provable: true` when nothing was in range. **Revised after plan critique:**
   the original wording named an invocation that cannot express an empty range,
   so it could only ever have been satisfied by a test passing for the wrong
   reason. The acceptance is now: whatever range fact slice 3 introduces, the
   closeout quotes one invocation that refuses and one that still passes, and
   states which input carries the range.
3. A `--head-sha` that is not HEAD, and a git command that fails, each produce a
   stated "could not establish" rather than a clean verdict.
4. A release draft named without the word `notes`, and an unreadable
   `output_dir`, each stop being silently publishable.
5. Each of the above has a test that FAILS when the fix is reverted — quoted as
   the revert output, not asserted.
6. `bash scripts/run-quality.sh` is green after commit, and the changed-line
   verdict in that run is real (not `UNPROVEN`, not a pre-commit reading).

## Agent Verification Plan

Low-cost, per slice (commit boundary):

- Targeted pytest for the slice's own surface (paths corrected after plan
  critique): `tests/quality_gates/test_prepush_focused_changed_line_coverage.py`,
  `tests/quality_gates/test_quality_runner.py`,
  `tests/test_degradation_branch_coverage.py` (NOT under `quality_gates/`),
  `tests/quality_gates/test_check_mutation_run_proof.py`,
  `tests/quality_gates/test_release_narrative_audit.py`.
- New tests must use the dotted `from scripts import <module>` import form.
  The D39/D41 exclusion below is coherent only under that constraint — a bare
  `import <stem>` would fire D41's reopen trigger and make the exclusion
  incoherent rather than conservative (`tests/test_degradation_branch_coverage.py:93-97`
  already carries the convention and the comment explaining it).
- `python3 scripts/run_slice_closeout.py --repo-root .` when the diff spans
  generated surfaces (every slice here mirrors into `plugins/charness/`).
- `python3 scripts/check_export_safe_imports.py`.
- Falsifier per fix: revert the fix, observe the new test fail, restore. A test
  that passes for a reason other than the one it names is the defect class this
  goal is repairing, so a green test is not evidence until it has been seen red.

High-confidence (bundle boundary):

- `bash scripts/run-quality.sh` full, run AFTER commit. A dirty pool makes the
  changed-line lane `UNPROVEN`, which is not a green — re-run rather than cite.
- Push-time refusal exercised through the real hook against a LOCAL bare remote
  (`git init --bare` in a tmpdir, `git push <tmp> HEAD`), with and without the
  `CHARNESS_PRE_PUSH` prefix. This executes `.githooks/pre-push` for real with
  no external side effect. Scope note: this proves the SOURCE repo's lane, which
  after the sibling-repo probe is the whole of the lane — there is no
  consumer-shaped probe to run, because no consumer repo has this surface.
- The `2026-07-29-unproven-gate-status.md` non-claim — "no live push has
  exercised `--refuse-unestablished` through the hook" — is discharged by the
  local-bare-remote probe only for the hook path. A push to `origin` is NOT run;
  see the non-claim in `Discuss before activation:`.

Test-duplication pressure: slices 1-4 each add 2-4 focused tests to suites that
already exist, so the broad duplicate/length gate should not move materially.
Slice 2 is the exception — it adds negative-path tests to
`test_degradation_branch_coverage.py`, whose cases are structurally similar by
design; if the dup ratchet moves, classify it as new-slice-local before
rebaselining anything.

## Slice Plan

Order revised after plan critique: arming precedes widening. Slice 1's original
"every later verdict consumes it" rationale was false — `changed_line_run_trust`
has exactly one consumer (`scripts/check_changed_line_mutation_coverage.py`),
and slices 3/4/5 never touch it. Landing the trust widening first would ship a
repair that is inert on every path a consumer runs.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 (done) | Pin the hook's CONTENT, not just its existence: `validate_maintainer_setup.py` must fail when `.githooks/pre-push` no longer arms the lane. Separately, narrow the adapter-contract language that implies consumer repos run the charness runner. | Scope collapsed from "arm every consumer repo" to "stop this repo silently disarming itself" once the sibling-repo probe showed no consumer runs this runner. It is the only reachable instance of the gap. | Deleting the `CHARNESS_PRE_PUSH=1` prefix from `.githooks/pre-push` makes `validate_maintainer_setup.py` FAIL; today it passes. Revert output quoted both ways. | done — 76560792, c2ad20d7 |
| 2 (done) | `changed_line_run_trust`: stop a non-HEAD `--head-sha` and a failed git command from reading as "nothing contaminated". Separate "could not establish" from "established clean". | The module docstring (`:18-19`) already asserts callers must read `[]` as "could not establish" while handing every caller an indistinguishable `[]`. | Non-HEAD head-sha and a forced git failure each produce a stated unestablished result; revert output quoted. | done — 0c481d90, 58d7dd44, 2c6c5e51 |
| 3 (done) | `check_mutation_run_proof`: stop `provable: true` standing for a range whose contents were never established. The slice's first task was deciding WHICH input carries the range fact; the answer was that the sampler manifest already carried it (see the slice log), so the classifier stayed pure. | Closes the unproven-gate critique's F6, recorded open on a different owner's surface. | One invocation that refuses and one that still passes, with the range-carrying input named. Adding git resolution to a deliberately pure classifier is a design change, not a fix — if that is the answer, stop and say so. | done — e9338493 |
| 4 | Publish refusal: split unreadable-vs-absent `output_dir`, and stop a draft whose filename lacks `notes` from being invisible. | Irreversible boundary (release publish); the escape is measured five times over. | Absent `output_dir` stays silently publishable (it is the normal state for a repo that drafts no notes); UNREADABLE produces an explicit unestablished record; a `...-release.md` draft for the target tag produces a blocker. The `--generate-notes`-with-no-drafts path stays publishable, pinned by the existing test. | pending |
| 5 | Make the `run-quality-full` bars honest per profile: the 36cpu bar sits BELOW its observed max (false-RED risk) and the 4cpu bar was sized before the armed lane existed. Decide separately whether the shared `BUDGET_SLACK_FACTOR` should change. | The 4cpu bar is a blocking pre-push false red waiting to happen on a slower box. | Each profile's bar restated against its own recorded window, or a dated decision naming why not. A `BUDGET_SLACK_FACTOR` change is scoped as its own decision, since the constant is global across every label and profile. | pending |

Slices 1-4 each change verdict logic on a proof surface, so each owes two
bounded review rounds; slice 5 does not (it changes budget numbers and their
reporting, not a verdict about code) and takes one round.

Compounding risk, named by the plan critique: slices 1 and 2 multiply. Slice 2
widens what counts as unestablished and slice 1 widens when unestablished
blocks, so after both land the blocking surface has grown by the product, not
the sum. Re-measure between them; this is Stop Condition (a) territory. Slice 5
must be measured AFTER slice 1, because arming the lane changes
`run-quality-full` wall time.

Discuss before activation: RESOLVED — the reopened item was settled by evidence
rather than by preference; four items total, each recorded below with the
non-claim that survives it.

- **Hook-runner pin mechanism — REOPENED then SETTLED BY EVIDENCE
  (2026-07-29).** At shaping the operator chose "runner determines push context
  itself, fails closed" from a set of options whose shared premise the plan
  critique falsified, and probing `../ceal`, `../crill`, `../cautilus` then
  falsified the replacement premise too. What the evidence forces: no consumer
  repo runs charness's `run-quality.sh` (ceal and cautilus own theirs, crill
  uses lefthook and has none), `install-git-hooks.sh` already writes only a
  `commit-msg` wrapper downstream by design, and cautilus already owns a
  `pre-push` that any charness-written hook would clobber. So neither original
  option is buildable, and the surviving defect is local: the hook's content is
  unvalidated. Slice 1 was rewritten to that. **Non-claim:** nothing in this
  goal gives any consumer repo push-time changed-line teeth, and this goal does
  not claim they should have them — whether to expose a portable push-time
  arming signal in the quality adapter is a separate design question, not a
  gap this goal closes.
- **The two wrong premises are recorded, not smoothed over.** The chunk was
  ranked #1 on the strength of "silently disarms every consumer repo". That
  reading was wrong twice over, and the slice that survives is materially
  smaller than the one the operator approved at ranking time. If the smaller
  slice no longer earns the #1 position, that is the operator's call to make
  with this correction in hand.

- **Live proof boundary — RESOLVED at shaping (2026-07-29).** The push-time
  refusal is proven against a local bare remote, not `origin`. Decided because a
  real push is an external irreversible action that this goal does not need: the
  hook executes identically against either remote. **Non-claim carried forward:**
  no push to `origin` will have exercised `--refuse-unestablished`, so the
  unproven-gate critique's non-claim is narrowed, not deleted. If the operator
  wants it fully discharged, that is a separate explicit approval.
- **Reversing an owner deferral — RESOLVED at shaping (2026-07-29).** D39 and
  D41 stay deferred; recorded in Non-Goals with the reason. Raised because the
  chunk's original objective text named them and shipping them silently would
  have overridden an owner decision.
- **Bundled scope — RESOLVED at shaping (2026-07-29).** Five surfaces in one
  goal, approved as chunk 1 of the handoff ranking on the grounds that they are
  one lane with one shared env/hook contract. Each slice commits independently,
  so a stop after any slice leaves the tree consistent.
- **Proof-level non-claim — ACKNOWLEDGED at shaping (2026-07-29).** Slice 5 may
  end in "record the bar as deliberately unadvised" rather than a code change.
  That is a documented decision, not a repair, and the closeout must say so
  rather than counting it as a closed gap.

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

### Slice 1: Slice 1 — pin the hook's content, not just its existence

- Objective: Make validate_maintainer_setup.py refuse a .githooks/pre-push that no longer arms the push-time changed-line refusal, instead of checking only that the hook file exists.
- Why this approach: Scope collapsed from the drafted 'arm every consumer repo' once ../ceal, ../crill and ../cautilus showed no consumer repo runs charness's run-quality.sh at all. What survived is local and reachable: deleting one env prefix disarmed the lane with this gate green.
- Commits: 76560792, c2ad20d7
- What changed: scripts/validate_maintainer_setup.py; tests/quality_gates/test_maintainer_hooks.py (new, split from test_quality_runner.py at its length cap); tests/quality_gates/test_quality_runner.py; scripts/boundary-bypass-baseline.json (one key renamed, not added); charness-artifacts/quality/dup-review.json; plugins/charness mirror
- Alternatives rejected: REJECTED runner-self-determines-push-context (the operator's first choice): git exposes no portable pre-push signal and run-quality.sh:650-654 records that overloading --read-only as push-imminent already caused a false stop. REJECTED exporting the hook: half of it is source-repo-only logic and cautilus already owns a pre-push it would clobber. REJECTED rekeying the check on hook existence (round-1 reviewer suggestion): a consumer repo can own an unrelated pre-push. WITHDRAWN the adapter-contract narrowing sub-objective: the quality references already name lefthook/Husky equivalents and CHARNESS_PRE_PUSH appears in no skill reference, so there was nothing to narrow.
- Targeted verification: Reproduced the hole first (disarmed hook -> rc=0, 'Validated maintainer hook setup'). Acceptance re-run across the fix: BEFORE rc=0, AFTER rc=1. 27 parser arms executed: 17 disarming rewrites all refused, 10 legitimate spellings all clean. Falsifier: reverting the check_pre_push_arming call fails 2 tests; gutting the run-quality.sh branch body fails the three-surface pin. 39 tests pass. run_slice_closeout.py green. Changed-line gate run AFTER commit: first BLOCKED on 12 uncovered verdict lines, clean after the in-process tests.
- Test duplication pressure: dup ratchet fired twice. (1) the shared `__main__` epilogue family, 14 of 15 members untouched — classified intentional in dup-review.json. (2) two hand-rolled quote scanners this slice introduced — genuinely mine, removed by extracting _unquoted_indexes rather than classified. check_python_lengths forced the test-file split; both files now under the cap.
- Critique: Two bounded rounds, both changed the design. Round 1: the parser failed OPEN — seven spellings (exec, $REPO_ROOT/, if !, pipe, variable, quoted-value, last-wins) disarmed one branch while the other kept the gate green; all seven parent-executed. Round 2 read the repair and found the same class four more times (comment ending in backslash, fake heredoc in comment/string, escaped-quote desync, .sh-suffixed stub) plus verdict-swallowing || true / & / | . Round-2 repairs are accepted-unreviewed per the cap. Reviewer boundary snapshotted before each spawn and verified at return BEFORE repairing: round 1 clean drift [], round 2 clean drift [].
- Off-goal findings: none filed
- Lessons carried forward: A gate that renders a verdict about another proof surface must fail CLOSED on input it cannot parse; 'recognize the known shape and skip the rest' is the same false-green one level up. Verdict branches exercised only through subprocess runs read as uncovered to the changed-line mapper — prove them in-process or they ship unmeasured.
- Metrics:

### Slice 2: Slice 2 — separate 'could not look' from 'looked and found nothing'

- Objective: Stop changed_line_run_trust reading a failed git command, and a non-HEAD analyzed head, as a clean mutation pool; and close the same conflation on the exported portable twin.
- Why this approach: The trust primitive every changed-line verdict in the lane rests on. Its own module header asserted the contract ('must be read as could not establish, never as nothing found') that the code did not implement — a rule for readers, not a mechanism.
- Commits: 0c481d90, 58d7dd44, 2c6c5e51, 8c9d1f (cover the unresolvable-head arm)
- What changed: scripts/changed_line_run_trust.py; scripts/check_changed_line_mutation_coverage.py; scripts/mutation_coverage_producer.py; skills/public/quality/scripts/changed_line_coverage_gate_lib.py; skills/public/quality/scripts/check_changed_line_coverage.py; tests/quality_gates/test_changed_line_mutation_coverage.py; tests/quality_gates/test_changed_line_coverage_gate.py; docs/public-skill-dogfood.json; charness-artifacts/quality/dup-review.json; plugins/charness mirror
- Alternatives rejected: REJECTED after implementing it: guarding an empty eligible pool (round-1 F5). The gate cannot tell a mis-resolved pool from a repo that legitimately has none, an existing test pins the legitimate case, and refusing there re-breaks the empty-scope contract the same round had just repaired. REJECTED by running it: round 1's suggested `git rev-parse -- <sha>` makes resolved[0] the literal '--'; now rev-parse --verify. REJECTED widening false_green_warning to non-HEAD heads: its message asserts 'analyzed head resolves to HEAD', so emitting it there would state something false — probe_run_trust reports that shape in its own words instead. NOT DONE, recorded: _head_resolves_to_head and uncommitted_pool_changes still collapse git failure to []; both are unreachable as greens (main no longer calls false_green_warning at all, and the producer path re-probes through the consumer, which refuses).
- Targeted verification: Both gaps reproduced first in a scratch repo: a dirty pool reported [] under an explicit older head, and a non-git dir reported [] identically to a clean pool. S25 reproduced in the portable twin (run_gate with an unresolvable base_sha -> ok:true, 'no eligible changed files', classify callback invoked 0 times), upgrading it from SUBAGENT-CONFIRMED to parent-reproduced. Falsifiers: reverting the probe fails 3 tests; reverting the portable raise fails 1. Exit contract re-verified by execution — empty scope under a head mismatch exits 0, a git failure exits 2. 42 + 12 focused tests pass; run_slice_closeout green. Changed-line gate run AFTER commit: BLOCKED twice on unmeasured verdict branches, clean after the in-process tests.
- Test duplication pressure: dup ratchet fired twice more. The first pointed at the exported twin — the finding, not noise, and it is what drove the S25 fix. After two genuine extractions (gate_config, human_line) it began matching two-line `if <cond>: return "<literal>"` guards across unrelated scripts; those two families are classified intentional with the fragments quoted rather than refactored further. check_changed_line_mutation_coverage.py sits at 474/480 code lines (6 left) and test_changed_line_mutation_coverage.py at 732/800 — the next slice touching either owes a cohesive split, not an append.
- Critique: Two bounded rounds, both changed the design. Round 1 found the exit-3 placement made an empty scope refusable (which the consumer itself names as an incoherent blocker), that a git failure was inheriting leniency justified for a dirty worktree, and the core.quotePath quoting gap masked by this machine's config. Round 2 read those repairs and found the empty-scope fix had gone SILENT — the same tree exits 1 on a real blocker via the honest head while the mismatch path printed clean and dropped the disclosure entirely — plus the quoting fix reaching only one of two detectors and the producer narrating a refusal as uncovered changed lines. Round-2 repairs accepted-unreviewed per the cap. Reviewer boundary snapshotted before each spawn and verified at return BEFORE repairing: both rounds exit 0, verdict clean, drift [].
- Off-goal findings: none filed; S25 was in-class rather than off-goal and is closed here.
- Lessons carried forward: A module docstring stating what callers 'must read' a value as is not a mechanism — it is the shape that lets the conflation survive review. When a fix moves a check to satisfy a contract, check what the moved-past path now says: the empty-scope repair was correct on the exit code and wrong on the disclosure. And a public-skill twin is part of the class, not adjacent to it.
- Metrics:

### Slice 3: Slice 3 — an empty range is not changed-line proof

- Objective: Stop check_mutation_run_proof calling a changed-line claim provable when the cited run's range contained no mutation-pool file.
- Why this approach: Closes the unproven-gate critique's F6, recorded open on a different owner's surface. The slice plan's first task was to decide WHICH input carries the range fact.
- Commits: e9338493, plus the _same_commit coverage follow-up
- What changed: scripts/check_mutation_run_proof.py; tests/quality_gates/test_check_mutation_run_proof.py; docs/deferred-decisions.md (D42); plugins/charness mirror
- Alternatives rejected: The planned design question resolved itself against the plan: the goal artifact said adding a head SHA or git access to a deliberately pure classifier would be a design change rather than a fix, and that premise was WRONG. Every manifest the sampler writes already carries the range size — changed_files_before_coverage in sample.json and a '- Changed pool files: N' line in sample.md, both from mutation_manifest_lib.write_manifest — and facts_from_manifest simply did not read it. REJECTED reading changed_files instead: that is the post-coverage sampling subset, so a range whose files were all coverage-excluded would refuse with a reason the input cannot support (round 1 F4). DEFERRED as D42 rather than decided: whether the manifest-less path should exit 3 instead of 0.
- Targeted verification: Reproduced first: an empty-range manifest returned provable:true with 'live over a real base..head range'. Falsifier: reverting the refusal fails 3 tests. Every round-1 and round-2 finding executed rather than reasoned — 4 of round 1's and 4 of round 2's confirmed, and the F5 md positive control pins 7 against neighbours 608 and 3 so a regex matching the wrong line fails. 22 focused tests pass; run_slice_closeout green; changed-line gate run AFTER commit BLOCKED on one unmeasured branch, clean after covering it.
- Test duplication pressure: no dup-ratchet movement this slice. tests/quality_gates/test_check_mutation_run_proof.py grew from 19 to 22 tests and stays well under the cap.
- Critique: Two bounded rounds. Round 1: the base-vs-manifest split let the flag's base wear the manifest's scope; the changed-line arm's own REFUSED report was accepted as a manifest; the changed_files fallback could refuse falsely. Round 2 read those repairs and found neither new refusal branch had a test, that the range hedge was made audible while its twin conclusion_established stayed silent WITH A NEW ASSERTION PINNING THAT SILENCE, that '--base-sha ""' printed a blank-sha contradiction, that an abbreviated sha was called a contradiction with its own full form, and that a baseless manifest still lent its count. It also caught the parent citing the empty-scope critique's F9 backwards — F9 argues the exit code must CARRY the meaning, and it was cited as license to leave the exit code alone. Reviewer boundary snapshotted before each spawn and verified at return BEFORE repairing: both rounds exit 0, verdict clean, drift [].
- Off-goal findings: none filed
- Lessons carried forward: When a plan says a fix needs new capability, check whether the fact is already on disk — this one had been written by the sampler on every run for as long as the gate existed. And a deferral is only honest if the cited precedent says what you claim: quoting F9 as 'leave the exit code alone' inverted an argument that the exit code is the only thing anyone reads.
- Metrics:

## Context Sources

- Source: handoff entry #6 (D39 / D41) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #7 (Gaps this session named and did not close) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `charness-artifacts/critique/2026-07-29-release-notes-publish-escape.md`
- Cited path: `charness-artifacts/critique/2026-07-29-unproven-gate-status.md`
- Cited path: `docs/deferred-decisions.md` (D39/D41) — resolved; the draft-time MISSING marker came from the handoff's `./` relative link, not from an absent file.

## Interview Decisions

- **D39/D41 disposition.** Family considered: out-of-scope / D41-only /
  both-in. Chosen: out of scope, DEFER upheld. Rejected `both-in` because it
  reverses a recorded owner decision whose reopen trigger has not fired, and
  `D41-only` because D41's own deferral says the mapper widening over-matches
  and owes a separate two-round review. single-point: an owner decision on this repo's
  deferred-decisions ledger, not a value that varies by host or profile.
- **Hook-runner pin shape.** Family considered: runner self-determines and
  fails closed / export the hook plus a drift validator / both / defer to
  activation. Chosen: runner self-determines, fails closed. Rejected the
  export-plus-validator path as the primary because it keeps the teeth
  contingent on the consumer's hook copy being current — the same dependency
  that produced the hole; it stays available as an additive follow-up.
  axis: consumer-repo install (RETRACTED — see Boundaries; the sibling-repo
  probe reduced it to single-point).
- **Timebox.** Family considered: none / 2h / 3h. Chosen: none. Rejected the
  timed options because each slice is independently committable and already
  supplies a natural stopping point, so a clock would add early-close reporting
  overhead without changing what gets built. single-point: a session-shape preference, not a system axis.
- **Mode.** Artifact-only shaping this turn; the goal is inert until `/goal`.
  Not asked — the `/achieve` invocation on a chunker-drafted skeleton settles
  it, and it is stated here rather than interrogated.

## Plan Critique Findings

One bounded round, parent-delegated: a `bounded-reviewer` (read-only
Read/Grep/Glob, no host addressing name, session model inherited per the Claude
Code host branch of the per-host subagent contract) on the scope/anchoring/
wrong-next-action angle. Delivery state: findings-received. Reviewer boundary
snapshotted before the spawn and verified at return BEFORE any repair — exit 0,
`verdict: clean`, drift `[]`, window `w-20260729T115209Z-3785262`. Every finding
folded below was re-run by the parent; none was accepted on the reviewer's
reading alone.

Blockers folded:

- **The publish-refusal premise was inverted.** The plan computed
  `420000/182923 = 2.30x` against the median; the advisory divides by
  `max_recent_elapsed_ms` (`runtime_budget_lib.py:194-201`). Parent re-ran it:
  36cpu max is 551850, ratio 0.76 — the bar is below its own worst run, a
  false-RED risk rather than a loose bar. The genuinely invisible bar is the
  4cpu one. Slice 5 rewritten; Boundaries corrected.
- **Slice 3's acceptance criterion was unimplementable.** `classify_run_proof`
  takes only `claim`/`event`/`base_sha`/`conclusion`, so the named invocation
  cannot express an empty range and any test against it would have passed for a
  reason other than the one it named — the defect class this goal repairs.
  Acceptance #2 and slice 3 rewritten to make "which input carries the range"
  the slice's first decision.
- **The hook premise was factually wrong — twice.** The reviewer found the
  first error: no `pre-push` is exported, so "an old vendored hook drops the
  teeth" could not happen. Reopening that with the operator produced the second
  correction, from a probe of `../ceal`, `../crill`, `../cautilus` at the
  operator's direction: no consumer repo runs charness's runner at all, so the
  reviewer's own replacement framing ("consumer repos have never had these
  teeth, therefore arm them") was also unbuildable. The surviving defect is
  local content-drift on this repo's own hook. Recorded as two corrections
  rather than one, because the second was not visible from inside the repo.
- **Slice order was backwards.** `changed_line_run_trust` has one consumer, not
  "every later verdict"; slices 3/4/5 do not import it. Arming now precedes
  widening, and the compounding risk between the two is named in the Slice Plan.

Should-fix folded: three profile blocks not two; `BUDGET_SLACK_FACTOR` is a
global constant with two other recorded blind bars; slice 4's "blocker OR
unestablished" hedge split into different answers for absent vs unreadable;
corrected test paths; the D41 dotted-import constraint added to the verification
plan.

Over-worry raised and NOT folded: the reviewer confirmed the D39/D41 exclusion
is coherent rather than merely conservative (neither reopen trigger fires — no
slice removes tests, and slice 4's surface is already mapped by
`suggest_mutation_coverage_command.py`'s quoted-path pattern). Recorded as
verified rather than acted on.

Not established by the review: whether any portable push-context signal exists
for slice 1 (the reviewer found none in tree and could not rule out one it did
not grep for); no runtime measurement was taken, so findings about the bars rest
on the recorded window rather than a live run.

## Coordination Cues

- Routing at shaping: `handoff` chunked routing produced this skeleton (chunk 1
  of 5, operator-selected); `achieve` Before-phase shaped it. Routed from
  installed skill metadata and model judgment, not from an inline phase map.
- Planned during the run: `impl` per slice, `prove` at each slice stop gate,
  `critique` for the two bounded review rounds each verdict-logic slice owes,
  `quality` for the bundle-boundary gate, `issue` for any off-goal finding,
  `retro` at closeout.
- `debug` is NOT planned up front: every gap here was already reproduced at
  shaping with the trigger recorded in Boundaries, so there is no open
  root-cause question. Load it if a repair does not behave as the reproduction
  predicted.
- No tracked issue originates this goal, so no `Close #N` closeout is owed;
  record `Issue closeout: n/a — no originating tracked issue` at completion
  unless a slice files one.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
