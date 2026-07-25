# Critique Review
Date: 2026-07-25

## Decision Under Review

Delete the `retro` skill's `weekly` mode entirely, rather than splitting it into
references as the handoff previously planned. The operator questioned whether the
concept was needed at all; the evidence said no.

What the measurement showed:

- 1 weekly artifact ever (`weekly-2026-04-14.md`, ~3.5 months old, never repeated)
  against 12 session retros and 114 release-auto retros.
- `metrics_commands: []` — the "metrics-heavy" rationale was inert.
- The **entire behavioral delta** between a session plan and a weekly plan was two
  extra `required_reads` plus a mode string. Same next_action, same gate_packets,
  same write path, same validation.

What was preserved: the one genuinely valuable thing sitting behind the mode — the
closeout-telemetry miner — moved to `references/closeout-telemetry.md` and is now
routed on **every** retro. Its live stream holds 985 records and 4 recurring
findings, the top one a gate peaking at 475s across 16 runs. Nothing was reading it.

## Failure Angles

- Michael Jackson (problem framing): is the concept dead, or merely the prose
  describing it?
- Atul Gawande (checklist/operational): does a consumer repo break on upgrade?
- Jef Raskin (humane interface): does a reader now face fewer decisions, or just
  fewer words?
- Barbara Minto (structure/communication): is anything left half-deleted?

## Counterweight Pass

- **Act Before Ship:** the reviewer falsified a load-bearing premise. I wrote that
  the configured snapshot was "never written"; `weekly-2026-04-14.md:77` records
  `yes .charness/retro/weekly-latest.json`. It *was* written — the path is
  gitignored, so no copy survives. The honest claim is **"no reader ever existed"**,
  which I verified independently (nothing in the repo reads `snapshot_path` or that
  file). Corrected here and in the commit message rather than shipping a rationale
  falsifiable in ten seconds by the very artifact I cited as evidence.
- **Act Before Ship (BLOCKER):** `charness-artifacts/capability-catalog/latest.*`
  still named `mode-guide.md` and `weekly-trends.md` and carried the old mode-selection
  description. CLAUDE.md routes agents to that catalog, and
  `validate_current_pointer_freshness.py` only cross-checks the `integrations`
  section — skill `referenced_paths` are never compared to disk, so this would have
  shipped silently and handed the *next agent* a capability map naming deleted files.
  Regenerated.
- **Bundle Anyway:** the dead `--invocation-text` flag (the `_select_mode` amputation
  site) was still advertised in `SKILL.md` and its help string claimed a use it no
  longer had; deleted. A machine-visible warning string still said "Session mode can
  proceed"; reworded. The `.charness/retro/weekly-latest.json` gitignore assertion in
  `test_managed_install.py` was a green test naming a deleted artifact; repointed at
  the telemetry stream the harness actually writes.
- **Over-Worry:** "this is the fewer-lines failure signature." The reviewer argued
  both sides and landed on genuine P2 delete, and I agree with its test: the change
  did the opposite of shaving — it *promoted* content out of a reference into
  unconditional routing, and turned an unread 985-record stream into something every
  retro must read. Line count is a side effect, not the claim.
