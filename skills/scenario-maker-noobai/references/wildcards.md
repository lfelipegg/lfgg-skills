# ComfyUI Wildcards

ComfyUI wildcard files are plain `.txt` files where each non-empty line is one possible random selection.

## Save Rules

- Save wildcard files automatically when the user requests wildcard batches.
- Default directory: `./wildcards` from the current working directory.
- Use the user's path when provided.
- Create the directory if it does not exist.
- If writing files is not available, output the exact file paths and contents instead.

## File Format

Each `.txt` file must contain:

- one prompt or fragment per line
- no markdown fences
- no bullets
- no numbering
- no blank separator lines
- no trailing explanations inside the file

Good:

```text
crystal desert under twin moons
abandoned greenhouse filled with blue fog
floating market above a neon canal
```

Bad:

```text
1. crystal desert under twin moons
- abandoned greenhouse filled with blue fog

Here are more ideas:
```

## File Names

Use lowercase kebab-case names based on the wildcard role:

- `subjects.txt`
- `settings.txt`
- `styles.txt`
- `lighting.txt`
- `camera-motions.txt`
- `full-prompts.txt`

If the user asks for one wildcard file, prefer `full-prompts.txt`. If they ask for modular prompt construction, create separate role files.

## Counts

- Use the requested count when specified.
- If no count is given, create 10 lines per file.
- Keep lines distinct enough to be useful in random selection.

## Content Guidance

Apply the requested format and authorized content first. For full-prompt wildcard files, each line is a complete ready-to-use prompt and otherwise uses the selected profile's compatible dialect defaults, including any applicable prefixes. For modular wildcard files, each line is a clean fragment that can combine with other parts; fragments do not repeat host-prompt boilerplate.

Profiles do not redesign the requested fragment, file, or export scope. Follow any selected profile's documented serialization rules while retaining one physical line per entry and no surrounding offers or explanations inside files. After writing, report the saved paths and line counts.

Avoid commas at the end of lines unless the user's ComfyUI template requires them.
