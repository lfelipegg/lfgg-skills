# MiniMax H3 (Native Local)

This profile supplies compatible prompt-authoring defaults only after the task, scene, permissions, and output have been resolved. Follow [Output Contracts](../output-contracts.md) for response shape and explicit-format precedence, [Constraints and Revisions](../constraints-and-revisions.md) for preservation, scope, and invention permissions, and [Video Prompts](../video-prompts.md) for shared temporal semantics. This profile does not broaden those permissions.

## Identity, Routes, and Deliverable

Supported prompt-writing routes are limited to the ordinary native local ComfyUI paths below:

- **H3 Ref2VA — reference video generation/editing:** `H3-Base-Ref2VA` through `MiniMaxH3ReferenceToVideo`.
- **H3 FL2VA — first-frame video:** `H3-Base-FL2VA` through `MiniMaxH3ImageToVideo`, with one actual opening image. Despite the checkpoint family name, this selected one-image task uses the official **I2VA** opening-anchor form, not the two-image FL2VA task prefix.
- **H3 Ref2VA — frame-derived still edit:** `H3-Base-Ref2VA` reference generation, followed downstream by separate extraction of the first generated frame.

Do not silently substitute hosted `MiniMax-H3`, `MiniMax-H3-Max`, older Hailuo models, another checkpoint, or adjacent text-only, continuation, last-frame, interpolation, guide-chain, ControlNet, mask, turbo, Context-IR, or 2K-regeneration workflows. Generic guidance is acceptable when identity is immaterial; clarify before an identity-dependent adaptation or capability claim.

Return **prompt text for later execution**, not workflow JSON, API payloads, sampler/install settings, generated media, or an extracted frame. Prompt authoring can use inspectable media or sufficiently clear descriptions/transcripts. Never claim unseen or unheard details were inspected. Actual source-dependent execution still requires the correctly connected media; a description or textual label does not connect conditioning.

Sparse descriptions are valid authoring evidence; do not demand optional appearance or setting detail to fill a template. When a consequential missing role requires clarification, ask only about that missing role or another genuine conflict, not unrelated optional scene detail.

## Official Guides and Local Overrides

This compact profile is sufficient for ordinary requests. Consult the bundled official guides conditionally when a request uses their complex features or asks for official examples:

- [`minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_base_en.md`](minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_base_en.md): consult §4 for extended camera, vocal-event, cross-cut, visible-text, and sound-placement examples; consult §2.1 and §3.1 only for the selected one-image I2VA anchor.
- [`minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`](minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md): consult §2–§6 for complex multi-reference, storyboard/composition, or mixed copied/referenced audio requests and extended examples. Its shared audiovisual conventions come from the base guide's §4.

The local route, permission, exact-text, output-format, length, unspecified-audio, and untimed-cut policies override differing upstream defaults. Upstream examples do not authorize new subjects, camera moves, audio, timestamps, or scene details. Keep the bundled guides byte-identical to their pinned sources; record provenance here rather than modifying those source copies.

## Language, Detail, and Output

- Default to **English** and **Medium** detail (about 150 tokens) for every supported route. Very Short (about 75) and Long (about 300+) are approximate guides, not quotas or model limits. Required content outranks a soft guide; never pad sparse input.
- Preserve visible text and supplied dialogue or lyrics in their original language, spelling, case, and punctuation unless translation or revision is authorized.
- Explicit format, language, length, multiplicity, and output instructions override presentation defaults when compatible. Preserve reference bindings and temporal meaning in the requested shape. Do not add notes, settings, variants, or a prompt package.
- Default video intent is one shot when no relevant delegation exists. Preserve explicitly requested cuts, shot order, actor/action bindings, overlap, timing, pace, and audio continuity. Wild or Unbound video development may choose cuts; those cuts are authorized rather than padding. Never invent cut times or timestamps, runtime, frame count, or frame-accurate scheduling.
- Leave camera behavior unspecified when neither the user nor valid Wild or Unbound video delegation chooses it. Under Wild or Unbound, camera behavior may be selected to serve the concept. Preserve requested movement or fixed framing and all supplied timeline or shot restrictions; clarify genuinely incompatible camera or framing locks rather than weakening them.
- The structures below form **one pasteable text prompt**. Their sections are not separate ComfyUI properties and are not parser requirements.

