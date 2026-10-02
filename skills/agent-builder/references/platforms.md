# Platform discovery and integration

Read this when auditing effective instructions, handling overrides, or producing
platform-specific artifacts. Inspect the target runtime, starting directory,
and existing configuration; do not infer them from a filename alone. Ask only
when the distinction affects the requested output and remains unknown.

## Codex

Codex builds guidance at session start. Global guidance comes from `CODEX_HOME`
(default `~/.codex`), preferring `AGENTS.override.md` over `AGENTS.md`. Project
discovery walks from the project root to the current directory. At each level
it selects at most one file: `AGENTS.override.md`, then `AGENTS.md`, then configured
`project_doc_fallback_filenames`. Later, deeper instructions override earlier
ones. Empty files are skipped. Without a project root, only the current project
directory is checked.

The combined loading budget is `project_doc_max_bytes`, default 32 KiB; a line
cap is not that limit. A nested file outside the startup path is not necessarily
loaded automatically. Inspect relevant local instructions before editing there.

Inventory candidate files, configuration, and applicable ancestor guidance;
label each as active, shadowed, or not verified. To verify actual loading, start
a fresh session in the intended directory and request its instruction sources.
Read-only inspection can establish expected discovery, but cannot prove what an
existing session loaded. [Official discovery documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Codex custom agents use TOML files in project `.codex/agents/` or personal
`~/.codex/agents/`, with `name`, `description`, and `developer_instructions`.
Check the current schema and existing configuration before generating them;
portable Markdown plans are not installed agents. [Official subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Claude Code

Claude Code reads `CLAUDE.md`; do not assume it discovers `AGENTS.md`. For a
shared guide, a project `CLAUDE.md` can import `@AGENTS.md`. Preserve other
instructions when adding that import. Ancestor instructions and relevant nested
files participate in loading; check the runtime's current memory rules and
imports for the requested directory. Verify loaded memory with `/context` in
a fresh session. [Official memory documentation](https://code.claude.com/docs/en/memory).

Claude Code custom agents are Markdown files with YAML frontmatter under project
`.claude/agents/` or personal `~/.claude/agents/`. Check supported fields and
existing scope before creating them. This differs from an arbitrary repository
`agents/` folder. [Official subagents documentation](https://code.claude.com/docs/en/sub-agents).

## Practical audit boundaries

Use `rg --files --hidden` with relevant filename globs for candidate discovery;
include configured fallback names and runtime-specific files. Inspect applicable
ancestors outside that listing separately. Account for ignored relevant files
with targeted reads; avoid scanning dependency trees, generated artifacts, or
unrelated personal configuration. File discovery does not establish precedence.

Inspect command definitions before running anything. Auditing an instruction
source or checking whether a deployment script exists does not authorize
executing that script. Report unavailable configuration or runtime verification
as a limitation, not proof that no override exists.

Platform facts and linked official sources verified 2026-09-05. Recheck them
when the runtime/version changes or observed discovery differs. Other runtimes
require their own verified loading and agent-registration rules.
