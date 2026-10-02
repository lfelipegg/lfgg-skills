#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass


MINOR_CODED_TERMS = {
    "child",
    "kid",
    "minor",
    "teen",
    "teenager",
    "young",
    "loli",
    "shota",
    "schoolgirl",
    "schoolboy",
    "student",
    "middle_schooler",
    "elementary_schooler",
}


@dataclass(frozen=True)
class Option:
    key: str
    label: str
    tags: tuple[str, ...]
    prose: str
    aliases: tuple[str, ...] = ()
    revealing: bool = False


GENDERS = {
    "female": Option(
        "female",
        "female",
        ("1girl", "mature_female"),
        "an adult woman",
        aliases=("woman", "girl", "f"),
    ),
    "male": Option(
        "male",
        "male",
        ("1boy", "mature_male"),
        "an adult man",
        aliases=("man", "boy", "m"),
    ),
    "nonbinary": Option(
        "nonbinary",
        "nonbinary",
        ("1other", "androgynous"),
        "an adult androgynous person",
        aliases=("nb", "androgynous", "other", "1other"),
    ),
}


HAIR_COLORS = {
    "black": Option("black", "black hair", ("black_hair",), "black hair", aliases=("dark", "raven")),
    "brown": Option("brown", "brown hair", ("brown_hair",), "brown hair", aliases=("brunette",)),
    "blonde": Option("blonde", "blonde hair", ("blonde_hair",), "blonde hair", aliases=("blond", "yellow")),
    "red": Option("red", "red hair", ("red_hair",), "red hair", aliases=("ginger", "auburn")),
    "white": Option("white", "white hair", ("white_hair",), "white hair", aliases=("silver",)),
    "blue": Option("blue", "blue hair", ("blue_hair",), "blue hair"),
    "green": Option("green", "green hair", ("green_hair",), "green hair"),
    "pink": Option("pink", "pink hair", ("pink_hair",), "pink hair"),
    "purple": Option("purple", "purple hair", ("purple_hair",), "purple hair"),
}


BANGS = {
    "asymmetrical": Option("asymmetrical", "asymmetrical bangs", ("asymmetrical_bangs",), "asymmetrical bangs"),
    "blunt": Option("blunt", "blunt bangs", ("blunt_bangs",), "blunt bangs"),
    "crossed": Option("crossed", "crossed bangs", ("crossed_bangs",), "crossed bangs"),
    "diagonal": Option("diagonal", "diagonal bangs", ("diagonal_bangs",), "diagonal bangs"),
    "long": Option("long", "long bangs", ("long_bangs",), "long bangs"),
    "parted": Option("parted", "parted bangs", ("parted_bangs",), "parted bangs"),
    "swept": Option("swept", "swept bangs", ("swept_bangs",), "swept bangs", aliases=("side swept", "sideswept")),
}


HAIR_STYLES = {
    "hair_bun": Option("hair_bun", "hair bun", ("hair_bun",), "a hair bun", aliases=("bun",)),
    "braided_bun": Option("braided_bun", "braided bun", ("braided_bun",), "a braided bun"),
    "single_hair_bun": Option("single_hair_bun", "single hair bun", ("single_hair_bun",), "a single hair bun"),
    "double_bun": Option("double_bun", "double bun", ("double_bun",), "double buns", aliases=("double", "double hair bun")),
    "cone_hair_bun": Option("cone_hair_bun", "cone hair bun", ("cone_hair_bun",), "a cone-shaped hair bun"),
    "front_braid": Option("front_braid", "front braid", ("front_braid",), "a front braid"),
    "side_braid": Option("side_braid", "side braid", ("side_braid",), "a side braid"),
    "french_braid": Option("french_braid", "French braid", ("french_braid",), "a French braid", aliases=("french",)),
    "crown_braid": Option("crown_braid", "crown braid", ("crown_braid",), "a crown braid"),
    "single_braid": Option("single_braid", "single braid", ("single_braid",), "a single braid"),
    "multiple_braids": Option("multiple_braids", "multiple braids", ("multiple_braids",), "multiple braids"),
    "twin_braids": Option("twin_braids", "twin braids", ("twin_braids",), "twin braids"),
    "tri_braids": Option("tri_braids", "tri braids", ("tri_braids",), "tri braids"),
    "quad_braids": Option("quad_braids", "quad braids", ("quad_braids",), "quad braids"),
    "low_twin_braids": Option("low_twin_braids", "low twin braids", ("low_twin_braids",), "low twin braids"),
    "pigtails": Option("pigtails", "pigtails", ("pigtails",), "pigtails"),
    "ponytail": Option("ponytail", "ponytail", ("ponytail",), "a ponytail"),
    "folded_ponytail": Option("folded_ponytail", "folded ponytail", ("folded_ponytail",), "a folded ponytail"),
    "front_ponytail": Option("front_ponytail", "front ponytail", ("front_ponytail",), "a front ponytail"),
    "high_ponytail": Option("high_ponytail", "high ponytail", ("high_ponytail",), "a high ponytail"),
    "short_ponytail": Option("short_ponytail", "short ponytail", ("short_ponytail",), "a short ponytail"),
    "side_ponytail": Option("side_ponytail", "side ponytail", ("side_ponytail",), "a side ponytail"),
    "split_ponytail": Option("split_ponytail", "split ponytail", ("split_ponytail",), "a split ponytail"),
}


