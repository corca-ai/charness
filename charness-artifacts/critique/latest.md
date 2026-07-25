# Documented-command flag gate
Date: 2026-07-26

## Decision Under Review

Adding a new blocking gate,
[check_documented_command_flags.py](../../scripts/check_documented_command_flags.py),
that asserts a flag documented beside a repo-owned script is a flag that
script's argparse actually accepts — by probing `<script> [subcommands] --help`
and reading the accepted option names out of the render. Plus the two live doc
defects it found, the shared emit helper
[gate_report_emit.py](../../scripts/gate_report_emit.py) the dup ratchet forced
out of it, and its timing verdict in
[validator-timing-layers.md](../../docs/conventions/validator-timing-layers.md).

This closes F8 of the
[2026-07-25 documented-command-resolution critique](./2026-07-25-documented-command-resolution-gate.md),
which shipped the rung below it (does the named script exist) and recorded the
flag rung as `valid-but-defer` because closing it needed an argparse contract
rather than another literal.

The motivating measurement, taken before any code was written: deleting the one
`add_argument("--run-checks", ...)` line from `check_skill_surface_preflight.py`
left `check_command_docs`, `check_doc_authoring_preflight`, `check_doc_links`,
`test_authoring_preflight_reference.py` (6 passed) and
`test_skill_surface_preflight.py` (25 passed) all green, while the documented
command exited 2.

## Failure Angles

- False green: which documented flag the named script rejects still passes —
  the direction that matters, since silence is this gate's whole failure mode.
- False red: which correctly-documented flag gets a blocking verdict.
- Coverage over-claim: what the pass line implies versus what was proven.
- Scope: does this duplicate or contradict what `check_doc_links.py` owns.
- Cost and timing layer: a ~180-subprocess gate on the commit path.

## Counterweight Pass

The reviewer graded down as often as up and separated live from latent
explicitly, which is what made its output usable. It cleared three angles by
tracing rather than by assertion: it walked the `HelpProbe` priming rounds and
proved no `KeyError` is reachable (the `.get`-returns-empty-set contract makes
each round descend exactly one level, so every prefix was primed by an earlier
round); it confirmed `COLUMNS=200` is honored through `shutil.get_terminal_size`
and that argparse never splits inside an action invocation; and it found no
duplication with `check_doc_links.py`, correctly identifying the boundary defect
as a *gap* rather than an overlap.

It classified `--flag=value`, `#`-comment collisions, cross-fence continuation
joins, the `shlex` dangling-backslash crash, subparser-flag-ordering, and a
flag-value/subcommand-name collision as latent with no live instance, rather
than inflating them into blockers — and enumerated all 17 subcommand names and
every documented flag value to prove the last one had no collision today.

Every live finding was reproduced before it was fixed. FG-1 was measured across
the whole probe set, not argued: 177 of 177 surfaces carried help-column-only
flags, and five were genuine contaminants that made a rejecting parser look
accepting (`--cached`, `--run-checks`, `--body-file`, `--min-confidence`,
`--mutation-coverage-command`). FG-4's fix then failed on first attempt for a
reason neither the parent nor the reviewer predicted — the generated
`plugins/charness/scripts/` mirror duplicates every canonical script, so a
repo-wide basename-uniqueness index resolved *zero* of the 40 bare invocations.
That measurement, not the plan, produced `build_canonical_basename_index`.

