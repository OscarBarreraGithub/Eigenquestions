# Public job v1: packaging failure before browser execution

Job 61605316 was submitted after the deployed aeda8e75 commit and scientific manifest 15b2dc99 were verified. The build completed with 18,454 files. Site check then rejected a missing newly linked repository receipt, `research/q025/integration/final-acceptance/supplement-v1/receipt.json`.

The reused a17 archive plus application-only overlay matched all executable application files, but did not include the newly committed evidence referenced by the final documentation. No public browser, permission-policy test or passive observer ran. This is an incomplete QA envelope, not a deployed runtime or scientific-package failure. Original logs remain in artifacts/.

Root authorized a separate v2 submission after complete committed-tree verification. Its delta includes every changed committed non-data file plus the exact installed discovery index. All 10,364 final committed files, 778,642,287 bytes, match the union of base archives, committed delta and declared atlas assets. The older equivalent-home discovery metadata was also replaced by the exact committed file. No application/scientific file changed, and no new release gate was inferred.
