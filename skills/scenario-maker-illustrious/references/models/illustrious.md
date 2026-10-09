# Illustrious XL

This profile supplies compatible prompt-presentation defaults only after the scene and requested output have been resolved. [Output Contracts](../output-contracts.md) owns response shape and precedence; [Constraints and Revisions](../constraints-and-revisions.md) owns preservation, invention, and scope. The profile never authorizes absent scene facts or an automatic prompt package.

## Identity and Aliases

This profile covers the official **Illustrious XL v0.1** early-release base and **Illustrious XL v1.0** base behavior represented by the sources below. Recognized aliases are `illustrious`, `illustrious xl`, `illustrious-xl`, and `ilxl`.

An explicit checkpoint or version remains exact. Do not silently reinterpret an unqualified alias as Illustrious XL v1.1, a later announced release, a community fine-tune, or the hosted Illustrious service. If the v0.1/v1.0 distinction materially affects a requested capability or interface instruction, preserve the supplied identity or clarify it rather than choosing a newer checkpoint.

## Prompt Language and Detail

- Default to comma-separated Danbooru-style anime tags. Illustrious XL v1.0 also supports natural language and mixed prompts; an explicit prose or other format request takes precedence over this tag default.
- Use common tag vocabulary, usually `lower_snake_case` for canonical Danbooru tags. A protected detail without a faithful tag equivalent may use the minimal literal or relational phrase permitted by [Output Contracts](../output-contracts.md).
- Keep authorized content visible and concrete. Do not add a subject, pose, action, setting, prop, camera treatment, lighting, atmosphere, or style merely because it appears in an ordering slot or example.
- Honor **Very Short**, **Medium**, and **Long** as approximate detail targets of about **75**, **150**, and **300+ tokens**. They are not quotas, limits, or permission to pad a sparse source. An explicit length instruction wins.

## Ordering and Optional Prefixes

- The compatible legacy order is: quality/style guidance, then whichever authorized fields are present among subject count, character traits, pose/action, setting, lighting, and composition.
- The accepted quality starter is `masterpiece, best quality, highres, absurdres`.
- That starter and the ordering are product conventions, not mandatory checkpoint grammar. Omit or replace them when the user requests different normalization, ordering, tags, prose, or no prefix.
- Keep composition tags restrained and only when supplied or permitted. Useful established vocabulary includes `close-up`, `upper_body`, `full_body`, `cowboy_shot`, `looking_at_viewer`, and `dynamic_angle`. Do not stack conflicting framings.
- Do not add Pony score/source/rating tags unless the user explicitly requests a compatible Pony-style workflow.

## Negative Prompts

Return a negative prompt only when requested or when the resolved output explicitly calls for a positive/negative pair. The accepted failure-focused convention is:

`worst quality, low quality, normal quality, lowres, bad anatomy, bad hands, extra digits, fewer digits, text, watermark, signature`

Adapt it to the requested medium and exclusions, add style-specific exclusions only when relevant, and never negate required content. This list is a practical default, not a required checkpoint field.

## Interface Syntax

- Portable output is plain prompt text. Weight syntax, embeddings, LoRA notation, BREAK-like delimiters, and encoder-specific fields belong to the named interface and must not be inferred from the checkpoint.
- Illustrious XL v1.0 documents both natural-language and tag-based prompting. The early v0.1 card documents Danbooru-derived training and composition/quality vocabulary. Neither source makes this profile's exact prefix or ordering mandatory grammar.
- Sampling settings, resolution, CFG, and model add-ons are interface controls, not prompt tokens. Do not append them unless the user asks for workflow settings.
- Character/source tags may be used when known. Do not fabricate an uncertain canonical tag; preserve the identity with an honest descriptive phrase when the output contract permits one.

## Examples

The following legacy example demonstrates presentation shape only. Its subject, wardrobe, action, setting, lighting, and composition are not invention permission for another request:

`masterpiece, best quality, highres, 1girl, solo, long_hair, blue_eyes, hooded_cloak, forest_path, holding_lantern, night, moonlight, fog, looking_at_viewer, cowboy_shot, dramatic_lighting`

## Primary Sources

- [OnomaAIResearch/Illustrious-xl-early-release-v0 model card](https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0) — identifies Illustrious XL v0.1, Danbooru2023 training, composition guidance, supported quality vocabulary, and the lack of a default style for the base.
- [OnomaAIResearch/Illustrious-XL-v1.0 model card](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.0) — identifies the v1.0 boundary and documents natural-language plus Danbooru-style tag prompting.
- [Illustrious technical report](https://arxiv.org/abs/2409.19946) — official technical background linked by the early-release card.
