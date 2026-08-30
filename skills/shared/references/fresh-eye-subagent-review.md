# Fresh-Eye Subagent Review

The canonical fresh-eye review path is a bounded, separate file-backed worker
selected by the adapter. `codex exec` and `claude -p` are valid worker backends;
typed subagents remain an optional host adapter. Before reporting a
task-completing result, consume the worker's typed receipt and delivery ledger,
proving that the returned findings reached the parent context. Guessing from a
file, exit code, or host prior is the exact failure mode this reference exists
to stop.

Use this for bounded reviewer scopes owned by another skill, including
`critique`, `spec`, `quality`, and any skill that names a
fresh-eye subagent review as its canonical path.

## Reviewer Tier

When a skill spawns a bounded fresh-eye reviewer, it declares a reviewer *tier*
that expresses leverage, never a provider model name:

- `high-leverage`: reasoning-heavy judgment — critique angles and counterweight,
  release / issue / quality closeout review, and deployment-confidence scans.
- `medium`: routine bounded checks where the caller needs a real fresh-eye
  read but does not need full deployment-confidence or issue-closeout depth.
- `standard`: simple bounded checks where the host's default reviewer model is
  enough.

Routine fresh-eye reviews should request `medium` when the host exposes a
medium-effort mapping. Use `high-leverage` only when the owning skill names a
review class that needs it, such as release, issue, or quality closeout, or
when the caller records a one-line reason that the narrow packet is still
high-risk. This keeps bounded reviewer packets from silently inheriting a
high-effort parent session just because a fresh context was needed.

The portable contract names only the tier. A host that exposes subagent model
overrides resolves the tier to concrete spawn fields (model, reasoning effort,
service tier); a host without that capability ignores the tier and spawns its
default reviewer. The tier is a request, never a hard requirement, so a host
that cannot honor it is not blocked for that reason.

Do not hardcode provider model names, reasoning-effort values, or service tiers
in skill prose or in this reference. The tier is host-plural: each host adapter
maps it to that host's strongest reviewer — for example a Codex host and a
Claude Code host resolve `high-leverage` to their own top reasoning model and
their own spawn fields — so the concrete values are host-specific and live in
the consuming skill's adapter, never here. The mapping is recorded once, under
`reviewer_tiers` in
`<plugin-dir>/skills/critique/adapter.example.yaml`; other skills cite this
policy and reuse the same tier names instead of repeating the mapping.

## Delegation Context

The caller that owns the review decides whether it needs fresh-eye subagents and
spawns them. Once a parent agent has delegated a bounded review task to a
subagent, that delegated subagent is already the fresh-eye reviewer for its
assigned lens. Critique angle and counterweight reviews are examples of bounded
review tasks; other skills may reuse the same parent-delegated rule for their
own fresh-eye reviewers.

Delegated reviewers should perform the assigned lens directly. They should not
try to spawn another subagent unless the parent explicitly requested recursive
delegation.

First branch for delegated reviewers:

- if your prompt says you are an angle reviewer, counterweight reviewer, or
  bounded fresh-eye reviewer, complete that lens directly
- do not run this capability check
- do not report `blocked` because nested subagent tools are unavailable
- return the requested findings or triage to the parent

Record the fresh-eye satisfaction context in the review result:

- `parent-delegated`: the parent spawned this reviewer, and the reviewer
  completed the assigned lens directly
- `nested-delegated`: the assigned task explicitly required recursive
  delegation, and that nested delegation ran
- `blocked <host-signal>`: required delegation could not run; include the
  concrete missing tool, host refusal, policy block, or exhausted budget
- `accepted-unreviewed-under-round-cap <cap-signal>`: the second bounded round
  repaired a verdict surface, and the operating cap intentionally accepts the
  repair without a third fresh-eye run. This is an explicit non-approval state;
  it must never be rendered or consumed as delegated approval.

Also record reviewer-tier evidence in the parent closeout artifact: requested
tier, requested spawn fields from the adapter, host exposure state
(`requested_fields_sent`, `metadata-hidden`, `host-defaulted`, or
`unsupported`), and `applied` only when the host confirms application. Sent
fields alone are not proof that the provider applied them.

Parent sessions that never spawned a fresh-eye reviewer cannot claim
`parent-delegated`. They must run the capability check below before calling the
canonical path blocked.

## Where The Delegation Request Comes From

