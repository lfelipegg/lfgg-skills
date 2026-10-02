# Selective AI Hero guidance

## Accepted decisions

- Update agent-builder only; preserve discovery metadata and grill-with-docs.
- Use concise, readable plans covering actions and verification, with unresolved
  questions at the end when present. Resolve blocking questions before finalization.
- Include planning policies in generated guides only when requested or established.
- Preserve safeguards, narrow-edit behavior, unique constraints, existing document
  locations, and the default 200-line ceiling with user-selected overrides.
- Prefer stable capabilities over detailed inventories while retaining necessary paths.
- Discover specialized guidance by content and relevant links, backed by manifests
  and configuration. Reuse existing destinations before creating topic documents.
- Separate language, testing, and build rules when useful during authorized creation
  or refactoring. Keep conditional relative links, preserve rule meaning, and avoid
  duplication, empty scaffolding, invented conventions, and circular reading chains.
- Distinguish topic guidance from directory-specific local guides. Audits propose
  moves only; narrow edits do not trigger unrelated extraction.
- Record four terms in the [root glossary](../CONTEXT.md) for terminology reference. No ADR is needed for this reversible edit.

## Implementation

Update the skill's planning, authoring, and routing guidance. Extend existing
disposable scenarios for extraction, unconventional document names, configuration
links, absent documentation, scoped requests, and optional planning policies.

## Verification

Run the skill validator, relative-link checks, and disposable behavioral scenarios.
Recheck narrow edits, preservation, and size overrides. Distinguish behavioral
execution from structural checks and walkthroughs. Use before/after comparisons
because this workspace has no Git repository.

## Sources

- [A Complete Guide To AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md):
  selective adoption of focused root instructions and linked specialized guidance.
- [My AGENTS.md file for building plans you actually read](https://www.aihero.dev/my-agents-md-file-for-building-plans-you-actually-read):
  concise plans and explicit unresolved questions, preserving readability.

## Results — 2026-09-10

Implemented and validated. Skill-creator validation, changed-file local links,
whitespace, fixture compilation, and unchanged discovery metadata checks passed.
Before/after comparison confirmed changes are limited to the skill, glossary,
scenario definitions, this plan, and the plan index.

| Behavioral case | Result and evidence |
| --- | --- |
| 01: Narrow edit | PASS: exact command replacement; manifest and API rule unchanged. |
| 03: Preservation | PASS: 226 lines reduced to 8; all unique lines and storage guidance preserved. |
| 07: Size override | PASS: initial 190 lines unchanged; follow-up 220 lines preserves all 217 fields under the 240-line cap. |
| 08: Topic extraction | PASS after correction: initial run omitted the language-to-testing link; clarified the rule and reran in a fresh fixture/session. Retest created all three topic docs and the complete relative-link chain, preserving safeguards and configuration. |
| 09: Existing discovery and scope | PASS: audit made no edits; narrow step corrected the command; refactor reused linked handbook docs without duplicate scaffolding or invented esbuild guidance. |
| 10: Planning and sparse evidence | PASS: concise plan made no edits; initial guide contained only known context; planning policy appeared only after explicit request. |

These were independent agent executions with output-file inspection, not manual
walkthroughs. Fixtures and outputs are in `/tmp/agent-builder-eval-817wmv2u`; the
extraction retest is `08-retest`. Cases 02, 04, 05, and 06 were not rerun. No
dependencies were installed and no fixture builds or project tests were run.
Native runtime instruction loading was not tested.
