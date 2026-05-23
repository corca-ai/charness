# Critique Closeout: Handoff Open-Issue Sweep (#198, #202-#206)

Date: 2026-05-23

## Execution

Five bounded fresh-eye subagent passes per the repo `Subagent Delegation`
contract (parent-delegated), matching the goal's design→impl→pattern→RCA→final
shape:

- Design critique (`general-purpose` subagent) ran on the #202-#206 proposals
  before any code landed: #204 already-shipped (cross-ref only), #205 clean
  mirror, #203 genuinely missing (per-session-file target), #202
  partially-shipped (labels prose exists; milestones the real gap, must route
  through `selected_backend`), #206 risky (heuristic meta-validator → downgrade
  to advisory).
- RCA (`general-purpose` subagent) on the two mutation issues: #207 is
  working-as-designed fail-closed (`check_mutation_score.py:200-207` requires
  `changed_scope_gap_count == 0`); #198 is a coverage-attribution gap, not a
  missing test.
- Pattern scan (folded into design + impl passes) surfaced the
  critique↔shared follow-up-grammar duplication.
- Post-impl critique (`general-purpose` subagent) on the full diff: SHIP, one
  should-fix (the dedup), verified the debug→shared refactor byte-for-byte.
- Final closeout critique (`general-purpose` subagent) on the tightened diff:
  SHIP, 13/13 follow-up edge cases behavior-equivalent, import-safe, gate green.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

n/a (no adapter sections)

## Target

`references/code-critique.md` substrate — post-impl review of a multi-skill +
validator + test change closing six issues.

## Change

- #198 (`tests/quality_gates/test_packaging_validation.py`): immutability test
  loads a fresh `eval_registry` copy from source (registered+popped in
  `sys.modules`) so the `@dataclass(frozen=True)` line re-executes under the
  test's coverage context; the line-6 mutant is now attributed to its kill test.
- #202 (`skills/public/issue/`): `issue_tool.py resolve-milestone` guard assigns
  only existing milestones and never invents; prose milestone rule mirrors the
  existing label rule and routes through `selected_backend`.
- #203 (`skills/public/retro/`): opt-in `## Sibling Search` for transferable
  waste patterns + `validate_retro_artifact.py`; the follow-up grammar was
  factored into `scripts/artifact_validator.py` and shared with `debug`.
- #204 (`skills/public/create-cli/`): `Lint Gate` closeout field + cross-ref to
  `impl/references/verification-ladder.md`; no new validator.
- #205 (`skills/public/ideation/`): opt-in `## Structured Questions` +
  `validate_ideation_artifact.py` (urgency/depends-on/action enums).
- #206 (`skills/public/create-skill/`): "Closeout Schema Rule" +
  advisory-only `validate_skill_output_schemas.py` (report, exit 0, un-wired).

## Findings

The unifying theme repeated from #199/#201: structured output without a
section-gated validator is debt the caller re-pays. The new validators are all
opt-in + changed-paths-default so historical artifacts and prose-only output
stay valid. The design critique's biggest correction was downgrading #206's
meta-validator from a hard gate to advisory (a heuristic over freeform Output
Shape prose would false-fire).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/validate_critique_artifacts.py:186 | action: fix | note: `_is_valid_followup_value` duplicated the shared grammar; now delegates to `artifact_validator.is_valid_followup_tail`, dogfooding #206's reuse rule
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/create-cli/SKILL.md | action: fix | note: initial `$SKILL_DIR` Bootstrap survey block tripped bootstrap-vars + long_core; folded into step 6 + quality-gates.md cross-ref
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/SKILL.md:69 | action: fix | note: line-wrap broke the required `Do not ask for approval...` contract snippet; restored to one line
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/artifact_validator.py:91 | action: fix | note: shared `validate_sibling_followups` parameterized by boundary headings + source reference so debug and retro enforce one grammar
- F5 | bin: valid-but-defer | evidence: strong | ref: scripts/check_mutation_score.py:200 | action: document | follow-up: https://github.com/corca-ai/charness/issues/207 | note: #207 fail-closed is working as designed; no code fix — a no-mutable-line changed-file allowlist would weaken a just-hardened guarantee; recommend by-design close
- F6 | bin: over-worry | evidence: weak | ref: skills/public/issue/scripts/issue_tool.py:233 | action: document | note: `resolve_milestone` strips `requested` but not `existing` titles; biases toward never-inventing, acceptable since backend titles are authoritative
- F7 | bin: over-worry | evidence: weak | ref: scripts/validate_ideation_artifact.py | action: defer | note: no `charness-artifacts/ideation/` home today; validator is a safe no-op until one lands (same posture as deferred #200 impl-artifact validator)

## Deliberately Not Doing

- Hard-gating `validate_skill_output_schemas.py`: rejected per design critique;
  the "needs a validator?" judgment is semantic, not lexical, so a heuristic
  hard gate would be noise. Advisory `--report` only.
- A `validate_ideation_artifact.py` standing artifact directory: not created;
  the validator stays a safe no-op until ideation gains a durable home.
- Lowering the mutation threshold or adding a no-mutable-line allowlist for
  #207: rejected; it would weaken the fail-closed scope-gap guarantee.

## Next Move

- Commit closes #198 #202 #203 #204 #205 #206 on push (auto-close keywords).
- #207 needs an RCA comment + by-design close (external action; surfaced to the
  operator rather than performed unprompted).
- Push and handoff update surfaced for operator decision.
