import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import process from "node:process";

import { INSTRUCTION_SURFACE_INPUTS_SCHEMA } from "./contract-versions.mjs";
import { normalizeInstructionSurfaceCaseSuite } from "./instruction-surface-case-suite.mjs";
import {
	artifactRef,
	backendFailureResult,
	materializeInstructionSurface,
	normalizeRoutingDecision,
	relativizeObservedPath,
} from "./instruction-surface-support.mjs";
import { extractClaudeTelemetry } from "./skill-test-telemetry.mjs";

export { normalizeInstructionSurfaceCaseSuite } from "./instruction-surface-case-suite.mjs";

const CODEX_SESSION_MODES = ["ephemeral", "persistent"];

const CLAUDE_CLI_ENV = {
	CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1",
	CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1",
	ENABLE_CLAUDEAI_MCP_SERVERS: "false",
	DISABLE_TELEMETRY: "1",
	DISABLE_AUTOUPDATER: "1",
	DISABLE_BUG_COMMAND: "1",
	DISABLE_ERROR_REPORTING: "1",
	CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL: "1",
};

function usage(exitCode = 0) {
	const text = [
		"Usage:",
		"  node ./scripts/agent-runtime/run-local-instruction-surface-test.mjs --repo-root <dir> --workspace <dir> --cases-file <file> --output-file <file> [--artifact-dir <dir>] [--backend codex_exec|claude_code|fixture] [--fixture-results-file <file>] [--sandbox read-only|workspace-write] [--timeout-ms <ms>] [--model <model>] [--reasoning-effort <level>] [--codex-model <model>] [--codex-reasoning-effort <level>] [--codex-session-mode ephemeral|persistent] [--codex-ephemeral true|false] [--codex-config <key=value>] [--claude-model <model>] [--claude-permission-mode <mode>] [--claude-allowed-tools <rules>]",
	].join("\n");
	const out = exitCode === 0 ? process.stdout : process.stderr;
	out.write(`${text}\n`);
	process.exit(exitCode);
}

function fail(message) {
	process.stderr.write(`${message}\n`);
	process.exit(1);
}

function readRequiredValue(argv, index, option) {
	const value = argv[index];
	if (!value) {
		fail(`Missing value for ${option}`);
	}
	return value;
}

function parsePositiveInteger(value, option) {
	const parsed = Number(value);
	if (!Number.isInteger(parsed) || parsed <= 0) {
		fail(`${option} must be a positive integer`);
	}
	return parsed;
}

function parseCodexSessionMode(value, option) {
	if (option === "--codex-ephemeral") {
		if (value === "true") {
			return "ephemeral";
		}
		if (value === "false") {
			return "persistent";
		}
		fail("--codex-ephemeral must be true or false");
	}
	if (CODEX_SESSION_MODES.includes(value)) {
		return value;
	}
	fail("--codex-session-mode must be ephemeral or persistent");
}

function defaultOptions() {
	return {
		repoRoot: process.cwd(),
		workspace: process.cwd(),
		casesFile: null,
		outputFile: null,
		artifactDir: null,
		backend: "codex_exec",
		fixtureResultsFile: null,
		sandbox: "read-only",
		timeoutMs: 120000,
		model: null,
		reasoningEffort: null,
		codexModel: null,
		codexReasoningEffort: null,
		codexSessionMode: "ephemeral",
		codexConfigOverrides: [],
		claudeModel: null,
		claudePermissionMode: null,
		claudeAllowedTools: null,
	};
}

