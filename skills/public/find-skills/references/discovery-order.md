# Discovery Order

`find-skills` should search in this order:

1. local public skills
2. local support skills
3. local external integration manifests
4. adapter-configured trusted skill roots
5. missing capability classification

Reason:

- users should prefer what already ships in the current harness
- support skills are not the product's public concept layer
- external integrations may require install/update/doctor flows that are not yet
  active
- trusted skill roots are host-trusted extension surfaces, not local product
  ownership

When more than one match exists:

- prefer the most direct public concept
- prefer local public skills over trusted-root skills unless the host adapter
  says otherwise
- fall back to support or integration layers only when the need is primarily a
  tool-use capability
