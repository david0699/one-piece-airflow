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

## DEC-003 - Keep Spark/Hive Business Logic Outside Airflow Repo

- Date: 2026-05-25
- Status: accepted
- Scope: architecture

### Context
The Airflow repository should focus on orchestration and avoid duplicating Spark or Hive processing code that belongs to the Scala/Spark project.

### Decision
Do not implement Spark or Hive business logic in this repository. Airflow DAGs may only orchestrate external jobs (for example, invoking a JAR with runtime args) and define workflow dependencies, retries, and schedules.

### Consequences
Spark/Hive transformation and DDL logic is maintained in the dedicated Scala/Spark repository. This repo keeps thinner DAGs, lower coupling, and smaller review surface for orchestration-only changes.

## DEC-004 - One DAG Definition Per File for Scalability

- Date: 2026-05-25
- Status: accepted
- Scope: coding-conventions

### Context
As orchestration grows, combining multiple DAG definitions in a single file reduces clarity and makes ownership, review, and change history harder to manage.

### Decision
Keep one production DAG definition per file in `dags/`. Related DAGs may share naming conventions and runtime variables, but each DAG should live in its own module.

### Consequences
DAG discovery and maintenance are clearer, review diffs stay focused, and repository scaling is simpler as orchestration flows increase.

## DEC-005 - Use XCom for Small Inter-Task Data Exchange

- Date: 2026-05-25
- Status: accepted
- Scope: coding-conventions

### Context
Airflow tasks in this project need to share small runtime control data (for example, table lists, flags, and branch inputs) while keeping orchestration explicit and maintainable.

### Decision
Use XCom as the default mechanism to share small data between tasks. Keep payloads lightweight (for example, identifiers, lists of names, booleans, and short metadata) and do not use XCom for large datasets or full API payloads.

### Consequences
Task contracts remain explicit and easy to test, branching logic is clearer, and scheduler/database pressure is reduced by avoiding large XCom payloads.
