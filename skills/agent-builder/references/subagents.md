# Subagent plans and handoff

Use separate agents when independent work benefits from distinct context,
verification, or ownership. A small task can stay with the parent. Architecture,
frontend, backend, database, CI, documentation, or security boundaries are useful
signals, not a required roster of agents.

## Choose the artifact

A repository file such as `agents/ui-reviewer.md` is a portable prompt plan.
It is not automatically registered or executed by the runtime. Here `agents/`
is relative to the repository root, not an absolute filesystem path or a command.
Reuse an existing location if the repository already stores plans elsewhere.

Use a single file unless actual support material warrants a folder. Create
reference or script directories only when there is content to put in them.
If installed agents are requested, consult [platforms](platforms.md), inspect
existing configuration, and use the supported format for the target runtime.
Do not install agents or dispatch live workers merely to satisfy a planning request.

## Plan contract

Each plan states:

- Purpose and trigger: the work it helps with and when to stay inline.
- Inputs: task, acceptance criteria, relevant paths/diff, applicable instructions,
  needed domain context, and known verification commands.
- Ownership: files it may edit and areas it must not change. A review-only agent
  has no editable areas unless a later task explicitly assigns fixes.
- Verification: relevant sourced checks and how to report unavailable checks.
- Output: findings with evidence, or changed files and verification when fixing;
  include unresolved decisions and risks.

Keep concurrent write ownership non-overlapping. Overlapping read-only reviews
are fine. Ensure workers receive applicable root and local guidance; do not
assume the host automatically forwards the parent's context.

## Invocation and coordination

When a task authorizes delegation, the parent:

1. Reads the selected plan and relevant support files.
2. Supplies its instructions, concrete task, applicable guidance, file scope,
   and verification expectations through the available delegation tool or API.
3. Checks returned findings or diffs, integrates results, and runs appropriate
   final verification. Reports delegated work and unresolved issues.

If delegation is unavailable, use the plan inline and disclose that no separate
agent ran. If only plans were requested, deliver the artifacts and explain this
handoff without executing it.

The parent normally coordinates. Add `agents/orchestrator.md` only when a
separate reusable coordination role has a concrete purpose beyond what the
parent already does. Multiple workers alone do not require another agent.
