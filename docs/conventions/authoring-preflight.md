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

## Artifact-shape preflight (charness-artifacts/**)

The skill-surface preflight above covers `skills/**` edits. The hand-authored
**artifact** family (`charness-artifacts/critique/*.md`, goal
`## Final Verification` closeout-evidence, retro, ideation, plus the
adapter-scoped debug/quality/handoff) is covered by
[check_artifact_surface_preflight.py](../../scripts/check_artifact_surface_preflight.py).
It generalizes the same author-time idea to the recurring "authoring-preflight
skip" class (issues 284 → 308 → 325 → 329 → 332 → 334): an author should learn an
artifact's required shape at author time, not by failing the broad gate (the 334
instance: a hand-authored critique missing `## Reviewer Tier Evidence` cost a
second full gate run).

Before authoring an artifact, surface its required shape (the dispatcher reads it
from the owning scaffold/template/validator — it never re-declares it):

```bash
python3 scripts/check_artifact_surface_preflight.py --type critique          # required shape
python3 scripts/check_artifact_surface_preflight.py --type critique --emit-stub  # starter stub
python3 scripts/check_artifact_surface_preflight.py --path <artifact>         # shape + current verdict
```

This is not merely a doc: the dispatcher's `--changed-artifacts` mode is wired
into [staged_commit_gate_plan.py](../../scripts/staged_commit_gate_plan.py) as a
**blocking** `STRUCTURAL_SWEEP_LABELS` member (`check-artifact-shape (staged)`),
exactly like the SKILL.md core-headroom gate. When a commit touches a
changed-scoped prefix family (critique/ideation/retro), its owning validator runs
at the commit boundary — the *same* validator with the *same* verdict, only
relocated earlier. It adds no new shape requirement and changes no validator's
judgment. The adapter-scoped trio (debug/quality/handoff) validate-all and are
author-time-only (`--type`/`--emit-stub`/`--path`); the broad gate remains their
enforcement (see the coverage report for the tier rationale).

### Closeout surfaces (closeout-draft + goal-closeout)

The same author-time idea covers the two closeout surfaces whose required shape
an author otherwise discovers by failing the validator several times:

```bash
python3 scripts/check_artifact_surface_preflight.py --type closeout-draft   # issue closeout body shape
python3 scripts/check_artifact_surface_preflight.py --type goal-closeout     # goal complete-gate forms
python3 scripts/check_artifact_surface_preflight.py --type goal-closeout --emit-stub  # fill-in closeout starter
```

- `closeout-draft` surfaces what `issue_tool.py validate-closeout-draft` (which
  reuses `verify_closeout`) enforces: the carrier-body source (for `direct-commit`
  pass `--commit-message-file`, not `--body-file`), the close keyword, the
  `resolution_critique` evidence (the cited critique must itself pass
  `validate_critique_artifacts`), and the per-classification ledger fields.
- `goal-closeout` pairs the goal template's `## Final Verification` block with the
  enforced FORMS `check_goal_artifact.py` applies at the complete flip: the allowed
  skip-reason enum, the bare-path + goal-slug binding, the disposition form, and the
  `Routing:` form.

Both are author-time-only (the validators stay the enforcement): a `closeout-draft`
verdict needs the full `validate-closeout-draft` command, and `goal-closeout` is
owned at the achieve complete flip. Each shape is rendered live from the owning
validator's constants by a `describe_*_shape.py` sibling, so it cannot drift from
the gate.

## General doc surfaces (docs/*.md)

The skill-surface and artifact-shape preflights above cover `skills/**` and
`charness-artifacts/**`. General docs — the handoff artifact and the rest of
`docs/*.md` — are the remaining surface class: an author there discovers
markdownlint rules (the `MD004` list-marker style, a wrapped inline-code span,
trailing space), the
[check_doc_links.py](../../scripts/check_doc_links.py) pathy-ref / link form,
and the surface length cap (the handoff line cap) one commit-gate failure at a
time. Forecast them all in one pass:

```bash
python3 scripts/check_doc_authoring_preflight.py --path docs/handoff.md
```

[check_doc_authoring_preflight.py](../../scripts/check_doc_authoring_preflight.py)
reuses the real validators — `check_markdown_inline_code`, `check_doc_links`,
markdownlint-cli2 with the repo config, and the owning length constant — so the
forecast cannot drift from what the gate enforces. Pass `--as-surface handoff`
to forecast a capped surface's length floor on a draft path. It is an affordance,
not a gate: a doc still commits without it, the existing gates stay the
enforcement, and
[run_slice_closeout.py](../../scripts/run_slice_closeout.py) prints an
`ADVISORY:` pointer when a slice edits a `docs/*.md` surface.

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