## Native References and Conditioning

The native Ref2VA node exposes up to 9 reference images, 3 reference videos, and 3 standalone reference audios. Each reference video has a separate index-paired soundtrack input. These are per-category socket maxima; do not import hosted aggregate file/duration limits or claim unlimited practical capacity.

Bind labels to **connected, consumed order**, not upload order or a universal socket-number convention:

- Images use `<Picture N>`; videos use `<Video N>`; audio uses its own `<Audio N>` counter.
- Presentation proceeds through images, then each video with its connected soundtrack audio label before that video, then standalone audio. Missing inputs create no labels.
- A soundtrack participates in audio numbering, so `<Video 1>` need not pair with `<Audio 1>`. Sound in a video is not automatically extracted or reused; its soundtrack must be separately connected and assigned a role.
- `<Subject N>` denotes reusable content, not an input slot. One asset may define several subjects, and several assets may define one subject.

Assign only named roles: identity, appearance, clothing, composition, motion, camera, style, source-video editing, audio reuse, or audio reference. An appearance source does not donate its background, pose, dialogue, or soundtrack. Wild or Unbound never invents an input asset, supplies an unknown reference role, or copies unassigned properties; either may create authorized new target content without pretending that content came from a reference. Clarify material role conflicts rather than choosing silently.

A connected socket or textual label does not prove active media conditioning. Image/video latent references depend on the video VAE; audio latent references depend on the audio VAE; tokenizer audio labels are not the audio signal. Known inactive conditioning, excess references, or required content beyond a consumed/truncated video segment requires clarification—not silent dropping or a capability promise. Native video references may be truncated to the target frame count and cropped to the valid frame grid; very short videos may be rejected. Unknown graph/runtime details remain unknown.

## Ref2VA Structure and Relationship Semantics

Reference generation, source-video editing, and frame-derived still editing use these sections in order:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

Use task prefixes only for relationships actually present. Within the selected routes, `keyframe completion`, `reference generation`, `video editing`, `audio reuse`, and `audio reference` describe assigned roles and may be joined with ` + ` when needed. The official guide uses `keyframe completion` when an image supplies an edited keyframe; in a frame-derived still edit this is reference-guided prompt intent, not an FL2VA hard anchor or native still-image editing. For a source-video edit, begin the summary body `The target video is an edited version of <Video N>.`, replacing N with the actual consumed label of the edited source, not always 1. An image edit is not `video editing` merely because Ref2VA outputs video, and a video used only for motion, camera, or rhythm is not the edited source.

In `subject_definitions`, give one line to each independently tracked content item:

- `<Subject N>` may denote a person, object, garment, environment, style, or action, not only a human. Cite an appearance-only picture or content-only video in its subject definition without adding a redundant standalone entry.
- Give `<Picture N>` its own entry when the image itself supplies an independently tracked edited frame, composition, or storyboard role. For a storyboard, map the specified shots and assigned planning properties; do not turn it into an I2VA hard anchor or infer additional cuts. Existing task-prefix rules determine whether an actual concrete frame role also requires `keyframe completion`.
- Give `<Video N>` its own entry for the selected editing source or independently tracked camera, cut, or rhythm structure. Conceptual content taken from that asset remains under `<Subject N>`. Continuation is not supported by the selected routes.
- Keep one `<Audio N>` definition for an assigned audio source even when it has multiple roles. All sections retain its consumed-order identity; omit unused connected audio without renumbering later consumed audio.

