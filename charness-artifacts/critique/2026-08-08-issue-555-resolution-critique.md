# Issue #555 resolution critique (delegated)

Classification: bug
Reviewer: delegated bounded reviewer (fresh-eye, read-only envelope: Read/Grep/Glob)
Fresh-eye context: `parent-delegated`
Envelope: bound as expected — no Bash, Edit, Write, or Agent tool exposed to this spawn
Verdict: RESOLVED WITH RESIDUAL RISK — three ledger/durable-record claims did not carry as
drafted (F1, F2, F3) and one shipped `required` choice is still the wrong shape (F4) -> records
restated, guard re-anchored, three issues filed, then closed

## Boundary Ownership

- Producer of the rule: `skills/public/issue/scripts/issue_backend.py` — `resolve_op` (binary
  derivation, `commands.<op>` lookup, `gh`-default fallback, allowlist/required validation,
  `part.format`), plus `op_is_declared` / `try_resolve_op` as the one policy fork.
- Consumers now routing through it: `issue_read.py`, `issue_create.py` (x2), `issue_close.py`
  (x3), `issue_verify_closeout.py`, `issue_runtime.py`, and
  `skills/public/handoff/scripts/chunked_routing_issue_backend.py`. Verified by an independent
  repo-wide grep for the binary-derivation expression rather than against the parent's list.
- Direction holds statically AND at runtime. `issue` is a genuine leaf: `issue_backend.py`
  imports only `re`/`shutil`/`subprocess`, so `handoff`'s file-path load cannot cycle back. No
  `issue` source references `handoff` in code.
- One consumer holds a NARROWER competing fact, disclosed: `plan_debug_run`-style
  `.is_file()`-versus-`.exists()` divergence does not apply here, but
  `chunked_routing_issue_backend` publishes `write_exists`-shaped facts from its own predicate
  elsewhere. Not this slice's subject.
- Adjacent, NOT in this repair: `skills/public/release/scripts/publish_release_helpers.py`
  `backend_command` is the same rule again over the `release_backend` key, and it has ALREADY
  drifted — `part.format(**subs) if subs and "{" in part` versus the owner's
  `if "{" in part` — so a brace-bearing template with no substitutions renders differently in
  the two. Different adapter key, different contractual owner. Filed as `#559`.
- Verdict: moved-to-owner — the private copies were moved into the module that already owned
  the rule, the pre-existing owner was kept rather than a new shared module invented, the
  `handoff` -> `issue` direction is the contractual one, and `issue` stays a leaf. The residual
  is not a second owner of the tracker rule; it is that the check meant to keep it that way was
  anchored on the wrong half of the rule (F5), and that the adjacent release-backend rule still
  has its own implementation.

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only fresh-eye, `.claude/agents/bounded-reviewer.md`)
- Requested spawn fields: agent_type=bounded-reviewer, model inherited, one-shot spawn with no
  host addressing/team name
- Host exposure state: requested_fields_sent
- Delivery state: findings-received
- Application state: applied as requested; envelope Read/Grep/Glob only and structurally unable
  to write or run `git`. Worktree+index integrity fingerprinted around this window with
  `skills/shared/scripts/reviewer_boundary_fingerprint.py` (window
  `issue555-resolution-critique`, verdict `clean`, no drift), as around both slice rounds
  (`slice3-555-round1` and `slice3-555-round2`, both parent-attributed with no unattributed
  drift).

## Fresh-Eye Satisfaction

parent-delegated — a separate bounded-reviewer context read the committed tree with no access
to the parent's reasoning or to either slice round's conversation. F1's arithmetic was
recomputed from the tree's own occurrence set by an independent grep, not from the parent's
count. F4 was derived by tracing `resolve_op`'s substitution handling into the consumer chain
rather than by re-checking a stated conclusion, and F5's live counterexample was found in a
root the guard already scanned. This is not a same-agent pass.

## JTBD

An agent picking up `docs/handoff.md` needs to know whether a backlog line's cited issue is
still live. `handoff` answers that through a tracker command it must build from an adapter
template; `issue` builds the same command to ACT on the tracker. Before `#555` the build rule
existed four times, and the one implementation that validated adapter templates was the one
nobody on the staleness path used — so a misconfigured adapter reached a verdict surface
unchecked, and any fix landed on one copy.

## Findings

### F1 (BLOCKER as drafted) — the siblings arithmetic over-counted removals, exactly as #548's did

