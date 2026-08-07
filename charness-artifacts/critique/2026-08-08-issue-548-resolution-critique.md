# Issue #548 resolution critique (delegated)

Classification: bug
Reviewer: delegated bounded reviewer (fresh-eye, read-only envelope: Read/Grep/Glob)
Fresh-eye context: `parent-delegated`
Envelope: bound as expected — no Bash, Edit, Write, or Agent tool exposed to this spawn
Verdict: RESOLVED WITH RESIDUAL RISK — F1 blocked the close as drafted, because the
`prevention` claim asserted a reach the guard did not have -> predicate widened, records
restated, then closed

## Boundary Ownership

- Producer of the pointer verdict: `scripts/scaffold_artifact_lib.py` — `current_pointer_state`
  is the sole `readlink` resolution of a `latest.md` pointer among the `write_artifact_path`
  producers, with `published_pointer_state`, `current_pointer_write_path`, and
  `write_target_facts` layered on it.
- Consumers, all routing through it: `scripts/resolve_artifact_path.py`,
  `skills/public/quality/scripts/resolve_quality_artifact.py`,
  `skills/public/quality/scripts/scaffold_quality_artifact.py`,
  `skills/public/debug/scripts/scaffold_debug_artifact.py`,
  `skills/public/debug/scripts/plan_debug_run.py`,
  `scripts/inventory_current_pointer_layouts.py`, the critique/retro/ideation scaffolds via
  `dated_record_payload`, and `skills/public/handoff/scripts/scaffold_handoff_artifact.py`.
  No remaining private `readlink`/`realpath` pointer resolution inside that set.
- One consumer holds a NARROWER competing fact, disclosed and live: `plan_debug_run.py`
  computes `write_exists` with `.is_file()` and publishes it beside the owner's
  `write_artifact_target_exists` (`.exists()`). The owner's comment says this is deliberate;
  the two disagree when the target is a directory. Two answers to "is something there" in one
  payload is the shape #548 is about, now under two key names.
- Adjacent, NOT in this repair: `skills/public/gather/scripts/gather_writer_lib.py` resolves a
  current pointer with `os.readlink` and, by its own docstring, mirrors the safety contract in
  `scripts/refresh_current_pointer.py` — a second implementation of the pointer-WRITER rule.
  `gather` also answers "target exists" with a third policy (REFUSE), against debug's append
  and quality's prohibition. Different contract, different owner; belongs in an issue.
- Verdict: moved-to-owner — five private copies were moved into the producer that owns the
  rule, every remaining `write_artifact_path` producer delegates, and the repair is in the
  right place. The residual is not a second owner of this rule; it is that the check claiming
  to keep it that way did not enumerate all of its subjects (F1), and that the adjacent
  pointer-WRITER rule still has two owners.

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only fresh-eye, `.claude/agents/bounded-reviewer.md`)
- Requested spawn fields: agent_type=bounded-reviewer, model=inherited, one-shot spawn with no
  host addressing/team name
- Host exposure state: requested_fields_sent
- Delivery state: findings-received
- Application state: applied as requested; envelope Read/Grep/Glob only and structurally
  unable to write or run `git`. Worktree+index integrity fingerprinted around this window with
  `skills/shared/scripts/reviewer_boundary_fingerprint.py` (window
  `issue548-resolution-critique`, verdict `clean`, no drift), as around both slice rounds
  (`slice2-548-round1` clean; `slice2-548-round2` parent-attributed, no unattributed drift).

## Fresh-Eye Satisfaction

parent-delegated — a separate bounded-reviewer context read the committed tree with no access
to the parent's reasoning or to the two prior slice rounds' conversation. F1 was reached by
evaluating the guard's own predicate against an independent repo-wide grep and comparing the
result to a producer set the reviewer enumerated itself, not by checking the parent's list.
F3, F4, F5 and F7 are contradictions between checked-in texts, or between a check and the code
it guards. This is not a same-agent pass.

## JTBD

An agent that has just run a quality or debug scaffold needs to know whether the path it was
handed is safe to write. Before #548 the payload said only WHERE, and
`write_artifact_role: current_pointer_target` reads as neutral while naming, for `quality`, a
finished dated review whose destruction leaves no trace, because the filename is dated. `#538`
is the recorded near-miss, with `quality/SKILL.md` step 8 pointing at exactly that path.

## Findings

### F1 (BLOCKER as drafted) — "every producer that names a write target" was false, and it missed the two scaffolds the issue is about

The sweep selected producers by `'"write_artifact_path":'` or
`write_artifact_path=write_artifact_path`. Neither matches
`skills/public/quality/scripts/scaffold_quality_artifact.py`, which returns
`current_pointer_payload(...)` and never spells the key, nor
`skills/public/debug/scripts/scaffold_debug_artifact.py`, which inherits the key and replaces
it through a fixed key list. Those are the two scaffolds of the issue title and the two CLIs
the behavioural verdict runs — so the guard offered as `prevention` did not enumerate the
subjects of the defect. Both were correct in behaviour, so this was unproven-prevention rather
than a wrong verdict, but the recurrence path is concrete: a new producer written in the
delegation style was invisible to both structural tests, and the `>= 8` floor still passed.
The same overclaim was checked into `dup-review.json`.

