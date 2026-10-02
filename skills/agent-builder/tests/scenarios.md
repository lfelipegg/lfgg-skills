# Behavioral acceptance scenarios

Run these after substantive changes to the skill. They test decisions and actual
outputs; the skill validator and Markdown checks do not prove these behaviors.
No application, dependencies, or test framework is required.

## Fixture setup

Run this Python 3 block to create disposable repositories. It prints the root
path. Every case has a `project/` directory and a separate `request.txt`; supply
only the candidate skill, project, and request to the executing agent, not the
rubric below. Cases 06, 07, 09, and 10 include sequential follow-up requests.

```python
from pathlib import Path
import json
import subprocess
import tempfile

root = Path(tempfile.mkdtemp(prefix='agent-builder-eval-'))

def case(number, files, request, followup=None):
    folder = root / number
    project = folder / 'project'
    project.mkdir(parents=True)
    for name, text in files.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    subprocess.run(['git', 'init', '-q', str(project)], check=True)
    (folder / 'request.txt').write_text(request, encoding='utf-8')
    if followup:
        (folder / 'followup.txt').write_text(followup, encoding='utf-8')
    (folder / 'before.json').write_text(json.dumps(files), encoding='utf-8')

case('01', {
    'AGENTS.md': '# Guide\n\nRun `npm test` for unit tests.\nKeep public API names stable.\n',
    'package.json': '{"scripts":{"test:unit":"node --test"}}\n',
}, 'Update only AGENTS.md to replace the stale unit-test command with the command defined in package.json. Apply the edit.')

case('02', {
    'AGENTS.md': '# Root\nUse the root test command.\nKeep shared API compatibility.\n',
    'apps/web/AGENTS.md': '# Local\nUse the local test command.\n',
    'apps/web/AGENTS.override.md': '# Override\nUse the override test command.\n',
}, 'Audit instruction discovery for Codex started in apps/web, with this project as its Git root. Its separately configured global guidance is empty and no fallback filenames are configured. Report the applicable sources and shadowed files. Findings only; do not edit files.')

case('03', {
    'AGENTS.md': '# Guide\n' + ('\nKeep edits scoped.\n' * 110) + '\nBefore changing storage, read [storage rules](docs/conventions/storage.md).\nNever log customer tokens.\nKeep legacy export names stable.\nValidate uploaded records server-side.\n',
    'docs/conventions/storage.md': '# Storage\nNever rewrite archived records.\n',
}, 'Shorten AGENTS.md to the default budget, preserving unique constraints and the existing documentation layout. Apply the changes.')

case('04', {
    'AGENTS.md': '# Guide\nCurrent code takes precedence over specs.\n',
    'docs/specs/input.md': '# Input\nReject empty input before storage.\n',
    'input.py': 'def accept(value):\n    return True\n',
}, 'Audit AGENTS.md against the input spec and implementation. Report what needs changing and why. Do not edit any files.')

case('05', {
    'README.md': '# Sample\nThe parent agent coordinates all reviews.\nUI and API are separate workstreams.\n',
    'src/ui/view.js': 'export const title = "Hello";\n',
    'src/api/input.js': 'export const accept = value => Boolean(value);\n',
}, 'Create portable plans for a UI reviewer and an API reviewer. Both are review-only and the parent coordinates. Explain how the parent uses the plans. Do not install agents or run reviewers.')

case('06', {}, 'Create a fast first draft of AGENTS.md for this empty repository.',
     'Now finalize the guide using only the facts already available. Keep it minimal and omit unsupported optional details. Apply the revision.')

lines = ['# Module policy', '', 'The following output names are public contracts.']
lines += [f'- Preserve public output field field_{n:03d}.' for n in range(1, 188)]
assert len(lines) == 190
case('07', {'AGENTS.md': '\n'.join(lines) + '\n'},
     'Review this 190-line guide for size only. Keep all public field constraints and keep it in one file; do not rewrite it if it fits.',
     'Use a 240-line cap for this guide. Append public field preservation rules for field_188 through field_217. Keep all earlier constraints and keep one file. Apply the change.')

case('08', {
    'AGENTS.md': '# Guide\nNever log customer tokens.\nPreserve public export names.\nFor TypeScript, use explicit return types on exported functions.\nFor TypeScript, prohibit non-null assertions at API boundaries.\nTests must cover rejected input and must not contact live services.\nRun npm test for tests.\nBuilds must keep source maps enabled.\nRun npm run build for builds.\nAuthentication handlers live in src/old-auth.ts.\nBefore storage changes, read [archive rules](docs/archive.md).\n',
    'docs/archive.md': '# Archive\nNever rewrite archived records.\n',
    'package.json': '{"scripts":{"test":"vitest run --config vitest.config.ts","build":"node esbuild.config.mjs"},"devDependencies":{"typescript":"*","vitest":"*","esbuild":"*"}}\n',
    'tsconfig.json': '{"compilerOptions":{"strict":true}}\n',
    'vitest.config.ts': 'export default {test: {environment: "node"}};\n',
    'esbuild.config.mjs': 'import {build} from "esbuild";\nawait build({entryPoints:["src/auth.ts"],outdir:"dist",sourcemap:true});\n',
    'src/auth.ts': 'export function authenticate(token: string): boolean { return Boolean(token); }\n',
}, 'Refactor AGENTS.md so language, testing, and build guidance are separate and discoverable when relevant. Preserve unique constraints and useful existing docs. Remove stale navigation. Apply the changes without installing dependencies or executing builds/tests.')

case('09', {
    'AGENTS.md': '# Guide\nNever log customer tokens.\nRun npm test for unit tests.\nTypeScript exports must declare return types.\nTests must not contact live services.\n',
    'README.md': '# Tool\nFor contributor guidance see [handbook](handbook/craft.md).\n',
    'handbook/craft.md': '# Craft\nTypeScript exports must declare return types.\nFor test changes read [checks](quality/checks.md).\n',
    'handbook/quality/checks.md': '# Checks\nTests must not contact live services.\nUse the unit script in [package manifest](../../package.json).\n',
    'package.json': '{"scripts":{"test:unit":"node --test"}}\n',
}, 'Audit AGENTS.md for stale commands and opportunities to separate specialized guidance. Report findings only; do not edit files.',
     'First update only the stale unit-test command in AGENTS.md. Do not reorganize anything. Report that diff. Then refactor the guide to use existing specialized documentation, preserving constraints. Apply both steps and report their changes separately.')

case('10', {
    'README.md': '# Parcel Inspector\nA command-line tool for inspecting parcel records.\n',
}, 'Plan a minimal AGENTS.md for this repository. Do not edit files yet. Keep the plan readable and actionable, with verification and unresolved questions only when needed.',
     'Create that minimal guide using only established facts. Show its initial content in your response. Then add a planning policy requiring concise readable plans with actions, verification, and unresolved questions at the end when present; resolve blocking questions before finalizing executable plans. Apply this policy and report the final content too.')

print(root)
```

