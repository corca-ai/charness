# Sequence Discipline

Use this when several implementation slices are plausible and order matters.

## Core Moves

- start with the slice that makes later work clearer or cheaper
- avoid locking in adjacent detail before the seam around it is proven
- prefer moves that preserve recovery paths and later option value
- keep verification aligned with the slice order so each step proves the next
  move honestly

## Translation For Impl

- choose the slice that answers the highest-leverage probe first
- do not spend early effort on polish or breadth that depends on an unproven
  seam
- if one slice would freeze an interface too early, delay it until the seam is
  better understood
