# Basic guide template

Adapt the fenced guide to the target repository. Add only confirmed project
purpose, commands (with working directories), document links, and local policies.
Omit unavailable sections. The block contains no invented project facts; these
authoring notes are not part of the generated `AGENTS.md`.

```markdown
# Agent Guide

## Before editing

Read applicable shared and local instructions for the target runtime, then the
smallest relevant set of repository docs, manifests, and configuration files.
Inspect existing behavior and the requested requirements before choosing a fix.
Follow applicable instruction precedence and explicit user choices. Report
material conflicts between code and requirements; existing behavior may be a bug.

## Scope and authorization

Keep changes within the request and preserve unrelated user work. Honor permission
already given for scoped actions without asking again for routine file edits.
Use the established dependency and git policies. Confirm missing authorization
before destructive actions or external mutations outside the authorized scope.
Do not expose secrets or weaken validation, tests, authorization, accessibility,
privacy, or data safety to make work pass.

## Verification and delivery

Use commands confirmed in repository files or user answers. Inspect scripts
before running them; choose the smallest relevant checks and report failures
or checks that could not run. Add focused regression coverage for behavior
changes when practical. Do not report required failing checks as passed.

Summarize changes, verification, and remaining risks. Apply established acceptance
and release gates; do not infer authorization to merge, push, or deploy from
permission to edit files.

## Maintaining this guide

Keep only reusable operating rules and pointers to existing source-of-truth docs.
Put task progress, specs, plans, and decision records in their established homes.
Add a rule when it addresses a durable constraint or recurring mistake; remove
stale rules. Default to at most 200 lines unless the user selects another cap.
Remove repetition before splitting. Create local instruction files only for
meaningful differences, and state when linked supporting guidance must be read.
```

For an explicitly requested draft with unresolved decisions, append one
`Assumptions to confirm` section describing those decisions. Do not fill command
slots with guesses. Remove the section when finalizing; resolve necessary facts
or omit unsupported optional details.