The draft claimed "four implementations, three consolidated". The tree carries the owner plus
THREE private copies, of which TWO were removed; the owner was never consolidated — it was
already the owner, which was the sharper finding of the premise check. "Three consolidated" is
only true if the owner is counted as a consolidation of itself. This is verbatim the mismatch
that blocked `#548` one slice earlier.

REPAIRED: restated everywhere as four implementations, two private copies removed, one filed,
with attribution 2 named by the issue / 1 found by bounded review.

### F2 (BLOCKER as drafted) — the prevention artifact contradicted itself about the count

`tests/test_tracker_backend_single_owner.py`'s module docstring opened with "was implemented
THREE times" while the same file said "the FOURTH copy" forty lines later and carried a
`_KNOWN_UNCONSOLIDATED` entry for it. The first text a future session reads when asking why the
owner exists recorded a pre-fix world the same file refutes.

REPAIRED: the docstring now states four implementations and marks each site REMOVED or NOT
removed with the reason.

### F3 (BLOCKER as drafted) — a live comment and a live test message both instructed the round-2 regression

`_resolve_command` still carried "`required` is deliberately EMPTY, not `allowed`" after round 2
had made it a per-op parameter that is NOT empty for `view_state` — false at the point it was
written, and contradicting an explanation thirty lines above it. Worse, the guard test repeated
the refuted instruction as an assertion message ("handoff must pass an EMPTY required set"),
and its `"frozenset()"` substring matched `LIST_OPEN_REQUIRED` regardless of what
`VIEW_STATE_REQUIRED` became, so it pinned nothing about the choice its message was about.

REPAIRED: the comment now explains that both extremes were wrong and points at the two named
constants; the assertions pin each constant BY NAME with the reason for its value.

### F4 (residual, disclosed and filed, does not block) — `{number}` closed the loud half of the identity, `{repo}` remains

`(repo, number)` is an issue's identity. A `view_state` template omitting `{repo}` is accepted,
the caller's repo is silently dropped by `resolve_op` (it renders only what the template
spells), and against a repo-agnostic binary the answer is about another repository's issue #N.
The payload-number guard cannot catch it, because numbers collide across repositories. So the
manufactured-CLOSED verdict remains reachable through the other half of the identity.

Not a regression: the pre-`#555` copy validated nothing at all, so this is a capability the
consolidation narrowed without closing. The closeout may say `{number}` closed the loud path
and must NOT say the class is closed. Filed as `#558` with three candidate directions.

### F5 (prevention was anchored on the cheapest half of the rule)

The guard selected on binary derivation — the one line a re-grown copy most readily delegates —
while the parts that carry the verdict are the template lookup, the built-in default, the
undeclared-op policy, and the rendering. The live proof was in a root the guard already
scanned: `publish_release_helpers.backend_command` re-derives the whole rule and was invisible,
because it takes the binary from the template's first element. Further evasions found: a
hardcoded four-root tuple missing `skills/shared` and `skills/support`; an AGGREGATE floor
(`>= 100`) that `scripts/` alone satisfies, so deleting every skill root left it green; a
non-recursive `glob("*.py")`.

REPAIRED: two tells, the second being the RENDERING step (`part.format(`), which is the rule
itself; four roots including `skills/shared` and `skills/support`; a PER-ROOT floor, because an
aggregate floor cannot detect the loss of the roots it protects; recursive globbing; and tells
matched against comment-stripped source, because a tell that matches prose matched the comment
explaining the tell. A first attempt at the second tell used the bare undeclared-op condition
and false-positived on three modules that check it as a PRECONDITION and then correctly call the
owner — a tell that fires on correct code trains readers to widen the exemption list, which is
worse than no tell.

### F6 (the memo claim was broader than what shipped)

`_issue_backend_owner`'s docstring justified memoizing by the per-issue loader cost, while
`_default_runner` on the same per-issue path still exec'd `issue_runtime` per call, unmemoized —
and the memo test injected a runner, so it never observed that half.

REPAIRED: both loaders go through one memo helper, and the docstring says so. Related: the
residual about `_load_issue_module`'s dead `repo_root` parameter is SMALLER than stated — the
memo's cross-root safety does not depend on it, since candidates derive from `__file__` alone,
so it is a lying signature rather than a correctness risk.

## Q2 — is the behavioural verdict's channel genuinely distinct? Real, and narrower than it reads