A skill that MANDATES bounded fresh-eye review cannot also AUTHORIZE it. The
mandate says the review must happen; the authorization says who is allowed to
spend tokens spawning it, and that grant is the user's to give. Naming only one
place the grant may live is how this rule went inert: for repos that carry
`AGENTS.md` it fired, and in every repo that had never run `setup` the mandate
stood with no reachable source of authorization, refusing silently with no
failure, no log line, and no ticket.

Resolve the authorization as a ladder, **in this order**, and stop at the first
rung that answers:

1. **`<repo-root>/AGENTS.md` carries a dedicated `Subagent Delegation`
   contract** saying repo-mandated bounded fresh-eye reviews are already
   delegated. Legitimate because the repo owner checked that sentence in
   themselves. Delegate immediately for the named bounded reviewer scopes.
2. **Else `<repo-root>/.agents/subagent-delegation.json` records a decision.**
   Legitimate for the same reason as rung 1 — it is repo-owned state a human
   put there — and it is a STRUCTURED field rather than prose, so no wording,
   emphasis, or line wrap decides whether the rule fires. A recorded
   `granted` delegates; a recorded `declined` is honoured (see below).
3. **Else ask the user once.** Name the bounded reviewer scopes being
   requested and what they cost, and on an answer PERSIST it into rung 2 so the
   question is asked at most once per repo. Legitimate because the grant stays
   the user's explicit act.

Resolve the ladder with
`python3 "$SKILL_DIR/../../shared/scripts/resolve_subagent_delegation.py" resolve --repo-root <repo-root>`
rather than re-deriving it, and persist a rung-3 answer with the same script's
`record --decision granted|declined`. Anything the resolver cannot read as a
decision — a missing file, malformed JSON, an unrecognized value — resolves to
`ask`, never to `granted`. **A skill invocation is not a rung.** Invoking
`critique` or `quality` does not authorize the reviewers those skills mandate;
that would let the plugin grant itself spawn rights in every repo that installs
it, with no per-repo record of what was authorized.

A recorded `declined` is a real answer and is honoured: the review does not run
and is not re-asked on the next slice. Record it as

```text
Fresh-eye satisfaction: blocked delegation-declined — delegation signal: the user
declined the standing bounded-review delegation request, recorded in
.agents/subagent-delegation.json
```

`delegation signal:` is a distinct heading from `host signal:` / `tool signal:`
on purpose. A user's deliberate "no" is not a host incapacity, and writing it as
one would both require a false `host signal:` line to satisfy the authoring
floor and report a user decision as a machine limitation at an irreversible
public boundary. A decline is not a defect to route around and not grounds for a
same-agent substitute.

**Rung 2 is read even when rung 1 answers.** `setup` is the skill that WRITES
the `AGENTS.md` block, so `decline at rung 3, then run setup` is a sequence this
harness manufactures — and resolving rung 1 without looking would erase the only
"no" the user ever gave. A recorded `declined` under a present `AGENTS.md` block
is a CONFLICT: it resolves to `ask` naming both sources, never to `granted` and
never to a silently dropped refusal.

A grant may name a narrower scope set than the canonical five. Pass
`resolve --scope <name>` when you know which scope you are about to spawn for; a
grant that does not cover it resolves to `ask` rather than reading as `granted`
to a caller it never covered.

The record is repo-owned testimony, not proof of who answered — no file-based
mechanism can prove human authorship. What it buys is an auditable, diffable,
per-repo record: `resolve` surfaces the recorded provenance at the point of use,
and `record` refuses a `granted` with no `--note`. It is JSON rather than the
`.agents/*.yaml` adapter idiom because it is machine-written by the rung-3
persist step, not hand-maintained.

Do not block merely because the live user message did not repeat the word
"subagent"; once a rung answers `granted`, first try the host spawn tool under
that grant. Only a real tool refusal, missing spawn surface, exhausted host
budget, or higher priority instruction that forbids honoring the grant is a
blocker.

The ladder changes where AUTHORIZATION may come from. It does not loosen what
counts as PROOF that a review ran: a genuine tool refusal is still a blocker, a
spawn is still not a received review (*Result Delivery*), and a same-agent pass
is still forbidden.

## Distinct Named Lenses

When a caller spawns more than one bounded fresh-eye reviewer over the same
artifact, assign each reviewer a **distinct, explicitly-named lens** (for
example encoding/i18n, injection/escaping, portability, or one of the `quality`
Behavior lenses such as verification-channel fitness and guard-propagation
across seams) rather than N generic "review this change" reviewers. Name the
lens in the packet prose, never in the spawn's host addressing or team field —
that field selects a delivery channel, not a label (see *Result Delivery*).

