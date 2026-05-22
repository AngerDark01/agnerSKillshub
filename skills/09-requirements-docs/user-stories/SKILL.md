---
name: user-stories
description: Write high-quality user stories using INVEST criteria and Given/When/Then acceptance criteria — breaking down features into independently deliverable, testable increments.
---

# User Stories

Write user stories that are independently deliverable, testable, and grounded in real user needs.

## The INVEST Criteria

Every good user story must be:

| Criterion | Meaning | Test question |
|-----------|---------|---------------|
| **I**ndependent | Deliverable without requiring another story | "Can we ship this alone?" |
| **N**egotiable | Not a contract — open to discussion | "Can the team change how to achieve the goal?" |
| **V**aluable | Delivers value to a user or business | "Who benefits and how?" |
| **E**stimable | Team can size it | "Can engineering estimate this?" |
| **S**mall | Fits in one sprint | "Could one engineer deliver this in ≤5 days?" |
| **T**estable | Has clear acceptance criteria | "Can QA write a test for this?" |

## User Story Format

```
As a [specific persona / role],
I want to [action / capability],
so that [outcome / value received].
```

**Example:**
> As a **first-time visitor**,
> I want to **see a product demo without signing up**,
> so that I can **evaluate whether it solves my problem before committing**.

## Acceptance Criteria (Given/When/Then)

Each story needs ≥1 acceptance criterion:

```
Given [initial context / precondition],
When [user takes action / event occurs],
Then [expected result / observable outcome].
```

**Example:**
> Given the user is on the pricing page and is not logged in,
> When they click "Watch Demo",
> Then they see a 2-min video without a signup prompt.

## Story Splitting Techniques

When a story is too large, split using these patterns:

| Pattern | Example |
|---------|---------|
| **By workflow step** | "Upload file" → "Select file" + "Preview before upload" + "Confirm upload" |
| **By user type** | "User edits profile" → "Admin edits any profile" + "User edits own profile" |
| **By data variation** | "Export report" → "Export as CSV" + "Export as PDF" |
| **By happy path first** | "Pay for order" → "Pay with credit card (happy path)" + "Handle payment failure" |
| **By performance** | "Load dashboard" → "Load dashboard (basic)" + "Load dashboard (<1s)" |
| **By optional feature** | Core + nice-to-have separated into two stories |

## Epic → Feature → Story Hierarchy

```
Epic: [Large initiative — 1–6 months]
  └─ Feature: [Meaningful capability — 1–4 weeks]
       └─ Story: [Single deliverable — 1–5 days]
            └─ Task: [Dev sub-task — hours]
```

**Epics** express business goals. Never write acceptance criteria for epics.
**Features** bundle related stories. May have a feature-level definition of done.
**Stories** are the unit of sprint planning and delivery.

## Story Writing Process

1. **Start with the job**: What job is the user trying to do? (JTBD)
2. **Write the story**: Fill in the As a / I want / So that format
3. **Check INVEST**: Validate all six criteria
4. **Write ACs**: 2–5 Given/When/Then scenarios per story
5. **Add edge cases**: At least one failure or error path AC
6. **Size check**: If >5 days, apply a splitting technique

## Story Card Template

```markdown
## Story: [Short title]
**ID**: [Prefix-###]
**Epic**: [Parent epic]
**Priority**: Must / Should / Could / Won't

### User Story
As a [persona], I want to [action], so that [outcome].

### Acceptance Criteria
- [ ] Given [context], When [action], Then [result]
- [ ] Given [error state], When [action], Then [graceful outcome]

### Notes / Constraints
- [Any tech constraint, design note, or dependency]
- [Link to mockup, API spec, or related story]

### Definition of Done
- [ ] AC all passing
- [ ] Unit tests written
- [ ] Accessibility checked (WCAG 2.1 AA)
- [ ] Reviewed and merged to main
```

## Common Anti-Patterns

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| "As a user, I want a dashboard" | No specific persona, no clear value | Identify who and what job they need done |
| AC with "should" / "could" | Ambiguous — is it required or optional? | Use "shall" for required, split into separate story for optional |
| Story with no AC | Nothing to test, nothing is done | Always write ≥1 AC before a story enters a sprint |
| Technical story with no user value | "Add Redis caching" | Frame as: "As a user, I want search results in <1s..." |
| Mega-story (>2 weeks) | Unpredictable delivery | Apply splitting techniques |

## Sources
- phuryn/pm-skills user-stories (open source)
- deanpeters/Product-Manager-Skills (CC BY-NC-SA 4.0)
