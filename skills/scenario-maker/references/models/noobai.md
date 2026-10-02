# NoobAI XL

This profile supplies compatible prompt-presentation defaults only after the scene and requested output have been resolved. [Output Contracts](../output-contracts.md) owns response shape and precedence; [Constraints and Revisions](../constraints-and-revisions.md) owns preservation, invention, and scope. The profile never authorizes absent scene facts or an automatic prompt package.

## Identity and Aliases

This profile preserves shared prompt behavior for the official **NoobAI XL 1.1** epsilon-prediction checkpoint and **NoobAI XL V-Pred 1.0** checkpoint. Recognized aliases are `noobai`, `noob ai`, `noobai xl`, `noobai-xl`, and `nai noob`; `noob v-pred` specifically names the V-Pred branch.

An unqualified alias does not silently select a prediction type or a newer checkpoint. Keep explicit `1.1`, `V-Pred 1.0`, and other supplied versions exact. Do not transfer this profile's interface claims to a differently versioned NoobAI release, derivative, merge, or similarly named model when the distinction matters.

## Prompt Language and Detail

- Default to comma-separated tags and short visual phrases in NoobAI's normalized tag style. Danbooru and e621 vocabulary is preferred when known, but the prompt spelling is normalized for NoobAI rather than copied verbatim from the boards.
- Replace underscores between words with spaces: use `long hair`, not `long_hair`.
- Preserve the legacy default of escaping parentheses in character/source tags: `hakurei reimu \(touhou\)`. This is parser-facing presentation, not checkpoint grammar; a verified named interface may require different escaping.
- Keep authorized content visible and concrete. Do not add lore, relationships, hidden personality, or any visual field merely to complete an ordering.
- Honor **Very Short**, **Medium**, and **Long** as approximate detail targets of about **75**, **150**, and **300+ tokens**. They are not quotas, limits, or permission to pad a sparse source. An explicit length instruction wins.

## Ordering and Optional Prefixes

- Preserve the compatible legacy order: quality/model-preference tags, then whichever authorized fields are present among subject, identity/source, traits, action, setting, lighting, and composition.
- The accepted starter is `masterpiece, best quality, very awa, newest`.
- `very awa` is optional: include it when the user wants stronger anime/aesthetic polish; omit it for strict neutral tag conversion.
- The official cards and manual document other useful prefix elements, including `absurdres`, `highres`, and a safety tag, and the manual also describes subject-first ordering with quality tags optionally prefixed. The exact starter and ordering above are preserved product conventions, not mandatory grammar. Explicit prefix, format, normalization, and ordering instructions take precedence.
- Do not add Pony score/source/rating tags unless the user explicitly asks for a compatible Pony-style workflow.

## Negative Prompts

Return a negative prompt only when requested or when the resolved output explicitly calls for a positive/negative pair. Preserve the accepted convention, normalized with spaces:

`worst quality, low quality, lowres, bad anatomy, bad hands, extra digits, fewer digits, text, watermark, signature, jpeg artifacts`

Adapt it to relevant failures and user exclusions, and never negate requested content. The model cards publish broader sample negatives, but those are not an automatic package or a universal blacklist.

## Interface Syntax

- Portable output is plain prompt text. Weighting, embeddings, LoRA notation, encoder fields, and node layout depend on the named interface and must not be inferred from the checkpoint.
- Preserve escaped parentheses for common WebUI-style parsers because unescaped parentheses may be consumed as weighting syntax. A raw API or another parser may use different escaping; interface-specific syntax overrides this portable convention when verified.
- NoobAI XL 1.1 is the epsilon-prediction branch and uses ordinary supported SDXL loading. NoobAI XL V-Pred 1.0 is a distinct prediction type: its official Diffusers example configures `prediction_type: "v_prediction"` and `rescale_betas_zero_snr: true`, and its card documents compatible WebUI/ComfyUI paths. Those are workflow requirements, not prompt tokens.
- Do not infer V-Pred settings from the generic `noobai` alias. Do not claim that a UI supports the V-Pred checkpoint without evidence for that interface.
- If a requested character/source tag is uncertain, use an honest descriptive identity phrase when the output contract permits it rather than fabricating a canonical tag.

## Examples

The following legacy example demonstrates presentation shape only. Its subject, clothing, setting, lighting, atmosphere, gaze, and framing are not invention permission for another request:

`masterpiece, best quality, very awa, newest, 1girl, solo, white hair, golden eyes, black sailor uniform, standing in a ruined classroom, broken windows, sunset light, dust particles, looking at viewer, upper body`

Normalization and literal-parenthesis shape:

`hakurei reimu \(touhou\), touhou, long hair`

This second line illustrates syntax only; it does not authorize adding that character, source, or trait.

## Primary Sources

- [Laxhar/noobai-XL-1.1 model card](https://huggingface.co/Laxhar/noobai-XL-1.1) — identifies the epsilon-prediction 1.1 boundary and documents native tag captions, prefix elements, quality/date tags, and recommended workflow settings.
- [Laxhar/noobai-XL-Vpred-1.0 model card](https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0) — identifies the V-Pred 1.0 boundary and documents prediction-specific loading, prompt/negative examples, prefix elements, and ordering.
- [NoobAI-XL User Manual (2024-11-28)](https://files.catbox.moe/vciz3c.pdf) — documents tag normalization, escaped parentheses, logical ordering, quality/aesthetic/date vocabulary, and epsilon-versus-V-Pred interface distinctions. Its version-specific parameter tables predate the final V-Pred 1.0 card, so the exact checkpoint card governs where they differ.
