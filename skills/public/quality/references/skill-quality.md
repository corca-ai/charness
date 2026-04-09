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
- references that exist and still match the body
- cold-start bootstrap that actually works on a clean repo
- durable artifact seams that are explicit and overridable
- repeated helper logic that should move to a shared seam
- drift between what the skill promises and what shipped scripts can enforce
- repeated documentation blocks that create copy-paste maintenance across skill
  bodies, references, or repo docs

Preferred deterministic gates:

- package validators such as `validate-skills.py`
- adapter resolution smoke checks such as `validate-adapters.py`
- duplicate detection for copied helper logic
- duplicate detection for checked-in docs and reference bodies
- markdown and link checks for checked-in skill docs

Preferred manual findings:

- one skill carrying too many concepts
- option or mode splits that should be inference instead
- portability drift that is conceptually real but not fully machine-checkable