The `summary` reuses established content labels and does not invent new label meanings. Give `retention_analysis` one row per separately defined or tracked item, not one row for every provenance-only token. Identify relevant shots or roles without inventing shot times.

| Visual marker | Selection rule |
| --- | --- |
| `fully_preserved` | All characteristics in the item's defined role remain intact. |
| `partially_preserved` | The same referenced content is used, but some defined characteristics change or only part is retained. |
| `attribute_transfer` | Specified characteristics transfer to a different identifiable target subject; identify that target. |
| `weak_reference` | Only broad category, style, composition, or atmosphere similarity is requested. |

| Audio marker | Selection rule |
| --- | --- |
| `fully_copy` | The entire source signal is intended as the target video's complete final audio track, with no added, replaced, or removed audio. |
| `partially_copy` | Copy selected time or layers, or copy the source while adding, removing, or replacing other sounds. A complete BGM file mixed with new dialogue belongs here. |
| `reference` | Recreate only assigned properties or content rather than directly reusing the signal. |
| `weak_reference` | Only broad category or atmosphere similarity is requested. |

These markers express scoped intent, not pixel identity, waveform equality, timing, lettering, edit fidelity, or generated-quality guarantees. A marker applies only to the role defined for that label: `fully_preserved` on an identity source does not copy its pose, background, or other unassigned properties. New authorized target actions or backgrounds do not downgrade preservation of a separately scoped identity source.

Audio needs an explicit role. Distinguish direct signal reuse from timbre, delivery, style, rhythm, dialogue/lyric-content, or sound-texture reference. Do not import source dialogue for a timbre-only request. Preserve supplied words and language for reuse or requested reperformance; mark unintelligible spans `[unclear]` rather than inventing them. Do not create a visible speaker for a vocal cue that exists only inside reused music. Keep referenced subjects and speaker IDs stable.

Wild or Unbound audiovisual delegation may establish new target sound intent, including whether a newly invented sound is diegetic or audience-only score. It does not assign a role to an existing audio reference. Bind every referenced audio property to an established target sound, not merely to an input. Timbre, rhythm, or delivery reference alone does not authorize opportunistically choosing speech, a musical performance, accompaniment, a visible musician, or placement. If an existing audio reference lacks its intended target sound or consequential placement, ask what should use that property. When the target sound is already specified, apply only the assigned properties without asking for optional detail.

Author audio sections when sound is requested, supplied as intended target content, or selected through valid Wild or Unbound audiovisual delegation. Otherwise write `Unspecified`; this does not request silence. `fully_copy`, explicit silence, no-score instructions, and other audio locks remain binding. Use `N/A` only with its explicitly declared meaning, such as requested complete silence in `overall_soundscape` or no non-diegetic music in `non_diegetic_music`.

## Shared Audiovisual Serialization

Apply these rules to Ref2VA `detailed_description` and I2VA `integrated_multimodal_description`. They do not add audio to frame-derived still editing when audio is irrelevant or unspecified.

### Speakers and Text

