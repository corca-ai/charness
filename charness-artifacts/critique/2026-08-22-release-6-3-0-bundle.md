# Release 6.3.0 Candidate Critique — the 2026-08-22 bundle

Date: 2026-08-22

## Decision Under Review

Whether the `f5211700a..HEAD` bundle (9 commits, 57 changed paths) should be
versioned and published as `6.3.0` / `v6.3.0` as a MINOR bump, with the stated
limitations, or whether the bump level or the publication itself should change.

Not the same question the four preceding rounds asked. Those read the code; this
asks whether shipping it, at this level, with these disclosures, is a good idea.

**Name collision, stated first because it is a hazard rather than trivia.** A
`6.3.0` critique corpus already existed on disk from 2026-08-21, reviewing the
**6.2.0 -> 6.3.0** candidate (trigger #670) with verdict `HOLD`. That candidate
was never published — `6.2.1` and `6.2.2` shipped instead — so the version number
was reused. Those files are now bannered as superseded. See F1.

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer (`bounded-reviewer` typed subagent),
  read-only, shared parent worktree, no exec tool.
- Requested spawn fields: `Agent(subagent_type=bounded-reviewer, model=opus)`,
  spawned UNNAMED per this repo's spawn-shape rule, carrying the release critique
  packet (bundle scope, proven state, six questions with the `major`-bump case
  named as the hardest, non-claims, out-of-scope lines).
- Host exposure state: applied
- Application state: host-confirmed: the reviewer ran via the Agent tool, returned
  its findings to this context, and the reviewer boundary snapshot
  `w-20260822T050415Z-1232915` verified `parent-attributed` with no undeclared drift.
- Delivery state: findings-received

The reviewer reported its own envelope as read-only (Read/Grep/Glob only; no
Bash/Edit/Write/Agent), so it could not execute. The two claims it flagged as
needing parent evidence — F1's acceptor result and F3's `VALID_STATUSES` history
— were executed by the parent and their output is quoted verbatim below.

## Verdict

**Publish as `minor`**, after clearing F1, passing `--bump-rationale`, and
writing F2/F3/F4/F5/F7 into the release notes. No finding blocks publication on
its merits; F1 blocks the release RUN until the stale corpus cannot authorize it.

## Bump Level

`minor` is correct under `references/version-policy.md`, and the case against it
was argued rather than assumed.

The `major` triggers are: renamed public skills or package ids; changed
invocation expectations that break existing automation; removed or incompatible
install surfaces; forced migration steps for existing users. The bundle reaches
none.

The strongest `major` argument was that two gates now refuse input they
previously accepted. It does not survive contact with the code:

- **The durability widening is not consumer-facing.** `consumer-validator-catalog.yaml`
  classifies `check_spec_evidence_durability.py` as `consumer_facing: false`, and
  it is wired only from this repo's own `run-quality.sh`. The 2339 newly-scanned
  docs are charness's own history, not a consumer's.
- **The hollow refusal reaches the exit code only under `--pursue-ready`.** The
  default `check_goal` path never consults it, and every non-shaping status is
  skipped, so no existing artifact reddens on update. A draft is refused at the
  moment someone tries to pursue it, the remedy is per-artifact, and the refusal
  names the `N/A — <reason>` escape in its own text. That is the policy's
  "meaningful new behavior that existing users can adopt without migration".

The reporter seam and `superseded` are additive; the cadence change strictly
narrows an existing over-fire, so 6.3.0 refuses FEWER artifacts than 6.2.2.

The bump is nonetheless debatable by any reading, which triggers the policy's
Guardrail — so `--bump-rationale` is mandatory here, not optional. The
immediately preceding release recorded "Bump rationale: NOT recorded by this
helper invocation"; repeating that would be a second consecutive violation of the
repo's own policy, on the release where the argument actually exists.

## Findings

### F1 — BLOCKER (release run, not the bundle): a stale `6.3.0` HOLD critique can authorize this publish

Confirmed by execution, not reasoning. The planner's `critique_acceptor` was run
against the 2026-08-21 artifacts with the real binding tokens for `6.3.0`:

```
tokens: ['6-3-0', '6.3.0']
ACCEPTED=True   charness-artifacts/critique/2026-08-21-release-6-3-0.md
ACCEPTED=True   charness-artifacts/critique/2026-08-21-release-6.3.0-packet.md
```

So a publish run that let the planner auto-fill `--critique-artifact` would have
been authorized by a document whose verdict is `HOLD`, about a candidate that no
longer exists — and an outside auditor asking "was 6.3.0 reviewed?" would find it.

Disposition, and the first attempt at it was WRONG in an instructive way. I began
by writing a superseding banner into both stale artifacts. That edit pulled them
into the critique validator's changed scope, where the 2026-08-21 record failed
its own binding-currency check with "declared reviewed inputs are stale" — which
is TRUE, and is the validator correctly refusing an edited frozen record whose
reviewed inputs have moved underneath it. Annotating a frozen critique is still
editing it. Both banners were reverted; the artifacts are byte-unchanged.

What actually holds the line here:

1. This release passes `--critique-artifact` EXPLICITLY, so no auto-fill occurs.
   That is the only mechanism that changes what authorizes this publish.
2. The hazard is recorded HERE, in the artifact an auditor reaches from the
   release record, rather than in the stale file where recording it broke a gate.
3. The structural problem — an acceptor that binds on version tokens, against a
   corpus where version numbers get REUSED whenever a candidate is abandoned — is
   filed as **#699**. A banner would have fixed one instance; the next abandoned
   candidate reopens it.

Explicitly NOT claimed: the stale artifacts still satisfy the acceptor. Running
it against them today still returns True, and nothing in this bundle changes
that.

### F2 — Disclosure: all three headline capabilities are undocumented on shipped operator surfaces

`node-test` appears only in code and tests; `mutation-testing.md`, the shipped
doctrine for this harness, never mentions the `reporter` plan key — and that is
the capability whose stated purpose is to unfork three Node consumers. `SKILL.md`
still enumerates a now-incomplete list of what makes `--pursue-ready` fail.
`superseded` is documented in `goal-artifact.md` but absent from
`lifecycle-after.md`, which is exactly where the phase brief routes an operator
holding one.

Mitigations credited: the `--plan` argparse help documents the reporter key, and
the runtime refusal names both the fix and the `--test-reporter=tap` requirement.
Folded into the release notes; the `tap`-vs-`spec` requirement in particular
bites interactively and not in CI, and appears in no doc.

### F3 — Disclosure: adopting `superseded` makes a downgrade lossy

A goal marked `superseded` under 6.3.0 is an INVALID status under 6.2.2 and
reddens `check_goal_artifact` after a downgrade. Parent-verified:
`git show f5211700a:...goal_artifact_lib.py` reads
`VALID_STATUSES = ("draft", "active", "blocked", "complete")`. One-way door the
moment a consumer uses the feature. Into the notes beside the feature.

### F4 — Disclosure, and the stated limitation UNDERSTATES it: #697's mitigation adds a third non-blocking skip

The limitation was written as a naming collision. What ships is a new guard that
returns "changed-line teeth skipped (non-blocking)" on finding a context-bearing
corpus, joining two pre-existing skips. In any session where the sampler ran
first, the changed-line proof now stands down rather than rendering a verdict.
The code is honest about it and publishes a resume command, and the direction is
safe — but the disclosure must say "a third route by which a proof surface
renders no verdict", not "a path collision". Reworded in the notes.

### F5 — Disclosure: `superseded` is materially cheaper than `complete`

It skips roughly fourteen closeout floors including the Auto-Retro disposition
gate, and `Superseded by: none — <reason>` is accepted by design. The design
argument holds — the alternative is a goal claiming a `complete` it never earned
— but the incentive is one line away and the notes must say so plainly. Tracked
as #698.

### F6 — FIXED IN THIS BUNDLE, not disclosed: the successor-pointer check ran at the validator but neither write

`refuse_flip_reason` and the create arm both called `check_superseded_record`
without `repo_root`, so the existence check — which this module calls the entire
cost of the status — reached only the validator. A pointer at a file nobody wrote
succeeded at the write and failed one cycle later, which is the window the write
guard's own docstring says it exists to close. Round 2 caught the sibling form
(both guards inside `if path.exists()`); this residual survived it. `repo_root`
is now threaded through both, verified: the flip is refused.

### F7 — Disclosure, needs a decision before the notes: there is no rollback path

`charness update` has no version, ref, or tag selector. The only mechanism is
manual — pin the managed checkout to `v6.2.2` and run `--no-pull` — and no doc
describes a downgrade procedure, while the install-refresh and adapter contracts
both push "rollback advice" into the release notes.

Decision taken: the notes say **remediate, do not roll back**, and say why. The
hollow refusal is per-artifact and fixable in place; the durability widening is
not consumer-run; the reporter and `superseded` are opt-in; and per F3 a
downgrade after adopting `superseded` is lossy. Claiming a clean downgrade exists
would be the false half.

### F8 — Staleness the release run will surface anyway

`docs/handoff.md` still describes the 6.2.2 unit, and this goal artifact still
carries `TODO`s in `## Final Verification` / `## Auto-Retro` with slices listed
`pending`. Expected mid-run; slice R's closeout floor needs both.

## Boundary Ownership

- Producer: the achieve and quality skill packages (goal-artifact floors, the
  mutation harness, the changed-line gate) plus their checked-in plugin export.
- Consumer: operators and agents invoking `/goal`, `mutate_and_restore.py`, and
  the changed-line lane; downstream repos consuming the exported plugin.
- Owning surface: `skills/public/achieve/**` and `skills/public/quality/**` for
  the shipped rules; `scripts/**` for the repo-internal gates.
- Verdict: owned-correctly

Every rule this bundle added landed with the surface that already owns it, and
the two attempts to do otherwise were caught and reversed rather than shipped:

- Reading a runner's counts is now owned by `mutation_test_reporters`, while
  killed/survived/refused classification stays in `mutate_and_restore`. The
  producer/consumer line is the COUNTS, not the verdict, which is why a third
  reporter can be added without touching the harness contract.
- The H2 section walk went to `goal_artifact_markdown.section_bounds`, the
  declared single owner, after a first cut hand-rolled an eighth copy and the
  duplicate ratchet refused it.
- The grandfathering-date rule initially delegated to
  `critique_enforcement_scope.observed_date`, the repo's one owner — and round 2
  showed that owner's corroboration argument inverts on this corpus, so the
  durability gate now reads the filename channel only and says why. That is a
  deliberate NARROWING away from the shared owner, recorded rather than silent.
- The scaffold template has one reader (`goal_artifact_lib._TEMPLATE`); a second
  lazy reader was written and deleted.

No rule was left in two places, and no consumer surface took ownership of a rule
its producer should hold.

## Over-Worry Raised And Not Folded

The reviewer considered and rejected the `major` bump on the durability gate,
having checked its consumer classification rather than assuming it. Recorded
because the assumption in the packet was WRONG and the correction came from the
reviewer, not from me: I had told it the gate was consumer-facing, citing the
catalog entry without reading the `consumer_facing: false` field beside it.

## Non-Claims

- No Cautilus evaluation was run; it is an explicit Non-Goal of the owning goal.
- The reviewer could not execute anything. F1's acceptor result and F3's
  `VALID_STATUSES` history were executed by the parent and are quoted above; the
  rest of its findings are reasoned from the tree it read.
- This critique authorizes a publish decision. It does not certify code
  correctness, which the four preceding bounded rounds addressed separately, nor
  does it certify that the notes derived later match the tree — the publish
  preflight re-derives them.
