#!/usr/bin/env node

// Keystone of the cautilus skill-experiment harness: parse a natural stream-json
// transcript (produced by run-local-eval-test.mjs's claude_code backend) into a
// `cautilus.skill_clone_experiment_input.v1` JSON that the deterministic cautilus
// scorer (`evaluate skill-experiment`) reads as `--input`.
//
// The scorer (cautilus internal/runtime/skill_clone_experiment.go @ 181ebef7) does
// NOT analyze transcripts — it reads each arm's host-captured `output.sourceRefs`
// plus `output.text` and `status`, then computes a source-coverage delta against
// the declared `sourceCoverageObligations`. This extractor is the bridge: it
// recovers `output.sourceRefs` from the agent's real tool calls in the transcript.
//
// Contract recovered from source (do not trust prose):
// - input requires schemaVersion / experimentId / taskPacket / baseline / variant.
// - taskPacket must carry >=1 of: path, sourceRef, schemaVersion, summary.
// - a run merges top-level `sourceRefs` with `output.sourceRefs` (unique-sorted);
//   we emit them under `output.sourceRefs`.
// - status is one of: passed, failed, blocked, degraded (default passed).

import { readFileSync, writeFileSync } from "node:fs";
import { isAbsolute, relative, resolve, sep } from "node:path";
import process from "node:process";

import { SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA } from "./contract-versions.mjs";

// Tool calls whose input names a concrete file the agent consulted or touched.
// `Read` is the canonical "consulted this reference" signal; Edit/Write/Notebook
// cover files mutated by a non-route task. Glob/Grep are intentionally excluded:
// they take patterns or directories, not a single resolved file, so counting
// them would inflate coverage with paths the agent never actually opened.
const SOURCE_REF_TOOL_PATH_KEYS = {
	Read: "file_path",
	Edit: "file_path",
	Write: "file_path",
	NotebookEdit: "notebook_path",
};

export function parseTranscriptEvents(raw) {
	const events = [];
	for (const line of String(raw).split("\n")) {
		const trimmed = line.trim();
		if (!trimmed) {
			continue;
		}
		try {
			events.push(JSON.parse(trimmed));
		} catch {
			// Non-JSON noise (e.g. a stray log line) is skipped, not fatal.
		}
	}
	return events;
}

function toolUseBlocks(event) {
	if (!event || typeof event !== "object") {
		return [];
	}
	const content = Array.isArray(event.message?.content)
		? event.message.content
		: Array.isArray(event.content)
			? event.content
			: [];
	return content.filter((block) => block && typeof block === "object" && block.type === "tool_use");
}

function relativizeRef(rawPath, workspaceRoot) {
	const value = String(rawPath).trim();
	if (!value) {
		return null;
	}
	if (!workspaceRoot || !isAbsolute(value)) {
		// Already repo-relative (or no root to relativize against): normalize seps.
		return value.split(sep).join("/");
	}
	const root = resolve(workspaceRoot);
	const rel = relative(root, value);
	// A path outside the workspace stays absolute so coverage stays honest about
	// what was read rather than silently inventing a repo-relative ref.
	if (!rel || rel.startsWith("..") || isAbsolute(rel)) {
		return value.split(sep).join("/");
	}
	return rel.split(sep).join("/");
}

export function collectSourceRefs(events, { workspaceRoot = null } = {}) {
	const refs = new Set();
	for (const event of events) {
		for (const block of toolUseBlocks(event)) {
			const pathKey = SOURCE_REF_TOOL_PATH_KEYS[block.name];
			if (!pathKey) {
				continue;
			}
			const ref = relativizeRef(block.input?.[pathKey] ?? "", workspaceRoot);
			if (ref) {
				refs.add(ref);
			}
		}
	}
	return [...refs].sort();
}

export function transcriptCwd(events) {
	// The system/init event carries claude's own `cwd`. Tool-call file_paths are
	// emitted by the same process in the same symlink form, so relativizing
	// against this cwd avoids the realpath/symlink mismatch that would otherwise
	// keep an absolute path and silently miss every obligation ref.
	for (const event of events) {
		if (event && typeof event === "object" && typeof event.cwd === "string" && event.cwd.trim()) {
			return event.cwd;
		}
	}
	return null;
}

