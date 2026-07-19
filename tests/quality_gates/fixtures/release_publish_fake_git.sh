#!/usr/bin/env bash
set -u

REAL_GIT=__REAL_GIT__
log_path="${FAKE_GIT_LOG:?FAKE_GIT_LOG is required}"
args=("$@")

json_escape() {
  local LC_ALL=C value="$1" char code escaped='' i
  for ((i = 0; i < ${#value}; i++)); do
    char="${value:i:1}"
    case "$char" in
      '"') escaped+='\"' ;;
      \\) escaped="${escaped}\\\\" ;;
      $'\b') escaped+='\b' ;;
      $'\f') escaped+='\f' ;;
      $'\n') escaped+='\n' ;;
      $'\r') escaped+='\r' ;;
      $'\t') escaped+='\t' ;;
      *)
        printf -v code '%d' "'$char"
        if (( code < 32 )); then
          printf -v char '\\u%04x' "$code"
        fi
        escaped+="$char"
        ;;
    esac
  done
  printf '%s' "$escaped"
}

args_equal() {
  (( $# == ${#args[@]} )) || return 1
  local i expected=("$@")
  for ((i = 0; i < ${#args[@]}; i++)); do
    [[ "${args[i]}" == "${expected[i]}" ]] || return 1
  done
}

json_args='['
separator=''
for arg in "${args[@]}"; do
  json_args+="${separator}\"$(json_escape "$arg")\""
  separator=','
done
json_args+=']'

if [[ -s "$log_path" ]]; then
  existing="$(<"$log_path")"
  printf '%s,%s]\n' "${existing%]}" "$json_args" >"$log_path"
else
  printf '[%s]\n' "$json_args" >"$log_path"
fi

is_branch_push=false
if args_equal push origin main; then
  is_branch_push=true
  branch_push_count=0
  remaining="$(<"$log_path")"
  branch_push_entry='["push","origin","main"]'
  while [[ "$remaining" == *"$branch_push_entry"* ]]; do
    remaining="${remaining#*"$branch_push_entry"}"
    branch_push_count=$((branch_push_count + 1))
  done
fi

branch_push_at="${FAKE_GIT_BRANCH_PUSH_ERROR_AT:-0}"
if [[ "$is_branch_push" == true && "$branch_push_at" != 0 && "$branch_push_count" == "$branch_push_at" ]]; then
  mode="${FAKE_GIT_BRANCH_PUSH_ERROR_MODE:-before}"
  if [[ "$mode" == after ]]; then
    "$REAL_GIT" "${args[@]}" || exit 1
  fi
  printf 'forced branch push error (%s)\n' "$mode" >&2
  exit 49
fi

if [[ "${FAKE_GIT_DIFF_NAME_ONLY_FAIL:-}" == 1 && "${args[0]-}" == diff && "${args[1]-}" == --name-only ]]; then
  printf 'forced diff failure\n' >&2
  exit 42
fi
if [[ "${FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL:-}" == 1 ]] && args_equal ls-remote --tags origin refs/tags/v0.0.0; then
  printf 'forced previous tag lookup failure\n' >&2
  exit 44
fi
if [[ "${FAKE_GIT_TAG_LIST_FAIL:-}" == 1 ]] && args_equal tag --list 'v[0-9]*.[0-9]*.[0-9]*'; then
  printf 'forced local tag list failure\n' >&2
  exit 45
fi
if [[ "${FAKE_GIT_LS_REMOTE_TAG_HISTORY_FAIL:-}" == 1 ]] && args_equal ls-remote --tags origin 'refs/tags/v[0-9]*'; then
  printf 'forced remote tag history failure\n' >&2
  exit 46
fi
if [[ "${FAKE_GIT_TARGET_TAG_EXISTS:-}" == 1 ]] && args_equal ls-remote --tags origin refs/tags/v0.0.0; then
  printf 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\trefs/tags/v0.0.0\n'
  exit 0
fi
if [[ "${FAKE_GIT_FETCH_TAG_FAIL:-}" == 1 ]] && args_equal fetch --quiet origin refs/tags/v0.0.0:refs/tags/v0.0.0; then
  printf 'forced tag fetch failure\n' >&2
  exit 43
fi
if [[ "${FAKE_GIT_ADD_FAIL:-}" == 1 && "${args[0]-}" == add ]]; then
  printf 'forced git add failure\n' >&2
  exit 47
fi
if [[ "${FAKE_GIT_RESTORE_FAIL:-}" == 1 && "${args[0]-}" == restore && "${args[1]-}" == --source ]]; then
  printf 'forced git restore failure\n' >&2
  exit 48
fi

exec "$REAL_GIT" "${args[@]}"
