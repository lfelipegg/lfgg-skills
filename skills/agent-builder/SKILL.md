---
name: agent-builder
description: Use when creating, updating, auditing, maintaining, or reorganizing AGENTS.md, nested AGENTS.md files, project agent instructions, docs/agents guidance, or /agents subagent plans for a repository
---

# Agent Builder

Create compact, durable repository instructions. The usual output is one root
`AGENTS.md` with confirmed commands, constraints, and pointers to relevant docs.
This skill handles agent guidance and subagent planning, not product implementation.

## Workflow

1. **Inspect.** Read the requested files, relevant manifests/configuration, and
   existing documentation. Identify the target runtime and effective instruction
   sources before choosing which file to change. For discovery, overrides, or
   cross-platform support, read [platforms](references/platforms.md).
2. **Choose the requested output.** Use the paths below; do not expand a narrow
   edit into a repository-wide reorganization.
3. **Resolve relevant unknowns.** Ask only for missing facts that change the
   requested output and cannot safely be discovered. Reuse decisions and
   authorization already established in the conversation. For broader setup
   with consequential missing choices, consult [interview](references/interview.md).
4. **Write within scope.** Preserve unique durable constraints, existing document
   locations, and user changes. For substantial revisions, briefly state the
   discovered facts and consequential assumptions before editing; this is not
   an approval gate. Apply the authoring rules below.
5. **Validate and report.** Use the checklist, then summarize changed files,
   verification, and unresolved risks. Explain new supporting files when needed.

### Request paths

- **Targeted update:** inspect the rule, its source, and applicable guidance;
  change only what the request requires. No unrelated policy interview.
- **Audit only:** inspect and return evidence-backed findings grouped as keep,
  update, move, or delete, with a proposed patch when useful. Do not mutate the
  target repository. A request to apply fixes authorizes the scoped revision.
- **Create or refactor:** draft the smallest useful guide; remove repetition
  before moving detail. Keep an inventory of unique constraints and their new
  locations during a large rewrite so shortening does not silently lose rules.
- **Initial setup:** write a minimal guide from known facts. Omit unavailable
  commands and optional sections. Create supporting documents only when they
  have useful content required by the request; do not scaffold empty directories
  or implement product features.
- **Fast draft:** inspect first, then isolate unresolved decisions in one
  `Assumptions to confirm` section. Do not supply guessed commands as executable
  instructions. When finalizing, resolve consequential unknowns or omit the
  unsupported details; remove draft placeholders from operating instructions.
- **Subagent planning:** read [subagents](references/subagents.md). Distinguish
  portable prompt plans from installed agents. A planning request alone does
  not authorize runtime installation or live delegation.

### Planning responses

Keep plans concise and readable: actions, verification, and unresolved questions
at the end when present. Resolve blocking questions before finalizing an executable
plan. Include planning policies in generated guides only when requested or already
established; planning does not imply mandatory commits or a new approval gate.

## Authorization and conflicts

Honor explicit user choices over skill defaults, within applicable higher-level
instructions and runtime permissions. Preserve authorization already given for
an action; do not ask again merely because a routine scoped edit updates or
removes file content. Preserve unrelated work and protect against data loss.

Record dependency, git, release, and documentation policies only when established
by the repository or user. Do not impose universal approval gates for installs,
worktrees, or ordinary edits. For destructive actions or external mutations,
check that the concrete action is authorized; request approval only if missing.
Permission for one task does not authorize unrelated changes or deployments.

Code records observed behavior; specs record intended behavior. Neither is an
unconditional override for the other. Follow applicable instruction precedence
and the current task. Report material conflicts, use available evidence to
resolve them, and ask only if an unresolved decision prevents correct work.
An existing bug does not become a requirement because the code implements it.

## Authoring rules

- Include durable, specific, actionable rules: relevant reading, verified
  commands, architecture boundaries, and project-specific security, privacy,
  accessibility, testing, and delivery expectations. Avoid generic advice that
  does not change the agent's decisions.
- Source commands from repository files or user answers, including working
  directory and prerequisites when relevant. Do not infer scripts from a stack
  name. Distinguish a documented command from one actually executed successfully.
- Prefer stable capabilities and architecture boundaries over detailed file
  inventories. Retain verified paths needed for commands, reading triggers, or
  critical constraints; remove stale navigation without losing durable rules.
- Preserve safeguards against exposing secrets, weakening validation or checks,
  and reverting unrelated user work. Do not convert project-specific preferences
  in examples into universal requirements.
- Include review/acceptance/merge gates when established: task alignment,
  relevant verification, resolved or explicitly deferred findings, and necessary
  documentation. Explained failures still need assessment; do not label a
  failing required check as passed. Include CI and rollout/rollback expectations
  for risky releases when applicable.
- Add a compact skill usage map only for confirmed available skills, stating
  when each helps. Do not copy full skill manuals or require unavailable tools.
- Final instructions contain confirmed facts and policies. Omit unsupported
  optional sections instead of retaining `confirm before use` command slots.
  Draft assumptions describe unresolved decisions, not guessed operating rules.

### Size and local scope

