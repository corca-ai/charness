# Authoring Preflight

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

Know the deterministic constraint *before* you author into a gated surface, so an
existing gate (or a fresh-eye reviewer) does not catch an avoidable rework cycle
after the fact. This reference gathers the three robustness traps: banned
attention-state vocabulary, single-file length headroom, and string-matching
edge cases. It adds no new gate and no edit-time
hook — the gates already exist; this is the discoverable list of what they check.

Read this alongside the headroom and skill-surface preflight bullets in
[implementation-discipline.md](./implementation-discipline.md).

## Attention-state banned vocabulary

[validate_attention_state_visibility.py](../tools/validate_attention_state_visibility.py)
scans Python **string constants** under `scripts/` and `skills/` for exit-zero
attention-state terms, and reads them as STATUS VALUES rather than as words. A
term counts when it is token-shaped — the whole value (`"skipped"`), one part of
a state-shaped token (`"silently-skipped"`), or one side of a labelled field
(`"WARNING: skipped"`, `"status=not_configured"`) — never when it is a word
inside an English sentence, and never inside a docstring. The token-shaped
reading also catches two real states a substring scan cannot see, spelled with a
different separator (`advisory_only_no_cli_surface`, `not-configured`).
A module that uses one of these as a status fails the gate unless it is declared in
[skills/public/quality/references/attention-state-visibility.json](../skills/public/quality/references/attention-state-visibility.json)
with a visibility and rationale.

The terms live in `ATTENTION_TERMS` in that validator. Do not recopy them here.

Before authoring: if the module genuinely reports one of these states, make it
visible (a `WARN:`/`ADVISORY:`-prefixed line, an artifact-visible status, or a
terminal-payload status field) and declare it. Do not reach for the heavyweight
public-skill-validation declaration when a reworded docstring avoids the term
entirely. Prefer the wording that does not read as a silent skip.

## Length headroom

Before a large addition to a `scripts/*.py` or skill-helper file, check how much
room is left:

```bash
python3 scripts/gates/check_code_lengths.py --repo-root . --headroom --paths <file>
```

It prints `limit − current` (tokei Python code lines) per gated file and flags
near-limit files. If a file is near its limit, start a new module instead of
appending. The advisory never blocks; the length gate is the hard floor.

## SKILL.md core headroom

A `skills/public/**` or `skills/support/**` `SKILL.md` core (frontmatter and body
outside the exempt `## Load-Bearing Anchors` / `## References` /
`## Closeout Vocabulary` sections — exempt only up to each heading's budget in
[`scripts/gates_support/skill_core_density.py`](../scripts/gates_support/skill_core_density.py), with the
overflow charged back to the count) is governed
by two limits held in
[`check_skill_surface_preflight.py`](../scripts/gates/check_skill_surface_preflight.py):
`MAX_CORE_NONEMPTY_LINES` and `CORE_NONEMPTY_HEADROOM_BUFFER`. Authoring a core
to the ceiling (0 headroom) passes the hard limit but fails the headroom buffer.
Run the command below rather than recopying the numbers.

**The preflight's `core nonempty` is not the quality inventory's
`core_nonempty_lines`.** [skill_ergonomics_lib.py](../skills/public/quality/scripts/skill_ergonomics_lib.py)
keeps its own exemption walk — it must stay skill-local-portable, so it cannot
import the repo module — and that copy exempts only `## Load-Bearing Anchors` /
`## References`, without a budget, without an audit, and without fence awareness
(a literal `## References` inside a code fence still opens a real exempt block
there). The two numbers therefore
diverge on any skill carrying a `## Closeout Vocabulary` block or an over-budget
exempt section. Quote the **inventory's** number in a quality artifact:
[validate_quality_artifact.py](../scripts/gates/validate_quality_artifact.py)
recomputes it and hard-fails a mismatch.

The commit-boundary ratchet is in
[check_skill_surface_preflight.py](../scripts/gates/check_skill_surface_preflight.py).
On a block, separate a concept or delete one — never shave lines or stash overflow
into `references/` (P2).

