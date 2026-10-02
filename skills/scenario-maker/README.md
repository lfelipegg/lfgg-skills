# Scenario Maker

Scenario Maker is an agent skill for writing, refining, critiquing, and batching prompts for AI image and video workflows. It turns rough ideas or existing prompts into model-aware descriptions while preserving the details you want to keep.

**It writes prompts; it does not generate images or videos.** Use the resulting text in your image or video generation tool.

## What it can do

- Create or expand scene descriptions, character designs, clothing descriptions, and isolated assets.
- Adapt prompts for SDXL, local Krea 2 RAW/Turbo, Illustrious, NoobAI, and Pony Diffusion V6 XL.
- Write text-to-video and image-to-video prompts, including Wan prompts.
- Write native local MiniMax H3 full-reference generation, source-video editing, first-frame video, and frame-derived still-edit prompts.
- Convert between natural-language prose, general tag prompts, and Danbooru-style tags.
- Revise specific details without changing the rest of a prompt.
- Critique prompts or compare model-specific approaches without silently rewriting them.
- Produce requested negative prompts, controlled variants, exploratory variants, and randomized character batches.
- Save ComfyUI wildcard batches as newline-separated `.txt` files.

## Supported models

The skill provides model-specific **prompt-writing guidance**, not model execution. Name the target in your request to select its conventions.