Use at most **200 lines per generated `AGENTS.md`** by default. An explicit user
cap replaces this default, including during validation. This is an editorial
budget, not a runtime loading limit. Shorter guides are welcome; do not pad them.

First delete repetition and unnecessary prose. Keep a useful single file when
it fits the selected cap; there is no earlier automatic split threshold. Move
necessary specialized detail to existing guidance locations when its scope or
remaining size warrants it. Choose destinations using content routing below.
Every pointer must explain when to read the linked guidance.

Root instructions cover shared behavior. Nested instructions cover meaningful
local differences: commands, package boundaries, testing, security, or design
constraints. Avoid repeating root rules unless needed to prevent a serious
mistake. Do not create nested files just because directories or subagents exist.

### Content routing

Reuse the repository's established documents and names first. The locations
below are suggestions only when a needed destination does not already exist.
Do not move unrelated documents or create a documentation system without scope.

| Content | Suggested destination |
| --- | --- |
| Durable shared agent rules | Root `AGENTS.md` |
| Local agent differences | Nested `AGENTS.md` |
| Language, testing, or build guidance | Existing topic docs; otherwise `docs/TYPESCRIPT.md`, `docs/TESTING.md`, or `docs/BUILD.md` as relevant |
| Detailed agent guidance | `docs/agents/` |
| Product requirements and feature specs | `docs/specs/` |
| Implementation plans | `docs/plans/` |
| Domain language and glossary | `CONTEXT.md` |
| Product intent and audience | `PRODUCT.md` |
| Visual direction and constraints | `DESIGN.md` |
| Architecture decisions and tradeoffs | `docs/decisions/` |
| Continuation notes | `docs/handoffs/` |
| Review records | `docs/reviews/` |
| Temporary tasks and backlog | Existing issue tracker or `docs/tasks/` |

Keep pointers in `AGENTS.md`, not full specs, plans, glossaries, design briefs,
chat summaries, temporary TODOs, or brainstorms. Detailed agent guidance is not
a substitute destination for product or task records.

### Discover and separate specialized guidance

During creation or refactoring, inspect instructions, relevant documentation links,
manifests, and language, testing, and build configuration. Recognize topic guidance
by content, not filenames: search existing docs and follow relevant links before
choosing a destination. Configuration establishes available tools and commands,
not evidence for invented coding conventions.

When separation improves relevance, move specialized rules into existing topic
documents first, preserving their meaning and unique constraints. Create a named
topic document only when needed content has no suitable home; do not scaffold
empty documents or split a useful small guide mechanically. Topic documents hold
specialized guidance; nested `AGENTS.md` files hold directory-specific differences.

Leave conditional reading pointers in the root guide. Link related topic documents
where useful, using paths relative to each containing document. When language
changes require tests, link language guidance to the testing guidance instead of
duplicating its procedures. For example,
`docs/TYPESCRIPT.md` can link to `TESTING.md` for test changes; that document can
reference the verified runner configuration, and `docs/BUILD.md` can reference
`../esbuild.config.mjs` if it exists. These are examples, not required tools or paths.
Avoid duplicated rules and unnecessary circular reading chains.

Audit requests only propose moves; narrow edits do not authorize unrelated
extraction. Verify moved rules and their reading paths before removing originals.

### Maintenance

Update instructions when a command, boundary, convention, or reusable constraint
changes, or a recurring review finding reveals a missing durable rule. A one-off
fix or product-spec edit alone does not require an instruction update. Add the
smallest useful rule, check conflicts and placement, and remove stale guidance.

### Examples

Read only the example needed for the requested output:

- [Basic template](examples/basic-template.md): one small guide.
- [Agent plans](examples/agents-example.md): root guidance plus a portable reviewer.
- [Fuller guide](examples/Very-long-AGENTS.md): project-specific constraints.

Adapt examples; their project policies and illustrative paths are not evidence
about the target repository. Do not copy authoring notes or unknown details into
final instructions. Preserve existing user-selected policies when revising them.

## Validation checklist

- Inspect the effective instruction chain for the target runtime, including
  overrides and applicable ancestors. Distinguish files found from files loaded.
- Compare the requested scope with the diff; audits alone must leave no edits.
- Verify unique constraints survived any rewrite; resolve contradictions and
  keep nested rules local.
- Count each generated guide against the selected cap (for example,
  `wc -l AGENTS.md`); include the final line even without a trailing newline.
  Check actual runtime size limits separately when relevant.
- Check each new local link exists, resolves from its containing file, and has
  a reading trigger. Do not treat example paths as required repository files.
- Trace commands, skill names, and policies to evidence. Inspect scripts before
  running checks; verifying a deploy command's existence does not authorize it.
- Search only existing target files for `TODO`, `TBD`, and draft placeholders;
  inspect results rather than treating Markdown links or quoted examples as errors.
- Check subagent inputs, invocation handoff, ownership, verification, and output.
  Report whether artifacts are plans or installed configuration.
- Report checks actually performed and any limitations; do not equate file
  shape checks with successful behavior.

When maintaining this skill itself, use [behavioral scenarios](tests/scenarios.md)
for substantive workflow changes. Keep fixtures disposable and evaluate actual
outputs; do not load this test rubric during ordinary repository work.
