# Pre-holdout access is ready

The exact frozen geometry-bearing package is staged under the private `research/q025/integration/native-local/preholdout-access-v1` directory. `access-ready.json` records its hashes and the actual read-only smoke checks. No reserved scientific records or evaluation questions were inspected.

From the repository root:

```sh
node research/q025/integration/native-local/preholdout-access-v1/read.mjs \
  research/q025/integration/native-local/preholdout-access-v1/access.json info
```

Replace `info` with `search --query TEXT`, `describe --destination ID`, `connections --destination ID`, `sources --destination ID`, bounded `context --id UNIT_ID`, or stateless `compute --destination ID`. These call the existing navigator and CLI. The static JSON entry is `application/atlas/manifest.json` inside that private access directory; it resolves the exact catalog/detail/source inventory. This is not generated HTML or a public installed version.

Frozen manifest: `62b2444c60f743adc9569d33ffe475211c9770d48f05abf5b976843e4e8d920c`; runtime commit: `17662cfb306191499b447af97f0b6d1b9270c8cd`. All 7,694 linked files were hash verified, with zero source payload copies. Only the metadata-only all-physics entrance was smoke-tested: describe and actual CLI compute agree, with 17 field choices. No model call or browser mutation test occurred.

Evaluator expectations, independent read-only navigators, and later fresh-agent rendered-browser acceptance are separate phases. The test version explicitly retains 43 reserved cases and fails the final-release accounting guard. The hard-linked data must never be written, chmodded, or used for mutation tests.
