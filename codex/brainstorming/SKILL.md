---
name: brainstorming
description: "Transforms ideas into validated designs before any implementation begins. Hard-gates all code writing until a design is approved. Use when starting any new project, feature, or significant change. Triggers: \"let's plan this\", \"I want to build\", \"design this feature\", \"let's think through\", or any new feature request before coding starts."
---

# Brainstorming

Hard-gates all implementation until a design is presented and approved by the user. Applies to every project, regardless of perceived simplicity — "simple" projects often hide the most dangerous unexamined assumptions.

**Core mandate:** Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it.

**Announce at start:** "I'm using the brainstorming skill to design this before implementation."

---

## The Five-Step Process

### Step 1: Explore Context

Before asking questions, read existing files, docs, configs, and package manifests to understand the current project landscape. Do not ask questions whose answers are discoverable by reading the code.

### Step 2: Ask Clarifying Questions

Ask **one question per message** — never multiple at once.

- Prefer multiple-choice questions over open-ended queries
- Uncover: purpose, constraints, scale, integrations, non-functional requirements
- Continue until you have enough clarity to propose concrete approaches

### Step 3: Propose 2-3 Approaches

For each approach, provide:
- What it does (one-sentence summary)
- Key trade-offs: complexity, performance, maintainability, reversibility
- Clear recommendation with reasoning

Do not proceed until the user selects an approach or requests modifications.

### Step 4: Present Design for Approval (Incrementally)

Present the design in appropriately-scaled sections, gaining approval section by section:

- **Small feature:** One design block, one approval
- **Large system:** Present each major section, confirm before continuing
- Revise any section if the user pushes back — do not treat initial approval as final

### Step 5: Document and Hand Off

After full approval:
1. Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
2. Announce: "Design approved and saved. Invoking writing-plans to create implementation tasks."
3. Invoke the `writing-plans` skill

---

## Critical Rules

**Always required — no exceptions:**
- Every project goes through this process, regardless of perceived simplicity
- One question per message only
- No code, no scaffolding, no file creation until design is fully approved
- After brainstorming completes, invoke **only** `writing-plans` — not any implementation skill directly

**The anti-pattern to eliminate:**
> "This is a small change, I'll just start coding."

These are exactly the cases where unexamined assumptions cause rework. The process is fast for simple things; skipping it is slow.

---

## Integration

**Leads to:** `writing-plans` — always invoke after design approval
**Never invoke directly:** Any code-writing skill until design is approved

---

*Based on obra/superpowers — https://github.com/obra/superpowers*
