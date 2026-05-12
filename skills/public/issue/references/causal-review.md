# Causal Review and Resolution Critique

`issue resolve` runs two reviewer-driven passes that the smallest-fix design
loop alone keeps missing: a **causal review** before design (step 4) and a
**resolution critique** before close (step 9). Both use bounded fresh-eye
subagents so the analysis is not anchored on the implementer's first hypothesis.

## Classification gate

Only `bug`-class issues require the full causal review. Other classes use a
lighter pass:

- `bug`: full three-lens causal review (root cause, detection gap, sibling
  search), then resolution critique
- `feature`: skip causal review, run resolution critique on the design only
- `question`: usually no implementation, no review pass; respond and close
- `decision-needed`: discuss with the user before either review pass; the
  decision often reshapes what `bug` vs `feature` even means
- `deferred-work`: existing issue body should already capture context; treat
  like `feature` once the deferral reason is no longer blocking

When unsure between `bug` and `feature`, default to `bug`. Misclassifying a
real bug as a feature is the failure mode that lets recurrence happen.

## Causal review subagent contract (step 4)

Spawn one bounded fresh-eye subagent. The subagent must not spawn nested
reviewers. It returns a single triage block the caller can act on directly.

The subagent's prompt must:

- restate the issue body and the reporter's JTBD verbatim
- name the three lenses below and require evidence for each
- include the substrate cite
  (`../../debug/references/five-whys-causal-chain.md`) and the
  "do not re-derive the RCA body" guard verbatim
- bound the time and scope ("under 600 words", "cite file:line")
- forbid prescribing the fix; the implementer designs the fix in step 7
- explicitly tell the subagent it is the bounded fresh-eye reviewer and must
  not invoke `issue`, `critique`, `debug`, or any other skill that itself
  spawns reviewers; complete the three lenses in-process

The single-subagent multi-lens shape (versus critique's multi-angle shape) is
appropriate here because the three lenses share evidence (the same diff, the
same test surface, the same neighboring files) and one reviewer can hold them
without triangulation. When evidence does not flow across lenses — for
example, a multi-component bug where root-cause, detection-gap, and
sibling-search live in different layers — the caller may upgrade to two
subagents (root-cause + detection together; sibling search separately) and
add a counterweight. That upgrade is rare; document it in the resolution
notes when used.

### Lens 1 — Root cause (close-ledger triage)

Consume the `debug` skill substrate
(`../../debug/references/five-whys-causal-chain.md`) and triage the resulting
structural cause through the close-ledger lens: does the named bottom map to
the issue body and the reporter's JTBD, and is the prevention surface (guard,
test, doc, tool) in scope for the close comment? **Do not re-derive the RCA
body in causal review.** If the substrate's chain is missing, weak, or
contradicts the issue body, return that as a
`Causal review: substrate incomplete` block instead of regrowing it inside
this lens.

### Lens 2 — Detection gap

Why did the issue need a human reporter? List concrete failure modes against
existing detection surfaces:

- which tests, gates, lints, type checks, or evals existed but did not fire
- what would have had to change for them to fire (a different assertion, a
  different fixture, a different sample) — the smaller the change, the more
  the gap is a missing invariant rather than missing scope
- whether monitoring or runtime observability would have surfaced this and
  was absent or noisy
- whether a human-only review path is the only realistic detection (some
  product-judgment issues are fine to have here; flag them honestly)

The output should make the next move legible: do we add a guard, broaden a
fixture, fix an assertion, or accept that this class is human-detection?

### Lens 3 — Sibling search

Look for the same pattern elsewhere. Start from the mental model that allowed
the issue, not from the issue title's nouns. Keyword and nearby-file search
are useful, but they are only the first pass.

The reviewer scans four axes:

- **same layer**: the literal same code shape in other modules, scripts, or
  configs (concrete duplications)
- **abstraction up**: the issue is one instance of a more general pattern.
  Name the general pattern in a sentence. Then check whether other instances
  exist (often in different files, different layers, but sharing the
  generalized shape).
- **specialization down**: the issue is the surface of a more specific
  problem. Name the narrower problem and check whether it shows up in finer
  granularity within the same module.
- **mental-model siblings**: name the operator or implementer assumption that
  made the bug plausible, then scan structurally similar traps even when they
  use different names. Common shapes include missing lifecycle endpoints,
  local checks not composed into aggregate surfaces, mutation paths missing a
  readiness probe, renderers hiding failing details, and safety checks that
  trust current working directory or an implicit default as the authority.