- Assign `(S1)`, `(S2)`, and subsequent IDs by first actual vocal event in the target timeline, independently of `<Subject N>` and `<Audio N>` numbers. Attach the assigned ID to the speaker at that first event and every later speech or singing fragment; no fragment is left unmarked. Keep each ID across shots and reuse it in any voice-bound audio definition. Do not put speaker IDs in `retention_analysis`.
- A referenced vocal source is `<Subject N> (Sx)`. An independent narrator without a visual subject uses its supplied identifying description plus `(Sx)`. Silent subjects receive no ID. When already identified voices speak or sing together, use a compound ID such as `(S1,S2)`.
- Establish each vocal source from supplied or inspectable distinguishing traits and permitted vocal properties. Wild or Unbound may author concise dialogue or lyrics and choose concept-serving vocal qualities; otherwise never invent age, accent, pitch, timbre, or a visible narrator to fill the structure.
- Use `<d>[Language] exact words</d>` for supplied speech or lyrics and words authored under Wild or Unbound. Preserve supplied text, language, spelling, and punctuation, including repeated punctuation, unless revision or translation was authorized. For words authored under Wild or Unbound, use an explicitly requested language or the profile's English default. Keep speaker identity, action, delivery, and reference-role prose outside `<d>`. Use `[unclear]` only for genuinely unintelligible source spans. A timbre-only reference does not authorize source dialogue.
- Use the exact phrase `says in an off-screen voiceover` for a requested voiceover. If the voice belongs to a character currently shown, immediately follow each voiceover block with closed-lips wording for that character. If no corresponding character is visible, do not invent one or close an unrelated visible speaker's lips. An in-scene voice whose speaker is off camera is not automatically voiceover; retain its requested off-screen diegetic role.
- A lyric cue contained only in directly reused score or soundtrack remains associated with `<Audio N>`; do not invent a separate vocal source or assign an `(Sx)` ID to a reacting visual subject.
- Put visible signs, labels, and subtitles in ordinary double quotes in the default prose format and preserve their contents byte-for-byte. A caption is not spoken dialogue unless it is explicitly also spoken.

### Cuts and Vocal Continuity

- Keep sequential `[Shot N]` labels and put no cut timestamp on `[Shot 1]`; the I2VA 0.00-second opening anchor remains separate.
- When a later cut time is supplied, express its unchanged value as `[Shot 2] At 00:03.500, ...` in the default `MM:SS.mmm` format. Supplied cut times must remain increasing and within a supplied duration. A contradictory specified timeline requires clarification, not reordered or dropped events or silently adjusted times.
- For requested cuts or cuts authorized by Wild or Unbound without supplied times, use sequential `[Shot N]` labels and preserve the intended relative order and overlap without inventing timestamps or asking for optional timing. An explicit no-timestamp format remains valid.
- When one supplied line or line authored under Wild or Unbound crosses a cut, put `<scenetrans>` at the connecting end and start of the two dialogue fragments and state that the same audio continues uninterrupted. Do not repeat the full line, reword its fragments, or restart the speaker. The marker is structure, not an extra spoken word.
- Use `<cutoff>` at a requested terminal interruption of speech. Never add truncation merely to fit the Medium soft target, and never finish a deliberately incomplete utterance. If a request supplies a full line but leaves the required truncation point unidentified, clarify that point rather than inventing omitted content.
- Explicit duration constrains the described intent. Do not schedule an event beyond it, invent a duration when none is supplied, or claim that prompt text controls runtime frame count or precise audio synchronization.

### Camera and Visual Specificity

- Put camera motion supplied or authorized by Wild or Unbound in natural prose in the relevant shot. Preserve its motion type and any supplied amplitude or speed; do not require missing amplitude or speed. Distinguish optical zoom from moving the camera forward, and pan from sideways camera translation. Do not replace a requested cut with a camera move merely because an upstream example recommends it.
- For Ref2VA, put overall style supplied or authorized by Wild or Unbound before `[Shot 1]`. For I2VA, establish source-derived style and composition inside `[Shot 1]`. If style is unspecified and not authorized by Wild or Unbound or established by permitted evidence, omit it.
- Prefer concrete visual and audible details supplied or authorized by Wild or Unbound over praise or generic cinematic filler. Wild or Unbound may select concept-serving style, instrumentation, tempo, dynamics, camera, and sounds without requiring every field. Do not delete or replace supplied intent, invent concrete instruments to reinterpret a supplied mood, or expand sparse sources in neither Wild nor Unbound to hit a word target.

### Sound Placement

