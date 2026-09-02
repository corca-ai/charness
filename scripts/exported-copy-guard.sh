#!/usr/bin/env bash
# The single home for the package-root != git-root refusal every shell gate needs.
#
# SOURCED, never executed. A caller sets `GATE_NAME` and `GATE_CONSEQUENCE`, sources
# this file, and gets `REPO_ROOT` (already `cd`-ed into) plus `REPO_ROOT_VERIFIED`.
#
# `$(dirname "${BASH_SOURCE[0]}")/..` is a script's PACKAGE root -- the tree it shipped
# in. That is the RIGHT answer for module resolution (scripts/skill_runtime_bootstrap.py
# documents returning `plugins/<pkg>` in an installed tree as correct) and the WRONG
# answer for anything that measures a git population or resolves a config from cwd. The
# generated mirror at `plugins/charness/` is a plain subdirectory of this repo, so a
# mirrored gate used to `cd` there and then measure from there: `git ls-files` is
# cwd-scoped, so `AGENTS.md`, `README.md`, `CLAUDE.md` and `docs/**` dropped out of the
# population (542 eligible files from the root, 240 from the mirror), the `:(exclude)`
# pathspecs became cwd-relative and silently matched nothing, and the repo's only
# `.markdownlint-cli2.jsonc` -- the file that sets `MD013: false` -- was never resolved,
# so the mirror run was RED on a clean tree. Issue #618.
#
# Switching unconditionally to `git rev-parse --show-toplevel` is not the fix. A
# genuinely installed plugin is often not in a git repo at all, or sits INSIDE a
# consumer's repo, where the toplevel is the CONSUMER root and the gate would measure
# the consumer's files. That is a different wrong answer, not a fix.
#
# So the rule is AGREEMENT, not preference: when git can name a toplevel for the
# script's own root and that toplevel is not the script's own root, this is an
# exported/mirrored copy and the gate REFUSES loudly instead of measuring a scope
# narrower than the one its own comments claim. When git cannot name a toplevel (no
# repo, no git binary) nothing is claimed and the package root stands; the downstream
# `git ls-files` failure is already loud, and `REPO_ROOT_VERIFIED` lets a caller tell
# "we know this root and discovery came back empty" from "we could not confirm the root".
#
# `CHARNESS_REPO_ROOT` is the escape hatch scripts/runtime_bootstrap.py already defines
# for the Python side; the shell gates reuse that name rather than inventing a second one.
#
# WHY ONE FILE. This guard shipped as six hand-copied blocks, and three gates that
# needed it never got one -- `check-python-lint.sh`, `run-quality.sh` and
# `self-validate-install-update.sh` each carried a comment SAYING they cannot run from
# the export and no code that said so to the operator. A rule that has to be retyped per
# gate is a rule whose coverage is whatever the last author remembered. With one home,
# `tests/quality_gates/test_shell_gate_root_resolution.py` asks a single membership
# question of every gate instead of grepping each one for a shape.

if [[ -z "${GATE_NAME:-}" ]]; then
  echo "exported-copy-guard.sh: sourced without GATE_NAME; this is a caller bug." >&2
  exit 2
fi

# `CHARNESS_GATE_DIR` is the sourcing gate's own directory, set by the builtin-only
# prelude every caller carries. It has to come from the CALLER: a sourced file's
# `BASH_SOURCE[0]` is itself, which would be the same answer only while the two sit in
# one directory. The prelude also proves the file is there before sourcing it, so a
# relocated, symlinked or PATH-resolved gate refuses BY NAME instead of dying on a bash
# `No such file or directory` -- replacing a gate-named refusal with a bash-level one
# was a real regression of the diagnostic quality this consolidation exists to raise.
# shellcheck disable=SC2034
REPO_ROOT="$(cd "${CHARNESS_GATE_DIR:-.}/.." && pwd)"
# shellcheck disable=SC2034
REPO_ROOT_VERIFIED=0

