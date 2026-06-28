# Hands-On Experiments

These experiments use synthetic traces because a minimal public repo cannot
recreate Replit's full agent runtime, tool telemetry, or eval suite.

The traces still exercise real control decisions:

- extract signals from event history.
- score and rank competing signals.
- enforce a card budget.
- suppress repeated guidance through cooldowns.
- emit evidence for every injected or suppressed card.

## 1. Long Debugging Session

Question: if an agent repeatedly edits the same file while the same runtime
error continues, should guidance be injected?

Trace:

```text
user reports crash
agent edits src/signup.py
test fails
console reports TypeError
agent edits src/signup.py again
test fails again
same console error appears again
agent edits src/signup.py again
agent proposes fake response
```

Expected result:

- inject `doom_loop`
- inject `diagnostic_signal`
- detect but suppress `mock_data_escape` because the card budget is full

Result file: [../results/long-debugging-session.json](../results/long-debugging-session.json)

## 2. Cooldown Prevents Repeated Noise

Question: if the same failure is still visible one turn later, should the harness
repeat the same guidance?

Expected result:

- suppress `doom_loop` because it is on cooldown.
- suppress `diagnostic_signal` because it is on cooldown.
- inject `mock_data_escape` because it is relevant and not on cooldown.

Result file: [../results/cooldown-prevents-repeated-noise.json](../results/cooldown-prevents-repeated-noise.json)

## 3. Risky Cleanup

Question: if the agent is about to run a destructive command, should the harness
intervene even without failed tests?

Expected result:

- inject `unsafe_change`.
- include the risky command as evidence.

Result file: [../results/risky-cleanup.json](../results/risky-cleanup.json)

## Interpretation

Decision-time guidance is useful only if it behaves like a controller, not a
second prompt file. These experiments check that the controller has a few basic
properties:

- it is evidence-driven.
- it can prioritize.
- it can stay quiet.
- it can treat destructive actions differently from ordinary debugging drift.

