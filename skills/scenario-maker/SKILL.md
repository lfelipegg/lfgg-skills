---
name: scenario-maker
description: Use when creating, refining, critiquing, or batching prompts for AI image and video generation, including character profiles, text-to-image, image editing, text-to-video, image-to-video, ComfyUI wildcards, prompt variants, tag prompts, Danbooru tags, negative prompts, Wan video prompts, MiniMax H3 reference/video/frame-derived editing prompts, and model-aware prompts for SDXL, Krea 2, Illustrious, NoobAI, or Pony.
---

# Scenario Maker

## Overview

Write visual prompts for AI image and video models. Turn rough ideas into ready prompts, requested analysis, variants, tags, negative prompts, and ComfyUI wildcard files. Prompt writing never invokes image/video generation.

## Reference Selection

- Read `references/routing.md` and `references/output-contracts.md` first for every request: infer the request's independent fields and apply the requested output shape before model defaults.
- Read `references/scene-composition.md` and `references/constraints-and-revisions.md` after routing for internal scene planning, operation/mode permissions, preservation, and scope boundaries.
- Read `references/model-prompts.md` and the selected file under `references/models/` when the request names SDXL, local Krea 2 RAW/Turbo, Illustrious/ILXL, NoobAI, Pony/Pony Diffusion, MiniMax H3, or another alias listed in the index. Load every named profile for a comparison.
- Read `references/prompt-types.md` for prose/tag syntax, length targets, negative prompts, and visible-only rules.
- Read `references/danbooru-tags.md` for Danbooru Version, Danbooru tags, tag validation, alias lookup, or related-tag expansion.
- Read `references/video-prompts.md` for text-to-video, image-to-video, reference-video generation, source-video editing, and Wan video prompts. For MiniMax H3, also read `references/models/minimax-h3.md`, including for frame-derived still editing; generic video guidance does not replace its route-specific contract.
- Read `references/wildcards.md` before creating ComfyUI wildcard `.txt` files.
- Read `references/characters.md` when creating original characters, character profiles, character prompt fragments, or randomized character batches.

## Workflow

1. Infer Operation, Task, Scope, Target, and Output independently using `references/routing.md`; do not ask the user to fill out a schema.
2. Build a lightweight internal scene description using `references/scene-composition.md`: supplied content and relationships, exact lettering, locked details, exclusions, and permitted changes. Keep it internal unless requested.
3. Apply `references/constraints-and-revisions.md` before model-facing wording. Preserve supplied facts and necessary implications; create/expand default to Balanced, adapt/revise to Preserve. Infer Wild from explicit selection or unmistakable concept-led delegation; infer Unbound from explicit selection or unmistakable whole-scenario delegation such as “invent the entire scenario from this seed” or “use this opening image and decide the whole video yourself.” Ordinary vagueness, “improve this,” and “go wild” do not escalate to Unbound; a specifically named lower mode stays selected. Apply invention only inside the resolved operation, scope, and open dimensions. Wild or Unbound audiovisual delegation applies only to supported audiovisual tasks. Modes cannot broaden the operation or scope. Apply `references/output-contracts.md` and resolve genuine incompatibilities before writing.
4. Keep visual prompts observable: describe appearance, environment, lighting, motion, camera behavior, weather, composition, and visible atmosphere where permitted. Avoid hidden thoughts, backstory, smells, lore, or internal emotions unless explicitly requested. For audiovisual H3 tasks, retain supplied/requested sound intent and any valid Wild or Unbound audiovisual choices under its profile; do not pad ordinary audio templates.
5. If a supported target model is explicitly named, resolve it through `references/model-prompts.md` and read its profile for compatible, unspecified defaults. Explicit formatting overrides profile presentation preferences, not required scene content or verified hard input requirements.
6. For Danbooru Version requests, use `scripts/danbooru_lookup.py` to validate uncertain tags, resolve aliases, and find related tags instead of reading the raw CSV files.
7. For randomized character requests, use `scripts/character_generator.py` and follow `references/characters.md`.
8. Compare the finished artifact against the source and locally authorized changes. Return the requested artifact: a finished prompt for single prompt writing, analysis for critique/comparison, or the requested pair, variants, or batch. Do not expose internal planning or add unsolicited notes, labels, negatives, or alternatives. For a completed H3 prompt, append the brief enhancement offer from `references/output-contracts.md` unless the user explicitly requires prompt-only or another artifact-only format. An inferred single-prompt output is not that explicit restriction. Do not offer after clarification or analysis.
9. When wildcard batches are requested, create newline-separated `.txt` files automatically under `./wildcards` unless the user provides another path.

