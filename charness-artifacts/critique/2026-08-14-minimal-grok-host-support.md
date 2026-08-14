# Minimal Grok Host Support Critique
Date: 2026-08-14

## Decision Under Review

Ship the smallest honest Grok Build install path: copy the exported plugin
tree to `~/.grok/plugins/charness`, detect `grok`, surface doctor/preamble
next-steps, accept `--host grok`, and refuse a marketplace.

## Failure Angles

- Jackson: doctor/init/update might solve an adjacent helper-only problem.
- Weinberg: doctor `installed` is directory presence, not load-ready.
- Gawande: official init/update overwrite the enable/no-marketplace sentence.

## Counterweight Pass

- Compact projector omitting `grok_host_guidance` is bundle-anyway; `host_next_steps` already carries grok.
- `installed == is_dir()` is the automated half of this slice; enablement writes were out of scope.
- Official init/update clobbering the enable sentence is act-before-ship.
- Codex-exporter copy advice, README checklist, rmtree snapshot, uninstall config strip, and skip-as-0 are defer or over-worry.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness project_runtime_response | action: fix | note: add grok to the compact host_guidance loop.
- F2 | bin: valid-but-defer | evidence: strong | ref: charness build_grok_host_guidance | action: defer | note: installed==is_dir is the automated contract; enabled detection needs a later TOML reader.
- F3 | bin: act-before-ship | evidence: strong | ref: charness cmd_init host_next_steps merge | action: fix | note: doctor installed/needs-install messages now always name [plugins].enabled and no marketplace.
- F4 | bin: over-worry | evidence: moderate | ref: scripts/install_machine_local.py | action: document | note: official Grok copy is install_surface after support sync.
- F5 | bin: valid-but-defer | evidence: strong | ref: README.md | action: defer | note: README already calls Grok a minimal path; checklist stays in host-packaging.
- F6 | bin: valid-but-defer | evidence: strong | ref: charness ensure_grok_plugin | action: defer | note: rmtree+copytree matches Codex export.
- F7 | bin: valid-but-defer | evidence: strong | ref: charness remove_grok_plugin | action: defer | note: uninstall does not write ~/.grok/config.toml.
- F8 | bin: over-worry | evidence: strong | ref: charness ensure_grok_plugin missing source | action: document | note: skip is a helper no-op after export.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: charness:bounded-reviewer read-only one-shot, inherited model, no host name
- Host exposure state: requested_fields_sent
- Application state: four parent-delegated reviewers completed (Jackson, Weinberg, Gawande, counterweight); F3 repaired in-tree before commit
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; Jackson, Weinberg, Gawande, and counterweight findings were received. F3 repaired. Remaining findings accepted as defer or over-worry.

## Boundary Ownership

- Producer: charness CLI install_surface / ensure_grok_plugin
- Consumer: Grok Build loading `~/.grok/plugins/charness` when `[plugins].enabled` lists `charness`
- Owning surface: host-packaging Grok Build section and doctor grok_host_guidance
- Verdict: owned-correctly
