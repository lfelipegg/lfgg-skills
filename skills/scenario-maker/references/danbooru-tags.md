# Danbooru Tags

Use the lookup script for Danbooru-style prompts. Do not open the raw CSV files directly, especially `docs/danbooru_tags/danbooru_tags_cooccurrence.csv`.

## Lookup Commands

Run commands from the `scenario-maker` skill root:

```bash
python3 scripts/danbooru_lookup.py search "black hair" --limit 20
python3 scripts/danbooru_lookup.py tag long_hair
python3 scripts/danbooru_lookup.py aliases girl --limit 20
python3 scripts/danbooru_lookup.py related long_hair --limit 30
python3 scripts/danbooru_lookup.py suggest "solo girl with long black hair in rain" --limit 40
```

The lookup script builds `docs/danbooru_tags/danbooru_tags.sqlite` automatically when missing. Rebuild manually after CSV updates:

```bash
python3 scripts/build_danbooru_index.py --force
```

## Categories

- `0`: general
- `1`: artist
- `3`: copyright
- `4`: character
- `5`: meta

Prefer general, character, copyright, and meta tags when they are relevant to the prompt. Avoid artist tags unless the user explicitly asks for artist identity/style tagging and that use is appropriate.

## Prompt Workflow

1. Use `suggest` for rough natural-language scenes.
2. Use `search` for uncertain phrase-to-tag conversions.
3. Use `tag` to inspect a specific canonical tag and aliases.
4. Use `related` to expand a strong seed tag with common co-occurring tags.
   Admit an optional candidate only when the request's operation and scope permit that added concept. For ordinary required attributes, prefer a faithful canonical tag combination over a prose restatement; reserve the output-contract fallback for meaning the combination cannot express. Keep a literal qualifier minimal rather than repeating an already-tagged subject. Do not invent underscore labels or claim unconfirmed literals are canonical.
5. Follow `output-contracts.md` for final formatting. Canonical tags use their lower_snake_case spellings; necessary literal qualifiers stay compact within the requested tag list. Tag-like appearance does not establish canonical status: never claim an unconfirmed literal was validated. Before returning, remove repeated subject nouns from attribute fallbacks when tags already identify the subject. Respect explicit formatting and canonical-only constraints; do not normalize exact visible lettering or break required relational phrases into disconnected tags.
