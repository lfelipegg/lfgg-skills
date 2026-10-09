# Wan Video Prompts

This profile supplies compatible presentation defaults only after the task, scene, permissions, and output have been resolved. Follow [Output Contracts](../output-contracts.md) for response shape and explicit-format precedence, [Constraints and Revisions](../constraints-and-revisions.md) for preservation, scope, and invention permissions, and [Video Prompts](../video-prompts.md) for shared task and temporal guidance.

## Identity and Aliases

Case-insensitive `Wan` and `Wan-style` select the existing version-agnostic Wan text-to-video and image-to-video prompt-writing guidance. No particular Wan release, checkpoint, fine-tune, interface, or additional task is asserted by this profile. Do not invent version aliases or infer newer-model support from the family name. If the exact version or interface materially changes the requested syntax or capability, obtain that verified contract or clarify rather than guessing.

## Wan Video Format

Wan prompts should be one cohesive paragraph. Within that paragraph, order only the fields the user supplied or the resolved permissions allow, which may include:

- subject
- scene
- subject and environmental motion
- camera language
- visual atmosphere
- stylization

This ordering is presentation guidance, not a requirement to fill every field. Do not split Wan output into shot lists unless the user asks. Keep the permitted content direct, cinematic, and ready to paste.

Explicit prose, tags, normalization, structure, length, and output instructions override this paragraph preference when compatible; they do not waive protected content or verified hard interface requirements. The generic length default remains Very Short unless the user specifies otherwise. A cinematic-paragraph request without a named target does not select Wan.

## Task, Audio, and Interface Boundaries

For text-to-video, describe only the supplied or permitted initial content and progression. For image-to-video, preserve the actual opening image and express only authorized subsequent motion or changes. An appearance reference is not automatically an opening image, and a model name is not evidence that an interface supports editing or reference controls. Use the shared video guidance without importing another model's reference labels, opening-anchor syntax, audio fields, or route-specific sections.

Do not infer audio support from Wan. Preserve intended sound information under the selected workflow's verified audiovisual contract when one is established; unspecified sound is not a request for silence. This version-agnostic profile does not assert an audiovisual interface or authorize inventing unsupported sound syntax.

## Negative Prompts and Wildcards

Do not add unsolicited negatives, companion files, or an enhancement offer. Follow [Output Contracts](../output-contracts.md#negative-channels) for requested negatives and the actual consuming workflow; this profile does not establish whether any particular Wan interface consumes a negative channel. Never silently fold negative text into a positive prompt or claim unsupported conditioning.

Follow [Wildcards](../wildcards.md) for file and fragment contracts; full-prompt entries use this profile's compatible paragraph default unless explicitly overridden.