# The rule is AGREEMENT between a root and git's opinion of it, and that rule applies to
# an ASSERTED root too. `CHARNESS_REPO_ROOT` used to skip the comparison outright and
# still set `REPO_ROOT_VERIFIED=1` -- so `CHARNESS_REPO_ROOT=$PWD/plugins/charness`
# reproduced the original narrowed-population defect silently, with the verified flag
# asserting the opposite. Every legitimate use survives this check: a consumer's own repo
# root IS its own toplevel, and a non-git directory names no toplevel at all.
_charness_asserted=0
if [[ -n "${CHARNESS_REPO_ROOT:-}" ]]; then
  if [[ ! -d "$CHARNESS_REPO_ROOT" ]]; then
    # By name, with a caller-misuse status. Letting the `cd` below fail under `set -e`
    # printed a bare `cd: ...: No such file or directory` with no gate name -- the one
    # input path the operator typed by hand, missing the property the prelude exists
    # to protect.
    {
      echo "${GATE_NAME}: CHARNESS_REPO_ROOT does not name a directory."
      echo "  CHARNESS_REPO_ROOT: $CHARNESS_REPO_ROOT"
    } >&2
    exit 2
  fi
  _charness_asserted_root="$(cd "$CHARNESS_REPO_ROOT" && pwd)"
  # PRESENCE is not misuse; DISAGREEMENT is. Refusing on presence alone reds a run
  # whose asserted root, derived root and git toplevel all agree -- and an operator
  # who exports this variable in a shell profile or a CI job then gets a red on
  # `--help`, indistinguishable from a gate failure. Status 2, not 1, because this is
  # caller misuse and a receipt must be able to tell it from a verdict.
  if [[ "${GATE_ACCEPTS_REPO_ROOT_HATCH:-0}" != "1" ]]; then
    if [[ "$_charness_asserted_root" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
      {
        echo "${GATE_NAME}: CHARNESS_REPO_ROOT names a different tree, and this gate does not accept one."
        echo "  asserted: $_charness_asserted_root"
        echo "  own root: $REPO_ROOT"
        echo "This gate runs a fixed path list belonging to the charness source checkout, so"
        echo "retargeting its root does not make it runnable elsewhere -- it only moves where"
        echo "it fails. Run it from a charness source checkout."
      } >&2
      exit 2
    fi
  fi
  REPO_ROOT="$_charness_asserted_root"
  _charness_asserted=1
fi

git_toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -n "$git_toplevel" ]]; then
  if [[ "$(cd "$git_toplevel" && pwd -P)" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
    {
      echo "${GATE_NAME}: refusing to run from an exported copy."
      if [[ "$_charness_asserted" == "1" ]]; then
        echo "  asserted root: $REPO_ROOT (CHARNESS_REPO_ROOT)"
      else
        echo "  script root:  $REPO_ROOT"
      fi
      echo "  git toplevel: $git_toplevel"
      if [[ -n "${GATE_CONSEQUENCE:-}" ]]; then
        echo "$GATE_CONSEQUENCE"
      fi
      echo "Run this gate from the checkout you want measured, or set CHARNESS_REPO_ROOT to"
      echo "that checkout's own root -- a subdirectory of a repository is the very shape"
      echo "this refusal exists to catch, whether the script found it or you named it."
    } >&2
    exit 1
  fi
fi
if [[ -z "$git_toplevel" && ! -f "$REPO_ROOT/packaging/charness.json" ]]; then
  {
    echo "${GATE_NAME}: refusing to run from an installed/exported copy without a source checkout."
    echo "  package root: $REPO_ROOT"
    echo "  no git toplevel was found and packaging/charness.json is absent."
    if [[ -n "${GATE_CONSEQUENCE:-}" ]]; then
      echo "$GATE_CONSEQUENCE"
    fi
    echo "Run this gate from a charness source checkout."
  } >&2
  exit 1
fi
# Verified means COMPARED and agreed, not merely supplied. When git names no toplevel
# nothing was established, so the flag stays 0.
# shellcheck disable=SC2034
if [[ -n "$git_toplevel" ]]; then REPO_ROOT_VERIFIED=1; fi
# ASSERTED is a separate fact from VERIFIED, and callers need both. `check-shell.sh`
# hard-fails an empty discovery only over a root it KNOWS, and an operator naming the
# root explicitly is such a root -- an unpacked non-git export at a named root would
# otherwise fall back to the tolerant empty-population exit 0, which is the green over
# a population that could not even see the gate itself.
# shellcheck disable=SC2034
REPO_ROOT_ASSERTED="$_charness_asserted"
# `|| exit 1` rather than shellcheck's suggested bare `|| exit`: a sourced file's bare
# `exit` inherits the previous command's status, and `cd` failing here must never be
# reported as the gate's own verdict.
cd "$REPO_ROOT" || exit 1
