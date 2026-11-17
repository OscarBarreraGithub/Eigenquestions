# Final public-origin acceptance

Prepared on 2026-11-17; **not executed evidence**. Run after the accepted atlas and
matching runtime are deployed. The local package must byte-match the public
manifest. This test uses isolated Slurm Chromium, never the owner's Chrome.

Run `public-bridge-acceptance.py` twice with separate output directories and
`--permission-mode default` / `--permission-mode consent`. Each invocation creates
a new nonpersistent context and authenticated loopback companion. Preserve both
outcomes; a consent-enabled success cannot be relabeled default-policy success.

The consent case calls
`context.grant_permissions(['local-network-access'], origin='https://eigenquestions.com')`.
This documented API simulates ordinary user consent for that exact origin inside
the isolated context. It does not demonstrate clicking a native permission prompt
or granting permission in the owner's browser. There are no disabled security
flags, request interception, proxy, wildcard origin, or address-space overrides.
Permission states are recorded before and after, including granular loopback state
when supported. The page initiates attachment through its Connect button.

[Playwright's API](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-grant-permissions)
documents origin-scoped grants and browser/version-dependent support.
[Chrome's current guidance](https://developer.chrome.com/docs/modern-web-guidance/guides/security/local-network-access)
distinguishes local and loopback permissions and requires secure initiating pages.
Existing CORS and companion bearer authentication remain enforced. A permission
grant does not replace either check.

The installed Slurm driver is Playwright 1.58.0. Its `crBrowser.js` SHA-256 is
`7d21bfbb273977605b469b8c249188b919d69784c3c56fd78721e1d6c8d0951b`.
Its normal grant implementation maps `local-network-access` to Chromium's
`localNetworkAccess`, `localNetwork`, and `loopbackNetwork` names, with the exact
origin and isolated browser-context ID. This was inspected read-only; no browser
was launched for that check. The test contacts the authorized loopback companion,
not other devices on a local network.

Each receipt checks the public compact destination URL independently first, the
exact public manifest hash, MCP → SSE → exact render acknowledgement, matching
browser/agent source IDs, static discovery and lazy source-context decoding.
Permission/network failure keeps its real UI message and compact-link success as
separate facts. Tokens stay out of reports/screenshots; temporary companions and
contexts are disposed afterward. Successful local HTTP QA10 is prior evidence,
not a substitute for these HTTPS cases.
