# Next session: is this code and test actually non-duplicated and high-value?

Status: pickup prompt, not closeout evidence. Do not commit conclusions from it
without measurement. Written 2026-08-31 at `3240ffcc1`.

Paste the **Prompt** section below to open the session. Everything above and
below it is context for whoever is deciding whether to run it.

---

## Prompt

Audit whether this repo's tests and the code they guard are actually
non-duplicated and worth their cost. Do not start from the Git/subprocess
census — that campaign is largely spent and the last session proved the count is
a poor proxy for value.

Read `charness-artifacts/retro/2026-08-31-session-retro.md` first, then
`charness-artifacts/impl/2026-08-31-git-subprocess-friction-session-note.md`
for what is already decided and rejected.

**The question.** For a bounded surface you and I agree on, answer three things
per test, with evidence, defaulting to KEEP when uncertain:

1. Does it catch something no other test catches?
2. Is it *reachable* — collected, dispatched, and actually asserting?
3. Is the production code it guards itself duplicated, so that two tests are
   pinning two copies of one contract?

Question 3 is the one this repo has never asked. Every audit so far has looked
at tests; nobody has asked whether the code under them is duplicated.

**Rulers, in the order they earned trust last session:**

- *Mutation attribution* is the only ruler that answers question 1. Not a
  mutation SCORE — per-mutant killer attribution: for each mutant, which tests
  fail. A test that is never the sole killer of any mutant is a deletion
  CANDIDATE; a test that is a sole killer is proven irreplaceable, which is the
  more useful half. A working harness exists at
  `/tmp/mutation_value/run_mutation_value.py` (snapshot copy, per-mutant scratch
  dir, baseline failures subtracted). It is in `/tmp` and will be gone — rebuild
  or make it repo-owned. It ran 213 mutants over two modules against 70 tests in
  about 12 minutes at 3 jobs.
- *Reachability* answers question 2 and is nearly free. Last session shipped five
  `_case_*` dispatch families and one of them had five helpers with no caller and
  eleven unreachable assertions — the count-based check passed it. Run the scan
  first; it is minutes and it found a real defect.
- *Adversarially-verified code review* beat every cheap syntactic metric. Fresh-eye
  reviewers with materially different lenses, each finding independently checked
  before it is believed. Three of five findings in the last critique were correct
  in mechanism but wrong about impact, and only the verification pass separated
  them.

**Do not repeat these mistakes, all made last session:**

- Do not publish a derived metric before running one hostile pass on its
  assumptions. Ask "what would have to be true for this answer to change between
  the two calls?" and test that. A metric was walked back 339 → 134 → ~35 for
  want of five minutes of this.
- Do not verify a change with an instrument that shares its blind spot. An
  assertion COUNT cannot see reachability. Any "nothing was lost" claim needs a
  negative control: break the restored assertion and confirm it fails.
- Do not spend a subagent before the target survives its own check. Two were
  commissioned on a dissolved target and both were reverted for a measured net
  of zero.
- Brittle is not low-value. The single highest-value test in the last mutation
  run (62 mutants, 11 exclusively) was one that had been red and needed repair.

**Known findings to start from, all deferred with evidence, none of them
regressions:**

- A deleted GITLINK is bound as `gitlink\0<commit>` but the semantic carrier only
  recovers blob bytes, so it refuses with `preimage-unavailable`. Fail-closed,
  pre-existing. Needs a typed deleted-input contract covering path kind, mode and
  object identity, consumed by both the identity builder and the carrier.
- Changed-line coverage stamps a fingerprint over base and source pool but does
  not bind the coverage JSON bytes; a post-stamp report mutation is accepted.
- `check_current_pointer_writes._could_write_current_pointer` prefilters on the
  literal `latest.` and so cannot see a bare `latest` stem the sibling function
  explicitly recognises.
- `tests/seed_cache.py::_compute_source_hash` consumes Git stdout without
  checking return codes, so a failed read hashes empty output into a valid key.
- `reviewed_input_verification` compares a rebuilt identity to `identity_sha256`
  without first recomputing the digest of the recorded components.
- A Git failure inside a *discoverable* repo still collapses into the same verdict
  as "not a repo" in the setup inspectors; typing it as degraded is a contract
  change, not a preflight.

**Also open, from the census, if you want the remaining efficiency work:**
~493 exact-argv repeats on MUTABLE observations (`status`, open `diff`) that need
case-by-case judgement, and ~35 on genuinely immutable both-endpoints-pinned
questions. The immutable ones are small; the mutable ones are unjudged. Do not
treat either as waste without establishing that nothing changes between the calls.

**Deliverable.** A bounded, evidence-backed disposition per test in the chosen
surface — KEEP / SUBSUMED (name the superset) / STRUCTURAL (quote the code that
makes the bug impossible) / MERGE (name the sibling) — plus, for question 3, any
production duplication found. Then the smallest change that acts on it. Measure
before and after; report measured numbers only.

---

## Why this shape

The last session asked "are these tests high-value?" and got three partial
answers that disagreed until they were forced to converge:

- A bounded reviewer reading 70 tests said KEEP 62, SUBSUMED 8, **STRUCTURAL 0** —
  nothing was obsolete.
- Mutation attribution said the pins have real teeth (73% score, 50 of 63 names
  kill something) and produced no deletion list.
- The only removals that survived both were **seven literal copy-paste
  duplicates** left by an incomplete file split, one of which had drifted into
  being weaker than its twin and would have passed with a known bug present.

So the value question, asked of tests alone, mostly returns "they earn it". The
un-asked half is whether the *production* code is duplicated underneath them.
That is what this prompt puts first.

## Suggested first surface

Pick one, small enough to finish:

- `scripts/reviewed_input_*.py` + `skills/public/critique/scripts/semantic_review_input.py`
  — already has mutation data (56 survivors, concentrated in
  `_parse_cat_file_batch` 7/9, `_git_objects_optional` 9/12,
  `_prepare_path_snapshots` 7/11) and a known restated-contract defect. The
  batching plumbing added *by the efficiency campaign* is the least-guarded code
  in the module while the semantics above it are heavily pinned.
- The `check_staged_*` / `dup_ratchet_*` gate family — several gates that look
  like they answer overlapping questions about a staged change.

## Instruments worth making repo-owned

Both were throwaways last session and both found real defects:

1. Orphaned-`_case_`-helper scan (helpers defined minus names referenced). Already
   filed as a Next Improvement in the retro.
2. Per-mutant killer attribution. Distinct from the existing mutation score
   surface, which answers "how good is the suite" rather than "which test is
   irreplaceable".