HAIR_LENGTHS = {
    "short": Option("short", "short hair", ("short_hair",), "short hair"),
    "medium": Option("medium", "medium hair", ("medium_hair",), "medium-length hair", aliases=("medium length",)),
    "long": Option("long", "long hair", ("long_hair",), "long hair"),
    "very_long": Option("very_long", "very long hair", ("very_long_hair",), "very long hair", aliases=("very long",)),
}


BREAST_SIZES = {
    "flat": Option("flat", "flat chest", ("flat_chest",), "a flat chest", aliases=("flat chest",)),
    "small": Option("small", "small breasts", ("small_breasts",), "small breasts"),
    "medium": Option("medium", "medium breasts", ("medium_breasts",), "medium breasts", aliases=("average",)),
    "large": Option("large", "large breasts", ("large_breasts",), "large breasts", aliases=("big",)),
    "huge": Option("huge", "huge breasts", ("huge_breasts",), "huge breasts"),
}


SKIN_COLORS = {
    "pale": Option("pale", "pale skin", ("pale_skin",), "pale skin"),
    "tan": Option("tan", "tan skin", ("tan",), "tan skin", aliases=("tanned",)),
    "dark": Option("dark", "dark skin", ("dark_skin",), "dark skin"),
    "very_dark": Option("very_dark", "very dark skin", ("very_dark_skin",), "very dark skin", aliases=("very dark",)),
}


TANLINES = {
    "none": Option("none", "no tanline", (), "no visible tanline"),
    "tanlines": Option("tanlines", "tanlines", ("tanlines",), "visible tanlines"),
    "bikini_tan": Option("bikini_tan", "bikini tan", ("bikini_tan",), "bikini tanlines", revealing=True),
    "one-piece_tan": Option("one-piece_tan", "one-piece tan", ("one-piece_tan",), "one-piece swimsuit tanlines", revealing=True),
    "shirt_tan": Option("shirt_tan", "shirt tan", ("shirt_tan",), "shirt tanlines"),
    "shorts_tan": Option("shorts_tan", "shorts tan", ("shorts_tan",), "shorts tanlines"),
    "pasties_tan": Option("pasties_tan", "pasties tan", ("pasties_tan",), "pasties tanlines", revealing=True),
    "slingshot_tan": Option("slingshot_tan", "slingshot tan", ("slingshot_tan",), "slingshot tanlines", revealing=True),
    "revealing_tanlines": Option("revealing_tanlines", "revealing tanlines", ("revealing_tanlines",), "revealing tanlines", revealing=True),
    "presenting_tanlines": Option("presenting_tanlines", "presenting tanlines", ("presenting_tanlines",), "presenting tanlines", revealing=True),
    "shibari_tan": Option("shibari_tan", "shibari tan", ("shibari_tan",), "shibari tanlines", revealing=True),
    "farmer_tan": Option("farmer_tan", "farmer tan", ("farmer_tan",), "farmer tanlines"),
    "double_tanline": Option("double_tanline", "double tanline", ("double_tanline",), "double tanlines"),
}


BODY_TYPES = {
    "petite": Option("petite", "petite body", ("petite",), "a petite build"),
    "athletic": Option("athletic", "athletic body", ("toned", "abs"), "an athletic, toned build with visible abs"),
    "toned": Option("toned", "toned body", ("toned",), "a toned build"),
    "muscular": Option("muscular", "muscular body", ("muscular",), "a muscular build"),
    "curvy": Option("curvy", "curvy body", ("curvy",), "a curvy build"),
    "wide_hips": Option("wide_hips", "wide hips", ("wide_hips",), "wide hips", aliases=("wide hips",)),
    "thick_thighs": Option("thick_thighs", "thick thighs", ("thick_thighs",), "thick thighs", aliases=("thick thighs",)),
    "skinny": Option("skinny", "skinny body", ("skinny",), "a skinny build"),
}


