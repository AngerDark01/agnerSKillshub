---
name: lean-ux
description: Apply Jeff Gothelf's Lean UX — declare assumptions, form hypothesis statements, build the smallest experiment to test them, and integrate discovery into dual-track Agile sprints.
---

# Lean UX — Hypothesis-Driven Design

Apply Lean UX principles to reduce waste, validate assumptions early, and integrate design learning into Agile delivery.

## Core Mindset Shift

| Traditional UX | Lean UX |
|----------------|---------|
| Design → Build → Measure | Assume → Hypothesize → Test → Learn |
| Deliverable is a spec | Deliverable is shared understanding |
| Designer owns the design | Team owns the outcome |
| Big design up front | Minimum viable experiment |
| Success = shipped feature | Success = validated learning or pivot |

## Step 1: Declare Assumptions

Before any design work, surface the team's beliefs. Run an **Assumption Mapping Workshop** (30–60 min):

**Prompt the team:**
- "We believe our customers want..."
- "We believe the biggest risk is..."
- "We believe [feature] will cause users to..."
- "We assume users already know how to..."

**Classify each assumption:**

```
              HIGH RISK (wrong = project fails)
                        │
         ┌──────────────┼──────────────┐
         │              │              │
  LOW    │   TEST FIRST │   TEST NOW   │  HIGH
UNKNOWN  ├──────────────┼──────────────┤ UNKNOWN
         │   MONITOR    │   WATCH      │
         │              │              │
         └──────────────┼──────────────┘
                        │
              LOW RISK
```

Focus all experimentation on the top-right quadrant.

## Step 2: Form Hypothesis Statements

Convert each risky assumption into a testable hypothesis:

```
We believe [doing / building / creating this]
for [these customers / users]
will achieve [this outcome / result].

We will know this is true when we see
[this measurable signal / criterion].
```

**Example:**
> We believe adding a progress indicator to onboarding
> for new users completing their first project
> will increase completion rates.
>
> We will know this is true when we see
> 7-day activation rate increase by ≥15%.

One hypothesis per experiment. Resist bundling multiple changes.

## Step 3: Design the Minimum Viable Experiment

Choose the cheapest test that could invalidate the hypothesis:

| Fidelity | Method | Ideal for | Time |
|----------|--------|-----------|------|
| Paper | Paper prototype test | Concept / flow | 1–2 days |
| Digital mockup | Figma clickthrough | UI/interaction | 2–5 days |
| Wizard of Oz | Manual backend, real UI | Complex features | 3–7 days |
| Concierge | Do manually what software would do | New service/workflow | 1–2 weeks |
| A/B test | Live traffic split | Copy, CTA, layout | 1–4 weeks |
| Fake door | CTA that captures interest (no real feature) | Demand validation | 1–3 days |

**Selection rule**: Use the lowest fidelity that can produce a clear signal.

## Step 4: Run Design Studios (Collaborative Design)

Replace "designer presents options" with **collaborative sketching**:

1. **Problem framing** (5 min): State the problem and constraints
2. **Individual sketching** (5–8 min): Everyone sketches 6–8 ideas silently
3. **Present and critique** (2 min/person): No defending — only questions
4. **Dot voting** (5 min): Everyone votes on strongest ideas
5. **Consolidate** (10 min): Combine best elements into shared direction

Participants: PM + Designer + 2–3 Engineers + 1 stakeholder.
Output: Rough sketches → shared direction → prototype brief.

## Step 5: Integrate with Agile

**Dual-track structure:**

```
Week 1          Week 2          Week 3
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Discovery  │  │ Discovery  │  │ Discovery  │
│ Sprint     │  │ Sprint     │  │ Sprint     │
│ (validate) │  │ (validate) │  │ (validate) │
├────────────┤  ├────────────┤  ├────────────┤
│ Delivery   │  │ Delivery   │  │ Delivery   │
│ Sprint     │  │ Sprint     │  │ Sprint     │
│ (build)    │  │ (build)    │  │ (build)    │
└────────────┘  └────────────┘  └────────────┘
```

**Rule**: Only items that have been through discovery (hypothesis + ≥1 experiment) enter the delivery sprint backlog.

## Lean UX Canvas

Use this as a single-page team alignment artifact:

```
┌─────────────────┬─────────────────┬─────────────────┐
│  Business       │  Users &         │  User           │
│  Problem        │  Customers       │  Outcomes &     │
│                 │                  │  Benefits       │
├─────────────────┼─────────────────┼─────────────────┤
│  Solutions      │  Hypotheses      │  What's the     │
│  (ideas, not    │  (risky          │  most important │
│   decisions)    │   assumptions)   │  thing to learn?│
├─────────────────┼─────────────────┼─────────────────┤
│  Minimum Viable │  Learning        │  Business       │
│  Experiment     │  Metrics         │  Outcomes       │
└─────────────────┴─────────────────┴─────────────────┘
```

## Deliverables

- [ ] Assumption log (classified by risk/unknown)
- [ ] Hypothesis statements (one per experiment)
- [ ] Experiment design brief (method, success criteria, timeline)
- [ ] Design studio sketches
- [ ] Learning summary after each experiment

## Sources
- Jeff Gothelf & Josh Seiden, *Lean UX* (3rd ed., 2021)
- wondelai/skills (MIT License)
