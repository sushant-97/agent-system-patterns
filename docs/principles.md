# Principles

This repo treats agent reliability as a control-systems problem.

The useful question is not "what prompt makes the agent smart?" The useful
question is:

```text
What boundary makes the agent's behavior observable, testable, and recoverable?
```

## 1. Controls Beat Vibes

A good pattern changes the system around the agent:

- what the harness observes
- what evidence it records
- what state the agent can mutate
- what conditions block promotion
- what happens after failure

Better wording can help. It is not enough.

## 2. Evidence Beats Claims

Agent output should be treated as a claim until a verifier captures evidence.

Evidence can be:

- runtime logs
- state diffs
- browser or API interactions
- failed checks
- merge-policy decisions
- audit records

## 3. Local Controls Beat Global Reminders

Long static prompts turn every reminder into a tax on every decision.

Some rules belong in the base prompt, especially security and permission
boundaries. But situational behavior should usually be handled at runtime:

- "you are looping"
- "the same error is still present"
- "this side effect is not reversible"
- "the UI passed but state did not change"

## 4. Reversibility Is A Product Feature

Agent autonomy is much easier to trust when attempts are isolated, diffed,
verified, and promoted deliberately.

Rollback is not a replacement for verification, but it is a necessary guardrail
for exploration.

