# Executable Claim Types

Every claim uses a saved one-row query. Set `value_column` to the observed scalar column and provide a stable label.

## Threshold

Use `kind: threshold` with `operator` equal to `gt`, `gte`, `lt`, `lte`, `eq`, or `neq` and a scalar `expected` value.

## Range

Use `kind: range`, `operator: between`, `expected` as the inclusive minimum, and `maximum` as the inclusive maximum.

## Comparison

Use `kind: comparison`, set `compare_column` to a second scalar column returned by the same query, and choose the operator comparing `value_column` with it.

## Change

Use `kind: change` when the metric query returns a current value and a baseline/comparison column. Express the intended comparison directly with `compare_column` and the operator.

## Status Semantics

- `pass`: the predicate holds.
- `warn`: it holds but is within an explicitly provided numeric `warning_tolerance` of its boundary.
- `fail`: the predicate does not hold.
- `unknown`: data refresh, schema validation, or evaluation failed.

Do not add a warning tolerance unless the research context justifies it. Do not turn causal, subjective, or multi-factor prose into a scalar claim merely to make it executable.