export function findResultEvent(events) {
	for (let index = events.length - 1; index >= 0; index -= 1) {
		const event = events[index];
		if (event && typeof event === "object" && !Array.isArray(event) && event.type === "result") {
			return event;
		}
	}
	return null;
}

function resultText(resultEvent) {
	if (!resultEvent || resultEvent.result === undefined || resultEvent.result === null) {
		return "";
	}
	return typeof resultEvent.result === "string" ? resultEvent.result : JSON.stringify(resultEvent.result);
}

function runStatusFromResult(resultEvent) {
	// No terminal result event => the run never completed comparably.
	if (!resultEvent) {
		return "blocked";
	}
	if (resultEvent.is_error === true) {
		return "failed";
	}
	return resultEvent.subtype === "success" ? "passed" : "failed";
}

export function extractRunFromTranscript(raw, { workspaceRoot = null, skillId = null, skillPath = null } = {}) {
	const events = parseTranscriptEvents(raw);
	const resultEvent = findResultEvent(events);
	// Prefer the transcript's own cwd over the caller-supplied root so coverage
	// relativization stays symlink-form-consistent across the two capture
	// worktrees; fall back to workspaceRoot for transcripts without an init cwd.
	const root = transcriptCwd(events) ?? workspaceRoot;
	const run = {
		status: runStatusFromResult(resultEvent),
		output: {
			text: resultText(resultEvent),
			sourceRefs: collectSourceRefs(events, { workspaceRoot: root }),
		},
	};
	if (skillId) {
		run.skillId = skillId;
	}
	if (skillPath) {
		run.skillPath = skillPath;
	}
	return run;
}

function assertNonEmptyString(value, field) {
	if (typeof value !== "string" || !value.trim()) {
		throw new Error(`${field} must be a non-empty string`);
	}
	return value.trim();
}

function assertTaskPacket(taskPacket) {
	if (!taskPacket || typeof taskPacket !== "object" || Array.isArray(taskPacket)) {
		throw new Error("taskPacket must be an object");
	}
	const hasView = ["path", "sourceRef", "schemaVersion", "summary"].some(
		(key) => typeof taskPacket[key] === "string" && taskPacket[key].trim(),
	);
	if (!hasView) {
		throw new Error("taskPacket must include at least one of: path, sourceRef, schemaVersion, summary");
	}
	return taskPacket;
}

// Mirrors the scorer's allowed status set (skill_clone_experiment.go:110-112) so
// a hand-authored spec is rejected at build time, not by cautilus after capture.
const RUN_STATUS_VALUES = new Set(["passed", "failed", "blocked", "degraded"]);

function assertRun(run, field) {
	if (!run || typeof run !== "object" || Array.isArray(run)) {
		throw new Error(`${field} must be an object`);
	}
	if (run.status !== undefined && !RUN_STATUS_VALUES.has(run.status)) {
		throw new Error(`${field}.status must be one of: passed, failed, blocked, degraded`);
	}
	const refs = run.output?.sourceRefs;
	if (refs !== undefined) {
		if (!Array.isArray(refs)) {
			throw new Error(`${field}.output.sourceRefs must be an array`);
		}
		refs.forEach((ref, index) => {
			// The scorer's normalizeSkillCloneStringList rejects empty entries.
			if (typeof ref !== "string" || !ref.trim()) {
				throw new Error(`${field}.output.sourceRefs[${index}] must be a non-empty string`);
			}
		});
	}
	return run;
}

export function buildSkillCloneExperimentInput({
	experimentId,
	taskPacket,
	baseline,
	variant,
	sourceCoverageObligations,
	rubricPhrases,
	isolation,
	exemplar,
} = {}) {
	const input = {
		schemaVersion: SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA,
		experimentId: assertNonEmptyString(experimentId, "experimentId"),
		taskPacket: assertTaskPacket(taskPacket),
		baseline: assertRun(baseline, "baseline"),
		variant: assertRun(variant, "variant"),
	};
	if (exemplar !== undefined) {
		input.exemplar = assertRun(exemplar, "exemplar");
	}
	if (sourceCoverageObligations !== undefined) {
		if (!Array.isArray(sourceCoverageObligations)) {
			throw new Error("sourceCoverageObligations must be an array");
		}
		input.sourceCoverageObligations = sourceCoverageObligations;
	}
	if (rubricPhrases !== undefined) {
		if (!Array.isArray(rubricPhrases)) {
			throw new Error("rubricPhrases must be an array");
		}
		input.rubricPhrases = rubricPhrases;
	}
	if (isolation !== undefined) {
		input.isolation = isolation;
	}
	return input;
}

