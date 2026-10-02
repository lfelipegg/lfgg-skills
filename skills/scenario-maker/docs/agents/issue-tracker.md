# Legacy Scenario Maker issue tracker: GitHub

Existing issues and specs remain at https://github.com/lfelipegg/scenario-maker-skill/issues; they were not transferred during consolidation. Use this guidance only for that legacy backlog and its Wayfinder maps. Collection-wide work belongs to the collection's own repository, not this tracker. Use the authenticated GitHub CLI (`gh`).

## Conventions

Pass `--repo lfelipegg/scenario-maker-skill` to all legacy `gh issue` and `gh pr` commands. For `gh api`, pass `--hostname github.com` and use the explicit repository path. Do not infer this repository from the collection's Git remote.

- Create: `gh issue create --repo lfelipegg/scenario-maker-skill --title "..." --body-file <file>`.
- Read: `gh issue view <number> --repo lfelipegg/scenario-maker-skill --json number,title,body,state,labels,assignees,comments,url`.
- List: `gh issue list --repo lfelipegg/scenario-maker-skill --state open --json number,title,labels,assignees,url`. Filter as needed; raise limits or paginate for complete results.
- Comment: `gh issue comment <number> --repo lfelipegg/scenario-maker-skill --body-file <file>`.
- Labels: `gh issue edit <number> --repo lfelipegg/scenario-maker-skill --add-label "..."` or `--remove-label "..."`.
- Close: `gh issue close <number> --repo lfelipegg/scenario-maker-skill`.

Publishing means creating a GitHub issue. Fetching a ticket includes its comments. Refer to issues by linked titles, not bare numbers. Ensure required labels exist before applying them.

## Pull requests as a triage surface

**PRs as a request surface: no.** If enabled later, use equivalent `gh pr` commands and include only external authors with association CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR, or NONE.

Issues and PRs share a number space. For ambiguous requests, try `gh pr view` and fall back to `gh issue view`.

## Wayfinding operations

- **Map:** one issue labelled `wayfinder:map`, with Destination, Notes, Decisions so far, Not yet specified, and Out of scope. Detail lives in ticket resolutions; the map only indexes it. Open tickets are queried, not listed in the map body.
- **Child ticket:** create an issue with a Question section and a `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or `wayfinder:task` label. Attach it using `gh api --hostname github.com --method POST repos/lfelipegg/scenario-maker-skill/issues/<map-number>/sub_issues -F sub_issue_id=<child-database-id>`.
- **Database IDs:** fetch with `gh api --hostname github.com repos/lfelipegg/scenario-maker-skill/issues/<number> --jq .id`. These are not issue numbers or GraphQL node IDs.
- **Blocking:** create tickets first, then add native dependencies using `gh api --hostname github.com --method POST repos/lfelipegg/scenario-maker-skill/issues/<blocked-number>/dependencies/blocked_by -F issue_id=<blocker-database-id>`.
- **Frontier:** list children using `gh api --hostname github.com repos/lfelipegg/scenario-maker-skill/issues/<map-number>/sub_issues --paginate`. Keep open, unassigned children with zero open blockers; select the first in map order. `issue_dependencies_summary.blocked_by` counts open blockers. If absent, fetch dependencies and inspect blocker states rather than assuming zero.
- **Claim:** re-read the ticket and, if unclaimed, assign it before work using `gh issue edit <number> --repo lfelipegg/scenario-maker-skill --add-assignee @me`.
- **Resolve:** post a resolution comment, close the ticket, then append its linked title and a one-line gist to Decisions so far. Link assets rather than pasting them. Re-read shared issue bodies before editing to preserve concurrent changes.
- **Fallback:** only if native sub-issues are unavailable, use a map task list plus a Part of link in each child. Only if native dependencies are unavailable, use a Blocked by line with linked blocker titles and check their states. Authentication or permission failures do not justify switching trackers.

Wayfinder plans decisions by default. Keep implementation issues separate unless the map's Notes explicitly opt into execution.