REPAIRED: the predicate now selects by key literal (including the single-quoted spelling) OR
by delegation call (`current_pointer_payload(`, `dated_record_payload(`,
`with_write_target_facts(`) in a module defining `payload_for`; it scans four roots rather
than two (`skills/support` and `skills/shared` added, because the repo's older sibling gate
records that omitting `skills/shared` once produced a clean report over a scope that excluded
a real violation); it REFUSES on a dynamically assembled key name rather than reporting clean
over a scope it cannot see; and the floor is set at the 11 producers it now finds. The
`dup-review.json` note was restated to what the predicate selects.

### F2 (prevention hole with a live instance) — the planner named a write target in four branches and carried the facts in one

`_artifact_next_action` emitted `write_artifact_path` with neither fact, and backed three of
the four `next_action` branches. Only the `scaffold-debug-artifact` branch carried them — and
that branch is reached when the artifact is absent or resolved, i.e. almost always
`create_new_file`. The `continue-existing-artifact` branch is the one whose target holds
content, and it was the one staying silent. The distribution was inverted against risk.

REPAIRED: all four branches now carry `write_artifact_effect` and
`write_artifact_target_exists`.

### F3 (misstatement in the durable diagnosis, inside the owner) — "implemented twice"

The owner's docstring said the rule "was implemented twice", while the tree's own later
comments say "A FOURTH copy", "a FIFTH implementation", "A SIXTH derivation". The first text a
future session reads when it asks why this module exists recorded the pre-fix world as two
copies when six implementations were found.

REPAIRED: the docstring now names six implementations — the owner plus five private copies —
lists all five sites, and records the attribution (two named by the issue, one by the
duplicate-ratchet gate, two by bounded review).

### F4 (siblings arithmetic) — six implementations, FIVE private copies

The tree's numbering includes the owner, so "six private copies" over-counted by one, and the
attribution 2 + 1 + 3 required three review-found copies where the tree names two. The third
review-found item was a producer BUG (stale facts before the target swap), not a copy of the
rule.

REPAIRED: restated everywhere as six implementations / five private copies removed, with 2/1/2
attribution and the producer bug named separately.

`dup-review.json`'s four `intentional` classifications verify against the tree, and both
new-family notes carry an explicit "not claimed as measured against a prior scan", which is
the right hedge.

### F5 (the fourth-pass prose was unbound) — deleting either SKILL.md sentence left everything green

No test referenced `write_artifact_effect` outside the new test file, and that file read only
Python sources. The existing `test_quality_skill_docs.py` pins step 8's older tokens, none of
the new sentences — including "`create_new_file` there is not a green light", which carries the
whole point of the new key for quality. This was the highest recurrence risk in the slice by
the slice's own evidence: prose rewritten three times, wrong twice, now the sole explanation of
two new keys, with nothing failing if it were trimmed or inverted.

REPAIRED: `test_the_two_skills_still_explain_how_to_read_the_write_target_facts` pins the
anchors that make each explanation correct — the hedge and the safe alternative — without
pretending to judge correctness, which stays a reviewer's job.

Recorded, not repaired: `skills/public/quality/references/bootstrap-escalations.md` is a third
writer of the same guidance, unbound to step 8 or to the payload.

### F6 (prose over-narrow for one reachable value)

Debug's `overwrite_existing_content` sentence claimed the file's "content is the investigation
you are continuing", while the owner computes the value from `.exists()` and its own comment
admits a directory or a symlink-to-existing also satisfies it. The `create_new_file` side got
four enumerated causes plus an explicit non-exhaustive hedge; the destructive side got a single
unhedged interpretation.

REPAIRED: hedged symmetrically.

### F7 (fixture honesty) — the new test's adapters were invalid and passed by coincidence

The fixtures wrote `schema_version: 1` with a nested `data: {output_dir: ...}` and an invented
`artifact_class` (`current_pointer_with_records` / `records_only`, which appear nowhere else in
the repo). The resolvers accept only `current` / `history` / `rolling` and read a TOP-LEVEL
`output_dir`, so every adapter resolved `valid: false` and every producer fell back to inferred
defaults whose `output_dir` happened to equal what the fixture intended. The tests therefore
exercised no adapter-configured output at all, while reading as though they did — the
fixture-supplies-its-own-premise family.

REPAIRED: a `_seed_adapter` helper writes the real schema with `artifact_class: history` (the
class that supports dated records, and the one `debug` itself declares). Correcting it
initially broke two tests, which is the proof the old fixtures were inert.

### F8 (the dependency-free guard missed the most natural second spelling)

It forbade `from scripts.` but not `import scripts.x`, which would break the file-path load the
guard exists to protect.

REPAIRED: `import scripts.` and `spec_from_file_location` added.

### F9/F10 (recurrence attack, and the repo's own better precedent)

