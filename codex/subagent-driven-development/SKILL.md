---
name: subagent-driven-development
description: "Executes an implementation plan by dispatching a fresh subagent per task with two-stage review (spec compliance then code quality) after each. Produces high-quality, reviewed code with fast iteration inside the current session. Use when you have a written plan with mostly independent tasks. Triggers: \"execute the plan with subagents\", \"run subagent-driven dev\", or when writing-plans hands off after plan creation."
---

# Subagent-Driven Development

Execute a plan by dispatching a fresh subagent per task, followed by two-stage review after each task.

**Core principle:** Fresh subagent per task + two-stage review (spec compliance → code quality) = high quality, fast iteration.

**Announce at start:** "I'm using the subagent-driven-development skill to execute this plan."

---

## When to Use

Use when you have a written plan and:
- Tasks are mostly independent (can be done in isolation)
- You want to stay in the current session
- You want automatic review checkpoints after every task

**Use `executing-plans` instead when:**
- Tasks are tightly coupled (each task depends heavily on the previous)
- You want human review between every batch
- You prefer a separate session with explicit checkpoints

---

## The Process

### Setup
1. Read the plan file
2. Extract all tasks into TodoWrite (mark them all `pending`)
3. Identify any questions before starting — resolve them with the user now

### Per-Task Loop

For each task, execute this sequence **in order**:

**Step 1 — Dispatch Implementer Subagent**
- Provide the full task text (do not give just a file path to read)
- Answer any clarifying questions the subagent asks
- Let the subagent: implement → run tests → commit → self-review

**Step 2 — Dispatch Spec Compliance Reviewer Subagent**
- Verify implementation matches plan requirements exactly
- If gaps found → dispatch implementer to fix → reviewer reviews again
- Repeat until spec compliance passes

**Step 3 — Dispatch Code Quality Reviewer Subagent**
- Check: DRY, YAGNI, error handling, type safety, code clarity
- If issues found → dispatch implementer to fix → reviewer reviews again
- Repeat until quality passes

**Step 4 — Mark Complete**
- Mark task as `completed` in TodoWrite
- Proceed to next task

### Completion

After all tasks are complete:
1. Dispatch a final overall code reviewer
2. Invoke `finishing-a-development-branch`

---

## Advantages Over Manual Execution

| Aspect | Manual | Subagent-Driven |
|---|---|---|
| Context | Accumulates across tasks → confusion | Fresh context per task → clarity |
| Review | Often skipped under time pressure | Automatic after every task |
| Questions | Discovered mid-task | Surfaced before work begins |
| Quality gate | End-of-PR review | Two-stage per-task review |

---

## Red Flags — Never Do These

- Start implementation on main/master without explicit user consent
- Skip spec compliance review before code quality review (order matters)
- Dispatch multiple implementation subagents in parallel
- Proceed with unfixed Critical or Important issues from any reviewer
- Pass a plan file *path* to subagents — always provide the **full task text**
- Skip subagent questions — answer them completely before implementation continues
- Accept a "partial pass" from a reviewer — fix loop until fully resolved

---

## Integration

**Requires:**
- `writing-plans` — creates the plan this skill executes
- `requesting-code-review` — drives the reviewer subagent dispatches
- `finishing-a-development-branch` — completion workflow after all tasks

**Subagents should use:** `test-driven-development`

**Alternative:** `executing-plans` for batch execution with human checkpoints

---

*Based on obra/superpowers — https://github.com/obra/superpowers*
