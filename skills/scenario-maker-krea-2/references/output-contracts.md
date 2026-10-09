# Output Contracts

The requested operation and output shape govern the response. Model guidance supplies compatible defaults only where the user left a choice unspecified.

## Prompt Writing and Analysis

For one prompt-writing request, return the finished prompt only. Do not add headings, wrappers, notes, explanations, negative prompts, alternatives, or model metadata unless requested. The prompt itself may contain a selected profile's section headings or reference syntax as compatible presentation defaults; these are not automatically hard interface requirements.

A critique remains analysis and does not silently become a rewrite. A comparison remains analysis unless prompts are also requested. An explicit batch or variant request retains its requested multiplicity; do not collapse it to one preferred result.

For prompt writing with multiple named targets, produce one prompt per target with only the minimal labels needed to distinguish them. A request for one shared prompt produces one prompt when the targets' requirements are compatible. If they are not compatible, ask which constraint may change rather than silently splitting the prompt. A comparison of those targets still returns analysis, not prompts.

Only a selected profile may authorize its documented, bounded exception to the prompt-only default, for the target and tasks it covers. This never grants generic permission for notes, packages, or automatic additional artifacts. Explicit “prompt only,” equivalent restrictions, machine-readable-only output, and artifact-only file content still suppress surrounding additions; follow the selected profile's exact conditions.

## Precedence

Operation, task, scope, and protected scene details determine what the artifact must communicate. Explicit output instructions determine its shape. Compatible model defaults fill only unspecified presentation choices.

An explicit request for prose, tag style, normalization, count, labels, or prefix exclusion overrides a model's presentation default. It does not override:

- required scene content or locked details;
- a verified hard requirement of the exact model, task, or interface;
- the requested operation, such as critique or comparison;
- the boundary that prompt writing does not perform generation.

Legacy or generic package defaults must not add unrequested negatives, notes, variants, labels, or wrappers. Consult [Prompt Types](prompt-types.md) for compatible syntax and generic prompt conventions, and the applicable model or task reference for compatible target-specific defaults.

## Genuine Incompatibility

A conflict is genuine only when the requested artifact cannot preserve required content within its hard constraints, or when the intended use contradicts a verified requirement of the exact model, task, or interface.

A preferred dialect, uncertain rendering quality, or difficulty rendering exact text or relationships is not by itself a conflict. First remove redundancy and optional invention. If the conflict remains, state it concisely and ask which constraint may change. Never silently omit required content, exceed a hard limit, substitute an output format, split a shared prompt, or claim unsupported capability.

## Tag and Danbooru Shapes

Generic Tag Version may use comma-separated visual phrases, including exact quoted lettering and explicit relationships. Preserve required text exactly rather than normalizing its lettering.

Ordinary Danbooru Version uses canonical tags where possible, including combinations of tags that faithfully express one required concept. Resolve ordinary descriptive phrases to those tags before considering a fallback; use targeted lookup for uncertain conversions. In a single-subject prompt, a grouped set of canonical attributes can express an unambiguous subject association without repeating it as a prose noun phrase.

Use a literal qualifier or relational phrase only for required meaning that the tag combination cannot express. Keep only the missing meaning. If canonical tags already identify the subject, an attribute fallback must omit the repeated subject noun; use a standalone qualifier when it expresses the full missing attribute. Do not use the fallback for optional quality boilerplate, convenience, or avoiding a known tag conversion. Explicit lettering and relationships retain the full wording needed for fidelity.

Keep a fallback honest: an ordinary literal word is not a verified canonical tag. Do not manufacture lower_snake_case labels, claim an unconfirmed lookup result, or change a required attribute merely to obtain a canonical spelling. Preserve exact lettering and explicit relationships intact; shortening or splitting them is not an improvement if it changes meaning.

An explicit `canonical-only`, `tags-only` in a canonical Danbooru context, or `no non-tag text` constraint forbids that fallback. If required content cannot be expressed faithfully with canonical tags, clarify instead of approximating or dropping it.

## Negative Channels

Return a positive/negative pair only when requested or when the resolved output explicitly calls for both. If a requested negative prompt appears intended for an exact workflow verified not to consume a negative channel, explain the mismatch and ask how to proceed. Return standalone negative text directly when that intent is already clear. Never silently fold negative text into the positive prompt.

## Files

When file output is requested, write only the requested artifact scope and report paths and counts truthfully after writing. Do not claim unwritten files, add unrequested companion files, or redesign wildcard structure as part of routing. Follow the dedicated wildcard guidance for wildcard contents and defaults.

## Boundaries

- `Tags only, no negative prompt` → the tag prompt only.
- Danbooru Version requiring `Open late!` → preserve `Open late!` in a minimal quoted literal phrase; do not lowercase or snake-case the lettering.
- Canonical-only tags with an unexpressible required relationship → ask which constraint may change.
- A model known to render text unreliably → preserve the requested text without interrupting solely for that uncertainty.
- `Write this for two named targets` → two minimally labeled prompts, not two prompt packages.
