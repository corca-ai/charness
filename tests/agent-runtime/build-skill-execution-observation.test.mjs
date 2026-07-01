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
	expandForLoopReadCommands,
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

test("expandForLoopReadCommands expands a literal primer-batch loop into per-file reads", () => {
	// The 2026-06-29 quality capture's actual batch-read shape: a `for` loop over a
	// literal primer list catting `references/$f.md`. The assembled paths only exist
	// after shell expansion, so a non-expanding matcher false-negatives the batch.
	const cmd =
		'for f in quality-lenses gate-classification skill-quality; do echo "## references/$f.md ##"; cat "references/$f.md"; echo; done 2>&1 | head -560';
	const expanded = expandForLoopReadCommands(cmd);
	// Only the `cat` body is emitted (echo is not a read), one per literal token.
	assert.deepEqual(expanded.sort(), [
		"cat references/gate-classification.md",
		"cat references/quality-lenses.md",
		"cat references/skill-quality.md",
	]);
	const names = new Set();
	for (const c of expanded) {
		for (const n of parseReadCommandBasenames(c)) {
			names.add(n);
		}
	}
	assert.ok(names.has("quality-lenses.md"));
	assert.ok(names.has("skill-quality.md"));
});

test("expandForLoopReadCommands handles ${VAR}, leaves non-literal lists and non-read bodies alone", () => {
	assert.deepEqual(expandForLoopReadCommands('for f in a b; do head -n 5 "docs/${f}.md"; done'), [
		"head -n 5 docs/a.md",
		"head -n 5 docs/b.md",
	]);
	// A glob/command-substitution list is not statically expandable.
	assert.deepEqual(expandForLoopReadCommands('for f in *.md; do cat "$f"; done'), []);
	assert.deepEqual(expandForLoopReadCommands('for f in $(ls); do cat "$f"; done'), []);
	// A non-read body emits nothing (no false floor match from an echo).
	assert.deepEqual(expandForLoopReadCommands('for f in a b; do echo "$f.md"; done'), []);
	// A non-loop command is untouched.
	assert.deepEqual(expandForLoopReadCommands("cat references/quality-lenses.md"), []);
});

test("expandForLoopReadCommands keeps coverage sharp: grep pattern in a loop body is dropped", () => {
	// The expanded read still routes through parseReadCommandBasenames, so a
	// reference NAMED in a loop's grep pattern is not miscounted as opened.
	const expanded = expandForLoopReadCommands('for f in expert-lens.md chunk-contract.md; do grep "$f" SKILL.md; done');
	const names = new Set();
	for (const c of expanded) {
		for (const n of parseReadCommandBasenames(c)) {
			names.add(n);
		}
	}
	assert.ok(!names.has("expert-lens.md"));
	assert.ok(!names.has("chunk-contract.md"));
	assert.ok(names.has("SKILL.md"));
});

test("collectOpenedBasenames and the floor see a reference read via a for-loop", () => {
	const events = [
		assistantToolUse([
			{
				name: "Bash",
				input: {
					command:
						'for f in quality-lenses gate-classification; do cat "references/$f.md"; done',
				},
			},
		]),
	];
	const opened = collectOpenedBasenames(events);
	assert.ok(opened.has("quality-lenses.md"));
	assert.ok(opened.has("gate-classification.md"));
	// The floor substring-matches the command log, which now carries the expansion.
	assert.match(collectCommandLog(events), /references\/quality-lenses\.md/);
});

