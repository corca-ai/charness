#!/usr/bin/env bash
set -euo pipefail

# Capture ONE real, isolated headless run of an installed charness plugin skill
# and leave its full session-log tree (parent + subagents/*.jsonl) on disk for
# build-skill-execution-observation.mjs to score.
#
# Why isolated: `/charness:quality` resolves from the INSTALLED plugin, which is a
# directory-source marketplace pointing at the shared clone. Editing that clone
# is the #258 hazard. This builds a throwaway worktree at the requested ref + a
# per-run CLAUDE_CONFIG_DIR whose marketplace points at that worktree, so the
# slash command resolves to exactly the ref under test without touching the shared
# install. It also neutralizes core.hooksPath to an empty dir for the captured
# subprocess (a worktree otherwise inherits the main clone's absolute hooksPath and
# the maintainer-setup gate derails the run; an empty dir also keeps charness's dev
# hooks from firing on the skill's own internal git ops). See the inline note below.
#
# This is an on-demand maintainer tool; it runs a real `claude -p` with full tools
# (a real user's permissive setup), so run it only against a trusted checkout.

usage() {
	cat <<'EOF'
Usage: capture-skill-run.sh --ref <git-ref> --invocation "/charness:quality" --out-dir <dir> [--repo-root <dir>] [--timeout-sec N] [--run-cwd <dir>]

--run-cwd runs the captured `claude -p` in <dir> instead of the worktree (the
plugin still resolves from the worktree ref). Use for scenarios whose target
repo must NOT be charness — e.g. setup's greenfield arm on a fresh sandbox
repo. The caller owns creating <dir> (git init etc.) and its cleanup; the
caller also owns cleanup of the run base recorded in run-base.txt.
--run-cwd must not live under --out-dir (refused) and should avoid descriptive
eval names in its path (warned): #423.

Writes under <out-dir> (grader-side artifacts only; run-visible state lives
under the neutral run base recorded in run-base.txt, #423):
  run-base.txt         the neutral mktemp dir holding all run-visible state for
                       this run: the checkout, config, hooks
  worktree -> <run-base>/<repo>   post-run symlink to the throwaway checkout at <git-ref>
  base-commit.txt      the commit the worktree was checked out at (the diff base a
                       committing run's produced-output extractor must use, #409)
  config -> <run-base>/config     post-run symlink to the isolated CLAUDE_CONFIG_DIR
  config/projects/.../ the session-log tree (parent + subagents/*.jsonl)
  stream.jsonl         the --output-format stream-json stdout (the authoritative
                       transcript source; the tree can drop the final block, #409);
                       written under the run base during the run, moved here after
  stderr.log
Prints SESSION_TREE=<dir> (the projects/<proj> dir) and RUN_BASE=<dir> on success.
Default timeout: 1200s. The caller owns cleanup of <out-dir> AND the run base
(run-base.txt): `git -C <repo-root> worktree remove --force <run-base>/<repo>`
then `rm -rf <run-base>`. Re-running with the same --out-dir also self-heals both.
EOF
}

ref=""; invocation=""; out_dir=""; repo_root=""; timeout_sec=1200; run_cwd=""
while [[ $# -gt 0 ]]; do
	case "$1" in
		--ref) ref="${2:-}"; shift 2 ;;
		--invocation) invocation="${2:-}"; shift 2 ;;
		--out-dir) out_dir="${2:-}"; shift 2 ;;
		--repo-root) repo_root="${2:-}"; shift 2 ;;
		--timeout-sec) timeout_sec="${2:-}"; shift 2 ;;
		--run-cwd) run_cwd="${2:-}"; shift 2 ;;
		-h|--help) usage; exit 0 ;;
		*) echo "Unknown argument: $1" >&2; usage >&2; exit 1 ;;
	esac
done
[[ -z "$ref" || -z "$invocation" || -z "$out_dir" ]] && { echo "Missing required arguments." >&2; usage >&2; exit 1; }
repo_root="${repo_root:-$(git rev-parse --show-toplevel)}"

mkdir -p "$out_dir"
# #423: all run-visible state lives under a NEUTRAL mktemp base, never under the
# descriptive --out-dir. The captured agent sees its own cwd and env paths; a
# descriptive out-dir name ("handoff-pickup-slice9-...") tells the run it is being
# evaluated and which floor it is graded against, and grader siblings
# (justification.md) become readable via `..`. Grader-side artifacts stay in
# --out-dir; worktree/ and config/ are exposed there as post-run symlinks.
# TMPDIR relocates the run base when /tmp is too small for a checkout.
if [[ -f "$out_dir/run-base.txt" ]]; then
	old_base="$(cat "$out_dir/run-base.txt")"
	git -C "$repo_root" worktree remove --force "$old_base/$(basename "$repo_root")" 2>/dev/null || true
	rm -rf "$old_base" 2>/dev/null || true
fi
# legacy layout (pre-#423) left a real worktree/ and config/ under out_dir
git -C "$repo_root" worktree remove --force "$out_dir/worktree" 2>/dev/null || true
rm -rf "$out_dir/worktree" "$out_dir/config" "$out_dir/empty-hooks" 2>/dev/null || true

run_base="$(mktemp -d)"
real_out="$(realpath "$out_dir")"; real_base="$(realpath "$run_base")"
if [[ "$real_base" == "$real_out" || "$real_base" == "$real_out"/* ]]; then
	echo "run base resolved under --out-dir (TMPDIR misconfiguration?): the captured run would see its eval identity (#423). Point TMPDIR elsewhere." >&2
	rm -rf "$run_base"
	exit 1
fi
[[ "$real_base" == *"$(basename "$real_out")"* ]] && \
	echo "warning: run base path contains the out-dir name '$(basename "$real_out")'; TMPDIR re-encodes the eval identity (#423)" >&2
wt="$run_base/$(basename "$repo_root")"
cfg="$run_base/config"
echo "$run_base" > "$out_dir/run-base.txt"

git -C "$repo_root" worktree add --detach "$wt" "$ref" >/dev/null
# Record the commit the worktree is checked out at, NOW, before the captured run can
# commit its slice and advance HEAD. A faithful skill run (impl, and any commit-discipline
# skill) commits inside the worktree, so the produced-output extractor must diff the
# changed set against THIS base, not the moved HEAD, or it reads an EMPTY set and the
# substance judge grades blind (#409 Gap 1). This is the detached base ref by definition of
# `git worktree add --detach <ref>`.
git -C "$wt" rev-parse HEAD > "$out_dir/base-commit.txt"
# Neutralize git hooks for the captured subprocess: point core.hooksPath at an
# EMPTY dir. A worktree otherwise inherits the main clone's absolute hooksPath and
# the maintainer-setup gate derails the run; pinning the worktree's own .githooks
# avoids that, but then every internal git op the skill runs (a quality_gates test
# that commits, an enforcement probe) fires charness's full dev hook suite, which
# the captured skill burns turns investigating and working around — the 2026-06-29
# quality capture spent ~9 Bash calls probing core.hooksPath and re-running pytest
# under empty hooks. A real installed-plugin user does not run charness's maintainer
# hooks at all, so an empty hooks dir is both quieter AND more faithful; the worktree's
# .githooks files stay on disk and readable for any operability-lens inspection.
# Do NOT `git config` it: a worktree shares .git/config, so that would pollute the
# main repo's core.hooksPath (and silently disable its hooks). GIT_CONFIG_* env is
# process-scoped and writes no file.
empty_hooks="$run_base/empty-hooks"
mkdir -p "$empty_hooks"
hooks_env=("GIT_CONFIG_COUNT=1" "GIT_CONFIG_KEY_0=core.hooksPath" "GIT_CONFIG_VALUE_0=$empty_hooks")

mkdir -p "$cfg/plugins"
cp "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.credentials.json" "$cfg/"
cp "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json" "$cfg/" 2>/dev/null || true
python3 - "$wt" "$cfg" <<'PY'
import json, os, sys
wt, cfg = sys.argv[1], sys.argv[2]
ts = "2026-01-01T00:00:00.000Z"
json.dump(
    {"corca-charness": {"source": {"source": "directory", "path": wt}, "installLocation": wt, "lastUpdated": ts}},
    open(os.path.join(cfg, "plugins", "known_marketplaces.json"), "w"), indent=2,
)
json.dump(
    {"version": 2, "plugins": {"charness@corca-charness": [
        {"scope": "user", "installPath": os.path.join(wt, "plugins", "charness"),
         "version": "0.0.0", "installedAt": ts, "lastUpdated": ts, "gitCommitSha": "0" * 40}]}},
    open(os.path.join(cfg, "plugins", "installed_plugins.json"), "w"), indent=2,
)
PY

run_dir="${run_cwd:-$wt}"
[[ -d "$run_dir" ]] || { echo "--run-cwd dir does not exist: $run_dir" >&2; exit 1; }
if [[ -n "$run_cwd" ]]; then
	real_out="$(realpath "$out_dir")"; real_cwd="$(realpath "$run_dir")"
	if [[ "$real_cwd" == "$real_out" || "$real_cwd" == "$real_out"/* ]]; then
		echo "--run-cwd must not live under --out-dir: the captured run could read grader files (justification.md) and its own eval identity (#423). Use a neutral mktemp dir." >&2
		# The worktree at $wt is already registered under $repo_root/.git by this
		# point (worktree add happens before run_dir is resolved) — refusing here
		# must not leak it or the run base.
		git -C "$repo_root" worktree remove --force "$wt" 2>/dev/null || true
		rm -rf "$run_base"
		exit 1
	fi
	[[ "$real_cwd" == *"$(basename "$real_out")"* ]] && \
		echo "warning: --run-cwd path contains the out-dir name '$(basename "$real_out")'; the captured run can see its eval identity in its own cwd (#423)" >&2
fi
echo "capture: ref=$ref invocation=$invocation timeout=${timeout_sec}s cwd=$run_dir" >&2
set +e
( cd "$run_dir" && env "${hooks_env[@]}" CLAUDE_CONFIG_DIR="$cfg" \
	CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 DISABLE_TELEMETRY=1 DISABLE_AUTOUPDATER=1 DISABLE_ERROR_REPORTING=1 \
	timeout "${timeout_sec}" claude -p "$invocation" \
		--output-format stream-json --verbose --dangerously-skip-permissions \
	> "$run_base/stream.jsonl" 2> "$run_base/stderr.log" )
rc=$?
set -e
echo "capture exit: $rc (124 = hit timeout cap; the partial tree is still usable)" >&2

mv "$run_base/stream.jsonl" "$out_dir/stream.jsonl"
mv "$run_base/stderr.log" "$out_dir/stderr.log"
# Post-run symlink (leak-free: the captured run has exited) so the observation
# builder's sibling-stream auto-resolve (three-up from the session tree = the run
# base) still finds the authoritative stream; the durable copy lives in out-dir.
ln -sfn "$out_dir/stream.jsonl" "$run_base/stream.jsonl"
ln -sfn "$wt" "$out_dir/worktree"
ln -sfn "$cfg" "$out_dir/config"
# Non-blocking canary (#423): a leak regression shows up as the out-dir basename
# inside the captured transcript. floor-addition-restraint: advisory.
leak_hits="$(grep -cF -- "$(basename "$out_dir")" "$out_dir/stream.jsonl" 2>/dev/null || true)"
[[ "${leak_hits:-0}" -gt 0 ]] && echo "identity-leak canary: out-dir basename appears ${leak_hits}x in stream.jsonl (#423)" >&2

tree_dir="$(find "$cfg/projects" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -1)"
[[ -z "$tree_dir" ]] && { echo "No session tree produced under $cfg/projects" >&2; exit 1; }
echo "SESSION_TREE=$tree_dir"
echo "RUN_BASE=$run_base"
