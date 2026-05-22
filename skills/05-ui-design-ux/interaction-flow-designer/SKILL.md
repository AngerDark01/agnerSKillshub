---
name: interaction-flow-designer
description: "Maps and designs user interaction flows, page state machines, and navigation architectures for web applications. Use when designing multi-step forms, onboarding flows, wizard UIs, modal stacks, or any feature requiring explicit state transitions. Triggers: \"design the user flow\", \"map out the interaction\", \"state machine for this feature\", \"how should users navigate\", \"design the UX flow\"."
---

# Interaction Flow Designer

Maps user journeys into explicit state machines and actionable UI specifications. Prevents the most common UX failure: building screens without first understanding how users move between them.

**Announce at start:** "I'm using the interaction-flow-designer skill."

---

## When to Use

- Designing new features with multiple steps or states
- Onboarding flows, checkout funnels, wizard UIs
- Modal/drawer/sheet stacks with complex dismiss logic
- Any flow where "what happens next" is non-trivial
- Auditing confusing existing navigation

---

## The Process

### Phase 1: Discover the Flow Shape

Ask (one at a time until clear):
- **Entry points:** How do users arrive here? (direct URL, button click, notification, redirect after action)
- **Exit points:** Where do they go when done, cancelled, or errored?
- **User intent:** What is the user trying to accomplish? What's their mental model?
- **Branching conditions:** What decisions affect which path they take? (role, state, data availability)
- **Error states:** What happens when something fails at each step?

### Phase 2: Define States and Transitions

Model the flow as a finite state machine:

```
States (exhaustive list):
  idle | loading | step-1 | step-2 | ... | success | error | cancelled

Transitions (event → new state):
  SUBMIT_STEP_1 → (validation passes) → step-2
  SUBMIT_STEP_1 → (validation fails) → step-1 [with error context]
  BACK → step-1
  CANCEL → cancelled → [navigation target]
  NETWORK_ERROR → error [with retry available]
```

Document every state. If a state is missing, it will become a bug.

### Phase 3: Produce Deliverables

**A. ASCII Flow Diagram**

```
[Entry: Click "Sign Up"]
        │
        ▼
┌─────────────┐   SUBMIT + valid    ┌─────────────┐
│   Step 1    │ ──────────────────► │   Step 2    │
│  Email+Pass │ ◄──────────────────  │  Profile   │
└─────────────┘   BACK              └─────────────┘
       │                                    │
       │ SUBMIT + invalid                   │ SUBMIT
       ▼                                    ▼
  [Inline errors]                    ┌─────────────┐
                                     │   Success   │
                                     │  → Dashboard│
                                     └─────────────┘
```

**B. State Inventory Table**

| State | User sees | Available actions | Guards / conditions |
|---|---|---|---|
| step-1 | Email + password fields | Submit, Cancel | Email valid format, password ≥ 8 chars |
| step-2 | Profile fields | Submit, Back | Name required |
| loading | Spinner, disabled inputs | None | - |
| success | Confirmation + CTA | Go to dashboard | - |
| error | Error message + retry | Retry, Cancel | - |

**C. Component Boundary Recommendations**

List which states map to which components, and what props/state each component needs.

**D. Edge Case Inventory**

Explicitly enumerate:
- What happens if user navigates back via browser?
- What if session expires mid-flow?
- What if network drops between steps?
- What if user opens flow in two tabs?

### Phase 4: Implementation Handoff

Output a specification section an engineer can implement directly:
- State type definitions (TypeScript union types)
- Event type definitions
- Recommended state management approach (local useState, useReducer, XState, Zustand, etc.)
- Data that must persist across steps

---

## Output Format

Always produce:
1. ASCII flow diagram (visual overview)
2. Complete state inventory table
3. Edge case list
4. Implementation spec (types + state management recommendation)

---

## Principles

**Make implicit states explicit.** "Loading" is a state. "Error" is a state. "Empty" is a state. Draw them all.

**Flows should be deterministic.** From any state, every possible user action leads to exactly one next state. If you can't say where an action leads, that's a design gap.

**Design for abandonment.** Users leave flows. Document what happens to their data and where they land if they exit at any step.

---

*Sources: UX state machine patterns, finite automata theory applied to UI*
