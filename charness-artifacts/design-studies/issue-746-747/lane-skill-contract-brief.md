# Lane brief: critique-skill-contract

`check-skill-contracts` (and, through it, the `run-evals` representative
contract eval) fails: `skills/public/critique/SKILL.md` no longer carries
the core contract snippets `scripts/check_skill_contracts.py` requires
(`optional\nevidence-led mode`, the `- \`Evidence Disposition\` (when
active; identity/count/coverage/digest)` bullet, and a `- \`Execution\``
bullet).

Root-cause first: commit `acd0b0e39` ("refactor(critique): drop output
ceremony") deliberately removed ceremony from the critique skill, but the
GATE's required-snippet list was not updated — so decide the direction by
reading both sides:

- If the dropped prose was genuinely dead ceremony, the stale requirement
  lives in the GATE: update `scripts/check_skill_contracts.py`'s required
  snippets for the critique skill to match the skill's CURRENT real
  contract (this repo prefers deleting stale rules over re-adding
  ceremony — CLAUDE.md), and update the pinning test
  `tests/quality_gates/test_skill_contracts_validation.py` accordingly.
- If any required snippet still names live behavior the skill genuinely
  owes (e.g. the evidence-led mode is still implemented by
  `skills/public/critique/scripts/*` and merely undocumented), restore
  the minimal honest sentence in SKILL.md instead.

State which direction you took per snippet and why in your result. Do not
weaken the gate for any other skill.

Requirements:

- `python3 scripts/check_skill_contracts.py --repo-root .` green.
- `python3 -m pytest -q tests/quality_gates/test_skill_contracts_validation.py`
  green.
- The failing run-evals case ("representative skill contracts") passes:
  run the evals runner's skill-contract case if it is runnable standalone
  (find how `run-evals` invokes it in `scripts/run-quality.sh`) or state
  precisely why it will pass.
- `./scripts/check-docs.sh` stays green if SKILL.md changes (markdown
  gate covers it). Remember `skills/public/` is canonical and portable —
  no charness-specific hacks in skill prose.
- Do not touch `plugins/**` (parent syncs the export).
- Do not spawn descendant agents.

Scope: `skills/public/critique/**`, `scripts/check_skill_contracts.py`,
`tests/quality_gates/test_skill_contracts_validation.py`, `evals/**`.
Touch nothing else.

Stop: checks above green in your worktree. One coherent commit, prefix
`fix(critique):`. Final message: per-snippet direction decision with
rationale, commands + observed results.
