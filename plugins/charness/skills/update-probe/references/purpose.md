# Purpose

`update-probe` exists only as an operator-visible sentinel while validating
whether `charness update` propagates upstream payload changes into the
host-visible installed copy.

Use it to answer a narrow question:

- after a clean installed baseline exists, does `charness update` make a newly
  added public skill appear without extra host actions, or only after
  `re-enable` or `reinstall`?

Once that question is answered, remove the skill again instead of normalizing
it into the long-term public surface.
