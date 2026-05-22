---
name: feature-prioritization
description: Apply RICE, ICE, Kano, and MoSCoW frameworks to prioritize features objectively — score candidates, surface hidden assumptions, and build a defensible, outcome-linked backlog.
---

# Feature Prioritization

Apply structured prioritization frameworks to make defensible, data-driven feature sequencing decisions.

## When to Use Which Framework

| Framework | Best for | Input required |
|-----------|----------|---------------|
| **RICE** | Comparing many features with impact data | Reach, effort estimates |
| **ICE** | Rapid lightweight scoring | Team gut-check |
| **Kano** | Understanding must-haves vs. delighters | Customer survey |
| **MoSCoW** | Release scoping under constraint | Stakeholder input |
| **Opportunity Score** | Data-rich discovery prioritization | Survey data |

---

## RICE Scoring

**RICE Score = (Reach × Impact × Confidence) / Effort**

| Factor | Definition | Scale |
|--------|------------|-------|
| **R**each | # customers affected per time period | Absolute number |
| **I**mpact | Effect on goal metric per customer | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| **C**onfidence | How sure are you of estimates? | 100%=high, 80%=medium, 50%=low |
| **E**ffort | Person-weeks of work (all roles) | Person-weeks |

**Scoring table:**

| Feature | Reach | Impact | Confidence | Effort | RICE Score |
|---------|-------|--------|------------|--------|------------|
| [Feature A] | 1,000 | 2 | 80% | 2 | **800** |
| [Feature B] | 500 | 3 | 50% | 1 | **750** |
| [Feature C] | 2,000 | 0.5 | 100% | 5 | **200** |

Higher score = higher priority. Revisit any feature where scores feel wrong — the framework surfaces hidden assumptions.

---

## ICE Scoring (Rapid)

**ICE Score = Impact + Confidence + Ease**

| Factor | Question | Scale 1–10 |
|--------|----------|------------|
| **I**mpact | How much will this move the goal metric? | 1=trivial → 10=transformative |
| **C**onfidence | How confident are we this will work? | 1=gut feeling → 10=proven |
| **E**ase | How easy is this to build? | 1=months → 10=hours |

Use ICE for quick team alignment, RICE when you have real data.

---

## Kano Model

Classify features by how they affect customer satisfaction:

| Category | Definition | Action |
|----------|------------|--------|
| **Must-be** (Basic) | Expected — absence causes dissatisfaction, presence is neutral | Fix first, don't invest in excess |
| **Performance** (Linear) | More = more satisfaction; less = less | Invest proportionally to goal |
| **Attractive** (Delighter) | Unexpected — absence is neutral, presence delights | Use for differentiation |
| **Indifferent** | Doesn't affect satisfaction either way | Deprioritize or cut |
| **Reverse** | Some customers dislike it | Segment carefully |

**Kano survey question pair (per feature):**

- *Functional*: "If this feature existed, how would you feel?"
- *Dysfunctional*: "If this feature did NOT exist, how would you feel?"

Response options: Delighted / Expected / Neutral / Can live with it / Dislike it

Map responses to category using the Kano evaluation table.

---

## MoSCoW Method

Use for **scoping a specific release** under time/resource constraint.

| Category | Meaning | Guideline |
|----------|---------|-----------|
| **M**ust have | Launch blocker — not shippable without this | ≤60% of capacity |
| **S**hould have | High value, important but not critical | ~20% of capacity |
| **C**ould have | Nice to have if budget allows | ~20% of capacity |
| **W**on't have | Explicitly out of scope for this release | Document for future |

**Critical rule**: "Must have" should be ≤60% of capacity. If everything is a Must, nothing is.

**MoSCoW scope table:**

| Feature | Category | Rationale |
|---------|----------|-----------|
| [Feature] | Must | [Why this is a launch blocker] |
| [Feature] | Should | [Why valuable but not critical] |
| [Feature] | Could | [Conditions under which we'd include] |
| [Feature] | Won't | [Deliberately deferred to v2 — reason] |

---

## Opportunity Scoring (Ulwick)

Identify which jobs/outcomes have the best improvement opportunity:

**Opportunity Score = Importance + max(Importance - Satisfaction, 0)**

Survey customers (1–10 scale):
- "How important is [outcome] to you?"
- "How satisfied are you with current solutions for [outcome]?"

| Outcome | Importance | Satisfaction | Score | Priority |
|---------|-----------|--------------|-------|----------|
| [Outcome A] | 9 | 3 | 9+6=**15** | High |
| [Outcome B] | 7 | 8 | 7+0=**7** | Low |
| [Outcome C] | 8 | 5 | 8+3=**11** | Medium |

Scores >10 = underserved opportunity. Scores <10 = table stakes or overserved.

---

## Prioritization Meeting Protocol

1. **Pre-populate the framework** before the meeting — don't fill in scores live
2. **Surface disagreements**: When scores differ >3 points between team members, discuss
3. **Challenge MUSTs**: Every Must-have needs a "if we skipped this, what actually breaks?" test
4. **Document the rationale** — future you will need to explain the decision
5. **Re-run quarterly** — priorities shift; stale rankings cause backlog debt

## Sources
- phuryn/pm-skills prioritization-frameworks (open source)
- dhzrx/ai-pm-claude-skills feature-prioritizer
- Tony Ulwick, *Jobs to be Done: Theory to Practice* (2016)