- **Valid but Defer:** `session` survives as a backticked token frozen by a CORE pin
  (`check_skill_contracts.py:161`) and by the `auto_session_trigger_*` adapter field
  names. Retained deliberately — with `weekly` gone it reads as a scope word ("a
  short session retro"), and removing it has real cost. Recorded so it is a conscious
  call, not an oversight.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/retro/weekly-2026-04-14.md:77 | action: fix | note: my "snapshot never written" premise is falsified by the artifact I cited as evidence; the load-bearing and verified claim is that no reader ever existed
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/capability-catalog/latest.json | action: fix | note: generated inventory still named two deleted references and the removed mode; CLAUDE.md routes agents to it and no gate cross-checks skill referenced_paths against disk, so a wrong capability map would have escaped to the next agent
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/retro/scripts/plan_retro_run.py | action: fix | note: `--invocation-text` became dead at the `_select_mode` removal but was still documented in SKILL.md and carried a help string claiming a use it no longer had
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/retro/scripts/resolve_adapter.py:124 | action: fix | note: a machine-visible adapter warning still told operators "Session mode can proceed", surfacing a concept the change claims to have removed end-to-end
- F5 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/test_managed_install.py:98 | action: fix | note: a passing test asserted the deleted `.charness/retro/weekly-latest.json` is gitignored — a green proof of a dead path; repointed at the telemetry stream that is actually produced
- F6 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_skill_contracts.py:230 | action: fix | note: the two retro PACKAGE pins were broadened, not deleted, but my justification comment claimed neither was ever weekly-specific — the snapshot guard was; comment corrected
- F7 | bin: bundle-anyway | evidence: strong | ref: tests/test_retro_plan.py | note: the only proof of upgrade-safety for retired adapter keys was an incidental fixture line; added a named test so a future fixture tidy cannot silently delete the contract | action: fix
- F8 | bin: bundle-anyway | evidence: strong | ref: skills/public/setup/references/retro-memory-seam.md:27 | action: fix | note: a consumer-facing setup reference still listed `snapshot_path` among the fields `seed_retro_memory.py` seeds, which it no longer does
- F9 | bin: over-worry | evidence: contested | ref: docs/design-north-star.md:95-99 | action: defer | note: "-177 lines cited as success" — the metric held was reachability of an unread waste stream, and the concept-clarity test (a reader no longer answers "which mode am I in" before "what depth does this deserve")
- F10 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_skill_contracts.py:161 | action: document | note: `session` survives as a backticked token frozen by a CORE pin and by `auto_session_trigger_*` field names; retained deliberately as a scope word rather than finishing the token-level delete
- F11 | bin: valid-but-defer | evidence: strong | ref: scripts/validate_current_pointer_freshness.py:220-254 | action: file-issue | follow-up: deferred to the next-session sweep | note: the freshness validator cross-checks only the `integrations` section, so a generated capability catalog naming deleted skill references is not gate-caught — the blind spot that made F2 possible
- F12 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/retro/retro.md | action: defer | note: the current-pointer copy is the April weekly artifact, 3.5 months stale despite 12 session retros since, and still asserts the removed `## Mode` shape; pre-existing, not caused by this slice

## Reviewer Tier Evidence

- Requested tier: high-leverage (deletion-safety review).
- Requested spawn fields: session-model inheritance (Claude Code host; the repo's
  Codex-only model/effort override does not apply on this host).
- Host exposure state: host-defaulted
- Application state: host-confirmed — a `bounded-reviewer` subagent spawned via the
  Agent tool with a Read/Grep/Glob-only envelope. It reported the envelope bound and
  named one evidence gap it could not close without Bash: `mutants/` is a pre-E2a
  snapshot, so its reading of the deleted `weekly-trends.md` telemetry section is
  inference from the spec plus surviving code rather than a diff. Recorded as a
  non-claim rather than papered over. Parent-side worktree+index integrity was
  fingerprinted around the review; verify returned `{"ok": true, "drift": []}`.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; the reviewer was pointed at the live
worktree and the base ref `79d23b86`).

## Boundary Ownership

- Producer: `retro` owns the mode concept, its references, planner, and adapter
  fields; `setup` owns the retro-memory seam it seeds.
- Consumer: repos whose `.agents/retro-adapter.yaml` carries the retired keys, and
  any repo installing the `retro` skill.
- Verdict: owned-correctly

## Non-Claims

- No capability was proven lost by execution; the survival of every `weekly`
  affordance was established by reading the surviving surfaces, not by running a
  weekly retro before and after.
- The telemetry relocation is proven routed (`tests/test_retro_plan.py`) but no
  retro was actually authored from the new reference in this slice.
- Consumer upgrade-safety is proven against this repo's resolver by a named test;
  no real consumer repo with the retired keys was upgraded and exercised.
- The reviewer's account of what the deleted `weekly-trends.md` telemetry section
  contained is inference from the spec and surviving code, not a diff against the
  base blob.
