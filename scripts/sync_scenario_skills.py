#!/usr/bin/env python3
"""Synchronize committed Scenario Maker resources; never run during installation."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys

GENERIC = "scenario-maker"
PROFILES = {
    "scenario-maker-sdxl": "sdxl.md",
    "scenario-maker-krea-2": "krea-2.md",
    "scenario-maker-illustrious": "illustrious.md",
    "scenario-maker-noobai": "noobai.md",
    "scenario-maker-pony": "pony-v6.md",
    "scenario-maker-wan": "wan.md",
    "scenario-maker-minimax-h3": "minimax-h3.md",
}
GUIDES = (
    "minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_base_en.md",
    "minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md",
)
SHARED = (
    "CONTEXT.md",
    "references/routing.md",
    "references/output-contracts.md",
    "references/scene-composition.md",
    "references/constraints-and-revisions.md",
    "references/prompt-types.md",
    "references/video-prompts.md",
    "references/characters.md",
    "references/danbooru-tags.md",
    "references/wildcards.md",
    "scripts/character_generator.py",
    "scripts/danbooru_lookup.py",
    "scripts/build_danbooru_index.py",
    "docs/danbooru_tags/danbooru_tags.csv",
    "docs/danbooru_tags/danbooru_tags_cooccurrence.csv",
)


class SyncError(ValueError):
    pass


def mapping():
    pairs = []
    for skill, profile in PROFILES.items():
        for relative in SHARED:
            pairs.append((Path("skills") / GENERIC / relative, Path("skills") / skill / relative))
        owned = [profile] + (list(GUIDES) if skill == "scenario-maker-minimax-h3" else [])
        for relative in owned:
            pairs.append((Path("skills") / skill / "references/models" / relative,
                          Path("skills") / GENERIC / "references/models" / relative))
    return pairs


def managed_path(root, relative):
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise SyncError(f"unsafe managed path: {relative}")
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise SyncError(f"symlinked managed path: {current}")
    try:
        current.resolve().relative_to(root)
    except ValueError as exc:
        raise SyncError(f"managed path escapes root: {current}") from exc
    return current


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate(root, pairs):
    sources, destinations = set(), set()
    validated = []
    for source_name, destination_name in pairs:
        source = managed_path(root, source_name)
        destination = managed_path(root, destination_name)
        if destination in destinations:
            raise SyncError(f"duplicate destination ownership: {destination}")
        sources.add(source)
        destinations.add(destination)
        if not source.is_file():
            raise SyncError(f"missing source file: {source}")
        if destination.exists() and not destination.is_file():
            raise SyncError(f"destination is not a file: {destination}")
        # Reject an unusable ancestor before writing any other destination.
        ancestor = destination.parent
        while ancestor != root:
            if ancestor.exists() and not ancestor.is_dir():
                raise SyncError(f"destination parent is not a directory: {ancestor}")
            ancestor = ancestor.parent
        validated.append((source, destination))
    if sources & destinations:
        raise SyncError(f"source/destination aliasing: {sorted(sources & destinations)[0]}")
    source_inodes = {(p.stat().st_dev, p.stat().st_ino): p for p in sources}
    destination_inodes = {}
    for _, destination in validated:
        if not destination.exists():
            continue
        stat = destination.stat()
        inode = (stat.st_dev, stat.st_ino)
        if inode in source_inodes:
            raise SyncError(f"source/destination aliasing: {destination} and {source_inodes[inode]}")
        if inode in destination_inodes:
            raise SyncError(f"destination aliasing: {destination} and {destination_inodes[inode]}")
        destination_inodes[inode] = destination
    for skill, profile in PROFILES.items():
        directory = managed_path(root, Path("skills") / skill / "references/models")
        allowed = {profile}
        if skill == "scenario-maker-minimax-h3":
            allowed.update(GUIDES)
            allowed.add("minimax_h3")
        if directory.exists():
            for path in directory.rglob("*"):
                relative = path.relative_to(directory).as_posix()
                if path.is_symlink() or relative not in allowed:
                    raise SyncError(f"unexpected model resource: {path}")
    return validated


def synchronize(root, check=False):
    pairs = validate(root, mapping())
    # Hash every source and existing destination before the first mutation.
    changes = []
    for source, destination in pairs:
        source_hash = digest(source)
        if not destination.exists() or digest(destination) != source_hash:
            changes.append((source, destination))
    if check:
        for _, destination in changes:
            print(f"drift: {destination.relative_to(root).as_posix()}")
        return 1 if changes else 0
    for source, destination in changes:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        print(f"changed: {destination.relative_to(root).as_posix()}")
    if not changes:
        print("synchronized: no changes")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.absolute()
    try:
        if root.is_symlink() or root.resolve() != root:
            raise SyncError(f"symlinked collection root: {root}")
        if not root.is_dir():
            raise SyncError(f"missing collection root: {root}")
        return synchronize(root, args.check)
    except (OSError, SyncError) as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
