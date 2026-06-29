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
	collectToolResultSizes,
	collectToolTrace,
	detectWaste,
	durationMs,
	finalAssistantText,
	listSessionTreeJsonl,
	parseEventsFromFiles,
	parseReadCommandBasenames,
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
			content: blocks.map((b) => ({ type: "tool_use", id: b.id ?? "t", name: b.name, input: b.input })),
		},
	};
}

// A user-track event carrying tool_result blocks (the output fed back to the
// model). collectToolResultSizes matches these to tool_use by id.
function userToolResult(results) {
	return {
		type: "user",
		message: {
			role: "user",
			content: results.map((r) => ({ type: "tool_result", tool_use_id: r.id, content: r.content })),
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

test("parseReadCommandBasenames counts sed/cat/head/tail/less file operands", () => {
	assert.deepEqual([...parseReadCommandBasenames("sed -n '1,120p' docs/handoff.md")], ["handoff.md"]);
	assert.deepEqual([...parseReadCommandBasenames("cat skills/a/x.md skills/b/y.md")].sort(), ["x.md", "y.md"]);
	assert.ok(parseReadCommandBasenames("head -n 30 docs/conventions/operating-contract.md").has("operating-contract.md"));
	assert.ok(parseReadCommandBasenames("less plugins/charness/skills/retro/references/expert-lens.md").has("expert-lens.md"));
});

test("parseReadCommandBasenames drops the grep/rg/awk pattern operand, counts the file", () => {
	// A reference NAMED in a search pattern must not masquerade as opened. The file
	// operand (SKILL.md) is the only real read here.
	const found = parseReadCommandBasenames('grep -n "expert-lens.md" skills/public/retro/SKILL.md');
	assert.ok(found.has("SKILL.md"));
	assert.ok(!found.has("expert-lens.md"), "named-in-pattern must not count as opened");
	const rgFound = parseReadCommandBasenames("rg 'mode-guide.md' references/section-guide.md");
	assert.ok(rgFound.has("section-guide.md"));
	assert.ok(!rgFound.has("mode-guide.md"));
});

test("parseReadCommandBasenames keeps the pattern dropped when an arity flag precedes it", () => {
	// `-m 5` / `-A 3` consume a value token; the pattern (a .md ref name) must NOT
	// slide into the file slot and over-count. This is the shape the naive
	// drop-first-operand parser got wrong.
	for (const cmd of [
		"grep -m 5 expert-lens.md skills/public/retro/SKILL.md",
		"grep -A 3 expert-lens.md skills/public/retro/SKILL.md",
		"grep -B 2 -C 2 expert-lens.md skills/public/retro/SKILL.md",
	]) {
		const found = parseReadCommandBasenames(cmd);
		assert.ok(found.has("SKILL.md"), `${cmd} should count the file`);
		assert.ok(!found.has("expert-lens.md"), `${cmd} must not count the pattern`);
	}
	// `-e PATTERN` supplies the pattern via the flag; the positional operand is then
	// a file, not a second pattern to drop.
	const eFound = parseReadCommandBasenames("grep -e expert-lens.md skills/public/retro/SKILL.md");
	assert.ok(eFound.has("SKILL.md"));
	assert.ok(!eFound.has("expert-lens.md"));
});

test("parseReadCommandBasenames ignores piped-stdin readers and redirect targets", () => {
	// `head` reads stdin (no file operand); `> out.md` is a write target, not a read.
	assert.equal(parseReadCommandBasenames("git show 29260c26 --stat | head -30").size, 0);
	assert.ok(!parseReadCommandBasenames("cat docs/handoff.md > /tmp/out.md").has("out.md"));
	assert.ok(parseReadCommandBasenames("cat docs/handoff.md > /tmp/out.md").has("handoff.md"));
});

test("parseReadCommandBasenames ignores non-read commands", () => {
	assert.equal(parseReadCommandBasenames("python3 scripts/plan_retro_run.py --repo-root .").size, 0);
	assert.equal(parseReadCommandBasenames("git log --oneline -30").size, 0);
});

test("collectOpenedBasenames counts Bash sed reads alongside Read tool-calls", () => {
	const events = [
		assistantToolUse([{ name: "Read", input: { file_path: "/x/references/expert-lens.md" } }]),
		assistantToolUse([
			{ name: "Bash", input: { command: "sed -n '1,80p' plugins/charness/skills/retro/references/waste-sibling-scan.md" } },
		]),
	];
	const opened = collectOpenedBasenames(events);
	assert.ok(opened.has("expert-lens.md"));
	assert.ok(opened.has("waste-sibling-scan.md"));
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

test("collectToolResultSizes maps tool_use_id to result char length across string and array content", () => {
	const events = [
		userToolResult([{ id: "a", content: "hello" }]),
		userToolResult([{ id: "b", content: [{ type: "text", text: "ab" }, { type: "text", text: "cd" }] }]),
	];
	const sizes = collectToolResultSizes(events);
	assert.equal(sizes.get("a"), 5);
	assert.equal(sizes.get("b"), 4);
});

test("collectToolTrace emits one ordered record per call with usage, result size, and wall gap", () => {
	const events = [
		assistantToolUse([{ id: "r1", name: "Read", input: { file_path: "/x/doc.md" } }], {
			usage: { output_tokens: 10, cache_read_input_tokens: 100 },
			timestamp: "2026-06-29T00:00:00.000Z",
		}),
		userToolResult([{ id: "r1", content: "x".repeat(42) }]),
		assistantToolUse(
			[{ id: "b1", name: "Bash", input: { command: "ls" } }, { id: "b2", name: "Bash", input: { command: "pwd" } }],
			{ usage: { output_tokens: 4 }, timestamp: "2026-06-29T00:00:05.000Z", isSidechain: true },
		),
	];
	const trace = collectToolTrace(events);
	assert.equal(trace.length, 3);
	assert.deepEqual(trace.map((r) => r.step), [1, 2, 3]);
	assert.equal(trace[0].name, "Read");
	assert.equal(trace[0].out_chars, 42);
	assert.equal(trace[0].msg_out_tokens, 10);
	assert.equal(trace[0].wall_ms, null); // first message has no prior
	assert.equal(trace[1].track, "sub");
	assert.equal(trace[1].msg_tool_count, 2);
	assert.equal(trace[1].wall_ms, 5000); // first call of the second message carries the gap
	assert.equal(trace[2].wall_ms, 0); // sibling call in the same message does not double-count
});

test("detectWaste flags duplicate reads, repeated edits, repeated bash, and large outputs", () => {
	const events = [
		assistantToolUse([{ name: "Read", input: { file_path: "/x/state.yaml" } }]),
		assistantToolUse([{ name: "Read", input: { file_path: "/x/state.yaml" } }]),
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/s.yaml" } }]),
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/s.yaml" } }]),
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/s.yaml" } }]),
		assistantToolUse([{ name: "Bash", input: { command: "git status" } }]),
		assistantToolUse([{ name: "Bash", input: { command: "git status" } }]),
	];
	const trace = [{ step: 1, name: "Read", out_chars: 60000 }];
	const flags = detectWaste(events, { trace });
	const kinds = flags.map((f) => f.kind).sort();
	assert.deepEqual(kinds, ["duplicate_read", "large_output", "repeated_bash", "repeated_edit"]);
	assert.equal(flags.find((f) => f.kind === "repeated_edit").count, 3);
	// two edits is normal, not a smell
	assert.equal(detectWaste([
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/s.yaml" } }]),
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/s.yaml" } }]),
	]).length, 0);
});

test("buildExecutionObservation surfaces a waste-smell clause and trace in the report", () => {
	const spec = {
		skillId: "hitl",
		evaluationId: "execution-hitl",
		targetId: "hitl",
		prompt: "/charness:hitl",
		requiredCommandFragments: [],
		declaredReferences: [],
	};
	const events = [
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/state.yaml" } }]),
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/state.yaml" } }]),
		assistantToolUse([{ name: "Edit", input: { file_path: "/x/state.yaml" } }]),
	];
	const { packet, report } = buildExecutionObservation({ spec, events });
	assert.equal(report.waste.length, 1);
	assert.equal(report.waste[0].kind, "repeated_edit");
	assert.equal(report.trace.length, 3);
	assert.match(packet.evaluations[0].summary, /Waste smells: 1 \(repeated_edit\)/);
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

	// The CLI writes a durable trace digest next to --output by default.
	const digestPath = join(root, "trace-digest.jsonl");
	const digestLines = readFileSync(digestPath, "utf-8").trim().split("\n").filter(Boolean);
	assert.equal(digestLines.length, 2); // one Bash (parent) + one Read (subagent)
	const records = digestLines.map((line) => JSON.parse(line));
	assert.ok(records.every((r) => typeof r.name === "string" && typeof r.step === "number"));
	assert.deepEqual(records.map((r) => r.name).sort(), ["Bash", "Read"]);
});
