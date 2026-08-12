# Open Backlog Execution Ledger

Opening cohort: the 22 issues listed in the 2026-08-12 goal's Backlog Recount.
This ledger turns that fixed scope into per-issue execution state. A row moves
from `premise-needed` only after the issue and comments are re-read and a
falsifiable premise is recorded. `unproven-defer` is an honest disposition, not
a closure claim: it requires a tracker-visible explanation, owner, and revisit
trigger.

| Issue | Initial owner/slice | Reported invariant to recheck | Owning boundary / first reader | Verdict logic | Required evidence / disposition criterion | State |
| --- | --- | --- | --- | --- | --- | --- |
| #527 | 4, decision preparation | users can choose destructive skills safely and evaluate public skills | public skill metadata and first-reader docs | no | operator decision or tracker-visible deferral before implementation | premise-needed |
| #528 | 4, consumer adapter | a coverage policy sub-key can be deliberately absent without silent refill | quality adapter resolution / consumer operator | yes | consumer reproduction plus resolver and warning behavior | split — Charness already resolves dotted deliberately-absent subkeys without silent refill. The cmanki consumer maintainer owns declaration migration; the Charness quality-policy owner owns the root-relative hook-discovery decision. Documentation now matches whole-field compatibility behavior. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/528#issuecomment-5269713927; revisit when cmanki adopts the declaration or a scoped hook-discovery decision is supplied. |
| #539 | 3, issue create | create payload always supplies a usable issue URL identity | issue create backend parser / issue reporter | yes | backend-shaped fixture and ledger readback behavior | local proof — create stdout is shape-validated; bare numbers retain number and can use validated readback URL, with malformed URL regressions. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/539#issuecomment-5269681471; final cohort closeout remains required. |
| #542 | 3, closeout evidence | a CLI/body target disagreement has a distinct refusal | evidence crosswalk / closeout author | yes | carrier-source cases and refusal payload | local proof — close-with-comment now refuses distinct singleton manual-declaration/CLI-target disagreement before backend mutation, while aggregate carriers retain not_singleton. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/542#issuecomment-5269820465; final cohort closeout remains required. |
| #546 | 2, runtime verdict | a budget with no selected sample cannot read as protective | runtime budget verdict / quality operator | yes | selected-profile fixtures and exit/result assertions | unproven-defer — runner membership is proven; conditional-label and consumer-runner intent remain |
| #550 | 4, adapter refactor | duplicated adapter resolver bodies can share behavior without losing distinctions | adapter resolver consumers | no | bounded equivalence map and focused regression suite | unproven-defer — current duplicate-ratchet hard arm identifies 12 unrelated untouched families, not a resolver family. A safe refactor needs a bounded resolver equivalence map and consumer contract tests. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/550#issuecomment-5270164395; revisit when a concrete family names resolver members or an adapter change requires the common preamble. |
| #582 | 1, umbrella disposition | proof/evidence infrastructure lacks machine-owned state where claimed | enumerated cited producer/reader pairs | unknown | enumerate every cited claim; close only when every child is proven or not-applicable | split — #525's live README-proof residual is locally proven: Claim Ledger Evidence cells now fail closed on non-path-backed state. #514/#524/#535 are backend CLOSED and do not prove their historic class; #524 taxonomy and #535 generic rebind remain deliberate non-implementations. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/582#issuecomment-5269364370; final direct-to-default readback remains required. |
| #583 | 1, umbrella disposition | named verification surfaces can become inert while green | enumerated cited producer/reader pairs | unknown | enumerate every cited claim; close only when every child is proven or not-applicable | unproven-defer — re-read found the cited pickup specs deleted and their current directory-scoped outcome judge owned by surviving handoff scenarios; #597 repaired the cited empty-fixture fail-open. No concrete producer/reader/fixture supports a generic premise gate. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/583#issuecomment-5269219339; revisit on a live stale test premise with a bounded owner. |
| #584 | 1, umbrella disposition | named surfaces discard decidable state into prose | enumerated cited producer/reader pairs | unknown | enumerate every cited claim; close only when every child is proven or not-applicable | local proof — SessionStart routing plus #532's representative quality/handoff planner read-cost slice are proven; broader planner rollout remains a deliberate widening follow-up. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/584#issuecomment-5269582606; final cohort closeout remains required. |
| #586 | 2, wired-proof path | a check runs through its actual caller path | check caller and consumer | yes | end-to-end wired-path regression proof | unproven-defer — inspected candidate is a superseded helper; both production closeout consumers use the equivalent wired loop, whose failure branch is proven. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/586#issuecomment-5268965258; revisit on a reproducible operator-path bypass. |
| #587 | 1, premise disposition | the original mutation-coverage blocker framing remains refuted or has live residue | mutation coverage lane / release operator | unknown | re-read retargeted issue and measurement; tracker-visible defer, close, or split decision | unproven-defer — tracker carrier https://github.com/corca-ai/charness/issues/587#issuecomment-5268526904; revisit on original-session recovery or a reproducible false blocker |
| #588 | 4, public helper | public dogfood invocation fails gracefully without internal policy files | consumer helper / skill author | no | clean consumer-shaped invocation and error contract | local proof — root, shipped quality, and plugin helpers return typed policy-absence applicability with an empty matrix for a synthetic consumer; present invalid policy stays an error. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/588#issuecomment-5270306863; final cohort closeout remains required. |
| #589 | 2, quality verdict | a fully applied preset lineage has a reachable clean state | declaration lifecycle verdict / quality operator | yes | applied and missing lineage fixtures with expected result | local-proven — validator-accepted prescribed lineage reconciles only with every exact declared command; missing, unavailable, and metadata-only states are rendered with focused proof. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/589#issuecomment-5268917088; final direct-to-default carrier/readback remain required. |
| #590 | 2, CI mutation report | a skipped JS mutation stage is distinguished from a missing report | scheduled workflow diagnostics / CI reader | yes | workflow fixture or CI-shaped parser proof | local-proven — prior repair's scheduled CI descendant recorded successful select/run/summarize stages; the original missing-JS-report collateral path is not present. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/590#issuecomment-5268992650; final direct-to-default carrier/readback remain required. |
| #595 | 2, runtime verdict | computed runtime signals affect an exit or typed disposition | runtime budget result / quality operator | yes | signal-to-exit behavior tests | local-proven — explicit advisory disposition and focused proof. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/595#issuecomment-5268493969; final direct-to-default carrier and readback are the revisit boundary |
| #597 | 2, fixture proof | an empty tool-fixture set cannot pass as exercised verification | fixture checker and quality gate caller | yes | empty/nonempty fixtures and gate wiring proof | local-proven — empty refusal, record shape, and runner wiring proven. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/597#issuecomment-5268494170; final direct-to-default carrier and readback are the revisit boundary |
| #599 | 4, operator discovery | an operator can discover readers of a symbol/path/key before removal | code-change author | no | query contract and representative consumer search | unproven-defer — `removed_name_consumers.py` only advises on deleted Python module-level names and cannot query path/key/phrase, glob, assertion, or source/plugin reader classes. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/599#issuecomment-5270339111; revisit on an approved result taxonomy or a removal/rename slice needing an unrepresented reader class. |
| #601 | 4, quality capability | quality identifies avoidable CLI test-harness subprocess and comment-only invariant pathologies | quality reviewer | unknown | selected detection boundary or tracker-visible defer with rationale | unproven-defer — Charness has a narrow subprocess-entrypoint advisory, but no current fixture/contract/threshold for #601's real-binary pure-render, wall-clock skew, or comment-only invariant classes. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/601#issuecomment-5270350837; revisit with an opt-in timing/spawn producer plus fixture, or a reproduced Charness CLI-harness class. |
| #602 | 3, issue create | creation has an in-grammar verification path and avoids placeholder priming | issue creator | yes | create verification command, help text, and substantive-title behavior | local proof — typed `verify-create` binds the selected backend view template plus returned positive issue number and repository evidence; byte fidelity requires the original body file and help avoids exact placeholder priming. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/602#issuecomment-5270132863; final cohort closeout remains required. |
| #605 | 1, premise disposition | trim-back loop is reachable or provably redundant under the narrowed parser | documented-command checker / docs author | unknown | construct a trigger or record a bounded impossibility argument and tracker disposition | unproven-defer — tracker carrier https://github.com/corca-ai/charness/issues/605#issuecomment-5268527170; revisit on a live trigger or a bounded impossibility proof |
| #606 | 2, ratchet verdict | baseline regeneration and all enforced counts agree | boundary-bypass ratchet / quality operator | yes | canonical rebuild, full count cross-check, and safe regeneration path | local-proven — canonical writer and integrity tripwire cover every persisted verdict input; guarded replacement emits reviewable metadata/summary/key delta and refuses malformed or non-file paths. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/606#issuecomment-5269188496; final direct-to-default readback remains required. |
| #607 | 5, settlement capability | subprocess inventory classifies conservative settlement risk | standing-test economics inventory / quality reviewer | yes | static callsite fixtures distinguish literal-bounded, unbounded-capture, and syntax-unknown seams without claiming runtime child semantics | local proof — detail inventory emits callsite-attributed deadline, lifecycle, tree-termination, and output-bounding signals; only literal numeric deadlines yield finite, and runtime-only facts remain `unknown`. GitHub OPEN; tracker carrier https://github.com/corca-ai/charness/issues/607#issuecomment-5270588693; final cohort closeout remains required. |

## Row Update Contract

For any selected row, record in the goal Slice Log or its owning durable record:

- current falsifiable premise and its source re-read;
- reproduction or bounded search, including the candidate scope and first reader;
- proof channel distinct from tracker state when resolving behavior;
- `verdict logic: yes/no/unknown` final classification and named deciding surface;
- disposition: `proven`, `unproven-defer`, `split`, or `not-applicable`, plus
  a tracker-visible carrier/comment and revisit trigger for every non-closure.

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
