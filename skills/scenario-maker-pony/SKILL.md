---
name: scenario-maker-pony
description: Use when authoring, adapting, revising, or critiquing prompts for Pony Diffusion V6 XL or PDXL, including prose/tag/Danbooru formats, characters, requested negatives, variants, and ComfyUI wildcards; not other Pony versions or cross-family comparison.
---

# Scenario Maker — Pony

Write prompts and requested analysis for Pony Diffusion V6 XL; never invoke image/video generation. Keep model expression separate from task, scene facts, permissions, and output shape.

## Workflow

1. For every request, read `references/routing.md` and `references/output-contracts.md` first, then `references/scene-composition.md` and `references/constraints-and-revisions.md`. Resolve Operation, Task, Scope, Target, and Output independently; do not ask the user to fill a schema.
2. Read `references/models/pony-v6.md` directly for this family's aliases, exact coverage, and verified interface boundaries before composing. Explicit invocation of `scenario-maker-pony` supplies Pony Diffusion V6 XL as Target only when the user omits a model. It does not supply Task, choose a checkpoint variant or native route, broaden Scope, select an invention mode, or release locks; clarify consequential identity/interface ambiguity under routing's material-ambiguity rule.
3. A different explicitly requested family overrides that implied Target. Do not compose in this specialist's dialect or guess the other family's contract. Explain that the requested profile belongs to the appropriate named specialist or `scenario-maker`; do not read hardcoded sibling paths. Cross-family comparison and multi-target authoring belong to `scenario-maker`, not this standalone profile.
4. Build the internal scene description and apply the shared preservation and invention permissions before wording. Retain supplied facts, source roles, exact lettering, relationships, exclusions, and locally authorized changes. Profile defaults fill only compatible unspecified presentation choices; explicit format, normalization, prefix exclusion, length, and output instructions win. Detail never authorizes invention or padding.
5. Load the conditional references below for the requested artifact. Use the selected profile's verified audiovisual contract when relevant; unspecified audio is not silence, and a family name does not establish audio support. Models and invention modes never supply missing source evidence or consequential reference roles.
6. Compare the finished artifact against the source and permitted changes. Return the requested prompt, analysis, pair, variants, or batch without exposed planning or unsolicited notes, labels, negatives, or alternatives. Analysis stays analysis. Only a bounded exception expressly documented by the selected profile may add an offer; explicit artifact-only restrictions still win. For wildcard files, report actual saved paths and line counts.

## Conditional References and Utilities

- Read `references/prompt-types.md` for prose/tag/Danbooru formats, length guidance, visible-only wording, or requested negatives. Generic length is Very Short unless this profile or the user selects another compatible default.
- Read `references/video-prompts.md` for video tasks, reference/source-video task semantics, or frame-derived editing. The local model profile remains authoritative for its supported routes and expression.
- Read `references/danbooru-tags.md` for Danbooru Version, tag validation, alias lookup, or related-tag expansion. Use `scripts/danbooru_lookup.py` for uncertain tags; never read raw CSVs as prompt context or fabricate lookup evidence.
- Read `references/characters.md` for original characters, profiles, character fragments, or randomized batches. Use `scripts/character_generator.py` only for requested randomization, not ordinary direct authoring.
- Read `references/wildcards.md` before wildcard output. Default to 10 entries per requested file under `./wildcards` unless another count or path is requested. Full prompts use the profile's compatible dialect; fragments do not repeat host boilerplate. Preserve requested file scope and no-write fallback.