```bash
python3 scripts/gates/check_skill_surface_preflight.py --path skills/public/<skill>/SKILL.md
```

## Artifact-shape preflight (charness-artifacts/**)

```bash
python3 scripts/gates/check_artifact_surface_preflight.py --type critique
python3 scripts/gates/check_artifact_surface_preflight.py --type critique --emit-stub
python3 scripts/gates/check_artifact_surface_preflight.py --path <artifact>
python3 scripts/gates/check_artifact_surface_preflight.py --type closeout-draft
```

The dispatcher reads required shape from the owning scaffold/validator; it never
re-declares it. Closeout grammar is
[`describe_closeout_draft_shape.py`](../skills/public/issue/scripts/describe_closeout_draft_shape.py).

## General doc surfaces (docs/*.md)

```bash
python3 scripts/gates/check_doc_authoring_preflight.py
python3 scripts/gates/check_doc_authoring_preflight.py --path docs/index.md
```

Omit `--path` to print the rules before a file exists; `--path` needs a real
file. It reuses the real markdown/link validators so the forecast cannot drift.
A class that could not run is `unforecast_classes`, never clean. It is an
affordance, not a gate. See [Documented commands](#documented-commands) for the
path-escape.

## Documented commands

A fenced or inline command naming a repo-owned script must name a script that
exists. Escapes: `<repo-root>/`, `<plugin-dir>/`, `<skill-dir>/`,
`<authoring-repo>/`, or any `<…>` placeholder in the path.

**Who evaluates this path?** The reader against their own tree →
`<repo-root>/` (unverifiable here). One decidable refusal:
[inventory_skill_script_references.py](../tools/inventory_skill_script_references.py)
refuses `<repo-root>/` naming a script that already lives in a skill package of
*this* tree. A sentence about what charness ships → `<authoring-repo>/`
(resolved here). A path the reader is told to **run** that only exists in the
authoring repo belongs in the skill package or behind `<plugin-dir>/`, never
`<authoring-repo>/`.

## Portable skill packages

Banned-pattern identity lives in
[validate_skill_ergonomics.py](../scripts/gates/validate_skill_ergonomics.py).
A `(#NNN)` comment that is fine in `scripts/` trips the package helper-comment
trap. Host specifics belong in adapters. No host intent means no edit-time
hook; `--scan-issue-anchors` and the commit sweep stay the backstop. One-shot:

```bash
python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
python3 scripts/gates/check_skill_surface_preflight.py --path skills/public/<skill>/SKILL.md --run-checks
python3 scripts/gates/check_skill_surface_preflight.py --scan-issue-anchors skills/public/<skill>/scripts/<file>.py
```

## Doc/SKILL prose and path pins

A `tests/` literal-string assertion that copies prose from a doc/SKILL.md, or
references one by path, breaks when you reword the prose or rename/delete the
file — and the broad pytest only surfaces it minutes later. Before paying for
that cycle, check which test pins your changed surfaces:

```bash
python3 scripts/gates/check_prose_pin.py --repo-root .
```

It reads the working-tree diff and reports the likely-broken pins (the test file,
line, and the pinned phrase or path). It is advisory by default (`--strict` exits
non-zero); run it directly when a prose edit needs this diagnostic.

### Pre-cut lossless + contract-safe check (skill-body cuts)

```bash
python3 -m tools.check_skill_cut_safety --repo-root .
python3 -m tools.check_skill_cut_safety --path skills/public/<skill>/SKILL.md
```

[check_skill_cut_safety.py](../tools/check_skill_cut_safety.py) reports BLOCK
(pinned phrase) vs REVIEW (no reference home). REVIEW is exit 0; `--strict`
fails it. It is a helper, not a new commit gate.

## Regex / string-matching edges

Prefer explicit containment over unbounded `.*`. Test a date that looks like a
version, a `v`-prefix, previous==target, and the absent token. Decide fail-open
vs fail-closed when the token is missing.
