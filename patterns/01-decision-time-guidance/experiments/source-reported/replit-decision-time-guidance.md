# Source-Reported: Replit Decision-Time Guidance

Source: <https://replit.com/blog/decision-time-guidance>

This file tracks claims and results reported by the source. It does not copy
Replit's internal implementation, data, or images.

## What Replit Reports

Replit describes decision-time guidance as a system that provides targeted
guidance during an agent run, instead of relying only on static prompt
instructions.

Their reported setup uses trajectory-aware classifiers to decide when specific
guidance should be injected. The important product-engineering point is that the
guidance is tied to the agent's current behavior, not blindly appended to every
turn.

## Result Reported By Source

The post reports that this approach improved their agent on targeted behaviors
without requiring a broad prompt rewrite. It also describes the operational
tradeoff: more reminders are not automatically better, because excessive
guidance can compete with the actual task context.

## How This Repo Uses The Source

This repo adopts the control-system shape, not the private implementation:

- observe trajectory events.
- classify known failure modes.
- inject short guidance cards.
- include evidence.
- enforce a card budget and cooldown.

## What We Do Not Claim

- We do not claim to reproduce Replit's classifiers.
- We do not claim to reproduce Replit's eval numbers.
- We do not copy Replit's diagrams or internal traces.
- Our hands-on traces are synthetic and exist to test our own implementation.

