# Scenario Maker model split — bounded-task handoff

## Goal and scope

Project: `/home/mothmanex/.agents/skills/lfgg-skills`. Finish the approved seven-specialist Scenario Maker split while preserving every capability and covered version/route. Implementation is present; final semantic acceptance is unfinished.

The user paused the long-running workflow because of elapsed time and resource use. **Task A is complete: offline evidence inventory only.** Continue in separately invoked, bounded tasks; no Tasks B–D were executed here.

## Completed in this chat

- Read applicable collection/skill/domain guidance and the complete approved plan.
- Inventoried every manifest slot, label mapping, completion-log entry, review record, and interrupted attempt in the repaired campaign. Exact coverage: **200 valid completed, 3 partial, 208 unstarted; 0 invalid completed records**.
- Enumerated the retained judgments independently of the progress log. Checked all 411 packet hashes, 200 review-to-packet identities/hash bindings, 1,200 recorded raw-file checksums, three reviewer-provenance hashes, and two capture-manifest hashes; no mismatch found.
- Inventoried all existing criterion states and inspected the sole hard-failure allegation against its frozen packet, source rules, and raw baseline/candidate outputs. It is baseline-only, not a candidate regression; independent adjudication remains required.
- Checked current OS process state: no matching review launcher, runner, or isolated reviewer worker. Inspected all three partial traces; none contains a final judgment or terminal completion.
- Updated only this handoff in the repository. No implementation/evidence edits, tests, paid models, captures, or review launches/restarts.

Authoritative approved plan:

`/home/mothmanex/.omp/agent/sessions/-.agents-skills-lfgg-skills/2026-10-08T18-03-25-753Z_01a11caf-30b9-73aa-902b-21385c787911/local/scenario-maker-model-split-plan.md`

The plan's retained copy is `E/approved-plan.md` (E defined below). Approach step 6 remains unfinished. The older `skills/scenario-maker/docs/next-steps.md` is historical, not the execution plan.

## Decisions and constraints

- Planning is approved. Do not restart the design interview or re-request approval for settled implementation/model choices.
- Specialists select a family only—not task, checkpoint variant, native route, invention permission, or scope. Generic retains its own complete local catalog.
- Use synchronized repository-local resources. No runtime sibling dependency or installation-time build; do not change the user's existing installations.
- Preserve original requests, expectations, fixtures, capability/version boundaries, and H3 guide bytes. Use the frozen pre-edit monolith, not the historical fixed-commit baseline.
- Approved evaluation: 124 requests × three repetitions × two sides = 744 captures, plus 54 boundary captures. Model: `openai-codex/gpt-6-astra`, high reasoning; generator deadline 300 seconds, reviewer deadline 900 seconds.
- Keep failed/partial evidence immutable. No automatic retry/resume machinery, replacement of failed attempts, best-of selection, or mixing candidate source versions.
- AI reviews never satisfy legacy human-only criteria. Packaging/tests/context bytes do not prove prompt-quality parity, native host selection, or rendered-media quality.
- Work on one named task per chat. Do not reduce coverage or silently switch models to save resources. Read existing evidence before scheduling new model calls.

## Verification and current state

Evidence root, abbreviated **E** below:

`/home/mothmanex/.agents/skills/lfgg-skills/skills/scenario-maker/evals/comparisons/model-split-20261008T184942Z`

**R** means `E/round-2`. These are filesystem locations, not retained Eval variables.

### Previously completed work — retained evidence, not rerun here

The generic entry point and seven specialists, synchronized self-contained resources, split capture/review/context tools, and root catalog are implemented. The first campaign's H3 offer/read-clipping regression and reviewer repetition-identity defect were repaired before round 2.

