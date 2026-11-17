# Two preserved whitespace failures

The original 0002 and 0007 proposals each contain a single JSON response attempt. All 32 and 30 source placement rows, respectively, are complete and match the row schema and full paired-annotation inventory. Both then write the first proposed scope through its scientific definition, methods, reading coverage and refs, and stop before required `revisesRef`. The streams end with 4,213 and 4,776 spaces outside strings. Neither is truncated, and neither is a complete valid JSON reply.

The first proposed scope's only missing record field is `revisesRef`; the newScopes array and the required top-level prior-review/limitations/unresolved tail are not complete. No missing value or array is inferred, no failed receipt is marked complete, and no model is restarted. Exact completed fields and value-byte ranges are preserved in ignored private extraction records; the public report exposes only structure, counts and hashes.

The matching location suggests a representation/formatting stall around the revision marker, rather than loss of all completed source reasoning. It does not prove that the empty-string convention caused the loop. The earlier parent whitespace failure used repeated tabs; this instance uses spaces and the frozen outside-string guard stopped it early. Output-density estimates are not completion guarantees.

A bounded successor can retain the 62 finished placement rows and every completed n0 field, request only the missing tail and any explicit required revision reference, then obtain an independent challenge of the resulting complete proposal. Future unstarted requests could use an explicit nullable no-revision marker through a separately pinned derivation/contract; frozen original inputs must not be edited. Such a change is a proposal for root review, not an adopted recovery.

See `report.json` for exact original receipts, streams, parser identity and extraction hashes. The source parser function was isolated through its AST; importing the historical script's state-mutating top level was avoided. No raw reasoning trace or primary text is published.
