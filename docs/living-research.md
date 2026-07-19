# Living research and claims

Living research separates two questions that ordinary dashboards often blur:

1. **What evidence supported the conclusion at the time?**
2. **Does the conclusion still hold for the current data?**

Krisk answers the first with immutable snapshots and the second with optional live
queries and claims.

## Research record

A saved record contains:

- the research question and optional hypothesis;
- ordered methodology steps;
- IDs of the saved SQL queries and chart snapshots used as evidence;
- findings observed in that evidence;
- a conclusion and explicit limitations;
- optional machine-checkable claims.

Example payload:

```json
{
  "question": "Does recorded revenue remain above 600?",
  "hypothesis": "The recorded total is at least 600.",
  "methodology": [
    "Inspected the sales relation and its columns.",
    "Summed revenue and plotted monthly values."
  ],
  "query_ids": ["MONTHLY_QUERY_ID", "TOTAL_QUERY_ID"],
  "chart_ids": ["CHART_ID"],
  "findings": ["Captured revenue totals 647."],
  "conclusion": "Recorded revenue is above 600 at capture time.",
  "limitations": ["The source contains recorded revenue, not audited revenue."],
  "claims": [
    {
      "label": "Revenue remains at least 600",
      "kind": "threshold",
      "query_id": "TOTAL_QUERY_ID",
      "value_column": "value",
      "operator": "gte",
      "expected": 600,
      "warning_tolerance": 25
    }
  ]
}
```

Krisk verifies that every referenced query and chart exists. The skill instructs the
LLM to save the structured result only after the user agrees with the conclusion; it
does not archive the entire private conversation by default.

## Claim types

Each claim query must return exactly one row containing `value_column`.

| Kind | Required shape | Example |
| --- | --- | --- |
| `threshold` | scalar operator and `expected` | revenue `gte` 600 |
| `range` | `between`, numeric minimum, and `maximum` | error rate between 0 and 2 |
| `comparison` | scalar operator and `compare_column` | actual `gte` target |
| `change` | scalar operator and `compare_column` | current `lt` previous |

Scalar operators are `gt`, `gte`, `lt`, `lte`, `eq`, and `neq`. Range claims use
`between`. `warning_tolerance` turns a passing value near a boundary into `warn`; it
does not turn a failing value into a pass.

Claim states:

- `pass`: the current value satisfies the claim;
- `warn`: it passes but is within the configured boundary tolerance;
- `fail`: it does not satisfy the claim;
- `unknown`: the query, source, column, or one-row result is unavailable.

## Export anatomy

HTML reports and notebooks include:

- the question, methodology, findings, conclusion, and limitations;
- saved query IDs, source names, source fingerprints, and SQL;
- immutable chart data captured as Parquet;
- a static ECharts view and accessible data table;
- claim status evaluated at export time;
- reproduction instructions;
- live URLs that are separate from the embedded evidence.

The notebook stores snapshot Parquet in a dedicated MIME output so another tool can
recover the evidence without scraping rendered chart markup.

## Snapshot and Live tabs

The Snapshot tab reads only embedded data. It remains available when the source,
database, or Krisk server is offline.

The Live tab calls `/api/v1/charts/{chart_id}/current`. The server reruns the saved SQL
against the source currently registered under the same name, recompiles the chart, and
returns current claim states. The response includes the original snapshot hash so the
client can show that historical evidence was not replaced.

## Reproducibility limits

A source fingerprint records source structure and relation metadata without credentials.
It helps detect obvious source drift, but it is not a cryptographic digest of an entire
external database. For long-lived or regulated research, also retain source-specific
version identifiers, data-release dates, and the database change policy in the
limitations or methodology.
