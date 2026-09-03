# Impl debug route and waste classes critique

Date: 2026-09-04

## Decision Under Review

Two prompt-affecting additions to `skills/public/impl/SKILL.md`: a debug entry
rule in `## Verify` (the same failure returning after a fix aimed at it, or a
result contradicting the contract, is routed on whether a falsifiable cause can
be stated; if not, `impl` stops patching and enters `debug`), and a six-signal
waste scan in `## Change` with a defined seam and a follow-up stopping rule.
`debug/SKILL.md` is unchanged: its Pattern Ladder already owns "pattern of
patterns". The README rewrite in the same release is a truth-surface change
reviewed separately by a bounded read-only reviewer.

## Verification Scope Decision

- Claim under test: an agent reading `impl` once will route a repeated
  unexplained failure to `debug` instead of a second guess, and will read its
  diff against the six signals before closing, without the rule firing on
  ordinary compile/test loops.
- Changed surfaces: `skills/public/impl/SKILL.md`; final consumers are the
  installed `impl` skill in Claude Code and Codex and the generated
  `plugins/charness` mirror.
- Minimum sufficient proof: `validate_skill_ergonomics.py`,
  `check_skill_surface_preflight.py --changed-skill-md` (core headroom 65/160,
  not regressed), `check-docs.sh`, and three file-backed fresh-eye reviews.
- Deliberately omitted checks: no behavioral evaluator; per
  `docs/public-skill-validation.md` a prompt-affecting diff alone does not
  justify one, and the scenario review is the three reviews recorded here.
- Verifier contract: `scripts/review/validate_critique_artifacts.py`,
  unchanged in this slice.
- Failure classification: none
- Negative control: none with rationale: the reviewers' `block` verdicts on the first draft are the evidence that the review channel discriminates; no refusal path is claimed.
- Subject identity: sha256:cb076af724e11db86e573c174976f715268c207358b86cf966ebedc93ecace0c
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:c173dd153b9b410283a5c2d6afc77790f656da74bb292fce9fd92420431ed2ee
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:688d992c299b9635b91f89a82f991c5ebd7d04fdcc5c319ec52165a507db64f7

## Failure Angles

- Trigger noise: a debug route that fires on every unpredicted command result
  becomes background text the reader learns to ignore, and debug's bootstrap
  (adapter, planner, scaffold, validator) is disproportionate for a reversible
  contract correction (north star P1).
- Recall: one long bullet with seven packed concerns and no retrieval cue is
  not read at the moment it matters (P2), and a self-justifying clause in the
  body argues against P3 inside the contract it is meant to serve.
- Ownership: the waste scan could duplicate `quality` or the north star's
  purpose section, and "fix the class" could widen every slice against
  "smallest coherent change".
- Loophole: a seam defined for code only leaves config, test, and artifact
  slices with no seam and no stopping rule.

## Counterweight Pass

- Real blockers, fixed before ship: the trigger width and the missing
  observable (now: same failure after a fix aimed at it, or a contradicted
  contract claim; test is a cause that predicts a disproving observation; a
  narrower new failure is excluded); the paragraph shape (now one-line
  principle, six-item sub-list, seam, stopping rule); the code-only seam (now
  every edited surface with consumers, readers, and generated derivatives).
- Bundled: "classes" became "signals; they overlap, and every match is
  repaired"; the self-justifying clause was removed from the body.
- Over-worry: "the enumeration duplicates quality and reverses P3". Quality is
  an on-demand inspection; impl is the moment of change. The operator's
  observed evidence is that the principle alone did not produce recall, which
  is the P3 exception the north star names. Recorded, not folded.
