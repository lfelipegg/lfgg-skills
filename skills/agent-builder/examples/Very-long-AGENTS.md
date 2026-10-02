# Fuller project guide example

The fenced guide illustrates adopted policies for a particular project. Verify
its stack, paths, and policies before adapting it; these are not universal
requirements. Authoring notes outside the fence are not generated instructions.

```markdown
# Prensa FIFA Agent Guide

Use this file as the quick-start operating guide for agents working in this repository. Keep it short, current, authoritative, and at most 200 lines unless the user specifies another cap. This file contains durable future-agent rules only, not product requirements, feature plans, chat summaries, or temporary task notes.

## Project Purpose

Prensa FIFA is a Spanish-first SvelteKit website for press and media outlets to learn about FIFA Fan Fest Monterrey artist press conferences and request accreditation for one or more conference days.

Core public surfaces:

- Event intro page: event information, artist schedule, FAQ, and registration calls to action.
- Registration form: media outlet details, responsible contact, selected conference days, per-day accreditation rosters, and supporting evidence links.

Spanish is the default locale. English routes may live under `/en/` only when the project keeps English content current.

## Required Stack

Use the existing project stack and the approved product stack:

- SvelteKit
- Svelte 5 Runes Mode
- TypeScript
- Vite
- TailwindCSS
- Paraglide
- GSAP when motion clearly improves hierarchy or transitions
- Supabase with Postgres for registration data
- Vercel as the deployment target

This project requires approval for new dependencies. Honor approval already given for the concrete addition; do not ask again.

## Source Of Truth

Read the relevant sources for the requested change:

- `docs/specs/*`: product scope, registration rules, data model direction, and acceptance criteria.
- `PRODUCT.md`: product intent, audience, positioning, and product-wide direction.
- `docs/agents/*`: read the relevant detailed convention before changing routing, i18n, testing, safety, documentation, or git workflow.
- `DESIGN.md`: UI, styling, motion, visual direction, and design constraints.
- `docs/CHANGELOG.md`: user-visible and important technical history.
- `package.json`: available scripts. Do not invent scripts.
- `messages/` and `project.inlang/`: localization configuration.

Follow applicable shared/local instructions, runtime precedence, and explicit user choices. Inspect overrides and ancestor guidance for the target runtime before deciding which instructions apply.

Code shows current behavior; specs describe intended behavior. Resolve discrepancies using the task and available evidence. Report material unresolved conflicts; neither existing bugs nor stale documentation automatically determine the desired result.

## Content Routing

Do not use `AGENTS.md` as a project notebook. Route content correctly:

- Durable future-agent rule: `AGENTS.md`
- Detailed agent guidance: `docs/agents/*`
- Product requirements or feature specs: `docs/specs/*`
- Product intent, audience, and positioning: `PRODUCT.md`
- Visual direction and design principles: `DESIGN.md`
- Implementation plans: `docs/plans/`
- Architecture decisions and tradeoffs: `docs/decisions/`
- Handoffs and continuation notes: `docs/handoffs/`
- Review records: `docs/reviews/`
- Current task records: `docs/tasks/`

`AGENTS.md` may point to these locations. It should not duplicate their full content.

## Agent Workflow

For non-trivial work:

1. Inspect existing files before deciding what to change.
2. Read the relevant source-of-truth documents before editing.
3. Create or use a dedicated git worktree under `.worktrees/` before mutating repo-tracked files.
4. Keep scope tight and avoid unrelated rewrites.
5. Create or update task docs when changes affect multiple files, UI, routes, data structures, docs policy, i18n, or architecture.
6. Implement the smallest coherent change.
7. Add or update focused tests when behavior changes.
8. Run the relevant existing checks from `package.json`.
9. Update task docs and `docs/CHANGELOG.md` when behavior, setup, commands, architecture, or user-visible behavior changed.
10. Summarize changed files, verification, docs, and follow-ups.

## Task Documentation

For non-trivial tasks, use:

~~~text
docs/tasks/{ascending-number}-{iso-timestamp}-{task-title}/summary.md
docs/tasks/{ascending-number}-{iso-timestamp}-{task-title}/next-steps.md
~~~

`summary.md` captures the request, decisions, files changed, verification, and unresolved risks. `next-steps.md` captures follow-ups, deferred work, cleanup opportunities, and prerequisites.

Do not put task progress or handoff detail in `AGENTS.md`.

## Implementation Rules

- Use Svelte 5 Runes Mode for Svelte components.
- Use Tailwind utilities and the project theme. Custom CSS classes or global styles require project approval; reuse authorization already given for the change.
- Keep reusable components in `src/lib/components`.
- Keep reusable data, labels, metadata, route labels, event schedules, form options, and localized content in `src/lib/data`.
- Keep reusable logic in `src/lib/utils`.
- Keep server-only Supabase writes, validation, and secrets in server routes or server-only modules. Never expose service-role keys to client code.
- Add both `es` and `en` values for new localized content when English is maintained for the affected route.
- Use Spanish slugs for Spanish routes.
- Prefer existing project patterns before introducing new ones.
- Prefer platform APIs, SvelteKit features, existing utilities, and installed dependencies before adding new packages.
- Do not create generic wrappers, services, managers, repositories, or helpers unless the current task proves reuse or boundary value.

## UI And Design Rules

Before meaningful UI, styling, motion, layout, or copy changes, read `DESIGN.md` and the relevant product/spec docs.

- Use existing theme tokens, components, and layout patterns before creating new ones.
- Keep Spanish copy primary and consistent with established terminology.
- Maintain keyboard access, visible focus states, readable contrast, and useful form errors.
- Use GSAP only when motion improves hierarchy, orientation, or transitions.
- Test responsive behavior for mobile and desktop when UI changes.

## Security And Data Safety

- Do not print, request, or commit secrets.
- Do not log service-role keys, access tokens, session cookies, accreditation evidence links, personal contact data, or raw registration payloads.
- Validate registration input server-side.
- Enforce authorization and data access rules server-side.
- Treat client-side checks as UX only, not security.
- This project requires authorization for schema, production-data, deploy-topology, or paid-service changes; ask only when that concrete action is not already authorized.

## Git And Guardrails

- Work from a dedicated git worktree under `.worktrees/` for implementation tasks, including docs, UI, code, tests, data structures, and architecture changes.
- Do not change unrelated files.
- Do not revert user changes unless explicitly asked.
- Routine scoped edits and removals need no repeated approval. Preserve user work and obtain missing authorization before destructive actions or external mutations. Permission to edit does not itself authorize pushes, deployments, or force-pushes.
- Do not weaken tests, checks, auth, authorization, validation, accessibility, privacy, or CI to make work pass.

## Verification

Use the relevant scripts actually defined in `package.json`, with their documented prerequisites and working directory. Inspect their effects before running them. Report checks that cannot run or fail because of unrelated work or environment setup, with relevant output; do not describe a failing required check as passed.

## Review Rules

Before requesting review, provide summary of changes, files changed, tests or checks run, docs updated, known limitations, and deferred follow-up work.

During review, check PRD/spec alignment, implementation simplicity, tests, security, data safety, accessibility, localization, UI quality, and docs.

## Acceptance Rules

A task can be accepted only when acceptance criteria are met, required checks pass or an applicable exception is explicitly accepted, unavailable or failing checks are reported, review findings are resolved or explicitly deferred, docs are updated when behavior/setup/commands/architecture/product decisions changed, and no unrelated changes are included.

## Merge Rules

Do not merge until the task is accepted, CI or the local equivalent passes, migrations/rollout risks/data risks are documented when relevant, rollback notes exist for risky changes, and any `AGENTS.md` change was reviewed as a durable instruction change.

## Nested AGENTS.md

Use nested `AGENTS.md` files only if a subdirectory needs local rules that meaningfully differ from this root guide. Nested files should cover local commands, editable areas, forbidden imports, package boundaries, testing rules, or local security constraints. Do not repeat the root unless repetition prevents a serious mistake.

## AGENTS.md Maintenance

Update this file only when a rule should apply to future agent work.

Do not add one-off task details, full specs, implementation plans, chat summaries, temporary task notes, product requirements, large glossaries, or unresolved brainstorms.

Remove repetition before splitting. If necessary detail exceeds the selected cap or has a useful separate scope, move it to existing guidance and leave a pointer explaining when to read it. Review changes to this file like code: the new rule must be durable, specific, correctly placed, non-conflicting, and short.

## Final Response

After coding, respond in this shape:

~~~txt
Done.
Changed:
- ...
Tested:
- ...
Docs:
- ...
Notes:
- ...
~~~

```