## Execution protocol

Use a fresh isolated session per case, with the candidate `SKILL.md` and its
referenced material available read-only. Set the working directory to that
case's `project/`. Do not let test executions edit this skill repository or
other fixtures, install packages, access live services, or read the plan/rubric.
For cases 06, 07, 09, and 10, give `followup.txt` only after the first response and retain
that case's conversation state. If only limited slots are available, run cases
in successive fresh sessions rather than merging their conversation histories.

Capture responses and before/after files outside the fixture project, excluding
`.git` metadata from comparison. Audit-only cases must have no target changes.
Do not run fixture deployment or install commands. A copied portable plan does
not need a live worker to validate that its contract and handoff are complete.

## Reviewer rubric

| Case | Observable success | Failure examples |
| --- | --- | --- |
| 01: Narrow edit | Only `npm test` becomes `npm run test:unit`; public API rule and package manifest survive. | Repeated approval, unrelated interview, extra docs or product edits. |
| 02: Effective discovery | Identifies root plus nested override as expected sources, local file as shadowed; shared root compatibility remains applicable. Distinguishes inspected expected chain from actual session loading. | Edits audit targets, claims all three files load, or claims native-session verification without running one. |
| 03: Preservation | All unique constraints survive; storage reading trigger and existing guidance remain useful; output fits 200 lines. | Lost token/privacy, validation, export, or archive rule; invented docs layout. |
| 04: Conflict | Identifies code/spec discrepancy and rejects automatic code precedence as a resolution. | Blesses current acceptance behavior or edits audit targets. |
| 05: Portable plans | Two review-only contracts with inputs, no edit ownership, verification limits, output, and explicit parent handoff. | Installed configuration, live dispatch, unnecessary orchestrator, or undefined invocation. |
| 06: Draft/final | Draft isolates any consequential unknowns; final omits unsupported commands, skill slots, and assumptions. No empty scaffolding. | Guessed package commands, final placeholder slots, or unanswered questions treated as policy. |
| 07: Size override | First guide remains one file at 190 lines; follow-up preserves all 217 fields under the 240-line user cap without splitting. | Automatic split at 180/200, ignored cap, or lost fields. |
| 08: Topic extraction | Preserves every unique rule; creates useful language/testing/build docs with root reading triggers, a language-to-testing link, and valid relative configuration references. Removes stale auth inventory; retains archive pointer/rule. | Lost safeguards; copied stale path; invented conventions; broken links; empty files; unnecessary nested guides or planning policy. |
| 09: Existing discovery and scope | Audit leaves files unchanged and finds handbook topics through content/links. First follow-up step changes only the command; second reuses handbook docs with useful triggers and preserves constraints. | Conventional duplicate docs, premature extraction, esbuild invented without evidence, or unrelated changes. |
| 10: Planning and sparse evidence | Initial plan covers actions and verification without edits or invented blockers. Initial guide uses known purpose without fabricated tools, empty docs, or planning policy. Explicit follow-up adds the requested policy. | Mandatory commits/approval, grammar that obscures actions, guessed commands, automatic topic scaffolding, or unrequested planning rules. |

Record pass/fail per case with evidence and any correction/retest. A manual
walkthrough is useful when fresh execution is unavailable, but label it as a
walkthrough rather than a behavioral pass. These scenarios validate generated
guidance; they do not establish native runtime loading or installation support.

## Structural checks

Run the installed skill-creator validator against the candidate directory when
available (use `python3`), plus `git diff --check` when Git is available;
otherwise compare before/after files and inspect whitespace. Check local reference links
outside fenced illustrative output and line counts inside each generated-guide
fence. Compare unique constraints against the pre-edit inventory for large
rewrites. Do not add exact-heading tests or regex suites that mirror the prose.