const VALUE_OPTIONS = {
	"--repo-root": (options, value) => {
		options.repoRoot = resolve(value);
	},
	"--workspace": (options, value) => {
		options.workspace = resolve(value);
	},
	"--cases-file": (options, value) => {
		options.casesFile = resolve(value);
	},
	"--output-file": (options, value) => {
		options.outputFile = resolve(value);
	},
	"--artifact-dir": (options, value) => {
		options.artifactDir = resolve(value);
	},
	"--backend": (options, value) => {
		options.backend = value;
	},
	"--fixture-results-file": (options, value) => {
		options.fixtureResultsFile = resolve(value);
	},
	"--sandbox": (options, value) => {
		options.sandbox = value;
	},
	"--model": (options, value) => {
		options.model = value;
	},
	"--reasoning-effort": (options, value) => {
		options.reasoningEffort = value;
	},
	"--codex-model": (options, value) => {
		options.codexModel = value;
	},
	"--codex-reasoning-effort": (options, value) => {
		options.codexReasoningEffort = value;
	},
	"--codex-session-mode": (options, value) => {
		options.codexSessionMode = parseCodexSessionMode(value, "--codex-session-mode");
	},
	"--codex-config": (options, value) => {
		options.codexConfigOverrides.push(value);
	},
	"--codex-ephemeral": (options, value) => {
		options.codexSessionMode = parseCodexSessionMode(value, "--codex-ephemeral");
	},
	"--claude-model": (options, value) => {
		options.claudeModel = value;
	},
	"--claude-permission-mode": (options, value) => {
		options.claudePermissionMode = value;
	},
	"--claude-allowed-tools": (options, value) => {
		options.claudeAllowedTools = value;
	},
};

function applyArgument(options, argv, index) {
	const arg = argv[index];
	if (arg === "-h" || arg === "--help") {
		usage(0);
		return index;
	}
	if (arg === "--timeout-ms") {
		options.timeoutMs = parsePositiveInteger(readRequiredValue(argv, index + 1, arg), arg);
		return index + 1;
	}
	const applyValue = VALUE_OPTIONS[arg];
	if (!applyValue) {
		fail(`Unknown argument: ${arg}`);
	}
	applyValue(options, readRequiredValue(argv, index + 1, arg));
	return index + 1;
}

function parseArgs(argv) {
	const options = defaultOptions();
	for (let index = 0; index < argv.length; index += 1) {
		index = applyArgument(options, argv, index);
	}
	if (!options.casesFile) {
		fail("--cases-file is required");
	}
	if (!options.outputFile) {
		fail("--output-file is required");
	}
	if (!["codex_exec", "claude_code", "fixture"].includes(options.backend)) {
		fail("--backend must be codex_exec, claude_code, or fixture");
	}
	if (!["read-only", "workspace-write"].includes(options.sandbox)) {
		fail("--sandbox must be read-only or workspace-write");
	}
	if (!CODEX_SESSION_MODES.includes(options.codexSessionMode)) {
		fail("--codex-session-mode must be ephemeral or persistent");
	}
	if (options.backend === "fixture" && !options.fixtureResultsFile) {
		fail("--fixture-results-file is required when --backend fixture");
	}
	if (!options.artifactDir) {
		options.artifactDir = join(dirname(options.outputFile), "instruction-surface-test");
	}
	return options;
}

function readJson(path) {
	return JSON.parse(readFileSync(path, "utf-8"));
}

function assertObject(value, field) {
	if (!value || typeof value !== "object" || Array.isArray(value)) {
		throw new Error(`${field} must be an object`);
	}
	return value;
}

function assertString(value, field) {
	if (typeof value !== "string" || !value.trim()) {
		throw new Error(`${field} must be a non-empty string`);
	}
	return value;
}

function nullableObservedString(value, field) {
	if (value === undefined || value === null) {
		return null;
	}
	if (typeof value !== "string") {
		throw new Error(`${field} must be a string`);
	}
	return value.trim() ? value : null;
}

function normalizeStringArray(value, field) {
	if (!Array.isArray(value)) {
		throw new Error(`${field} must be an array`);
	}
	return value.map((entry, index) => assertString(entry, `${field}[${index}]`));
}