Genuinely distinct and the strongest of this goal's three verdicts: a separate process, the
real `parse_handoff_entries.py --with-issues` CLI, a throwaway on-disk repo, a real
`.agents/issue-adapter.yaml` parsed by the real resolver, a DETACHED worktree as the execution
root, and — the part that matters — an oracle written by a NON-Python external executable. The
stub binary's argv log is produced outside the process under test, which is materially
different from unit tests that patch a `runner` callable inside the module. Unlike `#548`,
where both CLIs imported the owner and there was no independent oracle, the argv is observed
from the other side of `subprocess`.

What it does NOT establish, and the closeout says so:
1. It does not prove DELEGATION. An identical argv would appear if the removed copy were still
   in place. Delegation is proven by the structural guard and the unit tests; the behavioural
   channel proves the OUTCOME, not the ownership — which is `#555`'s actual subject.
2. The `view_state` argv is a template whose literal `--repo` flag takes the issue NUMBER as
   its value. No real tracker accepts that; the stub accepts anything. So the run proves the
   resolver ACCEPTS a `{repo}`-less template, not that such a template produces a usable
   command — and it is the same shape F4 says is unsafe.
3. `closed_issue_count: 1` came from a stub returning what it was told to return, so the CLOSED
   verdict is checked against the fixture's own belief rather than an externally established
   fact.
4. `search_newest_open`, the `issue`-side raising contract, and `gh` itself were not exercised
   through any CLI.

## Other residuals recorded, not repaired

- The owner's `part.format` raises raw `KeyError`/`ValueError` for a non-placeholder brace (a jq
  reshape, which this repo documents for this backend). `handoff` converts it to UNKNOWN;
  `issue`'s own callers see it raw.
- `skills/public/issue/references/issue-backend.md` documents neither `list_open`, `view_state`,
  nor `source_capture`, and no placeholder allowlist or required set anywhere — while the
  runtime now enforces an allowlist over them. `search_newest_open` requiring `{repo}` is a NEW
  runtime refusal this slice introduced, so an existing adapter template that omitted it worked
  before and raises now: a correct safety narrowing shipped as an undocumented adapter change.
- `issue_verify_closeout.py` reaches into `issue_close.py`'s private `_resolve_op` alias rather
  than the owner. Not duplication, so not `#555`'s subject; a coupling smell.

## Q7 — Verdict

RESOLVED WITH RESIDUAL RISK.

The fix is well shaped, and the premise check is again the best thing in the slice: refuting
the issue's own suggested remedy — because routing `handoff` through `issue`'s raising function
would have converted UNKNOWN into a crashed pickup through an `except`-less `main()` — and then
finding that the owner already existed and was the only validating implementation, is a better
outcome than the issue asked for. Two private copies of a verdict-bearing rule are gone, both
delegation sites gained placeholder validation they never had, the one genuine policy difference
is one extra entry point rather than a second implementation, and both refusal contracts are
pinned in both directions.

What failed as drafted was the ledger and the durable prose, for the third consecutive closeout
in this goal, always in the same place: F1 repeats `#548`'s arithmetic error exactly, F2 leaves
the prevention artifact contradicting itself, and F3 leaves two texts instructing the choice
round 2 proved manufactures a silent CLOSED verdict — the strongest of the three, because
`prevention` is claimed ON that test. All three are repaired above.

The residual to NAME, which does not block: `{number}` closed the loud half of the identity and
`{repo}` remains, so a wrong-repo CLOSED verdict is still reachable by reading. Pre-existing
rather than introduced, so the slice is a net narrowing. Filed as `#558`, alongside `#559` for
the fifth same-shape implementation and `#557` for the fourth copy.

Once the counts state population and removals separately, the guard file agrees with its own
exemption list, and the two texts instructing the empty `required` set are corrected, `#555` is
finished.

## Non-claims

No command was executed by this reviewer. `pytest`, `run-quality.sh`, the mutation-gate result
at `issue_runtime.py:159`, the dup-ratchet status, the reviewer-boundary fingerprints, and the
detached-worktree behavioural run with its argv log are taken as reported and are unproven by
this review, not disputed. `git show` was unavailable in this envelope, so every statement about
pre-fix code — including F4's non-regression finding and F6's "pre-existing" — rests on the
committed comments, which agree with each other. `#557`'s existence and scope were not verified
from inside the review. `plugins/**` mirror fidelity was spot-checked for two files and
otherwise assumed covered by the export-sync gate. No consumer repo was read. F1 is arithmetic
against the tree's own occurrence set; F2, F3 and the reference-doc gap are contradictions
between checked-in texts; F4, F5 and F6 are wrong-by-reading, traced through the consumer chain
rather than executed — in particular the wrong-repo `view_state` scenario was NOT reproduced
against a real repo-agnostic binary.
