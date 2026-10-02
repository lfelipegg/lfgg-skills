# SDXL 1.0 Base

This profile supplies compatible defaults only after the scene and output have been resolved. Follow [Output Contracts](../output-contracts.md) for response shape and explicit-format precedence, and [Constraints and Revisions](../constraints-and-revisions.md) for preservation, scope, and invention permissions.

## Identity and Aliases

- `SDXL`, `Stable Diffusion XL`, `Stable-Diffusion-XL`, and `Stable Diffusion XLarge` use this profile when they unambiguously mean the Stability AI family.
- Unqualified `SDXL` uses general guidance grounded in `stabilityai/stable-diffusion-xl-base-1.0`. It does not imply a fine-tune, the separate refiner, a base-plus-refiner pipeline, or a particular interface.
- If the named checkpoint or interface materially changes the requested syntax or capability, use that exact contract rather than assuming it from this base profile.

## Prompt Language and Detail

- **Product default:** compact ordinary-English phrases at **Very Short**, approximately 75 tokens. This is a presentation choice supported by official compact examples and Stability AI's statement that a few words can suffice; it is not a checkpoint grammar or a rendered-quality guarantee.
- **Available detail:** Very Short (about 75 tokens), Medium (about 150), and Long (about 300+). These are approximate targets, not quotas or model limits. Stop when the authorized content is fully expressed; never pad a sparse source.
- Medium or Long adds only detail permitted by the operation, scope, and invention mode. Adaptation remains Preserve at every detail level. Changing detail does not switch the compact phrase dialect to prose.
- Use descriptive prose when the user requests it. Any explicit prose, tag, normalization, structure, or hard-length instruction overrides the compact presentation default while preserving required content.
- Preserve every supplied subject, attribute binding, action, count, color, prop, exclusion, spatial relationship, and exact lettering. Detail controls never authorize new subjects, props, relationships, or scene facts.

## Ordering and Optional Prefixes

- SDXL has no official mandatory component order. Arrange the authorized details for clarity rather than filling subject, setting, camera, lighting, or style slots that the source did not supply or permit.
- Keep each subject close to its attributes and actions, and state relationships explicitly; disconnected object phrases do not preserve who holds what or what is left, above, behind, or in front of what.
- Preserve visible lettering exactly, including case and punctuation, and bind it to its carrier. Clearly quoted lettering is a fidelity-oriented editorial convention, not official SDXL syntax or a guarantee of legibility.
- Add no automatic prefix, `masterpiece`/quality stack, camera package, style package, or other boilerplate. Stability AI explicitly says qualifier terms such as `masterpiece` are not required merely to obtain quality.

## Negative Prompts

- Do not add a negative field to ordinary single-prompt output and do not attach a stock blacklist.
- When the user requests negatives and the named workflow consumes them, include only relevant exclusions or failure concerns. Never negate requested content or import a generic package.
- If negative text is intended for a workflow verified not to consume it, explain the mismatch and ask how to proceed. Return standalone negative text directly only when that intent is already clear; never fold it silently into the positive prompt.
- Negative input is an interface capability, not required SDXL text grammar. In Diffusers, `negative_prompt` and `negative_prompt_2` are optional and are ignored when classifier-free guidance is inactive.

## Interface Syntax

- Default to portable plain text. Parenthetical weights, special delimiters, LoRA triggers, node conventions, and other adapter syntax require evidence for the named interface.
- Diffusers accepts `prompt`; it can also address SDXL's second text encoder with optional `prompt_2`. Optional `negative_prompt` and `negative_prompt_2` provide corresponding negative inputs under active classifier-free guidance. These fields do not establish a visible ordering or weighting syntax.
- The base checkpoint can run alone or participate in a separate refiner workflow. Do not assume the refiner or promise that it improves the user's requested result.
- The official model card reports unreliable legible text and difficult compositional relationships. Preserve requested lettering and relationships anyway; mention limitations only in relevant analysis or requested notes, and never promise exact realization.

## Examples

These examples adapt the same source scene without adding facts: **a red cube left of a blue sphere; a sign reads `Open late!`**

- Default compact phrases: `red cube to the left of a blue sphere; sign reading "Open late!"`
- Descriptive prose requested: `A red cube is to the left of a blue sphere. A sign reads "Open late!"`

The quotes preserve and identify the lettering; they are not claimed checkpoint syntax. Medium or Long would not authorize a setting, surface, lighting treatment, or extra prop for this sparse Preserve adaptation.

## Primary Sources

- [Stability AI SDXL 1.0 Base model card, fixed revision](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/462165984030d82259a11f4367a4eed129e94a7b/README.md)
- [Stability AI announcement: simpler language and qualifier terms](https://stability.ai/news-updates/stable-diffusion-sdxl-1-announcement)
- [SDXL technical report](https://arxiv.org/abs/2307.01952)
- [Diffusers SDXL pipeline API, v0.40.0](https://huggingface.co/docs/diffusers/v0.40.0/en/api/pipelines/stable_diffusion/stable_diffusion_xl)
