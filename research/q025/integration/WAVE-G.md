# Contribution delivery and prepared-first agent guidance

Q-025 integration checkpoint, 2026-11-17. Runtime and owned evidence are frozen for
root verification. No accepted scientific atlas is installed and no deployment
was performed.

Typed source contributions remain separate from primary/context membership and
USING. The existing source reader now accepts `collection:"contributions"` and
returns paginated roles, reading basis, qualifications, review/evidence references
and source excerpts without changing the session. Browser disclosures group rows
by paper and load scientific context only when opened. Static pages expose the
same contributions, archived locators and optional compressed context. Coverage
links retain bibliographic-only unavailable-source records.

A supported question with zero primary/context members is valid when the pinned
index declares both counts zero and the membership sample is empty. It loads as
complete empty membership, keeps its contributions, and never turns those roles
into primary membership or established method applicability. Positive counts or
nonempty samples still require the full checksummed membership descriptor.

QA14 job **61478210** completed in 29 seconds with all five browser checks passing
and zero page errors. A synthetic contribution-only question has three roles from
two paper groups, primary0/USING0, readable source context and inventory links.
Actual stdio MCP navigation receives the exact browser render acknowledgement at
state `state-d0e8c42ae8044de6`, revision1. Mobile width and scroll width are both390.
[Report](qa14/report.json) · [mobile](qa14/contribution-only-mobile.png) ·
[connected browser](qa14/contribution-only-connected.png).

The original failures remain unchanged. QA11 timed out after the MCP checks;
QA12's added diagnostics identified the disclosure passing bare contribution rows
to the frozen source reader instead of using already-verified bundled sources.
QA13 passed grouped rendering/context but failed the mobile overflow assertion:
long unit IDs needed wrapping. QA14 fixes both. Its inventory request also uses an
absolute same-origin URL; the earlier relative URL was corrected before that test
was reached. [QA11](qa11/report.json) · [QA12](qa12/report.json) ·
[QA13](qa13/report.json).

Local build, all76 tests, site checks and skill validation pass. The independent
semantic audit separately verified the pinned-zero and contribution-reader gates;
its report is maintained by the auditor. The original frozen corpus is unchanged.
Prepared-first skill guidance, MCP descriptions, CLI help and singular status copy
were amended after the browser archive; exact differences and hashes are recorded
in [the wording ledger](wave-g-post-qa14.json). No browser behavior changed in those
five amendments. Evidence/context disclosures start collapsed; screenshots
intentionally expanded them.

Limitations: QA14 uses isolated Slurm Chromium and a synthetic fixture; it is not
scientific acceptance, an independent research-agent routing journey, public
HTTPS-to-loopback evidence or operation of the owner's Chrome. The public default
policy and exact-origin simulated-consent harness is prepared but unexecuted.
Final accepted data still requires fresh-document performance, scientific journeys,
combined asset limits, public source hashes and public connected-browser checks.
