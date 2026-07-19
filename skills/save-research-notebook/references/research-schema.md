# Research Record Schema

Construct `save_research` input with these fields:

- `question`: the precise research question.
- `hypothesis`: optional expectation stated before interpreting evidence.
- `methodology`: ordered, reproducible actions including filters, grouping, aggregations, and comparisons.
- `query_ids`: every saved query used as evidence or by a claim.
- `chart_ids`: every saved point-in-time chart included in the research.
- `findings`: concise observations supported by the referenced evidence.
- `conclusion`: the answer at the snapshot’s point in time; do not rewrite it on later refresh.
- `limitations`: data-quality issues, scope boundaries, assumptions, and non-causal interpretations.
- `claims`: optional executable claims following `claim-types.md`.

Do not submit the full conversation transcript. Do not include passwords, connection URLs, API keys, raw environment variables, or unsupported claims.

Before saving, confirm that the methodology enables another analyst to reproduce the same query and chart results and that each numerical statement maps to a query or chart ID.
