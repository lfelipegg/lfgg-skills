# Plan 001: Make agent-builder smaller and more reliable

## Status and objective

- Status: DONE
- Priority: P1
- Effort: M
- Risk: medium; these instructions affect future agents' decisions.
- Dependencies: none; execute the steps below in order.
- Planned against: `48cae46`, 2026-09-05.
- Workspace: `/home/mothmanex/.codex/skills/agent-builder`.

Implement all eight reviewed improvements: authorization, conflict handling,
instruction discovery, subagent integration, repetition, scoped interviews,
consistent size/placeholder rules, and behavioral validation. Preserve the
skill's central guarantees: inspect first, never invent repository facts,
preserve user preferences, retain unique durable constraints, and create only
the guidance needed by the requested task.

This is one documentation change, not a new framework or application. No
dependencies, production agent installation, or product features are needed.

## Current state

The repository contains five tracked Markdown files and no application build
or test configuration:

- `SKILL.md`: entrypoint, 863 lines / 4,372 words; YAML `name` and `description`,
  followed by workflow, modes, interview, routing, examples, and quality gates.
- `README.md`: human-facing overview and installation guidance, 267 lines;
  duplicates much of the entrypoint.
- `examples/basic-template.md`: small-repository template, 134 lines.
- `examples/agents-example.md`: root guide and two example agent prompts,
  197 newline-counted lines; several output files share one Markdown example.
- `examples/Very-long-AGENTS.md`: fuller project-specific example, 198 lines.

Evidence to locate before editing; line numbers describe the baseline:

| Location | Current text or behavior | Problem |
| --- | --- | --- |
| `examples/basic-template.md:63` | Dependency permission rule followed by `Do not delete, overwrite, push, deploy, force-push...without explicit approval.` | Routine authorized edits can trigger redundant permission requests. |
| `examples/Very-long-AGENTS.md:46` | Conflict priority ranks current code above specs and `AGENTS.md`. | Existing bugs can be treated as authoritative behavior. |
| `SKILL.md:808` | Audit search uses `find . -name AGENTS.md -print`. | Does not cover overrides, configured fallback names, or ancestor guidance. |
| `SKILL.md:683` | Produces `agents/{name}/subagent.md`. | Does not distinguish prompt plans from runtime configuration. |
| `SKILL.md:96` | Standard Mode runs the full interview for missing facts. | A narrow edit can expand into unrelated policy choices. |
| `SKILL.md:451` | `If the draft approaches 180 lines, stop adding detail and split files.` | Conflicts with Small Repo Mode's 200-line split threshold. |
| `SKILL.md:413`, `:786`, `:859` | Placeholder removal and retention instructions differ. | Draft assumptions and final instructions are not consistently distinguished. |

The entrypoint already has useful routing language at lines 507–508: link to
the detailed file and retain the rule that determines when to read it. Apply
that same pattern to the skill itself. Keep ordinary Markdown headings,
relative reference links, and the existing frontmatter identity.

## Scope and execution boundaries

Modify:

- `SKILL.md`
- `README.md`
- All three existing files under `examples/`
- `plans/README.md` and this plan, only for status and validation results.

Create only these supporting documents:

- `references/platforms.md`: discovery and runtime-specific compatibility.
- `references/interview.md`: optional broader interview checklist.
- `references/subagents.md`: planning criteria, ownership, and invocation handoff.
- `tests/scenarios.md`: reproducible behavioral scenarios and acceptance rubric.

Do not edit other installed skills, user/global agent configuration, or unrelated
repository files. Do not create actual `.codex/agents` configurations in this
skill repository. Do not install dependencies, commit, push, or publish as part
of this plan unless subsequently requested. Preserve concurrent user edits.

Before implementation, run:

```bash
git status --short
git diff --stat 48cae46..HEAD -- SKILL.md README.md examples references tests
```

Review any drift and reconcile it with the intended behavior before editing.
Routine line movement does not require user input. If a newer explicit policy
contradicts this plan, report the conflict and continue unaffected work.

## Step 1: Correct authorization and conflict handling

Update guardrail examples in `SKILL.md` and all three templates together.

- Honor authorization already established by the request or conversation.
- Allow routine, reversible changes within that scope. Do not make ordinary
  file updates or removals require a second approval merely because they are
  described as overwriting or deleting.
- Retain protection against destructive actions outside authorized scope,
  loss of user work, secret exposure, and unauthorized external mutations.
- Treat dependency and git policies as repository/user choices; do not inject
  a universal dependency-install approval policy into every generated guide.
- Remove the fuller example's code-first conflict hierarchy. Distinguish
  observed implementation from intended requirements. Follow applicable
  instruction precedence; surface material unresolved conflicts without
  automatically treating either stale prose or buggy code as correct.

Verify with `git diff --check` (exit 0), then review the complete diff for
`SKILL.md` and `examples/`. Authorization must remain bounded; the fix must not
grant blanket permission to push, deploy, or destroy data.

