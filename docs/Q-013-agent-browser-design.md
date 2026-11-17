# Agent-to-browser communication for the physics atlas

Request: Q-013. Author: /root. Researched 2026-11-16.
Status: architecture recommendation; the hosted live session is not implemented.
Read with the [agent interface](agent-interface.md), [stored-view operations](stored-views-operations.md),
[original view proposal](Q-003-contextual-view-proposal.md), and [Lab Notebook](../Lab%20Notebook.md).

## Recommendation

Keep one portable, versioned scientific-view format. Make ordinary HTTPS upload
and an immutable read link the general delivery path. Add an optional paired
browser session that presents the same object automatically. File import and the
existing page interface consume that same format. MCP is an adapter to these
operations, not a second state model or a prerequisite for every user.

The server stores, validates, authorizes and relays data. Scientific/model
computation remains in the agent or browser. The new physics-wide map and the
text explorer must render the same accepted scientific state; the existing fixed
overview is currently separate and cannot be assumed to support this interface.

## What the agent sends

A graph operation is not generally recoverable from its hash. SHA-256 identifies
exact bytes; it does not compress or encode them reversibly. Use a random view ID
for a public read URL and a checksum for integrity. A URL fragment beginning `#`
is a different concept: it is parsed by the page and is not sent with the initial
HTTP request ([MDN](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Fragment)).
Retain existing `/#view=ID` compatibility and return the direct JSON `readUrl` so
agents that do not execute JavaScript can retrieve the actual artifact.

The view should contain both the accepted result and, when available, its recipe:

- Data identity: graph, source snapshot, embedding/metric and relevant versions.
- Scientific context: resolved question, assumptions, lens, exclusions and path
  commitments needed to interpret the next question; no private reasoning transcript.
- Region: source/concept identities, weighted memberships and overlapping groups.
- Interpretation: actual accepted names, descriptions, evidence, relationship
  types, limitations and next directions. Do not regenerate these from a seed.
- Geometry: typed supplied layout or a specified projection, plus its diagnostics.
  Arbitrary new mathematics can run outside the browser and return supported data.
- Optional construction recipe: named operator/version, seeds, diffusion scale,
  normalization, parameters and referenced inputs, with a stated reproducibility scope.
- Continuation capabilities: what can be displayed, recomputed, or explored further.

Preserve a small display snapshot even when an exact recipe exists. Unknown or
unavailable builders may still yield a readable view; do not silently substitute
today's graph and claim the original calculation. A recipe alone is appropriate
only when all omitted results can be recovered by an available pinned builder.
The accepted model-generated labels/groups are outputs, not reproducible merely
from model names or random seeds. Numerical replay and pixel identity are separate.

Reference immutable shared data instead of sending the entire physics graph with
each question. Retain enough source metadata for basic inspection without a fresh
download. Large membership arrays can later use bounded, checksummed data shards,
but the initial protocol should send complete small views rather than patches.
Any recipe executed in the browser uses a known bounded worker operation; never
evaluate arbitrary JavaScript, functions, HTML or shader code supplied in a view.

