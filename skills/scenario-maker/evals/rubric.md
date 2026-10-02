# Scenario Maker prompt-behavior evaluation rubric

## Authority and scope

This evaluation suite implements the unchanged 16-case portfolio approved in [issue #16](https://github.com/lfelipegg/scenario-maker-skill/issues/16#issuecomment-5746288781), using the settled boundaries in [#17](https://github.com/lfelipegg/scenario-maker-skill/issues/17#issuecomment-5746449221), [#18](https://github.com/lfelipegg/scenario-maker-skill/issues/18#issuecomment-5746540497), [#19](https://github.com/lfelipegg/scenario-maker-skill/issues/19#issuecomment-5746665421), [#20](https://github.com/lfelipegg/scenario-maker-skill/issues/20#issuecomment-5746782536), and [#21](https://github.com/lfelipegg/scenario-maker-skill/issues/21#issuecomment-5746874984). Phase 3 applies the model-neutral scene-planning and preservation work authorized by [issue #5](https://github.com/lfelipegg/scenario-maker-skill/issues/5) and the invention/preservation contract in decision #17. It evaluates observable prompt-writing behavior and requested files, not rendered image or video quality.

The fixed starting revision is `5fcc3d0eded83c6a9aaf472a1dc8d5ce24011d9d`. Baseline failures are valid evidence. Phase 1 accepts a reviewed case set and honest, complete baseline capture; it does not require the fixed revision to satisfy future behavior.

On 2026-09-22 the maintainer approved keeping all 16 requests unchanged while moving only the existing `C07-COUNT` criterion's `mandatory_phase` from 6 to 2. This criterion-scheduling change creates a new cohort for future evaluation; it does not alter or relabel the immutable original Phase 1 evidence. Phase 3 does not change any request or criterion text in that portfolio.

The generating session MUST receive the case request and its declared fixtures, but MUST NOT receive this rubric, criteria, expected judgments, prior outputs, or reviewer notes.

## Concrete portfolio

Cases appear in this exact order in `evals/cases.jsonl`.

| Case | Approved behavior | Concrete mapping | Scheduled criteria |
| --- | --- | --- | --- |
| 01 | SDXL tags only, no negative prompt | Greenhouse on a cliff; one unlabeled comma-separated prompt | Routing/output P2; SDXL profile P4 |
| 02 | Adapt supplied scene to Krea 2 | Red teapot image-left of white cup; preserve the complete supplied still life | Routing P2; preservation P3; Krea 2 profile P4 |
| 03 | Revise only jacket color | Yellow denim jacket becomes red; all other facts retained | Routing P2; revision preservation P3 |
| 04 | Character design only | Adult lighthouse keeper with fixed anatomy, clothing, and equipment; no scene treatment | Character scope and preservation P3 |
| 05 | Empty courtyard with no people | Empty courtyard plus scoped exclusions; no unsolicited negative field | Routing P2; exclusion handling P5 |
| 06 | Exact required lettering `OPEN` | Bakery sign centered above door; literal presence and semantic binding checked separately | Exact text and preservation P3 |
| 07 | Four composition variants | Fixed cube/sphere/sign scene; only composition may vary | Count P2; distinctness and preservation P6 |
| 08 | Expand within an explicit word limit | Rowboat brief; complete output limited to 55 words | Output/limit P2; preservation P3 |
| 09 | Critique without replacement | Critique a vague prompt; no rewrite or variants | Critique routing P2 |
| 10 | Compare SDXL and Krea 2 prompts | Labeled analysis of two supplied prompts; no merged third prompt | Comparison routing P2; profile analysis P4 |
| 11 | Illustrious plus Danbooru and local lookup | Confirm `grey_hair` with the existing local lookup script; do not read raw CSV or expand related tags | Illustrious migration P4; tag/lookup evidence P5 |
| 12 | Pony profile preservation | Positive-only safe anime Pony prompt with fixed subject and scene | Preservation P3; profile migration P4 |
| 13 | NoobAI profile preservation | Positive-only space-normalized NoobAI prompt with fixed subject and action | Preservation P3; profile migration P4 |
| 14 | Existing Wan text-to-video route | One cohesive paragraph with subject, environment, camera motion, progression, and style | Routing P2; preservation P3 |
| 15 | Existing image-to-video route | Fixed synthetic source image; preserve first-frame content and add only requested motion | Routing P2; preservation P3 |
| 16 | Clothing-fragment wildcard export | Four clothing-only lines at `outputs/clothing-fragments.txt`, plus truthful external report | Export, fragment compatibility, and report P6 |

Existing-profile/route criteria are eligible for the original-baseline no-regression set immediately when all three original attempts pass; their scheduled repair phase does not postpone that protection. An inconsistent baseline remains an existing failure until its criterion's repair phase, rather than blocking unrelated earlier phases. No H3, Wan 2.2, Flux, Qwen, automatic skill-discovery, or other later Phase 7 case substitutes for these existing routes.

## Phase 3 coverage and acceptance schedule

Phase 3 consumes the model-neutral operation, scene-description, preservation, permission, and conflict rules in [`references/scene-composition.md`](../references/scene-composition.md) and [`references/constraints-and-revisions.md`](../references/constraints-and-revisions.md). Decision #17 is binding: Preserve, Balanced, and Explore grant invention permission only within the already selected operation and scope. A mode name never broadens adaptation or a narrow revision, and only an explicit compound permission opens its named local area.

The unchanged portfolio maps issue #5 and decision #17 as follows:

| Boundary | Existing portfolio coverage | Phase 3 scheduling |
| --- | --- | --- |
| Adaptation changes model-facing expression without changing the scene | Case 02 `C02-PRESERVE`; case 15 `C15-PRESERVE` also protects a supplied first frame | Hard and due in P3 |
| Cross-format conversion preserves subject count, colors, props, relationships, and exact lettering | Distributed coverage: cases 02, 12, and 13 preserve counts, attributes, props, and relationships; case 06 preserves and binds exact lettering. No one unchanged case combines the entire bundle | Hard preservation and lettering criteria are due in P3; target-profile expression remains P4 |
| Narrow revision changes only the requested detail | Case 03 `C03-REVISION` | Hard and due in P3 |
| Character-design scope excludes scene and presentation invention | Case 04 `C04-SCOPE` and `C04-DETAILS` | Hard and due in P3 |
| Expansion preserves supplied facts, necessary implications, exclusions, and locks | Case 08 `C08-PRESERVE` is due in P3; cases 05 and 07 retain dedicated exclusion and controlled-lock coverage | P3 preservation is due now; protected P5/P6 criteria also block regressions without changing their scheduled repair phases |
| Motion and source-image conversions preserve supplied content while applying only authorized temporal changes | Cases 14–15 preservation criteria | Hard and due in P3 |
| Critique does not silently replace; create/compare routes retain their requested operation | Cases 09–10 routing criteria | Already due in P2 and remains required |
| Clothing-only fragment scope remains narrow | Case 16 `C16-FRAGMENTS` | Scheduled repair remains P6; its original-baseline protection already blocks regressions |

No single existing request exhausts every decision #17 edge. The development-only probes below document uncovered plausible boundaries without modifying, replacing, or enlarging the approved 16-case human acceptance portfolio.

For Phase 3 candidate acceptance, run the same three repetitions of all 16 unchanged cases. Every applicable hard criterion due through Phase 3 must pass all three candidate repetitions; every `method: maintainer` decision among them requires explicit human review. Phase 1 trace requirements and every hard Phase 2 requirement remain due and cannot regress. The candidate must also preserve every check in the immutable original-baseline no-regression set. A future-phase criterion remains reported but does not block Phase 3 unless it is independently protected by that original-baseline set.

Advisory criteria never compensate for a hard failure. Phase 3 acceptance does not imply acceptance of P4–P7 repairs, any supplemental probe, or rendered-media quality.

## Phase 4 coverage and acceptance schedule

Phase 4 implements [modular model profiles and Krea 2 support](https://github.com/lfelipegg/scenario-maker-skill/issues/6), authorized and claimed in [this record](https://github.com/lfelipegg/scenario-maker-skill/issues/6#issuecomment-5787501931). [Decision #19](https://github.com/lfelipegg/scenario-maker-skill/issues/19#issuecomment-5746665421) supplies settled presets and detail controls. The [model index](../references/model-prompts.md) routes to separate profiles; this phase does not retune the migrated Illustrious/Pony/NoobAI conventions or implement Phase 5.

All 16 requests, criteria, severities, and due phases remain unchanged. Existing cases already schedule the following behavior for Phase 4:

| Boundary | Portfolio criteria | Evidence |
| --- | --- | --- |
| SDXL compact phrases honor explicit output constraints | `C01-PROFILE`, `C01-OUTPUT` | Human hard judgments |
| Krea 2 natural-language adaptation preserves the supplied scene without detail-driven invention | `C02-PROFILE`, `C02-PRESERVE`, `C02-OUTPUT` | Human hard judgments |
| Comparison distinguishes fidelity, expression, and ambiguity for both profiles | `C10-ANALYSIS`; `C10-ROUTING` remains hard | Human advisory analysis; no upgrade or weakening of severity |
| Legacy Illustrious/Pony/NoobAI profile conventions survive migration | `C11-PROFILE`, `C12-PROFILE`, `C13-PROFILE` and existing protected content criteria | Human hard judgments |
| Core routing, scope, scene preservation, exact lettering, and existing video/export behavior remain protected | All hard checks due through Phase 3 and the immutable original no-regression set | Mechanical and human checks according to each unchanged criterion |

Run the full 96-attempt paired cohort against the fixed original revision. All hard checks due through Phase 4 must pass every repetition, as must the original baseline protection set and newly accepted Phase Two/Three hard requirements. Later baseline variance never removes a protection. Missing human judgments remain `not-run` and block acceptance. The three accepted Phase Three `C10-ANALYSIS` failures are advisory findings for this phase, not a reason to rewrite earlier evidence.

`evals/phase-four-probes.jsonl` supplements development coverage of both SDXL presets, all Krea detail levels, explicit formatting, exact lettering and relationships, negative-channel consumption, and identity/interface boundaries. These are single-run development observations, not additions to the approved acceptance portfolio and not semantic passes. The same separation from rubric exposure and immutable raw capture applies. Index/link checks establish reference integrity, not generated-media quality.

After this milestone, collect actual ordinary-use failures before proposing broader implementation. Synthetic probes, baseline failures, and hypothetical risks are not ordinary-use reports. Keep later phases unstarted; Phase Four authorization does not authorize committing or pushing.

## H3 implementation development coverage

On 2026-09-22 the maintainer explicitly requested implementation of the settled [H3 contract](https://github.com/lfelipegg/scenario-maker-skill/issues/25#issuecomment-5750413381), bringing these bounded additions forward without accepting the broader phase chain. The four scoped units are [full-reference generation](https://github.com/lfelipegg/scenario-maker-skill/issues/26), [source-video editing](https://github.com/lfelipegg/scenario-maker-skill/issues/27), [first-frame video](https://github.com/lfelipegg/scenario-maker-skill/issues/28), and [frame-derived still editing](https://github.com/lfelipegg/scenario-maker-skill/issues/29).

`evals/h3-probes.jsonl` contains 44 supplemental development probes mapped by `acceptance_case` to all 21 approved H3 categories. Opposite branches exercise required clarification versus valid authoring, opening anchoring versus a completed edited output frame, audio reuse versus reference, explicit silence versus unspecified audio, and enhancement/negative-output permissions. Category 21 also exercises existing model dialects and task separation. These probes do not replace or modify the original 16-case portfolio.

The initial isolated capture in `evals/capture-checks/2026-09-22-h3-boundaries/` retains the selected runtime snapshot, requests, outputs, manifests, and traces: one attempt for the original 43 probes plus one for each original case. It retains a discovered audio-role defect rather than relabeling it as a pass. Subsequent `2026-09-22-h3-audio-role-repair`, `2026-09-22-h3-audio-binding`, `2026-09-22-h3-final-boundaries`, and `2026-09-22-h3-output-precedence` capture directories retain focused reruns, the added explicit-target-audio probe, and the correction distinguishing inferred output shape from an explicit prompt-only restriction. Generating sessions receive requests and declared fixtures, never expected behaviors or reviewer criteria.

`evals/results/2026-09-22-h3-development/` holds separate mechanical results and `development-review.json`, which records the 79 captures, observed defects, corrective evidence, and final source identity. Omitted repetitions and maintainer judgments remain `not-run`, not inferred passes. Development observations are neither three-repetition acceptance nor generated-media quality evidence. No generation or frame extraction is part of this evaluation.

## Fixed fixture

`evals/fixtures/case15-geometric-source.png` is a deterministic 128 × 80 RGBA PNG authored from flat geometric raster primitives. It depicts pale-cyan sky above blue water, a red-hulled sailboat with a dark mast, a yellow right sail and white left sail, a white cloud in the upper right, and three pale horizontal ripple marks. It contains no generated or private material.

SHA-256: `96d3453296fdd1239b21aeda140412632b643d96cb3980986739da4470bd8ded`

Any byte change to this fixture creates a new cohort. Case 15 reviewers judge the actual visible fixture, not only this description.

## Case and criterion contract

Each JSONL record has this schema:

- `id`, `title`, and exact `request`
- `fixtures`: paths relative to `evals/fixtures`
- `operation`, `task`, `scope`, and `target_profile`
- `required_details` and `prohibited_changes`
- `output_contract`
- `criteria`, each with globally unique `id`, `description`, `method`, `check`, `severity`, `mandatory_phase`, and `decision_url`

`severity: hard` represents an acceptance requirement when due. `severity: advisory` records quality or preference and never compensates for a hard failure. `mandatory_phase` is criterion-granular: routing/output P2, preservation P3, named still-image profiles/migration P4, constraint/tag handling P5, controlled variants/export P6, and later additions P7. Trace evidence uses P1. Existing accepted behavior is protected through the original-baseline no-regression set independently of the scheduled repair phase.

## Mechanical methods

Mechanical evaluation is deliberately narrow:

- `exact_text` checks literal presence only. It does not prove that text is bound to the correct sign, subject, or relationship; a separate maintainer criterion covers that meaning.
- `word_limit` tokenizes the entire final output on Unicode whitespace. Case 08 declares a maximum of 55 tokens and requests prompt-only output, so labels or commentary consume the same limit.
- `numbered_count` counts numbered entries at line starts. It does not establish semantic distinctness.
- `export` resolves the declared path under the attempt workspace, counts nonblank physical lines, rejects blank entries and exact duplicate lines, and verifies the expected line count. It does not establish that a line is clothing-only or insertion-compatible.
- `trace_policy` inspects captured observable tool calls and actions against the evaluator's local-tool allowlist. It does not prove every request-specific constraint or claim that the shell is sandboxed. Unknown event formats, incomplete capture, or ambiguous shell commands yield `not-run`, never a pass. Case 11 separately requires human review of actual lookup evidence; spelling presence alone is not confirmation.

No keyword-absence proxy may award semantic exclusion, preservation, style, subject binding, relationship, profile fidelity, controlled-variant distinctness, or fragment compatibility. Exact-output equality is not appropriate for free-form prompts.

## Human review

The maintainer is the final semantic reviewer. Semantic criteria begin unfilled. A generator, automated evaluator, or model review MUST NOT grant semantic acceptance.

Reviewer decisions are append-only JSONL records with:

```text
{case_id, attempt, criterion_id, state, human:true, reviewer:"human:<stable-id>", reviewed_at, evidence}
```

`state` is exactly `passed`, `failed`, or `not-run`. Only an explicitly human-approved review entry may pass a `method: maintainer` criterion. Evidence should briefly identify the relevant output or artifact detail. Missing review is `not-run`; it is never inferred from mechanical success.

`reviewed_at` must include a timezone; evidence must be nonempty. The evaluator rejects malformed, duplicate, unknown-criterion, and non-human review entries. Leave the generated pending template unsubmitted until actual review; its null fields are not approvals.

For advisory style comparisons, record preference, tie, or abstention in reviewer evidence without converting preference into a hard pass. The suite does not evaluate rendered media.

## Three-attempt reporting and acceptance

Run exactly three attempts for every case and revision. Retain errors, timeouts, missing outputs, and unsuccessful outputs; never select the best attempts or silently replace one. A complete baseline has 16 × 3 = 48 attempts.

Report per case and criterion as counts across all three attempts, not as a single aggregate. Mixed results remain explicit, for example `passed 2 / failed 1 / not-run 0`. A normal completed output may still be scored when another execution component failed, if its raw evidence is complete enough for that criterion. Execution errors and trace completeness remain separate.

At Phase 1, acceptance requires the reviewable portfolio and complete, honest evidence rather than prompt success. For later phases, each applicable hard criterion due by that phase must pass all three candidate repetitions; `failed` or `not-run` blocks that criterion. Future-phase criteria remain visible but do not block an earlier phase.

The **original baseline no-regression set** consists only of checks that pass all three attempts in the first immutable 48-attempt baseline. Those checks remain protected even if a later baseline rerun varies. Checks passing only one or two baseline attempts are recorded as existing mixed failures with their scheduled repair phase; zero-pass checks are recorded failures. Such baseline inconsistency does not by itself block an unrelated phase, but a hard requirement must pass every repetition when its repair phase is due. Newly accepted hard requirements join the protected set as their phases complete.

## Development-only supplementary probes

`evals/phase-three-probes.jsonl` is a compact development aid for decision #17 boundaries that the unchanged portfolio does not isolate. It is **DEVELOPMENT-ONLY**: its records are not approved cases, do not replace or add to the 16-case portfolio, are not inputs to the evaluator or capture schedule, and must not be mixed into a 48- or 96-attempt cohort.

`evals/wild-probes.jsonl` is supplemental development coverage for Wild activation, concept coherence, preservation and scope boundaries, ambiguity, multiplicity, wildcard output, and bounded H3 audiovisual delegation. It is likewise **DEVELOPMENT-ONLY**: its 19 records do not alter the 16-case portfolio, formal acceptance criteria, evaluator, or capture schedule. Captured prompt text and wildcard artifacts are prompt-authoring observations, not generated-image/video evidence. Distinctiveness, coherence, and semantic fidelity require concrete human review; execution completion and keyword presence do not establish a pass.

`evals/unbound-probes.jsonl` adds 12 **DEVELOPMENT-ONLY** probes for autonomous scenario completion from minimal seeds, whole-scenario delegation, actual opening images, preservation, scope and operation boundaries, required-source/reference-role clarification, ambiguity, and multiplicity. Like the Wild probes, these do not alter the fixed portfolio, formal criteria, evaluator, or capture CLI. `unbound-03` and `unbound-04` use the actual PNG from [Fixed fixture](#fixed-fixture): retain its hash and inspect the trace to confirm pixel inspection, not receipt of a fixture description. Described-image probes such as `unbound-05` and `unbound-09` test supplied textual evidence and cannot establish actual-image capability. Retain source identity, raw output, trace/context, errors, fixture hashes, and tool provenance; record concrete diagnostic observations outside immutable attempt directories. Completion is not formal acceptance or generated-media quality evidence.

Development runs may observe a probe response and record the raw output, including whether the assistant returned an artifact or requested clarification. Such observation is diagnostic only; it cannot produce a semantic pass or an acceptance claim. The expected behaviors for every probe require human semantic judgment if the maintainer later promotes that exact probe into an acceptance portfolio. Until such approval, no probe needs or receives an acceptance review:

| Probe | Boundary observed during development | Acceptance status |
| --- | --- | --- |
| `p3-dev-01` | Preserve does not infer rain, night, or other facts from a sparse wet-street source | Development observation only; human semantic review required if promoted |
| `p3-dev-02` | Balanced clothing and isolated-asset scopes add local design detail without wearers, support props, or scenes | Development observation only; human semantic review required if promoted |
| `p3-dev-03` | Explore respects a closed subject roster but may populate an explicitly open roster | Development observation only; human semantic review required if promoted |
| `p3-dev-04` | Mode names cannot broaden adaptation or narrow revision; explicit compound background permission applies only to the background | Development observation only; human semantic review required if promoted |
| `p3-dev-05` | A later specific instruction locally replaces a prior lock and establishes the new preserved detail | Development observation only; human semantic review required if promoted |
| `p3-dev-06` | Faithfully expressible ambiguity is preserved, while a forced interpretation triggers clarification | Development observation only; human semantic review required if promoted |
| `p3-dev-07` | Incompatible exact-text and hard-length requirements trigger clarification rather than omission, alteration, or overrun | Development observation only; human semantic review required if promoted |

The current evaluator intentionally has no probe schema or probe-scoring path. Do not infer a pass from keyword presence, output shape, or a model grader.

## Raw evidence and immutability

For each attempt, the capture runner creates:

```text
results-or-baseline-root/
  cohort/
    case-id/
      attempt-N/
        attempt.json
        output.txt          # when normal output exists
        trace.jsonl         # raw OMP JSONL events
        stderr.txt
        ...captured generated files...
```

`attempt.json` records:

```text
{case_id, attempt, revision,
 execution:{status:'completed'|'error'|'timeout'|'not-run', exit_code},
 raw:{output:'output.txt'|null, trace:'trace.jsonl', stderr:'stderr.txt'},
 trace_complete,
 artifacts:[{path, stored_path, sha256, bytes}]}
```

The raw attempt directory is immutable after capture. Evaluator scores, human reviews, anonymous label maps, summaries, and corrections belong outside it. Preserve raw JSONL OMP events and captured requested files. Record full revision, actual OMP version, requested and observable resolved model identity, `high` reasoning, exposed settings, command, tool availability, permissions, instruction/fixture/config provenance, date, and unavailable metadata. Unknown values remain `unknown`. Redaction or incomplete traces must be declared and cannot be represented as byte-complete evidence.

A changed case, criterion, fixture, environment, or capture mechanism creates a new cohort. Never overwrite the original Phase 1 baseline or present unlike cohorts as controlled comparisons.

## Reproduction procedure

1. Have the maintainer review `evals/cases.jsonl`, this rubric, and the fixture before any baseline model call.
2. Use fresh, isolated workspaces and sessions for each case, revision, and repetition. Load only the selected Scenario Maker revision and its applicable references. Hold instructions, fixture bytes, settings, tools, and permissions constant.
3. Permit local Danbooru lookup for case 11, fixture inspection for case 15, and the requested fixture-local file write for case 16. Do not permit web research, other skills, delegation, model switching, or image/video generation. Do not provide this rubric to the generator.
4. Capture the fixed original-baseline behavior with `python3 evals/run_baseline.py --out evals/baseline/<new-cohort>`. This mode still owns the fixed revision and 16 × 3 schedule; it does not read the worktree as the selected skill. A development `--smoke` capture is one separate smoke attempt and is never acceptance evidence.
5. Evaluate into a separate directory with `python3 evals/evaluate.py --cases evals/cases.jsonl --results evals/baseline/<cohort> --out evals/results/<new-review-dir> [--reviews PATH]`. Mechanical checks never fill semantic judgments.
6. Confirm all 48 attempt manifests and raw evidence references exist, record limitations, then freeze the cohort. Do not run or fabricate missing human review.

Reference environment from the decision: OMP observed `18.2.6`, requested model `openai-codex/gpt-6-astra`, explicit reasoning `high`. Record the actual values at execution; the requested model name is not proof of an immutable provider snapshot.

### Capture boundary

Without `--candidate-worktree`, `run_baseline.py` preserves the fixed original-baseline capture path. It refuses an existing output directory. Default scheduling submits cases in portfolio order, repetitions 1–3, with at most three fresh OMP processes in flight and a 300-second limit per attempt. Errors and timeouts are retained without replacement. The optional paired path is specified below.

Each fixed-baseline attempt uses a separate temporary workspace outside this repository, an explicit selected-skill path exported from the fixed revision, and independent fixture/cache paths. Selected source files are read-only hardlinks to one per-cohort snapshot; CSVs are not recopied for each attempt. Candidate attempts have the same isolation but hardlink the retained candidate snapshot. Only requested generated text artifacts are copied back. Fixed source content is recoverable through its Git revision and file hashes; candidate source content is recoverable through the retained content-addressed snapshot and file hashes.

`omp-config.json` disables discovery, external research surfaces, automatic retries/model fallback, compaction, advisor, memory, title generation, and media generation. CLI flags expose only local `read`, `grep`, `glob`, `bash`, and `write`. This is a controlled tool/prompt policy, **not an OS filesystem/network sandbox**. The capture extension replaces inherited system instructions with the exact `generator-system.txt` contents; it does not load the rubric or future prompt policies.

`context.jsonl` records the effective system prompt, selected model, reasoning, active tools, and allowlisted client-visible provider request body fields (including actual instructions, tools, and input). Credentials and headers are not captured. The body may use incremental provider context within one attempt; raw OMP events retain the local message/tool history. Hidden provider instructions, immutable snapshot identity, seed, and fingerprint remain unavailable. `partial-output.txt`, when present without a completed response, is retained but is not a normal final output.

The manifest records the actual host/model request, command, scheduling, deadline, environment, source/fixture/evaluator hashes, and limitations. Run a separate `--smoke` capture to verify JSON events, effective context isolation, output extraction, and file capture before baseline use. Smoke evidence is never one of the 48 portfolio attempts.

## Later paired cohorts

A complete candidate comparison contains 96 attempts: three fixed-baseline and three candidate attempts for each of the same 16 cases. The paired runner reruns the fixed revision alongside a content-addressed snapshot of the current worktree, interleaves adjacent baseline/candidate submissions for each case and repetition, and preserves case/repetition identity. The configured `--jobs` value is the maximum number of OMP processes in flight. There are no retries or replacement slots: errors, timeouts, partial output, and missing output remain evidence.

The candidate source is not a Git revision. `--candidate-worktree` copies the current `SKILL.md`, `references/`, source scripts, and the same tracked Danbooru CSV inputs used by the baseline into `candidate-source-snapshot/`, excludes caches, bytecode, and the generated SQLite index, hashes every retained file, and identifies the source as `worktree-sha256-<manifest-hash>`. The retained immutable source snapshot plus its file manifest is the recovery authority for that side. The baseline side remains recoverable from the fixed Git revision and its file manifest. Never describe the worktree identity as a commit.

Freeze the intended source files before invoking a paired capture, then run:

```text
python3 evals/run_baseline.py --candidate-worktree --out evals/comparisons/<new-cohort>
```

The output path must not already exist. The comparison root records the ordered submission schedule, source identities, capture-tool provenance, controlled-equal settings, the intentional selected-source difference, and a summary. Raw attempts are independently evaluable beneath `baseline/` and `candidate/`. A full run must contain exactly 16 cases × 3 attempts × 2 sides.

Before an expensive full run, the same path may be exercised with one separate pair:

```text
python3 evals/run_baseline.py --candidate-worktree --smoke --out evals/capture-checks/<new-paired-smoke>
```

Paired smoke checks capture mechanics only. It is not one of the 96 attempts, cannot establish semantic or mechanical acceptance, and must not be merged into a full cohort.

Run the existing evaluator separately for each side:

```text
python3 evals/evaluate.py --cases evals/cases.jsonl --results evals/comparisons/<cohort>/baseline --out evals/results/<baseline-review-dir>
python3 evals/evaluate.py --cases evals/cases.jsonl --results evals/comparisons/<cohort>/candidate --out evals/results/<candidate-review-dir>
```

These runs provide mechanical scores and independently anonymized review material. The evaluator does **not** currently create a shared randomized label map that binds each baseline/candidate case-and-attempt pair. Before paired blind preference review, an integration step must combine the two review packets by exact `{case_id, attempt}`, assign two randomized side labels per pair, and retain the shared label mapping outside both review cards and immutable raw trees. Do not infer or fabricate paired review support from separate evaluator runs.

The maintainer remains the final semantic reviewer. Candidate acceptance for any target phase requires all applicable hard criteria due through that phase to pass all three candidate attempts, completed human judgments for maintainer criteria, and comparison against the protected original-baseline no-regression set. A fresh paired baseline rerun measures contemporaneous environment variance; it is not a replacement for, or relabeling of, the first immutable baseline. Record scheduling and every observed environment difference. Latency and cost remain advisory.