A generic reviewer tends to inherit the author's framing blind spot. In the
incident that motivated this note, the generic reviewer caught a bracket/escaping
bug at the salient crossing but missed a sibling charset bug, because both author
and reviewer pattern-matched the same surface and read the same channel that
could not exhibit the failure. Named-lens diversity catches failure modes that
reviewer redundancy cannot — it is the "perspective-diverse verify" idea (give
each verifier a distinct lens, not N identical refuters) applied to review-lens
assignment. The lens names are a request like the reviewer tier, not a fixed
taxonomy: pick the hazard classes the diff actually crosses.

**Diversify the SOURCE, not only the hazard.** When a fan-out reviews a surface
the repo has designed before, assign at least one reviewer the question *what has
this repo already decided about this?* — pointed at the design record (specs,
goals, deferred decisions, prior issues), not at the code. Hazard-diverse lenses
all reading the same source share one blind spot: they can only find defects that
are visible in the implementation.

The incident behind this note: a parent spawned three reviewers over a subsystem,
gave each a distinct and well-chosen hazard lens, and briefed all three to read
`scripts/`, `skills/`, and `tests/`. They found real defects. None was asked what
the repo intended, so none opened the 73 checked-in artifacts specifying that
subsystem — including a completed contract whose *Deferred Decisions* section had
already ruled on the exact question the parent then paid an agent to redesign. The
parent's own audit greps had filtered the artifact directory out as noise, and a
spec path that did surface in one grep was classified as a past artifact and never
opened. Reviewer redundancy cannot catch that; a source axis can.

## Two Rounds For Verdict-Rendering Code

A slice that changes what a **proof surface** decides — a gate, validator, or any
code rendering a verdict about other code or artifacts — owes a SECOND bounded
round that reads the REPAIRED surface, because the repairs the first round drove
are themselves unreviewed. This is not caution: every measured slice of that class
in the authoring repo shipped a fix carrying the class it fixed, and the round that
read the repairs has caught blockers the first round structurally could not see
(it was reviewing code that no longer exists).

Round 2 reads the repaired surface, not the repair hunks — a hunk-only packet
cannot see a guard left dead, inverted, or bypassed elsewhere — and asks one
question: does this fix reproduce the class it fixes? A first round that produced
no repairs discharges the obligation; record that it found nothing rather than
spawning a reviewer over an unchanged tree. The cap is two rounds: round-2
repairs are recorded as accepted-unreviewed rather than triggering a third, a
deliberate stopping rule because the marginal round is worth less each time.

The trigger is what the surface decides, not that its file was touched. In the
authoring repo the full rule, the touched-vs-changed measurement behind that
scoping, and the producer-run ordering live in the authoring repo's operating contract
(Critique Discipline; authoring-repo-internal, not vendored with the skill). A
consuming repo that adopts this rule owns its own trigger definition.

## Shared-Tree Git Hygiene

Prefer an executable boundary. A host-enforced typed read-only reviewer may use
the parent worktree. An untyped or write-capable reviewer uses an isolated
checkout; if an untyped reviewer must share the parent, the fingerprint fallback
below detects git-state drift. In any shared tree, a reviewer that mutates git
state to "see the old behavior" can silently corrupt the operator's pending
commit: a `git checkout <base> -- <path>` can leave a staged reversion that a
later closeout recommits.

When you review in a shared worktree, treat git as read-only:

- Inspect any prior version through plumbing that does **not** touch the index or
  worktree: `git show <ref>:<path>`, `git diff <ref> -- <path>`, `git cat-file`.
- Do **not** run index- or worktree-mutating git commands in the shared tree:
  no `git checkout -- <path>`, `git checkout <ref> -- <path>`, `git restore`,
  `git stash`, or `git reset`, and do not `git add` files you touched only to
  inspect them. Each leaks your inspection into the operator's commit.
- If a check genuinely needs the old tree on disk, request an isolated worktree
  (`charness worktree create`) or a fresh clone; never roll the shared tree back
  under the parent session.
- Leave the index exactly as you found it. Report findings about prior behavior
  from the read-only diff, not by staging a reversion.

This section is the canonical owner of the rule; every skill that spawns
shared-tree reviewers inherits it by citing this section rather than restating
it. A deterministic pre-commit gate (`check_staged_reversion`) catches
the unambiguous phantom (`worktree == HEAD` but `index != HEAD`) as a backstop,
but the gate is rung 2: following this rule is what keeps the index clean in the
first place.

## Enforcement

