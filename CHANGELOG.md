# Changelog

Krisk follows semantic versioning after its historical `0.3.x` releases. Version
`1.0.0` has never been published.

## 0.9.0 — beta

This is the first integrated Chartics/Flarisk preview. It is currently available from
the repository rather than as a published package release.

### Added

- typed `ChartSpec` charts for notebooks, Python, REST, and MCP;
- self-contained ECharts 6 HTML and rich Jupyter output;
- local dashboard, REST API, Streamable HTTP MCP, and stdio MCP;
- named CSV/Parquet and PostgreSQL data sources;
- SQLite metadata and content-addressed Parquet snapshots by default;
- structured research records, typed claims, and current-data evaluation;
- static/live HTML reports and Jupyter notebook exports;
- portable `save-research-notebook` skill;
- source health, fingerprints, query provenance, and accessible table fallbacks.

### Security hardening

- read-only single-statement SQL parsing and result limits;
- disabled DuckDB external access for local sources;
- blocked file, network, extension, and administrative table functions;
- executable JavaScript rejection in typed chart overrides;
- snapshot row and serialized-size gates before artifact publication;
- loopback-only server binding unless explicitly overridden.

### Compatibility

- traditional notebook and Python charting works without the server;
- the original `krisk.plot` helpers remain available;
- the Flarisk `/simpleRequestServer` demonstration route remains as deprecated
  compatibility behavior.

### Not yet a 1.0 release

The `0.9` server is intended for a trusted local user and does not include multi-user
authentication or authorization. Shared production deployment, formal relational
migrations, and broader PostgreSQL integration coverage remain future `1.0` work.
