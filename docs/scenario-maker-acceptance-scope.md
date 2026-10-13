# Scenario Maker — fresh acceptance scope

## Status and authorization

**Full fresh paid acceptance and final disposition complete: not accepted.** The user selected “Authorize full fresh acceptance” through OMP `ask`, including the complete frozen session contract, residual provider/capacity risk and manual supervision/stop policy. A's `authorization.json` retains that decision. Managed handle `scenario-acceptance-20261010T220826Z`, runner PID 1262042, independently terminated with exit 1, matching the runner's completed, exception-free `execution.json`.

Semantic migration acceptance remains unmet because of a confirmed candidate H3 audio-permission regression and one unassessed candidate boundary criterion—not missing paid execution or provider/auth evidence. A's separate fresh summary, historical disposition, combined outcome and externally closed `disposition.json` are retained without rewriting runner records. No unfinished authorized execution task remains; repair, recapture and another assessment require new scope.

References:

- [Approved split plan, approach step 6](../skills/scenario-maker/evals/comparisons/model-split-20261008T184942Z/approved-plan.md#6-review-semantic-regressions-independently-and-measure-context-reduction)
- [Evaluation and recovery controls](../README.md#evaluation-tooling)
- [Completed repair and historical outcome](next-steps.md)

Paths below are relative to the collection root:

- **E** = `skills/scenario-maker/evals/comparisons/model-split-20261008T184942Z`
- **R** = `E/round-2`
- **P** = `R/ai-review-recovery-1`
- **A** = `E/acceptance-20261010T220826Z`, the prepared assessment now permanently claimed by its single authorized launch. Its immutable `preparation.json` and `offline-proof.json` retain the prior completed offline scope.

## Decision: a new full review, not another recovery

The authorized scope is a complete independent review of the unchanged round-2 captures. Use frozen `review_acceptance.py` orchestration over `review_split.py` helpers, never `review_recovery.py`.

| Evidence or sessions | Authorized scope |
| --- | --- |
| Existing corpus captures | All 744 from `R/corpus` |
| Existing boundary captures | All 54 from `R/boundary` |
| New generator sessions | 0, conditional on unchanged source/input bindings |
| New initial reviewer sessions | Exactly 411: 387 paired and 24 candidate-only packets |
| Reused initial judgments | 0; the old 200 remain historical evidence |
| Independent adjudications of new allegations | One for each required packet; quantity determined by the new judgments |
| Independent disposition of the retained allegation | One additional session for `h3-dev-02`, attempt 2 |

The baseline and candidate identities recorded in the handoff and `R/capture-and-context-proof.json` are:

- Baseline: `8c1db4ecf911696e5a7492cf07d67e101e538ebdf8d2f67eceb7c383dd9961da`.
- Candidate: `split-sha256-81a60df7cea26a553c679e4c72405ba3ab17defd615b6cff9b7e13140fac7f70`.

Reuse captures only after a new acceptance-specific offline binding check. The tool-only stdin change does not itself invalidate them. Do not assert that the current worktree still matches the captured candidate without that check.

This is a new assessment with entirely fresh initial judgments, not permission to repeat the earlier 200-reused/211-missing exception. Preserve original campaigns and failed/interrupted attempts. Never rerun P's `plan` or `run`, manufacture terminal artifacts, overwrite judgments, refresh sealed hashes, or assemble a best-of result across campaigns.

## Execution controls to retain

- Model: `openai-codex/gpt-6-astra`; high reasoning; no substitutions.
- Reviewer deadline: 900 seconds; concurrency: 3. The existing outer subprocess wait is 930 seconds; it is not a new model deadline.
- Generator deadline remains 300 seconds if a later, separately authorized source repair requires recapture.
- One fresh session per review/adjudication, request through argv, `stdin=subprocess.DEVNULL`, no retries/resume/replacement judgments.
- Complete frozen-baseline rubric, unchanged requests/expectations/fixtures, exact case IDs and repetitions, original criterion IDs, complete outputs/artifacts/interaction evidence.
- Deterministic A/B mapping retained outside reviewer packets; do not describe side-label blinding as identity-proof anonymity.
- Read-only declared reviewer tools; do not claim this is an OS security sandbox.
- Malformed, missing, timed-out or incomplete judgments remain unavailable/`not-run`, never passing.

## Task sequence and authorization

### 1. `ACCEPTANCE-PREPARE-OFFLINE` — complete

Authorized and completed with no real OMP/model invocation, including version/provider probes, and no campaign `plan`/`run` command. The original preparation contract follows:

Deliver acceptance-specific preparation outside the old campaigns:

1. Validate all 798 retained capture slots, frozen snapshots, fixtures, requests/expectations, corpus/boundary consistency and the two identities above using the existing fresh-review preflight. This is launch binding, not a repeat of Task B timeout triage or P status validation.
2. Compare current runtime package/input manifests with the captured candidate and evaluation inputs. Any prompt-source or input drift blocks the unchanged-capture proposal. Report the mismatch; do not silently synchronize, repair prompts or generate replacements.
3. Build and validate all 411 complete packets and their side map without launching reviewers. Retain original capture paths and hashes, packet hashes, full rubric and fixture bindings.
4. Freeze the repaired reviewer, reviewer system/config, and the evaluator dependency closure actually used by the new assessment. Record the difference from historical reviewer provenance; never edit that provenance. The existing `retain_preparation()` copies `review_split.py`, `reviewer-system.txt` and the captured config, not the complete imported-code closure.
5. Prepare the supplemental historical adjudication from the original valid `h3-dev-02/attempt-2` judgment, its packet/side map and all three repetitions of raw evidence. Verify label alignment; do not infer candidate regression from `regression: true`.
6. Supply bounded new-assessment orchestration for that supplemental adjudication using existing packet, `run_reviewer()`, judgment-validation and disposition helpers. Preserve its record separately from the 411 new initial slots. No recovery/resume/retry interface or changes to P.
7. Define the combined outcome record and process supervision before paid launch: exact argv, provenance bindings, managed handle/PID, raw stdout/stderr, actual runtime version, terminal exit or explicit interruption evidence. Recheck prepared bindings at launch. The actual OMP version remains an execution-time observation.

Offline preparation is complete only when all bindings and packet coverage validate, the historical adjudication path is runnable without editing old evidence, and launch/outcome handling cannot silently omit that path. If implementation is needed for this orchestration, verify it offline with isolated no-provider fixtures and a real subprocess smoke; do not repeat the already completed stdin reproduction or guarded startup probe.

Implemented under `skills/scenario-maker/evals/` in `review_acceptance_prepare.py`,
`review_acceptance_history.py` and `review_acceptance.py`. The `prepare` CLI created A; the `validate` CLI
executed from A's frozen provenance and passed all six binding gates. All 798
captures are available; current packages, inputs and fixtures match the captured
candidate. A retains 387 paired plus 24 candidate-only packets and zero reused
initial judgments.

The complete seven-module evaluator closure, reviewer system and captured config
are frozen. The reviewer source differs from historical provenance by hash;
system/config are unchanged. Historical provenance was not edited. The original
H3 packet, judgment, side map and all three raw repetitions passed independent
offline binding validation. Prior context/packaging proof remains applicable;
its checks were referenced, not rerun. Only four H3/generic prompt-wording files
differ from the initial packaging snapshot; utility/resource inventories and
implementation bytes are unchanged.

The new runner mandates the supplemental adjudication, preserves the standalone
fresh summary and supplemental disposition separately, and produces a hash-linked
combined result. Permanent launch claiming, frozen imports/argv, runtime evidence
and external observed-interruption handling were verified with offline fixtures.
A's current launch is separate from this prior offline evidence; preparation did not authorize paid execution.

### 2. Resolve provider-execution risk before full-wave approval

The separately authorized preflight completed under
`E/provider-preflight-20261010T230004Z`. It used A's frozen reviewer, system and
config with the first frozen packet (`case-01`, attempt 1), fixed
`openai-codex/gpt-6-astra`, requested high reasoning, 900-second reviewer deadline
and 930-second outer wait. One reviewer session; no retry, recapture or
adjudication. Diagnostic concurrency was one, not a change to acceptance's three.

OMP v18.8.7 was observed. The trace resolved `openai-codex/gpt-6-astra` through
`openai-codex-responses`; review exited 0 after 110.240 seconds, all four criteria
on both labels were assessed/passed, and citation/tool/trace validation passed.
The managed supervisor `scenario-provider-preflight-20261010T230004Z`, PID
1022682, independently exited 0. `disposition.json` binds the raw review, runtime,
process observations and separate managed terminal observation. High reasoning
was requested; resolved reasoning/provider settings remain unknown.

The diagnostic judgment is excluded from acceptance and never reused. The
historical allegation remains independently unassessed. A's preparation hash is
unchanged; no A launch, review, execution or outcome was created. This scope
checked only the preparation hash, frozen closure/config/system and selected
packet bindings—not the full offline gates or current package/input manifests.

Full-wave approval must acknowledge that one-session success is not a guarantee
of future availability or concurrency-three capacity. The current fresh CLI
queues the entire wave in `ThreadPoolExecutor`; `--jobs 3` limits concurrency,
not paid attempts. It has no canary mode or automatic stop-on-first-failure.
Do not repeat the preflight, promise either behavior or introduce it silently.

### 3. `ACCEPTANCE-EXECUTE-FRESH` — complete

Explicit full-wave approval was received through OMP `ask`, including the prepared bindings, all initial sessions and required adjudications, residual provider/capacity risk and manual supervision/stop policy. A's prior offline preparation did not itself authorize paid launch.

The new assessment must use the exact `future_execution.argv` and managed handle
retained in `A/preparation.json`, running A's frozen `review_acceptance.py execute`
entry point—not the changing worktree or the standalone fresh CLI. Its fixed
controls are 411 fresh initial reviews, all required new adjudications and one
separate historical adjudication. This exact command was launched once; no retry, resume or replacement is authorized.

The runner claims permanent `A/launch.json` before launch validation, rechecks all
bindings before OMP runtime observation, and rejects a second execution after
failure, blocking or interruption. Run once in a managed process with no enclosing
shell deadline. Persist the actual managed handle and launch evidence before
handoff. Readiness `acceptance_started` establishes runner startup only.

Fresh records live in `A/ai-review`; the mandatory historical session is under
`A/ai-review/historical-adjudications/h3-dev-02/attempt-2`. Keep
`ai-review/summary.json`, `historical-disposition.json` and `combined-outcome.json`
distinct. Missing/incomplete supplemental disposition or runtime/provenance
evidence blocks the combined result, even if fresh reviews pass. It is not a
412th initial judgment.

Manual interruption requires externally observed suspension, complete worker
inventory/termination and runner terminal evidence under `observe_interruption()`'s
schema. `record-interruption` retains an unsuccessful disposition but never
signals processes, fabricates `execution.json` or authorizes another attempt.

### 4. `ACCEPTANCE-DISPOSITION` — complete, not accepted

Validate the new retained evidence and publish an explicit pass/not-accepted outcome against every gate below. Keep the fresh CLI's summary, the historical adjudication and the combined disposition distinct and linked by hashes. Record missing coverage or interruption honestly; never fabricate finalization.

The runner writes its own `execution.json` before returning; its stored return
code is not independent observation of OS termination. Final disposition must
bind the actual managed service terminal result and require agreement. Missing
terminal evidence, mismatched exit or a signal after finalization blocks
acceptance even if the combined runner summary passed. Retain the external
observation and final disposition separately without rewriting runner records.

A substantiated candidate prompt-source regression requires a separately scoped repair, synchronization and both complete capture suites in new directories before another assessment. Do not recapture merely for the existing stdin-only tool repair, mix source revisions, alter expectations or automatically start another campaign.

## Unchanged acceptance gates

Acceptance requires all of the following together:

1. One consistent capture snapshot covering all 798 available captures.
2. Exactly 411 valid complete new initial reviews, with all required criterion sides assessed over all three repetitions.
3. Valid independent adjudication of every required new allegation, plus a complete independent disposition of the retained `h3-dev-02`, attempt 2 allegation.
4. Every new candidate boundary passes.
5. No unresolved new candidate hard contract failure.
6. Candidate per-criterion failure counts do not exceed baseline counts over all three repetitions.
7. No candidate failure on a baseline-always-passing criterion.
8. Consistent packet, fixture, rubric, evaluator and runtime provenance; no cross-campaign best-of aggregation.
9. The approved ordinary-path context/read boundaries and self-contained packaging evidence remain applicable to the same candidate snapshot. Previously completed evidence may be referenced, not misrepresented as rerun.

The retained allegation is **baseline-only**: A=baseline failed, B=candidate passed. A new passing judgment does not independently adjudicate that historical allegation. Baseline defects remain visible and are not a mandate to expand the prompt repair scope.

AI migration acceptance is not legacy human sign-off, native host automatic-selection proof or rendered-media-quality proof.

## Evidence checked in the fresh acceptance chat

- Launched A's exact frozen argv once in the prepared managed process, without
  an enclosing deadline. Launch validation passed before runtime/reviewer work;
  preparation SHA-256 remains
  `681aa71b3c7c101b8d15194897ff2c44842fb1d69de17b4541946b8f92a0a2d8`.
- Runtime observation: `omp v18.8.7`. All 414 reviewer sessions returned valid
  judgments: 411 fresh initial, two required independent new adjudications and
  one separate historical adjudication. Zero reused, invalid, retried or
  replacement judgments; no new generator sessions.
- The runner completed in 14475.715 seconds, with no exception or manual stop.
  `managed-start.json` and `managed-terminal.json` independently bind its PID,
  handle and actual exit 1. Read-only supervision evidence is retained separately.
- Actual offline `disposition-verifier.py` execution verified prepared/external
  bindings, raw reviewer hashes, judgment/citation/tool/model evidence, complete
  slot/adjudication coverage, recomputed fresh/historical dispositions and linked
  runner outcomes. `disposition-validation.json`: zero errors; managed exit
  matches the runner; no remaining wave processes observed. This validates
  unsuccessful evidence; it does not convert failed semantic gates into passes.

| Acceptance requirement | Observed disposition |
| --- | --- |
| Consistent capture snapshot | 798/798 available; bindings passed |
| Fresh initial review criteria complete | 411/411 valid judgments, but one candidate criterion remains `not-run` |
| Required new independent adjudications | 2/2 valid and complete |
| Separate historical disposition | Valid/complete; original baseline-only failure confirmed |
| Every candidate boundary passes | Blocked by `split-invoke-illustrious`, attempt 3, E2: lookup launch recorded but completion/results absent |
| No new candidate hard failure | Failed: `h3-guide-01`, attempt 3, E1 independently confirmed |
| Candidate failure counts no greater than baseline | Failed for H3 guide E1: baseline 0/3 failures, candidate 1/3 |
| Baseline-always-passing protection | Failed for the same H3 guide E1 |
| Provenance, context and packaging applicability | Passing bindings; prior context/packaging checks not rerun |
| Independent terminal result | Actual exit 1 matches completed runner finalization; not accepted |

The H3 candidate turned “No other sound or music is requested” into “Only the
specified dialogue; no additional sounds” and `non_diegetic_music: N/A`.
The frozen contract requires unchosen audio layers to remain `Unspecified`.
All three baseline repetitions preserved that distinction. This is a confirmed
candidate-output regression; its prompt-source cause has not been diagnosed
in this scope.

The Illustrious boundary is unavailable evidence, not a confirmed semantic
failure. Its visible lookup result says `Backgrounded as job bg_1`/`running`,
with no captured completion or returned canonical-tag results. A syntactically
valid reviewer correctly retained E2 as `not-run`; neither review replacement
nor promotion of uncaptured results is authorized.

The original `h3-dev-02`, attempt 2 allegation was independently confirmed on
the baseline side (A failed, B passed), with no historical candidate novelty
or baseline-pass protection violation. It is not a candidate repair target.

No routine regression suite, preparation, diagnostic preflight, stopped-P check,
prompt repair, synchronization, recapture, seal refresh, commit, push or tracker
mutation was repeated/performed.

## Evidence checked in the offline preparation chat

- Existing fresh-review preflight validated all 798 captures, frozen sources,
  requests/expectations, fixtures and corpus/boundary consistency. Current runtime
  and evaluation-input manifests matched the captured candidate.
- Actual `prepare` CLI exited 0; frozen `validate` CLI exited 0 with all six gates
  passing. Preparation SHA-256:
  `681aa71b3c7c101b8d15194897ff2c44842fb1d69de17b4541946b8f92a0a2d8`.
- Full offline evaluator suite: **78 tests passed in 347.113 seconds**, without an
  enclosing shell deadline. Synthetic full-count subprocess tests covered fresh
  review plus mandatory historical disposition, unavailable evidence, drift,
  repeated-launch refusal and observed interruption.
- A separate disposable real-subprocess smoke used A's actual historical packet
  and frozen reviewer with an isolated local Python-only `omp` stub: valid complete
  synthetic independent disposition, subprocess exit 0, **0.142 seconds**. Empty
  home/auth and restricted PATH prevented real OMP invocation. The disposable
  directory was removed; its synthetic judgment is not semantic evidence.
- `A/offline-proof.json` retains these observations. No real OMP/version/provider
  call, new capture, actual reviewer judgment, campaign launch, stopped-P status
  validation, seal refresh, commit, push or tracker mutation occurred.

**No unfinished authorized execution task remains.** Recommended next scope is focused diagnosis/repair of the confirmed H3 audio-permission regression and investigation of the Illustrious evidence gap. Source repair, synchronization, both complete new capture suites and a new full fresh assessment require explicit scope; none is authorized by this completed wave. A and P are permanently non-resumable. Do not repeat their launch, replace judgments or alter expectations.
