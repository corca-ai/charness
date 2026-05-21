const defaultMutate = ["scripts/agent-runtime/*.mjs"];
const mutate = process.env.MUTATION_JS_TARGETS
	? process.env.MUTATION_JS_TARGETS.split(/\s+/).filter(Boolean)
	: defaultMutate;

/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
	mutate,
	testRunner: "command",
	commandRunner: {
		command: "python3 -m pytest -q tests/test_cautilus_scenarios.py",
	},
	reporters: ["clear-text", "progress", "json"],
	jsonReporter: {
		fileName: "reports/mutation/stryker-js.json",
	},
	htmlReporter: {
		fileName: "reports/mutation/stryker-js.html",
	},
	thresholds: {
		high: 80,
		low: 60,
		break: 80,
	},
	concurrency: 2,
	timeoutMS: 60000,
	tempDirName: ".stryker-tmp",
	cleanTempDir: true,
	ignorePatterns: [
		".charness/**",
		".git/**",
		".venv/**",
		"charness-artifacts/**",
		"node_modules/**",
		"plugins/**",
		"reports/**",
	],
};