function normalizeObservedPathArray(workspace, value, field) {
	return normalizeStringArray(value, field).map((entry) => relativizeObservedPath(workspace, entry));
}

function baseSchema() {
	return {
		type: "object",
		additionalProperties: false,
		required: [
			"observationStatus",
			"blockerKind",
			"summary",
			"entryFile",
			"loadedInstructionFiles",
			"loadedSupportingFiles",
			"routingDecision",
		],
		properties: {
			observationStatus: {
				type: "string",
				enum: ["observed", "blocked"],
			},
			blockerKind: {
				type: "string",
			},
			summary: {
				type: "string",
			},
			entryFile: {
				type: "string",
			},
			loadedInstructionFiles: {
				type: "array",
				items: { type: "string" },
			},
			loadedSupportingFiles: {
				type: "array",
				items: { type: "string" },
			},
			routingDecision: {
				type: "object",
				additionalProperties: false,
				required: ["selectedSkill", "bootstrapHelper", "workSkill", "selectedSupport", "firstToolCall", "reasonSummary"],
				properties: {
					selectedSkill: { type: "string" },
					bootstrapHelper: { type: "string" },
					workSkill: { type: "string" },
					selectedSupport: { type: "string" },
					firstToolCall: { type: "string" },
					reasonSummary: { type: "string" },
				},
			},
		},
	};
}

function renderPrompt(evaluation) {
	const lines = [
		"You are being evaluated on whether the current repository instruction surface steers your first routing move honestly.",
		"Work inside the current repo checkout.",
		"Do not modify files.",
		"Do not read general repo docs, README files, or skill files unless the current instruction surface makes them necessary for the first routing decision.",
		"Before you begin the task, identify the first instruction file you intentionally used as the entry point.",
		"Only list instruction or supporting files that you actually read before or during the first routing decision.",
		"Report the first routing decision you made, including any bootstrap helper, the eventual durable work skill if one was chosen, any support helper, and the first tool call if one happened.",
		"Use `bootstrapHelper` for helpers such as discovery/bootstrap skills that precede the real work skill.",
		"If the repo instructions require a startup discovery or routing pass such as a mandatory `find-skills` check before broader exploration, record that helper in `bootstrapHelper` even when the eventual `workSkill` is already clear.",
		"Use `workSkill` for the durable task skill once it becomes clear.",
		"Keep `selectedSkill` as the single-lane alias when there is no meaningful bootstrap/work split; otherwise set it to the same value as `workSkill`.",
		"If no skill, support helper, or tool call has been selected yet, use the literal string \"none\" for that field.",
		"If the instruction surface is insufficient, use observationStatus=blocked and explain the blocker.",
		"Return only JSON matching the provided schema after you finish.",
	];
	if (evaluation.taskPath) {
		lines.push(`Task path in scope: ${evaluation.taskPath}`);
	}
	lines.push("", "User request:", evaluation.prompt);
	return `${lines.join("\n")}\n`;
}

export function codexArgs(options, schemaFile, outputFile) {
	const sessionMode = options.codexSessionMode ?? "ephemeral";
	const args = [
		"exec",
		"-C",
		options.workspace,
		"--sandbox",
		options.sandbox,
	];
	if (sessionMode === "ephemeral") {
		args.push("--ephemeral");
	}
	args.push(
		"--output-schema",
		schemaFile,
		"-o",
		outputFile,
	);
	if (options.codexModel ?? options.model) {
		args.push("--model", options.codexModel ?? options.model);
	}
	if (options.codexReasoningEffort ?? options.reasoningEffort) {
		args.push("-c", `model_reasoning_effort="${options.codexReasoningEffort ?? options.reasoningEffort}"`);
	}
	for (const override of options.codexConfigOverrides ?? []) {
		args.push("-c", override);
	}
	args.push("-");
	return args;
}

