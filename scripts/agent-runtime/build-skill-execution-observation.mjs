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
import { basename, dirname, join, resolve } from "node:path";
import process from "node:process";

import { SKILL_EVALUATION_INPUTS_SCHEMA } from "./contract-versions.mjs";

// Tool-call input keys that name a concrete file the agent opened. Used only for
// the reference-coverage report; the command-log fragment match below sees every
// input value regardless of key.
const FILE_PATH_KEYS = ["file_path", "notebook_path"];

// Shell commands whose file operands count as a "read" for the coverage report.
// A real run routes to a reference as often via `sed -n` / `cat` / `rg` as via the
// Read tool, so coverage that counts only FILE_PATH_KEYS under-reports (the retro
// captures missed sed-read references this way). The floor matcher
// (requiredCommandFragments) is unaffected — it already substring-matches the full
// command log; this only sharpens the secondary coverage metric.
const READ_COMMANDS = new Set(["cat", "sed", "head", "tail", "less", "nl", "rg", "grep", "awk"]);
// Read commands whose FIRST non-flag operand is a script/pattern, NOT a file. We
// drop that operand so `grep "expert-lens.md" SKILL.md` counts SKILL.md and never
// the named-but-unopened pattern — coverage must not inherit the floor matcher's
// "named anywhere in the command log" blur.
const PATTERN_FIRST_COMMANDS = new Set(["sed", "rg", "grep", "awk"]);
// grep/rg/sed/awk flags that consume a SEPARATE following token as their value.
// Without this, `grep -m 5 PATTERN file` mis-slots: `5` is eaten as the pattern,
// so the real PATTERN (e.g. a `.md` reference name) falls into the file slot and
// over-counts. Attached forms (`-m5`, `-A3`, `--context=3`) are single
// `-`-prefixed tokens and need no entry. Pattern-supplying flags (`-e`/`-f` and
// long forms) ALSO mean the pattern came from the flag, so no positional operand
// should be dropped as the pattern afterward.
const PATTERN_SUPPLYING_FLAGS = new Set(["-e", "-f", "--regexp", "--file"]);
const VALUE_FLAGS = new Set([
	"-m", "-A", "-B", "-C", "-d", "-g", "-t",
	"--max-count", "--after-context", "--before-context", "--context", "--glob", "--type",
	...PATTERN_SUPPLYING_FLAGS,
]);

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
			// Recover for-loop batch reads: the assembled path exists only after
			// shell expansion, so append the expanded read commands so a primer set
			// read via `for f in ...; do cat "ref/$f.md"; done` is visible to the
			// fragment matcher, not a false-negative. The raw command text is already
			// pushed above, so the synthetic reads only ADD the contiguous path the
			// shell would have assembled. Only read-command bodies are expanded (an
			// `echo "$f.md"` is skipped) — that keeps the sharp COVERAGE metric honest
			// (an echo is not a read), the same reason expansion routes through
			// parseReadCommandBasenames in collectOpenedBasenames.
			if (typeof input.command === "string") {
				for (const cmd of expandForLoopReadCommands(input.command)) {
					parts.push(cmd);
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

// --- Efficiency trace (per-tool-call digest + deterministic waste lens) ---------
// The claim matcher reduces a run to pass/fail + coverage, which throws away the
// per-call material an intelligent efficiency review needs ("this step was
// wasteful"). The 2026-06-29 hitl capture proved the gap concretely: its full
// transcript lived only in the ephemeral capture dir and was deleted, leaving
// only count-level summaries. So build also emits a durable per-call trace digest
// into the bundle and runs a deterministic, advisory waste lens over it.

// floor-addition-restraint: these are SMELL thresholds for a NON-blocking advisory
// lens (printed + recorded, never a pass/fail gate), tuned to the real 2026-06-29
// hitl shape (state.yaml edited 3x). Two edits / one large read are normal; do not
// lower without a recorded recurrence.
const EDIT_REPEAT_SMELL = 3; // 3+ edits to ONE file = batch-into-one candidate
const BASH_REPEAT_SMELL = 2; // identical command run 2+ times = redundant run
const LARGE_OUTPUT_CHARS = 50000; // one tool result over ~50k chars = context-bloat candidate
const ARGS_DIGEST_MAX = 160;

// tool_use_id -> char length of the tool_result fed back. Powers the large_output
// smell and the per-call out_chars field.
export function collectToolResultSizes(events) {
	const sizes = new Map();
	for (const event of events) {
		const message = event && typeof event === "object" ? (event.message ?? event) : null;
		const content = Array.isArray(message?.content) ? message.content : [];
		for (const block of content) {
			if (!block || block.type !== "tool_result" || !block.tool_use_id) {
				continue;
			}
			const raw = block.content;
			let text = "";
			if (typeof raw === "string") {
				text = raw;
			} else if (Array.isArray(raw)) {
				text = raw
					.map((part) => (typeof part === "string" ? part : part && typeof part.text === "string" ? part.text : ""))
					.join("");
			}
			sizes.set(block.tool_use_id, text.length);
		}
	}
	return sizes;
}

function digestArgs(input) {
	const raw =
		input.file_path ?? input.notebook_path ?? input.command ?? input.path ?? input.pattern ?? input.skill ?? input.description ?? "";
	const flat = String(raw).replace(/\s+/g, " ").trim();
	return flat.length > ARGS_DIGEST_MAX ? `${flat.slice(0, ARGS_DIGEST_MAX)}…` : flat;
}

// One record per tool call, in chronological emit order: name, an args digest, the
// result size, the emitting assistant message's usage (shared across its tool
// calls — msg_tool_count makes that explicit), and the wall gap to the previous
// tool-emitting message. This is the durable material for a later efficiency
// review; it stores a digest, NOT the raw transcript (lighter, and no
// secret-bearing tool outputs land in the committed bundle).
export function collectToolTrace(events, { resultSizes = null } = {}) {
	const sizes = resultSizes ?? collectToolResultSizes(events);
	const records = [];
	let step = 0;
	let prevTs = null;
	for (const event of events) {
		if (!event || event.type !== "assistant") {
			continue;
		}
		const message = event.message ?? {};
		const content = Array.isArray(message.content) ? message.content : [];
		const toolUses = content.filter((block) => block && block.type === "tool_use");
		if (toolUses.length === 0) {
			continue;
		}
		const usage = message.usage && typeof message.usage === "object" ? message.usage : {};
		const ts = typeof event.timestamp === "string" ? Date.parse(event.timestamp) : NaN;
		let gap = null;
		if (!Number.isNaN(ts)) {
			gap = prevTs === null ? null : ts - prevTs;
			prevTs = ts;
		}
		toolUses.forEach((block, indexInMsg) => {
			step += 1;
			const id = block.id;
			records.push({
				step,
				track: event.isSidechain ? "sub" : "parent",
				name: String(block.name ?? "unknown"),
				args: digestArgs(block.input ?? {}),
				out_chars: id !== undefined && sizes.has(id) ? sizes.get(id) : null,
				msg_out_tokens: Number(usage.output_tokens) || 0,
				msg_cache_read: Number(usage.cache_read_input_tokens) || 0,
				msg_tool_count: toolUses.length,
				// Attribute the wall gap to the FIRST call of the message only, so a sum
				// over records approximates total tool wall without double-counting.
				wall_ms: indexInMsg === 0 ? gap : 0,
			});
		});
	}
	return records;
}

// Deterministic, advisory "this was inefficient" smells. NOT a pass/fail gate —
// the outcome stays claim-matcher-only. Each flag is a candidate for an
// intelligent review to confirm or dismiss, never a verdict on its own.
export function detectWaste(events, { trace = null } = {}) {
	const reads = new Map();
	const edits = new Map();
	const bash = new Map();
	for (const event of events) {
		for (const block of toolUseBlocks(event)) {
			const name = String(block.name ?? "");
			const input = block.input ?? {};
			const path =
				typeof input.file_path === "string" ? input.file_path : typeof input.notebook_path === "string" ? input.notebook_path : null;
			if (name === "Read" && path) {
				reads.set(path, (reads.get(path) ?? 0) + 1);
			} else if ((name === "Edit" || name === "Write" || name === "NotebookEdit") && path) {
				edits.set(path, (edits.get(path) ?? 0) + 1);
			} else if (name === "Bash" && typeof input.command === "string" && input.command.trim()) {
				const cmd = input.command.trim();
				bash.set(cmd, (bash.get(cmd) ?? 0) + 1);
			}
		}
	}
	const flags = [];
	for (const [path, count] of reads) {
		if (count > 1) {
			flags.push({ kind: "duplicate_read", count, detail: `${basename(path)} read ${count}x`, path });
		}
	}
	for (const [path, count] of edits) {
		if (count >= EDIT_REPEAT_SMELL) {
			flags.push({ kind: "repeated_edit", count, detail: `${basename(path)} edited ${count}x (batch into one?)`, path });
		}
	}
	for (const [cmd, count] of bash) {
		if (count >= BASH_REPEAT_SMELL) {
			const short = cmd.length > 60 ? `${cmd.slice(0, 60)}…` : cmd;
			flags.push({ kind: "repeated_bash", count, detail: `\`${short}\` run ${count}x` });
		}
	}
	for (const record of trace ?? []) {
		if (typeof record.out_chars === "number" && record.out_chars > LARGE_OUTPUT_CHARS) {
			flags.push({
				kind: "large_output",
				count: record.out_chars,
				detail: `step ${record.step} ${record.name} → ${record.out_chars} chars`,
				step: record.step,
			});
		}
	}
	return flags;
}

// Split a shell command line into simple commands (each an array of tokens),
// respecting single/double quotes and breaking on unquoted separators, pipes, and
// redirections. Breaking on `|`/`<`/`>` is deliberate: a piped-stdin reader
// (`git show X | head -30`) and a redirect target (`> out.md`) must NOT look like a
// file the read command opened. This is a deliberately small shell-ish tokenizer,
// not a full parser — enough to find file operands of read commands.
function tokenizeShellish(command) {
	const simples = [];
	let current = [];
	let token = "";
	let hasToken = false;
	let quote = null;
	const pushToken = () => {
		if (hasToken) {
			current.push(token);
			token = "";
			hasToken = false;
		}
	};
	const pushSimple = () => {
		pushToken();
		if (current.length) {
			simples.push(current);
			current = [];
		}
	};
	const text = String(command);
	for (let index = 0; index < text.length; index += 1) {
		const ch = text[index];
		if (quote) {
			if (ch === quote) {
				quote = null;
			} else {
				token += ch;
				hasToken = true;
			}
			continue;
		}
		if (ch === "'" || ch === '"') {
			quote = ch;
			hasToken = true;
			continue;
		}
		if (ch === " " || ch === "\t" || ch === "\r") {
			pushToken();
			continue;
		}
		if ("\n;|&<>()`".includes(ch)) {
			pushSimple();
			continue;
		}
		if (ch === "\\") {
			const next = text[index + 1];
			if (next === "\n") {
				pushToken();
				index += 1;
				continue;
			}
			if (next !== undefined) {
				token += next;
				hasToken = true;
				index += 1;
				continue;
			}
			continue;
		}
		token += ch;
		hasToken = true;
	}
	pushSimple();
	return simples;
}

// A token is a file operand only if it is not a flag and looks like a path:
// either it contains a `/` or it ends in a short extension. This excludes flags
// (`-n`), numeric flag values (`30` from `head -n 30`), and sed scripts
// (`'1,120p'`) without per-tool flag-arity bookkeeping.
function looksLikePath(token) {
	if (!token || token.startsWith("-")) {
		return false;
	}
	return token.includes("/") || /\.[A-Za-z0-9]{1,8}$/.test(token);
}

// Basenames of files a shell read command (cat/sed/head/tail/less/rg/grep/awk)
// opens. Pattern/script operands of grep/rg/awk/sed are dropped so a reference
// named in a search pattern is never miscounted as opened.
export function parseReadCommandBasenames(command) {
	const found = new Set();
	for (const tokens of tokenizeShellish(command)) {
		if (tokens.length === 0) {
			continue;
		}
		const name = basename(tokens[0]);
		if (!READ_COMMANDS.has(name)) {
			continue;
		}
		let patternDropped = !PATTERN_FIRST_COMMANDS.has(name);
		for (let index = 1; index < tokens.length; index += 1) {
			const tok = tokens[index];
			if (tok.startsWith("-")) {
				if (VALUE_FLAGS.has(tok)) {
					index += 1; // consume the flag's separate value token
				}
				if (PATTERN_SUPPLYING_FLAGS.has(tok)) {
					patternDropped = true; // pattern came from the flag; positional operands are files
				}
				continue;
			}
			if (!patternDropped) {
				patternDropped = true; // the first positional operand is the script/pattern
				continue;
			}
			if (looksLikePath(tok)) {
				found.add(basename(tok));
			}
		}
	}
	return found;
}

const LOOP_VAR_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;

// A `for` list token is statically expandable only when it has no shell
// construct the analyzer cannot resolve: no nested $var, command substitution,
// glob, brace/seq, or subshell. A non-literal list is left unexpanded.
function isLiteralLoopToken(token) {
	return token.length > 0 && !/[$*?`{}()[\]]/.test(token);
}

// Replace $VAR and ${VAR} (whole-name only) in one token with the literal value.
// varName is validated against LOOP_VAR_RE, so it is safe to inject into a regex.
function substituteLoopVar(token, varName, value) {
	return token
		.replace(new RegExp(`\\$\\{${varName}\\}`, "g"), value)
		.replace(new RegExp(`\\$${varName}(?![A-Za-z0-9_])`, "g"), value);
}

// Expand `for VAR in TOK1 TOK2 ...; do BODY; done` over a LITERAL token list into
// the concrete read commands (cat/sed/head/...) each iteration actually runs,
// substituting each token for $VAR/${VAR} in the body's read commands. An agent
// that batch-reads its primer set with one for-loop genuinely opens every file,
// but the assembled path exists only after shell expansion — which the static
// command log never captures — so a non-expanding matcher false-negatives the
// whole batch (e.g. `for f in quality-lenses ...; do cat "references/$f.md"; done`
// reads quality-lenses.md yet the literal "quality-lenses.md" never appears).
// This recovers those reads. Only literal for-lists are expanded (no globs, seqs,
// or command substitution) and only read-command bodies are emitted (an
// `echo "$f.md"` is not a read), so it mirrors a deterministic shell expansion and
// never invents a read the run did not perform.
export function expandForLoopReadCommands(command) {
	const simples = tokenizeShellish(command);
	const expanded = new Set();
	for (let i = 0; i < simples.length; i += 1) {
		const head = simples[i];
		if (head.length < 4 || head[0] !== "for" || head[2] !== "in") {
			continue;
		}
		const varName = head[1];
		if (!LOOP_VAR_RE.test(varName)) {
			continue;
		}
		const values = head.slice(3);
		if (values.length === 0 || !values.every(isLiteralLoopToken)) {
			continue;
		}
		for (let j = i + 1; j < simples.length; j += 1) {
			let body = simples[j];
			if (body.length === 0) {
				continue;
			}
			if (body[0] === "do") {
				body = body.slice(1); // the first body simple carries the `do` keyword
			}
			if (body.length === 0) {
				continue;
			}
			if (body[0] === "done") {
				break;
			}
			if (!READ_COMMANDS.has(basename(body[0]))) {
				continue;
			}
			for (const value of values) {
				expanded.add(body.map((tok) => substituteLoopVar(tok, varName, value)).join(" "));
			}
		}
	}
	return [...expanded];
}

// Basenames of every file opened anywhere in the tree, via a path-bearing tool
// call (Read/Edit/Write) OR a shell read command (Bash). Powers the
// declared-reference coverage report.
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
			if (typeof input.command === "string" && input.command.trim()) {
				for (const name of parseReadCommandBasenames(input.command)) {
					names.add(name);
				}
				for (const cmd of expandForLoopReadCommands(input.command)) {
					for (const name of parseReadCommandBasenames(cmd)) {
						names.add(name);
					}
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
	const resultSizes = collectToolResultSizes(events);
	const trace = collectToolTrace(events, { resultSizes });
	const waste = detectWaste(events, { trace });
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
	const wastePart = waste.length > 0
		? ` Waste smells: ${waste.length} (${[...new Set(waste.map((flag) => flag.kind))].join(", ")}).`
		: "";
	const summary =
		`Execution of /${spec.targetId}: ${tokens.total} total tokens ` +
		`(${tokens.output} output, ${tokens.cacheRead} cache-read)` +
		`${duration !== null ? `, ${duration}ms wall` : ""}.` +
		`${profileLine ? ` Tool profile: ${profileLine}.` : ""}` +
		`${claimPart}${coveragePart}${wastePart}`;

	// metrics carries the headline budget numbers (cautilus applies its
	// max_total_tokens/max_duration_ms thresholds against total_tokens/duration_ms)
	// plus additive efficiency fields the A/B harness aggregates across runs. These
	// are advisory measurements, not pass/fail floors; surfacing them here lets the
	// A/B runner read one canonical per-run file instead of re-deriving waste logic.
	const metrics = {
		total_tokens: tokens.total,
		output_tokens: tokens.output,
		tool_count: trace.length,
		waste_smell_count: waste.length,
	};
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
			trace,
			waste,
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
    [--output <observed.v1.json>] [--trace-digest <trace-digest.jsonl>]

Reads every *.jsonl under the session tree (parent + subagents), applies the
spec's claim matchers (requiredCommandFragments / requiredSummaryFragments) over
the full-tree command log + final summary, reports declared-reference coverage,
and emits a cautilus.skill_evaluation_inputs.v1 observed packet for
\`cautilus evaluate observation\`. A human-readable claim/coverage line is printed
to stderr.

It also writes a per-tool-call efficiency trace (\`trace-digest.jsonl\`, default
next to --output) and runs a deterministic, advisory waste lens, printing any
smells plus a paste-ready \`## Efficiency\` finding block to stderr. Run --output
INTO the durable bundle dir so the trace survives the ephemeral capture cleanup.
`;

export function runCli(argv, { readFile = readJson } = {}) {
	const options = { sessionTree: null, spec: null, output: null, traceDigest: null };
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
		} else if (arg === "--trace-digest") {
			options.traceDigest = value;
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

	// Durable per-call trace digest: defaults next to --output so it lands in the
	// same (durable) bundle dir, surviving the ephemeral capture cleanup.
	const traceDigestPath =
		options.traceDigest ?? (options.output ? join(dirname(options.output), "trace-digest.jsonl") : null);
	if (traceDigestPath) {
		const lines = report.trace.map((record) => JSON.stringify(record)).join("\n");
		writeFileSync(traceDigestPath, lines.length ? `${lines}\n` : "");
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

	// Advisory efficiency lens: print smells + a paste-ready finding.md block.
	if (report.waste.length > 0) {
		process.stderr.write(`waste smells (${report.waste.length}): ${report.waste.map((flag) => flag.detail).join("; ")}\n`);
		process.stderr.write("--- paste-ready finding.md block ---\n");
		process.stderr.write("## Efficiency\n\n");
		process.stderr.write(`- trace: \`trace-digest.jsonl\` (${report.trace.length} tool calls)\n`);
		for (const flag of report.waste) {
			process.stderr.write(`- waste smell (${flag.kind}): ${flag.detail} — confirm or dismiss on review\n`);
		}
		process.stderr.write("--- end block ---\n");
	} else {
		process.stderr.write(`waste smells: none (${report.trace.length} tool calls traced)\n`);
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
