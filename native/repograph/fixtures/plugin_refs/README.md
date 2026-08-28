<!-- markdownlint-disable MD033 MD048 -->

# Plugin reference fixture

This resolves <plugin-dir>/skills/demo/SKILL.md.
This also resolves <plugin-dir>/README.md.
This is templated <plugin-dir>/skills/<skill>/SKILL.md.
This is also templated <plugin-dir>/skills/.../SKILL.md.
This escapes <plugin-dir>/../README.md.
This is absolute <plugin-dir>//etc/hosts.
This is missing <plugin-dir>/skills/not-shipped/SKILL.md.

Inline code is scanned: `<plugin-dir>/skills/demo/SKILL.md`.

<!-- <plugin-dir>/skills/not-commented.md> -->
<!--
<plugin-dir>/skills/not-commented-either.md
-->

```text
<plugin-dir>/skills/not-fenced.md
~~~
<plugin-dir>/skills/still-fenced.md
```

~~~text
<plugin-dir>/skills/not-tilde-fenced.md
```
<plugin-dir>/skills/still-tilde-fenced.md
~~~

This remains live <plugin-dir>/skills/demo/SKILL.md.
