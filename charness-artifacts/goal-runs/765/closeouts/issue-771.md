Closeout carrier: commit `6673ad6d9e4f3142bdb07206f60626284565aa2a` on `origin/main` (`Closes #771`), Goal Run corca-ai/charness#765; `issue_tool.py verify-closeout` = `verified` against that commit.

Classification: feature
Jtbd: when a charness skill's output forces rework in a consuming repo, the operator files it once and the next retro shows which skill caused it, without a new gate.
Boundary: issue filing shape (issue-shaping.md, issue SKILL.md), retro packet read (retro SKILL.md, prepare-packet.md, .agents/retro-adapter.yaml), one packet-section producer under scripts/; the `rework` label was created in corca-ai/charness and applied to #773. No skill behaviour redesigned.
Resolution Brief: charness-artifacts/goals/2026-09-02-north-star-realignment.md, slice 1 rework-instrument, and the #771 child body.
Implementation: scripts/render_retro_section_rework_issues.py runs gh through subprocess_guard.run_process, filters by created date, parses the first Causing skill: line with prose annotations stripped (the live #773 line's parenthetical rendered as a third skill in the disconfirming probe), and renders a per-skill table; it exits 0 with an UNAVAILABLE body when gh is absent. tests/test_retro_section_rework_issues.py covers it in-process with a fake runner (6 tests).
Prevention: the parser test pins the live #773 line so annotation drift cannot recreate a phantom skill row, and the retro SKILL.md tells the reader that an UNAVAILABLE body is an unread section, not zero rework.
Behavior: verified — charness-artifacts/retro/2026-09-02-771-rework-instrument-packet.md, produced by prepare_packet.py against live GitHub, renders achieve 1 and issue 1 for the period containing #773.
Review disposition: critique not required for this reversible local docs and adapter change; the export boundary proof belongs to #769.
AI-provenance: drafted, implemented, and verified by an AI agent (Claude Code) in the Goal Run #765 session; the producer was written by a Codex lane and integrated by the parent.
Goal lineage: Goal Run corca-ai/charness#765; draft sha256 129f065a28ce2c6a6a7fd7dc5f6ff2b63349b75ddf1ab62411ea4879ff8d2501; binding sha256 20fdaf7e9a3e1489a308b11041555a9249b2e826d93d951f294a565b24d161cf; Work Item rework-instrument (#771).
