---
name: continuous-discovery
description: Run Teresa Torres's continuous discovery cadence — weekly customer touchpoints, Opportunity Solution Trees, and assumption testing — to ensure teams always build the right thing.
---

# Continuous Discovery — Weekly Discovery Cadence

Apply Teresa Torres's framework from *Continuous Discovery Habits* to make customer discovery a weekly team discipline, not a one-time research project.

## Core Principles

1. **Weekly touchpoints** with customers — not quarterly research sprints
2. **Outcome orientation** — teams chase outcomes (behavior change), not outputs (features)
3. **Assumption testing** — small experiments before building
4. **Collaborative discovery** — PM + Designer + Engineering together, not siloed research

## The Opportunity Solution Tree (OST)

The OST is the central artifact for organizing discovery work:

```
                    [Desired Outcome]
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    [Opportunity 1]  [Opportunity 2]  [Opportunity 3]
          │               │
    ┌─────┼─────┐    ┌────┼────┐
    ▼     ▼     ▼    ▼         ▼
  [Sol] [Sol] [Sol] [Sol]    [Sol]
    │
  [Assumption Tests]
```

- **Desired Outcome**: The measurable business/team metric to move
- **Opportunities**: Customer needs, pain points, desires (not solutions)
- **Solutions**: Ideas for addressing opportunities (features, copy, flow changes)
- **Assumption tests**: Cheapest way to test a solution's riskiest assumption

## Weekly Cadence Template

**Goal**: At minimum, one continuous interview per week per team.

### Weekly Discovery Meeting (60–90 min)

```
1. Interview debrief (15 min)
   - Who did we talk to?
   - What opportunities did we hear?
   - Any surprises or pattern breaks?

2. Update the OST (15 min)
   - Add new opportunities
   - Prune or reframe existing ones
   - Check: Are we targeting the right opportunity?

3. Solution exploration (20 min)
   - For the chosen opportunity: generate 3+ solution options
   - No premature convergence — explore widely first

4. Assumption mapping (20 min)
   - For candidate solutions: what must be true for this to work?
   - Which assumption is riskiest AND most testable?

5. Test design (15 min)
   - Design a test for the top assumption
   - Target: results available before next week's meeting
```

## Opportunity Mapping

When capturing opportunities from interviews, use this format:

```
Customer: [Name / segment]
Situation: [When / context]
Pain: [Exact words they used — quote when possible]
Frequency: [How often this comes up]
Severity: [How much it matters — 1–5 scale]
Current workaround: [What they do now]
```

**Anti-patterns:**
- Don't jump to solutions while mapping opportunities
- Don't merge different customers' pains into one "compound opportunity"
- Don't only interview customers who love you

## Assumption Mapping

For each candidate solution, map assumptions across two axes:

```
              HIGH RISK
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    │   TEST      │   TEST      │
    │   FIRST     │   NOW       │
    │             │             │
LOW ◄─────────────┼─────────────► HIGH
IMPORTANCE        │             IMPORTANCE
    │   DEPRIORI- │   MONITOR   │
    │   TIZE      │             │
    │             │             │
    └─────────────┼─────────────┘
                  │
              LOW RISK
```

**Test methods (cheapest to most expensive):**
1. Fake door / smoke test (landing page, mock CTA)
2. Concierge test (do manually what the feature would automate)
3. Prototype test (clickable mockup)
4. A/B test (live with real users)
5. Build an MVP

## Interview Recruitment

**Target**: At minimum one interview per week per team.

**Sourcing strategies:**
- End-of-session NPS prompt + offer to talk
- "Thank you" emails to churned users
- In-product banner ("Help us improve — 20-min call")
- Customer success team introductions
- Slack/Discord community posts

**Participant diversity check:**
- Power users (love the product)
- Moderate users (use occasionally)
- Churned users (left or stopped using)
- Non-users from target segment (never tried)

## OST Health Checks

Weekly, ask:
- [ ] Is our outcome still the right one? (Still aligned to business metric)
- [ ] Are we working on the right opportunity? (Evidence from ≥3 customers)
- [ ] Have we explored ≥3 solution options before picking one?
- [ ] Have we tested the riskiest assumption before writing code?
- [ ] Are all three (PM + Designer + Eng) involved in discovery?

## Sources
- Teresa Torres, *Continuous Discovery Habits* (2021)
- wondelai/skills (MIT License)
