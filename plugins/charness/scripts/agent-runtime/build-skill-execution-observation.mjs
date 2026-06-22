#!/usr/bin/env node

// Build a `cautilus.skill_evaluation_inputs.v1` observed packet for ONE real
// execution of a skill, from the full Claude Code session-log tree
// (parent `<session>.jsonl` + `<session>/subagents/*.jsonl`).
//
// Why the whole tree, not the parent stdout: a real skill run delegates work to
// subagents, and a subagent's tool calls (including the Read of a reference it
// was routed to) live ONLY in its `subagents/*.jsonl`. A parent-stdout-only
// extractor silently misses them — the blind spot that made an earlier
// transcript-grep capture undercount coverage. This reads every jsonl under the
// session tree so delegated reference reads are counted.
//
// Division of ownership (cautilus skill-evaluation.md): the HOST owns invocation,
// transcript capture, and matching; cautilus `evaluate observation` consumes the
// emitted packet, applies the declared thresholds (`max_total_tokens` /
// `max_duration_ms`) for the `runtime_budget_respect` degrade, and rolls the
// outcome into a recommendation. So this script is the host-side matcher: it runs
// the claim assertions (fragment matchers over the command log + final summary)
// and reports reference coverage, then hands cautilus a packet to score.
//
// Outcome is set from the claim matchers only (passed/failed). Budget drift is
// left to cautilus's threshold degrade so the two signals stay separable.

import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import process from "node:process";

import { SKILL_EVALUATION_INPUTS_SCHEMA } from "./contract-versions.mjs";

// Tool-call input keys that name a concrete file the agent opened. Used only for
// the reference-coverage report; the command-log fragment match below sees every
// input value regardless of key.
const FILE_PATH_KEYS = ["file_path", "notebook_path"];

export function listSessionTreeJsonl(root) {
	const out = [];
	const walk = (dir) => {
		let entries;
		try {
			entries = readdirSync(dir);
		} catch {
			return;
		}
		for (const name of entries) {
			const full = join(dir, name);
			let st;
			try {
				st = statSync(full);
			} catch {
				continue;
			}
			if (st.isDirectory()) {
				walk(full);
			} else if (name.endsWith(".jsonl")) {
				out.push(full);
			}
		}
	};
	const st = statSync(root);
	if (st.isDirectory()) {
		walk(root);
	} else if (root.endsWith(".jsonl")) {
		out.push(root);
	}
	return out.sort();
}

export function parseEventsFromFiles(files, { readText = (p) => readFileSync(p, "utf-8") } = {}) {
	const events = [];
	for (const file of files) {
		for (const line of String(readText(file)).split("\n")) {
			const trimmed = line.trim();
			if (!trimmed) {
				continue;
			}
			try {
				events.push(JSON.parse(trimmed));
			} catch {
				// Non-JSON lines are skipped, not fatal.
			}
		}
	}
	return events;
}

function toolUseBlocks(event) {
	const message = event && typeof event === "object" ? (event.message ?? event) : null;
	const content = Array.isArray(message?.content) ? message.content : [];
	return content.filter((block) => block && typeof block === "object" && block.type === "tool_use");
}

// One newline-joined string of every tool-call input value across the tree:
// Bash commands, Read/Edit/Write paths, etc. Fragment matchers run against this,
// so a routed reference read shows up as its absolute path containing the
// reference basename.
export function collectCommandLog(events) {
	const parts = [];
	for (const event of events) {
		for (const block of toolUseBlocks(event)) {
			parts.push(String(block.name ?? ""));
			const input = block.input ?? {};
			for (const value of Object.values(input)) {
				if (typeof value === "string") {
					parts.push(value);
				} else if (Array.isArray(value)) {
					parts.push(value.filter((entry) => typeof entry === "string").join(" "));
				}
			}
		}
	}
	return parts.join("\n");
}

// Tool-call counts across the tree, keyed by tool name. The Bash-vs-Read ratio
// is the headline "gate-dominated, judgment-starved" signal: many gate runs, few
// reference reads.
export function collectToolProfile(events) {
	const profile = {};
	for (const event of events) {
		for (const block of toolUseBlocks(event)) {
			const name = String(block.name ?? "unknown");
			profile[name] = (profile[name] ?? 0) + 1;
		}
	}
	return profile;
}

// Basenames of every file opened via a path-bearing tool call, anywhere in the
// tree. Powers the declared-reference coverage report.
export function collectOpenedBasenames(events) {
	const names = new Set();
	for (const event of events) {
		for (const block of toolUseBlocks(event)) {
			const input = block.input ?? {};
			for (const key of FILE_PATH_KEYS) {
				const value = input[key];
				if (typeof value === "string" && value.trim()) {
					names.add(basename(value.trim()));
				}
			}
		}
	}
	return names;
}

