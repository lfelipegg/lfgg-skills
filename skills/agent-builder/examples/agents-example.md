# Compact guide plus a portable reviewer plan

This example has two output files, fenced separately. Adapt paths and policies
to the target repository. The `agents/` folder is repository-relative and stores
prompt plans; it does not register runtime agents. The parent coordinates this
review, so no extra orchestrator is needed. Root and nested instructions remain
separate from the reviewer plan and follow the target runtime's discovery rules.

## AGENTS.md

```markdown
# Agent Guide

## Working rules

Inspect applicable shared/local instructions, relevant docs, manifests, and
configuration before editing. Follow instruction precedence and explicit user
choices. Treat code as observed behavior and specs as intended behavior; report
material conflicts instead of automatically preferring existing code.

Keep changes scoped and preserve unrelated user work. Honor existing authorization
for routine edits. Follow established dependency/git policy; obtain missing
authorization for destructive or external actions. Do not expose secrets or
weaken validation, checks, accessibility, privacy, or data safety.

Use confirmed commands for relevant verification and report checks that fail or
cannot run. Summarize changes, evidence, and remaining risks. Editing permission
does not itself authorize merge, push, or deployment.

## Focused UI review

When an authorized task benefits from separate UI review, read
[the reviewer plan](agents/ui-reviewer.md). Supply the plan, concrete task,
relevant diff/paths, applicable guidance, and verification expectations through
the available delegation mechanism. Inspect findings and integrate the result.
If delegation is unavailable, review inline and report that no separate agent ran.
The plan itself neither installs an agent nor authorizes dispatch.

## Maintenance

Keep durable rules and links to existing source-of-truth docs here; put temporary
task records elsewhere. Remove stale or repeated rules before splitting. Use
at most 200 lines unless the user specifies another cap. Add nested instruction
files only for meaningful local differences and explain when to read deeper docs.
```

## agents/ui-reviewer.md

```markdown
# UI Reviewer

## Purpose and inputs

Review user-facing changes when a focused accessibility, responsive-behavior,
or consistency pass helps. For a small change needing no separate pass, the
parent can work inline.

Receive the concrete task, acceptance criteria, relevant diff and file paths,
applicable shared/local guidance, existing design docs, and confirmed checks.
Use only the supplied scope and read additional relevant files as needed.

## Ownership

Review only: no editable files. Do not change UI, backend logic, migrations,
deployment configuration, secrets, generated files, or unrelated files.
Return proposed fixes as findings; implementation requires a separate assignment
with clear write ownership. Never expose secrets in the report.

## Review and verification

Check use of existing components and tokens, semantic HTML, keyboard access,
focus states, labels, visible text, and responsive behavior at relevant viewport
sizes. Flag design/copy conflicts against the existing source-of-truth docs.
Run relevant existing checks only when their definitions and side effects fit
the assigned review. Report unavailable checks and avoid claiming a browser
check was performed when only source code was inspected.

## Output

Return findings with file locations, impact, and suggested changes; include
checks actually performed and remaining UI risks. The parent assesses the
findings, handles any separately authorized fixes, and provides the final result.
```

For installed agents, translate the requested role using the verified target
format described in [platforms](../references/platforms.md). Do not copy these
Markdown plans into runtime configuration folders and assume they are registered.
