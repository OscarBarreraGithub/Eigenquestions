# Final independent agent/browser acceptance

Status: design ready; accepted atlas and root launch gate pending. No fresh-agent
turn or final-data browser job has been launched. QA14 proves scripted MCP
transport; QA15 adds captured-revision rejection and real browser acknowledgement.
Neither proves that an independent agent can interpret and route a scientist's query.

## Reuse one running application

Use one authorized isolated Slurm allocation with the existing Node 22, Python
Playwright and Chromium paths from `qa14/run.sbatch`. Budget initially 2 CPU,
8 GB, at most 45 minutes; never exceed the authorized 8 CPU / 32 GB / 1 hour.
No owner's Chrome, local browser automation workaround, new service or copied
model-account credentials. Reuse the existing SSH alias privately.

The job starts from the complete pinned Git archive plus exact runtime/data overlays,
prevalidates the explicit default-home selector against the final manifest, then
installs the hash-pinned final site/archive and verifies its complete asset
manifest, starts `bin/navigate.mjs serve --atlas ... --connection ...`, and opens
its local token link in a fresh nonpersistent Chromium context. Extend QA14's
browser observer only to remain open while a real agent works. The observer may
initialize a case, record state/revision/DOM/screenshots and check expectations;
it must not choose the agent's destination or send navigation calls for it. Keep
the browser alive through failure capture; record the exact failed stage, current
DOM and sanitized state before closing the context.

Root starts a fresh Astra agent with `fork_turns:"none"` after the gate. Its input
contains only the portable skill/reference paths, a bounded command prefix, the
current visible starting point and natural-language tasks. It gets no expected
IDs, gold routes, prior reviewer conversations, recovery artifacts or evaluator
packets. Its actual shell tool calls run the maintained CLI inside the existing
Slurm allocation. Label this evidence **independent agent CLI → bridge → rendered
browser**, separately from the existing scripted stdio-MCP proof. Do not claim it
tests native MCP-client installation. The same MCP mutation guard is covered by
QA15 and the real stdio integration tests.

Prepared passive observer: `research/q025/integration/agent-browser-observer.py`.
It is Slurm-only, starts the existing companion/browser, writes a token-free
`agent-run.json`, records revision/DOM acknowledgements and screenshots, and waits
for a root `stop.json` marker. It sends no navigation commands. It has passed
syntax checking only; actual accepted-data execution remains gated.

For the final allocation, unpack and build in `$SLURM_TMPDIR` (or a private
job-specific node-local temporary directory), verify every input hash there, and
copy compact reports back to shared scratch. Keep the connection file node-local;
only its path goes to the agent wrapper. The shared-filesystem overhead observed
in QA23 is not a reason to change any scientific package bytes.

```sh
python research/q025/integration/agent-browser-observer.py \
  --project "$NODE_LOCAL_PROJECT" --atlas "$NODE_LOCAL_ATLAS" \
  --node "$NODE_BIN" --output "$PRIVATE_RUN_OUTPUT" --minutes 40
```

The separate public run adds `--public-origin https://eigenquestions.com` and
`--permission-mode default` or `consent`. It verifies the exact live manifest
before attaching and records these permission outcomes separately.

Safe command wrapper, with the exact allocation paths supplied in a private run
configuration at launch (no token contents in that configuration):

```python
import json, shlex, subprocess
run = json.load(open("private-run.json"))
def remote_cli(*arguments):
    command = ["srun", "--jobid", str(run["jobId"]), "--overlap", "--exact",
               "--nodes=1", "--ntasks=1", "--cpus-per-task=1",
               run["node"], run["project"] + "/bin/navigate.mjs",
               *arguments, "--connection", run["connectionFile"]]
    return subprocess.run(["ssh", "-o", "BatchMode=yes", "-o",
                           "StrictHostKeyChecking=yes", run["sshAlias"],
                           shlex.join(command)], check=True, text=True,
                          capture_output=True)
# Actual agent calls, at separate reasoning steps:
# remote_cli("state")
# remote_cli("search", "--query", agent_chosen_search_terms)
# remote_cli("action", "--json", json.dumps(agent_chosen_action),
#            "--expected-revision", str(captured_parent))
```

This is a thin command adapter around the existing CLI, not another service or
navigation engine. The agent's tool transcript must contain its own chosen CLI
arguments. Token contents never enter the agent prompt or command line; the
connection file stays on the compute node. Remote login performs scheduling only;
CLI computation runs in the allocation. The observer also supplies a sanitized
same-origin static base URL, so the agent may read exact destination HTML through
an equivalently quoted `srun curl` call. Reading the copied skill/static destination
HTML is allowed; answer-key/research directories are outside the task. Check the
complete tool transcript for that boundary. This is fresh-context testing, not a
claim of filesystem isolation beyond the documented sandbox.

The agent must read `SKILL.md` and `references/interface.md` through a real tool,
capture `state.revision` before interpreting each visible request, inspect scope
and source evidence, and supply `--expected-revision` on every mutation. It then
reads state until the exact revision reports `browserStatus.acknowledgedCurrent`.
The observer independently verifies matching DOM state ID and destination ID.
On a revision conflict the action stays uncommitted; preserve the draft and newer
state instead of restamping. This is enforced by the new protocol guard.

