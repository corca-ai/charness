# Continuation Sequence

Use this when more than one pickup path is plausible and the next operator
could misread the order.

## Core Moves

- record the first action, not just the eventual goal
- keep next actions in dependency order
- surface the first irreversible or high-cost move explicitly
- keep only the state facts that change what should happen next

## Translation For Handoff

- if a file must be read first, name it before broader goals
- if a manual operator step exists, place it exactly where the sequence needs it
- if a recovery path matters, put it next to the triggering action rather than
  burying it in history
