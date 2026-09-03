Release charness 8.0.3

Release: v8.0.3

Quality: ./scripts/run-quality.sh --release --read-only

release: charness 8.0.3 ships the #784 mechanisms and skill scripts inside the authoring repo run from the checkout (#788)

Closes #788

Classification: feature
Jtbd: a Charness consumer updates to a release whose lanes cannot report done past an unproven changed line, whose tests cannot ride a short deadline, whose runtime tree reclaims itself, and whose skill scripts say which copy answered; a maintainer session in this repo reads the checkout rather than an older installed plugin.
Boundary: the routing half landed in the parent commit series (goal_run_pickup.py and plan_release_run.py report `script_origin`; a drifted installed copy inside the authoring repo refuses as `stale-installed-copy`; bootstrap-resolution.md, the Claude host adapter, and docs/development.md carry the rule). The release half is the version bump to 8.0.3, the synced install manifests, the derived release notes, the GitHub release, the distinct-channel readback, the maintainer install refresh, and the readback from a consumer checkout, all through the release skill's own helper. No tag or manifest was written outside that helper.
Resolution Brief: charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md slice 5 and the #788 Work Item body; the operator pre-approved the 8.0.3 decision on 2026-09-03 and no release-skill step was skipped.
Implementation: two file-backed Codex fresh-eye reviewers (operational checklist; operator-surface legibility) ran over the release-locking surfaces before the bump, and the parent's counterweight pass is the critique artifact the publish helper was given; the notes were derived from the final tree and linted; the publish helper ran the release quality lane in a clean worktree, stopped at the prepared record for the claims review, and resumed to tag, publish, confirm through the https channel, and refresh the maintainer install.
Prevention: the routing mechanism is proven by tests/quality_gates/test_achieve_goal_run_pickup.py (a seeded drifted installed copy inside the authoring repo is refused before any provider read; the checkout reports same-tree; a consuming repo is never refused) and tests/quality_gates/test_release_planner_script_origin.py; the release itself is proven by the release record under charness-artifacts/release/ and the claims-review record under charness-artifacts/release-review/.
Review disposition: release critique artifact under charness-artifacts/critique/ named in the release record; claims review recorded with its observer distinctness as measured.
AI-provenance: implemented, reviewed through file-backed Codex workers, and published by an AI agent (Claude Code) in the Goal Run #784 session under the operator's pre-approval of 2026-09-03.
Goal lineage: Goal Run corca-ai/charness#784; draft sha256 878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151; binding sha256 9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82; Work Item checkout-first-routing-and-8-0-3 (#788).

Behavior #788: verified — pickup and the release planner report script_origin same-tree from the checkout and the generated mirror reports in-sync; a seeded drifted installed copy is refused before any provider read; the release is read back from the managed checkout after charness update