| Check | Retained result | Evidence |
| --- | --- | --- |
| Offline suites/sync | 18 utility + 24 evaluator tests passed; sync and `--check` passed | `E/offline-checks-v2.json` |
| Packaging/discovery/install | All eight isolated utilities worked; ten skills discovered; disposable Pony install worked | `E/packaging-proof.json` |
| Repaired captures | 744 corpus + 54 boundary outputs/complete traces; zero errors/timeouts | `R/{corpus,boundary}/execution-summary.json` |
| Mechanical scoring | 63 passes, zero failures per side; 108 legacy human states per side remain `not-run` | `R/legacy-{baseline,candidate}-scores/summary.json` |
| Context/input integrity | All eight byte/read-boundary paths passed; retained inputs/generation controls unchanged | `R/context-final.json`, `R/capture-and-context-proof.json` |

Baseline identity: `8c1db4ecf911696e5a7492cf07d67e101e538ebdf8d2f67eceb7c383dd9961da`.

Repaired candidate revision: `split-sha256-81a60df7cea26a553c679e4c72405ba3ab17defd615b6cff9b7e13140fac7f70`. Both repaired capture suites and the review manifest use it.

### Task A inventory — observed offline

Inventory process/hash check: **2026-10-09 14:51 UTC**. Authoritative index: `R/ai-review/manifest.json`; side mapping: `R/ai-review/label-map.json`; completion log: `R/review-runner.stdout.jsonl`; records: `R/ai-review/reviews/<case>/attempt-N/review.json`.

All **411 packets** exist with matching hashes and unique case/repetition identities: 387 paired plus 24 candidate-only packets, covering 798 available capture slots. The 200 completion-log entries match exactly 200 retained valid/completed records, with exit code 0, complete traces, and empty validation errors. There are no unlogged completed judgments or invalid completed records.

| Review family | Expected slots | Valid complete | Partial | Unstarted |
| --- | ---: | ---: | ---: | ---: |
| Formal `case-01`–`case-16` | 48 | 48 | 0 | 0 |
| All `h3-dev-*` | 132 | 132 | 0 | 0 |
| `h3-guide-01`–`h3-guide-14` | 42 | 20 | 3 | 19 |
| Phase-three probes | 24 | 0 | 0 | 24 |
| Phase-four probes | 33 | 0 | 0 | 33 |
| Wild probes | 57 | 0 | 0 | 57 |
| Unbound probes | 36 | 0 | 0 | 36 |
| Split boundaries | 39 | 0 | 0 | 39 |
| **Total** | **411** | **200** | **3** | **208** |

Validated coverage is **48.66%** overall: corpus 200/372; boundaries 0/39. Sixty-six of 137 requests have all three reviews. H3 guides 01–06 have all three, guide 07 has attempts 1/2 complete and attempt 3 partial; guide 08 has attempts 1/2 partial and attempt 3 unstarted; guides 09–14 are entirely unstarted. Every remaining family in the table is entirely unstarted.

The three partial directories are `R/ai-review/reviews/{h3-guide-07/attempt-3,h3-guide-08/attempt-1,h3-guide-08/attempt-2}`. Each contains only `command.json`, `request.txt`, `trace.jsonl`, and empty `stderr.txt`; no `review.json`, `output.txt`, `context.json`, or saved partial-output artifact. All trace JSONL parses, tool starts/ends match (24/38/43 tool calls respectively), but no final assistant message or terminal `agent_end` exists. These are interrupted attempts, **not recorded timeouts/provider failures**, and contain no recoverable completed judgment. Do not turn intermediate reasoning into a review.

No matching worker was found by the current OS check. `R/review-runner-execution.json`, `R/ai-review/summary.json`, adjudications, and adjudication packets are absent. The last logged completion is `h3-guide-07` attempt 2; log mtime is 2026-10-09 06:41:03 UTC. The manifest remains `acceptance: "not assessed"` and has no `finished_at`. The interruption cause/exit status is unknown; old job IDs are not recovery handles.

### Existing semantic issues — allegations, not final dispositions

