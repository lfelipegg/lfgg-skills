Here’s a practical plan.

## Goal

Create a Codex skill that turns rough user ideas into strong prompts, with formats like normal prompt, tag prompt, image prompt, video prompt, and revision prompt.

Codex skills are folders with a required `SKILL.md`; optional `scripts/`, `references/`, `assets/`, and `agents/` folders can support reusable logic and examples. Codex uses the skill `description` to decide when to activate it. ([OpenAI Developers][1])

## Required info

1. **Skill purpose**
   Example: “Help users write, refine, compress, expand, and adapt prompts for AI image/video/text generation.”

2. **Trigger conditions**
   When to use it:
   “Use when the user asks for prompt help, prompt engineering, image prompt, video prompt, Midjourney/SD/Flux/Wan prompt, tags, negative prompts, or prompt improvement.”

3. **Supported outputs**
   Suggested:

   * Normal prompt
   * Tag prompt
   * Danbooru-style tags
   * Text-to-image
   * Text-to-video
   * Image-to-video
   * Negative prompt
   * Prompt critique

4. **Required user inputs**

   * Theme / subject
   * Medium: image, video, text, code, etc.
   * Style
   * Length/token limit
   * Format
   * Must include / avoid
   * Target model, if any

5. **Default behavior**
   Example:
   “If missing details, make reasonable assumptions. Default to concise, visual, model-friendly prompts.”

## File structure

```text
prompting-skill/
  SKILL.md
  references/
    prompt-patterns.md
    image-prompt-guide.md
    video-prompt-guide.md
    tag-rules.md
  assets/
    prompt-templates.md
  scripts/
    validate_prompt.py
```

## MVP files

Start with only:

```text
prompting-skill/
  SKILL.md
  references/
    examples.md
```

## `SKILL.md` outline

```md
---
name: prompting-assistant
description: Use when the user asks to create, improve, rewrite, shorten, expand, structure, or critique prompts for AI tools, including text, image, video, coding, and tag-based prompts.
---

# Prompting Assistant Skill

## Core behavior
Help the user transform vague ideas into clear, effective prompts.

## Ask only when necessary
If the request is usable, do not ask clarifying questions. Make reasonable assumptions.

## Required output rules
- Match the requested format.
- Respect token limits.
- Focus on visible details for image/video prompts.
- Avoid hidden thoughts, backstory, emotions, or unverifiable traits unless requested.
- For tag prompts, use comma-separated visual elements.
- For video prompts, include subject, scene, motion, camera movement, atmosphere, and style.

## Workflow
1. Identify the target medium.
2. Extract subject, setting, action, style, lighting, mood, constraints.
3. Fill missing details with sensible defaults.
4. Produce the prompt.
5. Optionally include a negative prompt or variants when useful.

## Default output
A concise, polished prompt ready to paste into the target AI tool.
```

## Recommended next step

Create the MVP `SKILL.md`, then test it with 10 rough prompts like “cyberpunk girl in rain” and “make this better for Wan video.”

[1]: https://developers.openai.com/codex/skills?utm_source=chatgpt.com "Agent Skills – Codex"
