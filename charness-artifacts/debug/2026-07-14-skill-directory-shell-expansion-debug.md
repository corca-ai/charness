# Skill Directory Shell Expansion Debug
Date: 2026-07-14

## Problem

In a consuming repository, a debug-skill bootstrap attempt used
`SKILL_DIR=/path python3 "$SKILL_DIR/scripts/..."` and Python tried
`/scripts/...` because the shell expanded an unset variable before applying the
command-scoped assignment.

## Correct Behavior

Given a source checkout or installed plugin path, when an agent or operator
resolves the skill directory, then every later bootstrap command sees the same
non-empty exported value and executes the intended installed script.

## Observed Facts

- The reported v1.0.4 run failed three commands with `python3: can't open file
  '/scripts/...': [Errno 2] No such file or directory` and succeeded after
  exporting the variable first.
- In the current Codex command environment, `SKILL_DIR` is unset.
- `skills/shared/references/bootstrap-resolution.md` says agent runtimes inject
  the variable automatically and shows non-exported assignments for source and
  manual-shell use.
- The released v1.0.5 debug SKILL resolves through that shared reference;
  source, plugin export, and installed-cache copies initially retained the same
  unsafe contract.

## Reproduction

- With `SKILL_DIR` unset, run `SKILL_DIR=/tmp/example python3
  "$SKILL_DIR/scripts/resolve_adapter.py"`; shell expansion produces
  `/scripts/resolve_adapter.py` before Python starts.

## Candidate Causes

- POSIX shell expansion order makes command-scoped assignment unavailable to
  expansions on the same simple command.
- The shared bootstrap reference overstates host injection and leaves agents to
  improvise an unsafe one-liner.
- Only the old v1.0.4 cache is affected and v1.0.5 already corrected the
  reference.
- One shell implementation behaves differently from the documented contract.

## Hypothesis

- falsifiable claim: the current shared reference still permits the exact
  expansion-order failure across shells and exported two-step assignment fixes
  it; correcting the source reference, adding a validator, and syncing the
  plugin export will close the class | disconfirmer: inspect current source and
  plugin reference text, reproduce in supported shells, and execute the
  corrected snippet from an unrelated consuming-repo directory.

## Verification

- result: confirmed — `sh`, `bash`, and `zsh` each expanded the reported
  command-scoped form to `/scripts/resolve_adapter.py`, while a separate
  `export` expanded to `/tmp/example/scripts/resolve_adapter.py`.
- source and synchronized plugin debug resolvers both executed successfully
  from an unrelated temporary repository root using the documented export.
- five focused validator tests passed; the validator accepted all 21 skill
  packages and source/plugin reference and validator copies are identical.

## Root Cause

The shared contract conflated an agent-visible skill source locator with an
exported shell variable, then showed non-exported assignments without warning
about same-command expansion order. Because every skill delegated resolution
to that reference and the gate checked only the citation, an agent could form a
plausible but invalid environment-prefix command and the wrong answer escaped
into a released plugin.

Fresh-eye review also found a sibling lifetime/path ambiguity: a relative
source path only works from the Charness source root, and an export in one
ephemeral command tool call is unavailable to a later call. The final reference
therefore groups export and invocation in one shell block and shows an absolute
source path for consuming-repo execution.

## Invariant Proof

- Invariant: a resolved skill path must survive from resolution through every
  bootstrap command in source, plugin, and consuming-repo layouts.
- Producer Proof: the canonical reference now uses separate exported
  assignments and the validator rejects non-exported canonical shell examples.
- Final-Consumer Proof: source and synchronized plugin debug resolvers ran from
  an unrelated temporary repository with the documented export.
- Interface-Shape Sibling Scan: all 21 public/support skills cite the shared
  contract; no other tracked command-scoped `SKILL_DIR` or
  `CHARNESS_SUPPORT_DIR` assignment was found.
- Non-Claims: the released v1.0.5 installed cache remains unchanged until a
  later release/update; no claim covers every future host's environment.

## Detection Gap

- shared bootstrap-variable lint | checked only that SKILL files cited the
  shared reference, not that the reference's shell assignment was safe | it now
  rejects non-exported `SKILL_DIR` assignments in canonical shell fences.

## Sibling Search

- Mental model: path discovery was treated as equivalent to exported shell
  state, ignoring expansion order and host-tool environment boundaries.
- same layer: source and plugin copies of the shared reference | decision: same
  bug, fix now | proof: synchronized copies plus local payload proof.
- abstraction up: public/support SKILL bootstrap blocks | decision: same class,
  diagnostic-only for this slice | proof: they cite the shared contract.
- specialization down: source-checkout and installed-cache assignments |
  decision: same bug, fix now | proof: source and plugin-layout roundtrip; the
  released cache is a valid follow-up outside the slice | follow-up: deferred
  docs/handoff.md Next Session release/update boundary.
- cross-file: `scripts/check_skill_bootstrap_vars.py` is the existing final
  gate that currently trusts the cited reference without validating it.

## Seam Risk

- Interrupt ID: skill-dir-shell-expansion
- Risk Class: external-seam
- Seam: skill source locator to shell environment and installed helper command
- Disproving Observation: current Codex shell has no injected `SKILL_DIR`, and
  all three local shells reproduce the expansion-order failure.
- What Local Reasoning Cannot Prove: exact environment behavior of every future
  Claude Code and Codex host release.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-14-skill-directory-shell-bootstrap.md

## Prevention

Keep export-before-use explicit and retain the canonical-reference validator
plus unrelated-directory source/plugin proof. Do not treat host source metadata
as evidence that the tool shell inherited an environment variable, and do not
split export and dependent expansion across ephemeral tool invocations.