- Valid but deferred: debug has no narrow fast path that skips its bootstrap
  for a small reversible incident. That is a `debug` change, not this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/impl/SKILL.md#Verify | action: fix | note: trigger fired on any unpredicted result and did not separate a recurring unexplained failure from a narrowed new one; repaired with the falsifiable-cause test and the narrower-failure exclusion (reviewers 1 and 2; reviewer 3 confirms resolved).
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/impl/SKILL.md#Change | action: fix | note: seven concerns in one bullet with no retrieval cue and a clause arguing against north-star P3 in the body; repaired to a principle plus six-item sub-list (reviewers 1 and 2; reviewer 3 confirms resolved).
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/impl/SKILL.md#Change | action: fix | note: "what the slice touches" undefined, then defined for code only while impl also edits config, tests, and artifacts; repaired to every edited surface with its consumers, readers, and generated derivatives (reviewer 1; reviewer 3 narrowed it; fixed after).
- F4 | bin: bundle-anyway | evidence: moderate | ref: skills/public/impl/SKILL.md#Change | action: fix | note: the six entries overlap while the text called them classes; now named as overlapping signals with every match repaired (reviewer 3).
- F5 | bin: bundle-anyway | evidence: moderate | ref: skills/public/impl/SKILL.md#Verify | action: fix | note: "falsifiable" needed its observable; now "one that predicts an observation able to disprove it" (reviewer 3).
- F6 | bin: over-worry | evidence: contested | ref: skills/public/quality/SKILL.md | action: document | note: the waste scan duplicates quality and reverses P3; quality inspects on demand while impl is the moment of change, and the operator's observed non-recall is the P3 exception. Recorded here, not folded (reviewer 1).
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/debug/SKILL.md#Bootstrap | action: defer | note: debug offers no narrow fast path around its bootstrap for a small reversible incident; a debug-skill slice, outside this change (reviewer 1).

## Task-Run Code Critique (#790, #791)

One file-backed reviewer (attempt `task-run-790-791-code-1`, packet
`charness-artifacts/critique/task-run-790-791-code-1-packet.json`, SHA256
`75c24e38251fdaeb43001dba91ddf435955169b6db1cbbe0f9bc4736d7a24f51`, identity
`d5d33a1987362b178a096e70e4e2eab270926912603c3cb7a41b3c9dbb131cd1`) read
commit `793758b6a` under a correctness and seam-ownership lens and delivered
`block` with four findings, all acted on in the following commit:

- T1 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_runtime.py | action: fix | note: pid-only liveness cannot support the `consistent` store diagnosis (pid reuse; a live runner on a terminal record during retention); the projection is now `runner_pid` and `alive`, documented as advisory.
- T2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_scope.py | action: fix | note: brace expansion in `normalize_scopes` stole a literal path with braces in its name; expansion now follows the existing literal-precedence check in `resolve_scope_specs`, and each alternative records `expanded_from`.
- T3 | bin: bundle-anyway | evidence: strong | ref: scripts/task_run/task_run.py | action: fix | note: `timings_ms.prepare` measured creation, readiness, and prepare together; renamed `create` and documented as such.
- T4 | bin: bundle-anyway | evidence: moderate | ref: docs/agent-task-runs.md | action: document | note: the additive `liveness` key changes the `task status` response shape; kept additive and documented as a read-time projection beside the persisted fields rather than restructuring the response.

A repair-verification reviewer (attempt `task-run-790-791-repair-verify-1`)
read the repaired commit `286a2a745` and delivered `pass`,
`approval_eligible: true`: T1–T4 resolved, and four introduced-risk probes
verified (expanded glob specs refresh independently at completion; a
brace-bearing declaration that is itself a literal is emitted once; the
extracted helpers move no timestamp across a lifecycle boundary; the tests
make no wall-clock call). Its packet is named under Reviewed Input Identity.

## Reviewer Tier Evidence

- Requested tier: n/a (run_review.py default; adapter `reviewer_runner` is `file-backed-worker`, backend `codex_exec`, boundary `read-only-worker`).
- Requested spawn fields: file-backed Codex worker through `run_review.py`; no host subagent spawn.
- Host exposure state: host-defaulted
- Application state: unverified-by-packet; the packet records the request, not the model the host chose.
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: .charness/reviewer-round-impl-debug-route-final-1/worker-report.yaml
- Earlier rounds: `.charness/reviewer-round-impl-debug-route-weinberg-1/`, `-raskin-2/`, `-repair-verify-1/` (run state, not tracked).
- Worker report identity: 2c5bcb8e647bf00259494b1306893d1202c90e713cda2c21bb52753778375818
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: b3d8083fb9433fd5c41f02a127335ebec28db0837367e2dba9efe9687bc62bc1
- Worker report input identity: c173dd153b9b410283a5c2d6afc77790f656da74bb292fce9fd92420431ed2ee
- Worker report parent receipt identity: parent-7e5ed93e44da821706046c28b2c0dec8bb471e9972a21e79
- Worker report findings identity: 7f3e5f4c16dc19b510e14b9e4c69c92c29f7cec6e905d63aa0f386422227fd7b

