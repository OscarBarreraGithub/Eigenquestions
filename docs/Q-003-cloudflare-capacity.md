# Q-003 — Stored views on Cloudflare: free-tier capacity

Checked 2026-11-06 against Cloudflare's current primary documentation. This is
a quota/cost calculation, not a deployed service, account-usage audit or load test.
All free allowances are assumed available to this project.

## Recommended storage path

The agent or manual drag-and-drop produces the same validated contextual-view
file. The client compresses it and uploads binary bytes with an ordinary HTTP
POST. A small Worker assigns an immutable random key, stores the object in R2,
and returns a URL only after the write succeeds. The static application opens
that ID, fetches the saved object asynchronously and updates its explorer.

R2 stores the large view file. D1 is optional for future accounts, ownership or
searchable metadata; random-key lookup does not need SQL. A WebSocket is not
needed for this upload/receipt/read flow. The UI remains usable and can display
an upload indicator. Do not report a saved link before durable upload succeeds.

For public/unlisted share links, serve objects through an R2 custom domain such
as `views.eigenquestions.com`; the static application URL can be
`https://eigenquestions.com/#view=<id>`. Reads then bypass Worker invocation.
This is an architecture proposal, not a claim that those routes exist. The R2
development `r2.dev` endpoint is rate-limited and unsuitable for production.
Authenticated private reads would use a different route and budget.
[R2 public-domain documentation](https://developers.cloudflare.com/r2/buckets/public-buckets/).

Keep the numerical graph construction and compression in the agent/browser.
The upload endpoint does bounded admission/format checks and storage. Its
validation/authentication path still needs a real CPU and burst test.

## Published allowances and accounting

| Resource | Published free allowance | Planning budget with 20% reserve |
|---|---:|---:|
| R2 Standard storage | 10 GB-month/month | Keep retained objects below 8 GB |
| R2 Class A, including PUT | 1 million/month | 800,000/month |
| R2 Class B, including GET | 10 million/month | 8 million/month |
| Worker requests | 100,000/day | 80,000/day |
| Worker CPU | 10 ms/invocation | Must measure the proposed endpoint |

R2 egress is free. Static assets served without Worker execution do not consume
the dynamic Worker-request allowance. R2 storage is billed from averaged daily
peak storage, so 8 GB retained is a conservative planning threshold, not a
statement that Cloudflare has a hard 10 GB storage cap.
[R2 pricing](https://developers.cloudflare.com/r2/pricing/) ·
[Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/) ·
[Workers limits](https://developers.cloudflare.com/workers/platform/limits/).

The simple model counts one Worker POST and one R2 PUT per new saved view, plus
one R2 GET per opening. It assumes no cache hits, HEAD/list/polling calls or extra
authentication/preflight requests. Retries and operational overhead consume the
reserve; they are not free operations. A static shell must bypass the Worker.

Under this model, the operation budgets permit approximately **26,666 new saved
views/day averaged over 30 days** (1,111/hour), and **266,666 uncached openings/day**
(11,111/hour). The Worker separately permits an 80,000-POST planning budget on a
particular day. These averages are not per-hour rate limits, concurrency capacity
or latency guarantees. Storage lifetime is the tighter constraint below.

If every opening instead passes through a Worker, five openings per new view
require six Worker calls. That alternative permits about **13,333 new views/day**
under the same 80% planning budgets, before storage is considered.

## Capacity using measured view sizes

Budget **128 KiB = 131,072 stored bytes per view**. This gives room above the
roughly 81–101 KB DEFLATE sizes measured for current complete computed views.
Store compressed binary bytes, not base64 URL text. This is an assumed average,
not a universal bound on future richer views. PDFs and repeated corpus data are
not included. Source data/builders referenced by a view must remain available.

Using decimal GB for planning:

`retained views = floor(8,000,000,000 / 131,072) = 61,035`.

| Average stored view size | Views retained within 8 GB |
|---|---:|
| 32 KiB | 244,140 |
| 128 KiB baseline | 61,035 |
| 512 KiB | 15,258 |
| 1 MiB | 7,629 |

Permanent URLs accumulate storage; 61,035 is a total inventory, not a renewed
monthly allowance. At the baseline size:

| Daily active users | Saves/user/day | New saves/day | Opens/day at 5 per save | Storage after 30 days | Time to 8 GB |
|---|---:|---:|---:|---:|---:|
| 100 | 20 | 2,000 | 10,000 | 7.864 GB | 30.5 days |
| 500 | 20 | 10,000 | 50,000 | 39.322 GB | 6.1 days |

Both traffic examples fit the operation budgets. The second needs paid storage
much sooner if links remain available. Registered users and simultaneous users
cannot be inferred from these daily-activity assumptions.

For comparison only, an explicit rolling retention policy would sustain about
2,034 new views/day at 30 days, 678/day at 90 days, or 167/day at 365 days within
8 GB. **No expiration policy is selected here:** the owner proposes keeping links
and growing storage. Free storage cannot grow indefinitely at any positive rate.

## Growth and reliability decisions

Extra R2 Standard storage costs $0.015/GB-month. Holding 40 GB steadily costs
about $0.45/month for storage after the free allowance; 100 GB costs $1.35/month;
1 TB costs $14.85/month. These examples exclude operation overages, other services
and taxes. Growing inventories are billed from monthly averaged daily peaks,
not simply their last-day total. Workers Paid starts at $5/month if dynamic
request/CPU allowances become a constraint. [R2 pricing](https://developers.cloudflare.com/r2/pricing/)
· [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/).

R2 requires enabling its subscription and meters overages; its free allowance
is not an automatic zero-spend cutoff. A strictly free service needs upload-size,
rate and total-byte admission budgets. Budget exhaustion should stop new saves
while existing links continue to work. [R2 setup](https://developers.cloudflare.com/r2/get-started/).

Return durable immutable links and retry with the same object/key to avoid
duplicate saved views after a lost receipt. R2 provides strong read-after-write
consistency; avoid caching initial 404s for unpublished IDs. New cached public
objects should be immutable. [R2 consistency](https://developers.cloudflare.com/r2/reference/consistency/).

KV is a poorer payload choice here because its free plan allows only 1,000
writes/day. D1 has 5 GB total free storage but a 500 MB per-database free limit;
keep any D1 use to small indexed metadata rather than full view blobs.
[KV pricing](https://developers.cloudflare.com/kv/platform/pricing/) ·
[D1 limits](https://developers.cloudflare.com/d1/platform/limits/).

## Evidence and next action

[Machine-readable assumptions and calculations](evidence/q003/cloudflare-capacity-20261106.json)
· [measured view sizes](evidence/q003/size-study/report.json).

The capacity conclusion was independently checked by Astra protocol. No account
API was used, no R2 subscription/bucket was created, and no hosting change was
deployed for this calculation. Next, if implementing this design, preserve the
complete contextual-view contract, test the lightweight upload path against the
10 ms CPU allowance, and measure round-trip latency/bursts before claiming a
reliable service throughput. Agent model usage is outside these hosting costs.
