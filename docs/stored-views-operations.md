# Stored contextual views: service and activation

The implementation stores an already computed scientific view. All retrieval,
grouping, labeling, layout and model work happens in the agent or browser. The
Worker validates bounded JSON, reserves capacity, and stores the exact uploaded
bytes in R2. A small SQLite Durable Object coordinates upload budgets only.
Static assets and the numerical engine do not call that coordinator.

The default deployment is safe before storage is provisioned: static assets
work, file import/export works, and `/api/views` reports HTTP 503
`storage_unavailable`. The activation profile is
[`wrangler.views.toml`](../wrangler.views.toml). Implementation and local tests
are not evidence that the public storage service is active.

## HTTP contract

`POST /api/views` accepts a raw file body with `Content-Type: application/gzip`
(recommended), `application/json`, or `application/octet-stream`. Send no
`Content-Encoding` header. The same capsule can be imported manually as JSON or
gzip. Every upload is at most **512 KiB stored** and **2 MiB decoded**; uncompressed
JSON larger than 512 KiB must first be gzipped locally. The shared
[`capsule.mjs`](../lib/protocol/capsule.mjs) validates format, identities,
memberships, relation endpoints, finite numbers, depth and continuation metadata.
Unknown builders can supply readable authored snapshots; storage validation does
not certify their science or make them executable.

The response after a confirmed durable write is HTTP 201, or HTTP 200 for a
byte-identical retry:

```json
{
  "id": "22-character-base64url",
  "url": "https://eigenquestions.com/#view=22-character-base64url",
  "readUrl": "https://eigenquestions.com/api/views/22-character-base64url",
  "sha256": "sha256-of-the-exact-uploaded-bytes",
  "bytes": 12345,
  "createdAt": "2026-11-06T12:00:00.000Z"
}
```

Actual IDs contain exactly 22 characters from `[A-Za-z0-9_-]`, generated from 128
random bits. Keep the exact bytes until the receipt arrives. A persistent
SHA-256 reservation maps those bytes to one ID, so a lost response or uncertain
R2 write can be retried safely. Re-encoding JSON or gzip differently creates a
different byte identity. A reservation timestamp records when storage capacity
was first reserved; it is not a model execution or paper publication date.

`GET /api/views/:id` returns the exact bytes, their MIME type,
`X-Content-SHA256`, a quoted `ETag`, attachment disposition and an immutable
cache policy. `HEAD` and conditional GET are supported. There is no HTTP
`Content-Encoding`, so clients explicitly decode gzip once. Negative and error
responses use `Cache-Control: no-store`; no initial 404 is cached. Cross-origin
programmatic clients use CORS `*`, without cookies or credentials. Unsupported
methods return 405; the old voting, quiz and submission APIs remain retired.

Errors are JSON `{ "error": { "code": "...", "message": "..." } }`.
Invalid capsules return 400, over-limit files 413, unsupported transport 415,
daily admission exhaustion 429 with `Retry-After`, inventory exhaustion 507,
and unconfigured or unconfirmed storage 503. A failed save never returns a
saved URL. Keep or download the file when saving is unavailable.

## Admission and persistence

The launch budgets in [`backend/budget.mjs`](../backend/budget.mjs) are explicit
service limits, distinct from the theoretical capacities in the
[free-tier calculation](Q-003-cloudflare-capacity.md):

| Budget | Enforced limit |
|---|---:|
| Lifetime reserved object bytes | 8,000,000,000 |
| Lifetime reserved objects | 100,000 |
| New digest reservations per UTC day | 2,000 |
| Admitted upload attempts, including retries, per UTC day | 8,000 |

One named SQLite object, `public-view-budget-v1`, commits the digest, ID, byte
reservation and counters in one synchronous transaction before the Worker may
touch R2. Concurrent requests cannot oversubscribe those counters. Only a later
UTC day resets daily counters; restarts do not. Existing IDs are conditionally
created with `If-None-Match: *` and are never overwritten by this service.
R2's successful write is awaited before acknowledging the URL.
[R2 write/conditional semantics](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/)
and [SQLite transaction semantics](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/).

Failed or abandoned writes retain their reservation conservatively. Retrying
the same bytes reuses it. There is no automatic refund, deletion, expiration,
cleanup alarm, or scheduled pruning. Reserved totals may therefore exceed
actually stored bytes. Stop new saves at capacity while continuing existing
reads. The upload switch `VIEW_UPLOADS_ENABLED = "false"` stops saves while
retaining R2 and read access. Do not remove storage bindings to pause uploads.

Do not reset the budget object, rename its stable instance, point another
independent budget at the same bucket, erase its tables, or change the bucket
without reconciling the complete retained inventory first. That would invalidate
the lifetime bound or lose retry identities. No public administration or
deletion endpoint is exposed. Future budget increases and any reconciliation
need an explicit owner decision; pending reservations are not silently freed.

