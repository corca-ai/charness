# setup greenfield — capture-PROVEN KEEP; census MOVE refuted per-condition (#410 Slice 9c)

## What ran

**2026-07-09, ask-before-run captures, operator-authorized** (operator: proceed
with the entire remaining #410 queue; `justification.md`). The #410 blocker
("greenfield is NOT in-repo capturable") was removed by extending
`capture-skill-run.sh` with `--run-cwd`: the captured `claude -p` runs in a
fresh non-charness sandbox repo (git init only) while the plugin resolves from
the charness worktree at `--ref`. First-ever live evidence for this arm (the
floor was HYPOTHESIS since authoring).

## Capture 1 (sibling bundle `setup-greenfield-slice9-2026-07-09`) — the old prompt is a dead end

Old prompt said "from minimal ideation" but PROVIDED none. The faithful run
detected the empty repo, opened `greenfield-flow.md` for the minimum-questions
set (1/9 coverage; SKILL.md step 3 carries only the gist, the concrete question
set lives in the reference — genuine on-demand DEPTH the census-DUP verdict
under-counted), asked four honest ideation questions, and STOPPED without
scaffolding boilerplate. Grade vs RCF: `failed` (agent-docs-policy.md /
default-surfaces.md never reached) — an honest run could NEVER pass the old
fixture, so the prompt was corrected to carry the ideation inline (fixture
design per the per-condition method; input pinned in the spec, not derived from
a capture). 528,934 tokens, 37,717 ms.

## Capture 2 (this bundle) — the RCF floor is genuinely load-bearing

Corrected prompt (inline 'logtrim' ideation). **Grade vs the standing RCF spec:
`passed`** — the run GENUINELY opened all three floor docs
(`greenfield-flow.md`, `agent-docs-policy.md`, `default-surfaces.md`; 4/9
coverage), scaffolded README / AGENTS.md / docs/roadmap.md /
docs/operator-acceptance.md plus the CLAUDE.md→AGENTS.md symlink, ran three
bounded fresh-eye reviewers of its own, committed a root commit, and emitted
the full closeout vocabulary. 3,875,559 tokens, 378,840 ms wall.

## Verdict — KEEP (strengthened), not MOVE

- The slice7 census flattened setup to INLINE/DUP from the NORMALIZATION run's
  0/9 — that said nothing about the greenfield branch. Per the reconciliation
  doc's own METHOD CORRECTION ("a single fixture cannot exercise a
  conditionally-read doc"), the greenfield condition genuinely consults all
  three docs: **the census MOVE verdicts are REFUTED for this arm; the doc-open
  RCF floor stays.**
- **Strengthened with observed tokens:** RSF now pins `Repo mode:` +
  `Normalization non-claims:` — both OBSERVED in the capture-2 closeout
  (`Repo mode: GREENFIELD`, per-surface `scaffolded` accounting,
  honest non-claims naming missing code/tests/LICENSE/push) — never assumed.
- `thresholds.max_duration_ms=800000` set from the 378,840 ms baseline.
- The sibling `outcome-assertions.json` stays normalization-scoped; grading a
  greenfield capture against it still requires a scenario guard (unchanged).

Raw captures (worktree/config/stream/credentials/sandbox) scrubbed — not
committed; both bundles keep observed packet + trace digest + transcript.

## Non-Claims

- The normalization-scoped `outcome-assertions.json` was NOT exercised against a
  greenfield capture (scenario guard still required); no substance-judge verdict
  is claimed for this arm.
- The captured scaffold quality is evidence for floor engagement, not an
  operator acceptance of the generated docs; nothing was pushed anywhere.
