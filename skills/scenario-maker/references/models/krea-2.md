# Local Krea 2

This profile supplies compatible defaults only after the scene and output have been resolved. Follow [Output Contracts](../output-contracts.md) for response shape and explicit-format precedence, and [Constraints and Revisions](../constraints-and-revisions.md) for preservation, scope, and invention permissions.

## Identity and Aliases

- Unqualified `local Krea 2` uses guidance shared by the open RAW and Turbo checkpoints without silently selecting either one.
- `Krea 2 RAW`, `krea/Krea-2-Raw`, and reference CLI identifier `oss_raw` identify the open undistilled base checkpoint. `Krea 2 Turbo`, `krea/Krea-2-Turbo`, and `oss_turbo` identify the open eight-step distilled checkpoint.
- The open RAW/Turbo checkpoints are not aliases for hosted **Medium**, **Large**, or **Medium Turbo**. Do not infer a one-to-one mapping or transfer hosted-only controls to a local workflow.
- Other Krea-branded models are not Krea 2 aliases. Clarify identity only when it materially affects the requested adaptation, syntax, or capability.

## Prompt Language and Detail

- **Product default:** one cohesive natural-language paragraph at **Medium**, approximately 150 tokens. Official guidance recommends natural language and says long detailed prompts yield the best results while minimal prompting remains supported. The selected default is a product presentation choice, not a parser requirement, benchmarked optimum, or rendered-quality guarantee.
- **Alternatives:** Very Short (about 75 tokens) for minimal/direct wording and Long (about 300+ tokens) for more permitted detail. These are approximate targets, not quotas or model limits. Stop when the authorized content is fully expressed; never pad a sparse source.
- Medium or Long adds only detail permitted by the operation, scope, and invention mode. Adaptation remains Preserve at every detail level; detail never authorizes new subjects, props, actions, relationships, or other scene facts.
- An explicit request for tags, prose, bullets, JSON, another structure, or a hard length overrides the paragraph preference when compatible. It does not waive required scene content or a verified hard interface requirement.
- Preserve every supplied subject, attribute binding, action, count, color, prop, exclusion, spatial relationship, medium, and exact lettering.
- Krea's published `expansion.txt` is an optional helper-LLM system prompt, not intrinsic checkpoint behavior. Its useful expansion contract is faithfulness, grouped subject attributes/actions, grounded relationships, exact quoted text, no unsupported specificity or invented objects, light polishing of already detailed input, preserved medium, and one paragraph when that helper is selected.

## Ordering and Optional Prefixes

- Krea 2 has no official rigid clause order. Organize authorized content for clarity, keeping each subject beside its own attributes and actions and stating spatial relationships explicitly.
- For requested visible text, preserve exact spelling, case, and punctuation, bind it to the correct carrier, and put the words to be rendered in quotes. This is Krea's official recommendation, not a guarantee of typography accuracy.
- Add no automatic prefix, quality-token stack, style package, camera package, or other boilerplate. A field or example is not a checklist of facts to invent.

## Negative Prompts

- Do not add a negative field to ordinary single-prompt output and do not attach a stock blacklist.
- When the user requests negatives and the exact workflow consumes them, include only relevant exclusions or failure concerns. Never negate requested content or import an SDXL negative package.
- The official reference CLI exposes one positive `prompt` and no negative argument. The lower-level sampler accepts `negative_prompts` only through its programming interface and uses that branch when guidance is greater than zero; the recommended Turbo path uses CFG `0.0` and skips it.
- A RAW checkpoint or visible negative socket alone does not establish that the actual workflow consumes negative conditioning. If a requested negative appears intended for a verified non-consuming workflow, explain the mismatch and ask how to proceed. Return standalone negative text directly only when that intent is already clear; never fold it silently into the positive prompt.

## Interface Syntax

- Default to portable plain text. The official local CLI takes a positional prompt and selects `oss_raw` or `oss_turbo` with `--checkpoint`.
- RAW's documented reference invocation uses 52 steps and CFG 3.5; Turbo's uses 8 steps, CFG `0.0`, and `mu=1.15`. These are sampler settings, not prompt text.
- Prompt enhancement is a separate workflow step. Do not describe an LLM enhancer as checkpoint behavior, invoke it automatically, or promise preservation through an unknown downstream enhancer.
- Parenthetical weights, special delimiters, LoRA triggers, negative sockets, and enhancement toggles are adapter or graph features and require evidence for the named workflow.
- Hosted Creativity, Generative Sliders, moodboards, style references, and hosted Medium/Large selectors are not local RAW/Turbo prompt syntax.

## Examples

These examples adapt the same source scene without adding facts: **a red cube left of a blue sphere; a sign reads `Open late!`**

- Very Short minimal/direct: `A red cube is left of a blue sphere. A sign reads "Open late!"`
- Default Medium paragraph: `A red cube is positioned to the left of a blue sphere. A sign displays the exact words "Open late!"`

The default remains short because the source is sparse. Medium or Long does not authorize a setting, surface, lighting treatment, or extra prop, and an already detailed source should be lightly polished rather than expanded for its own sake.

## Primary Sources

- [Krea 2 official repository README, fixed revision](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/README.md)
- [Official Krea 2 prompting guide, fixed revision](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/docs/prompting.md)
- [Official optional expansion system prompt, fixed revision](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/docs/expansion.txt)
- [Official reference CLI, fixed revision](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/inference.py)
- [Official reference sampler, fixed revision](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/sampling.py)
- [Official Krea 2 RAW model card](https://huggingface.co/krea/Krea-2-Raw)
- [Official Krea 2 Turbo model card](https://huggingface.co/krea/Krea-2-Turbo)
