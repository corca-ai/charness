import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { SKILL_EVALUATION_INPUTS_SCHEMA } from "../../scripts/agent-runtime/contract-versions.mjs";
import {
	buildExecutionObservation,
	collectCommandLog,
	collectOpenedBasenames,
	collectToolProfile,
	durationMs,
	finalAssistantText,
	listSessionTreeJsonl,
	parseEventsFromFiles,
	runCli,
	sumTokens,
} from "../../scripts/agent-runtime/build-skill-execution-observation.mjs";

// A session-log event with assistant tool_use blocks. isSidechain marks a
// subagent track; the analyzer must read those too.
function assistantToolUse(blocks, { isSidechain = false, usage = null, timestamp = null } = {}) {
	return {
		type: "assistant",
		isSidechain,
		...(timestamp ? { timestamp } : {}),
		message: {
			role: "assistant",
			...(usage ? { usage } : {}),
			content: blocks.map((b) => ({ type: "tool_use", id: "t", name: b.name, input: b.input })),
		},
	};
}

function assistantText(text, { isSidechain = false } = {}) {
	return {
		type: "assistant",
		isSidechain,
		message: { role: "assistant", content: [{ type: "text", text }] },
	};
}

test("collectCommandLog includes Bash commands and Read paths across the tree", () => {
	const events = [
		assistantToolUse([{ name: "Bash", input: { command: "./scripts/run-quality.sh" } }]),
		assistantToolUse([{ name: "Read", input: { file_path: "/x/skills/quality/references/quality-lenses.md" } }], {
			isSidechain: true,
		}),
	];
	const log = collectCommandLog(events);
	assert.match(log, /run-quality\.sh/);
	assert.match(log, /quality-lenses\.md/);
});

test("collectToolProfile counts tool calls by name", () => {
	const events = [
		assistantToolUse([{ name: "Bash", input: { command: "a" } }, { name: "Bash", input: { command: "b" } }]),
		assistantToolUse([{ name: "Read", input: { file_path: "/p" } }], { isSidechain: true }),
	];
	assert.deepEqual(collectToolProfile(events), { Bash: 2, Read: 1 });
});

test("collectOpenedBasenames returns basenames including subagent reads", () => {
	const events = [
		assistantToolUse([{ name: "Read", input: { file_path: "/a/b/operability-signals.md" } }], { isSidechain: true }),
		assistantToolUse([{ name: "Bash", input: { command: "echo hi" } }]),
	];
	assert.ok(collectOpenedBasenames(events).has("operability-signals.md"));
});

test("sumTokens aggregates assistant usage across the tree", () => {
	const events = [
		assistantToolUse([{ name: "Bash", input: { command: "x" } }], {
			usage: { input_tokens: 10, output_tokens: 5, cache_creation_input_tokens: 2, cache_read_input_tokens: 100 },
		}),
		assistantToolUse([{ name: "Read", input: { file_path: "/p" } }], {
			isSidechain: true,
			usage: { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0 },
		}),
	];
	const t = sumTokens(events);
	assert.equal(t.output, 6);
	assert.equal(t.cacheRead, 100);
	assert.equal(t.total, 10 + 5 + 2 + 100 + 1 + 1);
});

test("durationMs spans min/max event timestamps", () => {
	const events = [
		{ type: "assistant", timestamp: "2026-06-22T09:00:00.000Z" },
		{ type: "assistant", timestamp: "2026-06-22T09:10:00.000Z" },
	];
	assert.equal(durationMs(events), 600000);
	assert.equal(durationMs([{ type: "assistant" }]), null);
});

test("finalAssistantText takes the last parent-track text, ignoring sidechains", () => {
	const events = [
		assistantText("early"),
		assistantText("subagent chatter", { isSidechain: true }),
		assistantText("final posture summary"),
	];
	assert.equal(finalAssistantText(events), "final posture summary");
});

