# Collection guidance

## Layout

- This is one Git repository. Each distributable skill lives in `skills/<name>/`
  with its own `SKILL.md`; do not add a root `SKILL.md`, nested `.git`, or submodule.
- Keep skill references, scripts, and data inside their skill directory so an
  individual installation remains self-contained. Resolve runtime resources
  relative to the skill's files, not the collection working directory.
- Before changing a skill, read its `SKILL.md`, README, applicable local
  `AGENTS.md`, and `CONTEXT.md` when present. Example `AGENTS.md` files are skill
  assets, not instructions for this collection.
- When adding or renaming a skill, update the root README's catalog and confirm
  discovery with `npx skills@latest add . --list` from the collection root.

## Questions

Use OMP's interactive `ask` tool for user decisions and clarification, including
Wayfinder and grilling, instead of numbered question lists in chat. Batch
independent questions, mark recommended options, and defer dependent questions
until their prerequisites are answered.

## Verification

From the collection root:

- Utility changes: `python3 -m unittest discover -s skills/scenario-maker/tests -v`.
- Evaluator changes: `python3 -m unittest discover -s skills/scenario-maker/evals -p 'test_*.py' -v`.
- Substantive Agent Builder workflow changes: use
  [its behavioral scenarios](skills/agent-builder/tests/scenarios.md).
- Run the affected utility or installer path as well as its automated tests.
  The Python checks require Python 3.12 or newer.
- Before running model-backed captures, read the root README's
  [evaluation tooling section](README.md#evaluation-tooling). It explains the
  external historical baseline and distinguishes paid model runs from offline tests.

## Historical material

Generated evaluation archives are excluded; keep reusable regression fixtures
under `skills/scenario-maker/evals/fixtures/`. Do not reintroduce captured copies
of whole skills into the distributable collection. Old issue numbers, handoffs,
and source commit IDs refer to the original repositories. For collection-wide
GitHub operations, resolve the collection's actual remote rather than assuming
one of the source repositories is the destination.
