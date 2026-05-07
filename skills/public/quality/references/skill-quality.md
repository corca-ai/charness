# Skill Quality

When a repo authors skills, `quality` should inspect them as first-class
runtime artifacts, not only documentation.

Borrow from `refactor` the habit of controlling drift across:

- `SKILL.md`
- references and scripts
- adapter examples and resolver behavior
- claimed workflow versus runnable helper surface

Check for:

- frontmatter that standard YAML parsers can read safely
- trigger contract honesty between directory name, frontmatter name, and body
- concise `SKILL.md` core that stays a decision skeleton rather than a second
  handbook
- progressive disclosure honesty: `SKILL.md` owns selection/sequence and
  references deepen the path without forking it
- unnecessary mode or option pressure when stronger defaults or inference would
  do
- trigger overlap or undertrigger risk against nearby public skills
- support-skill discoverability when workflow language implies hidden support
  surfaces such as executable specs, browser automation, markdown preview, or
  external-source gather providers
- references that exist and still match the body
- cold-start bootstrap that actually works on a clean repo
- durable artifact seams that are explicit and overridable
- repeated helper logic that should move to a shared seam
- repeated prose ritual that should become a helper script
- growing lint suppressions that indicate missing entrypoint, packaging, or helper seams
- drift between what the skill promises and what shipped scripts can enforce
- repeated documentation blocks that create copy-paste maintenance across skill
  bodies, references, or repo docs
- selection logic that drifted out of `SKILL.md` core into references, turning
  a reference into a second workflow instead of progressive disclosure
- stale E2E, eval, or smoke paths that still pay standing runtime after a
  cheaper and more direct proof now covers the same seam
- validator assertions that overfit exact prose snippets instead of checking the
  behavior, routing, package-level reference, or machine-readable contract they
  are meant to protect

Preferred deterministic gates:

- package validators such as `validate_skills.py`
- adapter resolution smoke checks such as `validate_adapters.py`
- duplicate detection for copied helper logic
- duplicate detection for checked-in docs and reference bodies
- markdown and link checks for checked-in skill docs
- repo-owned validators that fail on bare internal markdown references in prose
  when the project expects document mentions to stay clickable
- reference-aware contract checks for skill packages where `SKILL.md` owns the
  core trigger and `references/` may own detailed rules
- task-text support recommendation checks when a support skill should be
  discoverable before nearby public workflows continue

Preferred manual findings:

- one skill carrying too many concepts
- option or mode splits that should be inference instead
- a skill that assumes the model is too dumb to infer the obvious next move,
  causing needless user-facing branching
- portability drift that is conceptually real but not fully machine-checkable
- source-guard style tests over prose that should become package-level,
  structure-aware, or scenario-backed assertions before they block useful
  skill compression
