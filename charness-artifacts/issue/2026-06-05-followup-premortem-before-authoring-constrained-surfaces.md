## Observed problem

During the #302–#305 robustness goal, three avoidable rework cycles shared one
root cause: authoring into a *constrained/gated* surface before checking the
constraint, so an existing gate caught the violation later than ideal.

- **Gate vocabulary:** a new web-fetch support module's docstring used
  "silently-skipped", which the `attention-state-visibility` gate flags. The
  first fix went the wrong (heavyweight) direction — declaring the module in
  `skills/public/quality/references/attention-state-visibility.json` (pulling in
  the public-skill-validation gate) — then was reverted and the docstring
  reworded.
- **Length headroom:** `acquire_public_url.py` was already near the
  skill-helper `check_python_lengths` limit; adding to it forced an unplanned
  mid-slice module extraction.
- **Regex edges:** the #305 `update_instructions` staleness check was first
  written as a general semver-scan regex, then rewritten to previous-vs-target
  containment after fresh-eye review flagged date / `v`-prefix edge cases.

## Structural pattern

An agent authors content into a surface governed by a deterministic constraint
(banned-vocabulary gate, single-file length limit, string-matching edge cases)
without first reading the constraint, so avoidable rework is caught by the gate
(or a fresh-eye reviewer) after the fact rather than avoided up front.

## Triggering instance(s)

#302 attention-state docstring detour; #302 acquire length-gate refactor; #305
staleness regex→containment rewrite (2026-06-05 robustness goal).

## Suggested direction (not a decision)

Consider a lightweight "authoring preflight" affordance: a discoverable list of
the attention-state banned vocabulary near where support-module prose is
authored, surfacing `check_python_lengths` headroom before editing a near-limit
file, and a regex/string-matching edge checklist. Weigh against adding process
overhead; much of this is agent discipline that the existing gates already
enforce (just later than ideal). This is a workflow/discoverability change.

## Destination

charness (skill-authoring discipline / discoverability of existing gate
constraints). Sibling to #307 (which covers *when* a cheap checker runs); this
covers *knowing the constraint before authoring*.