Our earlier size study measured complete views at 80,850–102,746 bytes after
Brotli plus URL encoding; a lean source-referencing view still used about 29 KB.
Small recipes were much shorter but did not preserve arbitrary authored views.
Thus a giant URL is not the general protocol. These are measurements of the old
Swampland views, not predictions for the broader atlas. [Measurements](Q-003-contextual-view-proposal.md#measured-payloads-2026-11-06).

## The two user experiences

**Open a result.** The agent uploads a view over HTTPS and receives a URL only
after storage confirms persistence. The user opens that URL on any supported
browser/device. It refers to an immutable result, not a moving session head.
Download and file import remain available if hosting fails or is inappropriate.
GET/HEAD only retrieve; a link preview must never pair an agent or mutate a view.

**Follow an agent.** The user chooses Connect agent for the intended tab/session.
A one-time pairing grant lets the agent obtain narrowly scoped session access.
The agent uses ordinary HTTPS requests; it need not keep a socket or local daemon
alive. The browser opens an outgoing connection to Eigenquestions and receives
small notifications identifying new views/revisions. It fetches the payload,
validates and renders it through the same controller, then acknowledges that
revision. This avoids public-website-to-localhost dependencies.

A high-entropy, short-lived, single-use pairing grant is preferable to a long-lived
secret in a share link. A short human-entered code additionally needs tight attempt
limits and confirmation in the browser. Pairing provides session-scoped control,
not authority to publish private work, change other sessions or access the machine.
An authenticated MCP client can authorize the same session through its supported
authorization flow; do not disguise a custom pairing token as OAuth support.

The agent should be able to read the current scientific state and selected region
as well as present a result. Pairing shares only the atlas context needed for that
task, not the whole conversation or browser history. One foreground coordinator
presents; helper agents return proposals. Read-only orientation stays separate.

## Cloudflare implementation choice

- **Worker + R2:** validate and store immutable view objects. R2's direct API is
  strongly consistent; await the completed write before publishing a reference.
  Use conditional creation to preserve immutability.
- **One SQLite-backed Durable Object per active session:** retain the current
  session revision/view reference, bounded operation receipts, permissions and
  viewer acknowledgement state. Use transactional updates, not eventual-consistent
  KV, for the current session head.
- **Browser WebSocket using Durable Object hibernation:** send small revision
  notifications and acknowledgements. Persist everything needed across hibernation;
  memory is not durable. The agent continues to use POST/GET. A bounded, backoff
  HTTP polling fallback can recover from a blocked connection, without a second
  scientific protocol or endless aggressive polling.

SSE is viable for one-way browser notifications, and the local companion already
uses it. For the hosted bidirectional session, hibernating WebSockets fit the
platform's coordination model. They do not imply zero overall cost: traffic,
storage and active execution still count. No new quota/cost estimate is established
by this recommendation. Sources: [R2 consistency](https://developers.cloudflare.com/r2/reference/consistency/),
[SQLite storage](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/),
[WebSocket hibernation](https://developers.cloudflare.com/durable-objects/best-practices/websockets/),
[SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events).

## State and failure rules that matter

1. Capture the parent scientific revision when starting a computation. On return,
   compare it with the current session and tab state. Do not fetch the newest
   revision merely to stamp an old answer as current. A conflict yields a saved
   proposal/branch or an explicit reconsideration, never blind overwrite.
2. Store the artifact first, then atomically commit the session pointer/revision
   and operation receipt. R2 and the session database are not one transaction.
   Recheck expected state after external I/O; a failed commit may leave a stored
   unpresented artifact, which must be accounted for rather than silently deleted.
3. Use a unique operation ID and idempotent receipts. Retries after lost responses
   must not create repeated navigation steps. The same operation ID with different
   content is an error. Ordering follows committed revisions, not timestamps.
   Retain the exact upload bytes for retry; a checksum of compressed bytes does
   not imply semantic equivalence between differently serialized views.
4. A browser catches up from durable current state after disconnect, sleep or a
   missed event. Notifications are hints; they are not the sole record of state.
   Cancel stale downloads and reject late old results before replacing the screen.
5. Distinguish saved, accepted for a session, applied by a particular viewer, and
   rendered. A hidden/suspended tab may not render promptly; lack of acknowledgement
   is reported honestly. Even a render acknowledgement does not prove a human saw it.
6. Keep typing, panning and reading responsive while computation runs. Separate
   local camera/UI state from scientific state. A user can pause Follow agent or
   branch into independent exploration. A new result should not erase a draft or
   seize a browsing tab. Intentional scientific navigation is a real context change.
7. Give each viewer/tab its own identity and follow/paused status. A read-only
   shared link does not grant write control or automatically opt into live following.
   Forking exploration does not mutate the shared immutable result.
8. Explicitly bind the view to data/schema/builder versions. Missing assets or
   unknown operators degrade to the supplied snapshot, with unavailable actions
   disclosed. Do not equate successful display with reproducible computation or
   faithful continuation of a rich context.

Durable Objects still need concurrency discipline: awaiting external fetch/R2
operations permits interleaving. [Cloudflare concurrency rules](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/).

## Privacy, bounds and lifetime

Showing a view and publishing it are separate operations. Existing stored views
are public/unlisted: anyone with the link can read them. A random ID or checksum
is not named-collaborator privacy. Private live-session payloads require an
authenticated/session-capability read path that is never also served through the
public artifact endpoint; otherwise use the local/file route. The first public
rollout must not silently publish unpublished research markings.

Read and present/publish permissions are separate. Never put a write credential
in a shared URL, exported view or logs. If a pairing grant travels in a fragment,
consume it only after explicit pairing, clear it from the address, and avoid
analytics capture; fragments remain visible to page scripts and browser history.
Earlier public browser tests observed hosting-injected Cloudflare analytics, so
inspect the actual pairing page and network traffic rather than assuming its
script set matches the source HTML.
Validate WebSocket origins and use scoped authorization, not CORS as access control.
Apply per-scope authorization to every referenced private object. Private dedup
must not disclose another session's content through a global hash lookup.

Bound encoded and decoded sizes, nesting, arrays, numbers, references and compute
work. Render descriptions as data, sanitize supported markup, and restrict link
schemes. Never fetch arbitrary agent-supplied server URLs. Treat source text as
evidence, not instructions to the receiving agent. A valid schema does not certify
the science. Current v1 limits (512 KiB stored, 2 MiB decoded, 500 source nodes,
50 groups and 5,000 edges) are view limits, not permission to upload all physics;
revisit them only after representative measurements.

Immutable public objects can be cached. Mutable session state and failed reads
must not inherit immutable caching; negative caching can hide a newly uploaded
object. Private reads need appropriate private/no-store policy. Deletion and
revocation must account for caches and already downloaded copies. Existing saved
views have no approved automatic expiration; temporary pairing/session expiry
must be separately disclosed, and must not silently erase shared artifacts.
Keep export available and document retention/availability rather than promising
that a hash makes a view permanent.

## Generality and alternatives

| Approach | Role and limitation |
| --- | --- |
| HTTPS artifact + URL | Default portable result; works asynchronously and across devices; opening a link alone does not update an unrelated open tab. |
| Paired hosted session | Smooth live presentation with a normal public browser; needs explicit pairing and a small stateful relay. |
| Existing page API | Best shortcut when the agent can operate the intended page; shares the same validator/controller. |
| MCP | Optional discoverable tools over the same operations; remote HTTP or existing local stdio depends on the client. |
| WebMCP | Progressive enhancement for capable browser agents; currently an origin-trial/proposed standard, not a universal prerequisite. |
| Local companion | Existing tested route and useful local/private option; public-to-loopback access has browser permission constraints. |
| File/drop/paste import | Provider-neutral fallback; paste is a proposed convenience, not implemented capability. |
| Full view in URL | Useful only for demonstrably small recipes; does not accommodate arbitrary scientific views. |
| postMessage / WebRTC | Useful in specific integrations; postMessage needs a reachable window and origin checks, and peer connections need signaling/lifecycle work. Neither replaces the general upload/read contract. |

Current references: [MCP transports, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports),
[MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization),
[WebMCP status](https://developer.chrome.com/docs/ai/webmcp),
[local-network permissions](https://developer.chrome.com/blog/local-network-access),
[postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage).
An agent with read-only web search cannot acquire POST, code execution or tab
control by reading instructions. Discovery documents cannot grant capabilities.
Offer the best supported route and explain its limit. Mathematical computation
still needs execution in the agent or a connected browser worker; a protocol does
not make a search-only agent into an executable graph engine.

## Scope of the next implementation

First activate and verify the existing immutable save/read path through authorized
account access, retaining file fallback. Keep public/unlisted scope explicit.
Next add one narrowly scoped live session and connect the new map to the existing
controller. Add a thin remote MCP adapter where it reduces setup; preserve direct
HTTP and page operations. Avoid a new agent framework, universal patch protocol,
collaborative document editor or arbitrary-code execution service for this milestone.

Acceptance should cover: exact authored-view round trip; unknown-builder display;
retry after an uncertain upload/commit; stale agent result after user navigation;
out-of-order events; offline/hidden-tab acknowledgement; reconnect to the latest
head; multiple tabs with independent follow state; revoked/expired pairing; public
read links lacking write authority; private payloads inaccessible on public routes;
corrupt/oversized objects; and a physics-wide-to-Swampland view plus a region
description reaching the real renderer through this same interface.

Prior evidence remains bounded: the page API and local MCP bridge passed browser
tests; the public app.js matched the recorded release on 2026-11-16, while the
public stored-view endpoint returned HTTP 503 storage_unavailable. No hosted live
relay or physics-wide rendering has been implemented or tested. Existing tests do
not establish the new private-session or remote-MCP behavior described here.
