# Fresh-Eye Subagent Review

The canonical fresh-eye review path spawns bounded subagents. Before reporting
that path as blocked, confirm the host actually cannot provide them. Guessing
from priors is the exact failure mode this reference exists to stop.

Use this for bounded reviewer scopes owned by another skill, including
`critique`, `spec`, `quality`, `handoff`, and any skill that names a
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
`reviewer_tiers` in the critique adapter example at
`<repo-root>/skills/public/critique/adapter.example.yaml`; other skills cite this
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

Also record reviewer-tier evidence in the parent closeout artifact: requested
tier, requested spawn fields from the adapter, host exposure state
(`requested_fields_sent`, `metadata-hidden`, `host-defaulted`, or
`unsupported`), and `applied` only when the host confirms application. Sent
fields alone are not proof that the provider applied them.

Parent sessions that never spawned a fresh-eye reviewer cannot claim
`parent-delegated`. They must run the capability check below before calling the
canonical path blocked.

If `<repo-root>/AGENTS.md` contains a dedicated `Subagent Delegation` contract
that says repo-mandated bounded fresh-eye reviews are already delegated, treat
that as the explicit delegation request for those named bounded reviewer
scopes. Do not block merely because the live user message did not repeat the
word "subagent"; first try the host spawn tool under the repo contract. Only a
real tool refusal, missing spawn surface, exhausted host budget, or higher
priority instruction that forbids honoring repo delegation is a blocker.

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

## Shared-Tree Git Hygiene

Bounded fresh-eye reviewers usually run in the *parent session's* working tree,
not an isolated checkout. In that shared tree a reviewer that mutates git state
to "see the old behavior" silently corrupts the operator's pending commit: a
`git checkout <base> -- <path>` to read pre-change code leaves the parent index
holding a staged reversion, so the operator's closeout `git add -A && git commit`
re-commits the old code and undoes the very change under review — with every gate
still green, because the reverted code is internally self-consistent. This
staged-reversion trap is a hard rule, not a default.

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

Prose alone did not prevent recurrence: recorded shared-tree reviewer
violations include a reviewer that staged and committed content, one that
spawned an unauthorized child agent, and one that modified docs despite a
no-write brief. Two enforcement rails now back the rule instead of
instruction-following alone.

1. Parent-side integrity proof. Before spawning shared-tree reviewers, run
   `python3 "$SKILL_DIR/../../shared/scripts/reviewer_boundary_fingerprint.py" snapshot --repo-root <repo-root> --window-id <id>`.
   After EACH reviewer returns, run
   `python3 "$SKILL_DIR/../../shared/scripts/reviewer_boundary_fingerprint.py" verify --repo-root <repo-root> --window-id <id>`.
   Verify at the moment the reviewer returns, BEFORE applying anything the
   reviewer found: git records that the shared tree changed, never who changed
   it, so a parent that edits first gets drift on its own work shaped exactly
   like a boundary violation, and an unattributable `ok: false` teaches the
   parent to discount the one signal that would catch a real violation.
   A non-zero verify is a concrete, auditable violation signal: quarantine
   that review's approvals, restore state deliberately, and re-run verify to
   a full-clean result before re-snapshotting for the next reviewer (the
   drift list is fail-closed but names at least one drifted surface, not
   necessarily every one). Closeout evidence should cite the verify result,
   not reviewer self-report.
   The window id above is the first binding: verify refuses a snapshot from a
   different window (exit 2) instead of answering across two intervals.
   When the ideal order slips anyway, the parent declares what it changed
   itself rather than discounting the alarm. `--parent-path <path>` covers
   worktree content, `--parent-staged <path>` covers the index, and
   `--parent-head-moved` covers a parent commit; all are repeatable and take
   the exact repo-relative path git prints. Declared drift is reported as
   `parent_attributed_drift` and does not fail the verify; everything
   undeclared still does. Index drift needs its own `--parent-staged` —
   `--parent-path` never excuses it, because staging is the one class an
   enveloped reviewer cannot legitimately produce and is the staged-reversion
   trap above.
   A declaration is recorded parent testimony, not proof. It cannot pass as an
   undeclared clean run: an attributed pass exits **3**, not 0, and prints
   `verdict: parent-attributed` with the full `parent_declared` set. Cite
   `verdict` and that set in closeout evidence whenever anything was declared;
   a bare `{"ok": true, "drift": []}` quote is only honest for an exit-0 run.
   Drift that names no path is never attributable and always fails.
