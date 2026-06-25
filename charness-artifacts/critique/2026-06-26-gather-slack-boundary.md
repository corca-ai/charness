# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the gather advice test-speed slice that moves Google Workspace and Slack
payload behavior below the subprocess boundary while documenting intentional
real CLI smokes in the boundary-bypass exemption list.

## Failure Angles

- Jackson/problem framing: reducing nested process cost could remove the
  operator-facing `advise_slack_path.py --repo-root` command proof.
- Gawande/operations: exemption additions could hide ordinary behavior that
  should move in-process.
- Kent Beck/test feedback: the slice should reduce candidate/key counts while
  keeping behavior assertions readable at the test site.

## Counterweight Pass

- The first draft failed the real-boundary check; fresh-eye found all Slack CLI
  subprocess coverage had been removed.
- The final patch keeps one subprocess smoke per operator-facing advice command
  and exempts each with a rationale, while payload assertions call `payload_for()`.
- The output-schema exemption is justified because classifier/validator behavior
  stays in-process and the retained subprocess smoke proves startup and JSON
  stdout only.
- Public-skill review does not require a Cautilus run: the planner recommends
  no evaluator execution, and the existing gather scenario still covers routing
  while deterministic tests cover the helper seam.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_gather_google_workspace.py | action: fix | note: first draft removed all Slack advice CLI process proof; final patch restores one smoke per advice command
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/test_gather_google_workspace.py | action: fix | note: Google Workspace and Slack behavior assertions now call payload_for directly while keeping JSON fields visible
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/boundary-bypass-exemptions.txt | action: document | note: output-schema and gather advice retained CLI smokes now carry why, owner, and revisit rationale
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/gather/scripts/advise_google_workspace_path.py | action: fix | note: Google Workspace helper now has the same payload_for seam shape as Slack, including host-mediated coverage
- F5 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/scripts/boundary-bypass-exemptions.txt | action: fix | note: fresh-eye found plugin mirror drift after the Google exemption and sync cleared it before closeout
- F6 | bin: over-worry | evidence: moderate | ref: scripts/boundary-bypass-exemptions.txt | action: document | note: exempting intentional real-boundary smokes is policy-compliant when ordinary behavior remains in-process
- F7 | bin: bundle-anyway | evidence: strong | ref: evals/cautilus/scenarios.json | action: document | note: gather scenario coverage remains unchanged because this slice changes helper execution seams, not first-skill routing

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent_type=explorer, fork_context=false, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: fields accepted by spawn call; provider application not independently confirmed

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewers `019f011f-88da-7bb0-a33d-01965c9123ac`
and `019f0124-a296-7ba2-b223-8e5a2b45b1ae` completed through
`multi_agent_v1.spawn_agent`; the parent patch restored real subprocess CLI
smokes and synced plugin mirrors before closeout.