- **199** completed judgments pass every supplied criterion on both sides. The remaining judgment alleges **one baseline-only hard failure**: `h3-dev-02`, attempt 2, `h3-dev-02-E1`. A=baseline, B=candidate. Baseline asks, “How should video B’s metronome soundtrack (`<Audio 1>`) be used…” instead of delivering the requested picture/video bindings; candidate supplies those bindings and retains standalone audio as `<Audio 2>`. Frozen H3 rules permit omitting unused connected audio without renumbering (`E/before/references/models/minimax-h3.md:70,213`). The clarification's necessity versus the binding criterion remains for independent adjudication, not a source repair here.
- Evidence: `R/ai-review/reviews/h3-dev-02/attempt-2/review.json`, its matching `packets/.../packet.json`, and `R/corpus/probes/{baseline,candidate}/h3-dev-02/attempt-2/output.txt`. `regression: true` is **direction-neutral** under the frozen validator; it must not be reported as a candidate regression.
- Existing initial criterion states: baseline **322 passed / 1 failed / 0 not-run**; candidate **323 passed / 0 failed / 0 not-run**. No candidate-only or both-side failures, advisory failures, or logged validation problems were found. This says nothing about unreviewed slots: 229 baseline and 268 candidate criterion-side judgments remain absent.
- **At least one independent adjudication is required** by the frozen runner's `needs_adjudication`; zero exists. Remaining reviews may reveal additional allegations. No candidate implementation defect requiring Task B repair is currently substantiated.

Historical failure stays separate: `E/ai-review/summary.json` records first-campaign acceptance **false**, 411 initial sessions but only 132 valid judgments, and one valid adjudication confirming the H3 offer regression. Previous handoff attributed the invalid records to 259 repetition-ID mismatches, 18 deadlines, one provider error, and one nonliteral citation. None is replaced or imported as round-2 acceptance.

Two campaigns generated 1,596 primary captures. Round 2 additionally started 203 initial-review attempts: 200 completed plus three interrupted. Billing cost is not established; recorded usage estimates are not verified billing. Do not regenerate the repaired 798 captures merely because review was interrupted.

No semantic acceptance, human sign-off, rendered-media quality, native host automatic-selection result, or clean-worktree guarantee is claimed. Current authentication/provider availability was not tested.

## Next steps

Task A is complete. **Next recommended bounded task: C, only after the recovery decision below.** B is conditional, not required merely because the one allegation is baseline-only; D needs a completed coherent assessment. Do not chain tasks.

| Task | Scope and deliverable | Stop boundary |
| --- | --- | --- |
| **A — Evidence inventory: complete** | Exact inventory and existing allegations are recorded above. | Read-only/offline; only this handoff changed. No Tasks B–D executed. |
| **B — Targeted triage/repair, if needed** | Investigate only a specific allegation or reviewer/operational defect against raw artifacts and frozen rules. Distinguish baseline failures, reviewer/tool defects, and candidate regressions; fix only substantiated in-scope defects. Unblinded inspection is not independent adjudication. | No full campaign or opportunistic prompt repair. If no repair is justified, leave source unchanged. A new recovery/batch implementation is not authorized by Task B's existing scope. |
| **C — Controlled paid assessment: decision pending** | First choose the recovery protocol. Reuse the repaired 798 captures if prompt source is unchanged. The supported CLI starts 411 fresh initial reviews in a new directory, then required independent adjudications; it has no resume/batch mode. Record scope/model/deadlines/output paths and a managed process/status command before one launch. | No spending until the new recovery choice is resolved; no automatic repeats or recovery loop, no hours-long chat wait, no partial acceptance. An approved recovery-only design/implementation must be a separately scoped task before using that option. |
| **D — Final acceptance and documentation** | Read the completed coherent assessment, verify every gate, keep baseline failures separate, and update the root README/handoff with exact evidence and remaining limitations. Remove remaining throwaway launchers only after their execution evidence is retained. | No new model runs or source redesign. If a concrete gate fails, report it and return to the relevant bounded task rather than chaining another campaign. |

