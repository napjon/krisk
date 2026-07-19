---
name: save-research-notebook
description: Convert a completed data-analysis conversation into evidence-backed, reproducible living research through the Krisk MCP server. Use when a user asks to save an investigation, formalize its research methodology, preserve point-in-time charts, create executable conclusion checks, or export the work as a Jupyter notebook or static/live HTML report.
---

# Save Research Notebook

Turn an explicitly concluded investigation into a structured Krisk research record and export. Preserve observed evidence; never invent or silently recompute facts.

## Workflow

1. Confirm that the user wants to save the work. Do not persist an ordinary in-progress conversation.
2. Identify the research question, hypothesis if any, ordered methodology, findings, conclusion, and limitations from the conversation.
3. Reuse only query IDs and chart IDs returned by Krisk tools. If a necessary claim lacks evidence, run a new read-only query and show its result before saving.
4. Distinguish observations from inferences. State the capture time or data cutoff for every point-in-time finding.
5. Read [references/research-schema.md](references/research-schema.md) before constructing `save_research` input.
6. Read [references/claim-types.md](references/claim-types.md) when a conclusion can be checked against future data. Keep subjective or causal conclusions narrative-only.
7. Show the proposed conclusion, limitations, and executable claims to the user. Resolve material corrections before saving.
8. Call `save_research` once. Then call `export_research` when the user requested a notebook or HTML export.
9. Return the research ID, artifact locations, snapshot timestamp, and the command or link used to refresh live evidence.

## Evidence Rules

- Treat MCP query output as observation; treat interpretation as inference.
- Include query and chart references in the structured record, not credentials or connection URIs.
- Preserve the original snapshot and conclusion even when current data differs.
- Use a typed claim only when one bounded query returns the scalar values needed to evaluate it.
- Record missing data, sampling choices, filters, failed queries, and alternative explanations as limitations.
- If Krisk MCP is unavailable, stop before claiming the research was saved and provide the local setup command.

## Failure Handling

- If a referenced query or chart no longer exists, recreate the evidence with the user’s knowledge; never substitute an unrelated record.
- If a claim query returns more than one row, revise it to a one-row metric query before saving.
- If export fails, retain the saved research ID and report the export failure separately.
- If current data cannot be fetched, keep the static snapshot usable and mark live validity as unknown.