Evasions found against the pre-repair sweep: a producer outside the two roots; a dynamically
built key name (the sibling gate `scripts/check_current_pointer_writes.py` records this exact
escape, an `f"latest.{ext}"` slipping a verbatim-filename scan); a single-quoted key; a
delegation-shaped producer (two live instances, F1); a renamed key (`write_path`, live
instance, F2); and a floor one below the current count.

The load-bearing comparison: this repo ALREADY has an AST-based gate over the sibling surface
that derives its population from `git ls-files`, covers four roots including `skills/shared`,
and detects computed names. The lessons it paid for were not carried across. Four of the six
evasions are now closed (roots, single quotes, delegation shape, dynamic-name refusal, floor);
the remaining gap is that this sweep is substring-based rather than AST-based, and the renamed
`write_path` key is covered only by F2's repair rather than structurally.

### Q2 — is the behavioural verdict's channel genuinely distinct? Real, and narrower than it reads

Genuinely different and worth claiming: a separate process, `argparse` CLI entry, a real
filesystem repo, a DETACHED worktree at `58b5a66c` (an execution root distinct from the working
tree), and the assertion made against the CLI's printed stdout, which is the byte channel an
agent actually reads. Since #548 is about what a payload TELLS a reader, exercising the
emitted-bytes path is non-trivial.

What it does NOT establish: both CLIs import the owner, so there is no independent oracle for
the pointer rule or the effect classification. That is structural — consolidation to one owner
and channel independence are in direct tension, and the closeout says so rather than implying
otherwise. What IS independent is the seed: a known finished file at a known dated path, so the
`overwrite_existing_content` verdict is checked against an externally established on-disk fact
rather than against the code's own belief. The verdict does not exercise the debug side through
`plan_debug_run.py`.

### Q6 — reachable values against the prose

Quality (`--intent current`): pointer target, `overwrite_existing_content` for a symlink to an
existing review, `create_new_file` for a dangling symlink or absent `latest.md`.
(`--intent record`): dated path, normally `create_new_file`, `overwrite_existing_content` when
today's review already exists. Step 8 addresses all four, including the dangling case and the
same-day case. Debug: open pointer → existing record, `overwrite_existing_content`; resolved →
fresh followup, `create_new_file` (guaranteed); dangling or absent → `create_new_file`. The
fourth pass is materially better than the earlier ones; one sentence asserted more than its key
carried (F6, repaired) and nothing pinned any of it (F5, repaired).

## Other residuals recorded, not repaired

- `docs/artifact-policy.md` is silent on both new keys — but it never enumerated payload keys
  at all, so this is a long-standing granularity gap rather than drift introduced here.
- `resolve_artifact_path.payload_for` silently falls through to the current-pointer branch for
  `--intent record` when the artifact class is not `history`, while the payload still echoes
  `intent: record`. The new facts mitigate it; the mismatch is #548's family and is unswept.
- The `gather` pointer-writer duplicate and its third target-exists policy.
- `plan_debug_run`'s `.is_file()` vs the owner's `.exists()`, disclosed in the owner's comment.

## Q7 — Verdict

RESOLVED WITH RESIDUAL RISK. F1 blocked the close as drafted; nothing found required a
behaviour change beyond F2's branches.

The issue's real defect is fixed and the fix is well shaped. The premise check that refuted the
issue's debug account before any code was written is the strongest thing in this slice, and it
produced a better remedy than the issue's: `write_target_facts` states the consequence as a
FACT and leaves the policy to each skill, which is right precisely because the two skills
disagree about whether overwriting is correct. Five private copies of the pointer rule are
gone, every remaining producer delegates, the swap-then-stamp bug is fixed at the recompute
rather than by lengthening a key list, and the consolidation's second-order duplication was
classified rather than hidden.

What blocked it was the `prevention` / `siblings` ledger: the floor requires a decision AND
proof, and the proof offered for prevention did not enumerate the two scaffolds the issue
names. Under this repo's rule that the floor is the authorization rather than a checklist, a
claim asserted with proof that the proof does not carry is the authorization failing. The
predicate was widened rather than the claim narrowed — the cheaper and better of the two
options the reviewer offered, because it closes F1 and the F2 class together — the counts were
restated, the fixtures corrected, and the prose pinned. Once the ledger says only what the tree
carries, `#548` is finished.

## Non-claims

No command was executed by this reviewer: the mutation results, `pytest tests/` 7842,
`run-quality.sh` exit 0, the closeout aggregate, the dup-ratchet status, the reviewer-boundary
fingerprints, and the detached-worktree behavioural run are taken as reported and are unproven
by this review, not disputed; the two stdout payloads were not reproduced. `git show` was
unavailable in this envelope, so claims about pre-fix code rest on the committed comments,
which agree with each other. `plugins/**` mirror fidelity is assumed covered by the export-sync
gate. No consumer repo was read. F1, F2, F5, F7, F8 are wrong-by-reading; F3 and the
`dup-review.json` overclaim are contradictions between checked-in texts; F4 is an arithmetic
mismatch against the tree's own numbering.
