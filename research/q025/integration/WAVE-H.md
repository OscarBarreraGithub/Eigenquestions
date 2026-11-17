# Wave H — captured parent revisions and independent acceptance design

CLI and MCP now carry the agent's pre-interpretation revision through the existing
HTTP `If-Match` guard. CLI uses `--expected-revision N`; MCP navigation and import
use `expectedRevision`. Zero works. The shared runtime checks this parent before
preparation and preserves its second check before asynchronous work commits.
Omission remains explicit legacy behavior. The portable skill requires the guard
for all visible changes, including import, Back and replay.

A conflict preserves the newer state and the caller's action/import data. CLI
returns a nonzero structured conflict; MCP returns `isError` with a compact current
state. Neither restamps or retries. Read-only operations and scientific/session
identity remain unchanged.

Validation: `npm run build`, all **80 tests**, and `npm run check:site` passed.
Four new integration tests cover stale interpretation parents, zero, action/import
races during preparation, actual CLI/stdio-MCP transport, preserved drafts and
Back/replay. Existing lazy atlas, SSE and HTTP guard tests also pass. The original
test fixture initially omitted its corpus identity; that fixture was corrected
before this passing receipt. No corresponding runtime defect was inferred.

QA15 job **61499582** ran on isolated Slurm Chromium 145.0.7632.6 with 2 CPU,
8 GB and an 8-minute limit. It completed 0:0 in 20 seconds. Three browser checks
passed: guarded MCP revision zero rendered and acknowledged revision 1; a browser
change committed revision 2 and stale MCP action/MCP import/CLI import preserved
it and the original file; a distinct new Back request rendered revision 3 and the
exact prior state. No page errors. The inspected screenshot retains the connected
status and collapsed long disclosures. This is synthetic protocol regression
evidence, not accepted-science or independent-agent proof.

QA14's immutable archive was reused with a checksummed current-code overlay.
The combined content manifest pins all 608 inputs. No old QA manifest or failure
evidence was edited. Public evidence scanning found no token-bearing URL; the
companion stdout was suppressed and its temporary connection file removed.

[The independent acceptance plan](agent-acceptance-plan.md) is ready for root's
future accepted-data gate: fresh-context Astra agents choose their own CLI calls,
the existing browser observer checks exact render acknowledgements, and alternative
routes must converge on the same scoped question. KK→DM and two independent physics
cases are included. No fresh agent or final-data job was launched for this plan.

The previously prepared public HTTPS harness now supplies a captured revision and
uses DOMContentLoaded with explicit readiness. Those harness-only changes were
made after QA15 and are syntax-checked but remain **unexecuted** until the actual
accepted package is deployed. Default policy, scoped simulated consent and a fresh
agent's public-origin update retain separate outcome labels. The owner's Chrome
was neither accessed nor modified. Root owns release and the final content/UX gate.
