# Skill Catalog

The repository has two layers:

- `skills/`: categorized source of truth for humans.
- `sync/skills/`: generated flat copy used by skillshare and Codex.

Do not edit `sync/skills/` directly. Edit `skills/<category>/<skill>/`, then run `scripts/rebuild-sync.sh`.

## 00 Meta System

Agent operating discipline, skill management, task control, and improvement loops.

- `delivery-discipline`: completion criteria and verification before delivery.
- `self-improvement`: learning/error capture and promotion protocol.
- `skill-creator`: create, evaluate, and improve skills.
- `skillshare`: manage/sync skills across AI tools.
- `taskstate-runtime`: formal phase/task/deliverable controller.

## 01 Planning Execution

Feature design, implementation planning, and execution workflows.

- `brainstorming`: validate design before implementation.
- `writing-plans`: convert approved designs into atomic tasks.
- `executing-plans`: batch execute plans with human checkpoints.
- `subagent-driven-development`: execute plans through subagents and reviews.

## 02 Code Quality

Project understanding, debugging, testing, review, and security quality.

- `codebase-ontology`: build and maintain CODEBASE.md project intelligence.
- `systematic-debugging`: root-cause-first debugging.
- `requesting-code-review`: request code-review subagent feedback.
- `receiving-code-review`: process review feedback rigorously.
- `testing-generator`: generate frontend tests.
- `security-best-practices`: secure coding references and checklists.

## 03 Frontend Architecture

Frontend system structure and state architecture.

- `frontend-architecture-designer`: scalable frontend architecture.
- `project-structure-manager`: project structure and module boundaries.
- `state-management-architect`: React state management decisions.

## 04 Frontend Performance

Performance analysis and optimization.

- `bundle-size-optimizer`: reduce JavaScript bundle size.
- `frontend-performance-analyzer`: Core Web Vitals and runtime performance.
- `react-render-optimizer`: React render optimization.

## 05 UI Design UX

Visual design, interaction design, implementation, and UX review.

- `design-system-architect`: design tokens and system foundations.
- `figma-to-component`: convert Figma/mockups to components.
- `frontend-design`: high-quality frontend design guidance.
- `frontend-code-reviewer`: frontend accessibility/code review.
- `frontend-refactor`: React/Vue component refactoring.
- `interaction-flow-designer`: user flow and state-machine design.
- `microinteraction-designer`: interaction polish and animation.
- `ui-component-generator`: distinctive UI components.
- `ui-style-analyst`: analyze product visual style through Chrome.
- `ui-style-extractor`: extract reusable UI style artifacts.
- `ux-heuristic-reviewer`: usability/accessibility audit.

## 06 Browser Automation

Real browser control and visual capture tooling.

- `chrome-cdp`: local Chrome DevTools Protocol control.
- `chrome-cdp-setup`: Chrome CDP setup and troubleshooting.
- `playwright`: Playwright browser automation.
- `screenshot`: screenshot capture tooling.

## 07 Research Analysis

Market, product, technology, and deep research.

- `associative-research`: indirect/associative research strategy.
- `product-landscape`: product and market landscape research.
- `tech-stack-scout`: technical option scouting.
- `hv-analysis`: horizontal/vertical deep research reports.

## 08 Product Discovery Strategy

Product discovery, strategy, positioning, and customer understanding.

- `continuous-discovery`: weekly discovery cadence and opportunity trees.
- `customer-journey-map`: end-to-end customer journey mapping.
- `design-sprint`: 5-day design sprint workflow.
- `inspired-product`: Marty Cagan product discovery and risk framing.
- `jobs-to-be-done`: JTBD analysis.
- `lean-ux`: hypothesis-driven Lean UX.
- `mom-test`: customer interview protocol.
- `obviously-awesome`: product positioning.
- `user-personas`: evidence-based personas.

## 09 Requirements Docs

Requirements writing and document production.

- `feature-prioritization`: prioritization frameworks.
- `prd-writer`: PRD generation.
- `user-stories`: INVEST stories and acceptance criteria.
- `doc-coauthoring`: collaborative document drafting.
- `doc`: DOCX document rendering tooling.
- `pdf`: PDF processing.

## 10 GitHub Platform

GitHub/OpenAI platform workflows.

- `gh-address-comments`: address GitHub PR review comments.
- `gh-fix-ci`: debug/fix GitHub CI failures.
- `openai-docs`: official OpenAI documentation lookup.

## 11 Domain Autobid

Tender/bid document workflow.

- `autobid-initializer`: initialize bid workspace and task store.
- `autobid-office-tools`: DOCX/XLSX/task-store mechanical tools.
- `autobid-orchestrator`: bid workflow orchestration.
- `autobid-phase1-extractor`: phase 1 extraction.
- `autobid-phase2-composer`: phase 2 composition.

## 12 Domain Ontology

Formal business/domain modeling.

- `ontology-engineer`: ontology, knowledge graph, OWL/RDF/SPARQL modeling.

## 13 Writing Content

Long-form writing and content style.

- `khazix-writer`: Khazix public-account long-form writing.

## Not Imported

- OpenClaw repo-specific maintainer skills.
- Large OpenClaw tool skill set.
- `evolver`.
- duplicate `files (11)` UI style skill.
- duplicate `reasearch skills` bundle.
