# Q-007 — Visible child choices and unassigned excerpts

UI owner/reviewer: `/root/quiet_ui_review_sol` (Sol). Astra owns the overview
controller and browser regression; root owns the notebook, integration and release.

The previous overview changed the camera when a group was selected, while its
main list continued to show the broad groups. Genuine child buttons appeared
below a long description. This obscured the available smaller groups.

The coordinated sidebar now puts the actual next choices first. Its heading
distinguishes broad groups, finer groups and source questions; an ancestor path
and a 44px parent/back button provide return navigation. The same primary list
holds genuine children or source questions. A source-title/arXiv-ID filter sits
directly above a leaf source list. A separate Browse source questions action
keeps internal-group source memberships accessible without inventing another
cluster level. Descriptions and provenance remain below those controls.

The DOM adds `overview-topic-path`, `overview-topics-back`,
`overview-topic-context`, `overview-source-filter-field`,
`overview-source-filter`, `overview-browse-sources` and `overview-unassigned`.
Existing source/details and map selectors are preserved. The unassigned reading
bucket is a separate, quieter 44px action labeled **Unassigned excerpts (13)**,
rather than a major physics-topic caption. Its points and source records remain
part of the unchanged frozen dataset.

HTML parsing confirms balanced elements and 24 unique IDs, including every
agreed selector. No Mac browser was launched. Actual child/back behavior,
source filtering, phone fit and visual hierarchy require the integrated Slurm
screenshots before visual signoff; no acceptance is claimed yet.
