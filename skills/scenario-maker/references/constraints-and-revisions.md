# Constraints and Revisions

Apply these rules to the scene description before rendering model-facing wording. They implement the [resolved invention and preservation decision](https://github.com/lfelipegg/scenario-maker-skill/issues/17#issuecomment-5746449221). See [Scene Composition](scene-composition.md) for the workflow and [Output Contracts](output-contracts.md) for dialect, response shape, and genuine incompatibilities.

## Permission Boundaries

Modes grant permission **within the operation and scope**; they never override either. Supplied facts, necessary implications, exclusions, and locked details remain protected even when not explicitly labeled “locked.”

| Mode | Permitted invention |
| --- | --- |
| **Preserve** | Reword, reorganize, remove redundancy, and make necessary implications explicit. No new visual facts. A sparse result is valid; missing optional detail is not a reason to ask. |
| **Balanced** | Fill unspecified appearance, material, or other local details of the requested content. No new independent subjects, props, actions, or events. Complete lighting only where the scope permits presentation details and without introducing new scene facts. |
| **Explore** | Add compatible, in-scope ideas and props. Add subjects only if the brief leaves the roster open or explicitly authorizes additions. Never replace supplied facts merely because Explore was requested. |
| **Wild** | Develop a bold, coherent concept from the brief, making decisive choices in unspecified, permitted dimensions. Preserve every supplied fact, necessary implication, exclusion, and locked detail. |
| **Unbound** | Autonomously develop a complete in-scope scenario from a minimal seed or supplied opening image, choosing all missing creative direction while preserving every supplied fact and constraint. |

Create and expand default to Balanced. Adaptation and revision default to Preserve: adapt changes expression, while revision changes only what was requested. A vague improvement request or a mode name does not release protected details. Critique identifies problems without applying suggested changes.

Explicit additional permissions apply only to their named dimensions. “Adapt and invent background details” allows background invention, not a different subject. “Change only the jacket to red; Explore” still changes only the jacket color.

### Wild

Wild actively seeks a distinctive organizing idea and makes its details reinforce that idea. Unexpected material combinations, visual relationships, scale, design logic, or events can supply the departure. It need not be surreal and does not mean more objects, more adjectives, longer output, or maximum randomness.

Explore permits compatible additions; Wild directs concept-led invention. Do not artificially require Explore to be conventional or claim that a particular creative result is impossible in Explore.

Apply Wild wherever the operation and scope leave creative room, not only when the brief is short. When little room remains, respect the constraint rather than forcing novelty or asking the user to relax it. Subjects may be added only when the roster is open or additions are explicitly permitted, as in Explore: “a night market” leaves the roster open; “exactly two women” does not.

Preserve all supplied facts, not only explicit locks. This includes exact lettering and its carrier, supplied dialogue or lyrics, source roles, counts, identities, exclusions, and relationships.

Narrow scopes remain narrow. Character design permits appearance, anatomy, clothing, and equipment, not unsolicited pose, expression, setting, lighting, or camera. Clothing gains neither a wearer nor a scene; an isolated asset gains no supporting scene or props. Wild does not authorize the random character generator.

Adaptation changes expression only. A narrow revision changes only the requested dimension. “Adapt, Wild” does not invent a scene; “change only the jacket color; Wild” changes only that color. An explicit compound request can open a local dimension as described above. A generated Wild prompt becomes protected source content in subsequent adaptation or revision, including its previously invented details.

One prompt remains one prompt. Requested variants, counts, formats, lengths, negatives, and wildcard scopes retain their existing contracts. For explicitly broad Wild variants or batches, develop distinct coherent concepts within their common constraints; for controlled variants, vary only the named dimension. Do not make one result longer merely to signal Wild.

### Unbound

Unbound takes responsibility for the entire in-scope scenario: choose the premise and all missing creative direction needed for one coherent, finished prompt within the resolved task, operation, and scope. The user need not supply a concept, action, mood, camera, or ending. Wild seeks a bold organizing concept; Unbound delegates complete scenario authorship. Wild may also produce an equally complete result.

For a full-scene still, develop a coherent visible situation, subject treatment, setting, composition, and atmosphere as needed. Serialize a single frame, not a temporal story. For video creation or expansion, develop connected action and progression with a legible ending or payoff appropriate to the clip, supported by camera, environment, and supported audiovisual choices where useful. A fixed camera, quiet scene, or single shot can be intentional; effects, dialogue, music, cuts, and extra objects are not mandatory.

Preserve every supplied fact, necessary implication, exclusion, exact text, source-role binding, and ongoing lock. An opening image is evidence, not disposable inspiration. Subsequent movement may develop its opening pose or framing unless continuously locked, but Unbound does not authorize identity swaps, recoloring established clothing, transformations of established attributes, or additions to a closed roster.

Operation and scope still govern: pure adaptation invents nothing; an “only X” revision changes only X; character, clothing, and isolated-asset work stays within its scope; critique remains analysis. Generated details become protected source content on subsequent adaptation or revision.

Complete authorship means complete creative decisions, not compulsory longer output, a public storyboard, extra variants, or a new response package. Honor requested counts, formats, lengths, negatives, and wildcard scopes. For explicitly broad Unbound variants or batches, develop distinct coherent scenarios within their common constraints; controlled variants change only their named dimension.

## What Must Survive

Preserve meaning, not incidental prompt wording. Protect supplied counts, colors, props, actions, spatial relationships, exclusions, and required visible text. Required lettering retains exact spelling, case, and punctuation, as well as its binding to the correct object. Normalizing tag separators must not normalize lettering.

A plausible explanation, stereotype, or common association is not a necessary implication. A wet street does not establish active rain or nighttime; an occupation does not establish equipment or a setting. A model's example, tag ordering, preferred composition, or length target does not authorize such additions.

For adaptation or revision of a previously generated prompt, that supplied prompt is now the source to preserve, including details originally invented. Do not discard those details because they were absent from an earlier brief.

A clear later instruction may change a previously locked detail without saying “unlock.” Apply that permission locally; the replacement becomes the detail preserved thereafter. For example, after “the jacket is locked yellow,” “change only the jacket to red” replaces that color, not the hair, pose, props, or background. Simultaneously requiring incompatible colors is a conflict, not a later replacement.

## Scope Boundaries

| Scope | Permitted content |
| --- | --- |
| **Full scene** | Scene content within the selected mode and protected facts. |
| **Character design** | Appearance, anatomy, clothing, and equipment within the mode. No unsolicited pose, expression, action, setting, camera, or lighting treatment. Equipment is not automatically authorized by the character's role. |
| **Clothing** | Garment design, not an invented wearer or surrounding scene. |
| **Isolated asset** | The asset, not supporting objects or an added scene. |

Explicitly supplied or requested presentation details remain allowed and protected. A narrow scope is not permission to delete a requested pose, expression, lighting treatment, or background. No mode, including Explore, Wild, or Unbound, can expand a clothing or character-design request into a full scene.

## Ambiguity and Conflicts

Keep unresolved source ambiguity when it can be faithfully expressed. Do not choose an interpretation merely to make the prompt more specific. Ask when the requested artifact requires a choice that the source does not establish, or when the intended revision is genuinely unclear.
Distinguish an ambiguous new-creation seed from ambiguity in supplied source content. Wild or Unbound may choose a plausible interpretation of a new seed such as “create something around a bank” without asking. Neither may reinterpret “bank” in an existing scene being adapted, silently choose a reference role, invent a required missing input, or resolve contradictory constraints. Missing optional creative detail is an invitation to choose within permission, not a reason to ask.

Examples:

- A supplied “figure beside a bank” can retain “bank” during a prose revision that does not touch the setting. If a requested conversion requires choosing a financial building or a riverbank, clarify rather than deciding silently.
- “Expand this wet street, Preserve” may remain sparse. Do not ask for optional weather, time, or extra objects merely to fill a template.
- If required content cannot fit a hard length or format limit, remove redundancy and optional invention first. If still impossible, explicitly identify the conflicting requirements and ask which constraint may be relaxed. The clarification is not the impossible artifact and must not be compressed into an ambiguous response merely to obey its conflicting limit. Do not silently omit content, exceed the limit while pretending to supply the artifact, or change the format.
- Simultaneous incompatible instructions require clarification. Required `OPEN` lettering plus a limit too short to include it is not permission to abbreviate or drop the text.

Rendering uncertainty alone is not a conflict: preserve requested content without interrupting merely because the model might render it poorly.

## Wild Audiovisual Permission

These bounded permissions also apply to Unbound. When creating or expanding an audiovisual video concept in Wild or Unbound, the mode delegates permitted action and progression, camerawork, shot structure, ambience, sound effects, music, and concise original dialogue or lyrics and vocal qualities when they serve the concept. These are options, not mandatory slots.

Wild or Unbound may select cuts, but must not invent numeric cut times or runtime. Respect supplied duration, shot order, single-shot or continuous-take restrictions, fixed-camera instructions, supplied words, and sound exclusions.

“Animate this opening image; go wild” delegates future animation intent. Unbound plus an available opening image does so without a written scene/action brief once image-to-video is established. Preserve the actual opening; develop subsequent action, camera, and permitted sound without changing enduring identities, attributes, counts, or protected relationships. A starting pose or composition describes the opening; animation can evolve it where no ongoing lock exists. Neither mode can recolor a supplied red coat or add a person to a closed roster merely to create novelty.

Wild or Unbound does not reopen a source-video edit's unaffected dimensions, authorize copying unassigned reference properties, or add audio or temporal content to a still-image task. Pure adaptation and “only X” remain narrow even for audiovisual targets.

Unknown model or task capability still requires the existing routing decision. Wild or Unbound never implies that a visual-only target consumes audio, and neither mode authorizes generation or extraction.

## Boundary Examples

- **“Expand a coat design” — Balanced:** may choose unspecified fabric or stitching; no wearer, umbrella, or street.
- **“Create a witch character” — Balanced:** may invent unspecified hair and clothing; no automatic staff, familiar, or cottage. Explore may add compatible equipment, but not an unsolicited scene.
- **“Two women at a table” — Explore:** no added waiter without permission. **“Design a bustling market”** leaves the roster open.
- **“Adapt this scene to tags” — Preserve:** retain the same subjects, their attributes and relationships, and exact lettering; use the output contract's permitted fidelity-preserving expressions rather than changing the scene to fit convenient tags.
