import { copyFileSync, existsSync, mkdirSync, mkdtempSync, rmSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve } from "node:path";
import process from "node:process";

export const CODEX_HOME_MODES = ["isolated", "inherit"];
export const CODEX_AUTH_MODES = ["inherit", "env", "none"];

function pushOptionalPair(args, flag, value) {
	if (value) {
		args.push(flag, value);
	}
}

export function codexArgs(options, schemaFile, outputFile) {
	const sessionMode = options.codexSessionMode ?? "ephemeral";
	const args = [
		"exec",
		"-C",
		options.workspace,
		"--sandbox",
		options.sandbox,
	];
	if ((options.codexHomeMode ?? "inherit") === "isolated") {
		args.push("--ignore-user-config");
	}
	if (sessionMode === "ephemeral") {
		args.push("--ephemeral");
	}
	args.push("--output-schema", schemaFile, "-o", outputFile);
	pushOptionalPair(args, "--model", options.codexModel ?? options.model);
	const effort = options.codexReasoningEffort ?? options.reasoningEffort;
	if (effort) {
		args.push("-c", `model_reasoning_effort="${effort}"`);
	}
	for (const override of options.codexConfigOverrides ?? []) {
		args.push("-c", override);
	}
	args.push("-");
	return args;
}

function codexSourceHome(env = process.env) {
	return env.CODEX_HOME ? resolve(env.CODEX_HOME) : join(homedir(), ".codex");
}

function hasEnvCodexAuth(env = process.env) {
	return Boolean(env.OPENAI_API_KEY);
}

function authMissingMessage(authMode, sourceHome) {
	if (authMode === "env") {
		return "The codex_exec runner cannot authenticate: --codex-auth-mode env was selected but OPENAI_API_KEY is not set.";
	}
	return `The codex_exec runner cannot authenticate: isolated CODEX_HOME could not inherit ${sourceHome}/auth.json and OPENAI_API_KEY is not set.`;
}

function temporaryCodexHome() {
	const path = mkdtempSync(join(tmpdir(), "charness-codex-home-"));
	mkdirSync(path, { recursive: true });
	return path;
}

function withPreflightBlocker(runtime, summary) {
	return {
		...runtime,
		preflightBlocker: {
			blockerKind: "runner_auth_missing",
			summary,
		},
	};
}

export function prepareCodexRuntimeEnv(options, baseEnv = process.env) {
	const authMode = options.codexAuthMode ?? "inherit";
	const homeMode = options.codexHomeMode ?? "inherit";
	if (homeMode === "inherit") {
		const runtime = {
			env: baseEnv,
			cleanup: null,
			preflightBlocker: null,
			telemetry: {
				codex_home_mode: "inherit",
				codex_home_isolated: false,
				...(baseEnv.CODEX_HOME ? { codex_home_path: baseEnv.CODEX_HOME } : {}),
			},
		};
		if (authMode === "env" && !hasEnvCodexAuth(baseEnv)) {
			return withPreflightBlocker(runtime, authMissingMessage(authMode, codexSourceHome(baseEnv)));
		}
		return runtime;
	}

	const configuredHome = options.codexHome ? resolve(options.codexHome) : null;
	const codexHome = configuredHome ?? temporaryCodexHome();
	mkdirSync(codexHome, { recursive: true });
	const cleanup = configuredHome ? null : () => rmSync(codexHome, { recursive: true, force: true });
	const env = { ...baseEnv, CODEX_HOME: codexHome };
	const runtime = {
		env,
		cleanup,
		preflightBlocker: null,
		telemetry: {
			codex_home_mode: configuredHome ? "custom" : "isolated",
			codex_home_isolated: true,
			codex_home_path: codexHome,
		},
	};

	if (authMode === "inherit") {
		const sourceHome = codexSourceHome(baseEnv);
		const sourceAuthFile = join(sourceHome, "auth.json");
		const destinationAuthFile = join(codexHome, "auth.json");
		if (existsSync(sourceAuthFile) && resolve(sourceAuthFile) !== resolve(destinationAuthFile)) {
			copyFileSync(sourceAuthFile, destinationAuthFile);
		} else if (!existsSync(destinationAuthFile) && !hasEnvCodexAuth(baseEnv)) {
			return withPreflightBlocker(runtime, authMissingMessage(authMode, sourceHome));
		}
	}
	if (authMode === "env" && !hasEnvCodexAuth(baseEnv)) {
		return withPreflightBlocker(runtime, authMissingMessage(authMode, codexSourceHome(baseEnv)));
	}
	return runtime;
}

export function codexFailureBlockerKind(stderr = "") {
	const text = String(stderr).toLowerCase();
	const authFailure = [
		"401 unauthorized",
		"missing bearer or basic authentication",
		"not authenticated",
		"authentication error",
		"login required",
	].some((pattern) => text.includes(pattern));
	return authFailure ? "runner_auth_missing" : "runner_execution_failed";
}
