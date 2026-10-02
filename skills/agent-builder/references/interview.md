# Relevant missing decisions

Use this checklist for substantial setup or redesign after repository inspection.
It is a menu, not a required interview. Skip answered, irrelevant, and safely
omittable questions. Ask a consequential ambiguous question on its own; bundle
simple related choices when helpful. Continue independent authorized work.

| Decision | Ask only when it affects the output |
| --- | --- |
| Purpose and audience | What context changes how future agents should work? |
| Stack and commands | Which manifest, scripts, working directory, and runtime are canonical when evidence conflicts? |
| Source of truth | Where do requirements, domain language, design, decisions, and task records already live? |
| Guardrails | Which actions require authorization beyond the current task? |
| Dependencies | Is there an established policy for adding packages or restoring existing dependencies? |
| Git and worktrees | Does this repository require isolation, and what location/workflow is established? |
| Documentation | Which changes need task records, and where are they kept? |
| Delivery | Which acceptance checks, reviews, CI, release, and rollback expectations apply? |
| Local instructions | Which areas have meaningful differences from shared rules? |
| Skills | Which skills are confirmed available, and when should agents use them? |
| Delegation | Are portable plans or installed agents requested, for which distinct workstreams? |
| Response style | Is there a required summary format beyond reporting changes, checks, and risks? |

Do not suggest approval requirements for every routine action. Preserve existing
session authorization. Ask about unresolved policy only when needed; a missing
dependency policy does not block correcting a documented test command.

If task records are requested, reuse the current convention. When none exists,
a single task note may suffice. For users wanting separate history and follow-up
files, offer this optional format:

```text
docs/tasks/{number}-{timestamp}-{title}/summary.md
docs/tasks/{number}-{timestamp}-{title}/next-steps.md
```

For example, use `001-2026-09-05T15-30-00Z-update-tests`. Follow established
numbering and timezone conventions. Summaries cover request, decisions, changed
files, verification, and unresolved risks; next steps cover deferred work and
known owners or prerequisites. This is an optional convention, not a default
requirement for every non-trivial task.

For a draft, collect unanswered consequential choices in `Assumptions to confirm`.
For a final guide, ask only about necessary unresolved decisions and omit unknown
optional commands or sections. Do not turn silence into an answer or approval.
