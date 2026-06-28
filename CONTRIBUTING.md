# Contributing

The goal is depth, not volume.

## Pattern Acceptance Checklist

A new pattern must include:

- A production failure mode.
- A diagram.
- Runnable code with no paid API dependency.
- A clear verification step.
- Failure modes and tradeoffs.
- A "when not to use this" section.
- At least one credible engineering source.

## Preferred Pattern Template

```text
patterns/NN-pattern-name/
  README.md
  example.mjs
```

The README should answer:

- What problem does this solve?
- What is the control mechanism?
- What state does it observe?
- What action does it take?
- How does it fail?
- How do you verify it?

## Anti-Slop Rules

- Do not submit prompt-only patterns.
- Do not add role-play agents unless they have real control behavior.
- Do not cite a company just because it is famous; cite the specific technical
  mechanism.
- Do not add examples that only print a happy path.