Boundary evidence follows the execution mode; there is no universal
snapshot/verify ritual.

1. **Read-only worker:** record `boundary_mode: read-only-worker`. The
   Charness-owned file-backed worker launches with write and exec capability
   removed, so no parent fingerprint is needed. If that envelope cannot be
   proved, use isolation or the shared-tree fallback; do not assume it.
2. **Isolated worktree:** record the checkout's isolation. No parent fingerprint
   is needed because the reviewer cannot mutate the parent's index or worktree.
3. **Untyped reviewer sharing the parent:** run
   `python3 "$SKILL_DIR/../../shared/scripts/reviewer_boundary_fingerprint.py"
   snapshot --repo-root <repo-root> --window-id <id>` before launch and verify
   immediately after return, before applying findings. A failed verify
   quarantines the review's boundary approval. The helper detects git-state
   drift only; it does not prove fresh-eye independence or findings delivery.
   The snapshot receipt returns the exact verification path. Verify before
   applying findings; an undeclared drift quarantines the boundary approval.
   The window id binds the two calls. Parent-path declarations are only
   attribution, not proof, and are unnecessary when the parent has not written.

If none of these modes is proven, the returned text remains an independent
opinion/non-claim and cannot be used as boundary-clean closeout approval. A
missing fingerprint on a typed or isolated review is not a failure. Gitignored
runtime files remain outside this helper's scope because they cannot enter a
closeout commit.

## Result Delivery

The default worker path is the canonical consumer path. A worker run is
complete only when `reviewer_worker_report.py` returns a typed report with
`approval_eligible: true`; the report requires a succeeded worker receipt, a
fresh output hash, and a matching `findings-received` delivery-ledger attempt.
This keeps the report media-neutral: `codex_exec` and `claude_p` are adapter
choices, not verdict categories. The delivery CLI's `delivery_complete` field
is only a state-machine observation; it is intentionally not
`approval_eligible`. Only the combined worker report may emit that approval
field, after it joins the receipt, attempt, packet/input identities, and result
hash. The result itself must pass the canonical bounded-review result schema
and carry `verdict: pass`; a syntactically valid JSON file, a non-empty file, or
`findings-received` alone is not approval. The carrier also parses the canonical
delivery-attempt history and transition ledger, rather than trusting only the
final state/hash fields, and binds the packet repository as well as issue number.

For the optional typed-subagent path, **A spawned reviewer is not a received
review.** The parent holds the review only when the reviewer's findings text is in
the parent's own context. Spawn
acceptance, a clean boundary result, and an idle or completion notification
are each individually compatible with findings that never arrived — the
reviewer can run correctly, keep its boundary clean, write a complete final
message, and still deliver nothing the parent can read.

Some hosts deliver a reviewer's final message on more than one channel, and
there the **spawn call shape selects the channel**. A spawn that carries a host
addressing or team name is routed to a mailbox-style channel whose only
retrieval path is that host's message-sending tool; a parent to which the host
does not expose that tool never receives the findings at all. This is a
recorded failure, and it recurred because the correct spawn shape was known
only as a rolling retro lesson that decayed before it reached any contract —
which is why the rule lives here.

On at least one host this is a known, still-open upstream defect rather than
intended behavior: the name parameter silently switches the spawn onto a
teammate protocol, so completion emits an idle notification to a team inbox
instead of returning the result. Treat the unnamed-shape rule as a workaround
for a live host bug, not a permanent fact about spawning — when the upstream
defect closes, re-probe and the rule may relax to a preference. The invariant
above ("a spawned reviewer is not a received review") does not relax; it is what
makes the failure diagnosable at all.

Typed-subagent delivery is a per-host live claim, proven by the step-1 probe
below and never assumed — the same standing as envelope binding in rail 2. The channel-selection
differential above is recorded on one host at one version and corroborated by the
upstream report. The named arm has since been observed in a second session
(`n=2`); explicit background spawns and multi-reviewer concurrency remain
uninspected. The scope record, upstream lineage, and non-claims live in
`<repo-root>/charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md`
and its recurrence record
`<repo-root>/charness-artifacts/debug/2026-07-27-named-spawn-recurrence.md`.
On a host whose spawn surface exposes no addressing or team parameter, or where
the named shape is the delivering one, the unnamed-shape rule is a no-op and
only the "findings text in your context" test carries. The current Codex
`explorer` path is not inspected.

