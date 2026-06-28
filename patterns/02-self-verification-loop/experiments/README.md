# Self-Verification Loop Experiments

This folder separates hands-on local experiments from source-reported evidence.

## Folder Layout

```text
experiments/
  README.md
  run_experiments.py
  hands-on/
    README.md
  results/
    shallow-false-pass.json
    behavioral-catches-potemkin.json
    repair-rerun.json
    summary.json
  source-reported/
    replit-automated-self-testing.md
```

## Run

From the repo root:

```bash
python3 patterns/02-self-verification-loop/experiments/run_experiments.py
```

## Current Experiments

| Experiment | Question | Expected Result |
| --- | --- | --- |
| Shallow false pass | Can a broken app pass visual-only checks? | Yes, proving the verifier is weak |
| Behavioral catches Potemkin | Does behavioral evidence catch fake success? | Yes, rejected |
| Repair rerun | Can failed evidence drive a repair that passes rerun? | Yes, repaired app passes |

## Source-Reported Evidence

See [source-reported/replit-automated-self-testing.md](source-reported/replit-automated-self-testing.md).

