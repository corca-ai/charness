# Authoring Preflight

Know the deterministic constraint *before* you author into a gated surface, so an
existing gate (or a fresh-eye reviewer) does not catch an avoidable rework cycle
after the fact. This reference gathers the three robustness traps: banned
attention-state vocabulary, single-file length headroom, and string-matching
edge cases (#308). It adds no new gate and no edit-time
hook — the gates already exist; this is the discoverable list of what they check.

Read this alongside the headroom and skill-surface preflight bullets in
[implementation-discipline.md](./implementation-discipline.md).

## Attention-state banned vocabulary

[validate_attention_state_visibility.py](../../scripts/validate_attention_state_visibility.py)
scans Python **string constants**
(status strings *and docstrings*) under `scripts/` and `skills/` for exit-zero
attention-state terms. A new module that uses one of these as a bare status — or
a docstring that contains one (the #302 `"silently-skipped"` detour, which
matched `skipped`) — fails the gate unless the file is declared in
[skills/public/quality/references/attention-state-visibility.json](../../skills/public/quality/references/attention-state-visibility.json)
with a visibility and rationale.

Current banned terms (the canonical list is `ATTENTION_TERMS` in the validator;
the drift guard
[tests/test_authoring_preflight_reference.py](../../tests/test_authoring_preflight_reference.py)
keeps this list in sync):

- `no_adapter`
- `no_records`
- `disabled`
- `not_configured`
- `not_evaluable`
- `skipped`
- `advisory-only`
- `prose_review_status`

Before authoring: if the module genuinely reports one of these states, make it
visible (a `WARN:`/`ADVISORY:`-prefixed line, an artifact-visible status, or a
terminal-payload status field) and declare it. Do not reach for the heavyweight
public-skill-validation declaration when a reworded docstring avoids the term
entirely (the #302 over-correction). Prefer the wording that does not read as a
silent skip.

## Length headroom

Before a large addition to a `scripts/*.py` or skill-helper file, check how much
room is left:

```bash
python3 scripts/check_python_lengths.py --repo-root . --headroom --paths <file>
```

It prints `limit − current` (tokei Python code lines) per gated file and flags
near-limit files. If a file is near its limit, start a new module instead of
appending — that avoids the unplanned mid-slice extraction `acquire_public_url.py`
forced during #302.
[run_slice_closeout.py](../../scripts/run_slice_closeout.py) also auto-surfaces
near-limit *changed* files at every slice closeout, so this is workflow signal, not memory
(#256). The advisory never blocks; the length gate is the hard floor.

## SKILL.md core headroom

A `skills/public/**` or `skills/support/**` `SKILL.md` core (frontmatter and body
above the exempt `## Load-Bearing Anchors` / `## References` sections) is governed
by *two* separate limits: a hard `core_nonempty` ceiling of **160** lines, and a
broad-gate test that additionally requires at least **4** lines of headroom below
that ceiling. Authoring a core to exactly 160 (0 headroom) passes the hard limit
but fails the headroom buffer — the trap that bit `achieve/SKILL.md` during the
306-317 goal.

[check_skill_surface_preflight.py](../../scripts/check_skill_surface_preflight.py)
gates this buffer at the commit boundary for *changed* SKILL.md files (it runs in
[staged_commit_gate_plan.py](../../scripts/staged_commit_gate_plan.py) and so in
`run_slice_closeout.py --predict-commit`), instead of only in the broad gate. It
is a ratchet: a change that drops a core below the 4-line buffer is blocked, but a
skill already under buffer is grandfathered until an edit erodes it further. Check
headroom before authoring, and on a block move prose into `references/` or a
helper `scripts/` file rather than trimming to the hard limit:

```bash
python3 scripts/check_skill_surface_preflight.py --path skills/public/<skill>/SKILL.md
```

## Portable skill packages

A file under `skills/public/**` or `skills/support/**` ships as a *portable*
package, so
[validate_skill_ergonomics.py](../../scripts/validate_skill_ergonomics.py)
flags package text (SKILL.md,
references, **and helper scripts — including their comments**) that embeds
origin-repo-specific anchors. Authoring a fix into a skill-package helper is the
trap: a `(#NNN)` provenance comment that is fine in a `scripts/` repo file trips
`portable_package_issue_anchor` in a skill package.

Before authoring into a skill package, avoid (or expect to declare):

- bare issue anchors — `#310`, `owner/repo#5`, `issues/5` (keep issue provenance
  in the commit message and the goal/critique artifact, not the package).
- dated incident references — `2026-06-05 ... regression/trap/lesson`.
- host-surface references — `Claude Code`, `Codex`, `settings.json`,
  `.claude/`, `.codex/` (host specifics belong in adapters/presets).

Run the ergonomics validator after touching a skill package; it is fast and
catches these before the broad gate:

```bash
python3 scripts/validate_skill_ergonomics.py --repo-root .
```

## Regex / string-matching edges

When a check matches a version, identifier, or other token by string content,
broad scanning regexes accept inputs you did not intend (the #305
`update_instructions` staleness check was first a general semver-scan regex, then
rewritten to previous-vs-target containment after a fresh-eye reviewer flagged
date and `v`-prefix edges). Before shipping a string/regex check, walk this list:

- Prefer explicit containment or equality over an unbounded scan when you only
  need "does X mention version V".
- Anchor patterns (`^`/`$`) and avoid unbounded `.*`; ask what a partial or
  substring match would falsely accept.
- Test against edge inputs: a date that looks like a version (`2026.06.05`), a
  `v`-prefixed value (`v0.20.0`), the no-op case where previous == target, and
  the absent-value case (nothing to match).
- Decide fail-open vs fail-closed deliberately when the token is missing.
