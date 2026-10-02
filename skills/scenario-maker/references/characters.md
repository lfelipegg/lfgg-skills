# Character Generator

Use `scripts/character_generator.py` only when the user requests randomized characters, randomized character batches, or explicitly asks to use the generator. A character-design scope or supplied attribute list alone does not authorize randomization: write the requested design directly, preserving its supplied details.
Apply [Scene Composition](scene-composition.md) for the model-neutral content workflow and [Constraints and Revisions](constraints-and-revisions.md) for operation, mode, scope, preservation, and conflict rules.

## Scope Boundaries

A character-design prompt may describe appearance, anatomy, clothing, and equipment. Do not add pose, expression, action, setting, camera, or lighting unless the user explicitly supplied or requested that presentation; supplied presentation remains protected rather than being stripped because the scope is narrow.

Treat clothing as garments, not the wearer: a clothing-scope request does not gain a body, character, pose, or scene. Treat an isolated asset as the asset itself, without invented stands, hands, tables, containers, or other supporting objects. Models, task templates, output ordering, and example prompts change presentation only and do not authorize any of these additions.

## CLI

Run from the `scenario-maker` skill root:

```bash
python3 scripts/character_generator.py --count 1
python3 scripts/character_generator.py --seed 7 --count 3
python3 scripts/character_generator.py --gender female --hair-color black --bangs parted --hair-style "high ponytail" --hair-length long --body-type athletic --clothes hoodie
python3 scripts/character_generator.py --format json
python3 scripts/character_generator.py --list-options
```

Supported formats:

- `both`: default; prints `Danbooru:` and `Prose:` for each character.
- `danbooru`: prints comma-separated tags only.
- `prose`: prints natural-language descriptions only.
- `json`: prints selected groups plus rendered `danbooru` and `prose`.

These are CLI formats, not the assistant's response contract. Follow `output-contracts.md`: choose the requested format, and do not expose both renderings or generator labels by default when returning one finished prompt.

## Groups

The generator chooses from these grouped character fields:

- `gender`
- `hair_color`
- `bangs`
- `hair_style`
- `hair_length`
- `breast_size`
- `skin_color`
- `tanline`
- `body_type`
- `clothes`

Friendly overrides are accepted per group, such as `black`, `parted`, `long`, `athletic`, and `hoodie`. Use `--list-options` to inspect the current canonical keys, tags, aliases, and revealing opt-in markers.

## Output Ordering

Danbooru tags produced by the randomized generator are rendered in this order:

`gender`, `hair_color`, `hair_length`, `bangs`, `hair_style`, `breast_size`, `skin_color`, `tanline`, `body_type`, `clothes`

The order organizes fields that the authorized generator run actually selected; it is not a checklist for direct character writing and does not authorize filling absent fields. It follows common tag-group structure: subject count and adult presentation first, then hair, body, skin/tanline, build, and attire. When the user names a supported image model, read its selected profile through [Model-Specific Image Prompt Profiles](model-prompts.md) and apply compatible presentation without adding character or scene facts.

## Safety Defaults

These are generator behaviors, not defaults for directly written character prompts:

- Characters are adult-presenting by default.
- Female characters include one breast-size tag by default.
- Male and nonbinary characters omit breast size.
- `--breast-size` with a non-female gender exits with an error.
- Minor-coded overrides such as `child`, `loli`, `shota`, `schoolgirl`, and `schoolboy` are rejected.
- Revealing tanline or clothing options require `--allow-revealing`; random defaults exclude those options.

## Examples

Danbooru-only character for Illustrious:

```bash
python3 scripts/character_generator.py --format danbooru --gender female --hair-color white --hair-length long --bangs blunt --hair-style twin_braids --skin-color pale --body-type petite --clothes dress
```

Deterministic batch for prompt exploration:

```bash
python3 scripts/character_generator.py --seed 42 --count 5 --format json
```
