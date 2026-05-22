---
name: prd-writer
description: Write a concise, actionable Product Requirements Document (PRD) with structured problem framing, success metrics, scope boundaries, and implementation notes — ready for engineering handoff.
---

# PRD Writer

Generate a production-ready PRD for a feature or epic. Scope is negotiated upfront; output is saved to a file.

## Activation

When asked to write a PRD, first clarify:

**A. What is the feature/epic?** (1–2 sentence description)

**B. Scope level:**
- (a) Single feature / user story
- (b) Epic / multi-feature initiative
- (c) Product area overhaul

**C. What triggered this?** (user research, exec request, metric drop, competitive move)

**D. Do you have existing research?** (customer quotes, analytics, support tickets)

**E. Who are the primary stakeholders?** (PM, Engineering, Design, Legal, etc.)

Collect answers, then generate the PRD below.

---

## PRD Template

Save output to: `docs/prd/[feature-name]-prd.md`

```markdown
# PRD: [Feature Name]
**Status**: Draft | In Review | Approved | Shipped
**Author**: [Name]
**Date**: [YYYY-MM-DD]
**Stakeholders**: [PM, Eng Lead, Designer, ...]

---

## 1. Problem Statement

### What problem are we solving?
[1–3 sentences. State the customer pain in concrete terms, ideally using a customer quote.]

### Who has this problem?
[Reference persona(s) or customer segment. Link to persona doc if available.]

### Evidence of problem severity
- **Frequency**: [How often does this occur?]
- **Impact**: [What happens when it occurs?]
- **Current workaround**: [What do customers do today?]
- **Source**: [Interview notes / support tickets / analytics — link if possible]

---

## 2. Goals and Success Metrics

### Desired outcome
[The behavior change or business metric this feature should move.]

### Success metrics (OKR format)
| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| [Primary metric] | [Current value] | [Goal] | [Date] |
| [Secondary metric] | [Current value] | [Goal] | [Date] |

### Non-goals / out of scope
- [Explicitly list what this PRD does NOT address]
- [This prevents scope creep and clarifies tradeoffs]

---

## 3. User Stories

Format: **As a** [persona], **I want to** [action], **so that** [outcome].

Acceptance criteria: **Given** [context], **When** [action], **Then** [result].

| # | User Story | Acceptance Criteria | Priority |
|---|------------|---------------------|----------|
| 1 | As a [persona], I want to... | Given... When... Then... | Must / Should / Could |
| 2 | | | |

---

## 4. Proposed Solution

### Approach
[High-level description of what we're building. Not a technical spec — a product-level description.]

### Key design decisions
- [Decision 1]: [Why this approach over alternatives]
- [Decision 2]: [Tradeoff made]

### Prototype / mockup
[Link to Figma, screenshots, or description. "TBD" is acceptable at Draft stage.]

---

## 5. Scope and Phasing

### MVP (required for launch)
- [ ] [Capability 1]
- [ ] [Capability 2]

### Phase 2 (post-launch)
- [ ] [Capability 3]
- [ ] [Capability 4]

### Explicitly deferred
- [Item that was discussed but intentionally cut — with reason]

---

## 6. Risks and Assumptions

| Risk / Assumption | Likelihood | Impact | Mitigation |
|-------------------|-----------|--------|------------|
| [Assumption we're making] | H/M/L | H/M/L | [Test / monitor / accept] |
| [Technical risk] | H/M/L | H/M/L | [Spike / fallback] |

---

## 7. Dependencies and Constraints

- **Depends on**: [Other teams, APIs, infrastructure, legal review]
- **Blocks**: [What this PRD unblocks downstream]
- **Constraints**: [Compliance, platform limits, timelines]

---

## 8. Open Questions

| Question | Owner | Due | Status |
|----------|-------|-----|--------|
| [Unresolved question] | [Name] | [Date] | Open |

---

## Appendix
- Links to research, customer interviews, competitor analysis
- Related PRDs, design files, technical docs
```

---

## PRD Quality Checklist

Before marking "In Review":

- [ ] Problem statement includes customer evidence (quote, data, or both)
- [ ] Success metrics are measurable and have a baseline
- [ ] Non-goals explicitly list at least 3 things out of scope
- [ ] User stories follow Given/When/Then format
- [ ] Risks table is filled — never left blank
- [ ] Open questions have owners and due dates

## Sources
- snarktank/ralph SKILL.md
- github/awesome-copilot SKILL.md
- phuryn/pm-skills create-prd
