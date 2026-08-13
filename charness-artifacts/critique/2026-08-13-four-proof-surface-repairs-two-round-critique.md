# Four Proof-Surface Repairs Two-Round Critique

Date: 2026-08-13

## Decision Under Review

Repair four proof surfaces whose bounded closeout reviews found live defects that
their prior `local-proven` labels hid (#597, #607, #590, #609), plus the
release-resume ergonomics gap the claims-review contract named. Every one of the
five changes verdict logic on a surface that renders a judgement about other code
or artifacts, so each owed two bounded review rounds.

## Failure Angles

- A refusal keyed on the wrong quantity: counting artefacts rather than counting
  the work actually performed on them.
- A static scanner publishing a confident verdict about text it never parsed —
  worse when the mis-parse happens to balance, because only an unbalanced one
  degrades to `unknown`.
- A repair that carries the class it fixes, or that silently disables a sibling
  repair.
- A floor reachable only through one lane, where every other lane publishes
  unchecked.
- Guidance that names a command an operator will run and a gate will then refuse.

## Round 1

Three bounded reviewers, one per surface. Boundary window `2026-08-13-handoff-r1`,
verified `clean` with no parent declarations before any fold.

- **#597 fixture gate.** The comparison counter treated a digest checked against
  the constant `sha256("")` as a comparison, so one fixture carrying it twice
  reported `2 captured stream(s) compared` while opening no file — a floor
  satisfiable by typing 64 known characters. An existing test pinned that
  bypass as intended behaviour.
- **#607 JS scanner.** Three fabrication paths: `/\//` made `//` read as a
  comment and produced a balanced-but-wrong region; call names inside comments
  and strings minted seams; an option nested one object or array deep was
  attributed to the call. Also `.jsx` was discovered and then silently dropped.
- **#590 mutation report.** `clampBody` truncates from the front and `runLogTail`
  was last, so the D repair disabled the B repair for exactly the population B is
  about. A dead assertion, a hardcoded `PATH`, undrivable `error.status` arms, and
  a discarding `paginate` stub.
- **#609 claims floor.** A second prepare over an outstanding marker made every
  prepared branch decline, the phase fell back to the legacy marker-free lane, and
  that lane never validates a claims review. `--claims-review-artifact` outside
  the claims lane was accepted and ignored.
- **Planner.** Named critique candidates the publish gate then refuses — untracked
  files, and stubs below the residual floor.

## Round 2

Three bounded reviewers reading the repaired surfaces. Boundary window
`2026-08-13-handoff-r2`, verified `clean` with no parent declarations before any
fold. Round 2 found a defect inside a round-1 repair on every one of the three
surfaces, which is the count this rule exists on.

- The round-1 regex fold reopened the exact class the sibling fold closed: `}` in
  the value-position set made a JSX `/>` open a phantom regex whose scan
  terminated inside a later string, after which the walk was inside a string
  literal and minted seams from its contents. Reproduced executably before repair.
- The claims floor was blind in any consumer repo with a non-default adapter
  `output_dir`, through a route the new marker guard is structurally unable to
  see, because it re-asks the question that already returned "no file here".
- The narrative byte floor read the whole file, so appending one line to a
  previous release's narrative bought an accepted `pass`.
- The `**os.environ` fold re-armed the two harness control keys the rejection fold
  had introduced, so the propagate test could throw at the wrong stub with both
  assertions still holding.
- The F9 de-duplication was half-applied: the copy list it claimed to unify was
  still restated in the same module.

## Counterweight Pass

- The fixture floor's `file_backed` counter establishes "a digest matched bytes
  checked in under the fixture directory", not "a captured tool stream". A
  reviewed zero-byte capture counts. Refusing that would refuse honest evidence,
  so the wording was narrowed to what is actually established rather than the
  floor being tightened further.
- `_js_option_value` reports an assembled options object (`Object.assign`, spread,
  parenthesized) as `absent` rather than `unknown`. This over-reports settlement
  risk, which is the acceptable direction for this inventory; recorded rather than
  changed late in a two-round cap.
- The claims-review residual is stated at its real size: deleting the marker line
  and amending skips the floor entirely, which is far cheaper than forging a
  record. The floor raises the cost of a careless publication and gives a
  spawn-blocked host an honest alternative; it does not defeat a deliberate bypass.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: R1 fixture reviewer | action: fix | note: the corpus floor counted a constant-vs-constant digest check as a comparison; split into `checked` and `file_backed` and keyed the floor on the latter.
- F2 | bin: act-before-ship | evidence: strong | ref: R1 quality reviewer | action: fix | note: regex literals, call names in comments/strings, and one-container-deep options all produced fabricated `present`/`finite` verdicts.
- F3 | bin: act-before-ship | evidence: strong | ref: R1 mutation reviewer | action: fix | note: front-truncating `clampBody` discarded the run-log tail the B repair exists to attach; diagnostics now precede the summary.
- F4 | bin: act-before-ship | evidence: strong | ref: R1 release reviewer | action: fix | note: a second prepare over an outstanding marker published through a lane that never validates a claims review.
- F5 | bin: act-before-ship | evidence: strong | ref: R1 release reviewer | action: fix | note: `--claims-review-artifact` outside the claims lane was accepted and never opened.
- F6 | bin: act-before-ship | evidence: strong | ref: R2 quality reviewer | action: fix | note: the round-1 regex fold reopened the string-fabrication class; `}` removed from value position, keyword-aware regex detection added, and a newline bail bounds any mis-parse to one line. Accepted-unreviewed under the two-round cap.
- F7 | bin: act-before-ship | evidence: strong | ref: R2 release reviewer | action: fix | note: a non-default adapter `output_dir` made every marker lookup miss; refused loudly, with the proper threading tracked as an issue. Accepted-unreviewed.
- F8 | bin: act-before-ship | evidence: strong | ref: R2 release reviewer | action: fix | note: the narrative floor read the whole file, so an appended line on an earlier narrative bought a `pass`; the narrative must now be ADDED by the evidence commit. Accepted-unreviewed.
- F9 | bin: act-before-ship | evidence: strong | ref: R2 release reviewer | action: fix | note: `resume_publish`'s reconstructed-state fallback could publish a claims phase with the floor unrun; refused. Accepted-unreviewed.
- F10 | bin: act-before-ship | evidence: strong | ref: R2 mutation reviewer | action: fix | note: environment inheritance re-armed the harness control keys, and the workload-budget test still restated the copy list. Accepted-unreviewed.
- F11 | bin: bundle-anyway | evidence: strong | ref: R2 quality reviewer | action: document | note: the fixture floor's wording now says "bytes checked in under the fixture directory" rather than "a captured stream", which is the claim actually established.
- F12 | bin: bundle-anyway | evidence: strong | ref: R2 release reviewer | action: document | note: the claims-review non-claim now states the marker-deletion bypass, which is an order of magnitude cheaper than forging a record.
- F13 | bin: bundle-anyway | evidence: moderate | ref: R2 quality reviewer | action: document | note: `nested_cli_files` reads raw text and is deliberately wider than the seam scanner; the two counts are not reconciled and the docstring now says so.
- F14 | bin: valid-but-defer | evidence: moderate | ref: R1/R2 release reviewers | action: defer | note: the claims verdict does not reach the published release record ([#610](https://github.com/corca-ai/charness/issues/610)); the claims resume lane never runs the notes-file preflight ([#611](https://github.com/corca-ai/charness/issues/611)); the record path needs threading through the claims module ([#613](https://github.com/corca-ai/charness/issues/613)).
- F15 | bin: valid-but-defer | evidence: moderate | ref: R2 quality reviewer | action: defer | note: assembled/spread options report `absent` rather than `unknown`, and a `slice(0, 60000)` can split a surrogate pair. Both err toward over-reporting or a narrow input class.

## Reviewer Tier Evidence

Fresh-eye satisfaction: parent-delegated

- Requested tier: bounded fresh-eye reviewer (`bounded-reviewer`).
- Requested spawn fields: read-only one-shot task, unnamed, `bounded-reviewer` agent
  type with a Read/Grep/Glob envelope, inheriting the session model and effort.
- Rounds: two, three reviewers each, one per surface family.
- Boundary proof: `reviewer_boundary_fingerprint.py` snapshot/verify around each
  window. `2026-08-13-handoff-r1` and `2026-08-13-handoff-r2` both verified
  `clean` with empty `parent_declared`, each run before the first parent write.
- Host exposure state: requested_fields_sent
- Delivery state: findings-received
- Application state: the host reports no per-subagent confirmation of the model or
  effort it applied, so the requested fields are recorded as sent, not as
  confirmed-applied. What IS confirmed: all six spawns returned substantive
  findings, and both boundary windows verified clean. Round-1 repairs were read by
  round 2. Round-2 repairs are
  recorded as accepted-unreviewed under the two-round cap. No round-2 finding was
  itself a blocker in NEW verdict logic introduced by a round-2 repair, so no
  third round was escalated.

## Boundary Ownership

- Producer: the four proof surfaces themselves — the fixture checker, the JS
  settlement scanner, the mutation-report script body, and the claims-review
  validator — each of which produces a verdict other code and readers act on.
- Consumer: the quality runner and its inventory readers; every consuming repo
  that installs the mutation workflow template; the release publish/resume lane
  and the operator reading its refusal.
- Owning surface: each repair landed on the producer of the verdict it changes,
  not on a downstream reader.
- Verdict: owned-correctly

Five surfaces were touched and each repair landed on the surface that OWNS the
verdict, not on a downstream reader:

- the fixture corpus floor lives in the checker that counts comparisons, not in
  the quality runner that queues it;
- the JS settlement classification lives in the scanner, split into
  `js_settlement_scan_lib` when it outgrew its host module's discipline;
- the mutation-report body repair landed in all three checked-in workflow copies,
  including the two shipped consumer templates, because the reader is every
  consuming install and not just this repo;
- the claims-review record shape and the `output_dir` precondition both moved INTO
  `publish_release_claims_review`, which owns the record path — the precondition
  was initially written at its call site and relocated to its owner;
- the evidence-commit shape rule was given one owner
  (`claims_record_in_change_set`) after the planner and the resume classifier were
  found deciding it independently.

Three producer/consumer questions could not be resolved inside these surfaces and
were escalated to issues rather than half-implemented: #610, #611, #613.

## New Proof-Surface Disposition

`skills/public/quality/scripts/js_settlement_scan_lib.py` is a new file in a
proof-surface family. It DOES render a verdict about other code — it classifies
whether a JS/TS subprocess call site declares a deadline and whether its output is
bounded — so it is a proof surface, and it was read by a bounded reviewer in both
rounds against the birth-advisory classes.

Fresh-eye pass: skills/public/quality/scripts/js_settlement_scan_lib.py — round 1
found three fabricated-confidence paths (regex literal producing a balanced-but-wrong
region, call names in comments and strings minting seams, an option nested one
container deep attributed to the call); round 2, reading the repairs, found that the
regex fold had reopened the string-fabrication class through JSX `/>` and through a
regex after a keyword, plus a missing newline bail that turned any local mis-parse
into a file-wide desync. All were reproduced executably by the parent and repaired;
the round-2 repairs are accepted-unreviewed under the two-round cap. Class-by-class:
(a) an unbalanced or unreadable region returns `unknown`, not a pass; (b) the deadline
verdict discriminates literal, expression, zero, and absent; (c) the unbalanced
backstop is not suppressed by the normal case, but round 2 established it does not
fire for a mis-parse that happens to balance, which is why the walker itself was
repaired rather than the backstop widened; (d) there is no silent skip — a file the
scanner cannot read contributes no seam and the sibling `nested_cli_files` count
stays wider, which is now documented; (e) the plugin mirror is regenerated and
verified in sync; (f) no ratio; (g) fenced and quoted text is now excluded from
call-site detection, which was round 1's finding; (h) no self-declared field gates
its own floors.

## Non-Claims

- No issue in the cohort is claimed closed by this critique. #597, #607, #590, and
  #609 hold local proof only; their tracker disposition is separate work.
- No push, release, or publication occurred.
- The claims-review floor is not claimed to prove a distinct observer existed;
  see the non-claim in `skills/public/release/references/critique-boundary.md`.
- The JS settlement scanner produces zero seams in this repository today, because
  every JS/TS test file lives under an ignored directory. Its repairs are
  fixture-proven and consumer-facing, not proven against this repo's own tree.
- Both reviewers in round 2 traced their findings by reading; the three JS
  fabrication traces were then reproduced executably by the parent before repair,
  and the release `output_dir` finding is pinned by a new end-to-end test.
