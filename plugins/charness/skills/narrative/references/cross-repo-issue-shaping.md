# Cross-Repo Issue Shaping

Use this when `narrative` is helping shape an issue, proposal, or durable note
that will be handed to another repo rather than solved only inside the current
one.

Keep the writing order honest:

- `why`: what user, operator, or agent problem is actually showing up
- `what`: what contract, boundary, or outcome should exist
- `how`: candidate implementation directions only after the first two are clear

This keeps the receiving repo from inheriting a frozen implementation sketch
without the problem statement or acceptance boundary that would justify it.

## Rules

- do not lead with an implementation prescription when the receiving repo still
  needs to confirm the real problem
- keep `why` concrete enough that the next maintainer can tell who is blocked
  and how that shows up operationally
- keep `what` framed as contract, boundary, or desired outcome rather than as
  one forced mechanism
- move `how` into candidate directions, not hidden assumptions baked into the
  first paragraph
- if the current repo is only the sender, do not silently write the receiving
  repo's policy choices as settled facts
