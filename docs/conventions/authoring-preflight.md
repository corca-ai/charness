# Authoring Preflight

Know the deterministic constraint *before* you author into a gated surface, so an
existing gate (or a fresh-eye reviewer) does not catch an avoidable rework cycle
after the fact. This reference gathers the three traps from the #302–#305
robustness goal (#308): banned attention-state vocabulary, single-file length
headroom, and string-matching edge cases. It adds no new gate and no edit-time
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
