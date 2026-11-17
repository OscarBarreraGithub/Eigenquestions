# Preserved final run-v2 and corrected overview check

Job 61597266 used code a17c9ea3f7e660e4154172f574304bad14315722 and scientific manifest 15b2dc99f216462e7d0deaec9f16b4de416cf0a291c76bcda6b973cd3b4ff3cb. Its original result remains failed; twelve text/source/mobile checks passed with zero page errors. Classification, detailed schematic entrance, zoom/click and mobile detail screenshots were captured before the timeout.

The final return attempted `goto` on the same overview document with only a changed fragment. The overview reads its initial fragment at startup; same-document fragment navigation did not rerun startup. The harness then waited for seventeen physics-field buttons while the detail space remained open. This is a harness/UI-action mismatch, not a scientific-package failure. The original report's phase label predates the overview portion; the exact failing call is retained in browser/report.json and browser.log.

The bounded correction uses the existing “All physics fields” control and records the overview phase. No map engine or scientific data changed. The separate supplemental run on code 756df26acf233424154edbf6ef5290f01f778cfd passes all thirteen core checks, including the corrected return. This does not rewrite run-v2 as a pass.

The observer started in a separate observer-only allocation (61597944), retaining the same a17 runtime and immutable scientific manifest. Fresh agents alone choose its navigation; supplemental scripted checks use a different project, bridge and Chromium context.
