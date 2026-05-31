# Asset Refresh

`gather` should refresh an existing asset in place when the source identity is
the same.

## Same Source Signals

- same URL
- same repo path
- same document identity or upstream page

## Rule

Prefer one durable asset per source identity.

If freshness matters, add a concise update note or history entry instead of
creating a sibling file with almost the same contents.

## Pointer vs Canonical Record

The adapter exposes one artifact path (e.g., `latest.md`). Treat that path
as a **current pointer** that may be one of:

- empty (no asset captured yet)
- a regular markdown file holding the most recent record
- a symlink to a dated canonical record under the same directory

Never `apply_patch` or otherwise edit a current-pointer path that is a
symlink: the write follows the link and silently overwrites the prior
canonical record. The recipe is the same in all three cases:

1. Decide on a slug and write the new content to a dated canonical record
   under the same directory (e.g., `charness-artifacts/gather/YYYY-MM-DD-<slug>.md`).
   Always write to a fresh dated path; do not reuse another record's
   filename.
2. Safely refresh the current pointer to reference the new record. Use
   the scripted writer
   `../scripts/write_record.py` so the
   pointer-refresh path is symlink-aware. The refresh is unlink-then-write
   (mirrors `<repo-root>/scripts/refresh_current_pointer.py` in shape, not
   strictly POSIX-atomic); the small window is acceptable for gather's
   read-mostly workload. The writer:
   - existing symlink pointer → unlink + symlink to the new record
     (atomic)
   - existing regular file pointer → copy the dated record into place
     (refuses to silently follow a symlink it did not create)
   - empty pointer slot → fresh write
3. Verify the prior canonical record is byte-identical to its pre-write
   state. Any caller that bypasses the recipe and edits the pointer path
   directly is at risk of clobbering an unrelated record.

The asymmetric guard against symlink-follow lives at the writer surface
because read-side consumers of `latest.md` are happy to follow the link;
only writes need the lstat check.
