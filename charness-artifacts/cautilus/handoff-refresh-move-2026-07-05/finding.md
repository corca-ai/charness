# handoff refresh RCF→RSF MOVE — state-selection.md (#410)

## What ran

**2026-07-05, ask-before-run capture, operator-authorized.** Skill change under
test committed at `60434368`; captured via `capture-skill-run.sh --ref HEAD` on an
isolated worktree (the run resolves `/charness:handoff` from the worktree's
`plugins/charness`, so the tested skill is the ref, not the shared install).

## The MOVE

`state-selection.md` retired from the refresh `requiredCommandFragments` doc-open
floor to an emitted-token `requiredSummaryFragments` floor
(`Refresh kept:` + `Refresh non-claims:`), and dropped from
`plan_handoff_run.py`'s forced refresh `required_reads`. `spill-targets.md` stays
the doc-open RCF floor (its owning-path routing table is genuine depth absent from
SKILL.md — the over-relaxation guard).

Corrects the Slice-7 "refresh opened both docs → PROVEN load-bearing" framing,
which was the documented method error: a planner-forced open of a census-INLINE
doc is a redundant re-read, not proof of depth.

## Outcome — verification against the flipped spec (all from the captured stream, honest not assumed)

- **Grade vs flipped spec: `passed`.** All declared claims met — both RSF tokens
  observed in the closeout AND `spill-targets.md` in the command log.
  Coverage 1/5 DEPTH refs (state-selection.md excluded as INLINE).
- **Compaction achieved.** `Read(state-selection.md) = 0` — the refresh did NOT
  re-read the retired doc; it kept only next-action state from the inlined
  Compression Rule gist. `Read(spill-targets.md) = 1` — the kept DEPTH floor
  genuinely engaged.
- **Tokens are honest substance, not a FORM-floor echo.** `Refresh kept:` named
  real next-action state (unpushed `60434368`; the live #410/#416+#414+#408/
  argparse-debt queue with the D33 trip-wire; the declined D34/D35 discuss item).
  `Refresh non-claims:` named real dropped/spilled items (narrated #404/#415/#411
  closeouts dropped to `git log`; `#371` left discoverable via `gh issue list`;
  explicitly did NOT push `60434368`).

## Honest footnote — old spec ALSO passed (mention, not read)

Grading the same stream against the pre-flip spec (RCF `[state-selection.md,
spill-targets.md]`) also returned `passed`, but NOT because the run read
state-selection.md (`Read = 0`). The lone command-log occurrence is a **Write**
input: the refresh wrote a new `docs/handoff.md` describing this very refactor
commit ("retire the forced `state-selection.md` re-read"). So the old doc-open
floor was satisfiable by a filename mention in written output — extra evidence
that the doc-open RCF was a weak floor, reinforcing (not weakening) the flip. The
clean "old-spec-FAILED" counter-evidence from setup slice2b did not replicate here
only because this run happened to name the file in its output.

## Residual (unchanged, tracked in the spec `_comment`)

The RSF is a FORM floor (handoff has no substance judge): the gist stays inlined in
SKILL.md and the token re-pins harder if a future capture shows a hollow echo.
`pickup` / `pickup-ambiguous` NOT flipped — a faithful pickup hands off to the
invoked workflow, so its closeout token is fragile (deferred follow-up).

Run metrics: 1,564,095 total tokens, 207,634 ms wall. Bundle: `observed.v1.json`
(flipped-spec PASS), `observed.old-spec-mention.v1.json` (mention footnote),
`trace-digest.jsonl`, `transcript.txt` (closeout). Raw capture (worktree/config/
stream/credentials) scrubbed — not committed.