### Edit-time issue-anchor scan

The package sweep above runs over the whole skill surface at the commit boundary
(`run_slice_closeout` / pre-commit). To catch a `#NNN` anchor on the *one file*
you just edited — before the closeout machinery round-trips — scan that file
directly:

```bash
python3 scripts/check_skill_surface_preflight.py --scan-issue-anchors skills/public/<skill>/scripts/<file>.py
```

It reuses the exact `validate_skill_ergonomics` rule (`ISSUE_ANCHOR_RE` plus the
`is_allowed_issue_anchor_context` allow-list), so its verdict matches the commit
sweep per file: a disallowed anchor exits 1; allowed contexts (version fields,
placeholder issue URLs) pass. Accepts any skill-package text file — including
helper `scripts/` — not just `SKILL.md`. It is additive: the commit-time sweep
stays the backstop.

On Claude hosts the scan also fires automatically after each edit: the
`skill_anchor_edit_guard` intent in
[.agents/usage-episodes-adapter.yaml](../../.agents/usage-episodes-adapter.yaml)
installs a `PostToolUse(Edit|Write|MultiEdit)` hook (via `charness init` /
`charness update`, the same machinery as the SessionStart hooks) that runs
[scripts/post_edit_skill_anchor_guard.py](../../scripts/post_edit_skill_anchor_guard.py)
on the file just edited. The guard is
fail-open and scoped to `skills/public|support` files in this repo — a repo or
machine without the adapter intent inherits nothing. The firing stays
host-specific and adapter-declared; the scan stays the single repo-owned rule
source, and the commit sweep stays the backstop.

Multi-checkout posture (#343, decided 2026-06-10): charness installs **one
logical hook per machine**, deduped by script basename across checkouts —
NOT one hook per checkout, which would make every shared host event fire each
checkout's copy of the same guard. The commit-time sweep is the backstop for
edits made in a checkout the surviving hook does not cover. The trade is that
the installed hook binds one checkout's absolute script path; when that
checkout is moved (or the hook script disappears),
`python3 scripts/reconcile_usage_episodes_host_hooks.py --mode status`
(= `charness session-capture status`) flags the dangling state-tracked hook
via its `hook_liveness` section — reinstall from a live checkout or
uninstall. A *deleted* checkout's leftover settings entries are invisible to
state (the state file dies with the deleted checkout); the same status
surface's `settings_scan` section catches them by reading the host settings
files directly (claude `settings.json`, codex `hooks.json`, codex
`config.toml`) and flagging entries whose command carries a known charness
hook-script basename — derived from the owning modules' script constants,
never a forked list — but whose embedded path no longer exists. Both
sections join the exit-1 drift list; missing or unreadable settings files
degrade to silence, and foreign hooks are never flagged.

### One-shot portable-package preflight

Authoring into a skill package otherwise pays for the portable-package gates as
*serial* commit-boundary failures — one round-trip each for the ergonomics
issue-anchor, a cross-namespace ownership overlap, and a new exit-zero
attention-state term. Run them all at once instead:

```bash
python3 scripts/check_skill_surface_preflight.py --path skills/public/<skill>/SKILL.md --run-checks
```

`--run-checks` reports `validate_skills`, `validate_skill_ergonomics`,
`check_skill_ownership_overlap`, `validate_attention_state_visibility`,
`check_doc_links`, and `check-markdown` together, so the whole portable-package
set surfaces in one pass. `run_slice_closeout.py` also prints an `ADVISORY:`
pointer to this command when a slice edits a gated `skills/public/**` or
`skills/support/**` surface.

## Doc/SKILL prose and path pins

A `tests/` literal-string assertion that copies prose from a doc/SKILL.md, or
references one by path, breaks when you reword the prose or rename/delete the
file — and the broad pytest only surfaces it minutes later. Before paying for
that cycle, check which test pins your changed surfaces:

```bash
python3 scripts/check_prose_pin.py --repo-root .
```

It reads the working-tree diff and reports the likely-broken pins (the test file,
line, and the pinned phrase or path). It is advisory by default (`--strict` exits
non-zero), and `run_slice_closeout.py` surfaces the same `WARN:` lines at slice
closeout before the broad pytest runs.

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