## Step 2: Define discovery and the subagent handoff

Create `references/platforms.md` and `references/subagents.md`; link them at
the points where the entrypoint selects discovery or subagent work.

- Discover the target agent/runtime from the task and repository. Ask only if
  the distinction affects the requested output and cannot be established.
- Describe root, ancestor, nested, override, and configured fallback guidance
  where the target runtime supports them. Explain which files are actually
  loaded and how to verify effective instructions; do not imply every nested
  file is automatically loaded from a root session.
- Keep runtime facts separate from project conventions. For Codex, document
  override precedence, the root-to-current-directory discovery chain, and the
  configured byte limit. The 200-line convention is an editorial budget, not
  a runtime limit.
- Label repository `agents/*.md` documents as portable prompt plans. Include
  an explicit handoff: the parent reads the chosen plan and supplies its
  instructions and task context through the available delegation mechanism.
- If the user requests installed agents, inspect the target runtime's current
  supported format and existing configuration, then generate only what was
  requested. Planning alone does not authorize installation or live delegation.
- Make a separate orchestrator optional when the parent already coordinates
  the work. Retain clear inputs, edit boundaries, verification, and outputs.
- Adapt `examples/agents-example.md` to show this distinction and handoff.

Authoritative sources checked during the review; recheck before encoding
version-sensitive details:

- [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

The reviewed Codex docs describe custom-agent TOML files in `.codex/agents/`
or `~/.codex/agents/`. Do not assume that layout applies to other runtimes.
For other platforms claimed by the README, verify their official documentation
before stating discovery or installation behavior; disclose unverified support.

Verify with `git diff --check` (exit 0) and inspect the new relative links and
example handoff. Record the supporting URLs and verification date in the
platform reference. No actual runtime configuration should be installed.

## Step 3: Consolidate the workflow and defaults

Rewrite the entrypoint after the correctness fixes so obsolete text is not
simply moved into references.

- Keep one core workflow: inspect, choose requested output, resolve relevant
  unknowns, edit/draft, validate, report.
- Give targeted updates and read-only audits explicit short paths. A one-rule
  edit must not require an interview about unrelated team or deployment policy.
  An audit-only request returns findings without changing the target repository.
- Move the comprehensive interview to `references/interview.md`; use it as a
  menu of consequential missing decisions, not a mandatory questionnaire.
- Merge overlapping creation modes; retain quick-draft and initial-setup
  differences only where they change output behavior.
- Reuse existing documentation names and locations first. Present new paths
  as defaults only when a needed destination is absent. Do not create empty
  scaffolding merely because the project is new.
- Keep one content-routing table, one maintenance rule, and one checklist.
  Delete duplicated red flags, counters, section inventories, and generic advice.
- Keep the existing default cap of at most 200 lines per generated `AGENTS.md`,
  with explicit user overrides honored consistently by validation. Remove the
  automatic 180-line split. Remove repetition first; split only when useful
  scope or necessary remaining detail warrants it. Do not pad tiny guides.
- Final operating instructions contain confirmed commands, paths, skills, and
  policies. Omit unknown optional sections. For an explicitly requested draft,
  isolate unresolved assumptions in one labeled section; never present guessed
  commands as ready to run. Templates may have instructional placeholders,
  clearly identified as requiring adaptation before final use.
- Reduce the README to purpose, invocation examples, installation, file map,
  and links. Update all examples to demonstrate the same rules. Preserve useful
  project-specific constraints in the fuller example and its existing filename.

Before deleting or moving rules, keep a temporary inventory of unique durable
constraints and their resulting locations. This is a review aid, not another
permanent repository document. Every intentional removal needs a short reason.

Verify with `wc -l -w SKILL.md README.md examples/*.md references/*.md` and
`git diff --check`. The entrypoint and README must be smaller than their
baselines, without compressing paragraphs merely to manipulate line counts.
Check that each reference has a task-specific loading trigger. Review the
inventory to confirm that shortening preserved unique constraints.

## Step 4: Add and run behavioral acceptance scenarios

Create `tests/scenarios.md` with the prompts, minimal fixture contents, expected
observable outcomes, and failure conditions below. Fixtures live in disposable
temporary directories when executed. Do not add a testing framework or pretend
that heading/regex checks prove agent behavior.

| Scenario | Fixture and request | Required outcome |
| --- | --- | --- |
| Narrow authorized update | Existing guide and package manifest with `test:unit`; ask to replace the guide's stale test command. | Only the requested command changes; no redundant approval, policy interview, scaffolding, or product edit. |
| Effective discovery | Root guide, nested guide, and same-directory override with conflicting test commands; request an audit from the nested directory. | Audit identifies applicable sources and override behavior for the target runtime; does not rewrite an inactive file or mutate audit targets. |
| Preserve constraints | Guide above 200 lines containing repeated prose, unique safety rules, and existing `docs/conventions/`; ask to shorten it. | Unique constraints survive, existing destinations are reused, and useful split guidance has a reading trigger. |
| Requirements conflict | Spec requires rejecting invalid input while code accepts it; request an instruction audit. | Reports the discrepancy; does not bless existing behavior merely because code currently does it. |
| Portable agent plan | Ask for two focused review-agent plans without installation; existing parent coordinates tasks. | Explicit invocation handoff, bounded ownership, no installed configuration, no mandatory extra orchestrator, and no live delegation merely to create plans. |
| Draft versus final | Empty repo with no commands; request a fast draft, then a final minimal guide without supplying more facts. | Draft clearly separates assumptions; final guide omits unsupported executable details and unnecessary scaffolding. |
| Size policy | First request a useful 190-line single-file guide remain single-file; separately specify a 240-line cap. | No automatic split at 180; validation honors the explicit cap instead of silently reinstating 200. |

Run scenarios in fresh isolated agent sessions when available, using only the
candidate skill, fixture, and user prompt as input. Keep the expected rubric
out of the executing agent's prompt. Judge actual diffs and outputs against it.
If independent execution is unavailable, perform a manual walkthrough and
record that limitation; never report a walkthrough as a behavioral test pass.

Run the existing validator using `python3`; the local `python` shim is broken:

```bash
python3 /home/mothmanex/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/mothmanex/.codex/skills/agent-builder
git diff --check
git status --short
```

Expected: `Skill is valid!`, no whitespace errors, and only in-scope changes.
Inspect every newly introduced local link and check line counts for individual
generated guides, not the entire multi-file example. Record scenario outcomes,
validation commands, and limitations under this plan's execution results.

## Completion and maintenance

- All eight findings are covered by the completed diff and scenario rubric.
- Confirmed behavior, proposed policy, and unresolved assumptions are distinct.
- Every reference is reachable and loaded only when its subject matters.
- Structural checks pass; actual behavioral results are reported accurately.
- The plan index is marked DONE only when required work is complete; if fresh
  scenario execution was unavailable, explicitly preserve that validation limit.
- Future platform updates belong in `references/platforms.md`, not repeated
  throughout the templates. Future failure cases should refine the smallest
  relevant rule rather than add another universal checklist.

Pause dependent work only for a material conflict with newer user decisions,
an inability to preserve a unique constraint, or a required out-of-scope change.
Continue unaffected work and explain the concrete unresolved issue.

## Execution results

Implemented 2026-09-05. All eight findings are addressed.

- `SKILL.md`: 863 to 179 lines, 4,372 to 1,408 words.
- `README.md`: 267 to 50 lines.
- Added three conditional references and seven reproducible behavioral scenarios.
- Updated all examples together; retained the fuller guide's adopted stack,
  localization, storage/privacy, UI, task-history, worktree, and release constraints.
  Removed duplicated prose, unknown skill slots, unsupported example-script
  claims, blanket code precedence, and redundant approval/splitting defaults.
- Skill-creator `quick_validate.py` via Python 3: `Skill is valid!`.
- `git diff --check`: passed. New local reference links resolve.
- Generated fenced example guides: 38 lines (basic), 179 lines (fuller),
  and 33 lines (agent example root); reviewer prompt is a separate 33-line block.
- Fixture generator in `tests/scenarios.md` executed successfully without dependencies.

Each scenario ran in its own fresh subagent context, with sequential follow-ups
in the same context for cases 06 and 07. Executing agents received the candidate
skill, project, and user request without the rubric or implementation plan.
The parent inspected responses and compared actual files with fixture snapshots.

| Case | Result | Observed evidence |
| --- | --- | --- |
| 01 | PASS | Exact command replacement only; manifest and public API rule unchanged; no permission question. |
| 02 | PASS | Root plus nested override identified; local guide shadowed; shared root rule retained; no target mutations or claim of native loading verification. |
| 03 | PASS | 226-line guide reduced to 7 lines; unique privacy, compatibility, validation, and storage reading rules preserved; existing storage document unchanged. |
| 04 | PASS | Code/spec mismatch reproduced and unconditional code precedence flagged; suggested guide correction returned without file changes. |
| 05 | PASS | Two review-only plans with bounded contracts; parent handoff documented in README; source unchanged, no installed agents, dispatch, or extra orchestrator. |
| 06 | PASS | 13-line draft separated assumptions; follow-up produced a four-line final guide with no guessed commands, unresolved slots, or scaffolding. |
| 07 | PASS | Initial 190-line guide unchanged; follow-up retained all prior text and all 217 field rules exactly once in a single 220-line guide under the requested 240-line cap. |

Disposable artifacts and before-snapshots were inspected at
`/tmp/agent-builder-eval-rcng2umk`; they are not shipped and may be removed by
normal temporary-directory cleanup. Scenarios remain reproducible from the
repository test document independently of that directory.

Limit: these runs validate the skill's generated guidance and task behavior.
Native Codex/Claude sessions were not launched to test loading or installation;
platform integration statements were checked against the linked official docs.
No dependencies, runtime agents, commits, pushes, or deployments were created.
