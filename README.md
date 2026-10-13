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
├── AGENTS.md             # Shared agent guidance (OMP, Codex, Claude Code)
├── CLAUDE.md             # Imports AGENTS.md for Claude Code
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
directories are required, failures remain immutable, and generators have no
retries, resumes, or best-of replacements. Fresh review campaigns likewise have
no automatic recovery. The explicitly authorized review-only exception below
does not change generator behavior. Candidate captures contain only the selected
standalone package.

Generator deadlines are 300 seconds; independent reviewers default to 900
seconds so they can finish complete evidence packets. Every review must copy
its packet's exact case ID and repetition; malformed output stays `not-run`.

`review_split.py` passes the review request through argv and launches reviewers
with `stdin=subprocess.DEVNULL`. This supplies immediate EOF even when the
runner inherits a held-open pipe; the same launch serves initial reviews and
independent adjudications. Offline EOF regression and guarded startup proof do
not establish successful provider execution or semantic acceptance.

Independent blinded AI semantic reviews and regression adjudication are a
separate migration assessment. They never populate the legacy evaluator's
human-only review criteria. Packaging, tests, and reduced instruction bytes do
not establish prompt-quality parity or rendered-media quality. Acceptance needs
one complete consistent snapshot, full captures/reviews, no unresolved new
contract failures, and measured ordinary-path context reduction including the
installed descriptions and actual read traces. Native host automatic selection
is not established by explicit isolated-skill captures.

#### Fresh acceptance preparation

`evals/review_acceptance.py` prepares a new complete assessment without invoking
OMP, including version/provider probes. It never resumes the stopped recovery:
411 fresh initial judgments, every required new independent adjudication, and
one separately retained adjudication of the original baseline-only `h3-dev-02`,
attempt 2 allegation. Old initial judgments are not reused.

From the collection root, `ROUND` points to the unchanged round-2 captures and
`ACCEPTANCE` to a new sibling directory outside all retained campaigns:

```bash
python3 -B skills/scenario-maker/evals/review_acceptance.py prepare \
  --results "$ROUND/corpus" --boundary-results "$ROUND/boundary" \
  --source-review "$ROUND/ai-review" --candidate-root skills --out "$ACCEPTANCE"
python3 -B "$ACCEPTANCE/ai-review/provenance/review_acceptance.py" validate \
  --out "$ACCEPTANCE"
```

Preparation checks all 798 captures and current runtime/input manifests, freezes
411 packets and their side map, and retains the complete seven-module evaluator
import closure, reviewer system and captured config. Prompt/input drift blocks
reuse; preparation does not synchronize or repair it. `preparation.json` binds
the original evidence, fixtures, rubric, prior applicable context/packaging proof,
historical label alignment, evaluator differences and exact future execution
argv/managed handle. Prior packaging/context checks are not presented as rerun.

For the separately authorized repaired-source capture wave, supply **both**
`--capture-preparation` and `--package-smoke-proof`; one alone is rejected.
`CAPTURES` points to its completed frozen wave, `PACKAGE_PROOF` to the actual
isolated-package smoke JSON, and `HISTORICAL_REVIEW` to the original round-2
source review. Use a fresh `ACCEPTANCE` directory outside all retained campaigns:

```bash
python3 -B skills/scenario-maker/evals/review_acceptance.py prepare \
  --results "$CAPTURES/corpus" --boundary-results "$CAPTURES/boundary" \
  --source-review "$HISTORICAL_REVIEW" --candidate-root skills \
  --capture-preparation "$CAPTURES/preparation.json" \
  --package-smoke-proof "$PACKAGE_PROOF" --out "$ACCEPTANCE"
python3 -B "$ACCEPTANCE/ai-review/provenance/review_acceptance.py" validate \
  --out "$ACCEPTANCE"
```

This explicit scope binds the authorized repaired full-package identity, both
capture manifests, fresh context/read-trace gates, observed managed terminal
outcome, and exact runtime hashes from the isolated-package proof. The runtime-only
smoke identity is not the complete capture identity. Without these scope inputs,
the original unchanged-capture identity and ancillary-proof guards remain intact.