export function sumTokens(events) {
	const totals = { input: 0, output: 0, cacheCreation: 0, cacheRead: 0 };
	for (const event of events) {
		if (!event || event.type !== "assistant") {
			continue;
		}
		const usage = event.message?.usage;
		if (!usage || typeof usage !== "object") {
			continue;
		}
		totals.input += Number(usage.input_tokens) || 0;
		totals.output += Number(usage.output_tokens) || 0;
		totals.cacheCreation += Number(usage.cache_creation_input_tokens) || 0;
		totals.cacheRead += Number(usage.cache_read_input_tokens) || 0;
	}
	totals.total = totals.input + totals.output + totals.cacheCreation + totals.cacheRead;
	return totals;
}

export function durationMs(events) {
	const stamps = [];
	for (const event of events) {
		const ts = event && typeof event === "object" ? event.timestamp : null;
		if (typeof ts === "string") {
			const parsed = Date.parse(ts);
			if (!Number.isNaN(parsed)) {
				stamps.push(parsed);
			}
		}
	}
	if (stamps.length < 2) {
		return null;
	}
	return Math.max(...stamps) - Math.min(...stamps);
}

export function earliestTimestamp(events) {
	let best = null;
	for (const event of events) {
		const ts = event && typeof event === "object" ? event.timestamp : null;
		if (typeof ts === "string" && (best === null || ts < best)) {
			best = ts;
		}
	}
	return best;
}

// Final assistant text from the PARENT track (non-sidechain). This is the skill's
// own concluding report — what summary-fragment claims are checked against.
export function finalAssistantText(events) {
	let text = "";
	for (const event of events) {
		if (!event || event.type !== "assistant" || event.isSidechain) {
			continue;
		}
		const content = event.message?.content;
		if (!Array.isArray(content)) {
			continue;
		}
		const joined = content
			.filter((block) => block && block.type === "text" && typeof block.text === "string")
			.map((block) => block.text)
			.join("\n");
		if (joined.trim()) {
			text = joined;
		}
	}
	return text;
}

function fragmentFindings(label, text, requiredFragments, forbiddenFragments) {
	if (text === null || text === undefined) {
		return [];
	}
	const normalized = String(text).toLowerCase();
	const findings = [];
	for (const fragment of requiredFragments ?? []) {
		if (!normalized.includes(String(fragment).toLowerCase())) {
			findings.push(`${label} missing required fragment: ${fragment}`);
		}
	}
	for (const fragment of forbiddenFragments ?? []) {
		if (normalized.includes(String(fragment).toLowerCase())) {
			findings.push(`${label} included forbidden fragment: ${fragment}`);
		}
	}
	return findings;
}

