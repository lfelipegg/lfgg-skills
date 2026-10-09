# Scenario Maker — Wan

A standalone prompt-authoring specialist for Wan. Create, expand, adapt, revise, critique, and batch prompts while preserving the facts and constraints you supply. **It writes text; it does not generate images or videos.**

## Coverage and model defaults

Existing version-agnostic Wan/Wan-style text-to-video and image-to-video guidance. No newly asserted version aliases, audio capability, editing controls, or particular interface support.

One cohesive cinematic paragraph containing only supplied or authorized fields; Very Short detail by default. Shot lists require a request, and explicit formats override presentation defaults.

The authoritative [model profile](references/models/wan.md) records aliases, variants, presentation defaults, negative-channel distinctions, interface boundaries, and sources. Explicit format, normalization, prefix exclusion, length, and output requests override compatible presentation preferences, not required content or verified hard input requirements. Do not infer support for other checkpoints, interfaces, or releases.

## What it can do

- Create or expand scene descriptions, character designs, clothing-only descriptions, and isolated assets within the requested scope.
- Adapt model-facing expression without adding scene facts; revise a named detail while preserving unaffected content.
- Use requested ordinary prose, comma-separated visual phrases, or Danbooru-style formats; the selected profile supplies compatible defaults rather than mandatory boilerplate.
- Critique prompt expression, fidelity, or ambiguity without silently rewriting; requested in-family analysis remains analysis.
- Produce requested negatives or positive/negative pairs while respecting the actual workflow's consumed channels.
- Create controlled or exploratory variants, character fragments, and explicitly randomized character batches.
- Save full-prompt or fragment ComfyUI wildcard files with the requested scope.

Task and interface support are separate from model expression. A profile does not by itself establish image editing, video, reference conditioning, audio support, or any particular control. For video or source-media tasks, load the shared task guidance and preserve opening-frame, source-role, and temporal meaning under the profile's verified contract.

## Installation and invocation

From the collection root:

```bash
npx skills@latest add . --skill scenario-maker-wan
```

Keep `SKILL.md`, `references/`, `scripts/`, `docs/`, and `CONTEXT.md` together. The distributed package includes its own shared guidance, local tag data, and optional utilities; no sibling skill, runtime download, or installation-time build is needed. Invocation syntax depends on the hosting application.

```text
Use scenario-maker-wan. Write a Wan image-to-video prompt. Opening: a white cat sits on a blue cushion. Only its tail curls once; lighting and camera stay fixed. Return prompt only.
```

Explicitly invoking **scenario-maker-wan** supplies this family as Target only when no model is named. It does not select Task, checkpoint variant, interface/native route, invention mode, or permitted scene changes. Supply the exact variant and interface when their distinction matters; the assistant clarifies only material ambiguity, not optional detail.

A different explicitly requested family overrides the implied target. This specialist does not substitute its own dialect, guess the unavailable contract, or require sibling resource paths; it identifies the corresponding specialist or **scenario-maker**. Use **scenario-maker** for unnamed/unknown-model generic work, cross-family comparison, or multi-target authoring. Its explicit single-target requests remain supported through its own local catalog.

## Formats, scope, and preservation

- **Normal Version:** ordinary natural-language prose.
- **Tag Version:** comma-separated visual phrases, retaining literal lettering and relationships when needed.
- **Danbooru Version:** canonical tags where possible, plus minimal fidelity-preserving literal or relational phrases when needed. A `canonical-only` restriction forbids that fallback; incompatible required content needs clarification rather than omission.

Length targets are approximate detail guides, not quotas or model limits. Sparse content stays sparse; extra detail never permits invention. Honor hard limits after removing redundancy and optional invention, and preserve exact lettering, subject counts, attribute bindings, relationships, exclusions, and locked details.

**Preserve** rewords without new facts and is the adaptation/revision default. **Balanced** is the creation/expansion default and fills permitted local gaps, not independent subjects, props, actions, or events. **Explore**, **Wild**, and **Unbound** open only their authorized creative dimensions. Wild is concept-led; Unbound delegates complete in-scope scenario development. Neither a model template nor any mode broadens the operation/scope, releases locks, invents missing evidence, or assigns consequential missing reference roles. A supplied image alone does not imply a video task. See [permissions and revisions](references/constraints-and-revisions.md).

Ordinary single-prompt authoring returns only the prompt, with no unsolicited enhancement offer, negatives, notes package, settings, or alternatives.

Ask explicitly for analysis, notes, negative prompts, alternatives, pairs, or multiple outputs. Critique remains analysis. One compatible shared prompt remains one prompt when using the generic/comparison skill; labels do not justify unsolicited packages.

## Optional local tools

For uncertain Danbooru tags, alias resolution, or related-tag expansion, the assistant uses the local lookup utility instead of reading raw CSVs as prompt context. From this selected skill's root:

```bash
python3 scripts/danbooru_lookup.py --json tag grey_hair
python3 scripts/danbooru_lookup.py search "black hair" --limit 5
```

The lookup resolves local data and can create its local SQLite index automatically. Keep `scripts/build_danbooru_index.py` beside it. Randomized character generation is activated only by a randomization request; direct character authoring does not run the generator:

```bash
python3 scripts/character_generator.py --seed 7 --count 1 --format prose
```

See [character guidance](references/characters.md) and [Danbooru guidance](references/danbooru-tags.md) for output and safety rules.

## ComfyUI wildcard files

Each non-empty physical line is one selectable prompt or fragment, without Markdown fences, numbering, or explanations. Full prompts use this profile's compatible dialect unless an explicit format overrides it; fragments do not repeat host-template boilerplate. Default to **10 entries per requested file** under `./wildcards` relative to the assistant's working directory unless you specify another count or path. Preserve named modular roles and requested scope. The assistant reports actual saved paths and counts, or the documented no-write fallback when writing is unavailable. See [wildcards](references/wildcards.md).

## Resource ownership

The specialist owns its entry point, README, UI metadata, and [model profile](references/models/wan.md). The collection synchronization utility generates shared local contracts, optional scripts/data, and context from the generic skill, and copies this authoritative profile into the generic catalog. Edit owned sources in the collection rather than generated common copies. Specialists do not ship the all-model index.

Start with [SKILL.md](SKILL.md), [routing](references/routing.md), [output contracts](references/output-contracts.md), [scene composition](references/scene-composition.md), and [permissions](references/constraints-and-revisions.md).
