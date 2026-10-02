# Scenario Maker

A vocabulary for describing visual content and expressing it as prompts for image and video workflows. Prompt writing is distinct from running generation.

## Language

**Scene description**:
The visible content of a requested image or video, independent of the wording preferred by a model: subjects, attributes, relationships, setting, composition, visual treatment, and required text.

**Model profile**:
The conventions for expressing a scene for a particular model or checkpoint, including its prompt language and applicable syntax. A model profile is not a task definition or an interface's controls.

**Task profile**:
What must be communicated for an activity such as still-image creation, image editing, text-to-video, or image-to-video. It is distinct from how a model prefers that information expressed.

**Invention mode**:
The degree and kind of creative freedom available when developing unspecified content, within the requested operation, scope, and supplied facts.

**Wild**:
An invention mode that develops an idea around a bold, coherent concept while retaining every supplied fact and constraint.

**Unbound**:
An invention mode that autonomously develops a complete in-scope scenario from a minimal seed or supplied opening image while retaining every supplied fact and constraint.

**Locked detail**:
An attribute or relationship that must survive adaptation, revision, or variation unless the user explicitly permits changing it.

**Controlled variant**:
A version that changes one named dimension while preserving the other scene details.

**Exploratory variant**:
A version that changes multiple permitted dimensions while retaining the core concept and locked details.

**Full-prompt wildcard entry**:
A complete generation prompt selectable as one entry, including any applicable model-specific prefix.

**Fragment wildcard entry**:
A partial description intended for insertion into a larger prompt, rather than a complete prompt with repeated model boilerplate.

**Frame-derived image editing**:
A workflow that uses video generation and takes the first generated frame as an edited still image. The requested MiniMax H3 route uses this meaning; it does not assert that the model exposes native still-image editing.
_Avoid_: Native image editing, when referring to this video-and-frame-selection workflow
