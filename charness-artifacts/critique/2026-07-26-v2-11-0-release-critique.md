# v2.11.0 release: a minor bump that had to amend the previous release's own account
Date: 2026-07-26
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

Publishing `2.11.0` from `2.10.0` as a **minor** bump, carrying the runtime-profile
affinity slice: the widened `sched_getaffinity` catch, the derived-budgets mode
(`--suggest-budgets`), the sizing/enforcement split, and the measured 4-core
budget block.

## Failure Angles

One bounded read-only reviewer, on the release decision specifically: bump level
against the repo's own version policy, what an operator of the installed plugin is
owed, whether anything in the slice should be held back, whether the new mode's
flag rejection could break a caller, and whether repo-local budget numbers leak
into the exported plugin surface.

Parent-side worktree+index integrity was fingerprinted around the review
(`reviewer_boundary_fingerprint.py` snapshot/verify): `{"ok": true, "drift": []}`,
verified before any fix was applied.

## What The Review Changed

**The notes had to amend 2.10.0, not just announce 2.11.0.** This is the highest
finding and it is a repeat: the previous release's critique caught the same class
one release earlier. The 2.10.0 notes tell every installed operator that the
`OSError` crash is "Unreproduced, not yet fixed" and instruct them to "run the gate
once to see which id" on a `profile_config_errors` exit. This release fixes the
first and supersedes the second. Without an explicit amendment, the newest notes an
operator has read stay wrong, and someone pins 2.9.0 or works around a bug that no
longer exists. The notes now open with an `## Amends the 2.10.0 notes` section.

**A public name disappeared from an exported module, and the review made it
say so.** `SLACK_SUGGESTION_HEADROOM` was an attribute of `runtime_budget_lib` in
2.10.0 — confirmed against the tag, `git show v2.10.0:...runtime_budget_lib.py`
line 28 — and now lives only in the new sizing module. That is the one thing in the
diff with any major-bump smell. Verdict: still minor, because these are
path-loaded skill helpers rather than a published API and no consumer imports the
constant. But the version policy requires a debatable bump to state its reasoning,
so the relocation is now a named bullet in the notes rather than a silent break.

**The seam disagreed with itself on day one.** `runtime_budget_lib.evaluate`
already reports a machine token for the sample source (`runtime_signals` /
`command_timing_log` / `none`); the new sizing half returned display prose for the
identical fact (`"the repo-declared command_timing_log"`). A downstream caller
wanting to refuse a timing-log-derived block would have had to string-match a
sentence fragment written to sit inside a YAML comment. Sizing now returns the same
tokens through `COMMANDS_SOURCE_LABELS` and the renderer owns the prose, with a
test pinning that the raw token never reaches the operator-facing header.

**The slice's headline finding survived one hop downstream.** The whole point of
interpolating `--runtime-profile` into the blocking error was that
`--suggest-budgets` alone re-derives from the machine. But the *no-samples* message
one step later still said "run the gates once on this machine first" regardless of
the profile named — which files samples under the current machine's profile and
produces nothing for the profile the operator asked about. Exactly the
wrong-hardware confusion, in the message reached by the live aarch64 path. Fixed.

**Two documentation gaps.** The reference documented the new mode thoroughly and
never mentioned that combining it with `--json`/`--summary`/`--detail` is a usage
error; and my own slice critique claimed the mode "is advisory and exits 0" when it
exits **1** on no samples. That second one matters more than it looks: the previous
release's central finding was reconstructed from exactly this class of wrong
checked-in text. Both corrected.

**The baton reconcile was about to fire for a third consecutive release.**
`docs/handoff.md` claimed no version at 2.10.0 and the disposition has been carried
forward twice without being decided. Decided here: the handoff now carries a quoted
`"v2.11.0"` string, which the reconcile scan reads as a claim while the prose quotes
a string and points at the release artifact for current truth — satisfying the
baton contract without asserting a decaying fact.

## Counterweight Pass

