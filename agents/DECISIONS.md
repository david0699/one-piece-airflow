# DECISIONS

This file is the Architecture Decision Record (ADR) log for architecture, coding conventions, and workflow choices in this repository.

## Governance

- Decision IDs are immutable and unique (`DEC-###`).
- Every significant change must reference one or more decision IDs.
- Only the project owner (user) can supersede a decision.
- Existing decisions are not edited for meaning changes; add a new ADR with `Status: superseded` or `Status: accepted` and reference the prior ID.
- Allowed statuses: `proposed`, `accepted`, `deprecated`, `superseded`.

## ADR Template

Use this template for new records:

```md
## DEC-XXX - <Title>

- Date: YYYY-MM-DD
- Status: proposed|accepted|deprecated|superseded
- Scope: architecture|coding-conventions|workflow
- Supersedes: DEC-YYY (optional)

### Context
<Why this is needed>

### Decision
<Decision statement>

### Consequences
<Tradeoffs, constraints, follow-up implications>
```

## Pending Non-Negotiables

- Additional non-negotiables: pending to complete by project owner.

## Decision Log

## DEC-001 - No Push Without Owner Approval

- Date: 2026-05-24
- Status: accepted
- Scope: workflow

### Context
Direct pushes can bypass review and create unapproved repository state changes.

### Decision
Never push to any remote repository without explicit approval from the project owner for that specific push action.

### Consequences
All push operations require a prior approval checkpoint in the current thread. Work can proceed locally with commits and branches, but remote updates are blocked until approved.

## DEC-002 - No Rebase Without Owner Approval

- Date: 2026-05-24
- Status: accepted
- Scope: workflow

### Context
Rebase rewrites commit history and can change review references and branch semantics.

### Decision
Never run `git rebase` (interactive or non-interactive) without explicit approval from the project owner for that specific rebase action.

### Consequences
History-rewriting operations are blocked by default. Prefer non-rewriting alternatives unless owner approval is granted.
