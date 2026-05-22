---
name: customer-journey-map
description: Map the end-to-end customer experience across 7 stages — from awareness to advocacy — identifying aha moments, pain points, churn triggers, and improvement opportunities at each touchpoint.
---

# Customer Journey Map

Map the complete customer experience to identify friction, aha moments, churn triggers, and prioritized improvement opportunities.

## Why Journey Mapping

Journey maps reveal the experience *between* your product's features — the gaps, handoffs, and emotional transitions that analytics miss. Use them to:
- Align cross-functional teams on the customer experience
- Identify the highest-leverage friction points
- Find the aha moment (and make it earlier)
- Surface churn triggers before customers leave

## The 7 Stages

| Stage | Customer question | Team responsible |
|-------|------------------|------------------|
| **1. Awareness** | "Does this exist? Is it for me?" | Marketing |
| **2. Consideration** | "Could this solve my problem?" | Marketing / Sales |
| **3. Decision** | "Should I try / buy this?" | Sales / Product |
| **4. Onboarding** | "How do I get started?" | Product / CS |
| **5. Activation** | "Am I getting value yet?" ← aha moment | Product |
| **6. Retention** | "Is this worth continuing?" | Product / CS |
| **7. Advocacy** | "Should I recommend this?" | CS / Marketing |

## Journey Map Template

Build one map per primary persona. Use this row structure:

```
PERSONA: [Name + archetype]
SCENARIO: [The specific journey being mapped, e.g., "Free trial → paid conversion"]

STAGE →          │ Awareness │ Consideration │ Decision │ Onboarding │ Activation │ Retention │ Advocacy │
─────────────────┼───────────┼───────────────┼──────────┼────────────┼────────────┼───────────┼──────────┤
CUSTOMER ACTIONS │           │               │          │            │            │           │          │
  What do they   │           │               │          │            │            │           │          │
  actually do?   │           │               │          │            │            │           │          │
─────────────────┼───────────┼───────────────┼──────────┼────────────┼────────────┼───────────┼──────────┤
TOUCHPOINTS      │           │               │          │            │            │           │          │
  Where do they  │           │               │          │            │            │           │          │
  interact?      │           │               │          │            │            │           │          │
─────────────────┼───────────┼───────────────┼──────────┼────────────┼────────────┼───────────┼──────────┤
THOUGHTS         │           │               │          │            │            │           │          │
  What are they  │           │               │          │            │            │           │          │
  thinking?      │           │               │          │            │            │           │          │
─────────────────┼───────────┼───────────────┼──────────┼────────────┼────────────┼───────────┼──────────┤
EMOTIONS         │  😐/😊/😟 │               │          │            │            │           │          │
  Emotional      │           │               │          │            │            │           │          │
  state (emoji)  │           │               │          │            │            │           │          │
─────────────────┼───────────┼───────────────┼──────────┼────────────┼────────────┼───────────┼──────────┤
PAIN POINTS      │           │               │          │            │            │           │          │
  What frustrates│           │               │          │            │            │           │          │
  or confuses?   │           │               │          │            │            │           │          │
─────────────────┼───────────┼───────────────┼──────────┼────────────┼────────────┼───────────┼──────────┤
OPPORTUNITIES    │           │               │          │            │            │           │          │
  What could we  │           │               │          │            │            │           │          │
  improve here?  │           │               │          │            │            │           │          │
```

## Key Moment: The Aha Moment

The aha moment is when a customer first experiences the core value of your product — the moment that makes them think "this is worth it."

**Find it by:**
- Analyzing cohort data: What do retained users do that churned users don't?
- Customer interviews: "When did you first feel like this was working for you?"
- Activation analysis: What action correlates with 30-day retention?

**Make it earlier:**
- Remove all steps between signup and aha moment
- Make the aha moment the first onboarding goal, not a nice-to-have
- Show users exactly how to reach it (progress indicator, tooltips, guided checklist)

## Churn Trigger Identification

At each stage, identify what causes customers to stop and leave:

| Stage | Common churn triggers | Detection signal |
|-------|----------------------|-----------------|
| Consideration | Value prop unclear, wrong audience | Bounce rate, time-on-page |
| Decision | Price shock, trust deficit, no social proof | Abandoned checkout |
| Onboarding | Too long, too complex, unclear first value | Drop-off in onboarding steps |
| Activation | Never reached aha moment | Low activation rate |
| Retention | Feature doesn't fit workflow, better alternative | Usage drop, cancellation survey |

## Data Sources Per Stage

| Stage | Quantitative | Qualitative |
|-------|-------------|-------------|
| Awareness | SEO, ad impressions, referral source | Social listening |
| Consideration | Landing page analytics, scroll depth | User testing, 5-second test |
| Decision | Conversion rate, trial signup | Sales call recordings |
| Onboarding | Step completion rates | Onboarding interviews |
| Activation | Activation rate, time-to-aha | Activation interviews |
| Retention | DAU/MAU, feature usage, NPS | Churn interview, NPS verbatims |
| Advocacy | Referral rate, NPS score | Promoter interviews |

## Journey Map Facilitation Workshop

**Time**: 3–4 hours
**Participants**: PM + Designer + CS + Sales + Engineering (≤8 people)

1. **Agree on persona and scenario** (15 min)
2. **Each person fills their lane** — sticky notes on their area of expertise (30 min)
3. **Walk the journey together** — narrate stage by stage, left to right (45 min)
4. **Mark emotions** on the journey curve — high/low/neutral at each stage (15 min)
5. **Identify top 5 pain points** — dot voting on biggest impacts (20 min)
6. **Prioritize opportunities** — map pain points on Effort × Impact matrix (30 min)

## Deliverable

Output a visual journey map (Miro, FigJam, or table) plus a prioritized opportunity list:

```markdown
## Top Opportunities from Journey Map

| # | Stage | Pain Point | Opportunity | Effort | Impact | Priority |
|---|-------|------------|-------------|--------|--------|----------|
| 1 | Onboarding | Users don't reach first project | Guided checklist to first project | Low | High | P1 |
| 2 | Retention | Power users hit limits too early | Usage-based upgrade prompt | Med | High | P2 |
```

## Sources
- phuryn/pm-skills customer-journey-map (open source)
- wondelai/skills (MIT License)
