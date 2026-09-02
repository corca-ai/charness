#!/usr/bin/env bash
# Reword the three #768 WIP lane subjects (run from a clean main after all lanes are integrated).
set -euo pipefail
cd /home/hwidong/codes/charness
declare -A MSG
MSG[b646c21f6]="subprocess: route production skill and worktree spawns through subprocess_guard (#768 P2 lane candidate)"
MSG[697975921]="tests: migrate quality-gate tests in-process and mark real boundaries (#768 T2 lane candidate)"
MSG[f72baa7b6]="tests: migrate CLI and coverage-debt tests in-process and mark real boundaries (#768 T3 lane candidate)"
BASE=a5002ffc9
todo() {
  git log --reverse --format='%H %h' "$BASE"..HEAD | while read -r full short; do
    echo "pick $full"
    for k in "${!MSG[@]}"; do
      if [[ "$short" == "$k" ]]; then
        printf 'exec git commit --amend --no-verify -q -m %q\n' "${MSG[$k]}"
      fi
    done
  done
}
export TODO_FILE=/tmp/reword-768.todo; todo > "$TODO_FILE"
GIT_SEQUENCE_EDITOR="cp $TODO_FILE" git rebase -i "$BASE"
