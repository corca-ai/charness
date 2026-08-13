# Open Backlog Execution Ledger

Opening cohort: the 22 issues listed in the 2026-08-12 goal's Backlog Recount.
This ledger turns that fixed scope into per-issue execution state. A row moves
from `premise-needed` only after the issue and comments are re-read and a
falsifiable premise is recorded. `unproven-defer` is an honest disposition, not
a closure claim: it requires a tracker-visible explanation, owner, and revisit
trigger.

| Issue | Initial owner/slice | Reported invariant to recheck | Owning boundary / first reader | Verdict logic | Required evidence / disposition criterion | State |
| --- | --- | --- | --- | --- | --- | --- |
| #527 | 4, decision preparation | users can choose destructive skills safely and evaluate public skills | public skill metadata and first-reader docs | no | operator decision or tracker-visible deferral before implementation | unproven-defer — the issue is an enhancement proposal with unresolved invocation-lock, reader-documentation, success-signal, and maturity-policy choices. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/527#issuecomment-5270654051; repository operator owns the decision brief at `charness-artifacts/issue/2026-08-13-issue-527-brief.md`; revisit before implementation or on an explicit minimum viable boundary. |
| #528 | 4, consumer adapter | a coverage policy sub-key can be deliberately absent without silent refill | quality adapter resolution / consumer operator | yes | consumer reproduction plus resolver and warning behavior | split — Charness already resolves dotted deliberately-absent subkeys without silent refill. The cmanki consumer maintainer owns declaration migration; the Charness quality-policy owner owns the root-relative hook-discovery decision. Documentation now matches whole-field compatibility behavior. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/528#issuecomment-5269713927; revisit when cmanki adopts the declaration or a scoped hook-discovery decision is supplied. |
| #539 | 3, issue create | create payload always supplies a usable issue URL identity | issue create backend parser / issue reporter | yes | backend-shaped fixture and ledger readback behavior | closing — create stdout is shape-validated; bare numbers retain number and can use a validated readback URL, with malformed URL regressions. Behavior confirmed on the LIVE GitHub backend (this session's `create` of #609 returned a validated complete `created_url`), a channel distinct from the fake-backend fixtures. CLOSED — carrier `c3d3fdc3`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #542 | 3, closeout evidence | a CLI/body target disagreement has a distinct refusal | evidence crosswalk / closeout author | yes | carrier-source cases and refusal payload | closing — close-with-comment refuses a distinct singleton manual-declaration/CLI-target disagreement before backend mutation, while commit-message and multi-target carriers retain not_singleton. Behavior confirmed through a SUBPROCESS CLI run against a synthetic protected world in a temp repo (distinct from the in-process backend-spy tests, and touching no backend): disagreeing singleton -> `target_disagreement`; matching singleton -> a different refusal; commit-message carrier -> `not_singleton`. Scope disclosure: this repo's crosswalk instance is RETIRED, so the refusal cannot fire here; it is live for a consumer that checks in its own crosswalk. CLOSED — carrier `7ba3f4db`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #546 | 2, runtime verdict | a budget with no selected sample cannot read as protective | runtime budget verdict / quality operator | yes | selected-profile fixtures and exit/result assertions | unproven-defer — runner membership is proven; conditional-label and consumer-runner intent remain. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/546#issuecomment-5268428686; revisit when an adapter declares conditional-label expectations or a consumer runner supplies its own contract. |
| #550 | 4, adapter refactor | duplicated adapter resolver bodies can share behavior without losing distinctions | adapter resolver consumers | no | bounded equivalence map and focused regression suite | unproven-defer — current duplicate-ratchet hard arm identifies 12 unrelated untouched families, not a resolver family. A safe refactor needs a bounded resolver equivalence map and consumer contract tests. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/550#issuecomment-5270164395; revisit when a concrete family names resolver members or an adapter change requires the common preamble. |
| #582 | 1, umbrella disposition | proof/evidence infrastructure lacks machine-owned state where claimed | enumerated cited producer/reader pairs | unknown | enumerate every cited claim; close only when every child is proven or not-applicable | split — #525's live README-proof residual is locally proven: Claim Ledger Evidence cells now fail closed on non-path-backed state. #514/#524/#535 are backend CLOSED and do not prove their historic class; #524 taxonomy and #535 generic rebind remain deliberate non-implementations. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/582#issuecomment-5269364370; final direct-to-default readback remains required. |
| #583 | 1, umbrella disposition | named verification surfaces can become inert while green | enumerated cited producer/reader pairs | unknown | enumerate every cited claim; close only when every child is proven or not-applicable | unproven-defer — re-read found the cited pickup specs deleted and their current directory-scoped outcome judge owned by surviving handoff scenarios; #597 repaired the cited empty-fixture fail-open. No concrete producer/reader/fixture supports a generic premise gate. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/583#issuecomment-5269219339; revisit on a live stale test premise with a bounded owner. |
| #584 | 1, umbrella disposition | named surfaces discard decidable state into prose | enumerated cited producer/reader pairs | unknown | enumerate every cited claim; close only when every child is proven or not-applicable | split — SessionStart routing and #532's representative planner read-cost slice are proven, but the broader planner rollout is a deliberate widening follow-up, so not every enumerated cited item is `proven` or `not-applicable`. HELD BACK from the 2026-08-13 cohort carrier on this ledger's own Umbrella Closure Contract; the earlier `local proof` label was accurate about what shipped and was wrongly read as closure eligibility. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/584#issuecomment-5274365205; revisit when the remaining rollout lands or is recorded as an independently owned item dispositioned not-applicable to this umbrella. |
| #586 | 2, wired-proof path | a check runs through its actual caller path | check caller and consumer | yes | end-to-end wired-path regression proof | unproven-defer — inspected candidate is a superseded helper; both production closeout consumers use the equivalent wired loop, whose failure branch is proven. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/586#issuecomment-5268965258; revisit on a reproducible operator-path bypass. |
| #587 | 1, premise disposition | the original mutation-coverage blocker framing remains refuted or has live residue | mutation coverage lane / release operator | unknown | re-read retargeted issue and measurement; tracker-visible defer, close, or split decision | unproven-defer — GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/587#issuecomment-5268526904; revisit on original-session recovery or a reproducible false blocker |
| #588 | 4, public helper | public dogfood invocation fails gracefully without internal policy files | consumer helper / skill author | no | clean consumer-shaped invocation and error contract | closing — typed policy-absence applicability with an empty matrix for a policy-absent synthetic consumer; present invalid policy stays an error. Behavior confirmed by running the PLUGIN entrypoint (a genuinely separate file) against a temp-dir consumer. Scope correction from the closeout review: the `skills/public/quality/` wrapper is NOT a separate copy — its bootstrap imports the same root module — so this establishes mirror fidelity and consumer-shaped invocation, not independence from the root module. CLOSED — carrier `c3d3fdc3`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #589 | 2, quality verdict | a fully applied preset lineage has a reachable clean state | declaration lifecycle verdict / quality operator | yes | applied and missing lineage fixtures with expected result | closing — validator-accepted prescribed lineage reconciles only with every exact declared command; missing, unavailable, and metadata-only states render with focused proof. Behavior confirmed through the live repository planner detail, distinct from the lifecycle fixtures. Scope: the `reconciled` branch is reached by no live repo state and remains fixture-proven. CLOSED — carrier `c3d3fdc3`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #590 | 2, CI mutation report | a skipped JS mutation stage is distinguished from a missing report | scheduled workflow diagnostics / CI reader | yes | workflow fixture or CI-shaped parser proof | closing — this row's own criterion was "workflow fixture or CI-shaped parser proof", and the missing half now exists: `tests/quality_gates/test_mutation_issue_report_body.py` EXTRACTS the `Open or update mutation issue` script body from all three checked-in copies and EXECUTES it under `node` with `github`/`context` stubbed, driving defects B and D directly rather than asserting substrings. The B/D repair is ported to both shipped consumer templates, so the title's defect is no longer true of every install. Round 1 found the D repair silently disabled the B repair — `clampBody` truncates from the front and the run-log tail was last, so the runs with the most diagnostic output lost exactly the artifact B exists to attach; diagnostics now precede the summary and the survival is asserted. Round 2 narrowed the empty-log claim, which had asserted a whole-file property from the last 80 lines. Carrier `dd473642`; two-round critique as above. Non-claim: no CI run exercised the repaired step, and none can until the pipeline is red. GitHub OPEN pending the issue closeout floor |
| #595 | 2, runtime verdict | computed runtime signals affect an exit or typed disposition | runtime budget result / quality operator | yes | signal-to-exit behavior tests | closing — explicit advisory disposition with a named final consumer, and focused proof. Behavior confirmed through the selected `check-runtime-budget` lane against live measurement (108044ms latest vs 105000ms budget), distinct from the 50 unit tests. CLOSED — carrier `c3d3fdc3`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #597 | 2, fixture proof | an empty tool-fixture set cannot pass as exercised verification | fixture checker and quality gate caller | yes | empty/nonempty fixtures and gate wiring proof | closing — the empty-corpus refusal now keys on COMPARISONS PERFORMED, not on fixture count. Round 1 found the first repair carried the class it fixed (a digest checked against `sha256("")` counted as a comparison, so one fixture reporting `2 captured stream(s) compared` opened no file); the counter is now split into digest checks and file-backed checks with the floor on the latter. Executed proof: the tracker carrier's exact reproduction now exits 1, the constant-only corpus exits 1, and the live corpus reports `1 fixture(s): 2 stream digest(s) checked, 1 against checked-in capture file(s)`. The run-quality lane wiring is pinned by its own test (the pre-existing drift guard was one-directional). Scope disclosure: `file_backed` establishes that a digest matched bytes checked in under the fixture directory, NOT that those bytes came from a tool run; the docstring and the refusal now say exactly that. Carrier `dd473642`; two-round critique `../critique/2026-08-13-four-proof-surface-repairs-two-round-critique.md`. GitHub OPEN pending the issue closeout floor |
| #599 | 4, operator discovery | an operator can discover readers of a symbol/path/key before removal | code-change author | no | query contract and representative consumer search | unproven-defer — `removed_name_consumers.py` only advises on deleted Python module-level names and cannot query path/key/phrase, glob, assertion, or source/plugin reader classes. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/599#issuecomment-5270339111; revisit on an approved result taxonomy or a removal/rename slice needing an unrepresented reader class. |
| #601 | 4, quality capability | quality identifies avoidable CLI test-harness subprocess and comment-only invariant pathologies | quality reviewer | unknown | selected detection boundary or tracker-visible defer with rationale | unproven-defer — Charness has a narrow subprocess-entrypoint advisory, but no current fixture/contract/threshold for #601's real-binary pure-render, wall-clock skew, or comment-only invariant classes. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/601#issuecomment-5270350837; revisit with an opt-in timing/spawn producer plus fixture, or a reproduced Charness CLI-harness class. |
| #602 | 3, issue create | creation has an in-grammar verification path and avoids placeholder priming | issue creator | yes | create verification command, help text, and substantive-title behavior | closing — typed `verify-create` binds the selected backend view template plus returned issue number and repository evidence; byte fidelity requires the original body file and help avoids exact placeholder priming. Behavior confirmed on the LIVE GitHub backend: `verify-create --number 609 --body-file` returned `ok: true`, `body_verified: true`. CLOSED — carrier `c3d3fdc3`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #605 | 1, premise disposition | trim-back loop is reachable or provably redundant under the narrowed parser | documented-command checker / docs author | unknown | construct a trigger or record a bounded impossibility argument and tracker disposition | unproven-defer — GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/605#issuecomment-5268527170; revisit on a live trigger or a bounded impossibility proof |
| #606 | 2, ratchet verdict | baseline regeneration and all enforced counts agree | boundary-bypass ratchet / quality operator | yes | canonical rebuild, full count cross-check, and safe regeneration path | closing — the canonical writer and integrity tripwire cover every persisted verdict input (the digest set equals the persisted set by construction); guarded replacement emits a reviewable metadata/summary/key delta and refuses malformed or non-file paths. Behavior confirmed by exercising the repaired write and refusal paths against a baseline at an absolute temp path — fresh write carried `writer_integrity_sha256`; a mutated baseline re-written without `--confirm-baseline-delta` returned `ok: false` plus the rendered delta; non-object JSON returned `ok: false`. Distinct from both the 120 focused tests and an evaluation-only live run, which enters none of these branches. Known gap: a baseline holding literal `null` is indistinguishable from `no file` in the writer's guard and is replaced without confirmation. CLOSED — carrier `7ba3f4db`, pushed to `main`; `verify-closeout --carrier direct-commit --expect-state CLOSED` returned `verified` with no state mismatch, and an independent `gh issue list --state open` inventory reconciles. |
| #607 | 5, settlement capability | subprocess inventory classifies conservative settlement risk | standing-test economics inventory / quality reviewer | yes | static callsite fixtures distinguish literal-bounded, unbounded-capture, and syntax-unknown seams without claiming runtime child semantics | closing — the JS deadline path is rewritten as a per-call delimiter walk in a new `js_settlement_scan_lib.py`. Executed before/after over the carrier's own four cases: `timeout: 30 * 1000` and `5 + delay` move present->unknown, `timeout: 0` moves present->absent, and the borrowed sibling deadline moves present->absent, while a real `timeout: 100` still reads finite; the Python path is byte-identical at 767 seams. Two review rounds found five further fabrication paths beyond the reported one — regex literals producing a balanced-but-wrong region, call names inside comments and strings, options nested one container deep, JSX `/>`, and a missing newline bail that turned any local mis-parse into a file-wide desync — each reproduced executably before repair. Scope disclosure: this repo's test tree contains no JS/TS seams at all, so every repair here is fixture-proven and consumer-facing, not proven against live repo state. Carrier `dd473642`; two-round critique as above. GitHub closure carried by this commit; classified `feature` because the resolution shipped the capability the issue asked for, and the false-`finite` classifications were defects inside it |