- The timeline field owns speech, singing, in-scene music such as radio, phone, or television audio, and precisely synchronized sound events supplied or authorized by Wild or Unbound.
- `overall_soundscape` summarizes ambience, physical sounds, and non-verbal human sounds across the clip supplied or authorized by Wild or Unbound. Do not duplicate full dialogue or lyrics or classify diegetic songs or background score here.
- `non_diegetic_music` describes audience-only score supplied or authorized by Wild or Unbound using permitted instrumentation, tempo, and dynamics. Copy or reference relationships belong only in the section for the affected audio layer; a mixed asset may be cited in both sections for different assigned layers.
- Retain `Unspecified` for audio left unchosen, `overall_soundscape: N/A` for explicitly requested complete silence, and `non_diegetic_music: N/A` for explicitly absent score. Lack of instructions is not silence. Do not impose upstream sentence quotas.

All syntax in this section is a compatible default under [Output Contracts](../output-contracts.md). If the user explicitly requests plain prose without tags or headings, preserve speaker identity, exact words, continuity, and reference relationships in that form instead of forcing this serialization or claiming incompatibility.

### Bounded Serialization Snippets

These fragments illustrate only the named rule; they are not complete prompts or hard parser specifications.

**Speaker-order source brief:** Picture 1 defines Mira as `<Subject 1>`, Picture 2 defines Jo as `<Subject 2>`, and Audio 1 supplies only Mira's warm timbre. Jo says `Ready?` first, Mira says `Yes!` second, then both say `Go!` together.

```text
<Audio 1> is the voice-timbre reference for <Subject 1> (S2).
[Shot 1] <Subject 2> (S1) says, <d>[English] Ready?</d> <Subject 1> (S2) replies with the warm timbre referenced from <Audio 1>, <d>[English] Yes!</d> Then <Subject 2> and <Subject 1> (S1,S2) say together, <d>[English] Go!</d>
```

**Voiceover source brief:** Picture 1 shows Noor at a desk with her mouth closed; Noor's own voiceover says `I remember.` and her lips must remain closed. Separately, an independent unseen narrator says `Listen.` without any corresponding visible subject.

```text
Noor (S1) says in an off-screen voiceover, <d>[English] I remember.</d> Noor's lips remain closed.
The independent unseen narrator (S2) says in an off-screen voiceover, <d>[English] Listen.</d>
```

The second line does not invent a narrator body or close Noor's lips on the narrator's behalf.

**Cross-cut source brief:** Ari says the single exact line `Stay with me.`; `Stay` occurs before the supplied cut at 3.5 seconds and ` with me.` follows it as the same uninterrupted utterance. Separately, Ari says the explicitly unfinished words `If you open` and the video ends mid-utterance.

```text
[Shot 1] Ari (S1) begins one uninterrupted line, <d>[English] Stay<scenetrans></d>, and the same audio continues across the cut.
[Shot 2] At 00:03.500, Ari (S1) continues without restarting, <d>[English] <scenetrans>with me.</d>
Ari (S1) begins the separate unfinished line, <d>[English] If you open<cutoff></d>, which is interrupted by the end of the video.
```

**Mixed-audio source brief:** Audio 1 is a complete instrumental BGM file reused as audience-only score while Noor adds the new spoken line `Welcome.`.

```text
retention_analysis:
<Audio 1>: partially_copy - the entire instrumental source remains as audience-only score, but new dialogue is added to the final audio track.

detailed_description:
[Shot 1] Noor (S1) says, <d>[English] Welcome.</d>

non_diegetic_music:
<Audio 1> is directly reused in full as the audience-only score beneath the new dialogue.
```

This is `partially_copy`; `fully_copy` is reserved for the complete-final-track case illustrated in the source-video editing example below.

**Attribute-transfer source brief:** Picture 1 supplies a blue ceramic vase as the edit target. Picture 2 supplies only a red jacket's herringbone texture; transfer that texture to the vase without its red color, wearer, garment shape, or background.

```text
<Subject 1> is the blue ceramic vase from <Picture 1>.
<Subject 2> is only the herringbone texture from the jacket in <Picture 2>.
<Subject 2> (texture donor for <Subject 1> in [Shot 1]): attribute_transfer - only the herringbone texture transfers to the blue vase; no other jacket or picture attributes transfer.
```

