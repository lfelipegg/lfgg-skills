# LFGG Skills

A collection of agent skills maintained in one Git repository. Each skill is a
self-contained directory under `skills/`, with its own `SKILL.md` and supporting
resources. There are no submodules or nested Git repositories.

## Skills

| Skill | Purpose |
| --- | --- |
| [scenario-maker](skills/scenario-maker/README.md) | Generic and cross-model prompt authoring, comparison, and explicitly selected local model profiles. Writes prompts; does not generate media. |
| [scenario-maker-sdxl](skills/scenario-maker-sdxl/README.md) | SDXL 1.0 Base prompt authoring and adaptation. |
| [scenario-maker-krea-2](skills/scenario-maker-krea-2/README.md) | Open/local Krea 2 RAW and Turbo prompt authoring. |
| [scenario-maker-illustrious](skills/scenario-maker-illustrious/README.md) | Official Illustrious XL v0.1/v1.0 prompt authoring. |
| [scenario-maker-noobai](skills/scenario-maker-noobai/README.md) | NoobAI XL 1.1 epsilon and V-Pred 1.0 prompt authoring. |
| [scenario-maker-pony](skills/scenario-maker-pony/README.md) | Pony Diffusion V6 XL prompt authoring. |
| [scenario-maker-wan](skills/scenario-maker-wan/README.md) | Existing version-agnostic Wan T2V/I2V prompt authoring. |
| [scenario-maker-minimax-h3](skills/scenario-maker-minimax-h3/README.md) | Native local H3 Ref2VA, one-opening-image FL2VA/I2VA, and frame-derived still-edit prompt authoring. |
| [agent-builder](skills/agent-builder/README.md) | Create, update, and audit repository agent instructions such as `AGENTS.md`, and plan subagents. |
| [next-steps](skills/next-steps/README.md) | Save the current chat's progress, decisions, and remaining work to `docs/next-steps.md` with a prompt for continuing in a new chat. |

## Install

