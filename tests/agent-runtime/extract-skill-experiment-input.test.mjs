import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA } from "../../scripts/agent-runtime/contract-versions.mjs";
import {
	buildSkillCloneExperimentInput,
	collectSourceRefs,
	extractRunFromTranscript,
	findResultEvent,
	parseTranscriptEvents,
	runCli,
} from "../../scripts/agent-runtime/extract-skill-experiment-input.mjs";

// Build a stream-json transcript line for an assistant tool_use call.
function toolUseLine(name, input) {
	return JSON.stringify({
		type: "assistant",
		message: { role: "assistant", content: [{ type: "tool_use", id: "t", name, input }] },
	});
}

function resultLine({ result, subtype = "success", isError = false } = {}) {
	return JSON.stringify({
		type: "result",
		subtype,
		is_error: isError,
		result,
		usage: { input_tokens: 5, output_tokens: 2 },
		total_cost_usd: 0.01,
	});
}

function transcript(lines) {
	return `${lines.join("\n")}\n`;
}

test("schema constant matches the cautilus scorer input contract", () => {
	assert.equal(SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA, "cautilus.skill_clone_experiment_input.v1");
});

test("collectSourceRefs recovers read/edit paths, relativizes, and excludes pattern tools", () => {
	const root = "/work/repo";
	const events = parseTranscriptEvents(
		transcript([
			JSON.stringify({ type: "system", subtype: "init" }),
			toolUseLine("Read", { file_path: "/work/repo/skills/public/quality/SKILL.md" }),
			toolUseLine("Glob", { pattern: "**/*.md" }),
			toolUseLine("Grep", { pattern: "cautilus", path: "/work/repo/scripts" }),
			toolUseLine("Read", { file_path: "/work/repo/skills/public/quality/references/cautilus-on-demand.md" }),
			toolUseLine("Read", { file_path: "/work/repo/skills/public/quality/SKILL.md" }), // duplicate
			toolUseLine("Read", { file_path: "/outside/secret.md" }), // outside workspace
			resultLine({ result: "done" }),
		]),
	);
	assert.deepEqual(collectSourceRefs(events, { workspaceRoot: root }), [
		"/outside/secret.md",
		"skills/public/quality/SKILL.md",
		"skills/public/quality/references/cautilus-on-demand.md",
	]);
});

test("transcript cwd is preferred as the relativization root (symlink-form safety)", () => {
	// The agent's tool file_paths and its init cwd share one symlink form. Even
	// when the caller passes a DIFFERENT-form root, the cwd keeps refs repo-relative
	// so they still match obligations — the worktree symlink hazard from review.
	const run = extractRunFromTranscript(
		transcript([
			JSON.stringify({ type: "system", subtype: "init", cwd: "/private/var/wt/variant" }),
			toolUseLine("Read", { file_path: "/private/var/wt/variant/skills/public/quality/SKILL.md" }),
			resultLine({ result: "ok" }),
		]),
		// Caller passes the symlink form (/var -> /private/var); without the cwd
		// preference this would relativize wrong and keep an absolute path.
		{ workspaceRoot: "/var/wt/variant" },
	);
	assert.deepEqual(run.output.sourceRefs, ["skills/public/quality/SKILL.md"]);
});

test("buildSkillCloneExperimentInput rejects an invalid run status and empty source refs", () => {
	const okArm = { status: "passed", output: { text: "x", sourceRefs: ["skills/a/SKILL.md"] } };
	assert.throws(
		() => buildSkillCloneExperimentInput({ experimentId: "e", taskPacket: { summary: "s" }, baseline: { status: "weird", output: { sourceRefs: [] } }, variant: okArm }),
		/baseline\.status must be one of/,
	);
	assert.throws(
		() => buildSkillCloneExperimentInput({ experimentId: "e", taskPacket: { summary: "s" }, baseline: { status: "passed", output: { sourceRefs: ["   "] } }, variant: okArm }),
		/baseline\.output\.sourceRefs\[0\] must be a non-empty string/,
	);
});

test("findResultEvent returns the terminal result event", () => {
	const events = parseTranscriptEvents(transcript([resultLine({ result: "first" }), resultLine({ result: "last" })]));
	assert.equal(findResultEvent(events).result, "last");
	assert.equal(findResultEvent(parseTranscriptEvents("{}\n")), null);
});