## Ref2VA Full-Reference Generation

Use role-bound images, videos, and audio to synthesize a target video. After binding every reference role, communicate only supplied or authorized subjects, relationships, appearance, setting, composition, motion, camera, style, and sound. Wild or Unbound may develop new target content but identity-only sources still do not donate backgrounds, action, audio, or other unassigned properties. Preserve rosters, exclusions, locked details, and exact lettering. Transfer only the named properties from each supplemental reference.

**Example source:** Picture 1 supplies Mira's appearance and red coat; Video 1 supplies walking motion only; its separately connected soundtrack is Audio 1 but is not requested; standalone Audio 2 supplies a dry alto timbre and delivery for the exact line `门还开着。`; Mira walks past a sign that must read `Open late!`; camera is unspecified.

```text
subject_definitions:
<Subject 1> is Mira, whose identity, appearance, and red coat come from <Picture 1> and whose walking motion comes from <Video 1>.
<Audio 2> is the voice-timbre and delivery reference for <Subject 1> (S1); its signal and original words are not copied.

summary:
[reference generation + audio reference] The target video shows <Subject 1> walking past a sign reading "Open late!" while <Audio 2> guides only her voice timbre and delivery.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - Mira's identity, appearance, and red coat from <Picture 1> are retained, while only the walking motion is transferred from <Video 1>.
<Audio 2>: reference - its dry alto timbre and delivery guide Mira's supplied line without copying the signal or source words.

detailed_description:
[Shot 1] <Subject 1> (S1), preserving Mira's appearance and red coat from <Picture 1>, walks with the motion referenced from <Video 1> past a sign displaying the exact words "Open late!" She says in the dry alto timbre and delivery referenced from <Audio 2>, <d>[Chinese] 门还开着。</d> No visual, dialogue, background, camera behavior, or soundtrack is taken from <Video 1> beyond its assigned walking-motion role.

overall_soundscape:
Unspecified

non_diegetic_music:
Unspecified
```

Here `<Audio 1>` is absent from the prompt because the connected video soundtrack has no requested target role; `<Audio 2>` keeps its consumed-order label. The generation prompt communicates relationships but does not connect or execute the sources.

## Ref2VA Source-Video Editing

Identify the source video being edited, every authorized change, and the content to preserve. Wild or Unbound does not reopen unaffected dimensions of a source-video edit. Do not silently reuse, replace, remove, or invent its soundtrack. Clear edits apply locally; unaffected protected content remains protected.

**Example source:** Video 1 is the edited source. Change only Ana's green scarf to blue; preserve Ana, Ben, their positions, actions, café, framing, lighting, and the exact sign `Open late!`. Its separately connected Audio 1 is reused unchanged. No camera change is requested.

```text
subject_definitions:
<Video 1> is the source video for the target video edit.
<Subject 1> is Ana in <Video 1>, including her identity and clothing; only her green scarf is to change to blue.
<Subject 2> is Ben in <Video 1>, preserved without change.
<Audio 1> is the synchronized soundtrack of <Video 1> and is reused as the target video's complete final audio track.

summary:
[video editing + audio reuse] The target video is an edited version of <Video 1>. Only <Subject 1>'s green scarf becomes blue; all other specified visual content and <Audio 1> are retained.

retention_analysis:
<Video 1> (source composition, action, framing, lighting, setting, and timing): fully_preserved - the café, Ana and Ben's positions and actions, and the sign reading "Open late!" remain unchanged.
<Subject 1> (appears throughout): partially_preserved - Ana's identity and all clothing remain as in <Video 1>, except her green scarf is blue.
<Subject 2> (appears throughout): fully_preserved - Ben remains unchanged.
<Audio 1>: fully_copy - <Audio 1> is reused as the complete final audio track.

detailed_description:
The target keeps <Video 1>'s existing visual style.
[Shot 1] Follow <Video 1>'s original shot, composition, actions, framing, lighting, café setting, camera behavior, and timing. Preserve <Subject 1> and <Subject 2>, their positions and relationships, and the exact sign text "Open late!" Change only <Subject 1>'s scarf from green to blue from the first output frame onward. Reuse <Audio 1> unchanged; add no dialogue, sound, music, camera change, or other visual alteration.

overall_soundscape:
The ambience and physical sounds in <Audio 1> are directly reused as part of the complete copied soundtrack.

non_diegetic_music:
Any audience-only music present in <Audio 1> is directly reused as part of the complete copied soundtrack; add none.
```

