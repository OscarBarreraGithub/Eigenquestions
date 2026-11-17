# Prepared overview geometry interface

Agreed with the product adapter before scientific selection; no selected layout
has yet been computed. The overview is an optional chart of accepted destinations,
not a force plot of274,565 scientific source objects and not the definition of
scientific adjacency.

```json
{
  "overview": {
    "layoutId": "versioned-layout-id",
    "kind": "diffusion_chart",
    "sourceCandidateId": "selected-organization-id",
    "referenceGraphSha256": "exact-graph-hash",
    "membershipSha256": "exact-membership-hash",
    "nodes": [
      {"destinationId": "accepted-id", "x": 0.0, "y": 0.0, "mass": 1.0, "depth": 0}
    ],
    "edges": [
      {"source": "accepted-id", "target": "other-id", "kind": "geometric_affinity", "weight": 1.0}
    ],
    "provenance": {
      "operator": "lazy_random_walk",
      "diffusionTime": 4,
      "retainedModes": 2,
      "coordinateTransform": "declared common scaling and translation only"
    },
    "diagnostics": {
      "coverage": "Explicit question/region subset and source count",
      "components": 1,
      "twoDimensionalDistanceDistortion": "measured after selection"
    },
    "limitations": [
      "The plane is a lossy navigation chart; proximity is not scientific implication or equivalence."
    ]
  }
}
```

For accepted direct membership matrix H with row sums one, form the complete
coarse flow C=H^T W H, including the diagonal. Compute nonconstant modes of the
lazy random walk P=(I+D^-1 C)/2; coordinates use lambda^t psi. Preserve that
relative scaling rather than independently standardizing each axis, which would
cancel the time factor. A declared common scale/translation fits the viewport.
Disconnected components need an explicit display-packing convention and separate
distance qualifications. Zero/degenerate modes require an honest fallback.

All destination IDs must resolve in the selected catalog. Ancestors can use
membership-weighted centroids in the same fixed chart, so zooming and nested views
preserve orientation. Report the actual covered subset and comparison of2D with
retained higher-dimensional diffusion distances. If source graph choice differs
from candidate construction, say so in provenance; no universal metric is implied.

Containment, reviewed destination navigation and source-science relations remain
separate typed data. The renderer fits/zooms stored coordinates and selected
destinations/children; it does not invent coordinates or use positions to create
edges. Physics-wide metadata landmarks remain text outside this latent chart until
compatible coverage is computed.