test("extractRunFromTranscript maps status, text, and sourceRefs", () => {
	const run = extractRunFromTranscript(
		transcript([
			toolUseLine("Read", { file_path: "/w/skills/a/SKILL.md" }),
			resultLine({ result: "routed to quality" }),
		]),
		{ workspaceRoot: "/w", skillId: "quality", skillPath: "skills/a" },
	);
	assert.equal(run.status, "passed");
	assert.equal(run.output.text, "routed to quality");
	assert.deepEqual(run.output.sourceRefs, ["skills/a/SKILL.md"]);
	assert.equal(run.skillId, "quality");
	assert.equal(run.skillPath, "skills/a");
});

test("extractRunFromTranscript reports blocked when no result event and failed on error", () => {
	const blocked = extractRunFromTranscript(transcript([toolUseLine("Read", { file_path: "/w/x.md" })]), {});
	assert.equal(blocked.status, "blocked");
	const failed = extractRunFromTranscript(transcript([resultLine({ result: "boom", subtype: "error_max_turns", isError: true })]), {});
	assert.equal(failed.status, "failed");
});

test("buildSkillCloneExperimentInput emits a scorer-shaped input and validates required fields", () => {
	const arm = { status: "passed", output: { text: "x", sourceRefs: ["skills/a/SKILL.md"] } };
	const input = buildSkillCloneExperimentInput({
		experimentId: "exp-1",
		taskPacket: { summary: "route a quality request" },
		baseline: arm,
		variant: arm,
		sourceCoverageObligations: [{ id: "o1", ref: "skills/a/SKILL.md", required: true }],
		rubricPhrases: ["quality"],
		isolation: { productionSkillTouched: false, notes: ["isolated worktrees"] },
	});
	assert.equal(input.schemaVersion, SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA);
	assert.equal(input.experimentId, "exp-1");
	assert.deepEqual(input.baseline.output.sourceRefs, ["skills/a/SKILL.md"]);
	assert.equal(input.isolation.productionSkillTouched, false);

	assert.throws(() => buildSkillCloneExperimentInput({ taskPacket: { summary: "s" }, baseline: arm, variant: arm }), /experimentId/);
	assert.throws(
		() => buildSkillCloneExperimentInput({ experimentId: "e", taskPacket: { note: "no view" }, baseline: arm, variant: arm }),
		/taskPacket must include at least one of/,
	);
	assert.throws(() => buildSkillCloneExperimentInput({ experimentId: "e", taskPacket: { summary: "s" }, variant: arm }), /baseline must be an object/);
});

test("runCli builds a full input.v1 from two transcripts with per-arm roots", () => {
	const spec = {
		experimentId: "quality-ref-disposition",
		taskPacket: { summary: "route a validation request through quality" },
		sourceCoverageObligations: [{ id: "o1", ref: "skills/public/quality/references/cautilus-on-demand.md", required: true }],
		rubricPhrases: ["quality"],
		isolation: { productionSkillTouched: false },
		skillId: "quality",
		baseline: { skillPath: "skills/public/quality" },
		variant: { skillPath: "skills/public/quality" },
	};
	const baselineTranscript = transcript([
		toolUseLine("Read", { file_path: "/wt/baseline/skills/public/quality/SKILL.md" }),
		resultLine({ result: "baseline routed; quality" }),
	]);
	const variantTranscript = transcript([
		toolUseLine("Read", { file_path: "/wt/variant/skills/public/quality/SKILL.md" }),
		toolUseLine("Read", { file_path: "/wt/variant/skills/public/quality/references/cautilus-on-demand.md" }),
		resultLine({ result: "variant routed; quality" }),
	]);
	const files = {
		"spec.json": spec,
		"/wt/baseline/t.jsonl": baselineTranscript,
		"/wt/variant/t.jsonl": variantTranscript,
	};
	let written = null;
	const argv = [
		"--spec",
		"spec.json",
		"--baseline-transcript",
		"/wt/baseline/t.jsonl",
		"--variant-transcript",
		"/wt/variant/t.jsonl",
		"--baseline-workspace-root",
		"/wt/baseline",
		"--variant-workspace-root",
		"/wt/variant",
		"--output",
		"out.json",
	];
	// Inject readers; capture the write via a spy on process.stdout is avoided by --output.
	const rc = runCliWithCapture(argv, files, (value) => {
		written = value;
	});
	assert.equal(rc, 0);
	const input = JSON.parse(written);
	assert.equal(input.schemaVersion, SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA);
	assert.deepEqual(input.baseline.output.sourceRefs, ["skills/public/quality/SKILL.md"]);
	assert.deepEqual(input.variant.output.sourceRefs, [
		"skills/public/quality/SKILL.md",
		"skills/public/quality/references/cautilus-on-demand.md",
	]);
	assert.equal(input.skillId ?? input.baseline.skillId, "quality");
});

