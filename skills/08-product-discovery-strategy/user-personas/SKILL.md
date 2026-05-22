---
name: user-personas
description: Build evidence-calibrated user personas grounded in JTBD, behavioral research, and real customer data — not demographic assumptions or fictional archetypes.
---

# User Personas — Evidence-Calibrated

Create personas grounded in research data, JTBD interviews, and behavioral patterns — not demographic assumptions.

## Why Most Personas Fail

Traditional personas fail because they:
- Are based on assumptions, not research
- Emphasize demographics (age, gender, location) over behaviors
- Are created once and never updated
- Don't capture the job the user is trying to do
- Feel fictional rather than recognizable

## Evidence-First Persona Process

### Step 1: Gather Source Data

Before writing a single persona, collect:
- [ ] 5–10 customer interview transcripts (Mom Test style)
- [ ] Behavioral analytics (top user flows, drop-off points, feature usage)
- [ ] Support ticket themes (what they struggle with)
- [ ] Sales call recordings or CRM notes (objections, use cases)
- [ ] NPS survey verbatims (promoters AND detractors)

### Step 2: Identify Behavioral Patterns

Cluster customers by **what they do**, not who they are:

| Behavioral dimension | Segment A | Segment B |
|----------------------|-----------|-----------|
| Primary use case | ... | ... |
| Usage frequency | ... | ... |
| Technical sophistication | ... | ... |
| Decision-making context | ... | ... |
| Current workaround | ... | ... |

### Step 3: Write the Persona

Use this template per behavioral segment:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERSONA: [Name] — [Memorable archetype label]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REPRESENTATIVE PROFILE
  Role/context: [Job title or life situation]
  Environment:  [Where / when they use this product]
  Tech comfort: [Novice / Intermediate / Advanced]

THE JOB TO BE DONE
  When:    [Triggering situation / circumstances]
  I want:  [Progress they're seeking]
  So I can: [Underlying outcome / goal]

BEHAVIORS (from research)
  • [Observed behavior 1] — source: [interview/analytics]
  • [Observed behavior 2] — source: [interview/analytics]
  • [Observed behavior 3] — source: [interview/analytics]

PAIN POINTS (in their words)
  • "[Exact quote from customer interview]"
  • "[Exact quote from customer interview]"
  • "[Exact quote from customer interview]"

CURRENT WORKAROUND
  [What they use today instead of your product, or alongside it]

SUCCESS LOOKS LIKE
  [The outcome that would make this customer a promoter]

ANXIETIES / BARRIERS TO ADOPTION
  • [What holds them back from switching or using more]

REPRESENTATIVE CUSTOMERS
  [2–3 anonymized real customer examples that fit this pattern]

CONFIDENCE LEVEL: [Low / Medium / High]
EVIDENCE BASE:    [# interviews + data sources]
LAST UPDATED:     [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Persona Quality Checklist

- [ ] Every pain point is a direct quote or paraphrase from research, not invented
- [ ] The "job to be done" is in job statement format (When / I want / So I can)
- [ ] Behavioral patterns are supported by at least 3 customer examples
- [ ] Demographics are included only when they're actually decision-relevant
- [ ] Confidence level is marked — low confidence personas are labeled as hypotheses
- [ ] Update date is tracked — personas older than 6 months should be re-validated

## Anti-Patterns to Avoid

| Anti-pattern | Fix |
|--------------|-----|
| "Sarah, 32, Marketing Manager" (pure demographic) | Lead with job/behavior, not age/gender |
| Goals like "wants to save time" | Make it specific: "wants to invoice 10 clients in under 5 min" |
| Invented quotes | Use real verbatims from interviews, label source |
| Single "ideal user" persona | Create 2–4 behavioral segments; primary + secondary |
| Persona as deliverable, not tool | Use in design critiques, feature debates, and sprint planning |

## Using Personas in Practice

**In design critiques**: "Would [Persona] encounter this screen? What would they do?"

**In feature debates**: "Which persona does this serve? What's the evidence of their need?"

**In sprint planning**: "Which persona is this sprint primarily serving?"

**In roadmap reviews**: "Are we serving [high-value persona] or [edge-case persona] this quarter?"

## Sources
- phuryn/pm-skills (open source)
- Teresa Torres, *Continuous Discovery Habits* (2021)
- Rob Fitzpatrick, *The Mom Test* (2013)