The parent's own framing was refuted twice by the run itself. The first draft
scanned the named file's argparse source statically; measuring it produced 34
false missing flags, because this repo builds `--repo-root`/`--summary`/
`--detail` through shared parser helpers — that is why the gate execs `--help`.
And the first `render_report` claimed "Validated N invocations" with no
uncovered-surface line at all; the repo's own attention-state validator caught
it as an undeclared silent skip, and the honest fix was to print the skipped
count and reasons on the pass path rather than declare the silence.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_documented_command_flags.py | action: fix | note: the accepted-flag set was `FLAG_RE.findall` over the whole `--help` render, so `description=__doc__`, `epilog` and every `help=` string fed it; measured across all 177 probed surfaces, five parsers accepted a flag they reject (`--cached`, `--run-checks`, `--body-file`, `--min-confidence`, `--mutation-coverage-command`) — a false green in the gate's own dangerous direction. `accepted_options` now reads only argparse's two structural homes: the `usage:` block and the invocation column of each option row, cut at the two-space help gap
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_documented_command_flags.py | action: fix | note: the prefix-free `issue_tool.py verify-closeout --expect-state CLOSED` form was matched by neither this gate's regex nor `check_doc_links`' `COMMAND_TARGET_RE`, leaving it unowned by both while the scope note claimed the two partitioned the surface; 6 live sites in the `issue` skill alone. Now matched and resolved through `build_canonical_basename_index` — which the repo-wide index could not do, because the `plugins/` mirror makes every basename non-unique. Coverage 212 -> 249 invocations
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_documented_command_flags.py | action: fix | note: `[--converted ...]` optional-brackets and `--engine=tokei` inline values failed `FLAG_RE.fullmatch` and were dropped — and worse than a miss, their invocation still counted as validated and never reached the skipped tail, so the run over-claimed coverage exactly where the tail was supposed to prevent it; `normalize_argument_token` strips the notation
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/check_documented_command_flags.py | action: fix | note: one carrier naming two commands (`verify: python3 a.py --x, python3 b.py --y`) handed the second's flags to the first, because `,` is not a shell operator to cut on — a blocking false red on a correct doc. The tail is now bounded by the next invocation match. Live in retro packets, which this gate does not scan; latent in-scope
- F5 | bin: act-before-ship | evidence: moderate | ref: scripts/check_documented_command_flags.py | action: fix | note: `shlex.split` raises on a dangling backslash as well as an unclosed quote, and only the latter had a repair, so a doc typo would exit the blocking gate with a stack trace instead of a finding; the fallback chain now ends at a plain split. Bundled with `comments=True` so a trailing `# ...` note beside a fenced command stops becoming arguments (live carriers in authoring-preflight.md), and with a consecutive-line guard so a dangling `\` at the end of one fenced block cannot swallow the next block's first line
- F6 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/dup-review.json | action: document | note: the dup ratchet hard-armed on three new families; the real shared behavior (stream selection plus `--json` vs text) was extracted to `gate_report_emit.py` and adopted by `check_command_docs.py` too, and an unused `ValidationError` class plus its dead `try/except` were deleted. The two residual families are the per-script argparse declaration convention across seven validators and a findings-list renderer whose second member ships inside the portable quality skill package — classified `intentional` with those reasons rather than extracted, since a common `main()` would take each gate's own flags as data and every script would still spell the same list out through an indirection
- F7 | bin: valid-but-defer | evidence: strong | ref: scripts/check_documented_command_flags.py | action: defer | note: the accepted set is unioned across the whole resolved subcommand path, but argparse is not symmetric — a subparser option placed BEFORE its subcommand is rejected, and this gate would pass it. Structurally it cannot catch flag/subcommand ordering drift, the second most likely way these commands rot. Deferred because the fix needs per-token positions threaded through `split_arguments`, and the reviewer verified both live sites use the correct order; recorded in the handoff
- F8 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_documented_command_flags.py | action: defer | note: `resolve_subcommands` picks the first bare word present in the choices set regardless of position, so a flag VALUE equal to a subcommand name mis-routes the probe into the wrong parser and reports its siblings missing — a blocking false red. The reviewer enumerated all 17 subcommand names against every in-scope documented flag value and found no collision, so it is latent; it becomes live the day a `resolve` or `record` subcommand is added. Recorded in the handoff
- F9 | bin: over-worry | evidence: weak | ref: scripts/check_documented_command_flags.py | action: defer | note: `CHOICES_RE` accepts only `[a-z0-9-]`, so one subcommand named with an underscore or a capital would make the whole `{...}` group unmatched and every sibling unresolvable; all 17 subcommands in the repo are lowercase-hyphen, and widening it now trades a real false-red risk (brace tokens that are not choice groups) for zero current coverage
- F10 | bin: over-worry | evidence: weak | ref: scripts/check_documented_command_flags.py | action: defer | note: short options (`-x`) are never checked, and the gate does not scan `charness-artifacts/**` or `plugins/**`; both are deliberate scope, the first because this repo documents long flags and the second because those trees are generated mirrors of surfaces already scanned

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (correctness of a new blocking gate whose failure mode is silence).
- Requested spawn fields: per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls; spawned as `bounded-reviewer` with an explicit `model: opus` override and no host addressing `name`.
- Host exposure state: host-defaulted
- Application state: reviewer ran under the requested typed agent; no host tier-application signal exposed beyond the accepted spawn.
<!-- allowed Delivery state: findings-received | findings-recovered-from-transcript | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — the reviewer returned its findings inline.

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer spawned as `bounded-reviewer`
(Read/Grep/Glob only, no write/exec/spawn by envelope). Rail-1 boundary snapshot
was taken before the spawn and verified `{"ok": true, "drift": []}` the moment it
returned, **before** any fix was applied — the ordering the 2026-07-25 retro
recorded as a repeat trap.

Non-claim: the review covered the gate's correctness angle only. The dup-ratchet
classification (F6), the timing-layer verdict, and the two doc fixes the gate
itself found were not fresh-eye reviewed; they rest on deterministic gates plus
the parent's own reasoning, which is same-agent and recorded as such. F7 and F8
ship unfixed and unproven by construction — they are latent-only on today's
tree, not shown to be unreachable.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the doc author writing a command example, and the script author editing that command's argparse.
- Consumer: an operator or agent copying a documented command, and the gates that classify doc commands.
- Owning surface: `check_doc_links.py` owns whether a documented command names a script that resolves; `check_documented_command_flags.py` owns whether the arguments documented with it parse; `gate_report_emit.py` owns how a findings gate emits.
- Verdict: owned-correctly — "the named path resolves" and "the documented invocation parses" are different properties with different fixes, and the new gate cedes unresolvable paths and flagless invocations to the existing owner rather than reporting them twice with different wording. The one place they had drifted apart was a shared blind spot (the prefix-free form, F2), which is now covered on this side and counted, not silently dropped.