test("committed spec.json drives the extractor to a valid input with a real coverage gain", () => {
	const spec = JSON.parse(
		readFileSync(fileURLToPath(new URL("../../evals/cautilus/skill-experiment/spec.json", import.meta.url)), "utf-8"),
	);
	// Spec sanity: the 7 routed obligations + neutral rubric + declared isolation.
	assert.equal(spec.experimentId, "quality-ref-disposition-2026-06-21");
	assert.equal(spec.sourceCoverageObligations.length, 7);
	assert.equal(spec.isolation.productionSkillTouched, false);
	const routed = spec.sourceCoverageObligations.map((o) => o.ref);
	assert.ok(routed.includes("skills/public/quality/references/quality-lenses.md"));

	// Simulate the two arms: variant reaches a routed ref the baseline does not.
	const baseline = extractRunFromTranscript(
		transcript([
			JSON.stringify({ type: "system", subtype: "init", cwd: "/wt/baseline" }),
			toolUseLine("Read", { file_path: "/wt/baseline/skills/public/quality/SKILL.md" }),
			resultLine({ result: "baseline reviewed quality gates; consulted the reference index" }),
		]),
		{ workspaceRoot: "/wt/baseline" },
	);
	const variant = extractRunFromTranscript(
		transcript([
			JSON.stringify({ type: "system", subtype: "init", cwd: "/wt/variant" }),
			toolUseLine("Read", { file_path: "/wt/variant/skills/public/quality/SKILL.md" }),
			toolUseLine("Read", { file_path: "/wt/variant/skills/public/quality/references/quality-lenses.md" }),
			resultLine({ result: "variant reviewed quality gates; followed the pointer to the quality reference lenses" }),
		]),
		{ workspaceRoot: "/wt/variant" },
	);
	const input = buildSkillCloneExperimentInput({
		experimentId: spec.experimentId,
		taskPacket: spec.taskPacket,
		baseline,
		variant,
		sourceCoverageObligations: spec.sourceCoverageObligations,
		rubricPhrases: spec.rubricPhrases,
		isolation: spec.isolation,
	});
	assert.equal(input.schemaVersion, SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA);
	// The variant covers a routed obligation the baseline does not — the gain the scorer rewards.
	assert.ok(input.variant.output.sourceRefs.includes("skills/public/quality/references/quality-lenses.md"));
	assert.ok(!input.baseline.output.sourceRefs.includes("skills/public/quality/references/quality-lenses.md"));
});

// runCli writes via node:fs writeFileSync; to keep the test hermetic we re-run
// the pure builder path through the injected readers and intercept --output by
// pointing it through a small shim that captures the serialized payload.
function runCliWithCapture(argv, files, onWrite) {
	const readFile = (path) => {
		if (!(path in files)) {
			throw new Error(`unexpected readFile ${path}`);
		}
		return files[path];
	};
	const readText = (path) => {
		if (!(path in files)) {
			throw new Error(`unexpected readText ${path}`);
		}
		return files[path];
	};
	// Strip --output so runCli returns via stdout; capture stdout instead.
	const outIndex = argv.indexOf("--output");
	const filtered = outIndex === -1 ? argv : [...argv.slice(0, outIndex), ...argv.slice(outIndex + 2)];
	const originalWrite = process.stdout.write;
	process.stdout.write = (chunk) => {
		onWrite(String(chunk));
		return true;
	};
	try {
		return runCli(filtered, { readFile, readText });
	} finally {
		process.stdout.write = originalWrite;
	}
}
