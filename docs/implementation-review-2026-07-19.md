# Krisk 1.0 Implementation Review

**Date:** 2026-07-19
**Scope:** Working-tree rewrite of `krisk` against the MCP-native living research plan
**Reviewer:** Grok (read-only review; no code changes)

## Verdict

This is a real, coherent 1.0-shaped rewrite: typed charts, local REST+MCP, snapshots, research export, skill package, modern packaging, and green unit gates. Traditional notebook charting still works without a server.

It is **not yet plan-complete or ship-safe as 1.0.0**. The biggest gap is query sandboxing: file sources can still read arbitrary paths. Several plan items are simplified or missing, and a few security/correctness holes remain.

---

## What works well

| Area | Evidence |
|------|----------|
| Packaging | `pyproject.toml` + uv/hatch, Python 3.11–3.14, GitHub Actions, wheel builds with skill + ECharts 6.1 |
| Chart surface | All planned kinds compile; legacy `kk.bar/line/hist/...` kept; pie/KPI/sunburst wrappers added |
| Self-contained HTML | Embedded ECharts, no CDN/RequireJS in modern `to_html` / mimebundle path |
| Service core | Query → chart snapshot → research → claim evaluate → export round-trip tested |
| Live vs snapshot | Export HTML does **not** embed post-export values; refresh returns new data; snapshot hash unchanged (verified) |
| Local defaults | SQLite + Parquet under `var/krisk` is a pragmatic zero-config choice (README documents it) |
| Port claim | `PORTS.md` lists krisk on **8060 loopback** |
| Skill skeleton | `skills/save-research-notebook/` has SKILL.md, schema/claim refs, `agents/openai.yaml` |
| Gates (local) | `ruff` / `ruff format` / `mypy` (9 files) / **50 pytest** / `python -m build` all pass |

Architecture matches the spirit of the plan: thin REST/MCP → `KriskService` → sources/storage/compiler.

---

## Critical / high severity

### 1. File-source sandbox is broken (bug)

`validate_readonly_sql` only blocks DDL/DML-ish statements. DuckDB table functions still run:

```sql
SELECT * FROM read_csv_auto('/etc/hosts')
```

Verified: accepted and returns host file contents via `FileSource` **and** `FrameSource`. Same class of issue for Postgres if the role can call things like `pg_read_file` / `lo_import` — both are currently **accepted** by the guard.

Plan required: allowlisted dirs only, reject unrestricted file access, unsafe functions.

**Fix direction:** deny-list (or allow-list) function calls in the SQL AST (`read_csv*`, `read_parquet`, `read_blob`, `read_text`, `glob`, `postgres_scan`, `pg_read_file`, etc.), and/or run DuckDB with disabled external access / restricted views only.

### 2. `safe_overrides` JS rejection is incomplete (bug)

Strings containing `"function"` are blocked; arrow functions are not:

```python
safe_overrides={"tooltip": {"formatter": "() => 1"}}  # currently accepted
```

Plan: reject function strings / executable JS on MCP/REST specs.

### 3. Shared artifact can be deleted on size failure (bug)

```python
digest, path, size = self.artifacts.save_frame(snapshot)
if size > 5 * 1024 * 1024:
    path.unlink(missing_ok=True)  # content-addressed path may be shared
```

Size should be checked **before** promoting the object into the content-addressed store, and unlink must not remove a digest already referenced by another chart.

### 4. Version / milestone mismatch

Package is **`1.0.0`** while several plan acceptance items for living research / security / MCP transport tests are unfinished. Shipping this label oversells readiness.

---

## Medium severity (plan or product gaps)

### Query / sources

- Plan: Ibis-backed Postgres + DuckDB/Ibis files, `SourceAdapter` with relation discovery, schema, fingerprint, health.
- Code: direct `psycopg` / `duckdb`, no fingerprint/health, `ibis-framework` is largely unused (only `from_ibis` via `.to_pandas()`/`execute`).
- No enforced **snapshot row cap** (only query limit + post-hoc 5 MiB).
- File sources: no statement timeout; params unsupported (OK if documented).
- No provenance fingerprint on query records.

### Storage

- Plan: relational migrations (queries / charts / snapshots / research), upgrade/downgrade tests.
- Code: generic `krisk_records(kind, id, payload)` blob store (SQLite or Postgres). Works, but weak for integrity, indexing, and migration story.
- Failed-write cleanup / migration downgrade not tested.

