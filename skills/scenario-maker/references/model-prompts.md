# Model-Specific Prompt Profiles

Use only for an explicitly named supported model or clear alias. Read [Routing](routing.md), [Output Contracts](output-contracts.md), [Scene Composition](scene-composition.md), and [Constraints and Revisions](constraints-and-revisions.md) first. Then read the selected profile below; this index does not replace it. With no target, use generic task guidance.

## Model Detection

| Named target or alias (case-insensitive) | Profile |
| --- | --- |
| `sdxl`, `stable diffusion xl`, `stable-diffusion-xl`, `stable diffusion xlarge`, `SDXL 1.0 Base`, `stabilityai/stable-diffusion-xl-base-1.0` | [SDXL](models/sdxl.md) |
| `krea 2`, `local krea 2`, `Krea 2 RAW`, `Krea 2 Turbo`, `krea/Krea-2-Raw`, `krea/Krea-2-Turbo`, `oss_raw`, `oss_turbo` | [Local Krea 2 RAW/Turbo](models/krea-2.md) |
| `pony`, `pony diffusion`, `pony diffusion v6`, `Pony Diffusion V6 XL`, `pdxl` | [Pony v6](models/pony-v6.md) |
| `illustrious`, `illustrious xl`, `illustrious-xl`, `ilxl` | [Illustrious](models/illustrious.md) |
| `noobai`, `noob ai`, `noobai xl`, `noobai-xl`, `nai noob`, `noob v-pred` | [NoobAI](models/noobai.md) |
| `MiniMax H3`, `H3`, `H3-Base-Ref2VA`, `H3 Ref2VA`, `MiniMaxH3ReferenceToVideo`, `H3-Base-FL2VA`, `H3 FL2VA`, `MiniMaxH3ImageToVideo` | [MiniMax H3](models/minimax-h3.md); resolve the checkpoint/task/local interface before route-dependent authoring |

Exact versions and documented identifiers are delimited in each profile. Unqualified local Krea 2 uses shared open RAW/Turbo guidance without choosing a checkpoint. Hosted Krea 2 Medium/Large/Medium Turbo and other Krea-branded models are not aliases of these open checkpoints. Do not transfer profile guidance to an unrelated version or interface. Clarify identity only when it materially affects the requested adaptation or capability.

Bare `MiniMax H3` or `H3` selects identity guidance, not an automatic checkpoint or hosted/local choice. The H3 profile covers only the selected ordinary native local ComfyUI base-checkpoint routes. Hosted `MiniMax-H3`/`MiniMax-H3-Max`, Hailuo, and adjacent tasks do not inherit that support. Context can resolve an unambiguous local target; clarify consequential ambiguity.

## Shared Presentation Contract

Profiles supply compatible, unspecified defaults for language, ordering, prefixes, and model-facing expression—not permission to change the scene. Explicit format, normalization, prefix exclusion, length, and output shape override presentation defaults, not protected content or verified hard input requirements. A listed field or example never requires absent subjects, props, actions, settings, lighting, or style.

Return only the requested artifact. Negatives require a request and appropriate handling of the actual consuming workflow. Notes belong only in requested notes or relevant analysis, except the bounded H3 enhancement offer in [Output Contracts](output-contracts.md). Keep subject attributes/actions together, relationships explicit, and required lettering exact. Detail cannot authorize invention or padding; [Prompt Types](prompt-types.md#length-targets) supplies approximate length guides, not sentence quotas or checkpoint limits.

For multiple named targets, read every relevant profile. Prompt writing produces one prompt per target with minimal labels; comparisons remain analysis. Compare scene fidelity, profile expression, and ambiguity separately, distinguishing recommendations from requirements and prompt wording from rendered quality. An explicit shared-prompt request produces one compatible prompt or clarification, never a silent split.

## Wildcards With Named Models

Apply the requested format and authorized content first. Each full-prompt line otherwise uses its selected profile's compatible dialect defaults: Pony score/source/rating prefixes, Illustrious Danbooru-style tags, NoobAI space-normalized tags with appropriate escaping, SDXL compact natural-language phrases, Krea 2 natural-language paragraphs, or H3 route-specific reference bindings and temporal meaning. For H3, serialize applicable prompt sections onto the requested single line; do not put an enhancement offer inside a wildcard entry. Follow [Wildcards](wildcards.md) for file behavior; profiles do not redesign fragment or export contracts.