CLOTHES = {
    "hoodie": Option("hoodie", "hoodie", ("hoodie",), "a hoodie"),
    "casual": Option("casual", "casual clothes", ("casual_clothes",), "casual clothes"),
    "shirt": Option("shirt", "shirt", ("shirt",), "a shirt"),
    "sweater": Option("sweater", "sweater", ("sweater",), "a sweater"),
    "dress": Option("dress", "dress", ("dress",), "a dress"),
    "jacket": Option("jacket", "jacket", ("jacket",), "a jacket"),
    "suit": Option("suit", "suit", ("suit",), "a suit"),
    "uniform": Option("uniform", "uniform", ("uniform",), "a uniform"),
    "sportswear": Option("sportswear", "sportswear", ("sportswear",), "sportswear"),
    "bikini": Option("bikini", "bikini", ("bikini",), "a bikini", revealing=True),
    "swimsuit": Option("swimsuit", "swimsuit", ("swimsuit",), "a swimsuit", revealing=True),
}


GROUPS = {
    "gender": GENDERS,
    "hair_color": HAIR_COLORS,
    "bangs": BANGS,
    "hair_style": HAIR_STYLES,
    "hair_length": HAIR_LENGTHS,
    "breast_size": BREAST_SIZES,
    "skin_color": SKIN_COLORS,
    "tanline": TANLINES,
    "body_type": BODY_TYPES,
    "clothes": CLOTHES,
}


def normalize(value: str) -> str:
    return "_".join(value.strip().casefold().replace("-", "_").split())


def contains_minor_coded_term(value: str) -> bool:
    normalized = normalize(value)
    parts = set(normalized.split("_"))
    return normalized in MINOR_CODED_TERMS or bool(parts & MINOR_CODED_TERMS)


def alias_map(options: dict[str, Option]) -> dict[str, Option]:
    aliases = {}
    for option in options.values():
        keys = {option.key, option.label, option.prose, *option.tags, *option.aliases}
        for key in keys:
            aliases[normalize(key)] = option
    return aliases


def resolve_option(group: str, value: str, allow_revealing: bool) -> Option:
    if contains_minor_coded_term(value):
        raise ValueError(f"{group} value {value!r} is minor-coded and is not allowed")
    aliases = alias_map(GROUPS[group])
    normalized = normalize(value)
    option = aliases.get(normalized)
    if option is None:
        valid = ", ".join(sorted(GROUPS[group]))
        raise ValueError(f"unknown {group} value {value!r}; valid values: {valid}")
    if option.revealing and not allow_revealing:
        raise ValueError(f"{group} value {value!r} requires --allow-revealing")
    return option


def random_option(options: dict[str, Option], rng: random.Random, allow_revealing: bool) -> Option:
    choices = [option for option in options.values() if allow_revealing or not option.revealing]
    return rng.choice(choices)


def option_to_json(option: Option | None):
    if option is None:
        return None
    payload = {
        "key": option.key,
        "label": option.label,
        "tags": list(option.tags),
        "prose": option.prose,
    }
    if len(option.tags) == 1:
        payload["tag"] = option.tags[0]
    return payload


def render_danbooru(fields: dict[str, Option | None]) -> str:
    ordered_groups = [
        "gender",
        "hair_color",
        "hair_length",
        "bangs",
        "hair_style",
        "breast_size",
        "skin_color",
        "tanline",
        "body_type",
        "clothes",
    ]
    tags: list[str] = []
    for group in ordered_groups:
        option = fields.get(group)
        if option is None:
            continue
        for tag in option.tags:
            if tag and tag not in tags:
                tags.append(tag)
    return ", ".join(tags)


def render_prose(fields: dict[str, Option | None]) -> str:
    length = fields["hair_length"].label.removesuffix(" hair")
    color = fields["hair_color"].label.removesuffix(" hair")
    hair_phrase = f"{length} {color} hair"
    sentences = [
        (
            f"{fields['gender'].prose.capitalize()} with {hair_phrase}, "
            f"{fields['bangs'].prose}, and {fields['hair_style'].prose}."
        )
    ]
    traits = []
    breast_size = fields.get("breast_size")
    if breast_size is not None:
        traits.append(breast_size.prose)
    traits.extend([fields["skin_color"].prose, fields["body_type"].prose])
    sentences.append(f"They have {', '.join(traits)} and wear {fields['clothes'].prose}.")

    tanline = fields.get("tanline")
    if tanline is not None and tanline.key != "none":
        sentences.append(f"They also have {tanline.prose}.")
    return " ".join(sentences)


