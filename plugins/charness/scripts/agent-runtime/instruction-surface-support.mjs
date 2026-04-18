import {
	existsSync,
	lstatSync,
	mkdirSync,
	readFileSync,
	readlinkSync,
	rmSync,
	symlinkSync,
	writeFileSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";
import process from "node:process";

const ROOT_ENTRY_ALIASES = ["AGENTS.md", "CLAUDE.md"];

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

function optionalString(value, field) {
	if (value === undefined || value === null) {
		return null;
	}
	if (typeof value !== "string") {
		throw new Error(`${field} must be a string`);
	}
	return value.trim() ? value : null;
}

export function artifactRef(kind, path) {
	return { kind, path };
}

function normalizeRoutingField(value, key) {
	if (!value) {
		return value;
	}
	if (/^none\b/i.test(value)) {
		return "none";
	}
	if ((key === "selectedSkill" || key === "selectedSupport") && value.startsWith("charness:")) {
		return value.slice("charness:".length);
	}
	if (key === "firstToolCall") {
		if (value === "exec_command") {
			return "functions.exec_command";
		}
		if (value.startsWith("functions.exec_command")) {
			return "functions.exec_command";
		}
		if (value.startsWith("web.")) {
			return value.split(/[:\s]/, 1)[0];
		}
	}
	return value;
}

export function normalizeRoutingDecision(value, field = "observed.routingDecision") {
	if (value === undefined || value === null) {
		return {};
	}
	const record = assertObject(value, field);
	const normalized = {};
	for (const key of ["selectedSkill", "selectedSupport", "firstToolCall", "reasonSummary"]) {
		const text = normalizeRoutingField(optionalString(record[key], `${field}.${key}`), key);
		if (text) {
			normalized[key] = text;
		}
	}
	return normalized;
}

export function backendFailureResult(message) {
	return {
		observationStatus: "blocked",
		blockerKind: "runner_execution_failed",
		summary: message,
		entryFile: "",
		loadedInstructionFiles: [],
		loadedSupportingFiles: [],
		routingDecision: {
			selectedSkill: "",
			selectedSupport: "",
			firstToolCall: "",
			reasonSummary: message,
		},
	};
}

function safeWorkspacePath(workspace, relativePath) {
	const trimmed = assertString(relativePath, "instruction surface file path");
	const resolved = resolve(workspace, trimmed);
	const workspaceRoot = `${resolve(workspace)}${process.platform === "win32" ? "\\" : "/"}`;
	if (resolved !== resolve(workspace) && !resolved.startsWith(workspaceRoot)) {
		throw new Error(`instruction surface path escapes workspace: ${relativePath}`);
	}
	return resolved;
}

function artifactPathForFile(outputDir, relativePath, suffix = "") {
	return join(outputDir, "instruction-surface", `${relativePath}${suffix}`);
}

function writeInstructionArtifact(outputDir, relativePath, content, suffix = "") {
	const artifactPath = artifactPathForFile(outputDir, relativePath, suffix);
	mkdirSync(dirname(artifactPath), { recursive: true });
	writeFileSync(artifactPath, content, "utf-8");
	return artifactPath;
}

function captureWorkspaceInstructionFiles(workspace, outputDir) {
	const files = [];
	const artifactRefs = [];
	for (const relativePath of ROOT_ENTRY_ALIASES) {
		const workspacePath = join(workspace, relativePath);
		if (!existsSync(workspacePath)) {
			continue;
		}
		const stat = lstatSync(workspacePath);
		if (stat.isDirectory()) {
			continue;
		}
		if (stat.isSymbolicLink()) {
			const targetPath = readlinkSync(workspacePath);
			const artifactPath = writeInstructionArtifact(outputDir, relativePath, `${targetPath}\n`, ".symlink.txt");
			files.push({
				path: relativePath,
				kind: "symlink",
				sourceKind: "workspace_default",
				targetPath,
				artifactPath,
			});
			artifactRefs.push(artifactRef("instruction_surface", artifactPath));
			continue;
		}
		const content = readFileSync(workspacePath, "utf-8");
		const artifactPath = writeInstructionArtifact(outputDir, relativePath, content);
		files.push({
			path: relativePath,
			kind: "file",
			sourceKind: "workspace_default",
			artifactPath,
		});
		artifactRefs.push(artifactRef("instruction_surface", artifactPath));
	}
	return {
		instructionSurface: {
			surfaceLabel: "workspace_checked_in",
			files,
		},
		artifactRefs,
		restore() {},
	};
}

function snapshotWorkspaceEntry(workspacePath) {
	if (!existsSync(workspacePath)) {
		return { kind: "missing", workspacePath };
	}
	const stat = lstatSync(workspacePath);
	if (stat.isDirectory()) {
		throw new Error(`instruction surface path points to a directory: ${workspacePath}`);
	}
	if (stat.isSymbolicLink()) {
		return {
			kind: "symlink",
			workspacePath,
			targetPath: readlinkSync(workspacePath),
		};
	}
	return {
		kind: "file",
		workspacePath,
		content: readFileSync(workspacePath),
	};
}

function restoreWorkspaceEntry(snapshot) {
	rmSync(snapshot.workspacePath, { force: true, recursive: false });
	if (snapshot.kind === "missing") {
		return;
	}
	mkdirSync(dirname(snapshot.workspacePath), { recursive: true });
	if (snapshot.kind === "symlink") {
		symlinkSync(snapshot.targetPath, snapshot.workspacePath);
		return;
	}
	writeFileSync(snapshot.workspacePath, snapshot.content);
}

function resolveInstructionContent(casesFile, file) {
	if (file.content) {
		return {
			content: file.content,
			sourceKind: "inline",
			sourceFile: null,
		};
	}
	const sourceFile = resolve(dirname(casesFile), file.sourceFile);
	return {
		content: readFileSync(sourceFile, "utf-8"),
		sourceKind: "source_file",
		sourceFile,
	};
}

function maskUnspecifiedRootEntryAliases(workspace, files) {
	const backups = [];
	const specified = new Set(files.map((file) => file.path));
	for (const relativePath of ROOT_ENTRY_ALIASES) {
		if (specified.has(relativePath)) {
			continue;
		}
		const workspacePath = safeWorkspacePath(workspace, relativePath);
		backups.push(snapshotWorkspaceEntry(workspacePath));
		rmSync(workspacePath, { force: true, recursive: false });
	}
	return backups;
}

export function materializeInstructionSurface(options, evaluation, outputDir) {
	if (!evaluation.instructionSurface) {
		return captureWorkspaceInstructionFiles(options.workspace, outputDir);
	}
	const backups = maskUnspecifiedRootEntryAliases(options.workspace, evaluation.instructionSurface.files);
	const files = [];
	const artifactRefs = [];
	for (const file of evaluation.instructionSurface.files) {
		const workspacePath = safeWorkspacePath(options.workspace, file.path);
		backups.push(snapshotWorkspaceEntry(workspacePath));
		rmSync(workspacePath, { force: true, recursive: false });
		mkdirSync(dirname(workspacePath), { recursive: true });
		if (file.kind === "symlink") {
			symlinkSync(file.targetPath, workspacePath);
			const artifactPath = writeInstructionArtifact(outputDir, file.path, `${file.targetPath}\n`, ".symlink.txt");
			files.push({
				path: file.path,
				kind: "symlink",
				sourceKind: "inline_symlink",
				targetPath: file.targetPath,
				artifactPath,
			});
			artifactRefs.push(artifactRef("instruction_surface", artifactPath));
			continue;
		}
		const resolved = resolveInstructionContent(options.casesFile, file);
		writeFileSync(workspacePath, resolved.content, "utf-8");
		const artifactPath = writeInstructionArtifact(outputDir, file.path, resolved.content);
		files.push({
			path: file.path,
			kind: "file",
			sourceKind: resolved.sourceKind,
			...(resolved.sourceFile ? { sourceFile: resolved.sourceFile } : {}),
			artifactPath,
		});
		artifactRefs.push(artifactRef("instruction_surface", artifactPath));
		if (resolved.sourceFile) {
			artifactRefs.push(artifactRef("instruction_surface_source", resolved.sourceFile));
		}
	}
	return {
		instructionSurface: {
			surfaceLabel: evaluation.instructionSurface.surfaceLabel,
			files,
		},
		artifactRefs,
		restore() {
			for (const snapshot of backups.reverse()) {
				restoreWorkspaceEntry(snapshot);
			}
		},
	};
}

export function relativizeObservedPath(workspace, observedPath) {
	if (typeof observedPath !== "string" || !observedPath.trim()) {
		return observedPath;
	}
	let trimmed = observedPath.trim();
	const markdownLinkMatch = /^\[[^\]]+\]\(([^)]+)\)$/.exec(trimmed);
	if (markdownLinkMatch) {
		trimmed = markdownLinkMatch[1];
	}
	for (const alias of ROOT_ENTRY_ALIASES) {
		if (trimmed === alias || trimmed.startsWith(`${alias} `)) {
			return alias;
		}
	}
	const workspaceRoot = resolve(workspace);
	const resolvedPath = resolve(trimmed);
	if (resolvedPath === workspaceRoot) {
		return ".";
	}
	const prefix = `${workspaceRoot}${process.platform === "win32" ? "\\" : "/"}`;
	if (!resolvedPath.startsWith(prefix)) {
		return trimmed;
	}
	return resolvedPath.slice(prefix.length).replaceAll("\\", "/");
}
