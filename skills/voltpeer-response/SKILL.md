---
name: voltpeer-response
description: Draft and verify point-by-point responses to editor and reviewer comments on a battery Review, with traceable manuscript revisions.
---

# Reviewer response and resubmission

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Reply in the user's language with the result, usable result/preview links and material unresolved questions. Keep mappings, configuration, logs and recovery records inside the project's `.voltpeer/` folder; do not link them in a normal final reply. Provide the corresponding source record only when the user explicitly requests provenance. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this for received peer-review comments or manuscript revision after review. Use [RESPONSE_MATRIX.md](assets/templates/RESPONSE_MATRIX.md) only if the project lacks a better format. For a new independent referee report, use `voltpeer-reviewer` and keep it separate from response drafting.

## Received reviews: point-by-point map

Freeze the received letter and submitted version before editing. For each numbered point, retain the reviewer's exact wording and references to the submitted version. Record the underlying issue, decision, action, revised location, evidence and reply. Map old citations or figure labels to the revision with stable identifiers such as DOI or source panel. Preserve a direct answer to each numbered point when several points share one revision.

Before writing a rebuttal, verify the proposed scientific correction. For a battery-performance dispute, recheck cell type, branch, denominator, loading, electrolyte, N/P, cycling baseline, temperature, and whether a figure mixes measured and modelled values. If the evidence remains thin, narrow the claim and say so. Do not invent a new experiment, permission, source, or author approval.

Lead with the actual answer, evidence, or manuscript change. State a substantive withdrawal or correction plainly at the point that asks for it. On related points, explain what that choice changes for the specific concern. Cite the revised location after the answer. Keep author-supplied wording verbatim where requested and preserve any limitation that changes the answer.

## Revision consistency gate

Apply approved changes to the manuscript and dependent files. Read back the final Word and PDF, including embedded figure labels and table captions. Search surfaces that could still carry a retired framework. Compare the response excerpts verbatim with the final text, and derive revised page or line references from the author-facing export after pagination. Use the same final source for clean and marked copies and synchronize SI, both language versions of the response, and the cover letter as applicable.

Report point coverage, checked locations, and remaining evidence or author decisions. Reserve “re-reviewed” for a separate review of the revised file. Keep confidential reviewer materials within the authorized project.
