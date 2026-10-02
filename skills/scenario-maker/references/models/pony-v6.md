# Pony Diffusion V6 XL

This profile supplies compatible prompt-presentation defaults only after the scene and requested output have been resolved. [Output Contracts](../output-contracts.md) owns response shape and precedence; [Constraints and Revisions](../constraints-and-revisions.md) owns preservation, invention, and scope. The profile never authorizes absent scene facts or an automatic prompt package.

## Identity and Aliases

This profile is specifically for **Pony Diffusion V6 XL**, not every Pony-branded checkpoint. Recognized aliases are `pony`, `pony diffusion`, `pony diffusion v6`, `pony diffusion v6 xl`, and `pdxl`; within this skill those legacy generic aliases select this V6 XL profile.

Keep an explicit version exact. Do not silently treat a named earlier or newer Pony release, a community merge, an anime derivative, or another checkpoint containing “Pony” as V6 XL. When that distinction materially affects the requested adaptation or interface, clarify the identity instead of transferring V6 behavior.

## Prompt Language and Detail

- Default to comma-separated tags and short visual phrases using Pony V6's score/source/rating dialect.
- The official V6 card also supports natural language and mixed caption/tag prompts. Explicit prose, normalization, or another requested format overrides the tag presentation default while preserving the scene.
- Do not add generic SD quality boilerplate such as `masterpiece` or `best quality` unless the user explicitly requests it.
- Keep authorized content visible and concrete. An ordering slot or example is not permission to add a subject, species, action, setting, camera treatment, lighting, or style.
- Honor **Very Short**, **Medium**, and **Long** as approximate detail targets of about **75**, **150**, and **300+ tokens**. They are not quotas, limits, or permission to pad a sparse source. An explicit length instruction wins.

## Ordering and Optional Prefixes

- The compatible legacy order is: applicable score tags, source/rating tags, then the authorized subject and visual content.
- The accepted safe prefix is `score_9, score_8_up, score_7_up, source_anime, rating_safe`.
- Choose one source tag matching supplied content: `source_anime`, `source_cartoon`, `source_pony`, `source_furry`, or another source tag the user provides. Do not change the depicted content merely to fit a source label.
- Use `rating_safe` by default unless the user requests another allowed rating. Keep any explicit rating unchanged.
- The official card's opinionated full V6 score template includes `score_9` through `score_4_up`; this profile intentionally preserves the accepted shorter product prefix. Both are prompting conventions rather than mandatory grammar. Explicit prefix inclusion, exclusion, or ordering instructions take precedence.

## Negative Prompts

Pony V6 is documented as generally not needing a negative prompt. Return one only when requested or when the resolved output explicitly calls for a pair. Preserve the accepted requested-negative convention:

`score_6, score_5, score_4, low quality, bad anatomy, bad hands, extra fingers, text, watermark, signature`

Do not put `masterpiece`, `best quality`, or the selected source/rating tags in the negative prompt. Adapt the list to relevant failures and exclusions, and never negate required content.

## Interface Syntax

- Portable output is plain prompt text. Weight syntax, embeddings, LoRA notation, BREAK-like delimiters, and encoder-specific fields depend on the named interface and must not be inferred from the checkpoint.
- The model card instructs users to load Pony Diffusion V6 XL with **CLIP skip 2** (shown as `-2` in some software). This is an interface setting, not text to append to the prompt; control names and sign conventions vary by application.
- Score, source, and rating forms are checkpoint vocabulary, not UI field names. Keep them in prompt text when selected.
- Sampler, steps, resolution, CFG, and inpainting are workflow controls. Do not add them to prompt-only output.

## Examples

The following legacy example demonstrates presentation shape only. Its character traits, clothing, action, setting, camera relation, lighting, and time are not invention permission for another request:

`score_9, score_8_up, score_7_up, source_anime, rating_safe, 1girl, silver hair, red eyes, long coat, standing on a rainy rooftop, neon city, looking at viewer, dramatic rim light, night, detailed background`

## Primary Sources

- [Pony Diffusion V6 XL official Civitai model card](https://civitai.com/models/257749/pony-diffusion-v6-xl) — identifies the V6 boundary, full score template, source/rating vocabulary, natural-language support, no-negative guidance, and CLIP-skip requirement.
- [Pony_Diffusion_V6_XL Hugging Face card](https://huggingface.co/LyliaEngine/Pony_Diffusion_V6_XL) — a published mirror that attributes the source to the official Civitai model and repeats the V6 usage guidance.
