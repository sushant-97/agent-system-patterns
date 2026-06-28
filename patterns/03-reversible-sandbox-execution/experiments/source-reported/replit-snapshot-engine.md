# Source-Reported: Replit Snapshot Engine

Source: <https://replit.com/blog/inside-replits-snapshot-engine>

This file tracks source-reported ideas and results. It does not copy Replit's
internal implementation, data, or diagrams.

## What Replit Reports

Replit describes a snapshot engine used to support agent workflows. The useful
engineering idea is that an agent can explore and modify a project while the
platform preserves a recoverable boundary around the original state.

The post discusses checkpointing, isolation, rollback, and promotion as product
infrastructure, not just developer convenience.

## Source Figures

The post includes diagrams around snapshotting and state management. This repo
uses original reconstructions:

- [snapshot-fork-promote.svg](../../assets/snapshot-fork-promote.svg)
- [layered-state.svg](../../assets/layered-state.svg)

The diagram study is here:
[source-diagrams/README.md](../../source-diagrams/README.md).

## Result Reported By Source

The source describes snapshotting as infrastructure that makes agent workflows
safer and more recoverable. The central result is operational: agent-generated
changes can be attempted, inspected, reverted, or promoted without treating the
first attempt as canonical state.

## How This Repo Uses The Source

This repo adopts the control-system shape:

- create a checkpoint before the attempt.
- fork an isolated sandbox.
- let the agent modify the sandbox.
- compute an audit diff.
- verify invariants.
- promote only if merge policy passes.

## What We Do Not Claim

- We do not reproduce Replit's storage engine.
- We do not reproduce Replit's internal snapshot data model.
- We do not copy Replit's diagrams.
- Our experiments are synthetic and in-memory.

