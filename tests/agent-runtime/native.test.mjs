import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import {
	CODEX_AUTH_MODES,
	CODEX_HOME_MODES,
	codexArgs,
	codexFailureBlockerKind,
	prepareCodexRuntimeEnv,
} from "../../scripts/agent-runtime/codex-eval-runtime.mjs";
import {
	EVALUATION_CASES_SCHEMA,
	EVALUATION_INPUT_SCHEMA,
	EVALUATION_OBSERVED_SCHEMA,
	INSTRUCTION_SURFACE_CASES_SCHEMA,
	INSTRUCTION_SURFACE_INPUTS_SCHEMA,
} from "../../scripts/agent-runtime/contract-versions.mjs";
import { normalizeInstructionSurfaceCaseSuite } from "../../scripts/agent-runtime/instruction-surface-case-suite.mjs";
import {
	backendFailureResult,
	normalizeRoutingDecision,
	relativizeObservedPath,
} from "../../scripts/agent-runtime/instruction-surface-support.mjs";
import {
	buildObservedInstructionSurfaceInput,
	codexEnvironment,
	runClaudeEvaluation,
	runCodexEvaluation,
} from "../../scripts/agent-runtime/run-local-eval-test.mjs";
import { extractClaudeTelemetry } from "../../scripts/agent-runtime/skill-test-telemetry.mjs";

function withTempDir(fn) {
	const path = mkdtempSync(join(tmpdir(), "charness-agent-runtime-test-"));
	try {
		return fn(path);
	} finally {
		rmSync(path, { recursive: true, force: true });
	}
}

