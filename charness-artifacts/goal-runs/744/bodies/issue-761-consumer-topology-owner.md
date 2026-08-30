## Situation

Submodule (gitlink) binding was added to the reviewed-input identity in
`dc77742f2` and its parents, because a submodule bump previously had NO valid
declaration in either substrate: committed-ref refused with `null-content-hash`
(`git show <ref>:<path>` cannot read a gitlink) and working-tree refused it as
"a directory; declare the individual files" — with no individual files to
declare, a gitlink being a commit id rather than a tree.

It now binds. But three consecutive fresh-eye rounds each found a further git
behaviour the previous repair had missed, in this one area:

1. reading field 2 from BOTH `ls-tree` (`<mode> <type> <object>`) and
   `ls-files -s` (`<mode> <object> <stage>`), so every working-tree submodule
   bound the STAGE NUMBER — the constant `0`;
2. binding the INDEX entry rather than the checked-out commit, so moving a
   submodule's HEAD without staging left a changed input verifying as `current`;
3. resolving the checked-out HEAD with `git -C <path> rev-parse HEAD`, which
   walks UPWARD, so an uninitialised submodule bound the SUPERPROJECT's HEAD.

## Observed problem

Each was repaired and each has a regression test. The concern is the pattern:
three rounds, three distinct git behaviours missed by the same author, in the
same small area. States not yet probed at all include a DIRTY submodule
(uncommitted changes inside it), NESTED submodules, a submodule whose gitlink is
recorded but whose directory is absent, and conflicted (stage >0) index entries.

## Impact

Low today for charness itself: this repo has no submodules, so the binding is
exercised only by fixtures. It matters for CONSUMER repos, which is the whole
reason the support exists.

## Expected behavior

A bounded probe over submodule states — dirty, nested, absent-directory,
conflicted-stage — establishing for each what the identity binds and whether a
change in that state stales a verdict. Repairs only where the probe shows a
verdict surviving a real input change.

## Non-claims

- No claim that the current implementation is wrong; the known axes are tested.
- No claim that the unprobed states are broken — that is what the probe is for.

AI-provenance: agent-authored from the 2026-08-30 declaration-intersection sweep,
at the operator's direction.

---

<!-- charness-work-item-key: issue-761-consumer-topology-owner -->
# Work Item #761 — Assign consumer topology to consumer agents

## Purpose and disposition

Close this issue as `not planned / superseded` with no implementation. Charness provides composable reviewed-input capabilities and typed results; the agent operating each consumer repository owns submodule-specific composition, policy, and proof.

## Acceptance and proof

The issue-owned closeout comment records this ownership decision, makes no new submodule correctness claim, adds no live probe or Git-topology test matrix, and introduces no Charness product restriction.

## Non-claims

No claim that nested, conflicted, dirty, absent, or non-HEAD submodule states are verified or unsupported.
