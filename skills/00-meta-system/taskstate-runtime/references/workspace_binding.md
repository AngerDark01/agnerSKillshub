# Workspace Binding

TaskState resolves the workspace in this order:

1. Explicit `--workspace <path>`.
2. Current directory upward search for `.taskstate/task_state.json`.
3. `TASKSTATE_WORKSPACE` environment variable as fallback only.

`TASKSTATE_WORKSPACE` must not override a real workspace found from the current
directory. If the user opens another project with its own
`.taskstate/task_state.json`, bind to that project.

Verify binding before reading or changing state:

```bash
taskstate where
```

If the state file is missing, the current directory is not initialized. Starting
the monitor auto-initializes the current directory:

```bash
taskstate
```

Auto-initialization only creates a workspace and default placeholder state. It
does not mean the real task skeleton has been confirmed. For a new or vague
task, clarify the task with the user and confirm the top-level phases before
adding execution subtasks.

For explicit initialization, run:

```bash
taskstate init-here --task-id <task_id>
```

Standard workspace layout:

```text
<workspace>/
  .taskstate/task_state.json
  input/files/
  work/
  output/
  logs/
```

Use explicit `--workspace` for cross-project operations.
