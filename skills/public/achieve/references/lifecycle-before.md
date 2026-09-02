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
ceiling applies to the whole bounded interview, including questions raised by
the critique rounds. Record every question in the sibling interview record and
validate it with `interview_contract.py`; only `interview-complete` permits a
parent. If the ceiling is reached with an unanswered decision, the record reads
`interview-cap-reached`; preserve that decision and wait; do not create a Goal
Binding or provider parent.

Before asking for approval, run the pre-approval sequence from `SKILL.md`:
framing critique, child body drafting, adversarial critique of the repaired
whole, a current-to-target audit, and the briefing. Missing steps are stated,
not implied.

After explicit approval of the briefing and draft, read the exact parent
identity, hash the draft, and create the immutable Goal Binding. The binding
freezes the plan by draft hash and the approved Work Item manifest by stable
KEY. Children are later identified by their Work Item marker. Provider
membership is established by the provider's sub-issue graph plus parent
metadata `amendments`; prose edits never invalidate a run. No provider mutation
occurs before that identity is established.
