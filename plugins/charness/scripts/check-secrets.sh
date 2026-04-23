#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if command -v gitleaks >/dev/null 2>&1; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    scan_dir="$(mktemp -d)"
    cleanup() {
      rm -rf "$scan_dir"
    }
    trap cleanup EXIT
    if git ls-files -z --cached --others --exclude-standard | tar --null --ignore-failed-read -T - -cf - | tar -xf - -C "$scan_dir"; then
      exec gitleaks dir \
        --config "$REPO_ROOT/.gitleaks.toml" \
        --no-banner \
        --redact \
        "$scan_dir"
    fi
  fi

  exec gitleaks dir \
    --config "$REPO_ROOT/.gitleaks.toml" \
    --no-banner \
    --redact \
    "$REPO_ROOT"
fi

echo "check-secrets: gitleaks not found, falling back to secretlint via npm (~5s vs sub-1s). Install gitleaks for the fast path from https://github.com/gitleaks/gitleaks#installing" >&2

if command -v npm >/dev/null 2>&1; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    mapfile -d '' secretlint_files < <(git ls-files -z --cached --others --exclude-standard)
    if ((${#secretlint_files[@]} == 0)); then
      echo "No tracked or unignored files to scan."
      exit 0
    fi
    exec npm exec --no-install -- secretlint --secretlintignore .secretlintignore "${secretlint_files[@]}"
  fi

  exec npm exec --no-install -- secretlint --secretlintignore .secretlintignore "**/*"
fi

echo "secret scanning requires either gitleaks or repo-local secretlint via npm." >&2
exit 1