def generate_character(args, rng: random.Random) -> dict:
    gender = (
        resolve_option("gender", args.gender, args.allow_revealing)
        if args.gender
        else random_option(GENDERS, rng, args.allow_revealing)
    )

    if args.breast_size and gender.key != "female":
        raise ValueError("--breast-size can only be used with --gender female")

    fields: dict[str, Option | None] = {
        "gender": gender,
        "hair_color": resolve_option("hair_color", args.hair_color, args.allow_revealing)
        if args.hair_color
        else random_option(HAIR_COLORS, rng, args.allow_revealing),
        "bangs": resolve_option("bangs", args.bangs, args.allow_revealing)
        if args.bangs
        else random_option(BANGS, rng, args.allow_revealing),
        "hair_style": resolve_option("hair_style", args.hair_style, args.allow_revealing)
        if args.hair_style
        else random_option(HAIR_STYLES, rng, args.allow_revealing),
        "hair_length": resolve_option("hair_length", args.hair_length, args.allow_revealing)
        if args.hair_length
        else random_option(HAIR_LENGTHS, rng, args.allow_revealing),
        "skin_color": resolve_option("skin_color", args.skin_color, args.allow_revealing)
        if args.skin_color
        else random_option(SKIN_COLORS, rng, args.allow_revealing),
        "body_type": resolve_option("body_type", args.body_type, args.allow_revealing)
        if args.body_type
        else random_option(BODY_TYPES, rng, args.allow_revealing),
        "clothes": resolve_option("clothes", args.clothes, args.allow_revealing)
        if args.clothes
        else random_option(CLOTHES, rng, args.allow_revealing),
        "tanline": resolve_option("tanline", args.tanline, args.allow_revealing)
        if args.tanline
        else random_option(TANLINES, rng, args.allow_revealing),
        "breast_size": None,
    }

    if gender.key == "female":
        fields["breast_size"] = (
            resolve_option("breast_size", args.breast_size, args.allow_revealing)
            if args.breast_size
            else random_option(BREAST_SIZES, rng, args.allow_revealing)
        )

    character = {group: option_to_json(fields[group]) for group in GROUPS}
    character["danbooru"] = render_danbooru(fields)
    character["prose"] = render_prose(fields)
    return character


def list_options() -> str:
    lines = []
    for group, options in GROUPS.items():
        lines.append(f"{group}:")
        for option in options.values():
            aliases = f" aliases={', '.join(option.aliases)}" if option.aliases else ""
            marker = " [requires --allow-revealing]" if option.revealing else ""
            tag_text = ", ".join(option.tags) if option.tags else "no tag"
            lines.append(f"  {option.key}: {tag_text}{aliases}{marker}")
    return "\n".join(lines)


def render_output(characters: list[dict], output_format: str) -> str:
    if output_format == "json":
        return json.dumps({"characters": characters}, indent=2) + "\n"
    if output_format == "danbooru":
        return "\n".join(character["danbooru"] for character in characters) + "\n"
    if output_format == "prose":
        return "\n".join(character["prose"] for character in characters) + "\n"

    blocks = []
    for index, character in enumerate(characters, start=1):
        blocks.append(
            "\n".join(
                [
                    f"Character {index}",
                    f"Danbooru: {character['danbooru']}",
                    f"Prose: {character['prose']}",
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate adult-presenting character prompts.")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--format", choices=("both", "danbooru", "prose", "json"), default="both")
    parser.add_argument("--list-options", action="store_true")
    parser.add_argument("--allow-revealing", action="store_true")
    parser.add_argument("--gender")
    parser.add_argument("--hair-color")
    parser.add_argument("--bangs")
    parser.add_argument("--hair-style")
    parser.add_argument("--hair-length")
    parser.add_argument("--skin-color")
    parser.add_argument("--body-type")
    parser.add_argument("--clothes")
    parser.add_argument("--breast-size")
    parser.add_argument("--tanline")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_options:
        print(list_options())
        return 0
    if args.count < 1:
        parser.error("--count must be at least 1")

    rng = random.Random(args.seed)
    try:
        characters = [generate_character(args, rng) for _ in range(args.count)]
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")

    sys.stdout.write(render_output(characters, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