- If the adapter selects the optional typed-subagent path, spawn one-shot
  subagents **without** a host addressing or team name. This
  applies to EVERY spawn, not only bounded reviewers: the always-loaded contract in
  `<repo-root>/AGENTS.md` states the same rule for any spawn, because scoping the
  rule to review is what let it fail to bind at all. Reserve named spawns for agents the
  parent will address repeatedly, and only when the host exposes the matching
  retrieval tool in that same session.
- A tool named in host documentation is not a tool available in the session.
  Resolve it the way the host exposes tools before depending on it, the same
  way availability uncertainty is resolved below.
- Findings that never arrive are a **delivery failure to report**, never a
  reviewer that returned nothing and never grounds for a same-agent
  substitute. Re-spawn once under the unnamed shape before concluding
  anything about the host.
- Record delivery state in the closeout artifact next to the reviewer-tier
  evidence, as a field distinct from boundary state: `findings-received`, or
  `spawn-accepted-no-delivery <concrete channel or host signal>`. Boundary
  clean and findings received are independent claims; neither implies the
  other, and the selected boundary mode proves only the first.

Where a host persists subagent transcripts on disk, reading a stranded
reviewer's final message from its transcript is a legitimate **diagnostic** for
telling "reviewer produced nothing" apart from "delivery dropped it". It is not
the contract path: it is host-specific, it is not available on every host, and
a review recovered that way should be recorded with the delivery failure that
made it necessary.

