# References

This repository prefers engineering-team sources over vendor marketing pages.
A reference is useful here when it explains a shipped system, an operational
constraint, or a concrete control loop.

## Primary Source

### Replit: Decision-Time Guidance

Source: <https://replit.com/blog/decision-time-guidance>

Why it matters here: the post describes a control layer that watches an agent's
trajectory and injects short guidance at the moment it is likely to help. That
maps directly to [Decision-Time Guidance](patterns/01-decision-time-guidance/README.md).

## Source Standard

Accepted sources:

- Engineering blogs from product teams.
- Technical architecture posts for shipped products.
- Incident writeups that reveal control-system requirements.
- Papers only when they connect to an implementation pattern.

Rejected sources:

- Generic vendor landing pages.
- Prompt packs.
- "Top 100 AI agents" lists.
- Posts that claim autonomy without showing verification, rollback, or control.
