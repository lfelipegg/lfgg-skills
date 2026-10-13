# Scenario Maker model split — diagnosis complete, assessment not accepted

## Goal and scope

Project: `/home/mothmanex/.agents/skills/lfgg-skills`. Finish the approved seven-specialist Scenario Maker split without losing capabilities, versions, or routes. [Approved-plan approach step 6](../skills/scenario-maker/evals/comparisons/model-split-20261008T184942Z/approved-plan.md#6-review-semantic-regressions-independently-and-measure-context-reduction) semantic acceptance remains unmet.

Source repair, both complete fresh capture suites, offline assessment preparation, and the separately authorized paid assessment are complete. S is permanently claimed and externally closed **not accepted**, non-resumable/non-repeatable. One novel candidate hard failure and two `not-run` criteria remain. The user subsequently selected **Read-only diagnosis** of those three blockers; that bounded investigation is now complete. No implementation, evaluator change, reproduction, or paid execution was authorized by that selection. This handoff update is separately requested; it does not authorize the proposals below.

Read [resource ownership](../README.md#scenario-maker-resource-ownership), [evaluation controls](../README.md#evaluation-tooling), and [prior acceptance scope/outcome](scenario-maker-acceptance-scope.md) before any newly authorized dependent work. The older `skills/scenario-maker/docs/next-steps.md` is historical.

Paths relative to collection root (filesystem locations, not retained Eval variables):

- **E** = `skills/scenario-maker/evals/comparisons/model-split-20261008T184942Z`.
- **R** = `E/round-2`.
- **P** = `R/ai-review-recovery-1`, permanently stopped/non-resumable.
- **A** = `E/acceptance-20261010T220826Z`, completed/closed not accepted/non-resumable.
- **D** = `E/provider-preflight-20261010T230004Z`, historical diagnostic only, excluded from acceptance.
- **O** = `skills/scenario-maker/evals/comparisons/offline-repair-20261011T211940Z`, retained isolated-package smoke proof.
- **C** = `skills/scenario-maker/evals/comparisons/repaired-captures-20261011T214359Z`, completed single-use capture wave.
- **S** = `skills/scenario-maker/evals/comparisons/repaired-assessment-20261012T005141Z`, completed single-use assessment, closed not accepted.

## Completed in this chat

- Read S's existing disposition, combined outcome, summary, and failure adjudication; read ownership/evaluation controls and the approved acceptance gates. Did not revalidate or execute any campaign.
- Asked for a new bounded scope because the prior handoff explicitly excluded inferring repair authorization from “continue.” The user selected **Read-only diagnosis**: existing source/evidence only; no edits, model calls, campaign reruns, or provider diagnostics.
- Diagnosed all three blockers using frozen source, original requests, final outputs, actual tool events, delivered context, and existing reviewer evidence. Two read-only scouts investigated the independent incomplete criteria; their initial interpretations were corrected against primary evidence. Documentation examples were not treated as executed lookup results.
- Reported the findings and unimplemented bounded repair options below. No source, evaluator, test, campaign record, installed skill, or tracker was changed by the investigation. No fresh generator reproduction or causal experiment was performed.
- Refreshed this handoff at the user's request. The only intended file change in this handoff task is `docs/next-steps.md`.

## Decisions and constraints

- Seven specialists select a family only—not task, checkpoint variant, native route, invention permission, or scope. Generic retains its complete local catalog. Every package remains self-contained without runtime siblings or an installation build.
- Preserve original requests, expectations, criterion IDs, fixtures, boundaries, routes/versions, all repetitions, and both official H3 guide bytes. No exact-case special case, request rewrite, utility/cache redesign, recorder redesign, retry interface, or provider substitution.
- Baseline remains the frozen pre-edit monolith, not the historical fixed-commit baseline. `regression: true` is direction-neutral; `h3-dev-02` attempt 2 E1 is baseline-only, confirmed by fresh and separate historical adjudications. Do not broaden candidate repair to address baseline-only failures.
- Preserve A/P/C/S and all older evidence unchanged. Never resume/relaunch/repeat, replace slots or judgments, reuse judgments, aggregate across campaigns, choose best-of, promote uncaptured results, synthesize finalization, refresh seals, or rewrite preparation/runner/final records. No routine verifier/observer reruns, old campaign checks, provider diagnostics, or terminal waits/polls.
- Source repair invalidates old candidate-capture reuse. Any future authorized acceptance campaign must use a consistent complete snapshot and new evidence directories, not reuse C/S or substitute isolated repaired slots.
- Fixed controls remain `openai-codex/gpt-6-astra`, requested high reasoning; generator 300 seconds; reviewer 900 seconds, outer wait 930 seconds, concurrency 3. These are controls, not paid authorization.
- AI review is not legacy human sign-off, native host selection, or rendered-media proof. Side-label blinding is not identity-proof anonymity; declared read-only tools are not an OS sandbox. Resolved reasoning and immutable provider snapshot remain unknown.
- Preserve unrelated user work. No commit, push, tracker mutation, installed-skill mutation, or clean-worktree guarantee.

## Verification and current state

### Newly observed read-only findings

Frozen owning H3 profile below means `C/skills/scenario-maker-minimax-h3/references/models/minimax-h3.md`.

**1. `wild-12`, candidate attempt 2, E1 — serialization omission despite delivered rule**

- `C/corpus/probes/candidate/wild-12/attempt-2/output.txt:12–13`: opening speech lacks `(S1)`; the ID appears only after the cut. Attempts 1 and 3 mark both fragments correctly.
- Frozen profile `:122` requires an ID at the first actual vocal event and every later fragment; `:177–178` demonstrates both cross-cut fragments marked. The failed generator received the rule in the initial profile read and targeted `:81:raw` reread, and read official speaker/cross-cut guidance. Baseline attempt 2 also received the rule. See the corresponding `trace.jsonl` tool calls and `context.jsonl` delivered outputs.
- `S/ai-review/adjudications/wild-12/attempt-2/review.json:11–147` confirms baseline 3/3 versus candidate 2/3 and the novel hard failure. Missing or unread instruction is ruled out for this captured omission; model variation/context causality is unresolved.

**2. `h3-dev-02`, candidate attempt 3, E1 — clarification was not necessarily required**

- Original `C/corpus/probes/candidate/h3-dev-02/attempt-3/request.txt:3` assigns Video B a camera-motion role, with a separately connected metronome soundtrack but no target-audio role. `output.txt:1–3` asks whether that soundtrack should be copied, used as rhythm guidance, or unused; it correctly reserves `<Audio 1>` for the soundtrack and `<Audio 2>` for standalone bell timbre. No finished artifact exists.
- Frozen profile `:110` says to clarify an existing audio reference lacking target sound/placement. But `:88` expressly permits omitting unused connected audio without renumbering later audio, and `:209–233` demonstrates an unrequested video soundtrack omitted while standalone `<Audio 2>` retains its label. Both paths were delivered to this generator, including a targeted profile reread.
- `S/ai-review/summary.json:13465–13508` records candidate `not-run`: picture/video/subject bindings remain unassessed without a finished prompt. It also accepts the baseline's omission of the unassigned soundtrack. Candidate attempts 1/2 likewise finish without importing the metronome.
- Corrected conclusion: clarification is a conservative interpretation, not an established necessary prerequisite. A finished prompt using Video B only for camera motion, omitting its soundtrack, and retaining `<Audio 2>` is directly supported by the frozen profile. Do not claim that the user must supply a metronome role or that the existing `not-run` can now become a pass.

**3. `split-format-noobai`, baseline attempt 1, E1 — observed timeout, omitted async evidence**

- `C/boundary/boundary/baseline/split-format-noobai/attempt-1/trace.jsonl:235–240` records the baseline's sole actual bash lookup: `python3 scripts/danbooru_lookup.py suggest "1girl solo mature female long black hair green eyes" --limit 12`, deadline 30 seconds, returned `bg_1/running`.
- Raw trace `:275–276` records the same job's delivered `custom`/`async-result` notification: status `failed`, command timed out after 30 seconds, wall time 30.10 seconds. It precedes the final response at `:277–301`. Thus the raw trace does contain a tool-reported terminal timeout; successful validation hits are absent. Do not generalize the older Illustrious child's unresolved fate to this new slot, or assert unobserved process internals.
- Frozen `S/ai-review/provenance/review_split.py:388–403` preserves tool events and selected message roles but excludes role `custom`. S's normalized packet omits that async notification. This explains the existing review's “only a running handle” account; it is narrower than the raw trace, not evidence that no notification existed.
- Documentation/script read results include lookup examples, not prior successful baseline commands. Baseline executed no separate successful `mature_female` lookup. Candidate actually executed two lookups with 300-second deadlines: suggest completed in 34.21 seconds with canonical hits; `tag mature_female` completed in 0.04 seconds. Both outputs use the same final tags.
- `S/ai-review/reviews/split-format-noobai/attempt-1/review.json:11–87` retains baseline `not-run`, candidate passed, regression null. The timeout clarification does not supply successful validation or establish incorrect tag content. Candidate already has the cold-build-aware deadline/terminal-evidence instruction; this baseline-only issue justifies no additional candidate-source repair.

**Verification boundary:** these are observations of retained files and delivered events, not new integrity checks or reproduced model behavior. No tests, smoke commands, model/provider/subprocess calls, campaign verification, or terminal waits ran during this read-only diagnosis. Handoff verification is reading the rewritten file, not rechecking campaigns.

### Prior completed work — attributed to previous handoff and retained records

- Generic-owned Danbooru guidance was repaired for cold-index-aware bounded deadlines, same-command terminal status/hits, supported follow-up without polling/replacement, and unvalidated failure handling. Owning H3 profile gained general audio-state fidelity reinforcement: unchosen stays `Unspecified`; `N/A` retains declared silence/no-score meaning only under resolved intent/binding locks. Mitigation, not proven causal fix. Managed copies/docs were updated; no official guide bytes changed.
- Prior collection-root verification on Python 3.12.3: sync and `--check` exited 0; 18 utility tests passed; all eight isolated-package runtime smokes passed. Illustrious cold lookup completed in 31.881 seconds. O retains manifests/results. An initial smoke's unsupported `gray_hair` alias assertion was corrected to observed bundled aliases; no production fix was needed.
- C completed all 744 corpus plus 54 boundary captures, zero outer capture errors/timeouts/slot/binding/summary/checksum errors; managed exit 0. This does not mean every internal utility command succeeded. `C/capture-outcome.json` and `C/managed-terminal.json` retain results. Context byte/trace/combined gates passed; `C/packaging-proof-binding.json` binds O's eight actual runtime smokes to C's frozen package runtime hashes.
- Offline evaluator preparation added paired `--capture-preparation`/`--package-smoke-proof` seams and `review_acceptance_history.prepare_source_history()` without replacing old identity/direction guards. S froze 411 packets (387 paired/24 candidate-only), seven-module evaluator closure, original controls/guides/config, and separate historical bindings. Actual guarded prepare/validate and frozen CLI from `/tmp` with OMP absent from PATH passed; no subprocess calls. 90 evaluator tests passed in 308.476 seconds. An earlier 300-second attempt timed out and exposed an incidental wording assertion; wording constraint was removed while preserving tamper rejection, then the full suite passed.
- Separately authorized S paid execution completed 411 valid initial reviews, 3 valid required fresh adjudications, and 1 valid separate historical adjudication: **415 valid judgments**, zero reused. Managed exit 1 matched exception-free runner finalization; start PID 1424230, runtime omp v18.9.1. `S/paid-authorization.json` records that approval; preparation-time offline flags remain unchanged. `S/retained-evidence-verification.json` passed with zero errors/no model calls; `S/disposition.json` binds closed/not-accepted/non-resumable status. These records were read or attributed, not rerun here.
- All candidate boundaries/context/packaging bindings passed, but the novel speaker-ID failure and two incomplete criteria block acceptance. Fresh baseline-only failures are `h3-dev-02` attempt 2 E1 and `h3-guide-01` attempt 2 E1. Mandatory original historical adjudication confirms baseline-only `h3-dev-02`.
- Historical A is closed not accepted: 414 valid judgments, one candidate criterion not-run, managed exit 1. Its H3 audio prohibition failure occurred despite delivered rules; context/model causality is unresolved. Its Illustrious lookup child fate remains unresolved; the new NoobAI timeout observation does not resolve that older slot. P remains stopped exit 137 (200 reused/0 new/102 invalid/211 missing/0 required adjudication); D remains excluded. Do not repeat old diagnostics or promote their results.

Retained identities (not guarantees about the live worktree):

- Frozen monolith baseline: `8c1db4ecf911696e5a7492cf07d67e101e538ebdf8d2f67eceb7c383dd9961da`.
- C full candidate: `split-sha256-26055f990f2e24b85a268819c555bb67e79c3328db7fff9ffa02bfdc997fa74b`.
- O runtime-only aggregate: `split-sha256-5d2dd7214c1300c5fb163d2a2acea218fd065106affc01d91f31b31ca99e662f`; excludes README/context/UI files included in C, so do not conflate identities.
- S preparation SHA-256: `7d5207d48e337870f249ca355ba3806621f3dc847cf84e33ad396900df52c492`.
- A preparation SHA-256: `681aa71b3c7c101b8d15194897ff2c44842fb1d69de17b4541946b8f92a0a2d8`; old candidate: `split-sha256-81a60df7cea26a553c679e4c72405ba3ab17defd615b6cff9b7e13140fac7f70`.
- Official guide SHA-256: base `2cfebc096a6e08370f288d468d90b60f7f9bcb938f94bf090816e910e48e75fc`; ref `1e574f356716ad55612247ffb7bbccbcdb484ad96599d63c7dca1af186b1fab7`.

No installer/discovery, native host-selection, rendered-media proof, or clean-worktree verification was performed in this chat.

## Next steps

1. **No unfinished authorized project work remains.** Read-only diagnosis and this handoff are complete. Ask what bounded scope the user wants next; do not repeat diagnosis or automatically implement proposals.
2. Optional, unapproved H3 source proposals: final fragment-by-fragment speaker-ID check; disambiguate unused connected soundtracks from requested audio references lacking target bindings. These reinforce/clarify existing rules, not demonstrated causal fixes. Any implementation requires a new bounded scope, owned-source edits and synchronization, and appropriate offline verification. Preserve original evaluation inputs and guide bytes.
3. Separate optional, unapproved evaluator proposal: retain supported async terminal notifications in normalized review evidence. This is not permission for recorder redesign, policy changes, or rewriting S. Keep this separate from H3 runtime-source work.
4. Any later acceptance attempt needs separately authorized fresh complete captures/assessment under a consistent snapshot. Acceptance requires 798 complete captures, 411 fully assessed valid initial judgments, every required adjudication/separate historical disposition, candidate boundary checks, no novel candidate hard failure, per-criterion parity, baseline-always-pass protection, context/self-contained packaging/provenance, and matched managed terminal success. No retries/replacements/reuse/cross-campaign aggregation/best-of.

## Blockers and open questions

- Semantic acceptance remains unmet: novel `wild-12` candidate hard failure and two incomplete criteria. Static diagnosis cannot repair or fill existing slots.
- Speaker omission's model/context causality is unknown. H3 soundtrack rules permit a finished artifact but also admit the conservative clarification interpretation; reinforcement effectiveness is untested.
- Async timeout omission is established in S's frozen normalizer/packet. Preserving that notification would improve evidence fidelity, not create successful baseline validation.
- Earlier H3 causality and historical Illustrious child fate remain unresolved. No new experiment, repair, preparation, paid execution, or evidence mutation is authorized.

## Prompt for a new chat

```text
TASK=DIAGNOSIS-COMPLETE-ASSESSMENT-NOT-ACCEPTED
Project: /home/mothmanex/.agents/skills/lfgg-skills. Read applicable guidance and docs/next-steps.md. Goal remains the approved seven-specialist Scenario Maker split; semantic acceptance at approved-plan approach step 6 is unmet. Read README resource ownership/evaluation controls and the linked plan before any newly authorized dependent work.

Source repair, both fresh capture suites, offline preparation, and the separately authorized paid assessment are complete. S is permanently claimed, closed NOT ACCEPTED, non-resumable/non-repeatable. User then explicitly authorized Read-only diagnosis of all three blockers; that investigation is complete. This handoff update did not authorize implementing proposals. No unfinished agreed work remains.

FIRST ACTION: ask through the interactive ask tool what bounded scope the user wants next, using this handoff's completed diagnosis. Do not repeat campaign verification, diagnosis, source repairs, captures, preparation, execute, provider diagnostics, or terminal waits/polls. Preserve unrelated work and all campaign records. Before any newly authorized change, read the relevant current owned source/docs and compare only the state needed for that scope; frozen evidence is not a live-worktree guarantee.

Paths relative to collection root:
E=skills/scenario-maker/evals/comparisons/model-split-20261008T184942Z; R=E/round-2; A=E/acceptance-20261010T220826Z; P=R/ai-review-recovery-1; D=E/provider-preflight-20261010T230004Z.
O=skills/scenario-maker/evals/comparisons/offline-repair-20261011T211940Z.
C=skills/scenario-maker/evals/comparisons/repaired-captures-20261011T214359Z.
S=skills/scenario-maker/evals/comparisons/repaired-assessment-20261012T005141Z.

S: 415 valid judgments (411 initial, 3 fresh adjudications, 1 separate historical), zero reused; independent managed exit1 matched exception-free runner. Existing disposition/evidence verification preserved. All798 outer captures and candidate boundaries/context/packaging bindings passed, but wild-12 attempt2 E1 is a novel candidate failure (baseline3/3,candidate2/3), and candidate h3-dev-02 attempt3 E1 plus baseline split-format-noobai attempt1 E1 remain not-run. Valid execution is not complete criterion assessment.

Completed diagnosis:
1. wild-12 opening speech omits(S1), introduced after cut. Actual delivered H3 profile, targeted reread, and official guide included speaker requirements; missing/unread rule is ruled out. Model/context cause unknown. Proposal only: final per-fragment speaker-ID check in owning H3 profile, not a fixture special case.
2. h3-dev-02 clarification is not necessarily required. Frozen profile110 asks about existing audio references without target bindings, but88 and209-233 explicitly omit unrequested connected soundtracks without renumbering later audio. Both rules reached generator. Request assigns Video B camera motion, no target-audio role; finished prompt omitting metronome while preserving standalone Audio2 is supported. Proposal only: distinguish unused connected soundtrack from intended audio reference needing clarification. Do not rewrite request/criterion or promote old not-run to pass.
3. Baseline split-format-noobai ran ONE bash lookup, timeout30, bg_1/running; raw trace275-276 then delivered custom async-result statusfailed/timeout30 BEFORE final. No successful baseline hits. Documentation examples are NOT runtime lookup evidence. Frozen S provenance review_split.py388-403 excludes rolecustom, so packet omitted timeout and reviewer saw only running handle. Candidate actually used timeout300 and received hits (suggest34.21s, tag mature_female0.04s). Existing candidate deadline/terminal-evidence mitigation already covers this baseline-only issue; no new candidate-source repair justified. Separate optional evaluator proposal: retain async terminal notifications, not recorder redesign or rewriting S.

Diagnosis was retained-file inspection only: no fresh reproduction, tests, smoke/model/provider/subprocess calls, campaign verification, or waits. Prior tests/smokes/campaign results in handoff are attributed, not newly run. Existing Danbooru terminal-evidence and H3 audio-state mitigations remain implemented but not proof of acceptance.

No proposal is implemented or newly authorized. Keep H3 source work separate from evaluator evidence normalization and paid campaigns. Preserve original requests/criteria/fixtures/routes/versions/repetitions and both official guide bytes. Seven specialists select family only; packages remain self-contained. Baseline-only h3-dev-02 attempt2 and h3-guide-01 attempt2 do not justify expanded candidate repair; regression:true is direction-neutral.

A/P/C/S cannot be resumed/repeated; D stays excluded. Never replace slots/judgments, reuse judgments, cross-campaign aggregate, choose best-of, promote uncaptured results, synthesize terminal evidence, refresh seals, or rewrite preparation/runner/final records. Preserve separate paid authorization and preparation-time offline flags. Do not conflate O runtime-only identity with C full-package identity.

Any future acceptance needs a separately authorized consistent new complete snapshot:798 captures,411 fully assessed valid initial judgments,every required fresh/historical adjudication,candidate boundaries,no novel candidate hard failure,per-criterion parity,baseline-always-pass protection,context/self-contained packaging/provenance,matched managed terminal success. Fixed modelgpt-6-astra/requestedhigh;generator300s/reviewer900s/outerwait930s/concurrency3 are controls,not authorization. AI review is not human sign-off/native host-selection/rendered-media proof; resolved reasoning/provider snapshot remain unknown.
```