export function buildExecutionObservation({ spec, events } = {}) {
	if (!spec || typeof spec !== "object") {
		throw new Error("spec must be an object");
	}
	for (const field of ["skillId", "evaluationId", "targetId", "prompt"]) {
		if (typeof spec[field] !== "string" || !spec[field].trim()) {
			throw new Error(`spec.${field} must be a non-empty string`);
		}
	}
	const commandLog = collectCommandLog(events);
	const summaryText = finalAssistantText(events);
	const opened = collectOpenedBasenames(events);
	const tokens = sumTokens(events);
	const duration = durationMs(events);
	const startedAt = earliestTimestamp(events);
	const toolProfile = collectToolProfile(events);
	const profileLine = Object.entries(toolProfile)
		.sort((a, b) => b[1] - a[1])
		.map(([name, count]) => `${name}=${count}`)
		.join(" ");

	const declared = Array.isArray(spec.declaredReferences) ? spec.declaredReferences : [];
	const covered = declared.filter((ref) => opened.has(ref));
	const missing = declared.filter((ref) => !opened.has(ref));

	const findings = [
		...fragmentFindings("command log", commandLog, spec.requiredCommandFragments, spec.forbiddenCommandFragments),
		...fragmentFindings("summary", summaryText, spec.requiredSummaryFragments, spec.forbiddenSummaryFragments),
	];
	const outcome = findings.length > 0 ? "failed" : "passed";

	const coveragePart = declared.length > 0
		? ` Reference coverage: ${covered.length}/${declared.length} declared references opened` +
			`${missing.length > 0 ? ` (missing: ${missing.join(", ")})` : ""}.`
		: "";
	const claimPart = findings.length > 0
		? ` Claim failures: ${findings.join("; ")}.`
		: " All declared claims met.";
	const summary =
		`Execution of /${spec.targetId}: ${tokens.total} total tokens ` +
		`(${tokens.output} output, ${tokens.cacheRead} cache-read)` +
		`${duration !== null ? `, ${duration}ms wall` : ""}.` +
		`${profileLine ? ` Tool profile: ${profileLine}.` : ""}` +
		`${claimPart}${coveragePart}`;

	const metrics = { total_tokens: tokens.total };
	if (duration !== null) {
		metrics.duration_ms = duration;
	}

	const evaluation = {
		evaluationId: spec.evaluationId,
		targetKind: spec.targetKind ?? "public_skill",
		targetId: spec.targetId,
		displayName: spec.skillDisplayName ?? spec.targetId,
		evaluationKind: "execution",
		prompt: spec.prompt,
		...(startedAt ? { startedAt } : {}),
		invoked: true,
		summary,
		outcome,
		metrics,
		sampling: {
			sampleCount: 1,
			consensusCount: 1,
			invokedCount: 1,
			stable: true,
			statusCounts: {
				passed: outcome === "passed" ? 1 : 0,
				degraded: 0,
				blocked: 0,
				failed: outcome === "failed" ? 1 : 0,
			},
		},
		...(spec.thresholds && typeof spec.thresholds === "object" ? { thresholds: spec.thresholds } : {}),
	};

	return {
		packet: {
			schemaVersion: SKILL_EVALUATION_INPUTS_SCHEMA,
			skillId: spec.skillId,
			skillDisplayName: spec.skillDisplayName ?? spec.skillId,
			evaluations: [evaluation],
		},
		report: {
			outcome,
			findings,
			coverage: { declared: declared.length, covered: covered.length, coveredRefs: covered, missingRefs: missing },
			metrics,
			tokens,
			toolProfile,
		},
	};
}

function readJson(path) {
	return JSON.parse(readFileSync(path, "utf-8"));
}

const USAGE = `Usage:
  node ./scripts/agent-runtime/build-skill-execution-observation.mjs \\
    --session-tree <projDir-or-session.jsonl> \\
    --spec <spec.json> \\
    [--output <observed.v1.json>]

Reads every *.jsonl under the session tree (parent + subagents), applies the
spec's claim matchers (requiredCommandFragments / requiredSummaryFragments) over
the full-tree command log + final summary, reports declared-reference coverage,
and emits a cautilus.skill_evaluation_inputs.v1 observed packet for
\`cautilus evaluate observation\`. A human-readable claim/coverage line is printed
to stderr.
`;

export function runCli(argv, { readFile = readJson } = {}) {
	const options = { sessionTree: null, spec: null, output: null };
	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		if (arg === "-h" || arg === "--help") {
			process.stdout.write(USAGE);
			return 0;
		}
		const value = argv[index + 1];
		if (arg === "--session-tree") {
			options.sessionTree = value;
		} else if (arg === "--spec") {
			options.spec = value;
		} else if (arg === "--output") {
			options.output = value;
		} else {
			throw new Error(`Unknown argument: ${arg}`);
		}
		if (value === undefined) {
			throw new Error(`Missing value for ${arg}`);
		}
		index += 1;
	}
	if (!options.sessionTree) {
		throw new Error("--session-tree is required");
	}
	if (!options.spec) {
		throw new Error("--spec is required");
	}
	const spec = readFile(options.spec);
	const files = listSessionTreeJsonl(resolve(options.sessionTree));
	if (files.length === 0) {
		throw new Error(`No *.jsonl found under ${options.sessionTree}`);
	}
	const events = parseEventsFromFiles(files);
	const { packet, report } = buildExecutionObservation({ spec, events });
	const serialized = `${JSON.stringify(packet, null, 2)}\n`;
	if (options.output) {
		writeFileSync(options.output, serialized);
	} else {
		process.stdout.write(serialized);
	}
	process.stderr.write(
		`outcome=${report.outcome} | jsonl files=${files.length} | ` +
			`coverage=${report.coverage.covered}/${report.coverage.declared} | ` +
			`total_tokens=${report.metrics.total_tokens}` +
			`${report.metrics.duration_ms !== undefined ? ` | duration_ms=${report.metrics.duration_ms}` : ""} | ` +
			`tools: ${Object.entries(report.toolProfile).sort((a, b) => b[1] - a[1]).map(([n, c]) => `${n}=${c}`).join(" ")}\n`,
	);
	if (report.findings.length > 0) {
		process.stderr.write(`claim failures: ${report.findings.join("; ")}\n`);
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
