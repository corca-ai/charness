#!/usr/bin/env bash
queue_selected "fixture-label" python3 scripts/quality_validator.py --repo-root .
queue_selected "variable-target" python3 "$VAR" --repo-root .
queue_timed "fixture-shell" ./scripts/quality_shell_validator.sh --repo-root .
queue_selected "fixture-path" python3 scripts/quality_validator.py --path scripts/shared_input.py
queue_selected "fixture-echo" echo "run python3 scripts/echo_advice.py --repo-root ."
queue_selected "fixture-command-payload" bash -c 'python3 scripts/payload_validator.py'
queue_selected "$COMPUTED_LABEL" python3 scripts/quality_validator.py

queue_selected() {
  :
}
