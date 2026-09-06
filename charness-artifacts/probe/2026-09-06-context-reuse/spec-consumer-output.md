# Alias acceptance contract

Canonical names map to string values. An alias is a pair (alias, canonical).
Lookup accepts canonical names and aliases. Alias declarations must be consumed
as a list of pairs so duplicate declarations are visible before any dict
conversion. Duplicate alias names must be rejected, even for the same target.

Concrete acceptance examples:

- Given canonical names `blue` and alias declarations `[('b', 'blue'),
  ('b', 'blue')]`, when the declarations are validated, then the input is
  rejected as a duplicate alias before conversion to a dictionary.
- Given canonical names `blue` and `red` and alias declarations `[('tone',
  'blue'), ('tone', 'red')]`, when the declarations are validated, then the
  input is rejected as a duplicate alias before conversion to a dictionary.

These examples define rejection for repeated alias names regardless of whether
the canonical target is the same or different. They do not prescribe an error
type or message, alias ordering after rejection, or any change to the public
API or canonical lookup behavior.
