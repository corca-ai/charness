import { INSTRUCTION_SURFACE_CASES_SCHEMA } from "./contract-versions.mjs";

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
	return assertString(value, field);
}

function normalizePathList(value, field) {
	if (value === undefined || value === null) {
		return [];
	}
	if (!Array.isArray(value)) {
		throw new Error(`${field} must be an array`);
	}
	return value.map((entry, index) => assertString(entry, `${field}[${index}]`));
}

function normalizeExpectedRouting(value, field) {
	if (value === undefined || value === null) {
		return null;
	}
	const record = assertObject(value, field);
	const normalized = {};
	for (const key of ["selectedSkill", "selectedSupport", "firstToolCallPattern"]) {
		const text = optionalString(record[key], `${field}.${key}`);
		if (text) {
			normalized[key] = text;
		}
	}
	if (Object.keys(normalized).length === 0) {
		throw new Error(`${field} must declare at least one expectation field`);
	}
	return normalized;
}

function normalizeInstructionSurfaceFileEntry(path, record, field) {
	const content = optionalString(record.content, `${field}.content`);
	const sourceFile = optionalString(record.sourceFile, `${field}.sourceFile`);
	if ((content ? 1 : 0) + (sourceFile ? 1 : 0) !== 1) {
		throw new Error(`${field} must set exactly one of content or sourceFile for kind=file`);
	}
	return {
		path,
		kind: "file",
		...(content ? { content } : {}),
		...(sourceFile ? { sourceFile } : {}),
	};
}

function normalizeInstructionSurfaceSymlink(path, record, field) {
	const targetPath = optionalString(record.targetPath, `${field}.targetPath`);
	if (!targetPath) {
		throw new Error(`${field}.targetPath must be set for kind=symlink`);
	}
	if (record.content !== undefined || record.sourceFile !== undefined) {
		throw new Error(`${field} must not set content or sourceFile for kind=symlink`);
	}
	return {
		path,
		kind: "symlink",
		targetPath,
	};
}

function normalizeInstructionSurfaceFile(record, field) {
	const path = assertString(record.path, `${field}.path`);
	const kind = optionalString(record.kind, `${field}.kind`) ?? "file";
	if (!["file", "symlink"].includes(kind)) {
		throw new Error(`${field}.kind must be file or symlink`);
	}
	return kind === "file"
		? normalizeInstructionSurfaceFileEntry(path, record, field)
		: normalizeInstructionSurfaceSymlink(path, record, field);
}

function normalizeInstructionSurface(value, field) {
	if (value === undefined || value === null) {
		return null;
	}
	const record = assertObject(value, field);
	if (!Array.isArray(record.files) || record.files.length === 0) {
		throw new Error(`${field}.files must be a non-empty array`);
	}
	return {
		surfaceLabel: optionalString(record.surfaceLabel, `${field}.surfaceLabel`) ?? "custom_instruction_surface",
		files: record.files.map((entry, index) =>
			normalizeInstructionSurfaceFile(assertObject(entry, `${field}.files[${index}]`), `${field}.files[${index}]`),
		),
	};
}

function normalizeEvaluation(record, index) {
	const taskPath = optionalString(record.taskPath, `evaluations[${index}].taskPath`);
	const instructionSurface = normalizeInstructionSurface(record.instructionSurface, `evaluations[${index}].instructionSurface`);
	const expectedEntryFile = optionalString(record.expectedEntryFile, `evaluations[${index}].expectedEntryFile`);
	const expectedRouting = normalizeExpectedRouting(record.expectedRouting, `evaluations[${index}].expectedRouting`);
	return {
		evaluationId: assertString(record.evaluationId, `evaluations[${index}].evaluationId`),
		displayName:
			optionalString(record.displayName, `evaluations[${index}].displayName`) ??
			assertString(record.evaluationId, `evaluations[${index}].evaluationId`),
		prompt: assertString(record.prompt, `evaluations[${index}].prompt`),
		...(taskPath ? { taskPath } : {}),
		...(instructionSurface ? { instructionSurface } : {}),
		...(expectedEntryFile ? { expectedEntryFile } : {}),
		requiredInstructionFiles: normalizePathList(
			record.requiredInstructionFiles,
			`evaluations[${index}].requiredInstructionFiles`,
		),
		forbiddenInstructionFiles: normalizePathList(
			record.forbiddenInstructionFiles,
			`evaluations[${index}].forbiddenInstructionFiles`,
		),
		requiredSupportingFiles: normalizePathList(
			record.requiredSupportingFiles,
			`evaluations[${index}].requiredSupportingFiles`,
		),
		forbiddenSupportingFiles: normalizePathList(
			record.forbiddenSupportingFiles,
			`evaluations[${index}].forbiddenSupportingFiles`,
		),
		...(expectedRouting ? { expectedRouting } : {}),
	};
}

export function normalizeInstructionSurfaceCaseSuite(input) {
	if (input?.schemaVersion !== INSTRUCTION_SURFACE_CASES_SCHEMA) {
		throw new Error(`schemaVersion must be ${INSTRUCTION_SURFACE_CASES_SCHEMA}`);
	}
	if (!Array.isArray(input.evaluations) || input.evaluations.length === 0) {
		throw new Error("evaluations must be a non-empty array");
	}
	return {
		suiteId: assertString(input.suiteId, "suiteId"),
		suiteDisplayName: optionalString(input.suiteDisplayName, "suiteDisplayName") ?? assertString(input.suiteId, "suiteId"),
		evaluations: input.evaluations.map((entry, index) =>
			normalizeEvaluation(assertObject(entry, `evaluations[${index}]`), index),
		),
	};
}
