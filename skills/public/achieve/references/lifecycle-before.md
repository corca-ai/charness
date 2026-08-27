# Achieve Planning and Binding

Research the repository, adapter, relevant design material, and intended
provider target before asking the operator. Facts that can be established by
the repository or provider are not interview questions.

Create and refine one Goal Draft with `upsert_goal.py`. Keep consequential
alternatives, tradeoffs, recommendation, and critique reasoning in its
planning sections. Safe checkout paths must be portable or explicitly
dispositioned. The draft may remain incomplete while the operator is answering
ordinary planning questions.

Resolve `interview.max_questions` from the adapter, defaulting to 15. The
ceiling applies to the whole bounded interview. If it is reached with an
unanswered decision, return `interview-cap-reached`, preserve that decision,
and wait; do not create a Goal Binding or provider parent.

After explicit approval of the exact briefing and draft bytes, read the exact
parent identity, hash the draft, and create the immutable Goal Binding. The
binding records the parent and approved Work Item manifest. No provider
mutation occurs before that identity is established.
