# Next Steps

A skill that turns the current chat into `docs/next-steps.md`: a concise summary
of what happened and a copy-ready prompt for continuing in a new chat.

## Use

In Codex, invoke `$next-steps`; in Claude Code, invoke `/next-steps`.
For example:

- “Use next-steps to save this chat so I can continue in a fresh conversation.”
- “Record the plan we agreed on and the prompt to start its first unfinished step.”
- “Refresh docs/next-steps.md with what we finished and what is still blocked.”

The skill writes into the active project's `docs/` directory, creating it if
needed. It does not write into its own installation directory. If the handoff
already exists, it refreshes that file instead of appending a chat archive,
preserving relevant decisions and unfinished work while replacing stale state.

## What the handoff contains

- The goal and scope.
- Work completed in the chat, including planning or investigation outcomes.
- Decisions and constraints needed to avoid repeating or undoing work.
- Observed verification results, known failures, and important unverified state.
- Ordered next steps and any blockers or unresolved decisions.
- One fenced continuation prompt ready to paste into a new chat.

The continuation prompt directs the next assistant to read project guidance and
the handoff, check relevant current state, and resume agreed work. It does not
require approval again for already authorized steps or turn proposals into
permission to implement. When no agreed work remains, it says so and asks for
the user's next goal rather than inventing tasks.

Only available chat context and project evidence can be recorded. Missing
history and unverified claims remain explicit; secrets and unrelated private
conversation are excluded. Generating a handoff does not execute its next steps,
commit changes, push, or update a tracker.

## Continue in a new chat

Open a new chat with access to the same project and paste the block under
**Prompt for a new chat** in `docs/next-steps.md`. Keep the file available to that
chat; the prompt uses it for details instead of duplicating the entire handoff.

## Install

This skill is part of [LFGG Skills](../../README.md). From the collection root:

```bash
npx skills@latest add . --skill next-steps
```

For manual installation, copy the entire `skills/next-steps/` directory into your
agent's skill directory. The skill requires file read/write access but has no
runtime scripts or external service dependency.

## Files

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Handoff workflow, output contract, and evidence safeguards |
| [CONTEXT.md](CONTEXT.md) | Handoff, continuation prompt, and agreed-next-step terminology |

## Behavioral checks

When changing the workflow, exercise it in disposable projects with synthetic
chat context. Inspect the written file, not just a proposed answer:

- **Partial work and refresh:** carry forward a useful prior constraint and an
  unresolved task, retire a resolved blocker, preserve a known verification
  failure, and select the first remaining authorized step.
- **Planning only:** record the plan as completed planning, not implementation;
  a proposed but unapproved plan must not become authorized work.
- **Nothing left:** report completion without inventing a next phase. The prompt
  should ask for a new goal, not re-request approval for finished work.
- **Limited context:** label retained historical claims, avoid fabricated checks,
  and omit secret values from both the summary and the continuation prompt.

Confirm collection discovery with `npx skills@latest add . --list` from the
collection root. Discovery checks packaging, not the behavior of generated
handoffs.
