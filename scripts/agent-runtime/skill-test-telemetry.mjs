function normalizeNonNegativeInteger(value) {
	return Number.isInteger(value) && value >= 0 ? value : null;
}

function normalizeNonNegativeNumber(value) {
	return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

function isObjectRecord(value) {
	return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function claudePromptTokens(usage) {
	return [
		normalizeNonNegativeInteger(usage.input_tokens),
		normalizeNonNegativeInteger(usage.cache_creation_input_tokens),
		normalizeNonNegativeInteger(usage.cache_read_input_tokens),
	]
		.filter((value) => value !== null)
		.reduce((sum, value) => sum + value, 0);
}

function parseClaudeEnvelope(raw) {
	try {
		const parsed = JSON.parse(raw);
		return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
	} catch {
		return null;
	}
}

function compactTelemetry(telemetry) {
	const compact = {};
	for (const [key, value] of Object.entries(telemetry)) {
		if (value !== null) {
			compact[key] = value;
		}
	}
	return Object.keys(compact).length > 0 ? compact : null;
}

export function extractClaudeTelemetry(raw, options = {}) {
	const envelope = typeof raw === "string" ? parseClaudeEnvelope(raw) : raw;
	if (!envelope) {
		return null;
	}
	const usage = isObjectRecord(envelope.usage) ? envelope.usage : {};
	const promptTokens = claudePromptTokens(usage);
	const completionTokens = normalizeNonNegativeInteger(usage.output_tokens);
	return compactTelemetry({
		provider: "anthropic",
		model: options.claudeModel ?? options.model ?? null,
		prompt_tokens: promptTokens > 0 ? promptTokens : null,
		completion_tokens: completionTokens,
		total_tokens: completionTokens === null && promptTokens === 0 ? null : promptTokens + (completionTokens ?? 0),
		cost_usd: normalizeNonNegativeNumber(envelope.total_cost_usd),
	});
}
