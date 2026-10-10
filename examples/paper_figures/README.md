# Complete analytic Figure examples

Three independent, reproducible teaching models show how related panels form one Figure:

- **Cycling:** charge/discharge capacity, CE, retention relative to cycle 5, matching voltage profiles and a separate rate protocol.
- **Solvation methods:** two declared Gaussian spectral components and analytic RDFs with coordination integrals. These are not MD trajectories or identified species.
- **Operando structure:** an illustrative FCC lattice, Bragg-consistent peaks, a process map, selected scans and an illustrative voltage trace. This is not a claimed real cathode.

The data, model parameters, scientific checks and figure manifest are saved together. No private experiments, microscopy or published Figure pixels are included. Read the generated captions and input contract before using a template for author data. A clean calculation check does not certify an experimental mechanism.

From this repository root:

```bash
python examples/paper_figures/render_figure.py demo --kind cycling --output outputs/my-cycling-demo
python skills/voltpeer-assemble/scripts/compose_figure.py compose --manifest outputs/my-cycling-demo/rendered/manifest.json --out outputs/my-cycling-figure --strict --svg
```

Use `solvation` or `operando` for the other model. Always choose a new output directory/stem. To redraw saved inputs, run `render_figure.py render --config DEMO/inputs/config.json --output NEW_FOLDER`; do not regenerate inputs when recolouring. Add `--palette-lock PATH/palette.lock.json` to use a selected, hash-checked literature palette. The render report records the source CSV hashes and sample colours.

The source ZIPs linked from the website are self-contained: extract **source** and **CSV/configuration** into the same new directory and follow their README. They include the matching plotting and assembly runtime. Existing published installer ZIPs retain their original versions.

PNG previews, PDF and SVG share a physical-size composition. Text and paths in SVG remain editable; embedded raster matrices remain raster. Check final-size typography and the actual target journal's dimensions before manuscript use. Layout references document organization principles; these outputs do not reproduce a cited paper's results.

The manifests include measured plot rectangles and explicit `alignment_guides` for shared outer edges, row tops/bottoms and widths. These work across different column spans. Colourbars and CE labels occupy separate margins; equal outer panel boxes alone do not establish that data frames align. Version 1.0.1 corrects the outer alignment of the cycling and operando examples while retaining their original CSV values.

Original code, analytic inputs and figures: MIT. Literature colour records: attributed CC BY 4.0 selections with observed/used colours and explicit adjustments. Original paper Figures are not redistributed.
