# Disposition Review — goal `325-provenance-policy-handoff3-gate-capability` (#325 + handoff-3)

Bounded fresh-eye disposition review for the `/achieve` closeout of goal
`2026-06-07-325-provenance-policy-handoff3-gate-capability` (#325
provenance-placement policy + portable standing-doc check, and handoff-3
changed-line mutation gate as a portable `quality` capability). Verifies every
improvement the session retro
(`charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`)
surfaced got a real, honest disposition — applied / filed / opted-out — and that
no disposition is over-claimed.

## Reviewer Provenance

Bounded fresh-eye `critique` subagent (read-only) in the shared parent worktree.
Inputs: the goal artifact, the session retro (`## Next Improvements`,
`## Sibling Search`, `## Persisted`), the two delivery critiques, recent-lessons,
and read-only `gh issue view 328` / `gh issue view 325` + `git log` probes. No
edits except this artifact; no index- or worktree-mutating git ops.

## Verdict

**dispositions-sound** (with one non-blocking honesty note on persistence
timing — see Gaps).

## Per-Improvement

- **#1 workflow** (batch portable-surface validators upfront before the first
  broad closeout for slices adding new skill-package files) → disposition: adopt
  as next-session workflow + recorded in recent-lessons. **Sound.** Correct kind
  — a workflow lesson belongs in memory/recent-lessons, not an issue. Verified
  present in the working-tree recent-lessons (`Next-Time Checklist` + the
  `Authoring-preflight skip` repeat trap, source-tagged to this retro). Honest:
  the counterweight in the retro correctly carves out the unavoidable serial
  share (ruff sort, mirror sync, broad pytest), so the lesson does not over-claim
  that all serial discovery is preventable.

- **#2 capability** (extend `check_skill_surface_preflight.py` or a sibling to
  run the portable-package gate set as one pre-author/pre-closeout tripwire) →
  disposition: candidate fold into existing `issue #328`; decide there vs a new
  issue. **Sound and correctly routed.** `gh issue view 328` confirms #328 exists
  (OPEN, "Cheap upstream pre-checks before expensive/late verification — prose-pin
  scan + authoring-preflight prompt"). Its "useful outcome" already names "a
  lighter-weight prompt to run `check_skill_surface_preflight.py` /
  authoring-preflight.md before editing a gated SKILL.md/reference" and explicitly
  flags itself as #325-adjacent ("decide whether it folds there or stands alone").
  The retro's "fold into #328, decide there" is therefore the honest call — the
  gap is plausibly in scope, and the disposition defers the fold-vs-split decision
  to the issue rather than over-claiming resolution. A tooling gap → an issue is
  the right kind.

- **#3 memory** (retro + recent-lessons digest carry the recurrence) →
  disposition: done (persisted). **Substantively sound; timing nuance.** The
  recurrence IS captured: recent-lessons working tree carries both the repeat
  trap and the Next-Time Checklist entry, source-tagged to this retro (3 hits).
  The retro file itself exists. Caveat: at review time the retro file is untracked
  and the recent-lessons / lesson-selection-index edits are uncommitted (present
  only in the working tree, 0 hits in HEAD). This is expected for an in-progress
  closeout (retro precedes the final retro commit), so "persisted" is accurate to
  intent but not yet to git — see Gaps. The retro's `## Persisted` section still
  reads `(set on write)`, which should resolve when the closeout commits.

- **Sibling Search call** (serial discovery behind a gate → "recurrence of an
  existing tracked lesson; boost, do not file a new issue; the concrete capability
  gap is tracked under #328"). **Honest.** Verified the pattern is already in
  recent-lessons (the "serial discovery / authoring-preflight skip" repeat trap
  family and the #328 capability entry), so "boost not new issue" is justified —
  filing a duplicate would be the wrong move, and the one concrete tooling gap is
  not dropped (it rides on #328).

## Gaps

- **No silently-dropped improvement; no mis-routed disposition.** All three Next
  Improvements and the Sibling Search call are dispositioned honestly and with the
  right kind (workflow→memory, capability→issue #328, memory→persisted), and #328
  genuinely covers the capability gap.
- **One non-blocking persistence-timing note (not a drop):** the retro file is
  untracked and the recent-lessons / lesson-selection-index refresh is uncommitted
  at review time, and the retro's `## Persisted` block still says `(set on write)`.
  The lesson content is correct and present in the working tree, so this is a
  closeout-ordering artifact, not a dropped disposition — but the final
  `/achieve` closeout commit MUST include these files (and resolve `## Persisted`)
  for the "memory persisted" disposition to be true in git. The goal's
  `## Final Verification` likewise still carries `TODO` for Retro / Host-log /
  Disposition-review, which the closeout must bind (this artifact satisfies the
  Disposition-review slot). Per the repo disposition-floor lesson (#329, memory
  digest), confirm these land in the commit rather than relying on a clean tree.
