---
name: voltpeer-review-audit
description: Audit a near-complete battery Review or Perspective before submission for scope, evidence, metrics, figures, and consistency. Use for a preflight findings list, not copyediting or rebuttal.
---

# Whole-manuscript battery Review audit

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Reply in the user's language with the result, usable result/preview links and material unresolved questions. Keep mappings, configuration, logs and recovery records inside the project's `.voltpeer/` folder; do not link them in a normal final reply. Provide the corresponding source record only when the user explicitly requests provenance. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this when the user asks whether a draft is scientifically and structurally ready. Identify the manuscript version, current project brief, source access, target venue if any, and requested depth. An audit is a check of the supplied artifact, not an independent referee persona or a language-only edit.

## Inspect in decision order

1. **Identity and contribution:** compare title, abstract, central judgement, section sequence, display items, and conclusion with the current brief and close competing Reviews. Flag scope drift and claims of “first” without proof.
2. **Evidence:** sample or fully check consequential numeric, mechanism, safety, cost, scale-up, priority, and negative claims against original sources according to the task. Distinguish source not obtained (`NV`) from source checked but field unreported (`NR`). Identify unsupported paragraph-end citation clusters and missing counterevidence.
3. **Battery comparability:** inspect tables and graphics for cell type, package, branch/cycle, denominator, loading, electrolyte, N/P or other inventory, operating conditions, uncertainty, and reported versus modelled status. Do not accept unconditional ranking of incomparable results.
4. **Display integrity:** compare figure and table assertions to the caption and source. Inspect final-size layout, panel geometry, scale bars and axes. Record rights per reused panel. Use the local [figure evidence audit](references/FIGURE_EVIDENCE_AUDIT.md) for composite figures, digitized data, schematic arrows, or artwork changes.
5. **Consistency and package:** read the exported files. Check the actual embedded figures, native chemical notation, captions, cross-references, bibliography and declarations. Compare clean and marked text when both are in scope. Obtain current official journal rules for the exact article type through `voltpeer-submission` when requested.

Report findings by severity with exact manuscript location, why each matters, evidence checked, proposed correction, and whether it blocks submission. Separate `verified`, `not checked`, and `author decision` items. An attractive draft with unresolved central evidence or missing rights is not ready; a draft with only minor prose issues may be. Do not claim all citations were checked if the audit sampled them, and do not silently rewrite the authors' scientific position.