Return the exact patterns searched plus concrete locations the implementer
should inspect. The implementer decides at step 5 whether to bundle or defer.

### Output shape (causal review)

The subagent returns:

- `JTBD`
- `Classification confirmation` (agreeing or pushing back on the caller's
  classification)
- `Root cause` (substrate cite from
  `../../debug/references/five-whys-causal-chain.md`, plus close-ledger
  triage; do not regrow the chain) + `Over-reach check`: simplest evidence
  the lens did not invent a structural cause where there was a real symptom
- `Debug artifact: <path>` when a debug session wrote one; otherwise
  `Debug artifact: none (trivial fix)` or `Debug artifact: cite-only`
- `Detection gap` (which gates existed, which did not fire, smallest change to
  fix that) + `Over-reach check`: simplest evidence the gap is real, not "no
  test exists in this corner"
- `Sibling search` (mental model, patterns scanned, concrete locations on
  each axis) + `Over-reach check`: simplest evidence the listed locations are
  actual instances of the same pattern, not surface-level keyword matches
- `Bundle vs Defer recommendation` (a list, with cheap-now flagged)
- `Fresh-Eye Satisfaction`: `parent-delegated` / `nested-delegated` /
  `blocked <host-signal>`

The three `Over-reach check` slots are the lens-internal counterweight; they
keep the single-subagent shape honest without requiring a second spawn.

If the host blocks subagent spawning, stop and surface the blocked state. Do
not run a same-agent local causal review. Step 8 is also blocked for this run
since critique has no prior context to chain into; report both blocked states
in the close artifact.

## Resolution critique (step 8)

After the fix verifies, delegate to the `critique` skill with a recurrence
focus. The critique skill already owns its own bounded subagent contract
(angle reviewers + counterweight). This resolution critique satisfies the
CLAUDE.md task-completion critique obligation: when `issue resolve` is
invoked from `impl`, the implementer should declare
`Critique: full <issue-resolution-artifact>` instead of running a second
generic critique at impl's closeout step.

### Critique handoff template

Pass the following fields when delegating to `critique`:

- `decision_artifact`: the issue URL, the implemented diff (or commit hash),
  and the close comment draft
- `prior_context`: the verbatim causal-review output block from step 4 (so
  reviewers do not redo the root cause analysis)
- `framing_question`: "what would let this class of issue, and the siblings
  surfaced at step 4, come back"
- `success`: the fix is committed, sibling decisions are recorded, and any
  bundled prevention is wired into a guard, test, doc, or tool
- `out_of_scope`: re-litigating the root cause; redesigning the fix;
  re-classifying the issue

If step 4 was blocked (no causal-review output available), do not run
critique against an empty `prior_context`. Report both blocked states in the
close artifact and stop.

### Consuming the result

`critique` returns the four-bin triage (`Act Before Ship`, `Bundle Anyway`,
`Over-Worry`, `Valid but Defer`). Map it onto the close comment:

- `Act Before Ship`: hold commit, fix before close
- `Bundle Anyway`: include in the same commit if cheap
- `Valid but Defer`: list in close comment as deferred items so the next
  reader inherits them without reopening the issue
- `Over-Worry`: do not surface in the close comment

Run one critique per fix-unit (single issue or bundled siblings), not per
issue selector when resolving a range.

## Close comment shape

The close comment is the durable artifact for everyone who finds this issue
later. The shape depends on classification — restate per issue when resolving
a range.

For `bug`:

- the reporter's JTBD
- the root cause in one sentence
- `Debug artifact: <path>` (or `none (trivial fix)` / `cite-only`)
- which siblings were bundled into this commit and which were deferred (and
  where they live so future readers can find them)
- the structural recurrence-prevention move (guard, test, doc, tool) and
  what is deliberately not addressed yet

For `feature` or `deferred-work`:

- the reporter's JTBD
- what was implemented (capability + entry point)
- any critique-bundled prevention; "no recurrence prevention applicable" is a
  valid line for greenfield features

For `question` or `decision-needed`:

- the reporter's JTBD
- the answer or the recorded decision (with link to the durable spec/doc when
  the decision lives outside the issue)

This is the contract that lets `issue resolve` close the loop instead of
just clearing the queue.