Acceptance still requires all 411 valid initial reviews and all required independent adjudications; every new boundary must pass; no new candidate hard contract failure may remain; candidate per-criterion failures must not exceed baseline over three repetitions; any failure on a baseline-always-passing criterion blocks. All evidence must cover one consistent candidate snapshot. Mechanical/context gates are already exercised, not reasons to infer semantic acceptance.

If prompt source changes after a confirmed regression, synchronize and run **both complete capture suites** in new directories before their review. Keep old evidence; never alter expected behaviors, drop failures, use diagnostic passes as acceptance, or mix snapshots. Tool-only review repairs do not by themselves invalidate unchanged generator captures.

## Blockers and open questions

- Semantic acceptance lacks **211 initial judgments (three interrupted + 208 unstarted)**, at least one independent adjudication, and a final aggregate. The operational interruption has no retained exit/cause record; no current worker or authentication failure is established.
- **Recovery decision required before spending:** (1) use the supported fresh full run: **411 new initial sessions**, retaining the interrupted campaign separately; or (2) explicitly authorize a **review-only recovery/batching protocol**, reusing the 200 verified records and creating **211 new initial sessions**, plus all required adjudications. Option 2 saves 200 initial sessions but is neither implemented nor authorized, and requires an explicit exception to the current no-resume review policy. Do not quietly add resume flags or treat the three interrupted attempts as passes.
- Any recovery protocol must preserve original partial/failed evidence, frozen packet/fixture/rubric hashes, deterministic side mapping, model/reasoning/deadlines, complete identity/citation validation, full 411-slot coverage, consistent capture snapshot, independent adjudication of the baseline-only allegation and all later hard failures, and coherent aggregation with explicit provenance for reused/new records. No best-of selection, generator retry/resume machinery, source-version mixing, or lowered acceptance gates.
- If the approved model becomes unavailable during a separately authorized task, preserve evidence/commands and report the exact failure. Do not silently substitute another model.

## Prompt for a new chat

```text
TASK=C

Continue only Task C for the approved Scenario Maker model split in /home/mothmanex/.agents/skills/lfgg-skills. Read applicable repository guidance, docs/next-steps.md, the complete authoritative approved plan linked there, and the root README evaluation-tooling section. Do not reopen settled design/model choices or chain Tasks B/D.

Task A is complete. Implementation and repaired captures/mechanical/context gates are complete. Round-2 review has exactly 200 valid completed, 3 interrupted, and 208 unstarted slots out of 411. All 39 boundary slots remain unstarted. There is one baseline-only h3-dev-02 attempt-2 hard-failure allegation, zero candidate failures in existing records, and no adjudication/final aggregate. No matching worker existed at the inventory check. First-round failures and partial evidence remain immutable.

First check relevant current evidence/process state without rerunning tests or regenerating captures, preserving unrelated work. Then use OMP's interactive ask tool to resolve only the outstanding recovery decision before any spending: supported fresh 411-review campaign against existing captures, or explicitly authorized review-only recovery/batching that reuses 200 records and supplies 211 missing judgments. Do not infer permission for recovery implementation from this prompt. If that option is chosen, save its exact authorization/requirements and hand off to a separately scoped recovery task; do not implement it or launch models under the existing Task C scope.

If the supported full run is chosen and prompt source is unchanged, use review_split.py with R/corpus and R/boundary from the handoff and a new output directory. Record model openai-codex/gpt-6-astra, high reasoning, 900-second reviewer deadlines, exact command/output paths, and explicitly managed process/status tracking before launching one campaign. Preserve the old 200 records and three partial attempts unchanged; do not overwrite or automatically retry. Do not block the chat waiting for hours. Save the run status/continuation and stop Task C; no Task D in this chat.

Acceptance later requires 411 valid complete initial reviews, all required independent adjudications (including the baseline-only allegation), every boundary passing, no new candidate hard contract failure, per-criterion candidate failures no greater than baseline across three repetitions, protection of baseline-always-passing criteria, and one consistent capture snapshot. AI review is not legacy human sign-off, rendered-media proof, or native host selection proof. No prompt-source repair or recapture is justified solely by interrupted review.
```
