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
Usage: capture-skill-run.sh --ref <git-ref> --invocation "/charness:quality" --out-dir <dir> [--repo-root <dir>] [--timeout-sec N]

Writes under <out-dir>:
  worktree/            the throwaway checkout at <git-ref>
  config/              the isolated CLAUDE_CONFIG_DIR
  config/projects/.../ the session-log tree (parent + subagents/*.jsonl)
  stream.jsonl         the --output-format stream-json stdout
  stderr.log
Prints SESSION_TREE=<dir> (the projects/<proj> dir) on success.
Default timeout: 1200s. The caller owns cleanup of <out-dir> and the worktree.
EOF
}

ref=""; invocation=""; out_dir=""; repo_root=""; timeout_sec=1200
while [[ $# -gt 0 ]]; do
	case "$1" in
		--ref) ref="${2:-}"; shift 2 ;;
		--invocation) invocation="${2:-}"; shift 2 ;;
		--out-dir) out_dir="${2:-}"; shift 2 ;;
		--repo-root) repo_root="${2:-}"; shift 2 ;;
		--timeout-sec) timeout_sec="${2:-}"; shift 2 ;;
		-h|--help) usage; exit 0 ;;
		*) echo "Unknown argument: $1" >&2; usage >&2; exit 1 ;;
	esac
done
[[ -z "$ref" || -z "$invocation" || -z "$out_dir" ]] && { echo "Missing required arguments." >&2; usage >&2; exit 1; }
repo_root="${repo_root:-$(git rev-parse --show-toplevel)}"

wt="$out_dir/worktree"
cfg="$out_dir/config"
mkdir -p "$out_dir"
rm -rf "$wt" "$cfg" 2>/dev/null || true
git -C "$repo_root" worktree remove --force "$wt" 2>/dev/null || true

git -C "$repo_root" worktree add --detach "$wt" "$ref" >/dev/null
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
empty_hooks="$out_dir/empty-hooks"
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

echo "capture: ref=$ref invocation=$invocation timeout=${timeout_sec}s" >&2
set +e
( cd "$wt" && env "${hooks_env[@]}" CLAUDE_CONFIG_DIR="$cfg" \
	CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 DISABLE_TELEMETRY=1 DISABLE_AUTOUPDATER=1 DISABLE_ERROR_REPORTING=1 \
	timeout "${timeout_sec}" claude -p "$invocation" \
		--output-format stream-json --verbose --dangerously-skip-permissions \
	> "$out_dir/stream.jsonl" 2> "$out_dir/stderr.log" )
rc=$?
set -e
echo "capture exit: $rc (124 = hit timeout cap; the partial tree is still usable)" >&2

tree_dir="$(find "$cfg/projects" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -1)"
[[ -z "$tree_dir" ]] && { echo "No session tree produced under $cfg/projects" >&2; exit 1; }
echo "SESSION_TREE=$tree_dir"
