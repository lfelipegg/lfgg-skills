# Request Routing

Route each request by inferring independent fields from ordinary language. These fields are internal reasoning aids, not a schema the user must fill out or see.

## Routing Fields

- **Operation** — `create`, `expand`, `adapt`, `revise`, or `critique`. A comparison remains analysis across the named prompts, targets, or approaches; do not turn it into prompt writing unless the user also asks for prompts.
- **Task** — `still image`, `image editing`, `text-to-video`, `image-to-video`, `reference-video generation`, or `source-video editing`. The task describes what the prompt is for, independently of model wording or interface controls. Frame-derived still editing is an image-editing workflow whose downstream backend produces video; it is not animation of a hard-anchored opening.
- **Scope** — `full scene`, `character design`, `clothing`, or `isolated asset`. Character and clothing scopes are content boundaries, not models or tasks.
- **Target** — the named model or checkpoint profile, if any. Never infer a specific target from a style, scope, or task.
- **Output** — `prompt only`, `positive/negative pair`, `variants`, `file`, or the requested analysis. Preserve an explicit count, format, file scope, and analysis shape.

Infer all fields together, then apply the instructions for each without allowing one field to replace another. For example, adapting clothing for a named checkpoint is still a clothing-scope adaptation; it is not automatically a character-generation task.

Retain whether an output restriction was **explicitly requested**. Inferring a single-prompt artifact does not mean the user explicitly prohibited all surrounding text; this distinction controls only the bounded H3 enhancement offer in [Output Contracts](output-contracts.md), not generic permission to add notes.

## Content and Capability Boundaries

After resolving the fields, use [Scene Composition](scene-composition.md) to extract the internal scene description and apply the operation. [Constraints and Revisions](constraints-and-revisions.md) owns mode permissions, scope boundaries, supplied-fact and locked-detail preservation, ambiguity, and local change authorization. Create/expand default to Balanced; adapt/revise default to Preserve. Neither a mode nor a model profile broadens the operation or scope.

Infer Wild only from an explicit mode selection or unmistakable creative delegation such as “go wild with the concept.” Infer Unbound from explicit selection or unmistakable whole-scenario delegation, such as “invent the entire scenario from this seed” or “use this opening image and decide the whole video yourself.” Ordinary vagueness and “improve this” do not activate either mode; wild animals do not select Wild, and “go wild” alone does not escalate to Unbound. A specifically named lower mode stays selected. Without a mode or clear delegation, create and expand remain Balanced while adapt and revise remain Preserve. A more specific constraint bounds broad delegation; genuinely incompatible instructions follow the existing conflict rule.

Once the request or conversation establishes image-to-video, an available sole image supplies the opening. Unbound needs no additional written scene/action brief or optional question about what should happen; it develops the permitted subsequent scenario. Do not infer video from an image or Unbound alone. If the task is not established, use normal routing and clarify only material ambiguity. Missing or uninspectable media without a sufficient description still requires the image or a description; multiple materially ambiguous reference roles still require clarification.

Formatting permission is not permission to alter required scene content. Infer the task and scope from the request, but do not invent a target or claim unsupported model, task, or interface capabilities.

Prompt writing never invokes image or video generation. A request to create an image or video within this skill means writing the appropriate prompt unless the user explicitly requests a separate generation capability outside this skill.

## Unknown or Ambiguous Targets

With no target, use generic guidance for the resolved task and do not guess a model. An unknown or ambiguous name may use generic guidance only when its identity is immaterial to the requested artifact.

Ask a concise clarifying question before claiming model-specific adaptation, syntax, task support, or interface behavior when that claim depends on the unresolved identity. Do not ask merely because a model may render a requested detail unreliably; rendering uncertainty does not make the routing ambiguous.

## Routing Boundaries

- “Expand this character outfit for a still image” → `expand` + `still image` + `clothing` + no target + `prompt only` unless another output is requested.
- “Critique this SDXL prompt” → `critique` + the prompt's task and scope when discernible + `SDXL` + requested analysis; return critique, not a replacement prompt.
- “Compare this prompt in SDXL and Krea 2” → comparison analysis for two targets; do not silently produce prompts or generation results.
- “Adapt this starting frame for Wan image-to-video” → `adapt` + `image-to-video` + the described scope + `Wan` + the requested output.
- “Make a character for Pony” → character scope and Pony target; character is neither the model nor the task. Clarify the task only if the distinction materially changes the artifact.
- “Use native local H3 Ref2VA to combine these role-bound references” → reference-video generation; a video used only for motion or style is not automatically the source being edited.
- “Change only the coat in this source video using native H3 Ref2VA” → source-video editing, with an identified source, authorized change, and preserved surroundings.
- “Animate this opening image with native H3 FL2VA” → image-to-video; ask what should change or move only when animation intent is unspecified and future intent has not already been delegated by Wild or Unbound.
- “Use native H3 Ref2VA to edit this still; I will extract the first output frame” → frame-derived image editing; the complete edit must exist in the first generated frame. Do not generate video or extract it.
- “Use Aurora syntax” when Aurora's identity is unresolved → clarify if syntax depends on which Aurora is meant; proceed generically only when the requested result does not depend on that identity.

After routing and scene planning, apply [Prompt Types](prompt-types.md) for prompt syntax and general task conventions, plus the named model or video reference when the resolved target or task requires it. Apply [Output Contracts](output-contracts.md) to determine the returned artifact's shape.