Historical preparation independently rebuilds the original source review's
own capture roots, packet labels, and all three raw repetitions. Fresh repaired
outputs or side maps never replace that evidence. Both fresh and historical
bindings are rechecked during validation; no old campaign is rewritten or resumed.
The new scope changes preparation bindings only, not review criteria, source
requests, acceptance gates, or execution authorization.

Only a separately authorized `execute` may consume that frozen command. It
permanently claims `launch.json`, rechecks all bindings before runtime observation,
and rejects repeated, resumed or replacement execution. Use the exact retained
argv, a managed process and no enclosing shell deadline. Readiness
`"event": "acceptance_started"` proves runner startup only; concurrency three
is not a canary or automatic stop-on-first-failure policy.

The fresh `ai-review/summary.json`, supplemental `historical-disposition.json`
and hash-linked `combined-outcome.json` remain distinct. Missing or incomplete
historical adjudication blocks the combined result even when fresh reviews pass.
Runner PID/start identity, actual runtime banner, raw streams and terminal status
are retained at execution, not invented during preparation. Abrupt interruption
requires observed external stop evidence under the schema documented by
`observe_interruption()`; `record-interruption` neither signals processes nor
manufactures `execution.json`, and never authorizes another launch.

`execution.json` is the runner's own finalization/return-code record, not an
independent observation of its OS exit. Final acceptance disposition must also
retain the managed service's actual terminal result and match it to that record.
A missing/mismatched service exit or a signal after finalization blocks acceptance
even if a combined summary was already written. Preserve external evidence
separately; do not rewrite the runner's terminal records.

Offline preparation and synthetic subprocess verification do not establish
provider/auth availability or semantic acceptance. The current prepared directory
and authorization boundaries are recorded in [the handoff](docs/next-steps.md).

#### Authorized review-only recovery

`evals/review_recovery.py` implements the bounded exception recorded in
[the current handoff](docs/next-steps.md): reuse 200 verified initial reviews
from the interrupted round-2 campaign, supply its three interrupted and 208
unstarted judgments, and independently adjudicate the retained baseline-only
`h3-dev-02`, attempt 2 allegation plus every later hard-failure allegation.
It is deliberately not a general resume/retry tool. Finished, failed, recovered,
invalid, or differently populated source campaigns are rejected.

From the collection root, with `SOURCE_REVIEW` pointing to that original
`ai-review` directory and `RECOVERY` to a new nonoverlapping directory:

```bash
# Offline: validates all 798 captures, 411 frozen packets and 200 reused reviews.
python3 skills/scenario-maker/evals/review_recovery.py plan \
  --source-review "$SOURCE_REVIEW" --out "$RECOVERY" --jobs 3
python3 skills/scenario-maker/evals/review_recovery.py status --out "$RECOVERY"

# Paid: invoke only in the separately scoped Task C, once.
python3 -u skills/scenario-maker/evals/review_recovery.py run --out "$RECOVERY"
```

Planning preserves the original campaign and hashes its complete inventory,
including interrupted traces. New preparation retains exact packet, fixture,
rubric, side-map, system/config and evaluator-code bindings in `plan.json` and
`manifest.json`. Source, preparation or tool-code drift blocks launch.
The fixed reviewer controls remain `openai-codex/gpt-6-astra`, high reasoning,
900 seconds, fresh sessions and read-only declared tools.

`run` exclusively claims permanent `launch.json`; an interrupted or blocked
launch cannot be repeated or resumed. It runs only the 211 missing initial slots,
then all required fresh independent adjudications. Do not create another plan
to replace failed judgments or select best-of results. Reused reviews remain
referenced at their original physical paths; new reviews, adjudication packets
and raw evidence live under `RECOVERY`. Final `summary.json` and `manifest.json`
expose every reused/new record path, packet/record/raw hash, provenance and
evidence-backed disposition, retaining the original full-coverage acceptance
gates. A partial assessment never passes.

For long paid execution, use a managed process with no enclosing deadline and
readiness matching `"event": "recovery_started"`; save the returned process
handle before handing off. The runner retains PID/argv/version in `launch.json`,
completion events in `completion-stdout.txt`, and terminal status/exit code in
`execution.json`. Offline `status` revalidates retained hashes and reports valid
reused/new/missing reviews, adjudication coverage and validation errors.
`state: "started"` records a launch, not proof that its process is still alive.
Status may be slow because it hashes the complete frozen evidence; do not poll
in a loop. Authentication, provider availability and real semantic acceptance
are not established by planning or synthetic tests.

