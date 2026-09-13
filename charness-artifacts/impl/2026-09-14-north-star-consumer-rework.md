# North-star consumer rework slice

Date: 2026-09-14

## Changed behavior

- Ordinary `impl` completes from `SKILL.md`. References open only when their listed trigger is live.
- Cheap owners of edited files are an impl Verify step, and author-time `--paths` is named on the timing-layers page.
- Mutation issue comments that are `UNMEASURED` or skipped no longer headline as a scored regression.
- Inner Cosmic Ray exec timeout is capped to remaining job budget minus dump reserve.
- Grok Build host notes live at `.agents/grok-host.md`. `AGENTS.md` is unchanged.

## Verification

`./scripts/run-quality.sh --full --read-only` passed: 84 passed, 0 failed, 5 not run (named opt-in/read-only omissions). Fresh-eye on the mutation proof surface: pass, with residual non-claims below.

## Non-claims

- `#764` is not closed. Sampler baseline failures and uncovered changed lines remain distinct blocking signals.
- `charness-artifacts/quality/latest.md` is not refreshed; a stub would fail the quality-artifact contract.
- No push, release, or mutation-floor change.
- Issue title `Mutation test regression on main` is unchanged; the comment lead now contradicts a scored-regression reading.
- JS mutation after Python dump is not reserved inside the 120s dump window.
