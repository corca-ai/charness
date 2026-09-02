#!/usr/bin/env bash

queue_selected() {
  :
}

queue_selected "shell-only" python3 scripts/shell_only.py
queue_selected "check-rust" echo shell-command
