# Retro: handoff chunker v2 (#249/#248 + end-only timing)

Mode: session

## Context

Closeout of the achieve goal `2026-05-29-249-248-handoff-chunker-v2`: the
handoff chunker now reasons over the live open-issue backlog (#249 input),
fires on a bare skill invocation (#249 trigger), composes its stage scripts
predictably (#248), and the handoff baton is codified as closeout-only with
`## Next Session` reframed as a curation/sequencing memo. 6 planned slices + 1
length-budget split, each committed with tests; final broad gate 1793 passed /
4 skipped / 0 failed.

## Waste

- **#248 defect bit the operator first-hand at session start.** The very first
  chunker run this session failed on a stage-script flag mismatch
  (`--repo-root` vs `--entries` vs `--merge-proposal`) — the exact ergonomics
  defect #248 reports. It became Slice 1's regression seed, so the cost was
  recovered, but it cost one retry on the opening pickup.
- **Slice-2 over-merge caught only by live dogfood.** The first cut extracted
  boundary tokens from full issue *bodies*; on real data that collapsed
  unrelated issues into a giant spurious cluster (mutation body paths
  transitively merged with a process issue). The plan critique had flagged
  this exact risk as *over-worry*; real data proved it real. Cost: one design
  iteration + test rework to narrow to title+labels.
- **SKILL.md budget fight (recent-lessons trap #1 recurrence).**
  handoff/SKILL.md sat at exactly its 161-line slice-6 sub-budget; the Slice-5
  additions overshot to 169 and took two trim passes to claw back. The
  load-bearing content was right early; the budget fight cost the iterations —
  the documented "SKILL.md at the cap is a latent tax" trap, recurring.
- **Length trap recurrence (issue_source 393 > 360).** A new module grew past
  the soft single-file cap and was caught only at the After-phase length gate,
  forcing a 7th split commit. This is the SECOND recorded recurrence of the
  silent-lib-growth trap; `check_python_lengths` is still only informational.
- **Final broad gate is slow + opaque.** 6m36s, and `pytest -q` buffers output
  so background polling showed nothing until completion. Minor friction.

## Critical Decisions

- **End-only handoff timing** (the meta-discussion that opened the goal):
  reframed the handoff as a closeout-only baton; a pickup writes only the
  derived goal skeleton, never the baton. Now codified in operating-contract +
  chunked-routing.md. This decision shaped the whole goal.
- **Issue boundary tokens = title + specific labels only** (dogfood-driven):
  chose precision over recall to avoid over-merge. The single most important
  quality decision; validated by the live run collapsing to one correct cluster.
- **Reuse the `issue_runtime` backend seam** (gh default template / non-gh
  declares `commands.list_open`) instead of hardcoding `gh` — kept the chunker
  provider-portable per the #249 boundary.
- **Cautilus planner-refused → honest manual proof.** The planner returned
  `next_action: none` (`run_mode: ask`); per the cautilus-on-demand contract I
  did NOT invoke cautilus and fell back to the pre-declared manual dogfood
  proof, naming cautilus as a skipped level. No false closeout signal.

## Expert Counterfactuals

- **Don Norman / Jef Raskin (affordances + discoverability)** on #248: the
  inconsistent-flag pipeline was a discoverability failure — every hop forced a
  `--help` lookup and a wrong guess failed two stages downstream as opaque JSON.
  The fix (uniform `--input`/`-i`, stdin default, loud structured fail) is
  exactly Norman's "make the right action obvious, fail informatively." A
  Norman-first review of the original stage scripts would have caught the
  defect before it shipped, not after it bit a pickup.
- **W. Edwards Deming (the *study* step — measure against prediction)** on the
  Slice-2 over-merge: I predicted body-path clustering would group same-surface
  issues and pinned fixtures to that prediction; the live dogfood (the study
  step) refuted it. Running the dogfood *before* writing the fixtures
  (predict → measure → then pin) would have shaped the boundary-token decision
  from the start and saved the test rework.

## Next Improvements

- **capability**: Promote `check_python_lengths.py` from informational to a
  pre-commit gate (warn-at-~330, fail-at-360 for `skills/public/*/scripts/*.py`).
  This is the second recorded recurrence of the silent-lib-growth trap; the
  prior retro already recommended it. The recurrence is the evidence to act now.
- **workflow**: Before editing any SKILL.md, check budget headroom first
  (`wc -l` vs the repo/sub-budget cap). When headroom is <~10 lines, spill to a
  reference by default rather than writing prose and trimming back.
- **workflow**: For any heuristic that derives a signal from free text
  (clustering, boundary tokens, routing), run a live dogfood sanity check
  before pinning fixtures — Deming study-first — so the extraction breadth is
  data-shaped, not assumption-shaped.
- **memory**: end-only handoff timing + the over-merge precision lesson are
  codified (operating-contract, chunked-routing.md) and captured here for the
  recent-lessons digest.

## Sibling Search

Transferable pattern: **a merge/clustering signal derived from free text
over-clusters when the source is verbose.** Four-axis scan:

- **same-skill**: the handoff parser's `_build_boundary_tokens` also extracts
  path tokens from entry bodies — but handoff `## Next Session` entries are
  short curated prose, so over-merge risk is materially lower; left as-is
  (monitor, not fix).
- **same-mechanism**: `propose_merges` connected-components is shared by both
  handoff-entry and issue-entry inputs; the fix lives at the *token source*
  (issue conversion), not the proposer, so the proposer needs no change.
- **other-skills**: no other skill currently feeds free-text-derived tokens
  into a clustering step (issue/quality do not cluster).
- **docs/contract**: chunked-routing.md now documents "title+labels, not body"
  as the issue boundary rule, so the precision decision is discoverable.

Decision: **narrowly contained** — the only high-risk site (verbose issue
bodies) is fixed; the one sibling (handoff parser) is low-risk by input shape.
No follow-up issue filed.

## Persisted

Persisted: yes (see path printed by persist helper).
