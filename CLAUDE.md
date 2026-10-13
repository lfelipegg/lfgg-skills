# Claude Code guidance

`AGENTS.md` is the single source of truth for this collection and is shared with
Oh My Pi and Codex. Edit guidance there, not here; this file only imports it and
maps agent-specific tool names for Claude Code.

@AGENTS.md

## Claude Code tool mapping

- Where `AGENTS.md` says to use OMP's interactive `ask` tool, use
  `AskUserQuestion` with the same rules: batch independent questions (up to four
  per call), mark recommended options with "(Recommended)" as the first option,
  and defer dependent questions until their prerequisites are answered.
- Claude Code does not read `AGENTS.md` files on its own. When a skill directory
  has its own `AGENTS.md`, give it a sibling `CLAUDE.md` containing only
  `@AGENTS.md` (as `skills/scenario-maker/` does), and read the nested
  `AGENTS.md` before working in that skill.
