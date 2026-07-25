# Documented-command resolution gate
Date: 2026-07-25

## Decision Under Review

Closing the handoff's proxy-assertion follow-up by extending
[check_doc_links.py](../../scripts/check_doc_links.py) to resolve the repo-owned
script a documented command names, extracting the shared fence/HTML-comment walk
into [markdown_doc_scan.py](../../scripts/markdown_doc_scan.py), and binding four
literal-substring drift guards in
[test_authoring_preflight_reference.py](../../tests/test_authoring_preflight_reference.py)
to the affordances they name.

The motivating measurement: all six tests in that file passed while
`scripts/check_prose_pin.py` was deleted from the repo. They proved the doc
*says* a name, not that the named affordance exists — the retro's
"check named for a property that only asserts a proxy for it" shape.

## Failure Angles

- False negatives: which real documented-command shapes does the matcher miss,
  leaving the motivating rot class open under a different syntax?
- Over-firing on portable skill packages that legitimately name a *consuming*
  repo's command, and whether the stated escape is reachable before failure.
- Local-vs-CI divergence: a filesystem `.exists()` inside a gate whose every
  sibling check honors `--require-git-file-listing`.
- Whether routing a third call site through the extracted walk changed the
  behavior of the two gates that already used it.
- Whether the new tests assert the property or install a fresh proxy.

## Counterweight Pass

The reviewer graded down as often as up and separated live from latent
explicitly. It confirmed the `<!-- reproduction-source -->` marker semantics
survive the extraction intact by tracing the raw-`lines[lineno]` continuation
read, and said plainly that it found no regression there — the angle the parent
was most worried about. It classified five near-miss regex shapes (`../`,
interpreter flags, quoted paths, backslash continuations, bare `scripts/x.sh`)
as latent with no live instance, rather than inflating them into blockers.

The parent's own framing was refuted twice, and both refutations changed the
code. First, the header comment claiming fences were "the one syntax where a
rename can rot unseen" was false: the backtick checker waves through any span
containing whitespace, so an inline command with a flag was equally invisible —
with seven live sites. Second, the parent's fail-open concern was real but
mis-specified: untracked files *are* in the git listing, so the actual divergence
is gitignored targets. The test was rewritten around that, and it fails without
the fix.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_doc_links.py | action: fix | note: an inline `python3 scripts/x.py --flag` rots exactly as invisibly as the fenced form because the backtick checker skips any span containing whitespace; seven live sites were unprotected, so the check now scans inline spans as well as fenced lines and the false header comment was corrected
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/markdown_doc_scan.py | action: fix | note: the comment branches ran before the fence branch and were not gated on in_fence, so an unterminated `<!--` inside a fenced block swallowed the closing delimiter and left the rest of the document falsely marked fenced; the comment-open branch is now gated on `not in_fence` and the fenced-literal case is pinned by a test
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_doc_links.py | action: fix | note: resolving by filesystem `.exists()` while every sibling check honors `--require-git-file-listing` is a fail-open at the commit gate — a gitignored target passes locally and fails on the CI checkout; the resolution now threads the same `known_repo_paths` listing the rest of the gate uses
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/markdown_doc_scan.py | action: fix | note: dropping a whole line that merely starts with `<!--` discarded live content rendered after the `-->`, so a real citation of a gitignored target went silently clean; the line is now dropped only when removing its comment spans leaves nothing, and is still yielded verbatim so the reproduction-source marker survives
- F5 | bin: act-before-ship | evidence: moderate | ref: scripts/check_doc_authoring_preflight.py | action: fix | note: the new finding kind fell through to the generic branch and rendered as a bare path with no line number and no reason, which is the worst possible output for a tool whose entire purpose is author-time discoverability; it now renders the line, the reason, and the escape — and immediately caught a wrong example in this slice's own doc edit
- F6 | bin: bundle-anyway | evidence: moderate | ref: docs/conventions/authoring-preflight.md | action: document | note: the escape was documented only inside the `docs/*.md` section while the authors most likely to hit over-firing are portable-skill authors reading two other sections; promoted to its own section, and the undocumented `<…>`-anywhere escape is now stated rather than left as folklore
- F7 | bin: bundle-anyway | evidence: strong | ref: scripts/check_doc_links.py | action: fix | note: a dead `startswith("./")` branch and two dead `FENCE_RE` re-exports survived the extraction; removed, since a dead branch is the signal that a path was reasoned about and never tested
- F8 | bin: valid-but-defer | evidence: strong | ref: tests/test_authoring_preflight_reference.py | action: defer | note: the documented *flags* are still asserted as substrings, so dropping `--run-checks` from its owning script leaves the guard green while the documented command exits 2 — the same proxy class one level down; deferred because closing it needs an argparse-introspection contract rather than another literal, and the deferral is recorded in the handoff rather than guessed at here
- F9 | bin: over-worry | evidence: weak | ref: scripts/check_doc_links.py | action: defer | note: `../`-relative targets, interpreter flags, quoted paths, backslash continuations, bare `scripts/x.sh` invocations, and script-path arguments all miss the matcher; the reviewer verified none has a live instance in the gated surfaces, so widening the regex now would be speculative surface for zero current coverage
- F10 | bin: over-worry | evidence: weak | ref: scripts/markdown_doc_scan.py | action: defer | note: each doc is now read once per walk rather than once per gate; irrelevant at 585 files and the standing pytest wall time did not move, so a text-accepting overload is not worth the API surface yet

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (correctness of a new blocking gate plus a behavior change to an adjacent gate).
- Requested spawn fields: none sent — per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls (`bounded-reviewer`) with session-model inheritance, and no host addressing `name` was passed.
- Host exposure state: host-defaulted
- Application state: reviewer ran on the session-inherited model; no host tier-application signal exposed.
<!-- allowed Delivery state: findings-received | findings-recovered-from-transcript | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — the reviewer returned its findings inline under the unnamed spawn shape.

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer spawned as `bounded-reviewer` with no
host addressing `name`; it returned findings inline and self-reported the
read-only envelope bound (Read/Grep/Glob only). Rail-1 boundary snapshot was
taken before the spawn and verified `{"ok": true, "drift": []}` the moment it
returned, before any fix was applied.

Non-claim: the reviewer could not run `git show HEAD:<path>` inside its envelope,
so its angle-D conclusion (the extraction changed nothing beyond the
single-line-comment rule) is inferred from the current tree rather than diffed
against HEAD. The parent read both HEAD implementations directly earlier in the
session and confirms the ordering and fence anchor matched; that confirmation is
same-agent, not fresh-eye, and is recorded as such.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the doc author writing a command example, and the structural walk that decides whether a line is prose, fenced, or commented.
- Consumer: an operator copying a documented command, and the three gates that classify doc lines.
- Owning surface: `scripts/markdown_doc_scan.py` owns the structural walk; `scripts/check_doc_links.py` owns whether a named repo path resolves; `scripts/check_doc_authoring_preflight.py` owns telling the author before the gate does.
- Verdict: owned-correctly — "what is a live doc line" and "does this path resolve" are genuinely different properties, and the extraction gave the first one a single home shared by both gates instead of three drifted copies with an inconsistent comment rule.