function writeJson(path, payload) {
	writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`, "utf-8");
}

test("contract version constants are stable", () => {
	assert.equal(EVALUATION_CASES_SCHEMA, "cautilus.evaluation_cases.v1");
	assert.equal(EVALUATION_INPUT_SCHEMA, "cautilus.evaluation_input.v1");
	assert.equal(EVALUATION_OBSERVED_SCHEMA, "cautilus.evaluation_observed.v1");
	assert.equal(INSTRUCTION_SURFACE_CASES_SCHEMA, "cautilus.instruction_surface_cases.v1");
	assert.equal(INSTRUCTION_SURFACE_INPUTS_SCHEMA, "cautilus.instruction_surface_inputs.v1");
});

test("normalizes legacy evaluation input into case suite", () => {
	const suite = normalizeInstructionSurfaceCaseSuite({
		schemaVersion: EVALUATION_INPUT_SCHEMA,
		surface: "dev",
		preset: "repo",
		suiteId: "legacy",
		cases: [
			{
				caseId: "routes-quality",
				prompt: "Run validation.",
				expectedRouting: { bootstrapHelper: "find-skills", workSkill: "quality" },
			},
		],
	});

	assert.equal(suite.suiteId, "legacy");
	assert.equal(suite.suiteDisplayName, "legacy");
	assert.deepEqual(suite.evaluations[0].expectedRouting, {
		bootstrapHelper: "find-skills",
		workSkill: "quality",
	});
});

test("rejects malformed instruction surface cases", () => {
	assert.throws(
		() =>
			normalizeInstructionSurfaceCaseSuite({
				schemaVersion: EVALUATION_CASES_SCHEMA,
				suiteId: "bad",
				evaluations: [{ evaluationId: "bad", prompt: "x", expectedRouting: {} }],
			}),
		/evaluations\[0\]\.expectedRouting must declare at least one expectation field/,
	);
});

test("normalizes routing decisions and observed paths", () => {
	assert.deepEqual(
		normalizeRoutingDecision({
			selectedSkill: "charness:quality",
			bootstrapHelper: "none selected",
			workSkill: "charness:quality",
			selectedSupport: "none",
			firstToolCall: "exec_command",
			reasonSummary: "Uses quality.",
		}),
		{
			selectedSkill: "quality",
			bootstrapHelper: "none",
			workSkill: "quality",
			selectedSupport: "none",
			firstToolCall: "functions.exec_command",
			reasonSummary: "Uses quality.",
		},
	);

	assert.equal(relativizeObservedPath("/tmp/workspace", "[AGENTS.md](/tmp/workspace/AGENTS.md)"), "AGENTS.md");
	assert.equal(relativizeObservedPath("/tmp/workspace", "/tmp/workspace/skills/public/quality/SKILL.md"), "skills/public/quality/SKILL.md");
	assert.equal(relativizeObservedPath("/tmp/workspace", "/outside/README.md"), "/outside/README.md");
	assert.equal(backendFailureResult("boom").routingDecision.firstToolCall, "none");
});

test("codex runtime args and auth preflight are deterministic", () => {
	assert.deepEqual(CODEX_HOME_MODES, ["isolated", "inherit"]);
	assert.deepEqual(CODEX_AUTH_MODES, ["inherit", "env", "none"]);
	assert.deepEqual(
		codexArgs(
			{
				workspace: "/tmp/work",
				sandbox: "read-only",
				codexHomeMode: "isolated",
				codexSessionMode: "persistent",
				codexModel: "gpt-test",
				codexReasoningEffort: "low",
				codexConfigOverrides: ["sandbox_workspace_write.network_access=false"],
			},
			"/tmp/schema.json",
			"/tmp/output.json",
		),
		[
			"exec",
			"-C",
			"/tmp/work",
			"--sandbox",
			"read-only",
			"--ignore-user-config",
			"--output-schema",
			"/tmp/schema.json",
			"-o",
			"/tmp/output.json",
			"--model",
			"gpt-test",
			"-c",
			'model_reasoning_effort="low"',
			"-c",
			"sandbox_workspace_write.network_access=false",
			"-",
		],
	);

	const missing = prepareCodexRuntimeEnv(
		{ codexHomeMode: "inherit", codexAuthMode: "env" },
		{ PATH: "/bin" },
	);
	assert.equal(missing.preflightBlocker.blockerKind, "runner_auth_missing");
	assert.equal(codexFailureBlockerKind("401 Unauthorized: missing bearer or basic authentication"), "runner_auth_missing");
	assert.equal(codexFailureBlockerKind("process exited 2"), "runner_execution_failed");
});

test("isolated codex environment can use a custom home without inheriting host config", () =>
	withTempDir((root) => {
		const sourceHome = join(root, "source-home");
		const customHome = join(root, "custom-home");
		mkdirSync(sourceHome, { recursive: true });
		writeFileSync(join(sourceHome, "auth.json"), '{"token":"test"}\n', "utf-8");
		writeFileSync(join(sourceHome, "config.toml"), "model = 'stale'\n", "utf-8");
		const originalCodexHome = process.env.CODEX_HOME;
		const originalApiKey = process.env.OPENAI_API_KEY;
		process.env.CODEX_HOME = sourceHome;
		delete process.env.OPENAI_API_KEY;

		try {
			const runtime = codexEnvironment(
				{
					repoRoot: join(root, "repo"),
					codexHomeMode: "isolated",
					codexHome: customHome,
					codexAuthMode: "inherit",
				},
				join(root, "output"),
			);
			assert.equal(runtime.env.CODEX_HOME, customHome);
			assert.equal(runtime.telemetry.codex_home_mode, "custom");
			assert.equal(runtime.telemetry.codex_home_isolated, true);
			assert.equal(readFileSync(join(customHome, "auth.json"), "utf-8"), '{"token":"test"}\n');
			assert.equal(existsSync(join(customHome, "config.toml")), false);
		} finally {
			if (originalCodexHome === undefined) {
				delete process.env.CODEX_HOME;
			} else {
				process.env.CODEX_HOME = originalCodexHome;
			}
			if (originalApiKey === undefined) {
				delete process.env.OPENAI_API_KEY;
			} else {
				process.env.OPENAI_API_KEY = originalApiKey;
			}
		}
	}));

test("builds observed instruction-surface packets with fixture backend", () =>
	withTempDir((root) => {
		const workspace = join(root, "workspace");
		const artifactDir = join(root, "artifacts");
		const casesFile = join(root, "cases.json");
		const fixtureFile = join(root, "fixture-results.json");
		const outputFile = join(root, "observed.json");
		mkdirSync(workspace, { recursive: true });
		writeFileSync(join(workspace, "CLAUDE.md"), "# stale\n", "utf-8");
		writeJson(casesFile, {
			schemaVersion: EVALUATION_CASES_SCHEMA,
			suiteId: "agent-runtime",
			suiteDisplayName: "Agent Runtime",
			evaluations: [
				{
					evaluationId: "route-quality",
					displayName: "Route quality",
					prompt: "Validate this repo.",
					expectedEntryFile: "AGENTS.md",
					instructionSurface: {
						surfaceLabel: "inline",
						files: [{ path: "AGENTS.md", content: "# instructions\n" }],
					},
					requiredConcepts: [
						{
							id: "quality-routing",
							terms: ["quality", "validation"],
						},
					],
					expectedRouting: {
						bootstrapHelper: "find-skills",
						workSkill: "quality",
					},
				},
			],
		});
		writeJson(fixtureFile, {
			"route-quality": {
				observationStatus: "observed",
				blockerKind: "",
				summary: "The request routes to quality validation.",
				entryFile: `[AGENTS.md](${join(workspace, "AGENTS.md")})`,
				loadedInstructionFiles: [join(workspace, "AGENTS.md")],
				loadedSupportingFiles: [],
				routingDecision: {
					selectedSkill: "charness:quality",
					bootstrapHelper: "find-skills",
					workSkill: "charness:quality",
					selectedSupport: "none",
					firstToolCall: "exec_command",
					reasonSummary: "Use quality for validation.",
				},
			},
		});

		const packet = buildObservedInstructionSurfaceInput({
			repoRoot: process.cwd(),
			workspace,
			casesFile,
			outputFile,
			artifactDir,
			backend: "fixture",
			fixtureResultsFile: fixtureFile,
		});

		assert.equal(packet.schemaVersion, EVALUATION_OBSERVED_SCHEMA);
		assert.equal(packet.suiteId, "agent-runtime");
		const evaluation = packet.evaluations[0];
		assert.equal(evaluation.entryFile, "AGENTS.md");
		assert.deepEqual(evaluation.loadedInstructionFiles, ["AGENTS.md"]);
		assert.equal(evaluation.routingDecision.firstToolCall, "functions.exec_command");
		assert.equal(evaluation.conceptAssertions[0].status, "passed");
		assert.equal(evaluation.instructionSurface.surfaceLabel, "inline");
		assert.equal(readFileSync(join(workspace, "CLAUDE.md"), "utf-8"), "# stale\n");
		assert.equal(existsSync(join(workspace, "AGENTS.md")), false);
	}));

test("extracts compact Claude telemetry", () => {
	assert.deepEqual(
		extractClaudeTelemetry(
			{
				usage: {
					input_tokens: 10,
					cache_creation_input_tokens: 2,
					cache_read_input_tokens: 3,
					output_tokens: 5,
				},
				total_cost_usd: 0.0123,
			},
			{ claudeModel: "claude-test" },
		),
		{
			provider: "anthropic",
			model: "claude-test",
			prompt_tokens: 15,
			completion_tokens: 5,
			total_tokens: 20,
			cost_usd: 0.0123,
		},
	);
	assert.equal(extractClaudeTelemetry("not json"), null);
});

test("extracts Claude telemetry from JSON envelopes and model fallback", () => {
	assert.deepEqual(
		extractClaudeTelemetry(
			JSON.stringify({
				usage: {
					input_tokens: 1,
					cache_creation_input_tokens: 2,
					cache_read_input_tokens: 3,
					output_tokens: 4,
				},
				total_cost_usd: 0.5,
			}),
			{ model: "fallback-model" },
		),
		{
			provider: "anthropic",
			model: "fallback-model",
			prompt_tokens: 6,
			completion_tokens: 4,
			total_tokens: 10,
			cost_usd: 0.5,
		},
	);

	assert.equal(extractClaudeTelemetry("[]"), null);
	assert.equal(extractClaudeTelemetry("42"), null);
});

test("omits invalid Claude telemetry counters without fabricating totals", () => {
	const arrayUsage = [];
	arrayUsage.input_tokens = 9;
	arrayUsage.output_tokens = 9;

	assert.deepEqual(
		extractClaudeTelemetry({
			usage: {
				input_tokens: -1,
				cache_creation_input_tokens: 1.5,
				cache_read_input_tokens: "3",
				output_tokens: -2,
			},
			total_cost_usd: -0.1,
		}),
		{
			provider: "anthropic",
		},
	);
	assert.deepEqual(extractClaudeTelemetry({ usage: arrayUsage }), {
		provider: "anthropic",
	});
	assert.deepEqual(extractClaudeTelemetry({ usage: null }), {
		provider: "anthropic",
	});
	assert.deepEqual(extractClaudeTelemetry({ total_cost_usd: "0" }), {
		provider: "anthropic",
	});
	assert.deepEqual(extractClaudeTelemetry({ total_cost_usd: Number.POSITIVE_INFINITY }), {
		provider: "anthropic",
	});

	assert.deepEqual(
		extractClaudeTelemetry({
			usage: {
				input_tokens: 2,
				output_tokens: null,
			},
		}),
		{
			provider: "anthropic",
			prompt_tokens: 2,
			total_tokens: 2,
		},
	);

	assert.deepEqual(
		extractClaudeTelemetry({
			usage: {
				input_tokens: null,
				output_tokens: 5,
			},
		}),
		{
			provider: "anthropic",
			completion_tokens: 5,
			total_tokens: 5,
		},
	);

	assert.deepEqual(
		extractClaudeTelemetry({
			usage: {
				output_tokens: 0,
			},
			total_cost_usd: 0,
		}),
		{
			provider: "anthropic",
			completion_tokens: 0,
			total_tokens: 0,
			cost_usd: 0,
		},
	);
});

// The codex/claude subprocess boundaries take an injectable `spawn` seam (default
// spawnSync) so the runner orchestration — success normalization, non-zero exit,
// and timeout handling — is reachable without spawning a real agent CLI. These
// tests exercise that seam.
function evaluationFixture(workspace) {
	return {
		evaluationId: "eval-seam",
		displayName: "Seam evaluation",
		prompt: "route the request",
		workspace,
		requiredConcepts: [],
		requiredInstructionFiles: [],
		forbiddenInstructionFiles: [],
		requiredSupportingFiles: [],
		forbiddenSupportingFiles: [],
	};
}

function observedFixture() {
	return {
		observationStatus: "observed",
		blockerKind: "",
		summary: "selected the quality skill",
		entryFile: "",
		loadedInstructionFiles: [],
		loadedSupportingFiles: [],
		routingDecision: {
			selectedSkill: "quality",
			bootstrapHelper: "find-skills",
			workSkill: "quality",
			selectedSupport: "none",
			firstToolCall: "none",
			reasonSummary: "instruction surface routed to quality",
		},
	};
}

const SEAM_STARTED_AT = "2026-01-01T00:00:00.000Z";

function recordingSpawn(response) {
	const calls = [];
	const spawn = (command, args, spawnOptions) => {
		calls.push({ command, args, spawnOptions });
		return typeof response === "function" ? response(command, args, spawnOptions) : response;
	};
	return { calls, spawn };
}

test("claude runner success path is reachable through the injected spawn seam", () => {
	withTempDir((dir) => {
		const options = { workspace: dir, repoRoot: dir, timeoutMs: 1000, claudeModel: "claude-test" };
		const stdout = JSON.stringify({ result: JSON.stringify(observedFixture()) });
		const { calls, spawn } = recordingSpawn({ status: 0, stdout, stderr: "" });

		const result = runClaudeEvaluation(options, evaluationFixture(dir), dir, SEAM_STARTED_AT, spawn);

		assert.equal(calls.length, 1);
		assert.equal(calls[0].command, "claude");
		assert.ok(calls[0].args.includes("-p"));
		assert.equal(result.observationStatus, "observed");
		assert.equal(result.summary, "selected the quality skill");
		assert.equal(result.evaluationId, "eval-seam");
		assert.equal(result.routingDecision.workSkill, "quality");
	});
});

test("claude runner parses a natural stream-json transcript and persists it", () => {
	withTempDir((dir) => {
		const options = { workspace: dir, repoRoot: dir, timeoutMs: 1000, claudeModel: "claude-test" };
		// Newline-delimited stream-json: an init event, a real tool call, then the
		// terminal result event carrying the routing JSON plus usage/cost.
		const streamLines = [
			JSON.stringify({ type: "system", subtype: "init", session_id: "s1" }),
			JSON.stringify({
				type: "assistant",
				message: { content: [{ type: "tool_use", name: "Read", input: { file_path: join(dir, "skills/x/SKILL.md") } }] },
			}),
			JSON.stringify({
				type: "result",
				subtype: "success",
				result: JSON.stringify(observedFixture()),
				usage: { input_tokens: 7, output_tokens: 3 },
				total_cost_usd: 0.02,
			}),
		];
		const stdout = `${streamLines.join("\n")}\n`;
		const { calls, spawn } = recordingSpawn({ status: 0, stdout, stderr: "" });

		const result = runClaudeEvaluation(options, evaluationFixture(dir), dir, SEAM_STARTED_AT, spawn);

		assert.ok(calls[0].args.includes("stream-json"), "uses --output-format stream-json");
		assert.ok(calls[0].args.includes("--verbose"), "stream-json requires --verbose under --print");
		assert.equal(result.observationStatus, "observed");
		assert.equal(result.summary, "selected the quality skill");
		assert.equal(result.routingDecision.workSkill, "quality");
		assert.equal(result.telemetry.completion_tokens, 3);
		assert.equal(result.telemetry.cost_usd, 0.02);
		const transcript = readFileSync(join(dir, "transcript.jsonl"), "utf-8");
		assert.equal(transcript, stdout, "natural stream-json transcript is persisted verbatim");
		assert.match(transcript, /"type":"result"/);
	});
});

test("claude runner non-zero exit becomes a blocked result via the seam", () => {
	withTempDir((dir) => {
		const options = { workspace: dir, repoRoot: dir, timeoutMs: 1000 };
		const { spawn } = recordingSpawn({ status: 2, stdout: "", stderr: "boom" });

		const result = runClaudeEvaluation(options, evaluationFixture(dir), dir, SEAM_STARTED_AT, spawn);

		assert.equal(result.observationStatus, "blocked");
		assert.match(result.summary, /exited with status 2/);
	});
});

test("claude runner timeout becomes a blocked result via the seam", () => {
	withTempDir((dir) => {
		const options = { workspace: dir, repoRoot: dir, timeoutMs: 1000 };
		const { spawn } = recordingSpawn({ error: { code: "ETIMEDOUT" }, stdout: "", stderr: "" });

		const result = runClaudeEvaluation(options, evaluationFixture(dir), dir, SEAM_STARTED_AT, spawn);

		assert.equal(result.observationStatus, "blocked");
		assert.match(result.summary, /timed out/);
	});
});

test("codex runner success path is reachable through the injected spawn seam", () => {
	withTempDir((dir) => {
		const options = {
			workspace: dir,
			repoRoot: dir,
			timeoutMs: 1000,
			codexHomeMode: "inherit",
			codexAuthMode: "inherit",
			codexModel: "gpt-test",
		};
		const { calls, spawn } = recordingSpawn(() => {
			writeJson(join(dir, "result.json"), observedFixture());
			return { status: 0, stdout: "", stderr: "" };
		});

		const result = runCodexEvaluation(options, evaluationFixture(dir), dir, SEAM_STARTED_AT, spawn);

		assert.equal(calls.length, 1);
		assert.equal(calls[0].command, "codex");
		assert.equal(result.observationStatus, "observed");
		assert.equal(result.summary, "selected the quality skill");
		assert.equal(result.evaluationId, "eval-seam");
	});
});

test("codex runner non-zero exit becomes a blocked result via the seam", () => {
	withTempDir((dir) => {
		const options = {
			workspace: dir,
			repoRoot: dir,
			timeoutMs: 1000,
			codexHomeMode: "inherit",
			codexAuthMode: "inherit",
		};
		const { spawn } = recordingSpawn({ status: 3, stdout: "", stderr: "exploded" });

		const result = runCodexEvaluation(options, evaluationFixture(dir), dir, SEAM_STARTED_AT, spawn);

		assert.equal(result.observationStatus, "blocked");
		assert.match(result.summary, /exited with status 3/);
	});
});
