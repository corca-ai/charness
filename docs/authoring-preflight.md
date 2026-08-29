# Authoring Preflight

> Status: current
> Source of truth: this page and its linked executable surfaces

Know the deterministic constraint *before* you author into a gated surface, so an
existing gate (or a fresh-eye reviewer) does not catch an avoidable rework cycle
after the fact. This reference gathers the three robustness traps: banned
attention-state vocabulary, single-file length headroom, and string-matching
edge cases (#308). It adds no new gate and no edit-time
hook — the gates already exist; this is the discoverable list of what they check.

Read this alongside the headroom and skill-surface preflight bullets in
[implementation-discipline.md](./implementation-discipline.md).

## Attention-state banned vocabulary

[validate_attention_state_visibility.py](../scripts/validate_attention_state_visibility.py)
scans Python **string constants** under `scripts/` and `skills/` for exit-zero
attention-state terms, and reads them as STATUS VALUES rather than as words. A
term counts when it is token-shaped — the whole value (`"skipped"`), one part of
a state-shaped token (`"silently-skipped"`), or one side of a labelled field
(`"WARNING: skipped"`, `"status=not_configured"`) — never when it is a word
inside an English sentence, and never inside a docstring. That split is what
ended the #302 `"silently-skipped"` docstring detour and its repeat; it also
CAUGHT two real states a substring scan could not see, because they were spelled
with a different separator (`advisory_only_no_cli_surface`, `not-configured`).
A module that uses one of these as a status fails the gate unless it is declared in
[skills/public/quality/references/attention-state-visibility.json](../skills/public/quality/references/attention-state-visibility.json)
with a visibility and rationale.

Current banned terms (the canonical list is `ATTENTION_TERMS` in the validator;
the drift guard
[tests/test_authoring_preflight_reference.py](../tests/test_authoring_preflight_reference.py)
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
python3 scripts/check_code_lengths.py --repo-root . --headroom --paths <file>
```

It prints `limit − current` (tokei Python code lines) per gated file and flags
near-limit files. If a file is near its limit, start a new module instead of
appending — that avoids the unplanned mid-slice extraction
[`acquire_public_url.py`](../skills/support/web-fetch/scripts/acquire_public_url.py)
forced during #302.
The advisory never blocks; the length gate is the hard floor.

## SKILL.md core headroom

A `skills/public/**` or `skills/support/**` `SKILL.md` core (frontmatter and body
outside the exempt `## Load-Bearing Anchors` / `## References` /
`## Closeout Vocabulary` sections — exempt only up to each heading's budget in
[`scripts/skill_core_density.py`](../scripts/skill_core_density.py), with the
overflow charged back to the count) is governed
by *two* separate limits: a hard `core_nonempty` ceiling of **160** lines, and a
broad-gate test that additionally requires at least **4** lines of headroom below
that ceiling. Authoring a core to exactly 160 (0 headroom) passes the hard limit
but fails the headroom buffer — the trap that bit `achieve/SKILL.md` during the
306-317 goal.

**The preflight's `core nonempty` is not the quality inventory's
`core_nonempty_lines`.** [skill_ergonomics_lib.py](../skills/public/quality/scripts/skill_ergonomics_lib.py)
keeps its own exemption walk — it must stay skill-local-portable, so it cannot
import the repo module — and that copy exempts only `## Load-Bearing Anchors` /
`## References`, without a budget, without an audit, and without fence awareness
(a literal `## References` inside a code fence still opens a real exempt block
there). The two numbers therefore
diverge on any skill carrying a `## Closeout Vocabulary` block or an over-budget
exempt section. Quote the **inventory's** number in a quality artifact:
[validate_quality_artifact.py](../scripts/validate_quality_artifact.py)
recomputes it and hard-fails a mismatch.

[check_skill_surface_preflight.py](../scripts/check_skill_surface_preflight.py)
gates this buffer at the commit boundary for *changed* SKILL.md files (it runs in
[staged_commit_gate_plan.py](../scripts/staged_commit_gate_plan.py) and so in
the pre-commit dispatcher), instead of only in the broad gate. It
is a ratchet: a change that drops a core below the 4-line buffer is blocked, but a
skill already under buffer is grandfathered until an edit erodes it further. Check
headroom before authoring. On a block, separate a concept into its own surface or
delete one — never shave lines or displace overflow into `references/` just to
dodge the cap (P2: moving a genuinely separate concept to its own reference file
is fine; stashing overflow there just to fit is not). Procedural detail can still
move to a helper `scripts/` file when that is its natural home:

```bash
python3 scripts/check_skill_surface_preflight.py --path skills/public/<skill>/SKILL.md
```

## Artifact-shape preflight (charness-artifacts/**)

The skill-surface preflight above covers `skills/**` edits. The hand-authored
**artifact** family (`charness-artifacts/critique/*.md`, retro, ideation, plus
the adapter-scoped debug/quality) is covered by
[check_artifact_surface_preflight.py](../scripts/check_artifact_surface_preflight.py).
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
into [staged_commit_gate_plan.py](../scripts/staged_commit_gate_plan.py) as a
**blocking** `STRUCTURAL_SWEEP_LABELS` member (`check-artifact-shape (staged)`),
exactly like the SKILL.md core-headroom gate. When a commit touches a
changed-scoped prefix family (critique/ideation/retro), its owning validator runs
at the commit boundary — the *same* validator with the *same* verdict, only
relocated earlier. It adds no new shape requirement and changes no validator's
judgment. The adapter-scoped quality surface validates all by default and is
author-time-only (`--type`/`--emit-stub`/`--path`); the broad gate remains their
enforcement (see the coverage report for the tier rationale).

### Closeout surface (closeout-draft)

The same author-time idea covers the issue closeout surface whose required
shape an author otherwise discovers by failing the validator several times:

```bash
python3 scripts/check_artifact_surface_preflight.py --type closeout-draft   # issue closeout body shape
```

- `closeout-draft` surfaces what `issue_tool.py validate-closeout-draft` (which
  reuses `verify_closeout`) enforces: the carrier-body source (for `direct-commit`
  pass `--commit-message-file`, not `--body-file`), the close keyword, the
  `resolution_critique` evidence (the cited critique must itself pass
  `validate_critique_artifacts`), and the per-classification ledger fields.
`closeout-draft` is author-time-only: its verdict needs the full
`validate-closeout-draft` command. The shape is rendered live from the owning
validator's constants by a `describe_*_shape.py` sibling, so it cannot drift from
the gate.

## General doc surfaces (docs/*.md)

The skill-surface and artifact-shape preflights above cover `skills/**` and
`charness-artifacts/**`. General `docs/*.md` is the remaining surface class: an
author there discovers
markdownlint rules (the `MD004` list-marker style, a wrapped inline-code span,
trailing space), the
[check_doc_links.py](../scripts/check_doc_links.py) pathy-ref / link form,
one commit-gate failure at a time. `check_doc_links` also resolves the repo-owned script a documented command
names — in a fenced block or an inline span — so a `python3 scripts/…` example
cannot outlive the script it names. See
[Documented commands](#documented-commands) for the escape. Forecast them all in
one pass — and, before a single line exists, ask it for the rules instead:

```bash
python3 scripts/check_doc_authoring_preflight.py --path docs/index.md # a real target against them
```

The rules mode is what makes this surface match its sibling
([`check_skill_surface_preflight.py`](../scripts/check_skill_surface_preflight.py),
which describes by default). Every other
check here is content-driven, so without it an author got the rules only *after*
writing the thing that breaks them and one rework cycle was structurally
guaranteed. The rules are rendered, never restated: each line is
the owning validator's own constant, or the verdict that validator returns when
the preflight probes it with a sample.

[check_doc_authoring_preflight.py](../scripts/check_doc_authoring_preflight.py)
reuses the real validators — `check_markdown_inline_code`, `check_doc_links`,
and markdownlint-cli2 with the repo config — so the forecast cannot drift from
what the gate enforces WHEN EACH CLASS RUNS. A class
that could not run is reported in the payload's `unforecast_classes`, never as
clean: an absent markdownlint engine puts its class in that list and appends a
warning naming the remedy.
An empty `unforecast_classes` means no class reported itself unmeasured — which
is the strongest claim the collectors support, not a guarantee that everything
was measured. It is an affordance, not a gate: a doc still commits without it;
the existing gates stay the enforcement.

## Documented commands

Every markdown surface the gate covers — the repo readme, AGENTS.md, `docs/*.md`,
presets, profiles, and portable skill packages — has its documented commands
resolved against the repo's own git file listing. A fenced or inline command
naming a repo-owned script (a `python3`, `bash`, `sh`, or dot-slash invocation)
must name a script that exists, so a rename or deletion cannot leave a command
example that only looks runnable.

Two escapes, for the case where a command deliberately names something this repo
does not own — most often a portable skill documenting the *consuming* repo's
command:

- a `<repo-root>/`, `<plugin-dir>/`, `<skill-dir>/`, or `<authoring-repo>/` prefix;
- any `<…>` placeholder inside the path, e.g. `scripts/<name>.py`.

### `<repo-root>/` vs `<authoring-repo>/`

These are **not** synonyms, and the distinction is load-bearing.

- `<repo-root>/` means *the tree the reader is operating on*. It is unverifiable
  from here by definition, so it is exempt from resolution — **with one
  decidable exception**: when the named script is sitting in a skill package of
  *this* tree, the consumer-tree prefix is wrong no matter whose tree it is, and
  [inventory_skill_script_references.py](../scripts/inventory_skill_script_references.py)
  refuses it. That is the counted defect this whole convention exists to stop,
  and it is the only shape of `<repo-root>/` that can fail a gate. Absence alone
  never fails — a skill may correctly say "point your gate at
  `<repo-root>/scripts/run_pre_push.py`" about a file only the consumer has.
  When the basename exists BOTH in a package and at the authoring root the
  reference is genuinely ambiguous, and ambiguous is not blockable.
- `<authoring-repo>/` means *the charness repo itself* — "this is mine, not
  yours". It IS verifiable here, and
  [inventory_skill_script_references.py](../scripts/inventory_skill_script_references.py)
  resolves it rather than waving it through.

Why the split exists: 13 shipped commands accumulated undetected because a
reference to charness's own script wearing the consumer's placeholder is
indistinguishable from a typo — to this gate, and to a human reading the line.
The escape hatch and the defect were the same token. Giving the authoring-repo
case its own spelling makes the class diagnosable by eye instead of only by a
bespoke scanner.

Choosing between them, in one question: **who evaluates this path?**

- The reader, against their own tree → `<repo-root>/`. Example:
  [rca-ledger-append.md](../skills/shared/references/rca-ledger-append.md) gates a step on whether
  `<repo-root>/scripts/record_rca_event.py` exists; for a consumer that
  correctly evaluates false and the step is a documented no-op.
- Nobody — the sentence is describing what charness ships → `<authoring-repo>/`.
  Example: "`charness` wraps that path explicitly in
  `<authoring-repo>/scripts/check_supply_chain_online.py`".

A path the reader is told to RUN, that only exists in the authoring repo, is
neither: it is a bug, and belongs in the skill's own package or behind
`<plugin-dir>/`.

A command documented inside a portable skill package resolves against the package
root as well as the repo root, so a skill's own `scripts/` helper is found from
its SKILL.md and references without spelling out the full `skills/<kind>/<name>/`
prefix.

## Portable skill packages

A file under `skills/public/**` or `skills/support/**` ships as a *portable*
package, so
[validate_skill_ergonomics.py](../scripts/validate_skill_ergonomics.py)
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
(pre-commit). To catch a `#NNN` anchor on the *one file* you just edited, scan that file
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

On Claude hosts the scan may also fire automatically after each edit through an
adapter-owned `skill_anchor_edit_guard` intent. The guard is fail-open and
scoped to `skills/public|support` files; the commit sweep remains the universal
backstop. A machine without that explicit host intent inherits no hook.

Multi-checkout posture (#343, decided 2026-06-10): charness installs **one
logical hook per machine**, deduped by script basename across checkouts —
NOT one hook per checkout, which would make every shared host event fire each
checkout's copy of the same guard. The commit-time sweep is the backstop for
edits made in a checkout the surviving hook does not cover. The trade is that
the installed hook binds one checkout's absolute script path; when that
checkout is moved (or the hook script disappears),
            the host-hook status surface flags the dangling state-tracked hook
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
set surfaces in one pass.

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
non-zero); run it directly when a prose edit needs this diagnostic.

### Pre-cut lossless + contract-safe check (skill-body cuts)

Cutting prose from a public/support `SKILL.md` has a sharper failure mode than a
reword: a removed phrase may be *pinned* (a CORE/PACKAGE contract or a `tests/`
literal requires it, so removal breaks a gate) or *lost* (its content vanishes
with no reference home). Verify both **before** the cut, not after a late gate
rejects it:

```bash
python3 scripts/check_skill_cut_safety.py --repo-root .            # changed SKILL.md vs HEAD
python3 scripts/check_skill_cut_safety.py --path skills/public/<skill>/SKILL.md
```

[check_skill_cut_safety.py](../scripts/check_skill_cut_safety.py) composes the
two pin surfaces (`check_skill_contracts` CORE/PACKAGE phrases +
`check_prose_pin` test literals) and adds the lossless half, with two severities:

- **BLOCK** (exit 1): a removed phrase broke a CORE pin (must stay in `SKILL.md`),
  a PACKAGE pin (may move to a reference but must survive the package), or a
  `tests/` literal. Restore or re-home the pinned phrase before cutting.
- **REVIEW** (exit 0): a removed prose line vanished with no reference home.
  Confirm it is a justified no-op deletion (the §5 no-op test — legitimate, needs
  no reference home) or re-home its content. This stays REVIEW, not BLOCK, on
  purpose: a hard "every removed line must reappear" rule would forbid the prune
  cure that diagnosis-first body redesign depends on. Use `--strict` to fail on
  REVIEW too when a caller wants the stricter gate.

It is a helper, not a new commit gate: the contract gate, prose-pin, and
core-headroom ratchet stay the enforcement; this consolidates their pre-cut view
into one declarative command so a body cut is lossless+contract-safe by
construction.

## Regex / string-matching edges

When a check matches a version, identifier, or other token by string content,
broad scanning regexes accept inputs you did not intend (the #305
`update_instructions` staleness check was first a general semver-scan regex, then
rewritten to concrete previous/target containment after a fresh-eye reviewer
flagged date and `v`-prefix edges). Before shipping a string/regex check, walk
this list:

- Prefer explicit containment or equality over an unbounded scan when you only
  need "does X mention version V"; for evergreen adapter text, a concrete version
  mention is usually the smell, not the remedy.
- Anchor patterns (`^`/`$`) and avoid unbounded `.*`; ask what a partial or
  substring match would falsely accept.
- Test against edge inputs: a date that looks like a version (`2026.06.05`), a
  `v`-prefixed value (`v0.20.0`), the no-op case where previous == target, and
  the absent-value case (nothing to match).
- Decide fail-open vs fail-closed deliberately when the token is missing.