function normalizeExpectedFields(evaluation) {
	return {
		...(evaluation.taskPath ? { taskPath: evaluation.taskPath } : {}),
		...(evaluation.expectedEntryFile ? { expectedEntryFile: evaluation.expectedEntryFile } : {}),
		...(evaluation.requiredInstructionFiles.length > 0 ? { requiredInstructionFiles: evaluation.requiredInstructionFiles } : {}),
		...(evaluation.forbiddenInstructionFiles.length > 0 ? { forbiddenInstructionFiles: evaluation.forbiddenInstructionFiles } : {}),
		...(evaluation.requiredSupportingFiles.length > 0 ? { requiredSupportingFiles: evaluation.requiredSupportingFiles } : {}),
		...(evaluation.forbiddenSupportingFiles.length > 0 ? { forbiddenSupportingFiles: evaluation.forbiddenSupportingFiles } : {}),
		...(evaluation.expectedRouting ? { expectedRouting: evaluation.expectedRouting } : {}),
	};
}

function normalizeObservedCore(evaluation, observed, artifactRefs, startedAt) {
	return {
		evaluationId: evaluation.evaluationId,
		displayName: evaluation.displayName ?? evaluation.evaluationId,
		prompt: evaluation.prompt,
		startedAt,
		observationStatus: assertString(observed?.observationStatus, "observed.observationStatus"),
		summary: assertString(observed?.summary, "observed.summary"),
		loadedInstructionFiles: normalizeObservedPathArray(
			evaluation.workspace,
			observed?.loadedInstructionFiles,
			"observed.loadedInstructionFiles",
		),
		loadedSupportingFiles: normalizeObservedPathArray(
			evaluation.workspace,
			observed?.loadedSupportingFiles,
			"observed.loadedSupportingFiles",
		),
		routingDecision: normalizeRoutingDecision(observed?.routingDecision),
		artifactRefs,
	};
}

function normalizeObservedOptionalFields(workspace, observed, telemetry) {
	const optionalFields = {};
	const entryFile = nullableObservedString(observed?.entryFile, "observed.entryFile");
	if (entryFile) {
		optionalFields.entryFile = relativizeObservedPath(workspace, entryFile);
	}
	const blockerKind = nullableObservedString(observed?.blockerKind, "observed.blockerKind");
	if (blockerKind) {
		optionalFields.blockerKind = blockerKind;
	}
	if (telemetry) {
		optionalFields.telemetry = telemetry;
	}
	return optionalFields;
}

function claudeArgs(options) {
	const args = ["-p", "--no-session-persistence", "--output-format", "json", "--exclude-dynamic-system-prompt-sections"];
	if (options.claudeModel ?? options.model) {
		args.push("--model", options.claudeModel ?? options.model);
	}
	if (options.claudePermissionMode) {
		args.push("--permission-mode", options.claudePermissionMode);
	}
	if (options.claudeAllowedTools) {
		args.push("--allowedTools", options.claudeAllowedTools);
	}
	return args;
}

function renderClaudePrompt(evaluation, schema) {
	const basePrompt = renderPrompt(evaluation);
	return [
		basePrompt,
		"",
		"You MUST respond with ONLY a JSON object matching this schema - no markdown fences, no commentary:",
		"",
		JSON.stringify(schema, null, 2),
		"",
	].join("\n");
}

function extractJSON(text) {
	const fenced = text.match(/```(?:json)?\s*\n([\s\S]*?)\n\s*```/);
	if (fenced) {
		return JSON.parse(fenced[1]);
	}
	const braceMatch = text.match(/\{[\s\S]*\}/);
	if (braceMatch) {
		return JSON.parse(braceMatch[0]);
	}
	return JSON.parse(text);
}

function parseClaudeOutput(raw) {
	try {
		const parsed = JSON.parse(raw);
		if (parsed.result !== undefined) {
			return extractJSON(typeof parsed.result === "string" ? parsed.result : JSON.stringify(parsed.result));
		}
		return parsed;
	} catch {
		return extractJSON(raw);
	}
}

