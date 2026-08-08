# Issue #558 Resolution Critique
Date: 2026-08-08

## Decision Under Review

Resolving `#558` by making `(repo, number)` an enforced identity at every surface
that reads one issue's state back — the handoff staleness reader, the closeout
verifier, and the post-close readback inside `close-with-comment` — with a
declared `repo_scoped: owner/repo` waiver for a genuinely repo-bound binary, and
an answer-side check for a backend that is told the repository and ignores it.

Two delegated bounded rounds ran before the close call. Both are recorded here.

## Failure Angles

- **The remedy the issue named being the wrong one.** `#558` offers three options
  and calls none obviously right; the cheapest is the one most likely to be taken.
- **A guard that cannot fire.** This goal family's own class: a check added where
  no input can reach it.
- **Breaking a working host.** `{repo}` was optional for a real reason.
- **A shared helper changing every caller.** The identity rule has more than one
  consumer, and they do not share a risk budget.
- **Wrong versus silent.** A parse that answers wrongly is worse than one that
  declines to answer, because silence is accepted and wrongness refuses.
- **Tests that cannot fail for the reason they claim.**

## Counterweight Pass

The premise check earned the slice's shape before a line was written, twice.

The issue's cheapest suggested direction — "verify the ANSWER's repository when
the payload carries one" — is INERT as a closure. The default `view_state`
template requested `--json number,state`, so the payload never carried a
repository, and on the vulnerable path (a custom template omitting `{repo}`)
nothing guarantees the host's payload carries one either. Building it alone would
have shipped a guard that cannot fire, inside the goal that repairs guards that
cannot fire. It is kept, but as layer 2 and only after widening the default args.

The second finding reshaped the work from an invention into a reconciliation: the
identity rule already had TWO owners disagreeing. The handoff reader required
`{number}` alone; the closeout verifier already required both halves. The correct
answer was in the tree, one skill over, on the more dangerous surface.

Over-worry, checked and dismissed: whether requiring `{repo}` is a wolf-crier.
It is not — the requirement fires only for a template that genuinely omits an
identity-bearing placeholder, the declared waiver covers the one legitimate case,
and the refusal names the missing placeholder rather than reporting a symptom.