| Model | Covered versions or variants | Default prompt style |
| --- | --- | --- |
| [SDXL](references/models/sdxl.md) | Stable Diffusion XL 1.0 Base | Compact natural-language phrases. |
| [Local Krea 2](references/models/krea-2.md) | Open RAW and Turbo checkpoints | A cohesive natural-language paragraph; Medium detail by default. |
| [Illustrious XL](references/models/illustrious.md) | Official v0.1 and v1.0 bases; aliases include `Illustrious` and `ILXL` | Danbooru-style tags. |
| [NoobAI XL](references/models/noobai.md) | 1.1 epsilon-prediction and V-Pred 1.0 | Tags and short visual phrases, with spaces instead of underscores. |
| [Pony Diffusion](references/models/pony-v6.md) | V6 XL; aliases include `Pony` and `PDXL` | Tags and short visual phrases using applicable score/source/rating conventions. |
| [Wan](references/video-prompts.md#wan-video-format) | Wan-style text-to-video and image-to-video guidance; no version-specific profile | One cohesive cinematic paragraph describing authorized motion and scene details. |
| [MiniMax H3 Ref2VA](references/models/minimax-h3.md) | Native local H3-Base-Ref2VA through `MiniMaxH3ReferenceToVideo` | Six-section reference generation/editing prompt; English and Medium detail by default. |
| [MiniMax H3 FL2VA](references/models/minimax-h3.md#fl2va-first-frame-video) | Native local H3-Base-FL2VA through `MiniMaxH3ImageToVideo`, one opening image | Opening-frame anchor followed by three sections; English and Medium detail by default. |

Explicit format requests override these presentation defaults. For example, you can ask for Illustrious prose or an SDXL tag prompt.

**Coverage boundaries:** local Krea 2 guidance does not cover hosted Medium, Large, or Medium Turbo. Model-family names do not automatically extend support to newer releases, fine-tunes, or merges. Specify the exact checkpoint and interface when their differences matter.

For other models, the skill can write generic image or video prompts, but it does not claim model-specific syntax or capabilities without supporting guidance. With no model named, it uses generic task guidance rather than guessing a target.

### MiniMax H3 task boundaries

- **Full-reference generation:** combine image, video, and audio references with explicit roles; an appearance source does not donate its background or soundtrack.
- **Source-video editing:** identify the video being edited, the requested changes, and the content to preserve.
- **First-frame video:** the supplied opening image anchors time zero. Describe authorized motion or later transformations; changing that same opening requires resolving the route or timing.
- **Frame-derived still editing:** describe the complete edit in the first generated output frame. Your downstream workflow generates reference-guided video and extracts that frame; Scenario Maker does neither.

Provide inspectable media or sufficiently clear descriptions/transcripts for prompt authoring. Actual generation still needs the correctly connected media. These routes do not cover hosted H3/H3-Max, older Hailuo, or every adjacent native workflow. The ordinary selected native templates consume positive conditioning only, not a separate negative-text field. Reference retention expresses intent, not a fidelity guarantee.

Audio left unspecified remains `Unspecified`, not silence. Explicit formats override section defaults while preserving source roles and temporal meaning. See the [H3 profile](references/models/minimax-h3.md) for examples of all four tasks and native input boundaries.

## Getting started

This skill is part of [LFGG Skills](../../README.md). From the collection root:

```bash
npx skills@latest add . --skill scenario-maker
```

1. Make this directory available to an assistant that supports agent skills, using that application's skill installation or discovery mechanism. Keep `SKILL.md`, `references/`, `scripts/`, and `docs/` together so the skill can access its supporting instructions and lookup data.
2. Ask the assistant to use **scenario-maker**, then describe what you want. The entry point is [SKILL.md](SKILL.md); invocation syntax depends on the application hosting the skill.
3. Copy the returned prompt into your generation workflow, or use the saved wildcard files in your wildcard setup.

Start with an ordinary-language request:

```text
Use scenario-maker to write an SDXL prompt for an abandoned greenhouse
filled with blue fog. Use natural-language prose, under 60 words.
```

You do not need to fill out a schema. When useful, include:

- **Task:** still image, image editing, text-to-video, image-to-video, reference-video generation, or source-video editing.
- **Scope:** full scene, character design, clothing, or isolated asset.
- **Target:** the exact model or checkpoint, if known.
- **Output:** prose, tags, positive/negative pair, variants, critique, or files.
- **Constraints:** required details, exclusions, exact lettering, length, and what may change.

For image-to-video requests, provide the starting image or describe it. Naming a model selects prompt-writing guidance; it does not establish that a particular interface supports a task or control.

## Formats and defaults

| Format | What you get |
| --- | --- |
| **Normal Version** | Natural-language prose. |
| **Tag Version** | Comma-separated visual phrases. |
| **Danbooru Version** | Canonical tags where possible, with minimal literal or relational phrases when needed to preserve required meaning. |

For strictly canonical Danbooru output, say **canonical-only**. If canonical tags cannot faithfully express a required detail, the assistant asks how to resolve the conflict rather than dropping it.

Your explicit format and length take precedence over model presentation defaults. Without a named model or explicit format, the skill uses Normal Version. The default length is Very Short unless a selected profile supplies another default; local Krea 2 and MiniMax H3 default to Medium.

A single prompt-writing request returns the prompt only. For H3, the assistant also briefly offers optional in-chat enhancement after the prompt when your requested format permits it; say **“prompt only”** to suppress the offer. Enhancement is never automatic. Ask explicitly for explanations, negative prompts, alternatives, or a positive/negative pair. Critique and comparison requests return analysis rather than an unsolicited rewrite.

## Controlling changes

Supplied facts and **locked details** remain protected: subject counts, colors, relationships, exclusions, and exact visible text should survive adaptation and revision unless you authorize a change.

| Mode | Allowed changes |
| --- | --- |
| **Preserve** | Reword or reorganize without introducing new visual facts. Default for adaptation and revision. |
| **Balanced** | Fill unspecified local details without adding independent subjects, props, actions, or events. Default for creation and expansion. |
| **Explore** | Add compatible ideas within the requested scope; additional subjects require an open roster or explicit permission. |
| **Wild** | Develop a bold, coherent concept by making decisive choices only in unspecified, permitted dimensions while preserving every supplied fact and constraint. |
| **Unbound** | Autonomously develop a complete in-scope scenario from a minimal seed or supplied opening image, choosing the missing creative direction while retaining every supplied fact and constraint. |

Modes do not broaden the request. A clothing description does not become a full scene, and “change only the jacket color” still permits only that change, even in Explore, Wild, or Unbound mode. Wild activates when named explicitly or clearly delegated with language such as “go wild with the concept”; ordinary vagueness, “improve this,” wild animals, or the mere desire for a creative result does not activate it. Wild is concept-led rather than merely additive: its details reinforce one organizing idea instead of accumulating more objects or adjectives.

Unbound activates when named or when you unmistakably delegate the whole scenario, such as “invent the entire scenario from this seed.” It chooses the premise and missing creative direction for a finished prompt, not a longer response or extra alternatives. “Go wild” alone does not select Unbound, and a specifically named lower mode stays selected. Supplied images remain evidence: invent around the opening, not automatic transformations of established identities or attributes. An image alone does not imply video.

## Example requests

### Develop a minimal seed in Unbound

```text
Unbound: create one still-image prompt from the seed “a doorway”. Return prompt only.
```

### Delegate an image-to-video scenario in Unbound

```text
[attach an opening image] Unbound: write an image-to-video prompt from this image. Return prompt only.
```

The second request needs no written scene/action brief: the available image supplies the opening, and Unbound develops the subsequent scenario while preserving supplied facts and constraints.

### Develop a vague still seed in Wild

```text
Wild mode: create one still-image prompt for a night market.
Choose a bold, coherent direction. Return prompt only.
```

### Keep Wild clothing-only

```text
Create one clothing-only design in Wild mode: a moss-green coat.
No wearer, pose, setting, camera, lighting, or independent props.
Return prompt only.
```

### Animate an H3 opening image in Wild

```text
Animate this described opening image using native local H3 FL2VA; go wild.
Picture 1 shows one adult woman in a red coat beside a stall whose sign reads
exactly "Open late!". She is the only person; no animals. Preserve the actual
opening, then develop the future animation. Return prompt only.
```

These requests ask Scenario Maker to write prompts; they do not run image or video generation.

### Adapt an existing prompt

```text
Use scenario-maker to adapt this for Illustrious in Danbooru Version.
Preserve both subjects, their clothing colors, and the exact sign text
"Open late!". Do not add props or a background:
[paste the source prompt]
```

### Make a targeted revision

```text
Revise this prompt: change only the jacket from yellow to red.
Keep the hair, pose, setting, and all other details unchanged:
[paste the source prompt]
```

### Write a video prompt

```text
Write a Wan image-to-video prompt from this starting frame:
a small sailboat on calm water beneath an overcast sky.
Let the boat drift slowly left as the camera stays fixed.
Preserve the lighting and add no other boats.
```

### Edit a still through H3 reference generation

```text
Write a prompt for native local H3 Ref2VA frame-derived still editing.
Connected Picture 1 is the edit base: a yellow mug on a wooden table,
with "MORNING" printed on the mug. Change only the mug to cobalt blue,
already complete in the first generated output frame.
Preserve the table, composition, lighting, and exact lettering.
Leave later motion and audio unspecified. Return prompt only.
```

### Create controlled variants

```text
Create four controlled variants of this SDXL prompt, changing only
the lighting. Keep the subject, clothing, pose, and setting fixed:
[paste the source prompt]
```

### Request analysis instead of a rewrite

```text
Critique this prompt for unclear subject relationships and conflicting
visual instructions. Do not rewrite it:
[paste the prompt]
```

### Save a wildcard batch

```text
Create 20 full-prompt SDXL wildcard entries for abandoned botanical
interiors. Use Balanced mode and natural-language prose.
Save them to ./wildcards/botanical-interiors.txt.
```

## ComfyUI wildcard files

Each non-empty line is one selectable prompt or fragment. Files contain no Markdown fences, numbering, or explanatory text.

- **Full-prompt wildcard entries** are complete prompts, including applicable model-specific prefixes.
- **Fragment wildcard entries** are partial descriptions intended for insertion into a larger prompt, without repeated model boilerplate.
- The default destination is `./wildcards` relative to the assistant's current working directory, unless you provide another path.
- If no count is specified, the skill creates **10 entries per requested file**.
- After saving, the assistant reports the file paths and line counts.

To request modular files, name the roles explicitly, such as clothing, settings, or lighting. See [wildcard guidance](references/wildcards.md) for the file contract.

## Repository guide

- [SKILL.md](SKILL.md): skill entry point, workflow, and defaults.
- [references/](references/): model profiles, prompt formats, video guidance, preservation rules, character guidance, and wildcard conventions.
- [scripts/](scripts/): utilities for Danbooru tag lookup/indexing and randomized character generation.
- [docs/](docs/): supporting documentation and tag data.
- [wildcards/](wildcards/): existing wildcard files.
- [tests/](tests/): utility tests.
- [evals/](evals/): prompt-behavior evaluation cases, tooling, and regression fixtures. Historical runs and review records remain in the [original repository](https://github.com/lfelipegg/scenario-maker-skill/tree/d5804da2c1f14715dfde1160641e2ca2d563cb5d/evals); see the [collection evaluation instructions](../../README.md#evaluation-tooling).

For detailed behavior, start with [output contracts](references/output-contracts.md), [constraints and revisions](references/constraints-and-revisions.md), and the [model profile index](references/model-prompts.md).
