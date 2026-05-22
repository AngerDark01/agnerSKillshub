---
name: design-sprint
description: Run Jake Knapp's 5-day Design Sprint to answer critical product questions through rapid prototyping and user testing — compress months of work into one focused week.
---

# Design Sprint — 5-Day Process

Run Google Ventures' Design Sprint to answer a critical product question through design, prototyping, and testing with real users in 5 days.

## When to Run a Sprint

A Design Sprint is right when:
- [ ] There's a high-stakes question that needs an answer before building
- [ ] The team is stuck or has conflicting opinions
- [ ] A new product, feature, or market direction needs validation
- [ ] Months of work would be wasted if the core assumption is wrong

**Not ideal for**: incremental improvements, well-understood problems, or situations requiring >1 week of research.

## Preparation (Before Monday)

**Sprint team** (5–7 people, maximum):
- 1 Decider (has authority to make final calls — usually PM or Founder)
- 1 Facilitator (runs the sprint — often a Designer or PM)
- 1 Designer
- 1–2 Engineers
- 1 domain expert (marketing, sales, customer success, etc.)

**Logistics:**
- Block full 5 days for all participants — no partial attendance
- Book a room with 2 whiteboards minimum
- Recruit 5 user interview participants for Friday
- Prepare: sticky notes, markers, timer, paper, Sharpies

**Sprint Question**: Before day 1, write the single question the sprint must answer.
> "Will users understand how to [core workflow] without help?"
> "Is [value proposition] compelling enough to drive signups?"

---

## Monday — Map the Problem

**Goal**: Understand the problem space and pick a target.

| Activity | Time | Output |
|----------|------|--------|
| Long-term goal | 30 min | 2-year goal statement |
| Sprint questions (what could go wrong?) | 30 min | Risk list |
| How-Might-We notes from expert interviews | 90 min | HMW sticky notes |
| Map the customer journey | 60 min | End-to-end journey map |
| Target selection | 30 min | Chosen moment + user type |

**Map format:**
```
[Actor] → [Step 1] → [Step 2] → ... → [Outcome]
         Target area: ↑ mark the moment you'll focus on
```

**End of day**: Decider picks the target area of the map. Sprint focuses here.

---

## Tuesday — Sketch Solutions

**Goal**: Generate a wide range of solutions before converging.

| Activity | Time | Output |
|----------|------|--------|
| Lightning demos (existing solutions) | 60 min | 3–5 demos, key ideas noted |
| 4-step sketch | 90 min | Individual solution sketches |

**4-Step Sketch process:**
1. **Notes** (20 min): Walk through the map, write down ideas
2. **Ideas** (20 min): Rough sketches, quick variations, no judgment
3. **Crazy 8s** (8 min): Fold paper into 8 panels, sketch 8 variations of one idea
4. **Solution sketch** (30 min): 3-panel storyboard of the best idea

**Rules**: Sketches are anonymous, self-explanatory (can't explain in person), and detailed enough to build from.

---

## Wednesday — Decide

**Goal**: Pick the best solution without group debate.

| Activity | Time | Output |
|----------|------|--------|
| Art museum (hang sketches) | 10 min | Sketches visible to all |
| Heat map vote (dot stickers) | 20 min | Dots on most interesting parts |
| Speed critique | 30 min | Structured feedback, no debate |
| Straw poll + Decider vote | 15 min | One winner (Decider has final say) |
| Rumble or all-in-one decision | 15 min | Prototype plan |
| Storyboard (8–12 panels) | 90 min | Panel-by-panel prototype plan |

**Storyboard panels:**
```
[Panel 1]  [Panel 2]  [Panel 3]  [Panel 4]
Opening    Step 1     Step 2     Key moment
scene

[Panel 5]  [Panel 6]  [Panel 7]  [Panel 8]
Step 3     Decision   Outcome    Ending
           point                 scene
```

---

## Thursday — Prototype

**Goal**: Build a realistic prototype in one day. Real enough to test — nothing more.

**Prototype tools** (pick one per component):
- **Screens**: Figma, Keynote, PowerPoint (fast to assemble)
- **Docs/content**: Google Docs, Notion mockup
- **Hardware**: Camera + printed screenshots
- **Service flow**: Roleplay script for human steps

**Goldilocks quality**: Good enough that users don't comment on the medium, not so polished that feedback is about polish instead of concept.

**Divide and conquer**:
- 2 people: build screens
- 1 person: write realistic content/copy
- 1 person: compile assets, photos, icons
- 1 person: interview guide + logistics

**End of day**: Dry run the prototype as if it were a real user session.

---

## Friday — Test

**Goal**: Learn by watching 5 users interact with the prototype.

**Interview structure** (60 min/participant):

```
1. Welcome + framing (5 min)
   "We're testing the design, not you. Think aloud."
   "There are no wrong answers."

2. Context questions (5 min)
   Learn about their background and relevant behavior.

3. Introduce prototype (2 min)
   Set the scene — what they're about to do.

4. Tasks (40 min)
   Give 3–5 tasks without leading.
   "What would you do here?" not "Click that button."

5. Debrief (8 min)
   "What stood out? What was confusing?"
```

**Observation team** (3 people watching behind glass or screen share):
- Note observations on sticky notes: [+] positive, [-] negative, [?] questions

**End-of-day synthesis** (1 hour):
- Cluster observations by theme
- Identify patterns (must appear in ≥3 of 5 sessions to count)
- Recommend: Go / Modify / Don't Go

---

## Sprint Report (1 page)

```markdown
## Sprint Report: [Product/Feature Name]
**Sprint Question**: [The question you set out to answer]
**Dates**: [Mon–Fri dates]
**Team**: [Names + roles]

### What we tested
[2–3 sentence description of the prototype]

### Key findings
1. [Pattern from ≥3 sessions — with evidence]
2. [Pattern from ≥3 sessions — with evidence]
3. [Pattern from ≥3 sessions — with evidence]

### Recommendation
[ ] Go — proceed to build
[ ] Modify — adjust [specific element] and retest
[ ] Don't go — pivot or abandon

### Next steps
- [ ] [Action item] — [Owner] — [Date]
```

## Sources
- Jake Knapp, John Zeratsky, Braden Kowitz — *Sprint* (2016)
- wondelai/skills (MIT License)
