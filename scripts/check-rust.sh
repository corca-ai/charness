#!/usr/bin/env bash
set -euo pipefail

# Rust was production code with no lint gate at all. `check_python_lengths.py` globs
# `*.py` only, `check-shell.sh` walks `*.sh`, and the ratio gate counts `native/*/src/**.rs`
# in its PRODUCTION denominator -- so 11,891 lines of Rust were accounted as production
# while no gate read them. Files reached 1,399 lines against a 480-line Python cap.
#
# BLIND CLASS, stated before the first acceptance test: this gate runs `cargo fmt --check`
# and `cargo clippy -- -D warnings`. It therefore sees formatting and the lints clippy
# ships. It does NOT see file length, function length, or cyclomatic complexity -- clippy
# has no stable equivalent of the per-file caps the Python gate enforces. A 1,399-line
# Rust file passes this gate. Naming that here so the next reader does not mistake a
# green `check-rust` for the length discipline `check_python_lengths.py` provides.
GATE_NAME="check-rust"
GATE_CONSEQUENCE="This gate resolves crates by walking its own root, so a package root that is not the
git root would lint a narrower tree -- or no crate at all -- and still exit 0."
# Builtin-only, no `dirname`: see check-shell.sh for why the guard is located this way.
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-rust: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

manifests=()
while IFS= read -r manifest; do
  [[ -n "$manifest" ]] && manifests+=("$manifest")
done < <(find native -maxdepth 2 -type f -name Cargo.toml 2>/dev/null | sort)

# A DISCOVERED empty set is a real answer and stays a cheap no-op: a consuming repo with
# no Rust has nothing for this gate to say. That is distinct from the case below, where a
# crate exists and the toolchain does not -- there the gate establishes nothing and must
# say so rather than report the same silent green.
if [[ ${#manifests[@]} -eq 0 ]]; then
  echo "check-rust: no Cargo.toml under native/; nothing to lint (discovered empty scope)."
  exit 0
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "check-rust: ${#manifests[@]} crate(s) present but cargo is unavailable;" >&2
  echo "  this run established NOTHING about them. Install the Rust toolchain," >&2
  echo "  or run this gate on a host that has it." >&2
  exit 2
fi

status=0
for manifest in "${manifests[@]}"; do
  crate_dir="${manifest%/Cargo.toml}"
  echo "check-rust: $crate_dir"
  # Run from INSIDE the crate, not with --manifest-path from the repo root. rustup
  # resolves `rust-toolchain.toml` from the working directory, so the root form silently
  # picks the ambient toolchain: measured here as rustc 1.93 against a crate pinned to
  # 1.96, which fails as "not supported by the following packages" and reads exactly like
  # a lint finding. A gate whose failure mode impersonates its own verdict is worse than
  # no gate.
  if ! (cd "$crate_dir" && cargo fmt --check); then
    echo "check-rust: $crate_dir is not rustfmt-clean; run: (cd $crate_dir && cargo fmt)" >&2
    status=1
  fi
  if ! (cd "$crate_dir" && cargo clippy --release --all-targets --quiet -- -D warnings); then
    echo "check-rust: $crate_dir has clippy findings; run: (cd $crate_dir && cargo clippy --release --all-targets)" >&2
    status=1
  fi
done

if [[ $status -ne 0 ]]; then
  exit 1
fi
echo "check-rust: ${#manifests[@]} crate(s) are rustfmt-clean and clippy-clean."