The [skills CLI](https://github.com/vercel-labs/skills) discovers the bundled skills and
lets you choose which skills and agents to install them for. It requires Node.js
and npm; Git is needed when installing from a Git repository.

From this collection's root, list skills without installing anything:

```bash
npx skills@latest add . --list
```

Install one skill or several from the local checkout:

```bash
npx skills@latest add . --skill scenario-maker
npx skills@latest add . --skill scenario-maker-pony --agent codex
npx skills@latest add . --skill agent-builder
npx skills@latest add . --skill next-steps
npx skills@latest add . --skill scenario-maker agent-builder next-steps
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
npx skills@latest add lfelipegg/lfgg-skills --skill scenario-maker agent-builder next-steps
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
    ├── next-steps/
    │   ├── SKILL.md
    │   └── CONTEXT.md
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

### Scenario Maker resource ownership

The generic skill owns the shared routing, output, preservation, composition,
format, video, character, tag, and wildcard contracts, all three utilities, and
both source CSVs. Each specialist owns its model profile; H3 also owns its two
byte-identical official guides. The generic comparison catalog receives managed
local copies of all seven profiles. Entry points, READMEs, and UI metadata are
maintained independently.

After changing an owned resource, synchronize its committed copies:

```bash
python3 scripts/sync_scenario_skills.py
python3 scripts/sync_scenario_skills.py --check
```

The utility resolves its default collection root from its own location, validates
the complete allowlisted map before writing, and never deletes unmanaged files.
`--check` is read-only and exits 1 on missing/different copies. Missing sources,
symlinks, escaping paths, aliasing, or unexpected specialist model resources fail
nonzero. Only changed managed files are copied. No runtime sibling resources,
symlinks, downloads, or installation-time build are needed; each package includes
its own optional character/tag utilities and CSV data. SQLite indexes and caches
are generated locally and ignored. Dataset duplication is intentional.

Invoking a specialist supplies only its model family, not a task, checkpoint
variant, route, invention permission, or released lock. A different explicit
family wins; an isolated specialist identifies the mismatch instead of using the
wrong dialect. Install the generic skill for unnamed requests and cross-family
work; explicit single-model use of the generic skill remains supported.

For substantive Agent Builder workflow changes, use its
[behavioral scenarios](skills/agent-builder/tests/scenarios.md). They are a manual
acceptance rubric, not an executable automated test suite.

For Next Steps workflow changes, use its
[behavioral checks](skills/next-steps/README.md#behavioral-checks) in disposable
projects. Inspect the generated handoff and continuation prompt; installer
discovery alone does not establish correct handoff behavior.

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

The model-split comparison is separate from that historical capture. It uses a
frozen current-monolith directory and does not require the old repository:

```bash
python3 skills/scenario-maker/evals/run_split.py \
  --baseline "$RUN/before" --candidate-root skills --out "$RUN/corpus" \
  --suite corpus --timeout 300 --jobs 3
python3 skills/scenario-maker/evals/run_split.py \
  --baseline "$RUN/before" --candidate-root skills --out "$RUN/boundary" \
  --suite boundary --timeout 300 --jobs 3
python3 skills/scenario-maker/evals/evaluate.py \
  --cases skills/scenario-maker/evals/cases.jsonl \
  --results "$RUN/corpus/formal/baseline" --out "$RUN/legacy-baseline-scores"
python3 skills/scenario-maker/evals/evaluate.py \
  --cases skills/scenario-maker/evals/cases.jsonl \
  --results "$RUN/corpus/formal/candidate" --out "$RUN/legacy-candidate-scores"
python3 skills/scenario-maker/evals/review_split.py \
  --results "$RUN/corpus" --boundary-results "$RUN/boundary" --out "$RUN/ai-review"
python3 skills/scenario-maker/evals/measure_split_context.py \
  --baseline "$RUN/before" --candidate-root skills \
  --results "$RUN/corpus" --boundary-results "$RUN/boundary" --out "$RUN/context-final.json"
```

Set `RUN` to a new ignored comparison directory after freezing the current source
and evaluation provenance, before runtime edits. The fixed model is
`openai-codex/gpt-6-astra`, high reasoning; authenticated captures and review are
paid model sessions, not offline tests. The corpus retains 744 attempts (124
requests, three repetitions per side); the 13 boundary cases add 54. Fresh output
directories are required, failures remain immutable, and there are no retries,
resumes, or best-of replacements. Candidate captures contain only the selected
standalone package.

Generator deadlines are 300 seconds; independent reviewers default to 900
seconds so they can finish complete evidence packets. Every review must copy
its packet's exact case ID and repetition; malformed output stays `not-run`.

Independent blinded AI semantic reviews and regression adjudication are a
separate migration assessment. They never populate the legacy evaluator's
human-only review criteria. Packaging, tests, and reduced instruction bytes do
not establish prompt-quality parity or rendered-media quality. Acceptance needs
one complete consistent snapshot, full captures/reviews, no unresolved new
contract failures, and measured ordinary-path context reduction including the
installed descriptions and actual read traces. Native host automatic selection
is not established by explicit isolated-skill captures.

## Consolidation provenance

This is a fresh Git repository, not a merge of the old commit histories. The
skills were imported from these published revisions:

| Skill | Source revision |
| --- | --- |
| scenario-maker | [`d5804da`](https://github.com/lfelipegg/scenario-maker-skill/tree/d5804da2c1f14715dfde1160641e2ca2d563cb5d) |
| agent-builder | [`d9e3927`](https://github.com/lfelipegg/agent-builder-skill/tree/d9e3927d4126bf82181cc093991ca304490163be) |

At consolidation, core skill instructions and runtime resources were preserved.
Collection navigation, repository-specific guidance, packaging ignore rules,
and historical evaluation dependencies were adapted. About 3 GB of generated
evaluation archives were left in the original Scenario Maker repository; the
initial collection was about 106 MB, mostly its bundled Danbooru lookup data.

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
