# Exact final installation handoff

Prepared only; no installation or deployment was performed. Root must first accept
the final rendered-browser/independent-agent result. The scientific package and its
frozen manifest remain unchanged by installation.

The read-only audit is:

```sh
python3 research/q025/assembly/final-release-v1/install.py
```

After that explicit acceptance, run from the repository root:

```sh
python3 research/q025/assembly/final-release-v1/install.py \
  --install \
  --approved-manifest-sha256 15b2dc99f216462e7d0deaec9f16b4de416cf0a291c76bcda6b973cd3b4ff3cb \
  --report research/q025/assembly/final-release-v1/installation-receipt.json
```

This narrow installer verifies the frozen handoff, delivery list, manifest and
external asset plan; checks every compressed/original byte count and SHA-256;
screens delivered JSON for private absolute paths and credential-like strings;
copies regular files into a temporary version directory; verifies the copies; and
selects the new version in the discovery index last. It refuses to overwrite an
existing immutable version. Existing discovery entries remain intact. It does not
commit, deploy, change scientific data or change the frozen publication status.
The explicit command flag records the operator's release gate, not another science
admission or an automatic inference from successful QA.

Only these new public paths should be tracked:

```text
data/atlas/index.json
data/atlas/q025-approved-organization-candidate/2026-11-17-post-test-accounted-v1/**
```

The package contains 7,680 files / 486,811,841 bytes (464.26 MiB), plus the small
discovery index. Of these, 910 package files occupy 233,627,984 bytes; 6,735 source
context files occupy 217,456,068 bytes; and 35 supplemental proof/policy/route files
occupy 35,727,789 bytes. The largest file is the 7,021,318-byte catalog. All external
assets exist locally and are copied from the exact descriptors: the installed tree
has no dependency on the owner's filesystem, FASRC, a download service or LFS.

Do not recursively copy the research directory. In particular, do not publish the
asset plan with private `sourcePath` values, aggregate/native inputs, full primary
archives, geometry matrices, handoff/assembly scratch reports or recovery tar. The
checksummed public `delivery-assets.json`, source/context objects, locators and
scientific proof records are intentionally included.

After installation, root runs the existing sequence:

```sh
npm run build
npm test
npm run check:site
```

Measure the actual `dist` inventory before committing. The frozen estimate is
18,833 files, including a 500-file ordinary-site reserve; seven original-ID redirect
pages also consume that reserve. There are 10,653 current destination pages. The
site checker enforces 20,000 files and 25 MiB per file. No old research packages
should be copied alongside this version. Existing historical public versions, if
any, must be counted as well.

The existing GitHub workflow only checks out Git, runs `npm ci`, build/test/site
checks, then deploys `dist` through the existing Wrangler configuration on a push
to `main` (or a manual dispatch). It has no external fetch and no LFS checkout.
Therefore commit the actual installed data files as ordinary Git blobs with the
final code; committing only research hashes or an overlay receipt is insufficient.
Root should verify the committed file inventory and a clean-checkout build before
merging/deploying. `dist` remains generated and ignored.

This payload is below GitHub's enforced 100 MB single-object and 2 GB push limits.
The flat immutable directory exceeds its 3,000-entry width recommendation; keep the
frozen paths and use hashes/clean-build verification rather than GitHub's limited
diff UI. No LFS conversion is needed for these file sizes. Limits checked against
[GitHub's repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)
on 17 November 2026. This is a size assessment, not a guarantee of network push or
deployment success.

Finally verify the live manifest hash and sampled `.json.gz` compressed bytes.
The exact frozen manifest is
`15b2dc99f216462e7d0deaec9f16b4de416cf0a291c76bcda6b973cd3b4ff3cb`;
HTTP content handling must not silently alter the pinned compressed bytes.