function normalizeObservedResult(evaluation, observed, artifactRefs, startedAt, telemetry = null) {
	const observationStatus = assertString(observed?.observationStatus, "observed.observationStatus");
	if (!["observed", "blocked"].includes(observationStatus)) {
		throw new Error("observed.observationStatus must be observed or blocked");
	}
	return {
		...normalizeObservedCore(evaluation, observed, artifactRefs, startedAt),
		...normalizeExpectedFields(evaluation),
		...normalizeObservedOptionalFields(evaluation.workspace, observed, telemetry),
	};
}

function fixtureObservedResult(evaluation, fixtureResults) {
	const observed = fixtureResults[evaluation.evaluationId];
	if (observed === undefined) {
		throw new Error(`fixtureResults.${evaluation.evaluationId} must exist`);
	}
	return assertObject(observed, `fixtureResults.${evaluation.evaluationId}`);
}

function runFixtureEvaluation(evaluation, fixtureResults, outputDir, startedAt) {
	const promptFile = join(outputDir, "prompt.md");
	writeFileSync(promptFile, renderPrompt(evaluation));
	const artifactRefs = [artifactRef("prompt", promptFile)];
	return normalizeObservedResult(evaluation, fixtureObservedResult(evaluation, fixtureResults), artifactRefs, startedAt);
}

function runCodexEvaluation(options, evaluation, outputDir, startedAt) {
	const promptFile = join(outputDir, "prompt.md");
	const schemaFile = join(outputDir, "schema.json");
	const outputFile = join(outputDir, "result.json");
	const stderrFile = join(outputDir, "result.stderr");
	const prompt = renderPrompt(evaluation);
	writeFileSync(promptFile, prompt);
	writeFileSync(schemaFile, `${JSON.stringify(baseSchema(), null, 2)}\n`);

	const result = spawnSync("codex", codexArgs(options, schemaFile, outputFile), {
		cwd: options.workspace,
		encoding: "utf-8",
		env: {
			...process.env,
			PATH: `${join(options.repoRoot, "bin")}:${process.env.PATH ?? ""}`,
		},
		input: prompt,
		timeout: options.timeoutMs,
	});
	writeFileSync(stderrFile, result.stderr ?? "");
	const artifactRefs = [artifactRef("prompt", promptFile), artifactRef("schema", schemaFile), artifactRef("stderr", stderrFile)];
	if (result.error?.code === "ETIMEDOUT") {
		return normalizeObservedResult(
			evaluation,
			backendFailureResult(`The codex_exec runner timed out after ${options.timeoutMs}ms.`),
			artifactRefs,
			startedAt,
		);
	}
	if (result.status !== 0) {
		return normalizeObservedResult(
			evaluation,
			backendFailureResult(`The codex_exec runner exited with status ${result.status}.`),
			artifactRefs,
			startedAt,
		);
	}
	let observed;
	try {
		observed = readJson(outputFile);
	} catch (error) {
		return normalizeObservedResult(
			evaluation,
			backendFailureResult(`The codex_exec runner did not produce valid JSON: ${error.message}`),
			artifactRefs,
			startedAt,
		);
	}
	artifactRefs.push(artifactRef("result", outputFile));
	const model = options.codexModel ?? options.model;
	const sessionMode = options.codexSessionMode ?? "ephemeral";
	const telemetry = {
		...(model ? { model } : {}),
		session_mode: sessionMode,
	};
	return normalizeObservedResult(evaluation, observed, artifactRefs, startedAt, telemetry);
}