## FL2VA First-Frame Video

For the default structured output, the selected local path uses one actual opening image and begins with the official I2VA anchor:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

After one blank line, write `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music`. The image is the actual 0.00-second opening: preserve its starting identity, clothing, colors, objects, composition, and relationships, then express authorized motion or transformation forward from it. Do not rebuild the image as an invented scene.

Bare “animate this” requires asking what should change or move only when future animation intent has not been supplied or delegated; motion is not compulsory, and an explicit still hold is valid. Wild or Unbound delegation supplies future animation intent. In particular, Unbound plus an available opening image suffices without any written scene/action brief once image-to-video is established: independently develop the subsequent scenario, not a replacement opening. The actual opening, enduring attributes, and every ongoing lock remain protected.

Separate subject motion, environmental motion, temporal transformation, and camera behavior. An ordinary opening pose or composition may develop through action; continuous pose/composition locks remain binding. “Only the curtain moves” does not permit blinking, gestures, lighting drift, sound, or a camera move. A later red-to-blue coat transition preserves red at the opening but requires permission for that transformation; neither Unbound nor future-animation delegation itself authorizes recoloring established clothing. A request for the anchored opening itself to already be blue conflicts with this route and requires clarification rather than route substitution or source rewriting.

**Example source:** The opening image contains a woman in a red coat beside a closed curtain and a sign reading `Open late!`. Only the curtain may move gently; framing is locked; audio intent is unspecified.

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve <Picture 1> as the opening state, including the woman's identity, red coat, still pose, position, the closed curtain, the locked framing and lighting, and the sign displaying the exact words "Open late!" The camera remains fixed. Only the curtain begins to move gently; the woman, her clothing, the sign, all other objects, and the lighting remain still and unchanged.

overall_soundscape: Unspecified

non_diegetic_music: Unspecified
```

Explicitly requested multi-shot intent or cuts authorized by Wild or Unbound are allowed: use sequential shot labels and preserve supplied cuts, order, overlap, timing, and audio continuity without inventing timestamps, runtime, or scheduler precision. Audio, dialogue, music, camera motion, and cuts may serve the scenario but are not mandatory.

## Ref2VA Frame-Derived Still Editing

This route means reference-guided video generation followed by downstream extraction of the **first generated output frame**. It is not native still-image editing, generation is not extraction, and Scenario Maker performs neither.

Identify an image or video reference as the visual edit base and scope every supplemental reference. For a video base, enough source/target information must identify the intended opening image; clarify an ambiguous moment instead of selecting or extracting a frame. The complete requested still edit must exist in the first output frame. Wild or Unbound remains inside the authorized still edit: neither adds later animation, soundtrack, or motion merely because the backend is video. Do not describe a later transition as satisfying the still. Leave later motion, camera behavior, and whole-clip stillness unspecified unless the request explicitly supplies them. If the required state exists only later while the requested deliverable is the first frame, clarify rather than moving the extraction point or dropping the event. Do not use the FL2VA hard first-frame anchor to edit that same anchored frame.

**Example source:** Picture 1 shows a hand holding a yellow mug labeled `MORNING` above a wooden table. Change only the mug to cobalt blue and preserve the hand, table, framing, lighting, and exact label; later motion and audio are irrelevant.

```text
subject_definitions:
<Picture 1> is the visual edit base for the first generated output frame, showing a hand holding a yellow mug labeled "MORNING" above a wooden table.
<Subject 1> is the mug and holding hand from <Picture 1>; only the mug color changes.

