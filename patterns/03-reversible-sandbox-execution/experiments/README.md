# Reversible Sandbox Execution Experiments

This folder separates hands-on local experiments from source-reported evidence.

## Folder Layout

```text
experiments/
  README.md
  run_experiments.py
  hands-on/
    README.md
  results/
    safe-ui-copy.json
    destructive-billing-migration.json
    external-side-effect.json
    competing-sandboxes.json
    summary.json
  source-reported/
    replit-snapshot-engine.md
```

## Run

From the repo root:

```bash
python3 patterns/03-reversible-sandbox-execution/experiments/run_experiments.py
```

The script writes JSON result files into `results/`.

## Current Experiments

| Experiment | Question | Expected Result |
| --- | --- | --- |
| Safe UI copy | Can a low-risk file change promote? | Promoted |
| Destructive billing migration | Does durable data loss get blocked? | Rejected |
| External side effect | Does non-reversible external activity get blocked? | Rejected |
| Competing sandboxes | Can two forks be compared before promotion? | Promote only the safe candidate |

## Source-Reported Evidence

See [source-reported/replit-snapshot-engine.md](source-reported/replit-snapshot-engine.md).

