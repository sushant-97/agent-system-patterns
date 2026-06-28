# Decision-Time Guidance Experiments

This folder separates three things:

1. **Hands-on experiments**: synthetic traces we can run locally.
2. **Implementation**: the script that executes those traces against the Python
   guidance engine.
3. **Source-reported evidence**: short, attributed summaries of experiments or
   results described by product engineering teams.

The local experiments are not claims about Replit's internal implementation.
They test whether our interpretation of the pattern has useful control behavior.

## Folder Layout

```text
experiments/
  README.md
  run_experiments.py
  hands-on/
    README.md
  results/
    long-debugging-session.json
    cooldown-prevents-repeated-noise.json
    risky-cleanup.json
    summary.json
  source-reported/
    replit-decision-time-guidance.md
```

## Run

From the repo root:

```bash
python3 patterns/01-decision-time-guidance/experiments/run_experiments.py
```

The script writes JSON files into `results/`. These files are checked in so a
reader can inspect the outcome without running code.

## Experiment Standard

Each experiment should state:

- question
- trace shape
- implementation entry point
- expected result
- observed result
- interpretation

## Current Local Experiments

| Experiment | Question | Expected Result |
| --- | --- | --- |
| Long debugging session | Does the controller catch repeated runtime/debugging failure? | Inject `doom_loop` and `diagnostic_signal`; suppress lower-priority `mock_data_escape` |
| Cooldown prevents repeated noise | Does the controller avoid repeating the same nudge immediately? | Suppress recently injected guidance; allow a different relevant card |
| Risky cleanup | Does the controller intervene on destructive commands even without test failures? | Inject `unsafe_change` |

## Source-Reported Evidence

See [source-reported/replit-decision-time-guidance.md](source-reported/replit-decision-time-guidance.md).