## Default Choices

- Output format: Normal Version when neither an explicit format nor a named model's compatible default selects another dialect.
- Length: Very Short unless the selected profile supplies another default (local Krea 2 and MiniMax H3 use Medium) or the user specifies a length or hard limit. Detail never authorizes invention or padding.
- Task: infer still image, image editing, text-to-video, image-to-video, reference-video generation, or source-video editing independently of the operation, scope, target, and output. An existing image does not by itself imply video. H3 frame-derived still editing remains an image-editing task, not first-frame animation.
- Model coverage: use generic image/video guidance unless a supported target is named. Use Wan rules for Wan video prompts. Use `references/model-prompts.md` and its selected profile for SDXL, local Krea 2, Illustrious, NoobAI, Pony, or MiniMax H3. Do not guess a model when none is named.
- Wildcard count: if a wildcard request omits a count, create 10 lines per requested file.

## Output Rules

- Follow `references/output-contracts.md` for output shape, multiplicity, and precedence.
- Respect user-specified token limits and formats.
- For Tag Version, use comma-separated visual phrases; exact lettering and relationships may remain literal.
- For Danbooru Version, use canonical tags where possible and minimal fidelity-preserving literal/relational phrases where necessary. Canonical-only constraints forbid that fallback; clarify if no faithful expression exists.
- For video prompts, express subject motion, environmental motion, camera motion, atmosphere, and stylization only where supplied or permitted; these fields are not an invention checklist.
- For Wan prompt writing, use one cohesive cinematic paragraph unless explicitly requested otherwise.
- For selected native MiniMax H3 routes, use the profile's reference sections or first-frame anchor and sections as compatible defaults. Do not apply Wan's one-paragraph default, confuse a conditioned opening image with an edited first output frame, or imply generation/extraction.
- A model's tag/prose dialect is a default, not permission to override the requested output format or add model notes.
- For wildcard files with a named supported model, use its compatible dialect defaults unless the user specifies another format.
- For wildcard files, report saved paths and line counts after writing them.

## When To Ask

Unbound supplies missing optional creative direction, not missing evidence. An available sole opening image suffices without a written scene/action brief once the request or conversation establishes image-to-video; do not ask what should happen. Neither an image nor Unbound alone establishes a video task. Retain normal routing and clarify only material task ambiguity, unavailable required media without a description, or materially ambiguous reference roles.

Ask a concise question only when proceeding would likely produce the wrong artifact, such as:

- The user says "continue this image" but no image or image description is available.
- The user requests saved wildcard files outside the current workspace and no writable path is clear.
- The user asks for a specific unsupported model format whose constraints are unknown and materially affect the prompt.
- Required content cannot fit the requested hard constraints after removing redundancy and optional invention.
- Producing the artifact requires resolving ambiguity in supplied source content, the requested revision is genuinely unclear, or simultaneous content instructions conflict. Wild or Unbound may choose a plausible interpretation of an ambiguous new-creation seed; that exception does not resolve source ambiguity or missing required inputs and reference roles.
- The requested artifact conflicts with a verified requirement of the exact model/task/interface. A preferred dialect or uncertain rendering quality alone does not justify interrupting.
