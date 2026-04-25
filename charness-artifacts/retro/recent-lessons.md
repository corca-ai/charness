# Recent Retro Lessons

## Current Focus

- The reviewed work unit changed the `narrative` public skill so agents can create or check repo-local narrative adapters before rewriting README or other first-touch truth surfaces. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- The user challenged my final phrasing that cited a "host-level delegation policy" after a quality review that should have respected this repo's checked-in subagent delegation contract. (source: `charness-artifacts/retro/2026-04-24-delegation-policy-phrasing.md`)

## Repeat Traps

- That delayed two useful facts: runtime budgets were machine-profile blind, and only the final runtime-budget phase has a real ordering dependency. (source: `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`)
- The available instructions hinted at consumer validation but did not force a customer-of-this-skill angle. `create-skill` says to use a realistic consumer prompt, and `premortem` offers blast-radius/current-consumer angles, but neither makes “run the changed skill as its customer would” a stop gate for repo-local skill changes. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- The first premortem came too late. It caught the important misses only after implementation: bad examples, empty scaffold fields, missing repair loop, and weak volatile-path detection. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- The first runtime-optimization passes used direct local exploration before applying the repo rule that task-completing `quality` and `init-repo` reviews should run bounded delegated review. (source: `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`)
- A C3 hitl decision deleted the `## Subagent Delegation` section without sweeping for the still-live "When the section below applies..." callers in Operating Stance. The broken self-reference rode through to apply and was only caught by the user. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- `scripts/migrate_backtick_file_refs.py` converted backticked paths to markdown links repo-wide without distinguishing portable skill surfaces from charness-only surfaces, producing 110+ broken `[label](../../../../path)` links inside `skills/public/` and `skills/support/`. `scripts/check_doc_links.py` then warns on the symmetric bare-backtick form, so the two tools push portable bodies toward whichever shape is currently broken. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)

## Next-Time Checklist

- Capability: keep runtime-budget contracts profile-aware so samples from different machines do not share one hard threshold. (source: `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`)
- Consider a validator or canned quality closeout phrase that rejects vague "host policy" wording when the repo's bounded subagent rule is the relevant local contract. (source: `charness-artifacts/retro/2026-04-24-delegation-policy-phrasing.md`)
- For public skill changes, start with the changed skill's customer journey, not the skill package. Name at least one real or synthetic consumer repo and run the first-use path before declaring the design good. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- For repo-local skill customization in other repos, use the same principle: validate the changed skill from the repo-local consumer's first prompt, including missing adapter, stale adapter, and thin adapter states. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- After deleting or renaming a heading or anchor in `AGENTS.md` or a SKILL body, run a callers sweep (grep for the heading text plus the phrase "section below" / "above") before any apply pass. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- Before running a repo-wide markdown migrator, separate portable skill surfaces (`skills/public/`, `skills/support/`) from charness-only surfaces and apply distinct rules per surface; default to placeholders like `<repo-root>/...` inside portable bodies for charness-only paths. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- When a hook flags one markdown lint mistake, run the underlying validator end-to-end (e.g. `python3 scripts/check_doc_links.py --repo-root .`) before re-attempting commit, instead of fixing one finding at a time across many retries. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-24-delegation-policy-phrasing.md`
- `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`
- `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`
- `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`
