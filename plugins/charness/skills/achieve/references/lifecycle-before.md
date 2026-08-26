# Achieve Lifecycle — Before

## Before

`achieve` shapes planning truth before any Goal Run mutation. The complete Goal
Draft is the only mutable surface in this phase; it becomes immutable after the
operator approves the exact briefing and bytes.

## Research

Read repository code, current adapter, issue/provider state, relevant specs,
recent lessons, and existing evidence before asking questions. Facts that the
repository or provider can establish are not operator questions. Record source
identities and unresolved assumptions in the draft.

## Interview

Resolve `interview.max_questions` from the adapter, defaulting to 15. The limit
is a ceiling shared by the initial interview and consequential findings from
planning review. Every question records:

- alternatives and the tradeoff of each;
- one recommendation and its reason;
- the operator's answer; and
- why each non-selected alternative was rejected.

Stop when ambiguity is gone. If the ceiling is reached first, return
`interview-cap-reached`, preserve the unresolved decision, and do not create or
mutate a provider parent.

## Approval and binding

Before approval, run the required critique/alignment/briefing work and update
the draft while it is still mutable. Explicit approval binds the complete draft
bytes, final briefing digest, parent identity, and initial Work Item manifest.

After approval:

1. read the exact intended parent through the selected issue provider;
2. freeze and hash the complete draft;
3. create or read back the immutable Goal Binding; and
4. run provider preflight before every subsequent mutation.

The provider operation file carries exact repository and parent identity,
binding/draft hashes, an attempt id, and a repository-local observation path.
No provider mutation is authorized by a local-only or fake-backend success.

## Bootstrap exception

The first live issue-native Goal Run may reconcile its already-existing history through
the minimum provider boundary after approval. Its parent marker is
`verified-target-roundtrip` only after the completed provider, orchestration,
and evidence capabilities re-read the same graph from a clean process. That
marker proves the target read path, not child or parent completion.

## Before-phase closeout

End this phase with a concise record of:

- the complete draft path and frozen hash (after approval);
- the exact parent repository, number, and URL;
- the binding path/hash and approved graph digest;
- the selected provider preflight result;
- the first executable Work Item and its dependencies; and
- explicit non-claims for live, hosted, installed, publish, push, release, and
  issue-close behavior not actually read back.

The next action is the exact objective `/goal #N`. A sidecar path is an internal
identity pointer, never operator input.
