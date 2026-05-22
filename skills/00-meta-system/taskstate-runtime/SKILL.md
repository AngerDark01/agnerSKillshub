---
name: taskstate-runtime
description: >
  Use this skill first, before domain-specific skills, for any complex task
  that needs task planning, any long-running task, or any broad or multi-phase
  task that needs progress control, deliverables, review, or phase transitions.
  This includes reading or mapping a codebase, onboarding to a project,
  architecture audits, debugging plans, document generation, implementation
  plans, research projects, and any task that will create CODEBASE.md,
  ITERATION_LOG.md, reports, staged outputs, or review checkpoints. Also use it
  for creating or resuming a .taskstate workspace, showing task status,
  clarifying vague tasks, drafting a top-level phase skeleton, creating
  subtasks, submitting deliverables, reviewing deliverables, or advancing
  phases. This skill explains how agents should use the CLI and collaborate
  with the user; it does not contain business rules for any specific domain.
---

# TaskState Runtime

TaskState is the formal task controller. It is stricter than a todo list:
phases, subtasks, deliverables, reviews, and phase transitions must go through
the `taskstate` CLI.

Treat `.taskstate/task_state.json` as the CLI's private persistence file. Do
not edit it directly during normal work.

Default mode is human-in-the-loop. Use TaskState to make task boundaries visible,
confirm important changes with the user, then execute and deliver.

Workspace initialization is not the same as task definition. Auto-initializing a
workspace only creates a place to store task state. It does not mean the task
phases, deliverables, or review rules are already correct.

## Precedence

TaskState is the outer task controller. If a user asks for a complex task that
needs planning, a long-running task, a broad project reading, codebase mapping,
onboarding pass, architecture scan, staged debugging plan, report, or other
multi-phase investigation, run `taskstate where` before loading or executing the
domain-specific skill. Use domain skills inside the current TaskState phase
after the workspace and phase skeleton are clear.

## Workspace Binding

Before reading or changing state, verify the bound workspace:

```bash
taskstate where
```

Workspace resolution order:

1. explicit `--workspace <path>`
2. current directory upward search for `.taskstate/task_state.json`
3. `TASKSTATE_WORKSPACE` fallback only

When the user starts the monitor with `taskstate` or `taskstate tui`, the CLI
auto-initializes the current directory if no local state exists. For explicit
template-based initialization, still use `taskstate init` or `taskstate
init-here`.

For details, read `references/workspace_binding.md`.

## Read State

Use these commands to inspect state:

```bash
taskstate panel
taskstate show
taskstate show --full
taskstate phase
taskstate task --task-id <task_id>
taskstate actions
taskstate tui
```

Use `panel` for compact agent context. Use `show` when the user needs to review
the task state. Use `show --full` when the user needs all human-readable state,
including event log, action payloads, deliverable checks, notes, and task
results. Use `tui` when the user wants a live monitor.

## Framing Before Task Creation

For a new or vague task, do not immediately create execution subtasks after
workspace initialization. First clarify the task with the user.

Framing steps:

1. Read the user's goal and inspect obvious local context.
2. If the task belongs to a specific domain, load the relevant domain skill
   before designing the TaskState.
3. If the task depends on current facts, markets, tools, policies, prices, or
   external options, do the required web research before proposing the task
   skeleton.
4. Propose a simple top-level skeleton: phases, each phase goal, final
   deliverables, and review rules.
5. Ask the user to confirm the skeleton and the execution mode.
6. Only after confirmation, write the skeleton into TaskState.

Keep the skeleton concise. Use plain language. Do not create a large task tree
before the user confirms the top-level direction.

If `taskstate` auto-created the default initial/execution state and it is only a
placeholder, replace it with the confirmed template using `taskstate init
--config <template.yaml> --workspace <workspace> --task-id <task_id>
--overwrite`. Do not overwrite a state that already contains user-approved work
without explicit confirmation.

## Execution Modes

After the top-level skeleton is confirmed, choose one mode with the user:

- Phase-by-phase collaboration: define only the current phase in detail, execute
  it, review it, advance, then discuss the next phase. Use this for exploratory,
  ambiguous, research, product, or planning work.
- Full-chain autonomous execution: define all phases, subtasks, deliverables,
  dependencies, and review rules up front, then execute through TaskState. Use
  this only when the process is stable and the user explicitly approves
  autonomous execution.

In both modes, locked phases are not executable. A later phase can be shown as a
name/status skeleton, but detailed work waits until the state machine unlocks it.

## Write State

Use CLI actions for normal edits:

```bash
taskstate add-task --task-id <task_id> --name "<name>" --goal "<goal>"
taskstate add-task --parent-task-id <parent_id> --task-id <task_id> --name "<name>"
taskstate add-deliverable --task-id <task_id> --name "<name>" --workspace-path <path>
taskstate add-review-rule --task-id <task_id> --rule "<rule>"
taskstate set-task-status --task-id <task_id> --status running|blocked|done
taskstate submit --task-id <task_id> --workspace-path <path>
taskstate review --task-id <task_id> --workspace-path <path> --approved
taskstate complete-phase
```

Use `add-subtasks --file` or `propose-change --file` only for batch or complex
changes. Put temporary operation files under `work/taskstate_ops/`.

## Collaboration Rules

- Do not assume workspace from chat history; run `taskstate where`.
- Do not directly edit `.taskstate/task_state.json`.
- Auto-initialized workspace state is only a placeholder until the user confirms
  the task skeleton.
- Before creating or replacing a TaskState, clarify the task and ask the user to
  confirm top-level phases, final deliverables, review rules, and execution
  mode.
- Only work on the current visible phase. Locked phases are not executable.
- Treat user ideas during execution as potential TaskState changes. Discuss the
  implication first, then write the confirmed change through CLI actions.
- If the current phase has no subtasks, draft scoped subtasks and ask the user
  to confirm the execution boundary before substantial work.
- If an assigned task is still too broad, decompose it under its parent.
- A child task must be narrower than its parent.
- Use dependencies for serial work and `execution_mode: async` for independent
  work that can run in parallel.
- A phase can complete only after required subtasks are done and required
  deliverables pass mechanical check plus content review.
- Use normal todos only as scratch notes. They never replace TaskState.

## Start Or Resume

1. Run `taskstate where`.
2. If state exists, run `taskstate show`.
3. If state is missing and the user wants to start the monitor, run
   `taskstate`; it will initialize the current directory automatically.
4. If this is a new or placeholder state, clarify the task with the user before
   adding subtasks.
5. Propose and confirm the top-level phase skeleton.
6. Write the confirmed skeleton into TaskState, then use `taskstate panel` to
   decide the next action.
7. Show the user important state changes after writing them.

## Human Confirmation Points

Ask for confirmation when:

- initializing a new TaskState
- replacing an auto-initialized placeholder with the confirmed task skeleton
- choosing phase-by-phase collaboration or full-chain autonomous execution
- decomposing a broad phase into subtasks
- changing deliverables, review rules, priority, or scope
- reviewing a phase final deliverable
- advancing to the next phase

Keep confirmation concise: show what changed, what is blocked, and the next
action.