## Fresh-Eye Satisfaction

worker-delivered; four file-backed Codex workers ran through `run_review.py`. Reviewers 1 and 2 (Weinberg/Ousterhout ownership, Raskin first-reader) delivered `block` on the first draft; reviewer 3 (repair verification) delivered `block` with three wording gaps; reviewer 4 (final bytes) delivered `pass`, `approval_eligible: true`, on the exact subject identity above. No same-context substitute was used.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/impl-debug-route-final-1-packet.json
- Packet path: charness-artifacts/critique/impl-debug-route-final-1-packet.json
- Packet SHA256: b3d8083fb9433fd5c41f02a127335ebec28db0837367e2dba9efe9687bc62bc1
- Identity SHA256: c173dd153b9b410283a5c2d6afc77790f656da74bb292fce9fd92420431ed2ee
- Reviewer 3 packet: charness-artifacts/critique/impl-debug-route-repair-verify-1-packet.json, SHA256 659fc911267111bf17bfa4cc6da76354efa6bc56e597cadf990a08d15283450e, identity 7ae92ecbdae1723ebff33dcfba92f5db4fb8cecb847fe20b8fd4efa827e558df, verdict block, three wording gaps.
- Reviewer 1 packet: charness-artifacts/critique/impl-debug-route-weinberg-1-packet.json, SHA256 4bca88c074ec041de97af5b0acf73faaae98066757e87181720f1935996b45a7, identity 028c40b32436808e24e97b113cd46c73fa5d36b08fdc07b26b2bded0c5844b72, verdict block, three findings.
- Reviewer 2 packet: charness-artifacts/critique/impl-debug-route-raskin-2-packet.json, SHA256 04d6fc96016090314c1886068333c396b06043554d7dc14525c9d494448d7eee, identity 15b1eb5dd241267cb72388feee43ab09a3ce06dcb722157409d8420a70114759, verdict block, three findings.
- Reviewer 4 read the final tree; the subject identity above is that tree.
- Task-run code critique packet: charness-artifacts/critique/task-run-790-791-code-1-packet.json, SHA256 75c24e38251fdaeb43001dba91ddf435955169b6db1cbbe0f9bc4736d7a24f51, identity d5d33a1987362b178a096e70e4e2eab270926912603c3cb7a41b3c9dbb131cd1, verdict block, four findings (commit 793758b6a).
- Task-run repair-verification packet: charness-artifacts/critique/task-run-790-791-repair-verify-1-packet.json, SHA256 23b8998eef52f1222274c26cc809ec7768fca07a55b4bc52d4e9ccda0949ee7b, identity 5ade27d84510d40a597d39626f7ad289dd21e1c35b19626da51e04db56599beb, verdict pass, approval-eligible (commit 286a2a745).

## Release Scope

Version: `8.2.0`. Tag: `v8.2.0`. Previous: `8.1.0`.

Change: minor. What changes for a consumer: the installed `impl` skill routes a
repeated unexplained failure into `debug` instead of a second guess, and reads
its diff against six waste signals before closing; the README is rewritten as
the user guide with the install-effects list corrected against `init.sh` and
the CLI; and `charness task run` accepts `{a,b}` groups in `--scope`, names
out-of-scope paths at `candidate.disallowed_paths`, and writes `runner_pid`,
UTC `timestamps`, `timings_ms`, and `codex.timeout_scope` into every record,
while `task status` adds a read-time `liveness` projection (#790, #791). The
receipt fields and scope syntax are additive maintained behaviour adopted
without migration, which is the minor shape in `version-policy.md`; no public
skill, CLI subcommand, adapter key, or install surface gained or lost a
member. The README review was two bounded read-only reviewers, separate from
the four workers above; their install-list findings are the corrections in
commit `b528a0add`. The task-run change has its own code critique below.

## Boundary Ownership

- Producer: `skills/public/impl/SKILL.md` states the debug entry rule and the waste signals.
- Consumer: the agent executing an implementation slice; `debug` receives the handoff and already hands back to `impl`.
- Owning surface: public skill `impl` (repair discipline itself stays owned by `debug`).
- Verdict: owned-correctly
