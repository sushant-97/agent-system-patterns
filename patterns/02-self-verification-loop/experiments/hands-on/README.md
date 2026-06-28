# Hands-On Experiments

These experiments exercise the Python verifier in
[../verification_engine.py](../../verification_engine.py).

## 1. Shallow False Pass

Question: can a broken app pass if verification only checks visible success?

Expected:

- shallow scenario passes.
- app still does not persist the signup.

Result: [../results/shallow-false-pass.json](../results/shallow-false-pass.json)

## 2. Behavioral Catches Potemkin

Question: does a behavioral verifier catch fake success?

Expected:

- behavioral scenario fails.
- failed evidence includes missing persisted email and missing persistence log.

Result: [../results/behavioral-catches-potemkin.json](../results/behavioral-catches-potemkin.json)

## 3. Repair Rerun

Question: can the failed evidence drive a targeted repair and rerun?

Expected:

- pre-repair report fails.
- repair swaps in a persistence-capable submit handler.
- post-repair report passes.

Result: [../results/repair-rerun.json](../results/repair-rerun.json)

