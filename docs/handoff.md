# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.52.6 released** (pushed + tagged + verified): dup-ratchet hardening +
  `check_dup_ratchet.py` coverage (0->86%, #393) + nose 0.13.3 scan->query migration. CI
  Quality Core green; install refreshed (plugin == repo).
- **lychee BUY reverted** (item ②): 0 behavioral gain vs the existing 2-line `.exists()`;
  net-negative, reset to origin/main. Lesson: a BUY must beat the *existing baseline*, not
  a strawman. v0.52.6 findings resolved (#395 filed; pre-push vs release-mode divergence =
  intended design).

## Next Session

- **TOP PRIORITY — execute the North-Star Overhaul**
  ([roadmap](./north-star-overhaul-roadmap.md)). Authored but **barely started**: only
  the #386 non-terminality pilot landed; Phase 1 (#387) + Phases 2-4 are unstarted, so
  the public **skills do NOT yet embody the new doctrine** (equip a judge; teeth only
  where a wrong answer escapes; non-terminal per-unit disposition over terminal-green).
  Now #1 because it **gates propagating the doctrine to consumer repos (ceal)**. Start:
  Phase 0 (validate diagnosis) -> Phase 1 (#387, aggregate closeout-shape errors in one
  pass). Open question (roadmap): one `achieve` goal vs independent issues.
- **craken-agents absorption (recurring overhaul input).** Pass-1 done
  ([note](../charness-artifacts/audit/2026-06-20-craken-agents-absorption-pass-1.md)):
  craken & charness independently converged on the north star, so wins are better
  phrasings/worked examples (A1 survivor-disposition, A2 re-audit-by-removal, A4
  evidence-depth), not new capability; `bug-hunt` is an external skill NOT in the repo —
  locate it next pass. Re-run each session.
- **ceal propagation (downstream; 2 surfaces).** ceal embeds charness via a vendored pin
  (~35 commits stale — this is how the ceal agent instance ships charness inside itself)
  and via a machine-level plugin install; the two can drift independently. Plus a real
  bug: its native nose advisory calls the removed `nose scan`. Issue draft re-scoped
  across both surfaces; pin target is the v0.52.6 release tag. Review before filing.
- **Secondary — gate demotions:** Track A = demote check_doc_links backtick/bare-mention
  to advisory (surviving value from item ②), then critique/skill-ergonomics demotions.
  Plus: changed-line gate `--reuse-coverage` should skip a coverage file containing none
  of the changed paths (removes a false-block class, not a floor).
- **Untouched:** [#391](https://github.com/corca-ai/charness/issues/391) extractions +
  tool_version stamp; #392 gather X; #371 agent-browser teardown.

## Discuss

- **Operator decided (2026-06-20):** finish the north-star overhaul in charness BEFORE
  propagating the doctrine to ceal — the skills must embody it first. ceal gets the
  already-shipped mechanisms now (separate issue); the overhaul doctrine waits.

## References

- [design north star](./design-north-star.md),
  [north-star overhaul roadmap](./north-star-overhaul-roadmap.md),
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md)
