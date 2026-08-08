# Issue #536 Resolution Critique
Date: 2026-08-08

## Decision Under Review

Closing `#536` on the drift message built at `67beced4` and `1fa7fd75` — one
shared renderer in `tests/probe_drift_support.py` consumed by all three drift
sites, splitting CORPUS causes from RULE causes, naming the files to `git diff`,
and listing every surface a re-record must touch paired with the command that
regenerates it.

The build already had two bounded rounds. This critique is the third delegated
reviewer and the one the closeout floor requires before the close call; it then
took a FOURTH round, because its own repairs changed verdict logic on a proof
surface.

## Failure Angles

- **Claim fidelity.** Both build rounds failed the same way: the author asserted
  where a fact lived without opening the file, and each wrong location produced
  an instruction that would cause the harm it was written to prevent. Every
  location the message names is a claim to re-open.
- **The repair carrying the class it fixes.** The message tells a reader where to
  look; a repair to it is another set of where-to-look claims.
- **Pin adequacy over a message.** A substring pin cannot see an inversion, and a
  pin comparing a constant to itself cannot see a swap of contents.
- **Surface-list completeness.** The message's whole value is "these carry the
  same numbers". An omitted surface is a silent partial update.
- **Ledger over-claim.** Siblings whose "proof" is an assertion; a behaviour
  channel that is not actually distinct.

## Counterweight Pass

The angle that paid was claim fidelity, twice, and both times against MY OWN
repair rather than against the shipped build.

Round 1 (resolution critique) found four blockers. Two were omitted surfaces —
the marker probe's `_provenance.why` ends on the presence-only total while the
message framed `current_corpus` as *the* prose field, and the floor probe's
`_provenance.counterfactual_floor_20` transcribes a corpus-moving pair with no
regenerating command at all. Two were pin-adequacy holes it CONSTRUCTED: the
pairing pin compared `command == MARKER_RECURSIVE_COMMAND`, constant to constant,
so moving `--recursive` between the two constants kept all ten pins green while
telling the reader to paste recursive output over the top-level payload — round
2's exact harm, reachable through the pin written to stop it; and
`DISCRIMINATION_PATHS` could be gutted while a rule cause still named the deleted
file.

Round 2 read those repairs and found three more, the worst of which is the one
worth recording. I had repaired the `current_corpus` omission by asserting the
floor probe's `_provenance` "deliberately transcribes no figures at all". Three
of its keys quote counts. I had PRINTED those keys in the same session before
writing the sentence. That is the fixed class, shipped inside the fix for it, for
the third consecutive round on this issue.

The sharper round-2 finding is structural rather than factual: I paired the new
counterfactual surface with `run: <command>`, and the module's own contract says
a paired command's output REPLACES the surface. Executed, `--floor 20 --json`
emits a payload whose key set is IDENTICAL to the probe's top-level payload with
`floor` set to 20. A literal follow does not produce stale prose — it pins a
threshold the gate does not use, which is a rule change wearing a corpus change's
clothes, the single outcome the whole message exists to prevent. My repair for an
omitted surface had manufactured a worse instruction than the omission.