function runClaudeEvaluation(options, evaluation, outputDir, startedAt) {
	const promptFile = join(outputDir, "prompt.md");
	const outputFile = join(outputDir, "result.json");
	const rawFile = join(outputDir, "result.raw");
	const stderrFile = join(outputDir, "result.stderr");
	const schema = baseSchema();
	const prompt = renderClaudePrompt(evaluation, schema);
	writeFileSync(promptFile, prompt);

	const result = spawnSync("claude", claudeArgs(options), {
		cwd: options.workspace,
		encoding: "utf-8",
		env: {
			...process.env,
			...CLAUDE_CLI_ENV,
			PATH: `${join(options.repoRoot, "bin")}:${process.env.PATH ?? ""}`,
		},
		input: prompt,
		timeout: options.timeoutMs,
	});
	writeFileSync(stderrFile, result.stderr ?? "");
	writeFileSync(rawFile, result.stdout ?? "");
	const artifactRefs = [artifactRef("prompt", promptFile), artifactRef("raw", rawFile), artifactRef("stderr", stderrFile)];
	if (result.error?.code === "ETIMEDOUT") {
		return normalizeObservedResult(
			evaluation,
			backendFailureResult(`The claude_code runner timed out after ${options.timeoutMs}ms.`),
			artifactRefs,
			startedAt,
		);
	}
	if (result.status !== 0) {
		return normalizeObservedResult(
			evaluation,
			backendFailureResult(`The claude_code runner exited with status ${result.status}.`),
			artifactRefs,
			startedAt,
		);
	}
	let observed;
	try {
		observed = parseClaudeOutput(result.stdout ?? "");
	} catch (error) {
		return normalizeObservedResult(
			evaluation,
			backendFailureResult(`The claude_code runner did not produce valid JSON: ${error.message}`),
			artifactRefs,
			startedAt,
		);
	}
	writeFileSync(outputFile, `${JSON.stringify(observed, null, 2)}\n`);
	artifactRefs.push(artifactRef("result", outputFile));
	const telemetry = extractClaudeTelemetry(result.stdout ?? "", options);
	return normalizeObservedResult(evaluation, observed, artifactRefs, startedAt, telemetry);
}

function evaluateSurface(options, evaluation, fixtureResults) {
	const caseDir = join(options.artifactDir, evaluation.evaluationId);
	mkdirSync(caseDir, { recursive: true });
	const materialized = materializeInstructionSurface(options, evaluation, caseDir);
	const startedAt = new Date().toISOString();
	const observedEvaluation = {
		...evaluation,
		workspace: options.workspace,
	};
	try {
		let observed;
		if (options.backend === "fixture") {
			observed = runFixtureEvaluation(observedEvaluation, fixtureResults, caseDir, startedAt);
		} else if (options.backend === "claude_code") {
			observed = runClaudeEvaluation(options, observedEvaluation, caseDir, startedAt);
		} else {
			observed = runCodexEvaluation(options, observedEvaluation, caseDir, startedAt);
		}
		return {
			...observed,
			instructionSurface: materialized.instructionSurface,
			artifactRefs: [...(observed.artifactRefs ?? []), ...materialized.artifactRefs],
		};
	} finally {
		materialized.restore();
	}
}

export function buildObservedInstructionSurfaceInput(options) {
	const caseSuite = normalizeInstructionSurfaceCaseSuite(readJson(options.casesFile));
	const fixtureResults = options.backend === "fixture" ? readJson(options.fixtureResultsFile) : {};
	const evaluations = caseSuite.evaluations.map((evaluation) => evaluateSurface(options, evaluation, fixtureResults));
	return {
		schemaVersion: INSTRUCTION_SURFACE_INPUTS_SCHEMA,
		suiteId: caseSuite.suiteId,
		suiteDisplayName: caseSuite.suiteDisplayName,
		evaluations,
	};
}

function main() {
	const options = parseArgs(process.argv.slice(2));
	mkdirSync(options.artifactDir, { recursive: true });
	const packet = buildObservedInstructionSurfaceInput(options);
	writeFileSync(options.outputFile, `${JSON.stringify(packet, null, 2)}\n`);
}

if (import.meta.url === new URL(process.argv[1], "file:").href) {
	main();
}