Do that diagnostic with
`python3 "$SKILL_DIR/../../shared/scripts/reviewer_result.py" get --agent <name-or-id> --repo-root <repo-root>`
(`list` enumerates the session's reviewers) rather than improvising a transcript
reader. It returns only the final assistant text block under a size cap, with a
typed `found` / `partial` / `still-running` / `not-found` / `ambiguous` status,
and reports `layout-not-found` on a host whose transcript layout it cannot
resolve instead of guessing. Read it once: a `still-running` result is not an
invitation to poll, and using it at all still means recording a delivery
failure.

For the default Charness-owned worker, use the one runner that binds the
producer paths and run id into the parent-side ledger before launch, then
collects the typed result through the same contract. Do not assemble
`reviewer_delivery.py`, `reviewer_worker.py`, and `reviewer_worker_report.py`
as separate shell steps: that split can create a findings-received ledger with
no producer binding. Do not infer delivery from a non-empty output file,
process exit code, or worker receipt status alone. Require the generated report
to say `collection_ready: true`; a shipping approval additionally requires
`approval_eligible: true`:

The same runner exposes in-progress work as typed `spawn-accepted`, `running`,
or `partial` delivery states. A partial carrier is an identity-bound descriptor
of preserved bytes (`schema_version`, kind, path, size, and SHA-256), not a
review result. Timeout or interruption retains that descriptor while projecting
the terminal non-delivery signal, and late bytes cannot resurrect the attempt;
only `findings-received` with a terminal schema- and identity-checked result can
be approval-eligible.

```bash
python3 "$SKILL_DIR/../../shared/scripts/run_reviewer_worker.py" \
  --repo-root "$REPO_ROOT" \
  --prompt-file "$RUN_DIR/prompt.md" \
  --capability-file "$RUN_DIR/capability.json" \
  --attempt-id "$ATTEMPT_ID" \
  --scope "$SCOPE_ID" \
  --packet-identity "$PACKET_SHA256" \
  --reviewed-input-identity "$INPUT_IDENTITY_SHA256" \
  --parent-receipt-identity "$RECEIPT_ID" \
  --boundary-mode read-only-worker \
  --ledger-file "$RUN_DIR/delivery.json" \
  --output-file "$RUN_DIR/result.json" \
  --receipt-file "$RUN_DIR/receipt.json" \
  --report-file "$RUN_DIR/report.yaml" \
  --execution-mode file-backed-worker \
  --backend "$BACKEND" \
  --timeout-seconds 900 \
  --run-id "$ATTEMPT_ID"
```

The backend runner itself must publish a typed receipt and a schema-validated
fresh result before the parent calls the `findings` operation. It resolves every
relative prompt/schema/output/receipt/ledger/report path against the explicit
repository root and refuses paths outside that root; launch `cwd` is not an
identity boundary. The receipt must
carry the attempt, scope, packet/input, mode/backend, prompt/schema, and result
identities so a foreign run cannot be paired with the current ledger. A finite timeout,
absolute paths resolved before `cwd`, unique run artifacts, and a pre-existing
output refusal are part of that runner boundary; a result file's presence is
not a terminal success signal.

The launch capability envelope owns `capability_non_claims` and
`capability_non_claims_sha256`. A reviewer prompt must tell the worker to copy
those exact values; semantic limits such as “no live provider behavior was
tested” belong in the result's ordinary `non_claims` array. Do not invite the
worker to synthesize capability non-claims from semantic review limits: an
otherwise useful review then fails collection because it no longer matches the
launch envelope.

## Required Before Declaring The Canonical Path Blocked

0. Resolve the authorization ladder in *Where The Delegation Request Comes
   From* first. "No standing delegation request in this repo" is not a blocker
   until rung 3 has actually been asked; an unasked question is a step you
   skipped, not a host restriction. A recorded `declined` IS a legitimate stop,
   recorded as such and not re-asked.
1. Attempt the bounded setup the skill calls for.
   - Run one file-backed worker with a tight scope and time box. A single
     worker run is enough to prove the canonical path; do not spawn a typed
     reviewer merely to prove that the worker exists.
   - The worker probe passes only when `reviewer_worker_report.py` returns
     `approval_eligible: true`. A fresh output file, process exit code, or
     succeeded receipt without matching ledger findings is not a passed probe.
   - If the adapter explicitly selects typed-subagent, The probe passes only when the reviewer's findings text reaches you. A spawn the host
     accepted but whose result never arrived is a failed probe; re-probe under
     the unnamed shape from *Result Delivery* before reporting anything as blocked.
   - If you are already a bounded fresh-eye subagent spawned by a parent, do not
     run this probe again unless your assignment explicitly requires nested
     delegation. This includes assigned angle and counterweight reviewers.
   - Treat refusal-to-spawn, a concrete host error, or a missing agent-spawn
     tool as evidence. Prior belief is not evidence.
   - Availability means an actual host-exposed subagent/spawn tool or a real
     tool event from that tool. A shell-only runner, routing-only proof, or
     model self-report that subagents were "used" is not evidence that the
     canonical path ran.
2. Resolve availability uncertainty before assuming a cap.
   - If the host exposes an agent-count budget, a "maybe available" signal, or
     a tool surface you are unsure about, probe it first: read the relevant
     setting, inspect the tool surface, or ask the host.
   - A vague sense that agents "might be rate-limited" is not a cap. Unread
     documentation is not a cap.
3. Only then report the canonical path as blocked.
   - Cite the concrete signal: which tool was missing, what error the host
     returned, which operator instruction forbids subagents for this run, or
     which agent-count budget is already exhausted.
   - If the blocker is recorded in a durable artifact, write it as
     `host signal:` or `tool signal:` so validators can distinguish a real host
     block from the old "no explicit subagent request" misread.

## If The Canonical Path Is Blocked

Stop and record the concrete worker or host signal. Treat it as a host/runtime contract gap
for this run, not as permission to replace the review with a
same-context local pass. Do not present a local pass as the canonical fresh-eye
review, and do not call a same-context substitute "good enough" just because
the probe failed.

## Do Not

- Do not assume subagents are unavailable from model priors.
- Do not require recursive subagent spawning from an already delegated reviewer
  unless the parent task explicitly asks for nested delegation.
- Do not treat "I am uncertain if the host supports this" as a block; resolve
  the uncertainty first.
- Do not claim a typed subagent ran unless the runtime actually exposed and
  used a subagent/spawn tool. If the adapter selects the worker path, do not
  reinterpret its receipt as a subagent claim.
- Do not silently collapse into a same-agent review (a same-context local pass)
  and call it the canonical path; use the worker report or record the concrete
  worker block.
- Do not name the blocker as "canonical path unavailable" without the concrete
  signal that made it unavailable.
- Do not treat a spawn the host accepted, a clean boundary fingerprint, or an
  idle notification as proof that findings were received. Only findings text in
  your own context proves that.
- Where the host makes the name optional, do not attach a host addressing or
  team name to a one-shot bounded reviewer spawn unless the host exposes the
  matching retrieval tool in that same session; that selects a mailbox channel
  the parent may have no tool to read.
- Do not report "the user did not explicitly allow subagents" when repo
  `Subagent Delegation` instructions already delegated bounded fresh-eye review
  scopes.
- Do not treat a missing `AGENTS.md` delegation block as the end of the ladder.
  Rungs 2 and 3 exist precisely for that repo; skipping to `blocked` there is
  the inert-rule failure this section was rewritten to stop.
- Do not let a skill invocation stand in for a rung. Mandating a review is not
  authorizing it, and a self-grant leaves no per-repo record of what the user
  actually allowed.
