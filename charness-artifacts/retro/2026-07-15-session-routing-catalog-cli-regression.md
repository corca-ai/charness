# Session Routing and Catalog CLI Regression Retro
Date: 2026-07-15

## Mode

session

## Context

An agent in a consumer repository attempted the removed `charness find-skills`
command, then treated its rejection as an inability to inspect skills. The
operator correctly identified that the session-start and AGENTS guidance should
have prevented that inference. Investigation also reproduced a separate
installed-CLI defect: `charness catalog list` could not import its backend when
the CLI was copied to `~/.local/bin`.

## Evidence Summary

- `charness --help` lists `catalog` but no `find-skills` subcommand.
- `scripts/session_start_routing.py` and the setup routing renderer recommend
  `charness catalog list`, but neither forbids the retired name nor says how to
  interpret an inventory-command failure.
- The installed CLI at `/home/hwidong/.local/bin/charness` raised
  `ModuleNotFoundError: No module named 'scripts'` for `catalog list` while
  `charness version --json` identified a managed checkout.
- Packet Consumed: `charness-artifacts/retro/2026-07-15-021844-packet.md`.

## Waste

The public-removal work retained a positive replacement command but left its
ordinary-task action less direct than it should be: start the matching workflow
from metadata and judgment, then use the exact inventory command only for an
unclear hidden-availability question. The old loader test also reused an
already imported backend, so it did not exercise a standalone installed CLI.

## Critical Decisions

- Keep ordinary routing with installed metadata and model judgment; do not
  reintroduce a semantic `find-skills` command.
- State the direct ordinary-task action, exact inventory action, and
  failure-interpretation action in the session hook and setup-generated AGENTS
  guidance without a prohibitory command list.
- Make the copied CLI load the catalog backend from its managed checkout and
  prove that path in a subprocess regression test.

## Expert Counterfactuals

- Engelbart's system-improving-itself lens would specify the tool, routing
  language, and installed-runtime proof as one replacement contract. The
  surviving instructions should state the next required action precisely rather
  than growing a list of prohibited historical commands.

## Sibling Search

- same layer: `scripts/session_start_routing.py` | decision: same waste, fix now | proof: its directive reaches each host session
- abstraction up: `skills/public/setup/scripts/render_skill_routing.py` and `AGENTS.md` | decision: same waste, fix now | proof: generated and repo-local routing guidance share the same contract
- specialization down: `charness` catalog loader and `tests/charness_cli/test_codex_cache_refresh.py` | decision: same waste, fix now | proof: copied CLI import path is the concrete runtime failure
- mental-model siblings: historic cleanup markers in `scripts/host_hook_session_routing.py` | decision: intentional boundary | proof: they remove old host configuration and must retain the legacy token

## Next Improvements

- workflow: applied: state direct ordinary-task routing and the exact conditional inventory action in the same replacement contract.
- capability: applied: session and generated-AGENTS routing state the matching-workflow action and command-failure reporting action without a prohibition list.
- memory: applied: persist this retro and the matching debug record with the focused installed-CLI regression proof.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-15-session-routing-catalog-cli-regression.md
