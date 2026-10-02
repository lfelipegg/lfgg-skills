# Agent Builder

A skill for creating, updating, and auditing compact repository agent guidance.
It inspects existing instructions and commands, preserves useful constraints,
and keeps narrow edits scoped. It can also draft portable subagent plans or
configure agents when installation is explicitly requested.

## Use

In Codex, invoke `$agent-builder`; in Claude Code, invoke `/agent-builder`.
For example:

- “Update AGENTS.md to use the test command defined in this repository.”
- “Audit our agent instructions, including overrides. Report findings only.”
- “Shorten AGENTS.md while preserving its unique constraints and existing docs.”
- “Plan two focused reviewers; the parent will coordinate. Do not install them.”

## Install

This skill is part of [LFGG Skills](../../README.md). From the collection root:

```bash
npx skills@latest add . --skill agent-builder
```

Copy the skill folder, including `SKILL.md`, `references/`, `examples/`, and
`tests/`, to the selected skill directory. `plans/` is implementation history
and is not needed to use the skill. Preserve an existing installation rather
than creating a second copy with the same name.

| Runtime | Project location | Personal location |
| --- | --- | --- |
| Codex | `.agents/skills/agent-builder/` | `~/.agents/skills/agent-builder/` |
| Claude Code | `.claude/skills/agent-builder/` | `~/.claude/skills/agent-builder/` |

See the official [Codex skill docs](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code skill docs](https://code.claude.com/docs/en/skills) for discovery,
other installation scopes, and invocation details. These locations were checked
2026-09-05; this repository's current location need not be changed to edit it.

Installing this skill and loading generated repository guidance are separate
steps. See [platform compatibility](references/platforms.md) for Codex discovery,
Claude Code's shared-guide import, and runtime-specific agent formats.

## Files

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Core workflow, output rules, and validation |
| [references/platforms.md](references/platforms.md) | Instruction discovery and installed-agent compatibility |
| [references/interview.md](references/interview.md) | Optional questions for consequential missing decisions |
| [references/subagents.md](references/subagents.md) | Portable plans, ownership, and invocation handoff |
| [examples/basic-template.md](examples/basic-template.md) | Minimal single-guide template |
| [examples/agents-example.md](examples/agents-example.md) | Guide plus a portable reviewer plan |
| [examples/Very-long-AGENTS.md](examples/Very-long-AGENTS.md) | Fuller project-specific example |
| [tests/scenarios.md](tests/scenarios.md) | Behavioral acceptance scenarios for skill revisions |
