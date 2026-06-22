export const EVALUATION_CASES_SCHEMA = "cautilus.evaluation_cases.v1";
export const EVALUATION_INPUT_SCHEMA = "cautilus.evaluation_input.v1";
export const EVALUATION_OBSERVED_SCHEMA = "cautilus.evaluation_observed.v1";
export const INSTRUCTION_SURFACE_CASES_SCHEMA = "cautilus.instruction_surface_cases.v1";
export const INSTRUCTION_SURFACE_INPUTS_SCHEMA = "cautilus.instruction_surface_inputs.v1";
// Observed skill-evaluation packet consumed by cautilus `evaluate observation`
// (internal/runtime/skill_evaluation.go). The host runner emits one execution
// evaluation; cautilus applies declared thresholds (max_total_tokens /
// max_duration_ms) for runtime_budget_respect degrade and rolls outcome ->
// recommendation. Verified against cautilus skill-evaluation.md + the
// skill_evaluation_inputs.v1 example packets.
export const SKILL_EVALUATION_INPUTS_SCHEMA = "cautilus.skill_evaluation_inputs.v1";
// Consumed by cautilus `evaluate skill-experiment` (the deterministic scorer
// BuildSkillCloneExperimentReport in internal/runtime/skill_clone_experiment.go).
// Verified against the cautilus source at constants.go:69 (181ebef7).
export const SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA = "cautilus.skill_clone_experiment_input.v1";
