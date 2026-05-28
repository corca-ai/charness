# Operating Contract

This document owns Charness repo conventions that do not need to be repeated in
the root instruction file. [AGENTS.md](../../AGENTS.md) stays as the session
entry and link index.

## Guiding Principles

These expand in [README.md Core Concepts](../../README.md#core-concepts):

1. Less Is More: strong defaults over menus; progressive disclosure.
2. Agents Are First-Class Users: CLIs, scripts, artifacts, docs are agent-facing.
3. Reveal Intent, Hide Detail: public surface names intent; tool detail sits underneath.
4. Human-Code-AI Symbiosis: humans judge, code verifies, AI drafts.
5. Long-Running Agents Need Quality Software: quality as trust surface.
6. Tacit Knowledge Becomes Workflow: expert moves become reusable skills.
7. The System Should Get Smarter With Use: retros and adapters learn.
8. Context Must Keep Flowing: handoff, review, release, and narrative are core work.

## Commit Discipline

- After each meaningful unit of work, create a git commit before moving on.
- Do not leave task-completing repo work in a dirty tree unless the user
  explicitly asked to pause before commit or an unresolved blocker is named.
- Prefer commit subjects that state user-facing purpose, not only mechanism.
- After any `git push`, confirm the branch is clean and the remote update succeeded.
- When a Charness workflow creates or updates durable artifacts under
  [charness-artifacts/](../../charness-artifacts/), include meaningful artifact
  changes in the same commit as the work they support.
- Cite proof from checked-in durable evidence in spec, quality, release,
  dogfood, debug, premortem, and design-study artifacts. Paths matching
  [.gitignore](../../.gitignore) are reproduction sources only and must
  carry an inline `<!-- reproduction-source -->` marker; otherwise check in a
  selected proof artifact with the cited fields. See
  [skills/public/spec/references/evidence-durability.md](../../skills/public/spec/references/evidence-durability.md).

## Pointer-Write Discipline

- Skill `latest.*` artifacts are read-mostly current pointers. When a skill
  refreshes the pointer to a new canonical record, never overwrite or unlink
  the prior canonical record by writing through a stale symlink target. The
  trap (issue #138, gather): `latest.md -> 2026-01-01.md` symlink combined
  with a writer that opens `latest.md` for writing rewrites the prior dated
  record in place. The fix shape is `lstat` the pointer first, write a fresh
  canonical record under its dated filename, then atomically swap the pointer
  via `unlink + symlink_to` (acceptable small-window race for read-mostly
  pointers).
- The reference implementation lives in
  [skills/public/gather/scripts/write_record.py](../../skills/public/gather/scripts/write_record.py)
  and [`gather_writer_lib`](../../skills/public/gather/scripts/gather_writer_lib.py).
  Other skills that publish a `latest.*` rolling pointer
  (find-skills/quality/release/cautilus/debug/hitl/narrative/retro/critique)
  inherit the same hazard and should reuse this writer once promoted to a
  shared helper, not reimplement open-and-overwrite.

## Critique Discipline

- Every task-completing repo change runs critique before closeout. Scale the
  pass, not the obligation.
- Small local-risk slices may use a short scoped critique artifact that names
  the decision, the likely misread, counterweight triage, and the next move.
- Non-trivial design, deletion, rename, release, workflow, compatibility,
  install/update, host-proof, prompt-surface, public-skill, validator, or export
  decisions use the standalone `critique` skill.
- `Critique: not-applicable <reason>` is reserved for inspect-only, status-only,
  or routing-only requests that do not complete repo work.
- If the required bounded-review path is blocked by the host, stop and record
  `Critique: blocked <host-signal>` instead of substituting same-agent review.

## Skill And Metadata Discipline

- Treat `skills/public/<skill-id>/SKILL.md` as the trigger contract and
  decision skeleton; keep long rationale, examples, schemas, and edge cases in
  `references/`.
- Sparse real-person anchors in `SKILL.md` core are intentional retrieval aids
  when they improve reasoning; keep them factual, behavior-linked, and
  supported by `references/`.
- Keep frontmatter YAML-safe. Quote descriptions when punctuation would make
  plain scalars fragile.

## Dogfood Discipline

- Loaded skills may come from a host-managed checkout or plugin cache rather
  than this working tree. For Claude managed-checkout dogfood, that path is
  usually `~/.agents/src/charness/`.
- Editing `skills/public/<id>/SKILL.md` does not reach the next Claude/Codex
  session in this repo until the relevant install or update path picks it up.
- Keep detailed dogfood procedures in [docs/development.md](../development.md),
  not in AGENTS.md.
- After a release or dogfood cycle, `charness update` with no flags restores
  the managed-checkout flow.

## Local Enforcement Policy

- `./scripts/run-quality.sh --read-only` is enforced locally via `.githooks/pre-push`. Every push runs current-pointer freshness, plugin manifest sync, and the artifact-mutation guard. The read-only gate runs in two shapes per push, selected by [`classify_push_diff_lib.py`](../../scripts/classify_push_diff_lib.py):
  - **Full gate**: every push that touches `plugins/`, `.claude-plugin/`, `.agents/plugins/`, `scripts/`, `skills/`, `tests/`, `integrations/`, `profiles/`, `presets/`, `packaging/`, `evals/`, the `charness` CLI, packaging manifest, `Makefile`, any top-level dotfile/dir, or any non-allowlisted path. The first three are the slice-7 stop-condition prefixes and are unconditional.
  - **Docs-only subset**: every push whose entire diff is on the allowlist (`docs/`, `charness-artifacts/`, plus the root README/AGENTS/CLAUDE entry-point files). Runs ~15 doc/artifact phases (check-doc-links, check-markdown, check-links-internal, check-references-link-inventory, check-spec-evidence-durability, check-title-slug-drift, check-duplicates, validate-{handoff,debug,quality,retro,ideation,critique-artifacts}-artifact, inventory-quality-handoff, validate-current-pointer-freshness) in ~13s instead of ~100-120s.
  - Operator override: `CHARNESS_FORCE_FULL_GATE=1 git push ...` forces the full gate regardless of the classifier's decision.
  - New ref creation, ref deletion, and unresolvable upstream all force the full gate (no upstream-sha to diff against).
- The only checked-in workflow is [`scheduled-deeper-check`](../../.github/workflows/mutation-tests.yml). It is marked `# charness:gate-policy scheduled-deeper-check` and is intentionally exempt from CI/local gate parity by [`inventory_ci_local_gate_parity.py`](../../skills/public/quality/scripts/inventory_ci_local_gate_parity.py).
- PR CI does **not** mirror the read-only quality gate. This is the intended posture under the current single-maintainer push model: the pre-push hook owns standing enforcement, and no recurring external PR contribution path exists yet. Quality reviews that flag "no non-exempt PR CI workflow runs the local gate" should treat that as intended, not missing.
- Reopen trigger: when external PR contribution becomes a recurring path (more than one outside contributor PR per release cycle), add a conditional PR CI workflow that mirrors `./scripts/run-quality.sh --read-only` for `pull_request.head.repo.full_name != github.repository`.

## Session Discipline

- Update [docs/handoff.md](../handoff.md) when the next session's first move changed.
- If the user correctly points out a missed issue, broken assumption, or
  missing gate that should likely have been caught, run a brief retro before
  continuing and say whether that retro was persisted.
