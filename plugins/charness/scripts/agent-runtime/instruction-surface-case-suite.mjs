import {
	EVALUATION_CASES_SCHEMA,
	EVALUATION_INPUT_SCHEMA,
	INSTRUCTION_SURFACE_CASES_SCHEMA,
} from "./contract-versions.mjs";

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
	for (const key of ["selectedSkill", "bootstrapHelper", "workSkill", "selectedSupport", "firstToolCallPattern"]) {
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

function normalizeRequiredConcept(value, field) {
	const record = assertObject(value, field);
	const conceptId = assertString(record.id, `${field}.id`);
	const terms = normalizePathList(record.terms, `${field}.terms`);
	if (terms.length === 0) {
		throw new Error(`${field}.terms must be a non-empty array`);
	}
	const sourceFields = normalizePathList(record.sourceFields, `${field}.sourceFields`);
	for (const sourceField of sourceFields) {
		if (!["summary", "routingDecision.reasonSummary"].includes(sourceField)) {
			throw new Error(`${field}.sourceFields must contain only summary or routingDecision.reasonSummary`);
		}
	}
	return {
		id: conceptId,
		terms,
		sourceFields: sourceFields.length > 0 ? sourceFields : ["summary", "routingDecision.reasonSummary"],
	};
}

function normalizeRequiredConcepts(value, field) {
	if (value === undefined || value === null) {
		return [];
	}
	if (!Array.isArray(value)) {
		throw new Error(`${field} must be an array`);
	}
	return value.map((entry, index) => normalizeRequiredConcept(entry, `${field}[${index}]`));
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
	const requiredConcepts = normalizeRequiredConcepts(record.requiredConcepts, `evaluations[${index}].requiredConcepts`);
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
		requiredConcepts,
		forbiddenSupportingFiles: normalizePathList(
			record.forbiddenSupportingFiles,
			`evaluations[${index}].forbiddenSupportingFiles`,
		),
		...(expectedRouting ? { expectedRouting } : {}),
	};
}

function translateEvaluationInput(input) {
	if (input?.schemaVersion !== EVALUATION_INPUT_SCHEMA) {
		return input;
	}
	if (input.surface !== "dev" || input.preset !== "repo") {
		throw new Error("evaluation_input fixture must use surface=dev and preset=repo");
	}
	if (!Array.isArray(input.cases) || input.cases.length === 0) {
		throw new Error("cases must be a non-empty array");
	}
	return {
		schemaVersion: EVALUATION_CASES_SCHEMA,
		suiteId: input.suiteId,
		suiteDisplayName: input.suiteDisplayName,
		evaluations: input.cases.map((entry, index) => {
			const record = assertObject(entry, `cases[${index}]`);
			return {
				...record,
				evaluationId: assertString(record.caseId, `cases[${index}].caseId`),
			};
		}),
	};
}

export function normalizeInstructionSurfaceCaseSuite(rawInput) {
	const input = translateEvaluationInput(rawInput);
	if (![EVALUATION_CASES_SCHEMA, INSTRUCTION_SURFACE_CASES_SCHEMA].includes(input?.schemaVersion)) {
		throw new Error(`schemaVersion must be ${EVALUATION_CASES_SCHEMA}`);
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
