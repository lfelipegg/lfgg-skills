# LFGG Skills

A collection of agent skills maintained in one Git repository. Each skill is a
self-contained directory under `skills/`, with its own `SKILL.md` and supporting
resources. There are no submodules or nested Git repositories.

## Skills

| Skill | Purpose |
| --- | --- |
| [scenario-maker](skills/scenario-maker/README.md) | Write, refine, and batch model-aware prompts for AI image and video workflows. Writes prompts; does not generate media. |
| [agent-builder](skills/agent-builder/README.md) | Create, update, and audit repository agent instructions such as `AGENTS.md`, and plan subagents. |

## Install

The [skills CLI](https://github.com/vercel-labs/skills) discovers both skills and
lets you choose which skills and agents to install them for. It requires Node.js
and npm; Git is needed when installing from a Git repository.

From this collection's root, list skills without installing anything:

```bash
npx skills@latest add . --list
```

Install one skill or both from the local checkout:

```bash
npx skills@latest add . --skill scenario-maker
npx skills@latest add . --skill agent-builder
npx skills@latest add . --skill scenario-maker agent-builder
```

These commands install into the current project by default. To install into a
different project, run the command there and replace `.` with the path to this
checkout. Add `--global` for a personal installation, or `--agent codex` /
`--agent claude-code` to select an agent. Review existing installations before
replacing them; do not keep duplicate installations with the same skill name.

If this collection is published as `lfelipegg/lfgg-skills`, the equivalent remote
commands are:

```bash
npx skills@latest add lfelipegg/lfgg-skills --list
npx skills@latest add lfelipegg/lfgg-skills --skill scenario-maker agent-builder
```

The remote commands require that repository to exist and contain these files.
This local consolidation does not create or publish a GitHub repository.

For manual installation, copy an individual `skills/<name>/` directory, not the
whole collection, into your agent's skill directory. Keep its supporting files
together. Merely cloning the collection does not install it for every agent.

## Repository layout

```text
lfgg-skills/
├── .git/                 # Only repository metadata directory
├── .gitignore
├── AGENTS.md
├── README.md
└── skills/
    ├── agent-builder/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── examples/
    │   └── tests/
    └── scenario-maker/
        ├── SKILL.md
        ├── references/
        ├── scripts/
        ├── docs/
        ├── tests/
        └── evals/
```

The tree highlights the entry points and supporting directories; each skill also
retains its own README and other source resources. Run Git commands from the
collection root. To add a skill, create `skills/<name>/SKILL.md` with `name` and
`description` YAML frontmatter, include its resources inside that directory, add
it to the table above, and check discovery with `npx skills@latest add . --list`.
Do not initialize another Git repository inside a skill.

## Development checks

The Python utilities use the standard library. Run the existing utility and
evaluator regression suites from the collection root with Python 3.12 or newer:

```bash
python3 -m unittest discover -s skills/scenario-maker/tests -v
python3 -m unittest discover -s skills/scenario-maker/evals -p 'test_*.py' -v
```

Smoke-test the relocated character generator:

```bash
python3 skills/scenario-maker/scripts/character_generator.py --seed 7 --count 1 --format prose
```

For substantive Agent Builder workflow changes, use its
[behavioral scenarios](skills/agent-builder/tests/scenarios.md). They are a manual
acceptance rubric, not an executable automated test suite.

### Evaluation tooling

Scenario Maker's evaluation tooling, cases, probes, rubric, and fixtures are
included. The three captured `case-11` attempts needed by the evaluator regression
are retained under `skills/scenario-maker/evals/fixtures/lookup-trace/`; they are
copied from the original baseline, not newly generated acceptance evidence.

Historical runs and reviews remain in the original repository. Generated
`baseline/`, `capture-checks/`, `comparisons/`, `results/`, and `reviews/` directories
under `skills/scenario-maker/evals/` are ignored here.

The capture tool compares against the fixed historical commit
`5fcc3d0eded83c6a9aaf472a1dc8d5ce24011d9d`. That history is not part of this new
repository, so capture requires an explicit `--baseline-repo` pointing to a clone
of `lfelipegg/scenario-maker-skill` containing that commit. For example, when the
original clone is next to this collection:

```bash
python3 skills/scenario-maker/evals/run_baseline.py \
  --baseline-repo ../scenario-maker \
  --candidate-worktree --smoke \
  --out skills/scenario-maker/evals/capture-checks/local-smoke
```

This capture command requires OMP and authenticated access to its configured
model. It launches model sessions; it is not part of the offline regression
suite. Choose a new output directory for each run. The evaluator's `--results`
option can also read recorded evidence directly from the original repository.

## Consolidation provenance

This is a fresh Git repository, not a merge of the old commit histories. The
skills were imported from these published revisions:

| Skill | Source revision |
| --- | --- |
| scenario-maker | [`d5804da`](https://github.com/lfelipegg/scenario-maker-skill/tree/d5804da2c1f14715dfde1160641e2ca2d563cb5d) |
| agent-builder | [`d9e3927`](https://github.com/lfelipegg/agent-builder-skill/tree/d9e3927d4126bf82181cc093991ca304490163be) |

Core skill instructions and runtime resources are preserved. Collection
navigation, repository-specific guidance, packaging ignore rules, and historical
evaluation dependencies were adapted. About 3 GB of generated evaluation
archives were left in the original Scenario Maker repository; the working
collection is about 106 MB, mostly its bundled Danbooru lookup data.

Migration checks passed: the skills CLI discovered and installed both skills
into a disposable Codex project; all 19 Python regression tests passed; installed
runtime resources matched the original source bytes. The character generator,
bundled-data lookup, historical baseline extraction, and relocated candidate
snapshot were exercised. No model-backed prompt evaluation was rerun.

The original repositories, local installations, commit histories, and GitHub
issues were not deleted, archived, redirected, or transferred. Historical
handoffs and plans are retained as history, not current collection instructions.
Existing Scenario Maker issues still use its original tracker; collection-wide
work must not be sent there automatically.