What the counterweight did NOT protect against, and this is the honest part: five
of the five blockers below are in my own repairs, not in the analysis. The
angles above were the right angles and I still walked into four of them.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/resolve_adapter.py:184 | action: fix | note: round 1 — the escape hatch was INERT. `_parse_backend` returns a fixed key set, so `repo_scoped` never reached the runtime; the fix therefore hard-broke every genuinely repo-scoped host with no configuration able to restore it. The parser now parses it
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_issue_identity_is_repo_and_number.py:51 | action: fix | note: round 1 — every waiver test hand-built the backend dict and bypassed the parser, so the suite structurally could not see F1. A test that skips the parser cannot fail for a key the parser drops. All waiver tests now go through `_parse_backend` via a `parsed_backend()` helper
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_backend.py:154 | action: fix | note: round 1 — the waiver was subtracted GLOBALLY inside `resolve_op`, silently loosening the closeout verifier, which had required both halves absolutely. An irreversible boundary loosened in order to fix a reversible reader. `waivable` is now a per-call-site parameter defaulting to empty, so every pre-existing caller keeps the strictness it had
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/resolve_adapter.py:212 | action: fix | note: round 1 — a bare `repo_scoped: true` cannot say WHICH repository, and this skill routes to two targets (`upstream_target`/`local_target`), so an unqualified waiver drops the identity for the target the binary is not bound to. The value must now be `owner/repo`, and the waiver applies only when the asked-about repo matches
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_backend.py:48 | action: fix | note: round 2 — the owner-shape rule was applied to the `repository` STRING branch and not to the DICT branch, so `nameWithOwner: "charness"` returned a bare half-identity: a WRONG value, which refuses a correct closeout, in the shape a host-mediated backend most naturally emits. One `_qualified()` rule now governs every branch
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_close.py:164 | action: fix | note: round 2 — the CLOSE path's own post-close readback passed no `required` set at all and never read the `url` it was already fetching. That readback is the evidence an irreversible mutation landed, and it is the code that closed `#536` earlier in the same session. Both halves are checked there now, with no waiver offered
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_backend.py:131 | action: fix | note: round 2 — the waiver failed OPEN when `repo` was absent from the substitutions: the comparison was skipped rather than refused, so a future opt-in caller that passes no repo would be waived unconditionally. Fails closed now
- F8 | bin: act-before-ship | evidence: moderate | ref: skills/public/issue/scripts/resolve_adapter.py:190 | action: fix | note: round 2 — a malformed `repo_scoped` appended to `errors`, taking the whole adapter invalid and the entire issue lane red over one optional key, against this file's own recorded norm that consumer-authored mistakes WARN. It warns and ignores now, which is also the fail-closed direction: no declaration means no waiver. The same finding showed `count("/") != 1` left nested-namespace hosts unable to declare a scope at all
- F9 | bin: act-before-ship | evidence: moderate | ref: skills/public/issue/scripts/issue_backend.py:82 | action: fix | note: round 1 advisory taken as a fix — the URL parse matched the last four path segments positionally and returned `projects/1` for `/orgs/foo/projects/1/issues/2`: a wrong repository, which REFUSES a correct verdict. The path must now be exactly `owner/repo/issues/<n>` (or the REST `repos/owner/repo/issues/<n>`) after the host, and the docstring NAMES the two shapes it covers rather than implying it covers all of them
- F10 | bin: act-before-ship | evidence: moderate | ref: tests/test_issue_identity_is_repo_and_number.py:297 | action: fix | note: round 2 — the boundary test accepted any `RuntimeError` whose text contained `repo`, which the unknown-placeholder message also does (it renders the allowlist). It matches `missing required placeholders` now, and goes through the parser like its siblings
- F11 | bin: act-before-ship | evidence: moderate | ref: skills/public/issue/references/issue-backend.md:64 | action: fix | note: round 2 — the reference claimed the requirement is "enforced by the backend owner rather than per caller", which is false: `required=` is a caller argument, and the close-side `comment`/`close` calls pass none. Reworded to say the owner RENDERS it and each call site CHOOSES it, and to name the three surfaces that choose it
- F12 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/release_backend.py:19 | action: file-issue | note: surfaced by the duplicate ratchet hard-blocking on this slice — a second adapter-backend parser converged with `_parse_backend`. NOT consolidated: different adapter keys, different owning skills, and the release copy has already drifted from the issue owner on rendering, so unifying them changes at least one skill's observable refusals. Already filed | follow-up: https://github.com/corca-ai/charness/issues/559
- F13 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_backend.py:89 | action: document | note: feared the strict URL parse would refuse correct verdicts; it returns None for unusual shapes, and None is ACCEPTED as "the payload does not say". The residual cost is that layer 2 is genuinely inert for path-prefixed installs, which the docstring now states rather than glossing
- F14 | bin: over-worry | evidence: strong | ref: tests/test_tracker_backend_single_owner.py:267 | action: document | note: feared that retargeting two existing tests destroyed coverage. Round 1 checked and refuted it: the `{limit}` case they were really about is preserved through the public caller, the loud-refusal cases still pin, and the `{repo}` assertion they lost was pinning the defect itself

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), two spawns — a resolution critique on the implementation, then a second round reading that critique's repairs.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: both spawns returned findings inline and each reported the read-only envelope bound, with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

Per-host note: Claude Code host, so the repo's Codex-only `gpt-5.6-terra`/`medium`
request does not apply; typed `bounded-reviewer` agents were used instead.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers in distinct contexts, each
boundary-fingerprinted with `reviewer_boundary_fingerprint.py` snapshot/verify —
windows `w-20260808T060155Z-3826448` and `w-20260808T060806Z-3838410`, both
verifying `clean` with empty drift and empty parent-attributed drift, and both
verified the MOMENT the reviewer returned, before any repair.

The measured result is the finding worth carrying: five blockers, and all five
were in REPAIRS rather than in the original analysis. Round 1's three were in the
build; round 2's two were inside round 1's repairs, and one of them (the
post-close readback) was a surface the build had never touched at all — found
only because round 2 was asked whether the repair's own claims were true of every
caller they named.

None of the five was mutation-findable. Nineteen mutants were killed across the
build and both repair sets, including two inversions, and every one was written
from what the code already met.

The cap is two rounds, so round 2's repairs (F5-F11 and the pins over them) are
recorded as accepted-unreviewed.

## Reviewed Input Identity

<!-- No packet consumed: this critique binds to the issue body, the working tree at review time, the two reviewer reports cited inline above, and the constructed reproductions executed before and after each repair. -->

## Boundary Ownership

- Producer: `skills/public/issue/scripts/resolve_adapter.py::_parse_backend`, the sole path by which a real caller obtains a backend dict, and `issue_backend.resolve_op`, which renders a template into argv.
- Consumer: three surfaces that read one issue's state back — `chunked_routing_issue_backend.issue_state` (a staleness reader), `issue_verify_closeout._view_issue_state`, and `issue_close.close_with_comment`'s post-close readback.
- Owning surface: `skills/public/issue/scripts/issue_backend.py` for the identity rule and its parse; each call site for whether it can afford the declared waiver. The `release_backend` parser convergence is `#559`'s and is not fixed here.
- Verdict: owned-correctly