summary:
[keyframe completion] The first generated output frame is an edited still based on <Picture 1>, with only <Subject 1>'s mug changed from yellow to cobalt blue.

retention_analysis:
<Picture 1> ([Shot 1] edited opening keyframe): partially_preserved - its hand, table, framing, lighting, composition, and exact "MORNING" label are retained while the mug color changes.
<Subject 1> (appears in [Shot 1]): partially_preserved - the same mug and hand are retained, with only the mug's yellow surface changed to cobalt blue.

detailed_description:
[Shot 1] The first generated output frame already shows the complete edit: the same hand holds the same mug in the composition, framing, and lighting of <Picture 1>, but the mug is cobalt blue. Preserve the wooden table and the mug's exact visible label "MORNING" without alteration. Later motion and camera behavior are unspecified.

overall_soundscape:
Unspecified

non_diegetic_music:
Unspecified
```

## Negatives and Optional Enhancement

Do not add automatic negatives or a stock blacklist. The inspected native templates route positive conditioning to `BasicGuider` and expose no separate negative-text path. If a requested negative is intended for this selected path, explain that it is not consumed and clarify the intended use. Clearly requested standalone negative text may be returned without claiming execution support. Never silently fold it into the positive prompt. Scene exclusions remain binding authored instructions; never negate required text, intentional style or blur, stillness, or authorized motion.

After the pasteable prompt, briefly offer optional in-chat enhancement only when the requested output format permits. Suppress the offer for “prompt only” or equivalent restrictions. Do not emit a second version automatically. Enhance only after the user requests it, preserving task, scope, invention permissions, source evidence, role bindings, and locks. This is an in-chat rewrite—not external Context-IR, a hosted service, checkpoint behavior, generation, or extraction.

## Primary Sources

- [Portable H3 prompt-writing skill, pinned audit revision](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/skills/h3-prompt-writing/SKILL.md)
- [Official base/I2VA prompt guide, pinned audit revision](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/skills/h3-prompt-writing/references/base-en.txt)
- [Official full-reference prompt guide, pinned audit revision](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/skills/h3-prompt-writing/references/ref-en.txt)

Audit date: 2026-09-23. Both bundled guides were byte-identical to upstream revision `d21241f0a4b3acbb34c97dae47fa417b7065e438`:

| Bundled guide | SHA-256 |
| --- | --- |
| `minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_base_en.md` | `2cfebc096a6e08370f288d468d90b60f7f9bcb938f94bf090816e910e48e75fc` |
| `minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` | `1e574f356716ad55612247ffb7bbccbcdb484ad96599d63c7dca1af186b1fab7` |

- [Native H3 ComfyUI nodes, fixed revision](https://github.com/Comfy-Org/ComfyUI/blob/5ba116a40f1944f64e2e4a8ace826656e6293bf4/comfy_extras/nodes_minimax_h3.py)
- [Native H3 tokenizer, fixed revision](https://github.com/Comfy-Org/ComfyUI/blob/5ba116a40f1944f64e2e4a8ace826656e6293bf4/comfy/text_encoders/minimax.py)
- [Native I2V workflow template, fixed revision](https://github.com/Comfy-Org/workflow_templates/blob/371a7b7171bbd11e9cc92ef615ba5ad223d7e5b4/templates/video_minimax_h3_i2v.json)
- [Native R2V workflow template, fixed revision](https://github.com/Comfy-Org/workflow_templates/blob/371a7b7171bbd11e9cc92ef615ba5ad223d7e5b4/templates/video_minimax_h3_r2v.json)
- [BasicGuider implementation, fixed revision](https://github.com/Comfy-Org/ComfyUI/blob/5ba116a40f1944f64e2e4a8ace826656e6293bf4/comfy_extras/nodes_custom_sampler.py#L792-L816)