function readJson(path) {
	return JSON.parse(readFileSync(path, "utf-8"));
}

function parseCliArgs(argv) {
	const options = {
		spec: null,
		baselineTranscript: null,
		variantTranscript: null,
		workspaceRoot: process.cwd(),
		baselineWorkspaceRoot: null,
		variantWorkspaceRoot: null,
		output: null,
	};
	const map = {
		"--spec": (value) => {
			options.spec = value;
		},
		"--baseline-transcript": (value) => {
			options.baselineTranscript = value;
		},
		"--variant-transcript": (value) => {
			options.variantTranscript = value;
		},
		"--workspace-root": (value) => {
			options.workspaceRoot = resolve(value);
		},
		"--baseline-workspace-root": (value) => {
			options.baselineWorkspaceRoot = resolve(value);
		},
		"--variant-workspace-root": (value) => {
			options.variantWorkspaceRoot = resolve(value);
		},
		"--output": (value) => {
			options.output = value;
		},
	};
	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		if (arg === "-h" || arg === "--help") {
			options.help = true;
			return options;
		}
		const apply = map[arg];
		if (!apply) {
			throw new Error(`Unknown argument: ${arg}`);
		}
		const value = argv[index + 1];
		if (value === undefined) {
			throw new Error(`Missing value for ${arg}`);
		}
		apply(value);
		index += 1;
	}
	return options;
}

const USAGE = `Usage:
  node ./scripts/agent-runtime/extract-skill-experiment-input.mjs \\
    --spec <spec.json> \\
    --baseline-transcript <baseline.jsonl> --variant-transcript <variant.jsonl> \\
    [--workspace-root <dir>] [--baseline-workspace-root <dir>] [--variant-workspace-root <dir>] \\
    [--output <input.v1.json>]

The spec carries the static experiment fields:
  { experimentId, taskPacket{summary|path|sourceRef|schemaVersion},
    sourceCoverageObligations?, rubricPhrases?, isolation?, skillId?,
    baseline?{skillPath}, variant?{skillPath} }
Baseline/variant transcripts supply each arm's status, output.text, and
output.sourceRefs (recovered from the agent's Read/Edit/Write tool calls).
`;

export function runCli(argv, { readFile = readJson, readText = (p) => readFileSync(p, "utf-8") } = {}) {
	const options = parseCliArgs(argv);
	if (options.help) {
		process.stdout.write(USAGE);
		return 0;
	}
	if (!options.spec) {
		throw new Error("--spec is required");
	}
	if (!options.baselineTranscript || !options.variantTranscript) {
		throw new Error("--baseline-transcript and --variant-transcript are required");
	}
	const spec = readFile(options.spec);
	const baselineRoot = options.baselineWorkspaceRoot ?? options.workspaceRoot;
	const variantRoot = options.variantWorkspaceRoot ?? options.workspaceRoot;
	const baseline = extractRunFromTranscript(readText(options.baselineTranscript), {
		workspaceRoot: baselineRoot,
		skillId: spec.skillId ?? null,
		skillPath: spec.baseline?.skillPath ?? null,
	});
	const variant = extractRunFromTranscript(readText(options.variantTranscript), {
		workspaceRoot: variantRoot,
		skillId: spec.skillId ?? null,
		skillPath: spec.variant?.skillPath ?? null,
	});
	const input = buildSkillCloneExperimentInput({
		experimentId: spec.experimentId,
		taskPacket: spec.taskPacket,
		baseline,
		variant,
		sourceCoverageObligations: spec.sourceCoverageObligations,
		rubricPhrases: spec.rubricPhrases,
		isolation: spec.isolation,
		exemplar: spec.exemplar,
	});
	const serialized = `${JSON.stringify(input, null, 2)}\n`;
	if (options.output) {
		writeFileSync(options.output, serialized);
	} else {
		process.stdout.write(serialized);
	}
	return 0;
}

if (import.meta.url === new URL(process.argv[1], "file:").href) {
	try {
		process.exit(runCli(process.argv.slice(2)));
	} catch (error) {
		process.stderr.write(`${error.message}\n`);
		process.exit(1);
	}
}
