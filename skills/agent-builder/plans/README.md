# Implementation plans

Plan 001 was prepared 2026-09-05 against `48cae46`. It covers all eight findings from
the agent-builder review; implementation is complete with all seven behavioral scenarios passing.

| Plan | Priority | Effort | Depends on | Status |
| --- | --- | --- | --- | --- |
| [001: Improve agent-builder](001-improve-agent-builder.md) | P1 | M | None | DONE |
| [002: Selective AI Hero guidance](002-selective-aihero-guidance.md) | P1 | S | 001 | DONE |

Plan 001 used four steps: correct policy semantics, document platform
behavior and agent handoff, consolidate guidance, then validate outcomes.
The shared files make sequential editing simpler than parallel implementation.

No reviewed findings were rejected. New dependencies, a test framework, and
live agent installation are outside this change's scope.
