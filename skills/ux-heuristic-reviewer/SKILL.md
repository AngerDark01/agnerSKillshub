---
name: ux-heuristic-reviewer
description: "Audits UI designs and implementations against Nielsen's 10 usability heuristics plus accessibility standards. Produces a prioritized list of issues with severity ratings and specific fixes. Triggers: \"review the UX\", \"usability audit\", \"check accessibility\", \"UX review\", \"is this good UX\", \"audit the interface\", \"check usability\"."
---

# UX Heuristic Reviewer

Systematic usability audit against proven heuristics. Produces actionable, prioritized findings — not vague suggestions.

**Announce at start:** "I'm using the ux-heuristic-reviewer skill."

---

## Review Process

### Step 1: Gather Context

Before reviewing, establish:
- **What is this?** (product type, user goal, technical constraints)
- **Who are the users?** (expertise level, context of use, accessibility needs)
- **What to review?** (specific flows, components, or full app)
- **Provide materials:** screenshots, code, Figma links, or describe the UI

### Step 2: Audit Against 10 Heuristics

For each heuristic, scan the UI and flag violations with severity:

**Severity Scale:**
- 🔴 **Critical** — Blocks task completion or causes errors
- 🟠 **Major** — Significant friction, likely causes user errors or abandonment
- 🟡 **Minor** — Noticeable friction but users can work around it
- 🔵 **Enhancement** — Would improve experience but not a problem

---

### H1: Visibility of System Status
*Always keep users informed about what is going on.*

Check:
- Does every action have visible feedback within 100ms?
- Are loading states clearly communicated (spinner, progress, skeleton)?
- Is the current state/location always visible (active nav, breadcrumbs)?
- Do background processes surface their status?

Common violations: No loading indicator, silent failures, no confirmation after form submit.

### H2: Match Between System and Real World
*Speak the users' language. Use words, phrases, concepts familiar to the user.*

Check:
- Is terminology consistent with user's mental model, not internal system terms?
- Are icons universally understood or labeled?
- Are dates/times in user's local format?
- Do metaphors (folders, trash, cart) match their real-world counterparts?

Common violations: Technical error codes exposed to users, jargon in UI labels, unfamiliar icon-only buttons.

### H3: User Control and Freedom
*Users often choose system functions by mistake. They need a clearly marked "emergency exit".*

Check:
- Can every action be undone or cancelled?
- Is there a way back from every state?
- Are destructive actions reversible (soft-delete, undo)?
- Can users cancel long operations?

Common violations: No undo for deletions, no cancel on uploads, no way to exit a flow without losing progress.

### H4: Consistency and Standards
*Users should not have to wonder whether different words, situations, or actions mean the same thing.*

Check:
- Is terminology consistent throughout (e.g., "save" vs "update" vs "submit")?
- Are visual patterns consistent (buttons, links, forms, modals)?
- Do similar actions behave consistently across the product?
- Does it follow platform conventions (Ctrl+S to save, Esc to close)?

Common violations: Multiple names for same concept, inconsistent button styles for same action type.

### H5: Error Prevention
*Even better than good error messages is a careful design which prevents a problem from occurring.*

Check:
- Are dangerous actions confirmed before executing?
- Do forms validate inline before submit?
- Are ambiguous inputs constrained (date pickers over free text, dropdowns over text fields)?
- Are common errors made impossible (e.g., can't select past dates for future events)?

Common violations: Delete without confirmation, form only validates on submit, free-text for constrained data.

### H6: Recognition Rather Than Recall
*Minimize the user's memory load. Options should be visible or easily retrievable.*

Check:
- Do users need to remember information from one screen to another?
- Are all available actions visible (or one click away)?
- Do forms prefill where possible?
- Are search results visible without memorizing query syntax?

Common violations: Hidden keyboard shortcuts with no discovery, multi-step wizards with no summary, complex query languages.

### H7: Flexibility and Efficiency of Use
*Allow users to tailor frequent actions.*

Check:
- Do power users have shortcuts (keyboard, bulk actions)?
- Are frequent workflows streamlined for repeat use?
- Can defaults be customized?
- Does the UI serve both novice and expert users?

Common violations: No keyboard navigation, no bulk actions for repeated tasks, no way to save preferences.

### H8: Aesthetic and Minimalist Design
*Dialogues should not contain irrelevant or rarely needed information.*

Check:
- Does every element on screen earn its place?
- Is there visual hierarchy (one clear focal point per screen)?
- Is information progressively disclosed (details available but not overwhelming)?
- Is there enough whitespace for breathing room?

Common violations: Dashboard with 15+ equal-weight metrics, modal with 8+ action buttons, walls of text.

### H9: Help Users Recognize, Diagnose, and Recover from Errors
*Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution.*

Check:
- Are errors in plain language (not "Error 422")?
- Do error messages tell users what to do next?
- Are errors shown near the problem (inline, not only at top)?
- Is context preserved when an error occurs (form data not cleared)?

Common violations: "Something went wrong" without guidance, errors that clear the form, server-side validation errors not surfaced.

### H10: Help and Documentation
*Even though it is better if the system can be used without documentation, it may be necessary to provide help.*

Check:
- Are tooltips/inline help available for complex inputs?
- Is there onboarding guidance for first use?
- Are empty states instructive (not just blank)?
- Is documentation accessible from within the flow where needed?

Common violations: Blank empty states, no tooltips on complex settings, help only in external docs.

---

### Step 3: Accessibility Spot Check (WCAG 2.1 AA)

| Check | Tool/Method |
|---|---|
| Color contrast (text) | ≥ 4.5:1 for normal, ≥ 3:1 for large text |
| Color contrast (UI elements) | ≥ 3:1 for focus indicators, icons |
| Keyboard navigation | Tab through all interactive elements |
| Focus indicators | Visible on all focusable elements |
| Alt text | All images have meaningful alt text |
| Form labels | All inputs have associated labels |
| Error identification | Errors not communicated by color alone |
| Touch targets | ≥ 44×44px on mobile |

---

## Output Format

### Audit Report

```
## UX Heuristic Audit: [Component/Flow Name]

### Summary
X critical, X major, X minor issues found across [scope]

### Critical Issues (fix immediately)
1. [H3 - User Control] No undo for "Delete Account" action
   - Where: Settings > Danger Zone
   - Impact: Users who click accidentally cannot recover
   - Fix: Add confirmation dialog + 30-day soft-delete with recovery

### Major Issues
2. [H9 - Error Recovery] Form clears on validation error
   - Where: Checkout form > submit
   - Impact: Users must re-enter all fields after any error
   - Fix: Preserve field values; only clear password fields

### Minor Issues
...

### Accessibility
- ❌ [Contrast] Nav link color #767676 on white = 4.48:1 (fails AA for small text)
  Fix: Use #595959 = 7.0:1

### Enhancements
...
```

---

## Principles

**Audit the experience, not the code.** Heuristics apply to the user's perception, not implementation quality.

**Every finding must be actionable.** "This is confusing" is not a finding. "Label says 'Submit' but triggers async validation — add loading state and disable button" is a finding.

**Prioritize by user impact.** One critical issue that blocks 80% of users matters more than 10 minor polish items.

---

*Sources: Nielsen (1994) "10 Usability Heuristics", WCAG 2.1, Baymard Institute UX research*