2. Host envelope. Hosts that expose typed subagent definitions spawn bounded
   reviewers under a read-only envelope (Claude Code receives the installed
   plugin's `agents/bounded-reviewer.md` (Read/Grep/Glob only), so
   that, where the envelope binds, writes, index mutation, and undelegated
   nested spawning fail with the host's concrete tool-unavailable signal. An
   enveloped reviewer has no shell, so prior-version content (`git show`) rides
   the parent's packet instead of a reviewer-run command. Reviewer-tier
   semantics stay intact because the tier maps to spawn fields, not tools.
   Envelope binding is a per-host claim that must be proven live, never
   assumed: a recorded host probe has seen a typed spawn accepted by name
   while the tool restriction did not bind (the reviewer still held shell
   and write tools). Until a live denial signal is recorded on the current
   host, treat rail 2 as unproven, rely on rail 1 plus the shared-tree rules
   above, and have parents audit reviewer tool-use events rather than trust
   self-report.

   Codex does not discover Claude's markdown envelope from a plugin root. On the
   current Codex host, use its native `explorer` agent with the bounded review
   packet; pass reviewer-tier spawn fields when the host exposes them. This is
   not the Claude tool envelope: its binding must be recorded separately, and
   the Claude envelope rail is `unsupported` on Codex. Keep the parent-side
   fingerprint rail as enforcement.

Rail 1 covers the git-state class: worktree writes, index mutation, HEAD
moves, and untracked churn on non-ignored paths. A reviewer action that
leaves no git trace — an unauthorized child that never writes — is prevented
only by rail 2. Two limits are by design: gitignored paths are out of
fingerprint scope (they cannot enter a closeout commit), and on hosts
without the envelope a writing reviewer could rewrite the default snapshot
file itself, so pass `--out` to keep the snapshot outside the
reviewer-reachable tree when that matters.

## Result Delivery

A spawned reviewer is not a received review. The parent holds the review only
when the reviewer's findings text is in the parent's own context. Spawn
acceptance, a clean rail-1 fingerprint, and an idle or completion notification
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

Delivery is a per-host live claim, proven by the step-1 probe below and never
assumed — the same standing as envelope binding in rail 2. The channel-selection
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

- Spawn one-shot subagents **without** a host addressing or team name. This
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
  other, and rail 1 proves only the first.

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

## Required Before Declaring The Canonical Path Blocked

1. Attempt the bounded setup the skill calls for.
   - Try to open one fresh-eye or critique subagent with a tight scope and
     time box. A single probe is enough; you are not required to spawn the full
     reviewer set just to prove availability.
   - The probe passes only when the reviewer's **findings text reaches you**.
     A spawn the host accepted but whose result never arrived is a failed
     probe, not a passed one; re-probe under the unnamed spawn shape from
     *Result Delivery* before reporting anything as blocked.
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

Stop and record the concrete host signal. Treat it as a host/runtime contract
gap for this run, not as permission to replace the review with a same-agent
local pass. Do not present a local pass as the canonical fresh-eye review, and
do not call a same-agent substitute "good enough" just because the probe
failed.

## Do Not

- Do not assume subagents are unavailable from model priors.
- Do not require recursive subagent spawning from an already delegated reviewer
  unless the parent task explicitly asks for nested delegation.
- Do not treat "I am uncertain if the host supports this" as a block; resolve
  the uncertainty first.
- Do not claim bounded subagents ran unless the runtime actually exposed and
  used a subagent/spawn tool. If the only observed tool is shell execution,
  report the canonical path as blocked by the missing spawn tool surface.
- Do not silently collapse into a same-agent review and call it the canonical
  path.
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
