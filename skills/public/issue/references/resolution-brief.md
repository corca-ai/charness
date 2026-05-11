# Resolution Brief

`feature` and `deferred-work` issues require a **pre-mutation resolution
brief** at step 6 of the resolve flow. The brief makes the proposed product
or workflow boundary visible in the transcript before any mutation tool is
invoked, so scope and tradeoff disagreements can be caught while they are
still cheap.

This complements the bug-class causal review at step 4: both insert a
fresh-eye pause between issue reading and design, but the brief is owned by
the resolving agent (boundary intent) while causal review is owned by a
bounded fresh-eye subagent (root-cause attribution).

## Brief Template

Emit the brief as a transcript block before the first mutation tool call. The
block is markdown and contains, at minimum:

```markdown
## Resolution Brief — <org>/<repo>#<number>

**Classification**: <feature|deferred-work>

**Reporter JTBD**: <one line>

**Proposed boundary**:
- in scope: <what this fix owns>
- out of scope: <what this fix does not own>

**Non-goals**:
- <thing explicitly not being done>

**Acceptance checks**:
- <how we know the fix is done>

**Open decisions**:
- <contentious tradeoff, or the literal `none`>

**Autonomous vs pause**: <continuing because empty open decisions and
adapter/flag pre-authorized | pausing for user discussion>
```

Inline rendering is fine — the brief does not need to be a separate file unless
it pauses (see Persistence below).

## Pause vs Continue

Open decisions always force a pause. The adapter setting and invocation flag
only control the empty-open-decisions case.

| Adapter `feature_brief_pause` | open decisions non-empty | open decisions empty |
| --- | --- | --- |
| `on-open-decisions` (default) | pause | continue |
| `always` | pause | pause |
| `never` | pause | continue |

Invocation flags override the adapter for one invocation:

- `--auto` → equivalent to `feature_brief_pause: never`
- `--pause` → equivalent to `feature_brief_pause: always`

Non-empty `open decisions` cannot be overridden. The brief still pauses.

## Persistence

When the brief pauses, persist it as a dated artifact so the discussion is
recoverable across session compaction or restart. Resolve the path through:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" brief-path --repo-root . --number <n>
```

That emits a canonical `charness-artifacts/issue/YYYY-MM-DD-issue-<n>-brief.md`
write path. Write the same brief text there before pausing.

When the brief continues without pause (empty open decisions + `--auto` or
`feature_brief_pause: never`), transcript emission is sufficient and no
artifact is written. The commit message and the close comment's
`Resolution brief: inline (no pause)` line carry the boundary forward.

## Trivial-Feature Short-Circuit

The brief may be replaced by a single transcript line when all three of the
following hold:

1. the fix touches a single file
2. no public contract changes (no SKILL.md surface, no adapter schema, no
   exported docs, no marketplace manifest)
3. no plausible alternative implementation surface (renames or simple typo
   fixes are the canonical case)

Record:

```text
Resolution brief: trivial; boundary = <one line>
```

and proceed. The close comment uses `Resolution brief: trivial`. Misuse of
the short-circuit is a guardrail failure mode in `SKILL.md`.

## Range Resolve

Run the brief per fix-unit, not per selector. When step 5 bundles sibling
issues into one commit, that fix-unit shares one brief. When sibling issues
are deferred or filed separately via `issue new`, each separately-resolved
fix-unit gets its own brief on its own resolve turn.

## Close Comment Coupling

The step 10 close comment for `feature`/`deferred-work` carries the brief
forward through:

- a one-line `Boundary` field (copied from the brief)
- a `Resolution brief: <path>` field, with `inline (no pause)` or `trivial`
  as alternatives

This lets a later reader recover the resolved boundary directly from GitHub
state without rebuilding the transcript.
