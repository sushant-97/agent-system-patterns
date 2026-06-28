# Agent System Patterns

Practical control patterns for building AI agents that can be inspected,
verified, rolled back, and improved.

This repo focuses on agent reliability infrastructure rather than prompt packs
or role-play agent templates. Each pattern includes:

- a production-inspired failure mode
- a concrete control mechanism
- runnable Python code
- local experiments with checked-in results
- original diagrams
- engineering references from teams shipping real products

## Patterns

| Pattern | Use It When | Core Control |
| --- | --- | --- |
| [Decision-Time Guidance](patterns/01-decision-time-guidance/README.md) | An agent is drifting, looping, ignoring logs, or overusing generic instructions | Watch the trajectory and inject a short, evidence-backed nudge only when the current decision needs it |
| [Self-Verification Loop](patterns/02-self-verification-loop/README.md) | An agent produces plausible output but may not have working behavior | Run an executable scenario, capture evidence, repair from failure, and rerun |
| [Reversible Sandbox Execution](patterns/03-reversible-sandbox-execution/README.md) | An agent needs to edit code/data but direct side effects are risky | Fork state, run the attempt in isolation, verify it, and promote only approved diffs |

Together, the three patterns form a reliability loop:

```text
guide the decision -> verify the result -> bound the side effects
```

## Quickstart

Run all published pattern demos and experiments:

```bash
npm run check
```

Run individual patterns:

```bash
python3 patterns/01-decision-time-guidance/guidance_engine.py
python3 patterns/01-decision-time-guidance/experiments/run_experiments.py

python3 patterns/02-self-verification-loop/verification_engine.py
python3 patterns/02-self-verification-loop/experiments/run_experiments.py

python3 patterns/03-reversible-sandbox-execution/sandbox_engine.py
python3 patterns/03-reversible-sandbox-execution/experiments/run_experiments.py
```

## Repository Layout

```text
patterns/
  01-decision-time-guidance/
    guidance_engine.py
    experiments/
    source-diagrams/
    assets/
  02-self-verification-loop/
    verification_engine.py
    experiments/
    source-diagrams/
    assets/
  03-reversible-sandbox-execution/
    sandbox_engine.py
    experiments/
    source-diagrams/
    assets/
```

Each pattern directory is designed to stand alone: read the pattern README, run
the Python implementation, then inspect the experiment results.

## Source Standard

The repo prioritizes technical writing from product engineering teams. For the
current patterns, the primary sources are Replit engineering posts:

- [Decision-Time Guidance](https://replit.com/blog/decision-time-guidance)
- [Automated Self-Testing](https://replit.com/blog/automated-self-testing)
- [Inside Replit's Snapshot Engine](https://replit.com/blog/inside-replits-snapshot-engine)

See [references.md](references.md) for source notes.

See [docs/principles.md](docs/principles.md) for the repo's design principles.

There is also a static overview page at [docs/index.html](docs/index.html).

## Pattern Quality Bar

A pattern should not be added unless it has:

- a concrete failure mode
- a control boundary, not just a better prompt
- runnable code with visible pass/fail behavior
- experiments or source-reported results
- clear failure modes and tradeoffs
- at least one credible engineering reference

## Roadmap

Planned next additions:

1. **Static Prompt vs Runtime Control Comparison**  
   A small experiment comparing global reminders against decision-time guidance.

2. **Sandbox Merge Policy Extensions**  
   More realistic diff categories: dependency upgrades, schema migrations,
   generated files, secrets, and network effects.

3. **Trace Viewer**  
   A lightweight static view for agent trajectories, detected signals, injected
   guidance, sandbox diffs, and promotion decisions.

## Non-Goals

- Prompt collections.
- Generic multi-agent role templates.
- Framework comparison matrices.
- Claims of reliability without executable checks or cited evidence.
