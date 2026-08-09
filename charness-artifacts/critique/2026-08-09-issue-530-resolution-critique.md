# Issue #530 Resolution Critique
Date: 2026-08-09
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- requested tier: `bounded-reviewer` typed subagent, read-only by definition
- requested spawn fields: inherited parent model and reasoning settings; no
  per-subagent model or effort override requested; spawned unnamed
- host exposure state: host-defaulted
- envelope note: the reviewer confirmed only Read/Grep/Glob were exposed and
  listed the commands it could not run rather than asserting their outcomes
- application state: spawn tool accepted the reviewer agent id; reviewer-tier
  application details are host-hidden
- Delivery state: findings-received

## Decision Under Review

Closing `#530` on the work shipped as slice 4 of
`charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`
(commit `474ce7c2`, pushed in `ec67291e..18a9a439`).

`#530`: a typo'd adapter key and an unsupported `version` both pass as
`valid: true, errors: [], warnings: []`; 16 of 17 resolvers never compared
`version` against a supported value.

The premise was re-measured rather than inherited, and it REFUTED the planned
slice: `grep -rl 'version must be an integer' scripts skills` returns 0, and a
live probe of all 16 `skills/public/*/scripts/resolve_adapter.py` found 16/16
already refusing `version: 7` with none echoing it back. The version half had
been shipped by the folded `repair-declaration-to-verdict-at-root` goal. What
measurement exposed instead was that the unknown-key tier, armed and shipped,
warns on CORRECT keys in every consumer repo.

## Failure Angles

- **The surface claiming a scope it never established** — the goal's own class,
  turned on the repair that closes it.
- **A false-positive rate measured only where it was low.** The module refused
  to arm `reader-elsewhere` at 13% for being a wolf-crier, then shipped
  `unknown` at ~100% in consumer repos.
- **A close that buries scope.** The repair resolves by DECLINING to answer in
  consumer repos; the risk is that the closeout reads as restored coverage.

## Round 1 — DEFECTIVE, blocker

The guard tested `(repo_root / SHARED_CORE_OWNER).is_file()` — a PROXY for
corpus membership that disagrees with the corpus builder. `_is_reader_file`
drops any path containing a `plugins` component, so under
`--repo-root plugins/charness` the shared core is `is_file()` while every
candidate reader is excluded: corpus empty, guard satisfied, tier confident.
Reproduced by execution at **126 false WARNINGs** over 19 correct shipped
examples, reported as `126 unreconciled declared key(s) across 19 declaring
file(s)`. The repair had reproduced the defect it removed, at larger scale, on
the layout closest to what consumers install.
`test_exported_validate_adapters_runs_from_flattened_layout` runs that exact
root and asserts only the exit code, so the suite could not have caught it.

Repaired: `reader_corpus_established` asks `iter_reader_files` — the corpus
builder itself. An intermediate cache-based version made the predicate depend on
call order and was replaced with the cache-free form.

## Round 2 — DEFECTIVE, blocker inside the round 1 repair

The new "did not run" message said the shared core `is not readable`, which is
FALSE at the plugins root: the file is present and packaging REQUIRES it; it is
EXCLUDED. An operator acting on that sentence would hunt a missing file that is
not missing. The message also lived in a different module from the predicate it
described — a second declaration of the guard's meaning, reconciled by nobody.

Repaired: `unestablished_corpus_reason` now lives next to the predicate and
names the fact actually checked, with a CLI-level test at a plugins-rooted tree.

## Resolution Critique — NOT-CLOSABLE on the first draft

A third delegated reviewer read the closeout draft against the tree and refused
it. The code was sound; the LEDGER was not:

- The repair makes half (b) HONEST, not FIXED, and the draft did not say so. A
  typo'd key still returns `valid: true, errors: [], warnings: []` from every
  resolver — the exact string the issue title quotes. Detection moved to a
  different command that does not affect the exit code.
- In a consumer repo no key verdict is rendered at all, by design, and that gap
  had no durable record anywhere a `#530` reader would find it.
- `siblings` said "three ... Both" (arithmetic), and CLEARED overreached from
  four quality-catalog gates to consumer-invoked surfaces generally, while
  `charness catalog list` is one and is filed as `#574`.
- `debug_artifact` cited "slice 3b", which does not exist in the Slice Log.
- `root_cause` (a) read as if this close fixed the version half; it shipped
  earlier.
- D46 was mis-cited: it governs uninterpreted LINES, not unknown well-formed
  keys; the WARN choice was an operator decision recorded at
  `scripts/adapter_key_registry.py:494-498`.
- Three things `#530` named were unmentioned (`KNOWN_FIELDS`, `charness
  doctor`, `tests/test_retro_plan.py:299`), and one addressed thing was
  unclaimed (the warn scope widening to shipped `adapter.example.yaml`).

All were folded into the posted ledger, and the undocumented consumer gap was
filed as `#576` before the close.

## Counterweight Pass

- **Over-worry rejected:** "declining to answer is not a resolution." It is, for
  the defect actually filed — the issue's measured harm was a false verdict, and
  a surface that cannot compare its inputs must say so. What it is NOT is
  restored detection, which is why `#576` exists.
- **Over-worry rejected:** "the ~100% figure is inflated." Partly fair —
  `validate_adapters.py` is not among the four consumer-facing catalog gates, so
  the measurement is on a fixture and the plugins root. Recorded as a non-claim
  rather than dropped, because the surface still ships.

## Boundary Ownership

- Producer: `scripts/adapter_warn_tier.py` — it produces the unknown-key verdict and the corpus-established fact.
- Consumer: `scripts/validate_adapters.py`, and through it the operator reading a commit-time gate log.
- Owning surface: the adapter warn tier (charness-internal proof surface), not the per-skill resolvers and not the consumer's adapter.
- Verdict: escalated-to-issue-spec

The repair spans two surfaces it owns (`scripts/adapter_warn_tier.py`,
`scripts/validate_adapters.py`) and deliberately does NOT reach the readers that
live behind other owners. Three gaps were escalated rather than absorbed: `#574`
(version-unchecked readers outside the resolver glob, a trust boundary owned by
`capability_catalog_sources` and `setup_adapter`), `#575` (a `check_regenerable_facts`
scope defect owned by `quality`), and `#576` (the consumer-repo verdict gap this
repair created by design). Absorbing any of them would have coupled independently
owned surfaces inside a close.

Deletion, release, and push are out of this critique's scope. The close itself
is the irreversible act reviewed here; `#574`, `#575`, `#576` carry what this
close does not.

## Will The Class Recur

Partly guarded. `reader_corpus_established` asking the corpus builder cannot
drift from the scan, and the plugins-rooted test pins the exact tree. What is
NOT guarded is the general habit of measuring a rate in the only tree where it
is favorable; that is a reasoning failure, and only the five-consumer-repo
channel caught it here.

## Non-Claims

- The five consumer repos are not the whole consumer population.
- The reviewer could not run commands; the `126`, `3 -> 0`, and planted-typo
  figures were verified by the parent's executed runs, not by the reviewer.
- This critique reviews the CLOSE decision. The implementation's own two bounded
  rounds are recorded in the goal artifact's Slice Log, `### Slice 4`.
