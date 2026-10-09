---
name: scenario-maker
description: Use for creating, adapting, revising, critiquing, or batching AI image/video prompts when no model is selected or the model is unknown, and for cross-model comparisons or multi-target authoring, including characters, formats, tags, negatives, variants, and ComfyUI wildcards.
---

# Scenario Maker

## Overview

Write prompts, not images or videos. This is the generic/comparison entry point for unnamed or unknown targets and work across model families. Explicitly invoking `scenario-maker` with one supported target also works through its local catalog; invocation alone never selects a model.

## Reference Selection

- Read `references/routing.md` and `references/output-contracts.md` first for every request: infer the request's independent fields and apply the requested output shape before model defaults.
- Read `references/scene-composition.md` and `references/constraints-and-revisions.md` after routing for internal scene planning, operation/mode permissions, preservation, and scope boundaries.
- For a named supported target or alias, read `references/model-prompts.md` and its selected local profile before composing. Read every relevant local profile for cross-target analysis or authoring. Finish each selected profile, continuing any omitted or truncated sections before composing. With no named target, read no model catalog or profile; use generic task guidance.
- Read `references/prompt-types.md` for prose/tag syntax, length targets, negative prompts, and visible-only rules.
- Read `references/danbooru-tags.md` for Danbooru Version, Danbooru tags, tag validation, alias lookup, or related-tag expansion.
- Read `references/video-prompts.md` for video tasks and frame-derived still editing; the selected profile owns any verified route, reference, audiovisual, or serialization contract.
- Read `references/wildcards.md` before creating ComfyUI wildcard `.txt` files.
- Read `references/characters.md` when creating original characters, character profiles, character prompt fragments, or randomized character batches.

## Workflow

1. Infer Operation, Task, Scope, Target, and Output independently using `references/routing.md`; do not ask the user to fill out a schema.
2. Build a lightweight internal scene description using `references/scene-composition.md`: supplied content and relationships, exact lettering, locked details, exclusions, and permitted changes. Keep it internal unless requested.
3. Apply `references/constraints-and-revisions.md` before wording: preserve supplied facts and locks; resolve mode, scope, and local permissions. Modes and model families never broaden the operation, task, interface, or scope. Use `references/prompt-types.md` and the selected profile for permitted visual or verified audiovisual expression.
4. Apply explicit format and length before compatible profile defaults. Resolve only genuine incompatibilities under `references/output-contracts.md`; profile preferences do not override required content.
5. For Danbooru requests, validate uncertain tags, aliases, and related tags with `scripts/danbooru_lookup.py`, never the raw CSVs. Use `scripts/character_generator.py` only for authorized randomized character requests.
6. Perform the final fidelity check from `references/scene-composition.md`. Return the requested prompt, analysis, pair, variants, or batch without internal planning or unsolicited additions. Only a selected profile's documented bounded output exception may apply; explicit artifact-only restrictions still win.
7. For wildcard batches, follow `references/wildcards.md`: write the requested files automatically and report saved paths and line counts.

## Default Choices

- Output format: Normal Version when neither an explicit format nor a named model's compatible default selects another dialect.
- Length: Very Short unless the user specifies a length or hard limit or the selected profile supplies another default. Detail never authorizes invention or padding.
- Task: resolve independently under `references/routing.md`; neither an image nor a selected model establishes a video task or native route.
- Wildcard count: if a wildcard request omits a count, create 10 lines per requested file.

## Output Rules

Follow `references/output-contracts.md` for requested shape, multiplicity, explicit-format precedence, negatives, and fidelity-preserving tag/literal syntax. A comparison remains analysis unless prompts are also requested; a compatible shared prompt remains one prompt, not one per target. Model profiles supply expression, not extra content or output packages.

## When To Ask

Use the material-ambiguity and conflict rules in `references/routing.md`, `references/constraints-and-revisions.md`, and `references/output-contracts.md`. Ask concisely only for an unresolved consequential task/model/interface, required unavailable media without a sufficient description, ambiguous source roles or revisions, incompatible instructions, an impossible hard constraint, or an unclear writable destination outside the workspace.

Missing optional creative direction is not missing evidence: once image-to-video is established, Unbound plus an available sole opening image needs no written scene/action brief. Do not infer video or reference roles from an image, family invocation, or mode alone, and do not interrupt merely for uncertain rendering quality.
