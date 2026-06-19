# Session Retro — item-5 slice-2 boy-scout dup ratchet gate

## Mode

session

## Context

Implemented item-5 slice-2 (the boy-scout duplicate ratchet's teeth): pure policy
lib + git seams, the adapter-driven gate CLI, a validated `dup_ratchet` adapter
block, the green-seeded gate baseline + charness rollout (D6), run-quality + broad
pre-push wiring, the reference, and SC1–SC6 tests. Full `run-quality.sh
--read-only` green (77/0); bounded fresh-eye critique ran (4 angles + counterweight),
acted/deferred/over-worry triage recorded in the spec.

## Evidence Summary

Working-tree diff (26 files), the spec contract `### Slice 2`, the live gate runs
(seed + green re-check), the four critique angle returns + counterweight triage,
and the run-quality `--read-only` summary.

## Waste

- **Re-seeded the gate baseline 3×** (mid-implementation, after the module
  extraction, after the critique fixes). The baseline is a content-hash
  (`family_id`) snapshot of the scanned `.py` tree, so every code edit shifts it
  and invalidates a prematurely-seeded baseline. Each re-seed cost a scan + a
  re-verify. Root cause: seeding a content-hash baseline before code was frozen.
- **Two length-cap collisions discovered at the gate, not before the edit:**
  `quality_policy_defaults.py` was already at its cap (adding the validator pushed
  490 > 480), and `quality/SKILL.md` was pinned at exactly 200 lines (adding a
  required reference entry pushed it to 201). Both forced rework (extract a module;
  trade a redundant convenience line) that a pre-write headroom check would have
  surfaced up front.

## Critical Decisions

- Extracted the dup_ratchet adapter policy into its own module
  (`scripts/quality_dup_ratchet_policy.py`) rather than compacting and leaving a
  length WARN on `quality_policy_defaults.py` — fix the conflicting surface (north
  star) instead of skirting the gate.
- D6 green-seeded baseline + advisory boy-scout arm (operator-decided): ships the
  hard arm live and green, the down-arm dormant-but-tested.
- Per-surface vs whole-gate degrade kept as the FD8 conservative posture
  (never false-block) after the counterweight; the genuine silent-false-green
  (empty real scan vs non-empty baseline) was closed instead.

## Expert Counterfactuals

- **Gerald Weinberg (diagnostic):** "What is this artifact's identity function and
  when does it change?" Asked up front, the `family_id`-of-the-working-tree nature
  of the gate baseline makes "seed last, after freeze" obvious — would have avoided
  two of the three re-seeds.
- **Atul Gawande (checklist):** a standing pre-write step — run
  `check_python_lengths --headroom` on every file about to grow — turns both
  cap collisions from gate-time surprises into a 2-second pre-edit check.

## Next Improvements

- workflow: for content-hash-keyed baselines (this gate; also `nose-baseline.json`
  / `doc-nose-baseline.json`), seed/re-seed as the LAST pre-commit step once code
  is frozen. The dup-ratchet adoption doc now orders scope-then-seed; the "seed
  last" timing is the transferable half.
- workflow: run `check_python_lengths --repo-root . --headroom <file>` before
  adding code to a near-cap module, rather than learning the cap at the gate.
- memory: this artifact + the recent-lessons digest carry the "seed content-hash
  baselines after freeze" + "check length headroom before editing near-cap files"
  lessons.

## Sibling Search

The "content-hash baseline must be seeded after the code is frozen" pattern has
two siblings — `nose-baseline.json` and `doc-nose-baseline.json`, both
`--write-baseline` flows. Both already document per-scanner-version re-baseline
discipline, but neither states the *timing* ("seed last in the slice"); they are
maintainer-run deliberately, so the recurrence risk is low. Recorded here rather
than opening a follow-up: `n/a — low transfer; existing baselines are
deliberately maintainer-seeded`.

## Persisted

(to be filled by the persistence helper)