#### Stopped review-only recovery: not accepted

The user authorized a controlled stop of the claimed recovery on 2026-10-10.
The runner was suspended to prevent further queued launches, its three isolated
worker groups were terminated, and the runner was killed. The final process
snapshot showed no remaining runner or workers; the managed service reported
exit 137. Task D is closed with an unsuccessful, interrupted disposition—not
semantic acceptance.

Post-stop offline validation found 200 valid reused reviews, zero valid new
reviews, 102 invalid timeout attempts, 211 missing valid judgments, and no valid
independent adjudication of the one required. No validation errors were reported.
The sealed plan and original review-manifest hashes remain unchanged.

The stop bypassed finalization: `execution.json` and `summary.json` are absent,
and the retained manifest/status still say `started` and `not assessed`.
That filesystem state is not evidence of a live process. Actual signal/process
evidence and the gate-by-gate disposition are retained outside the recovery in
`controlled-assessment-stop.json` and `controlled-assessment-outcome.json` under
the comparison root named in [the handoff](docs/next-steps.md).

In that stopped campaign, full review coverage and independent adjudication were
not met; boundary and three-repetition semantic protection gates were not
established. Complete capture, packaging, and context evidence did not substitute
for them. Its baseline-only `h3-dev-02`, attempt 2 allegation had no adjudication
in that campaign; the later separate fresh assessment below confirmed it.
Timeouts are unavailable judgments, not semantic failures of the skill prompts.
Do not resume/replan this recovery or manufacture terminal artifacts. The live
reviewer stdin repair was separately authorized and verified offline; frozen
provenance and stopped campaigns remain unchanged. Any further provider/model
diagnostic or acceptance campaign requires separately scoped authorization.

#### Completed fresh acceptance: not accepted

The separately authorized frozen assessment completed all 411 fresh initial
reviews, both required new independent adjudications and one separate historical
adjudication, using the unchanged 798 captures. All 414 judgments were valid;
none was reused, retried or replaced. Its managed process independently exited 1,
matching exception-free runner finalization. Retained-evidence validation reported
zero errors and no remaining wave processes.

Semantic acceptance failed: `h3-guide-01`, attempt 3, independently confirmed a
candidate audio-permission regression—unrequested audio became prohibited rather
than `Unspecified`. Baseline passed that criterion in all three repetitions;
candidate failed one. `split-invoke-illustrious`, attempt 3, also retains a
`not-run` canonical-tag criterion because the capture contains a backgrounded
lookup launch but no completion/results. Valid JSON is not complete criterion
coverage. The separately adjudicated historical H3 allegation is baseline-only,
not a candidate regression.

The fresh summary, historical disposition, combined runner outcome and
externally closed disposition remain distinct under the acceptance directory
identified in [the handoff](docs/next-steps.md). This single-use assessment is
closed and cannot be resumed or repeated. No source repair, synchronization,
recapture or further paid assessment is authorized by its completion.

The separately authorized offline source repair is complete: the shared Danbooru
workflow now requires terminal lookup status/results and a cold-build-aware
bounded deadline; the owning H3 profile adds a general audio-state fidelity check.
Managed copies were synchronized and all eight isolated packages passed offline
utility/resource smoke checks; both official H3 guide hashes were preserved.
This is an implemented mitigation, not semantic acceptance. The repaired source
invalidates unchanged-capture reuse. The user subsequently authorized both
complete fresh capture suites; all 798 captures completed successfully in a
fresh frozen wave, with independently matched managed exit 0 and passing offline
context gates. Separately authorized offline preparation is also complete: all
411 fresh packets, independent original historical evidence, and all six binding
gates passed actual preparation/frozen-CLI validation; 90 offline evaluator tests
passed. The user subsequently authorized the complete paid assessment. It is
now closed **not accepted**: all 415 judgments were valid (411 initial, three
fresh adjudications, one separate historical adjudication), but `wild-12`
attempt 2 omitted the first-event speaker ID and two criteria remain `not-run`.
Independent managed exit 1 matched exception-free runner finalization; retained
evidence verification passed with zero errors. No retry or further campaign is
authorized. See [the current handoff](docs/next-steps.md) for evidence and limits.


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
