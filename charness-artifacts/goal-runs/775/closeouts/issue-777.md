core: one layout resolver answers where a repo script lives, and a form check refuses another (#777)

Closes #777

Since the concept packaging (#770) the question "where does scripts/<name>
live now" had six private answers: a glob in scaffold_artifact_lib, two
rglobs in seeding_support, a glob in the exported quality skill's
public_spec_adapter_policy, two rglobs in tests/script_closure.py, and three
more rglobs in tests the plan had not listed. Each carried its own fallback,
and the #770 rename sweep, with nothing to ask, swept by regex. repo_layout.py
now owns the answer: repo_script and find_repo_script return the flat path or
the one packaged owner, a miss is a typed RepoScriptMiss, and two owners is a
RepoScriptAmbiguity rather than the first sorted match. Every lookup is folded
onto it and deleted; present_gate schedules the path the resolver found so a
bare name that moved into a package no longer schedules a missing flat file.
check_script_lookup_form.py refuses a by-name glob or rglob under scripts/
outside the resolver, tests included, and runs in the standard lane.

Classification: feature
Jtbd: a maintainer who moves or adds a script under scripts/ changes one resolver and no caller, and the next lookup someone writes by hand is refused before it lands.
Boundary: scripts/core/repo_layout.py, scripts/core/scaffold_artifact_lib.py, scripts/staged_commit_gate_plan_helpers.py, skills/public/quality/scripts/public_spec_adapter_policy.py and public_spec_inventory_lib.py, tests/script_closure.py, tests/quality_gates/seeding_support.py and support.py, three tests that searched scripts/ by name, the new gate with its registration in .agents/quality-gates.yaml, the test fixture copy, tests/quality_gates/support.py, the repograph label fixture, docs/validator-timing-layers.md, and docs/development.md. No file moved; no rename-sweep tool.
Resolution Brief: charness-artifacts/goals/2026-09-03-verification-shape-alignment.md slice 2 and the #777 Work Item body.
Implementation: the resolver is flat-first, then a single rglob under scripts/ skipping __pycache__; a scripts-relative path is taken literally and never searched. scaffold_artifact_lib keeps one fixed path (scripts/core/repo_layout.py) as its only hard-coded location and asks the resolver for everything else, because it must stay importable with no package context. The exported skill reaches the resolver through the skill runtime bootstrap, the seam every other quality script uses. _seed_path became seeded_script_path with the twin's location from the resolver; _packaged_script, _repo_script, and load_repo_script_module no longer exist.
Prevention: the #778 clean-clone proof ran the release lane on this tree and caught test_scaffold_changed_line_coverage.py, a release_only test that located the fallback by the literal `_repo_script` anchor; the anchor now names find_repo_script, and the standing lane could not have seen it. check_script_lookup_form.py with seeded refusals for an rglob, an f-string glob, a variable pattern, and a lookup inside tests/, plus enumerations and non-scripts trees staying green; test_repo_script_resolver.py covers flat, packaged, relative-literal, missing, ambiguous, and bytecode-cache cases; the live-repo test asserts zero lookups outside the resolver.
Behavior: verified — python3 scripts/gates/check_script_lookup_form.py --repo-root . --require-git-file-listing validates 1457 file(s); export-safe PASS and python3 -m tools.check_export_self_sufficiency exit 0 after the mirror sync; run_standing_pytest.py 8620 passed with release_only and slow_corpus deselected; ./scripts/run-quality.sh --full --read-only 81 passed, 0 failed; ./scripts/check-docs.sh PASS, all read on the integrated tree at the #777 closeout, which includes this commit.
Review disposition: critique not required; reversible refactor proven by the form check on the live tree, seeded refusals, and the standing lane.
AI-provenance: implemented, probed, and verified by an AI agent (Claude Code) in the Goal Run #775 session.
Goal lineage: Goal Run corca-ai/charness#775; draft sha256 6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898; binding sha256 ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0; Work Item layout-resolver (#777).