## Row Update Contract

For any selected row, record in the goal Slice Log or its owning durable record:

- current falsifiable premise and its source re-read;
- reproduction or bounded search, including the candidate scope and first reader;
- proof channel distinct from tracker state when resolving behavior;
- `verdict logic: yes/no/unknown` final classification and named deciding surface;
- disposition: `proven`, `unproven-defer`, `split`, or `not-applicable`, plus
  a tracker-visible carrier/comment and revisit trigger for every non-closure.

## Late Arrivals (2026-08-13, second session)

Recorded here rather than silently absorbed into the cohort. None is a completion
requirement for this goal.

- [#609](https://github.com/corca-ai/charness/issues/609) — the claims-review
  distinctness floor reduced to string inequality. RESOLVED locally by schema v2
  (recorded `observer_distinctness`, no passing `same-agent` kind, a review
  narrative that must be ADDED by the evidence commit and bound to the prepared
  commit, and a first-class `verdict: unproven`). Two rounds; round 1 found a
  second prepare over an outstanding marker fell through to a lane that validates
  nothing, round 2 found the same fall-through reachable through a non-default
  adapter `output_dir`. Carrier `dd473642`; GitHub closure carried by this commit.
- [#610](https://github.com/corca-ai/charness/issues/610) — the claims verdict
  never reaches the published release record. RESOLVED: every record written after
  a validated claims review carries a fixed `## Claims Review` section naming the
  record path, verdict, distinctness kind and signal, and the narrative, with
  `unproven` stating the negative property rather than the bare token. Two rounds;
  round 2 found the signal still able to satisfy three closeout sentinels, and an
  assertion that passed with the repair reverted. Carrier: this commit.
- [#611](https://github.com/corca-ai/charness/issues/611) — the claims resume lane
  never runs the notes-file preflight, so drafted notes and issue closeout can be
  silently dropped. RESOLVED for the notes half: the preflight runs on the lane,
  above the artifact commit and guarded on `release_exists`, and the planner now
  places `--notes-file` when exactly one candidate exists. The `--close-issue` half
  stays unenforced on this lane and is recorded as such — no durable record of the
  original intent exists at a prepared stop. Two rounds; round 2 found the gate
  creating the state it then refuses. Carrier: this commit.
- [#613](https://github.com/corca-ai/charness/issues/613) — the claims floor reads
  a hardcoded record path, so a non-default adapter `output_dir` made it blind.
  RESOLVED: the path is derived once from `output_dir` and consumed by the floor,
  the planner, the resume publish tail, and the closeout recovery; the loud refusal
  is replaced by `assert_record_readable`, which refuses positively when the record
  is not readable at the derived path. Two rounds; round 2 found the strip on one
  side reintroducing the two-derivations class, and `git add` aborting on a
  pathspec matching nothing. Carrier: this commit.

New tracker issues after the opening recount are late arrivals. They stay outside
this cohort unless the goal is explicitly amended; they are recorded as an
off-goal dependency and prevent only the affected claimed row or umbrella from
closing when their behavior is required for that row's stated invariant.

## Umbrella Closure Contract

Before #582, #583, or #584 can close, Slice 1 records an enumerated cited-claim
list for that umbrella: claim, actual producer, first reader, owned child row or
independent work item, durable carrier or evidence location, and current state.
The umbrella stays open while any cited child or required late-arrival dependency
is `premise-needed`, `unproven-defer`, or `split`; a tracker-visible explanation
names the remaining owner and revisit trigger. An umbrella may close only after
every enumerated item is `proven` or `not-applicable` on evidence independent of
the umbrella tracker text.

## Slice 1 Re-read Notes

- #582 — premise holds. Its closed member issues do not resolve the umbrella:
  #525's residual is a live evidence-path validation gap, while #524 and #535
  are recorded cost/rule dispositions and #514 is now closed. The umbrella's
  independent work item is an evidence-path reader/validator, with this ledger
  as the temporary carrier until its owning implementation record exists.
- #583 — premise holds. #568 still lacks the described collapse detector and
  #569's fixture-rule cost decision leaves the cheaper empty-fixture fail-open
  routed to #597. The umbrella cannot close until the eval-premise residue and
  #597 disposition are independently recorded.
- #584 — premise holds. #531 and #532 are closed but the cited SessionStart
  per-repo routing and planner read-cost computations remain live implementation
  items. Their durable carrier is #584 until implementation creates an owning
  record; no closed child is treated as proof of behavior.
- #587 — premise re-read. Its original serial-aggregate remedy is refuted; the
  remaining false-blocker question depends on the unavailable original session
  record. State: `unproven-defer`; the tracker body itself carries the reason and
  reopens when that source is recovered.
- #605 — premise re-read. Neither a live trim-back trigger nor an impossibility
  proof exists. State: `unproven-defer`; it remains open until one evidence path
  is established, rather than being deleted or declared fixed.
- #546 — 2026-08-12 re-read and current probe: the repository-only membership
  reader is armed, reconciles 37 budget labels against 102 runner labels, and
  finds none unknown; the selected profile has no missing samples. The issue's
  remaining named-but-never-run conditional and consumer-runner cases require
  an adapter-declared expectation. GitHub disposition:
  https://github.com/corca-ai/charness/issues/546#issuecomment-5268428686.
- #584 — local proof: SessionStart configured-artifact routing is proven by
  `e3822458`; the #532 successor now measures representative quality/handoff
  reads under source and plugin layouts with two review rounds recorded in
  `charness-artifacts/critique/2026-08-13-issue-584-planner-read-cost-resolution.md`.
  GitHub remains OPEN with tracker carrier
  https://github.com/corca-ai/charness/issues/584#issuecomment-5269582606 and
  pending cohort closeout;
  debug/retro/issue/gather rollout is a deliberate widening follow-up.
- #595 — `c9d25da4` measured a live latest-only spike and made its advisory
  contract explicit in human and structured output while retaining median-red
  enforcement; tracker closure waits for the final direct-to-default carrier.
- #597 — `08b01ddc` makes empty fixture evidence refuse and wires the checker
  into the quality runner; tracker closure waits for the final direct-to-default
  carrier.
