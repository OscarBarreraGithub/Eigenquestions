# Frozen pre-holdout read access

This is a private access stage for the 8,399 reviewed homes, 31 extraction-context gaps and 43 reserved cases. It is not a final release, scientific amendment or live browser mutation test. The manifest must explicitly remain `partial_pre_holdout_candidate`, `pre_holdout_freeze`, `sourceInventoryAccounted:true`, `sourceAccountingComplete:false`. Preparation verifies file hashes without inspecting reserved scientific records or evaluation queries.

After geometry freezes the new geometry-bearing package and root approves its exact manifest/runtime pins:

```sh
python3 research/q025/integration/preholdout-access-v1/prepare.py \
  --candidate "$FROZEN_PREHOLDOUT_PACKAGE" \
  --manifest-sha "$FROZEN_MANIFEST_SHA256" \
  --commit "$ROOT_VERIFIED_COMMIT" --output "$NEW_PRIVATE_ACCESS_DIRECTORY"
```

The output directory must be new and on the same filesystem as the immutable source pack. Code, skill and schema files come from exact committed Git blobs. The complete checksummed delivery inventory, existing source-context pack and frozen source metadata are hard-linked after verifying bytes/hash, with zero source payload copies. No file is written or chmodded after linking. Do not edit these linked files or run mutation fixtures against this tree. Unlinking a disposable access tree is safe; changing a linked file changes its source. Native vector exploration is intentionally unavailable in this read-only stage.

The usable static data entry is the exact path printed as `staticEntry`, namely `application/atlas/manifest.json`. Its checksummed catalog, scientific detail records, source memberships and optional source-context shards are adjacent. This is ordinary static JSON discovery, not a claim that generated HTML or the public website already serves this version. If HTTP-only reading is needed, the existing companion can serve this directory with `bin/navigate.mjs serve --atlas application/atlas --static application/atlas`; keep its token-bearing output/connection file private. No additional service is implemented here.

The usable read-only CLI entry is:

```sh
node "$ACCESS/read.mjs" "$ACCESS/access.json" info
node "$ACCESS/read.mjs" "$ACCESS/access.json" search --query "user's scientific terms"
node "$ACCESS/read.mjs" "$ACCESS/access.json" describe --destination DESTINATION_ID
node "$ACCESS/read.mjs" "$ACCESS/access.json" connections --destination DESTINATION_ID --limit 30
node "$ACCESS/read.mjs" "$ACCESS/access.json" connections --destination DESTINATION_ID --relation-id RELATION_ID --include-proof
node "$ACCESS/read.mjs" "$ACCESS/access.json" sources --destination DESTINATION_ID --limit 20
node "$ACCESS/read.mjs" "$ACCESS/access.json" sources --destination DESTINATION_ID --collection contributions --limit 20
node "$ACCESS/read.mjs" "$ACCESS/access.json" context --id UNIT_ID --section objects --offset 0 --limit 20
node "$ACCESS/read.mjs" "$ACCESS/access.json" compute --destination DESTINATION_ID
```

`compute` executes the unchanged `bin/navigate.mjs compute --atlas` command. Other commands delegate to the same `loadLocalAtlas`, navigator and read-only runtime methods used by CLI/MCP. There is no independent retrieval, semantic resolver or navigation engine. Mutating commands and arbitrary flags are rejected. Every result carries the exact manifest SHA. `describe` returns the complete scientific record, canonical selector and prepared URL fragment; the fragment is not advertised as installed on the public site. Search is lexical title/alias lookup; the fresh navigator must interpret prose and inspect full scope, reading limits, sources and route qualification.

The evaluator first freezes reading/query expectations separately. Fresh navigators receive only the portable skill, this access entry, natural-language queries and response requirements. They receive no expected destination IDs, prior scientific campaign answers or hidden oracle routes. Preserve their actual tool calls and exact returned selector/proofs. The evaluator and root compare results after the independent responses are frozen. No model calls are launched by this package. This read-only exercise cannot establish browser rendering; fresh-agent → rendered-browser and public HTTPS/default/scoped-consent checks remain separate final-release gates.

Validation before any real staging: three Python tests cover exact pre-holdout accounting, immutable hash-verified hard links and unsafe paths; one Node test exercises actual runtime/CLI search, describe, compute, sources and connections, rejects mutations/foreign arguments, and detects manifest changes. Three existing final-ingress tests now additionally reject incomplete accounting or reserved cases even when legacy partial booleans are absent. The final ingress guard itself remains separate and requires `sourceAccountingComplete:true` and `reservedQuestionCount:0`.

Current status: mechanics prepared and tested; geometry-bound frozen input pending. No real access directory, generated HTML, held-out navigation result, browser success or publication is claimed yet.