test("buildExecutionObservation fails when a required command fragment is absent", () => {
	const spec = {
		skillId: "quality",
		evaluationId: "execution-quality",
		targetId: "quality",
		prompt: "/charness:quality",
		requiredCommandFragments: ["quality-lenses.md"],
		declaredReferences: ["quality-lenses.md", "operability-signals.md"],
		thresholds: { max_duration_ms: 600000 },
	};
	const events = [
		assistantToolUse([{ name: "Bash", input: { command: "./scripts/run-quality.sh" } }], {
			usage: { input_tokens: 1, output_tokens: 1 },
			timestamp: "2026-06-22T09:00:00.000Z",
		}),
		assistantText("posture summary", {}),
	];
	const { packet, report } = buildExecutionObservation({ spec, events });
	assert.equal(packet.schemaVersion, SKILL_EVALUATION_INPUTS_SCHEMA);
	const ev = packet.evaluations[0];
	assert.equal(ev.outcome, "failed");
	assert.equal(ev.evaluationKind, "execution");
	assert.deepEqual(ev.thresholds, { max_duration_ms: 600000 });
	assert.equal(ev.sampling.statusCounts.failed, 1);
	assert.equal(report.coverage.covered, 0);
	assert.equal(report.coverage.declared, 2);
	assert.match(ev.summary, /missing required fragment: quality-lenses\.md/);
});

test("buildExecutionObservation passes and counts coverage when a subagent reads the routed ref", () => {
	const spec = {
		skillId: "quality",
		evaluationId: "execution-quality",
		targetId: "quality",
		prompt: "/charness:quality",
		requiredCommandFragments: ["quality-lenses.md"],
		declaredReferences: ["quality-lenses.md", "operability-signals.md"],
	};
	const events = [
		assistantToolUse([{ name: "Agent", input: { description: "lens review" } }]),
		// the routed read happens INSIDE a subagent track:
		assistantToolUse([{ name: "Read", input: { file_path: "/x/references/quality-lenses.md" } }], {
			isSidechain: true,
		}),
	];
	const { packet, report } = buildExecutionObservation({ spec, events });
	assert.equal(packet.evaluations[0].outcome, "passed");
	assert.equal(report.coverage.covered, 1);
	assert.deepEqual(report.coverage.coveredRefs, ["quality-lenses.md"]);
});

test("buildExecutionObservation rejects an incomplete spec", () => {
	assert.throws(() => buildExecutionObservation({ spec: { skillId: "q" }, events: [] }), /must be a non-empty string/);
});

test("parseEventsFromFiles and listSessionTreeJsonl read a parent + subagents tree, and runCli emits a packet", () => {
	const root = mkdtempSync(join(tmpdir(), "charness-skilltree-"));
	const sub = join(root, "sess", "subagents");
	mkdirSync(sub, { recursive: true });
	writeFileSync(
		join(root, "sess.jsonl"),
		`${JSON.stringify(assistantToolUse([{ name: "Bash", input: { command: "gate" } }], { usage: { output_tokens: 3 }, timestamp: "2026-06-22T09:00:00.000Z" }))}\n` +
			`${JSON.stringify(assistantText("done"))}\n`,
	);
	writeFileSync(
		join(sub, "agent-1.jsonl"),
		`${JSON.stringify(assistantToolUse([{ name: "Read", input: { file_path: "/r/quality-lenses.md" } }], { isSidechain: true, timestamp: "2026-06-22T09:01:00.000Z" }))}\n`,
	);
	const files = listSessionTreeJsonl(root);
	assert.equal(files.length, 2);
	const events = parseEventsFromFiles(files);
	assert.ok(collectOpenedBasenames(events).has("quality-lenses.md"));

	const specPath = join(root, "spec.json");
	writeFileSync(
		specPath,
		JSON.stringify({
			skillId: "quality",
			evaluationId: "execution-quality",
			targetId: "quality",
			prompt: "/charness:quality",
			requiredCommandFragments: ["quality-lenses.md"],
			declaredReferences: ["quality-lenses.md"],
		}),
	);
	const outPath = join(root, "observed.json");
	const code = runCli(["--session-tree", root, "--spec", specPath, "--output", outPath]);
	assert.equal(code, 0);
	const packet = JSON.parse(readFileSync(outPath, "utf-8"));
	assert.equal(packet.schemaVersion, SKILL_EVALUATION_INPUTS_SCHEMA);
	assert.equal(packet.evaluations[0].outcome, "passed");
});
