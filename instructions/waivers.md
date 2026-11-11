# Standards waivers register

Approved deviations from `instructions/*.md` and `AGENTS.md`. Every waiver has an expiry (at most 12 months) and is
reviewed on or before it. An expired waiver is non-compliant until renewed or resolved.

## Active

| # | File or object | Rule deviated | Reason | Mitigation | Approved by | Approved | Expires |
|---|---|---|---|---|---|---|---|
| | | | No active waivers | | | | |

## Security waivers (need the security owner's sign-off in addition to the tech lead)

| # | File or object | Rule | Reason | Security approval | Expires |
|---|---|---|---|---|---|
| | | | No active security waivers | | |

## Expired or resolved

| # | File or object | Rule | Resolution (renewed / resolved) | Date |
|---|---|---|---|---|

## Process

1. Open the change with the deviation; add a `# waiver: <#>` comment at the site (or a row in the spec's Decision Log for design deviations).
2. Add a row above with the mitigation and an expiry.
3. Tech lead approves on the PR; security owner approves rows in the security table.
4. On expiry: renew (new approval, new date, old row moves to "Expired or resolved" as renewed) or resolve.