These links are **public and unlisted**, not private, authenticated or encrypted
for an owner. Anyone holding the link can fetch it. Do not upload secrets or
private conversation transcripts. Store concise scientific context. No listing
endpoint is provided; a random ID is a sharing capability, not access control.
The service has no promise of perpetual hosting, but it selects no expiration
policy and does not expire links automatically. Pinned external builders/data
must remain available to support recomputation or continuation.

## Costs and operational limits

The bounds cover this service's own reservations, not the account's remaining
free allowance. Other buckets, applications and external writes consume shared
allowances. R2's allowance is not a spending cap and enabling R2 can require its
subscription. This change does not switch the account to Workers Paid or
authorize paid overages. Check the actual account before activation.
[R2 pricing](https://developers.cloudflare.com/r2/pricing/) and
[Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/).

Every API read still invokes a Worker and performs one R2 GET or HEAD. There is
no R2 custom-domain read path in this release. Browser caching may avoid a later
request; no such savings are assumed. A new save uses one budget RPC, one R2
HEAD and one conditional PUT. A racing retry may add a second HEAD. Retries
that find an existing object avoid PUT. The 8,000-attempt cap bounds authorized
R2 PUT attempts at 248,000 in a 31-day month; every admitted request is counted
before R2 access, including an uncertain or failed write. Reads, malformed
requests, preflights, error traffic and retries still consume platform requests.

Workers Free's request ceiling is separate from application admission. Attacks
can exhaust it and make existing API links temporarily unavailable even when
the objects remain intact. Free SQLite Durable Objects also have independent
request, duration and SQL limits. Exhaustion fails instead of granting unlimited
capacity. The implementation does not claim uninterrupted reads or a zero-cost
guarantee under arbitrary traffic or unknown account usage.
[Workers limits](https://developers.cloudflare.com/workers/platform/limits/) and
[Durable Objects pricing and Free limits](https://developers.cloudflare.com/durable-objects/platform/pricing/).

The shared validator's worst-case CPU and actual endpoint latency must be
measured on the intended account. Local workerd wall time includes emulated
storage and is not the production Workers Free 10 ms CPU measurement. Do not
raise the plan automatically to make validation fit. Use
[`scripts/benchmark-stored-views.mjs`](../scripts/benchmark-stored-views.mjs) for
reproducible local comparison; account CPU and a controlled public upload/read
remain activation checks.
[Recorded local comparison](evidence/q003/stored-views-local-benchmark.json).

## Activation and verification

1. Verify that the actual account has enough unused R2 Standard allowance and
   Workers Free/SQLite Durable Object capacity. Confirm any R2 subscription
   decision with the owner. No old D1 database participates in this design.
2. Create the dedicated **empty** R2 bucket `eigenquestions-views`. Leave public
   `r2.dev` access and automatic expiration disabled. Keep R2 Standard storage.
   Do not reuse an occupied bucket without a ledger migration.
3. Review `wrangler.views.toml`: the `VIEWS` bucket binding, `VIEW_BUDGET` binding,
   `stored-views-v1` SQLite class migration, domain route, and upload switch.
   The configured deployment token needs those resource permissions. Do not
   print or commit any token. `wrangler types --config wrangler.views.toml`
   can generate the binding types when needed.
4. Run `npm run build`, `npm test`, and `npm run check:site`. A local packaging
   check is `npx wrangler deploy --dry-run --config wrangler.views.toml`;
   it is not provisioning or a production CPU test.
5. Set the GitHub **repository variable** `ENABLE_STORED_VIEWS` to exactly
   `true`, then use the authorized main deployment workflow. Its config choice
   remains active on later main pushes. Leaving that variable unset deploys
   the unbound API profile. Neither profile activates a paid plan.
6. Upload a real gzip capsule from the agent, confirm the durable receipt,
   re-upload the exact bytes and confirm the same ID, then fetch and verify
   its SHA-256. Open its short URL in a fresh browser and verify authored
   grouping/labels, unavailable-builder behavior, and supported continuation.
   Measure Worker CPU separately from wall time before calling the endpoint
   compatible with the Free CPU limit.

To pause writes after activation, keep `ENABLE_STORED_VIEWS=true` and deploy
the activated profile with `VIEW_UPLOADS_ENABLED=false`. Existing GETs remain
available. Retain both bucket and budget namespace on rollback. Removing the
repository variable or deploying the default unbound profile also disables
reads and is not the way to pause admission.

Local acceptance uses the exact Wrangler-pinned Miniflare/workerd dependencies
and tests concurrent same-byte saves, immutable writes, failed and uncertain
PUTs, SQLite restart/day rollover/capacity boundaries, malformed and over-size
gzip, source-reference rejection, unknown builders, exact authored-data reads,
CORS, method boundaries and negative caching. None of these tests uses the
old D1 database or provisions remote resources.