- **Is the changed advisory number a breaking change?** No, and the reviewer's
  reasoning is right: `suggested_budget_ms` is a value inside a pre-existing
  advisory field, the advisory never affects an exit code, and the value only ever
  moves *up*, by at most 499ms. A caller pasting it gets a marginally looser bar,
  never a tighter one. Patch-grade repair riding along with an additive minor.
- **Could the new `--json` rejection break a caller?** No. It is reachable only via
  a flag that does not exist in 2.10.0 or earlier, so no pre-existing invocation
  can produce the new exit 2.
- **Do repo-local bars leak into the export?** No. Verified: no
  `plugins/charness/.agents/`, the exported consumer template still renders
  `runtime_budgets: {}` / `runtime_budget_profiles: {}`, and the only
  `local-linux-*` strings in the export tree are a doc example and a validator
  hint.
- **Should anything be held back?** No incomplete surface, no
  documented-but-unimplemented path. The reviewer confirmed every claim in the
  reference is implemented and exercised.
- The v2.9.0 "dead export" class does not recur: the new module is present in the
  plugin tree and every entrypoint that loads its importer has the scripts
  directory importable.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-07-26-v2.10.0-notes.md:71 | action: fix | note: 2.10.0 notes state the OSError crash is unfixed and give a superseded migration instruction; notes now amend both
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_sizing_lib.py COMMANDS_SOURCE_LABELS | action: fix | note: sizing returned prose for the fact enforcement reports as a token; unified with a token plus rendered label
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/check_runtime_budget.py no-samples message | action: fix | note: told the operator to run gates on THIS machine even when another profile was named
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/references/adapter-contract.md | action: document | note: the --json/--summary/--detail rejection was undocumented
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md | action: fix | note: non-claim said the mode "exits 0"; it exits 1 on no samples
- F6 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md | action: fix | note: baton carried RECONCILE REQUIRED for two releases; decided with a quoted version claim
- F7 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py:27 | action: document | note: SLACK_SUGGESTION_HEADROOM removed from an exported module; confirmed against v2.10.0 and stated in the notes as the one debatable point
- F8 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py suggested_budget_ms | action: defer | note: the advisory's changed number is not a breaking change; it only ever moves up and never gates an exit code

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` typed read-only subagent, release-decision scope.
- Requested spawn fields: `subagent_type: bounded-reviewer`, release-decision prompt, session-model inheritance (Claude-host branch of the per-host subagent contract).
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported `envelope-unbound` with only Read/Grep/Glob visible, and explicitly requested two `git show` commands it could not run itself.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded read-only reviewer in the shared parent worktree;
`reviewer_boundary_fingerprint.py` snapshot/verify returned
`{"ok": true, "drift": []}`, run before any fix was applied.

## Reviewed Input Identity

<!-- No prepared packet: the reviewer was given the committed release candidate (HEAD cfebe91f) with its changed surfaces enumerated in the prompt, plus the prior release's notes and critique as comparison material. -->

## Boundary Ownership

- Producer: this repo's release helper, which bumps the packaging manifest and the generated plugin/marketplace surfaces from one declared version.
- Consumer: an operator of the installed plugin, reading release notes to decide whether and how to upgrade.
- Owning surface: the release surface (`packaging/charness.json` plus generated mirrors) and the release-notes artifact; the version-policy judgment is the maintainer's, not the helper's.
- Verdict: owned-correctly

## Non-Claims

- **The bump is a judgment, not a computed fact.** No tool here decides minor vs
  patch; the reasoning is stated so it can be disagreed with.
- **`SLACK_SUGGESTION_HEADROOM`'s removal is unproven as harmless for external
  consumers.** No in-repo consumer imports it and it was never a documented API,
  but this repo cannot see a downstream that reached into the helper.
- **Public release verification is not claimed by this artifact.** It is owned by
  the publish helper's distinct-channel confirmation and the release record.
- **The sizing module has not been through a mutation run.**

## Next Move

Publish `2.11.0` through the repo-owned helper with this artifact as the critique
proof, then verify the public surface through a distinct channel before calling the
release complete.
