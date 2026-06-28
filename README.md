# Agent System Patterns

A focused, production-inspired study of reliable AI agent control patterns.

This repository intentionally starts small. It is not an "awesome agents" list,
a prompt dump, or a collection of role-play agent names. The first release goes
deep on a small set of control patterns:

1. Decision-time guidance
2. Reversible sandbox execution

Each pattern includes architecture diagrams, runnable Python code, experiments,
failure modes, and references from engineering teams that ship products.

## Why A Small Pattern Set?

Agent systems fail in boring, expensive ways: they repeat mistakes, claim work is
done without checking it, or make irreversible changes before anyone understands
the blast radius. A broad catalog is easy to make shallow. This repo starts by
making a few control patterns concrete enough to run, inspect, and criticize.

## Current Pattern

| Pattern | Problem It Solves | Main Idea |
| --- | --- | --- |
| [Decision-Time Guidance](patterns/01-decision-time-guidance/README.md) | Agents drift, loop, or ignore long static instructions | Detect the current failure shape and inject a short, situational nudge |
| [Reversible Sandbox Execution](patterns/03-reversible-sandbox-execution/README.md) | Agents need autonomy but durable side effects are risky | Fork state, verify the attempt, and promote only approved diffs |

## Quickstart

The implementation uses Python standard library code. The repo check is wrapped
in Node only so later patterns can share one command.

```bash
node scripts/run-examples.mjs
```

You can also run the pattern and experiments directly:

```bash
python3 patterns/01-decision-time-guidance/guidance_engine.py
python3 patterns/01-decision-time-guidance/experiments/run_experiments.py
python3 patterns/03-reversible-sandbox-execution/sandbox_engine.py
python3 patterns/03-reversible-sandbox-execution/experiments/run_experiments.py
```

## Quality Bar

A pattern belongs here only if it has:

- A specific production failure mode.
- A concrete control mechanism, not just a prompt.
- A runnable example with visible pass/fail behavior.
- A "when not to use this" section.
- A cited engineering reference from a team shipping real products.

## Primary References

This V1 uses Replit's engineering writing as the primary source set because the
posts describe concrete control systems around a real coding agent:

- [Decision-Time Guidance](https://replit.com/blog/decision-time-guidance)
- [Inside Replit's Snapshot Engine](https://replit.com/blog/inside-replits-snapshot-engine)

See [references.md](references.md) for the full reference notes and how sources
are evaluated.

## Non-Goals

- No generic "multi-agent CEO/PM/engineer" role-play examples.
- No prompt collections without an execution harness.
- No framework fan-out matrix.
- No claims that an agent is reliable unless the example verifies behavior.