Over-worry, checked and dismissed: whether the surface list is now too long to
read. It is eight entries and each names a distinct file or key with its own
remedy; compressing it is what produced the "update D47 and the probe together"
message this replaces.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/probe/2026-08-01-inventory-marker-rule.json:1266 | action: fix | note: round 1 — `_provenance.why` ends "The current synchronized corpus measurement is 196", a corpus figure one key away from `current_corpus`, while the surface list framed `current_corpus` as the prose field; a literal follow left it stale
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json:5 | action: fix | note: round 1 — `_provenance.counterfactual_floor_20` quotes "10 citations / 46 label values", both corpus-dependent, and the bookkeeping entry listed only `date`, `repo_head_at_run`, `worktree` and the `synchronized_*` prose; it is a SECOND measurement needing `--floor 20`, verified to reproduce 10/46 exactly
- F3 | bin: act-before-ship | evidence: strong | ref: tests/test_probe_drift_message.py:145 | action: fix | note: round 1 — the pairing pin compared constant to constant and the existence pin only split out the script name (identical for both marker commands), so swapping `--recursive` between them kept every pin green while instructing a paste of recursive output over the top-level payload; now the FLAGS are pinned
- F4 | bin: act-before-ship | evidence: strong | ref: tests/test_probe_drift_message.py:198 | action: fix | note: round 1 — only `GATE_MODULE` and the corpus directory were pinned as members of `DISCRIMINATION_PATHS`, so deleting `scripts/measure_inventory_marker_rule.py` stayed green while a rule cause kept naming a marker predicate in it; version 2's failure, reachable through the list rather than the prose
- F5 | bin: act-before-ship | evidence: strong | ref: tests/probe_drift_support.py:84 | action: fix | note: round 2 — my F1 repair claimed the floor probe's `_provenance` transcribes no figures; `why`, `synchronized_after` and `counterfactual_floor_20` all quote counts, and the block's own "NOT transcribed here" is scoped to the HEADLINE pair only. Third consecutive round finding this class in this issue's own fix
- F6 | bin: act-before-ship | evidence: strong | ref: tests/probe_drift_support.py:90 | action: fix | note: round 2 — my F2 repair paired the counterfactual surface as `run:`, and the module contract says a paired command's output REPLACES the surface; executed, the `--floor 20` payload is key-identical to the probe payload with `floor: 20`, so a literal follow pins a threshold the gate does not use. Now unpaired, with an explicit do-not-paste and rewrite-by-hand instruction
- F7 | bin: act-before-ship | evidence: strong | ref: tests/test_probe_drift_message.py:125 | action: fix | note: round 2 — my F4 pin derived the file set with `"/" in token` plus an extension allowlist of `{py, json}`, so a bare filename, a markdown link, a trailing `:`/`)`, or a `.md`/`.yaml` threshold home went unmeasured while the pin reported green; the population is now asserted per-cause and by count
- F8 | bin: act-before-ship | evidence: moderate | ref: plugins/charness/scripts/validate_inventory_consumption.py:83 | action: fix | note: round 2 advisory taken as a fix — a NINTH surface, the exported mirror, carries the identical counterfactual pair; added with its sync command rather than as a hand edit, because hand-editing a generated mirror is separately blocked
- F9 | bin: act-before-ship | evidence: strong | ref: scripts/validate_inventory_consumption.py:172 | action: fix | note: round 2 advisory taken as a fix — the message said the second label-minimum transcription sits in "the residual helper's docstring"; it is in `_labelled_line_engages`, and `residual_chars`'s docstring carries no figure, so a reader following the pointer finds nothing and distrusts the list. The COUNT (`TWICE`) was correct; the LOCATION was not
- F10 | bin: act-before-ship | evidence: moderate | ref: tests/probe_drift_support.py:80 | action: fix | note: round 1 advisory taken as a fix — the D47 surface enumerated "the artifact count and the presence-only total" as if complete; D47 quotes roughly seventeen figures across shallow and recursive prose, so the subset read as the whole and invited exactly the partial update the entry warns about
- F11 | bin: act-before-ship | evidence: moderate | ref: tests/test_probe_drift_message.py:147 | action: fix | note: round 2 advisory taken as a fix — the new `_provenance.why` pin accepted any digit, which a date satisfies; the CLAIM is that it ENDS on the presence-only total, so that is what it asserts now
- F12 | bin: valid-but-defer | evidence: strong | ref: tests/quality_gates/test_measure_evidence_residual.py:103 | action: file-issue | note: a THIRD probe pins the INVARIANT (`min_residual >= floor`) rather than equality and has never needed a refresh — the difference between making a recurring tax cheaper and removing it. Already filed | follow-up: https://github.com/corca-ai/charness/issues/561
- F13 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/probe/2026-08-01-inventory-marker-rule.json | action: file-issue | note: the same mechanical-re-stamp reflex on a different proof surface, with an observed 0/5 true-positive rate; a proof-surface deletion touching ~35 `sha256` references, so it needs its own two rounds rather than this slice's tail | follow-up: https://github.com/corca-ai/charness/issues/562
- F14 | bin: over-worry | evidence: strong | ref: tests/test_probe_drift_message.py:59 | action: document | note: the absence pin matches the literal "git was unavailable", so a reworded reintroduction would pass; judged acceptable because the removed cause was refuted on its FACTS (it named a field and value no code produces), and any reworded version would fail the same factual check a reviewer applies
- F15 | bin: over-worry | evidence: moderate | ref: tests/test_probe_drift_message.py | action: document | note: feared the behaviour verdict was not a distinct channel; it is a distinct test file and a distinct set of assertions exercised by a constructed corpus write rather than by the pins, but it is the same TOOL (`pytest`) and the same render function, and the closeout says so rather than claiming more

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), two spawns — the resolution critique before the close call, then a second round reading that critique's repairs.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: both spawns returned findings inline and each reported the read-only envelope bound, with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

Per-host note: Claude Code host, so the repo's Codex-only `gpt-5.6-terra`/`medium`
request does not apply; typed `bounded-reviewer` agents were used instead.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers in distinct contexts, each
boundary-fingerprinted with `reviewer_boundary_fingerprint.py` snapshot/verify —
windows `w-20260808T052344Z-3740093` and `w-20260808T053129Z-3760763`, both
verifying `clean` with empty drift and empty parent-attributed drift. Each
boundary was verified the MOMENT the reviewer returned and BEFORE any repair, so
no repair is inside a window it could contaminate.

Round 2 is where this issue's record is made: four rounds have now read this
message, and every single one found the fix asserting a location without opening
it. The two rounds here found seven blockers between them, and none of the seven
was reachable by mutation — fourteen mutants were killed across both repair sets,
including the two inversions round 1 constructed, and the mutants were written
from what the code already met.

The cap is two rounds, so round 2's repairs (F5-F11 and the pins over them) are
recorded as accepted-unreviewed.

## Reviewed Input Identity

<!-- No packet consumed: this critique binds to the issue body, the working tree at review time, the two reviewer reports cited inline above, and the closeout draft the reviewers were handed. -->

## Boundary Ownership

- Producer: `scripts/measure_inventory_marker_rule.py` and `scripts/measure_inventory_consumption_floor.py`, whose payloads the probes record; `scripts/validate_inventory_consumption.py`, which owns every threshold a rule change moves.
- Consumer: the agent mid-slice reading a red assertion and deciding whether to re-record.
- Owning surface: `tests/probe_drift_support.py` for the message, `tests/test_probe_drift_message.py` for the claims it makes. The recurring-refresh TAX itself is `#561`'s and is not fixed here.
- Verdict: owned-correctly
