# Release Disposition Review — Repairs That Carry Their Class

Goal: `charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`
Release: `6.2.1`
Tag commit: `46169b7ad7491e1d4b1a50b5411ebf5a08f03a68`
Post-publish artifact/main: `d0df6dc7ac9c761b14bd1d5c5ef8b95bd1f2ec9d`

This is a repository-local disposition review, not a GitHub issue closeout
carrier. Tracker closeout was not requested. The review separates shipped
Charness prevention from issue-specific behavioral probes and external host
claims.

| Issue | Final disposition | Evidence boundary | Remaining non-claim |
| --- | --- | --- | --- |
| #681 | already-satisfied source disposition retained | current source checker and comments-inclusive read | tracker closure not requested |
| #682 | source/planner repair shipped in 6.2.1 | committed-basis carrier plus release/install/version/doctor readback | issue-specific post-publish replay not rerun |
| #683 | snapshot continuation repair shipped in 6.2.1 | emitted `verify --before` carrier plus release/install/version/doctor readback | issue-specific post-publish replay not rerun |
| #685 | persistence repair shipped in source/plugin surfaces | 6.2.1 release and general managed install readback | dedicated post-publish persistence probe not rerun |
| #686 | installed-path planner repair shipped in source/plugin surfaces | 6.2.1 release and general managed install readback | dedicated post-publish planner probe not rerun |
| #687 | Charness non-delivery prevention shipped | typed delivery/readback contract and source/plugin parity | host terminal event and host-side resolution unproven |

The release therefore claims a published Charness repair train and general
managed install/readback, not closure of the GitHub rows or a fresh-eye PASS.
