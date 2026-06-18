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

- **Mid-track: gate buy-vs-build.** Per-item decided plan + full reasoning is the
  source of truth in
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md)
  — read it first.
- **4 commits done, UNPUSHED (operator HELD push):** A (bootstrap idiom
  unification + #390 record fix + craken study), B triage, B DROP #1/#2
  (test-production-ratio + title-slug demoted to advisory), and **① now COMMITTED**
  — `validate_critique_packet` DELETE (both copies, tests, doc pointer; dogfood
  decision recorded in the critique dogfood case). Fresh-eye SAFE
  (all 5 deletion claims CONFIRMED); verification-lock closeout green
  (3201 pass); Cautilus next-action `none`.
- length-config WITHDRAWN (caps stay hard). nose v0.13.0 = char-n-gram markdown
  dup (confirmed); lychee on PATH but not a managed integration yet.

## Next Session

- Each remaining gate item is its own slice (B1 advisory pattern, fresh-eye +
  broad closeout):
  - **3.** function-length cap -> ruff PLR0915 + keep mccabe; delete the bespoke
    function-length arm (file-line cap unchanged).
  - **4.** doc near-dup -> nose advisory + make nose a required install.
  - **2.** doc-links -> lychee BUY; keep placeholder/boundary residue; demote
    backtick/bare-mention enforcement to advisory (keep the principle).
  - **Demotions:** validate_critique_artifacts (keep tier-honesty, demote rest);
    validate_skill_ergonomics (keep export-leak arm only — DELICATE adapter split).
- **Separate untouched tracks (original primary, NOT started):**
  - **C. SRP / skill-body reduction.** ~12 public SKILL.md at/near the 200-line
    cap. P2: separate a concept or delete — NOT line-shave (floor stays hard).
    Pre-check pinned snippets (check_skill_contracts) + core-headroom before edit.
    **AGENTS.md `## Skill Routing` is GENERATED/pinned** by setup's
    [render_skill_routing.py](../skills/public/setup/scripts/render_skill_routing.py)
    — reduction needs a lockstep generator edit (recent-lessons S5 trap).
  - **D. #391** extractions (per-package-copy aware) + baseline tool_version stamp.

## Discuss

- **find-skills inventory drift:** session-start bootstrap regenerates `latest.*`
  repo-only (4 support / 11 integ) vs committed host-enriched (8 / 13, incl.
  pry + google-workspace from installed plugins). Restored to HEAD this session
  to keep ① scoped. Decide: should canonical inventory be repo-only local-first
  or host-enriched, and which env regenerates it?
- Open: validate_skill_ergonomics adapter-split appetite. Push timing
  (4 commits ready). Untouched this track: #391, #387, #371.

## References

- [decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [triage](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-triage.md),
  [#390 record](../charness-artifacts/quality/2026-06-19-390-code-layer-quality-pass.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [design north star](./design-north-star.md)
