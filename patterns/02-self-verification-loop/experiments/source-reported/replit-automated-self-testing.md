# Source-Reported: Replit Automated Self-Testing

Source: <https://replit.com/blog/automated-self-testing>

This file tracks source-reported ideas. It does not copy Replit's internal
implementation, data, or diagrams.

## What Replit Reports

Replit describes automated self-testing for coding agents: the agent can run and
interact with the app it is building, observe failures, and repair the result.

The relevant production idea is that agent completion should be grounded in
runtime evidence. A generated app that renders is not necessarily a working app.

## How This Repo Uses The Source

This repo adopts the control-system shape:

- define an executable scenario.
- run the candidate artifact.
- collect UI, state, and log evidence.
- reject shallow false positives.
- repair from failed evidence.
- rerun the same scenario.

## What We Do Not Claim

- We do not reproduce Replit's testing infrastructure.
- We do not reproduce Replit's internal agent behavior.
- We do not copy Replit's diagrams.
- Our experiments are synthetic and intentionally small.