### MCP / REST / CLI

- Tools present: list/inspect/run/create/refresh/save/evaluate + `export_saved_research` (plan name was `export_research`).
- Resources: research + chart snapshot only — missing **current chart data** and **exports**.
- No MCP in-memory / dual-transport tests (plan required).
- CLI `research export` always writes both formats — no `--format ipynb|html|both`.
- `export`/`output_dir` can write anywhere the process can write (acceptable for trusted local use; still worth documenting/restricting).

### Charts / accessibility

- Typed histogram ignores **density** (legacy `kk.hist(..., density=True)` still works).
- Limited a11y: ARIA on ECharts options yes; plan’s **tabular fallback** largely absent (only a short description paragraph).
- Legacy `_repr_javascript_` still injects **jQuery + RequireJS** path; modern mimebundle is self-contained. Classic Notebook may still hit the old path.
- `set_tooltip_format` still injects raw JS function strings (legacy); not clearly marked deprecated for local-only use.

### Research / claims / exports

- Claim `kind` is stored but **not enforced** in evaluation (range/comparison/change all share one operator path).
- `warn` uses `abs(observed - expected) ≤ tolerance` while still passing — OK for “near threshold value,” but not documented as “near failure band for one-sided ops.”
- Research HTML has snapshot/live tabs and claims on live refresh; static export does not embed a claims section or “sources and provenance” / “reproduction instructions” as fully as the plan’s section list.
- Skill present, but **no `quick_validate.py`** or scripted mock-MCP scenarios from the plan.
- No browser E2E for static-with-server-down / refresh / claim transitions.

### Repo hygiene

- Large **notebook diffs** (~60k lines on `tidy-plot.ipynb` alone) despite project guidance not to normalize notebooks. High noise for review/merge.
- Untracked junk risk: `notebooks/root@163.172.156.124` (HTML), `notebooks/gap.html`, old `krisk.egg-info` / egg in `dist/`.
- Plan gate `bun test` vs actual `bun run test` (`node --check`); bare `bun test` finds nothing.

### mypy scope

- Typed only on new modules; `krisk/chart/core.py` and `plot/*` are outside mypy files list — fine short-term, weak for a “1.0 typed” claim.

---

## Test status (what was run)

```
ruff check          pass
ruff format --check pass
mypy                pass (9 files)
pytest              50 passed
bun run test        pass (syntax check only)
uv build            krisk-1.0.0 wheel includes skill + echarts + krisk-live.js
```

**Not covered by tests:** file escape, arrow-function overrides, artifact unlink race, MCP client, Postgres adapter, browser export, skill validation.

---

## Plan coverage scorecard

| Milestone | Status |
|-----------|--------|
| **0.4 Foundation** | Mostly done (pyproject, CI, security intent, eval/nbextension path reduced). Notebook noise + dual legacy render remain. |
| **0.5 Typed charts** | Strong core parity; density/a11y/theme polish incomplete. |
| **0.6 Data + MCP** | Vertical slice works; sandbox/fingerprint/migrations/MCP transport tests short of plan. |
| **1.0 Living research** | End-to-end path exists; skill/docs/demo lighter than plan; browser + claim matrix incomplete. |

---

## Priority fix list (pre-1.0 cut)

1. **Block DuckDB/Postgres file and admin functions** in `validate_readonly_sql` (AST-level); add regression tests that currently fail open.
2. **Harden `safe_overrides`** (reject any string value under executable keys; reject `=>` / `function` / callables everywhere under overrides).
3. **Fix snapshot size gate** before content-addressed publish; never unlink an existing digest.
4. Add MCP client tests + file-adapter escape tests.
5. Drop or rebrand version to **0.6.x / 0.9.0** until sandbox + acceptance gaps close — or finish the plan items above before keeping `1.0.0`.
6. Revert unrelated notebook churn; delete/ignore the `root@…` artifact.
7. Align `bun test` / CI script naming with the plan.

---

## Bottom line

The rewrite successfully turns a 2016-era ECharts binder into a **usable local research toolkit** with the right shape: typed specs, immutable snapshots, MCP tools, living HTML/notebook export, and a portable skill. The implementation is thoughtfully simplified (SQLite default, document store) in ways that still fit local single-user use.

The SQL layer and override sanitizer are **not 1.0-ready** until the file-escape and executable-override holes are closed and tested. Everything else is polish, depth, and plan fidelity rather than structural failure.
