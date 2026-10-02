# Video Prompts

Use this reference for text-to-video, image-to-video, reference-video generation, source-video editing, and Wan-style prompts. For MiniMax H3, read [its model profile](models/minimax-h3.md) as well: it owns native reference binding, audio, first-frame anchoring, frame-derived still editing, and output sections. The H3 profile is also required for frame-derived edits requested as still images.

Read `routing.md`, `output-contracts.md`, [Scene Composition](scene-composition.md), and [Constraints and Revisions](constraints-and-revisions.md) first. These task fields do not change a critique/comparison into prompt writing, authorize video generation, or expand operation and scope permissions. Explicit output formatting overrides presentation defaults below.

## Core Video Fields

The following are available video-description fields, not required slots or permission to invent:

- subject: who or what appears
- scene: where the action happens
- subject motion: what the subject does over time
- environmental motion: weather, particles, crowds, water, lights, fabric, smoke
- camera motion: how the camera moves
- progression: how the scene changes from start to end
- atmosphere and style: visual mood, medium, realism, genre

Express only fields supplied by the user or permitted by the resolved operation, mode, and scope. A model or video template does not authorize missing motion, camera movement, atmosphere, supporting objects, events, or scene content. Within an authorized Wild or Unbound audiovisual task, motion, camera, progression, and sound may be chosen to serve the organizing concept rather than merely to fill these fields.

Keep visual video descriptions observable. Avoid dialogue, music, sound effects, inner thoughts, and invisible story context unless supplied, requested, or validly delegated by Wild or Unbound as part of the intended audiovisual contract. Supplied nonvisual information needs a visible rendering only for a visual-only task; do not discard intended audio in an audiovisual H3 task. Supplied reference media alone does not authorize copying its sound or inventing sound. Use only supplied or permitted cues, and never infer audio support from Wan or an unnamed model.

## Text-to-Video

Use when the video is generated from text alone. Describe the permitted initial content and its authorized changes over time. Do not invent a “full” initial scene or motion merely to populate the format.

Conditional structure:

`[Supplied/permitted initial content]. [Supplied/permitted motion or progression]. [Supplied/permitted camera, style, lighting, or atmosphere].`

Include pace such as slow, smooth, handheld, fast, drifting, or dramatic only when it was supplied or pace may be chosen within the resolved permissions.

## Image-to-Video

Use when an uploaded image or existing image is the first frame.

- Preserve all content established by the source first frame—including subjects, identity, counts, appearance, objects, text, relationships, composition, setting, style, and exclusions—unless the user locally authorizes a change.
- Describe only the motion or change supplied or permitted after that frame. Wild or Unbound can supply missing future animation intent while preserving the actual opening; preserve the rest and do not make static content disappear merely because it is not moving.
- Do not infer active weather, off-frame causes, new objects, or other details from a plausible reading of the frame. In Unbound, once image-to-video is established, an available opening image needs no written scene/action brief: develop a coherent subsequent sequence with a legible ending. These chosen events are new target content, not facts inferred from the pixels; enduring attributes and continuous locks remain protected.
- If no inspectable image or sufficient description is available, ask for the image or a short description before writing a specific i2v prompt. Wild or Unbound does not invent a required source.

Conditional structure:

`Starting from the provided image, [preserved visible content]. [Supplied/permitted motion or change]. [Supplied/permitted camera, lighting, or atmosphere change].`

## Reference Generation and Source-Video Editing

References are role-bound sources, not necessarily opening anchors. Identify which source contributes identity, appearance, clothing, composition, motion, camera, style, or sound; transfer only those properties. Editing requires an identified visual base, local changes, and preservation of unaffected content. A motion-reference video is not automatically the video being edited. Use the selected profile's verified labels and consumption rules rather than inventing universal reference syntax.

For H3 frame-derived image editing, the requested edited state must exist in the first generated output frame, not at the end of a later transformation. This differs from FL2VA anchoring the input image at time zero. Never perform downstream generation or extraction for a prompt-writing request.

## Wan Video Format

Use for Wan, Wan-style, or when the user asks for a cinematic single-paragraph video prompt.

Wan prompts should be one cohesive paragraph. Within that paragraph, order only the fields the user supplied or the resolved permissions allow, which may include:

- subject
- scene
- subject and environmental motion
- camera language
- visual atmosphere
- stylization

This ordering is presentation guidance, not a requirement to fill every field. Do not split Wan output into shot lists unless the user asks. Keep the permitted content direct, cinematic, and ready to paste.

Example shape when every depicted field is authorized:

`[Established subject and scene]. [Authorized subject or environmental motion]. [Authorized camera movement and progression]. [Authorized style, lighting, or atmosphere].`

## Camera Language

Use precise camera terms when camera treatment is supplied or may be chosen within the resolved permissions:

- close-up, medium shot, wide shot, extreme wide shot
- low angle, high angle, overhead, eye-level
- tracking shot, dolly in, dolly out, orbit shot, crane shot
- handheld, stabilized, slow push-in, pullback, aerial shot
- rack focus, shallow depth of field, parallax, reveal

Use only a few authorized camera terms per prompt. Too many directions can make the prompt muddy.

## Video Variants

When variants are requested, keep protected content and first-frame content unchanged across them. Controlled variants vary only the named dimension. Explicitly broad Wild or Unbound variants may vary multiple open dimensions and should develop distinct coherent concepts within their common constraints; do not produce alternatives unless the user requested them.

For variants in neither Wild nor Unbound, or when the request opens one dimension, vary one meaningful authorized dimension at a time, such as camera motion, pacing, lighting change, subject action, environmental motion, or stylization. Keep variants compatible with the same core idea unless the user asks for broad exploration.