## Small case matrix, fixed before agent launch

Bind the exact target IDs, allowed alternatives, source witnesses and boundary
conditions only after final scientific admission. Keep this oracle outside the
agent-facing packet. These are preselected acceptance cases, not a claimed unseen
scientific holdout. A missing accepted destination is an explicit coverage result.

1. **KK → dark matter.** Start at the all-physics entrance. Ask how a KK-graviton
   tower acquires cosmological abundance, then whether a tower with repeated
   intermode decays can serve as dark matter. Ask what controls the near-threshold
   transition rate and what observational conclusions depend on that rate.
   Require separate production, decay and observational scopes, real recorded
   connections, attributed source challenges and their assumptions. Capture the
   final exact rate-question selector.
2. **Alternate entry and wording.** A different fresh agent begins at an accepted
   cosmology/dark-matter entrance and asks for the dynamics setting the rate of
   nearly degenerate heavier-to-lighter KK-graviton transitions under the same
   defining assumptions. It must converge to the same accepted question selector
   as case 1 through its own interpretation and route. Changing the governing
   regime is a separate boundary probe, not required to converge.
3. **Independent physics case.** A fresh agent asks what ultraviolet-gravity
   models imply for black-hole behavior, then asks which renormalization-group
   mechanism underlies the selected application. The observer binds the actually
   admitted black-hole → RG application route after the final data freeze. The
   agent receives only the scientific request, not endpoint IDs, route labels or
   a suggested lookup. Require exact scope, reading limits and an inspected
   relation proof; do not substitute an unadmitted island/replica-wormhole route.
4. **Premise-sensitive independent case.** A fresh agent asks about weak dissipation
   at CMB scales becoming strong late enough for a primordial-black-hole mechanism,
   then whether a compatibility argument requiring strong dissipation throughout
   applies. Require separate regimes and exact source/reading context rather than
   attributing every co-paper assumption to the selected question.

Run agents serially against fresh case contexts so they do not overwrite each
other. Bound each case to roughly 6 minutes and 25 CLI/tool operations; one clear
data/connection failure is a recorded outcome, not a retry loop. Do not steer the
agent toward the oracle during its run. Subsequent repair and rerun get distinct
lineage and are not counted as the original independent success.

In one successful case, ask for Back, replay and an explicit new path. Save the
existing session before branching; demonstrate that another agent change does
not discard a locally authored test work note. Use synthetic test notes only,
export them separately and verify compact links omit them. Require exact IDs and
source scope, not a particular prose style. Normal branches should give a useful
roughly 1–15 choices; the 17-field metadata entrance is an explicit exception.

## Public HTTPS is a separate gate

After root publishes the exact accepted manifest, reuse
`public-bridge-acceptance.py` in two fresh isolated Chromium contexts:

```sh
python research/q025/integration/public-bridge-acceptance.py \
  --project "$PROJECT" --output "$OUT/default" --node "$NODE_BIN" \
  --atlas "$ATLAS" --destination "$DESTINATION" --permission-mode default
python research/q025/integration/public-bridge-acceptance.py \
  --project "$PROJECT" --output "$OUT/consent" --node "$NODE_BIN" \
  --atlas "$ATLAS" --destination "$DESTINATION" --permission-mode consent
```

These arguments match the maintained script. Both cases first
verify public compact URL rendering and live manifest hashes. Record default
browser policy as its own outcome. The separate consent case uses only normal
`BrowserContext.grant_permissions(['local-network-access'],
origin='https://eigenquestions.com')`, already approved for this isolated test.
Record that it simulates scoped user consent, not a demonstrated native prompt
click or permission in the owner's browser. No disabled security, interception,
wildcard permission or DNS workaround. Use DOMContentLoaded and explicit connected/
rendered-revision waits, never network-idle for a live SSE connection.

For the final independent public-connected proof, keep the public page attached
to the same authorized companion and let a fresh agent choose and commit one real
destination using the strict CLI guard. The observer verifies the exact public
origin, accepted manifest, state/revision and DOM acknowledgement. A scripted MCP
call alone does not satisfy this requirement. If default policy blocks attachment,
preserve that result and the visible help/fallback state even if scoped consent
passes. Static `/atlas/index.html` discovery and compact links remain separately
testable without installation or upload.

## Final presentation and evidence

Inspect a small actual-data set: root, one reviewed broad region, the KK rate
question, one contribution-only question, and one independent case. If frozen
assumptions/conventions contain workflow boilerplate, preserve their definitions
and hashes and place an explicit editorial/display annotation with exact origin
under methods/reading/workflow context. Never present "requires independent
review" as current status after admission or a numerical-membership warning as a
physics premise. This is an attributed display treatment, not a scientific edit.

Receipt pins: code/archive/skill/accepted-atlas hashes, Slurm job, fresh agent
identity/model/context isolation, tool transcript, chosen selectors, every captured
parent and committed/rendered revision, source IDs, screenshots and failure
lineage. Publish token-redacted derivatives only, with an explicit redaction record;
private originals remain private. Record transfer/parse/long-task and mobile
overflow evidence on the real corpus; retain the final asset-count/25 MiB limits.
No final success claim until source semantics, independent routing, actual render
and public permission cases have their own inspected results.