test("buildExecutionObservation passes when the required fragment is read via a for-loop", () => {
	const spec = {
		skillId: "quality",
		evaluationId: "execution-quality-claim-fidelity",
		targetId: "quality",
		prompt: "/charness:quality",
		requiredCommandFragments: ["quality-lenses.md"],
		declaredReferences: ["quality-lenses.md", "gate-classification.md", "unread.md"],
	};
	const events = [
		assistantToolUse([
			{
				name: "Bash",
				input: {
					command:
						'for f in quality-lenses gate-classification; do cat "references/$f.md"; done',
				},
			},
		]),
	];
	const { report } = buildExecutionObservation({ spec, events });
	assert.equal(report.outcome, "passed");
	assert.equal(report.coverage.covered, 2);
	assert.deepEqual(report.coverage.missingRefs, ["unread.md"]);
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

test("coverage denominator counts DEPTH refs only; INLINE/DUP stay advisory and declaredAll keeps the full count", () => {
	const spec = {
		skillId: "impl",
		evaluationId: "execution-impl",
		targetId: "impl",
		prompt: "/charness:impl",
		requiredCommandFragments: [],
		requiredSummaryFragments: ["categorized closeout"],
		declaredReferences: ["depth-a.md", "depth-b.md", "inline-c.md", "dup-d.md"],
		referenceEngagement: {
			"depth-a.md": { engagement: "engage-always", rationale: "x", classTag: "DEPTH" },
			"depth-b.md": { engagement: "on-demand", rationale: "x", trigger: "t", classTag: "DEPTH" },
			"inline-c.md": { engagement: "engage-always", rationale: "x", classTag: "INLINE" },
			"dup-d.md": { engagement: "engage-always", rationale: "x", classTag: "DUP" },
		},
	};
	const events = [
		assistantToolUse([{ name: "Read", input: { file_path: "/x/references/depth-a.md" } }]),
		assistantText("categorized closeout emitted"),
	];
	const { packet, report } = buildExecutionObservation({ spec, events });
	assert.equal(report.coverage.declared, 2); // DEPTH refs only
	assert.equal(report.coverage.declaredAll, 4); // full declared set preserved
	assert.equal(report.coverage.covered, 1); // depth-a opened
	assert.deepEqual(report.coverage.missingRefs, ["depth-b.md"]); // inline/dup never "missing"
	assert.deepEqual(report.coverage.inlineRefs, ["inline-c.md"]);
	assert.deepEqual(report.coverage.dupRefs, ["dup-d.md"]);
	assert.equal(report.outcome, "passed"); // RSF summary token present, no RCF needed
	assert.match(packet.evaluations[0].summary, /1\/2 DEPTH references opened \(missing: depth-b\.md\)/);
	assert.match(packet.evaluations[0].summary, /Advisory ref classes: 1 INLINE, 1 DUP/);
});

test("untagged declared refs default to DEPTH so declared === declaredAll (backward compatible)", () => {
	const spec = {
		skillId: "quality",
		evaluationId: "execution-quality",
		targetId: "quality",
		prompt: "/charness:quality",
		requiredCommandFragments: ["quality-lenses.md"],
		declaredReferences: ["quality-lenses.md", "operability-signals.md"],
	};
	const { report } = buildExecutionObservation({ spec, events: [] });
	assert.equal(report.coverage.declared, 2);
	assert.equal(report.coverage.declaredAll, 2);
	assert.deepEqual(report.coverage.inlineRefs, []);
	assert.deepEqual(report.coverage.dupRefs, []);
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

test("buildExecutionObservation surfaces additive efficiency metrics (output/tool_count/waste)", () => {
	const spec = {
		skillId: "hitl",
		evaluationId: "execution-hitl",
		targetId: "hitl",
		prompt: "/charness:hitl",
		requiredCommandFragments: [],
		declaredReferences: [],
	};
	const events = [
		assistantToolUse([{ name: "Read", input: { file_path: "/x/state.yaml" } }], { usage: { output_tokens: 7 } }),
		assistantToolUse([{ name: "Read", input: { file_path: "/x/state.yaml" } }], { usage: { output_tokens: 5 } }),
		assistantToolUse([{ name: "Bash", input: { command: "ls" } }], { usage: { output_tokens: 3 } }),
	];
	const { packet } = buildExecutionObservation({ spec, events });
	const m = packet.evaluations[0].metrics;
	assert.equal(m.tool_count, 3);
	assert.equal(m.output_tokens, 15);
	assert.equal(m.waste_smell_count, 1); // state.yaml read twice -> one duplicate_read smell
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

// #409 Gap 2: a committing/clean run renders its closeout LAST, after the on-disk
// session tree's final flush, so the tree can drop the block requiredSummaryFragments
// match against. The authoritative capture stdout (stream.jsonl) retains it; the fix
// reads the summary from a separate `finalTextEvents` stream while coverage/trace stay
// on the tree (a subagent's reference read lives ONLY in the tree, never in the stream).
test("finalTextEvents sources the closeout summary so a truncated tree is not a false MISS (#409 Gap 2)", () => {
	const spec = {
		skillId: "impl",
		evaluationId: "execution-impl",
		targetId: "impl",
		prompt: "/charness:impl",
		requiredCommandFragments: [],
		requiredSummaryFragments: ["ran-pass"],
		declaredReferences: [],
	};
	// Tree dropped the final closeout: its last parent text is the pre-commit critique line.
	const treeEvents = [
		assistantText("wrote the tests, ran pytest"),
		assistantText("Critique verdict: CLEAN; committing before closeout"),
	];
	// Authoritative stream retains the ran-pass closeout as the final parent block.
	const streamEvents = [
		...treeEvents,
		assistantText("## Lint Gate\n`ran-pass bash .githooks/pre-commit`"),
	];
	// Tree-only summary -> false MISS.
	assert.equal(buildExecutionObservation({ spec, events: treeEvents }).report.outcome, "failed");
	// Stream-sourced summary -> the RSF token matches -> PASS.
	const { report } = buildExecutionObservation({ spec, events: treeEvents, finalTextEvents: streamEvents });
	assert.equal(report.outcome, "passed");
	assert.equal(report.findings.length, 0);
});

test("finalTextEvents only sources the summary; coverage stays on the tree", () => {
	const spec = {
		skillId: "impl",
		evaluationId: "execution-impl",
		targetId: "impl",
		prompt: "/charness:impl",
		requiredCommandFragments: [],
		requiredSummaryFragments: ["ran-pass"],
		declaredReferences: ["depth-a.md"],
		referenceEngagement: { "depth-a.md": { engagement: "engage-always", rationale: "x", classTag: "DEPTH" } },
	};
	// The reference read is in the TREE only; the stream carries only the closeout text.
	const treeEvents = [
		assistantToolUse([{ name: "Read", input: { file_path: "/skills/public/impl/references/depth-a.md" } }]),
		assistantText("did the work"),
	];
	const streamEvents = [assistantText("closeout: `ran-pass`")];
	const { report } = buildExecutionObservation({ spec, events: treeEvents, finalTextEvents: streamEvents });
	assert.equal(report.outcome, "passed"); // ran-pass came from the stream
	assert.equal(report.coverage.declared, 1);
	assert.equal(report.coverage.covered, 1); // depth-a.md opened, seen in the TREE not the stream
});

test("runCli --stream sources the summary from the authoritative stdout, not the truncated tree", () => {
	const root = mkdtempSync(join(tmpdir(), "charness-stream-"));
	// Session tree: final parent block has NO ran-pass (dropped closeout).
	writeFileSync(
		join(root, "sess.jsonl"),
		`${JSON.stringify(assistantToolUse([{ name: "Bash", input: { command: "pytest" } }]))}\n` +
			`${JSON.stringify(assistantText("Critique verdict: CLEAN; committing"))}\n`,
	);
	// stream.jsonl: complete stdout with the ran-pass closeout as the final block.
	const streamPath = join(root, "stream.jsonl");
	writeFileSync(
		streamPath,
		`${JSON.stringify(assistantText("Critique verdict: CLEAN; committing"))}\n` +
			`${JSON.stringify(assistantText("## Lint Gate `ran-pass`"))}\n`,
	);
	const specPath = join(root, "spec.json");
	writeFileSync(
		specPath,
		JSON.stringify({
			skillId: "impl",
			evaluationId: "execution-impl",
			targetId: "impl",
			prompt: "/charness:impl",
			requiredCommandFragments: [],
			requiredSummaryFragments: ["ran-pass"],
			declaredReferences: [],
		}),
	);
	// Without --stream: tree-only summary -> false MISS.
	const failPath = join(root, "fail.json");
	runCli(["--session-tree", join(root, "sess.jsonl"), "--spec", specPath, "--output", failPath]);
	assert.equal(JSON.parse(readFileSync(failPath, "utf-8")).evaluations[0].outcome, "failed");
	// With --stream: closeout token matches -> PASS.
	const okPath = join(root, "ok.json");
	const code = runCli(["--session-tree", join(root, "sess.jsonl"), "--spec", specPath, "--stream", streamPath, "--output", okPath]);
	assert.equal(code, 0);
	assert.equal(JSON.parse(readFileSync(okPath, "utf-8")).evaluations[0].outcome, "passed");
});
