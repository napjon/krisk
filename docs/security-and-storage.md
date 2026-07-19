# Security and storage

Krisk `0.9` is a trusted-local-user application, not a multi-tenant analytics gateway.
Its defaults reduce accidental exposure, but they do not replace database permissions,
authentication, or operating-system isolation.

## What uses SQLite?

SQLite is the default for Krisk's own metadata:

- saved query text and source fingerprints;
- chart specifications and snapshot pointers;
- research methodology, findings, conclusions, limitations, and claims.

The default file is `var/krisk/krisk.db`. SQLite is sufficient for the normal local
server and survives process restarts. Traditional `Chart.from_dataframe(...)` usage
does not touch this database.

## When is PostgreSQL used?

There are two separate, optional uses:

1. A named `kind = "postgres"` source lets Krisk read an external database.
2. `DATABASE_URL` replaces internal SQLite metadata for an intentionally shared
   deployment.

Configuring one does not configure the other. Most users should keep SQLite for
internal metadata even when querying an external PostgreSQL source.

## Files and artifacts

| Location | Content | Mutability |
| --- | --- | --- |
| `var/krisk/krisk.db` | local metadata | updated as records are saved |
| `var/krisk/artifacts/` | content-addressed Parquet snapshots | immutable by digest |
| `var/krisk/exports/` | generated HTML and notebooks | user-managed output |

Use `KRISK_DATA_DIR` to relocate the whole local data directory, or
`KRISK_DATABASE_PATH` to relocate only the SQLite database.

## SQL boundary

MCP and REST queries must be one `SELECT` or `WITH` statement. Krisk parses SQL before
execution and rejects mutation, administrative statements, external table functions,
file readers, network-backed scanners, and unknown relations for local DuckDB sources.

For file and in-memory sources, Krisk also disables DuckDB external access and locks
that setting before running the query. Configured CSV and Parquet files are materialized
as named relations; SQL cannot supply an arbitrary filesystem path.

For PostgreSQL, use a role with database-enforced read-only access to only the schemas
the LLM is allowed to inspect. Application filtering is defense in depth, not a reason
to grant the role broader permissions.

## Resource limits

- query result limit: 10,000 rows;
- chart snapshot limit: 10,000 rows;
- serialized snapshot limit: 5 MiB;
- local DuckDB query timeout: 30 seconds;
- query preview returned to the LLM: first 200 rows by default.

Aggregate or downsample before charting larger datasets.

## Credentials and provenance

PostgreSQL URLs are read from environment variables named by `url_env`. Connection
strings are not stored in query records, chart snapshots, research records, notebooks,
or HTML exports.

Source fingerprints intentionally describe relation structure rather than credentials.
File fingerprints use relation names, sizes, and modification times; PostgreSQL
fingerprints use visible relation names. They are provenance signals, not secrets.

## Network boundary

The server binds to `127.0.0.1` by default and has no user authentication. CORS is
limited to the supported loopback origins, but CORS is not authentication. Do not make
the server reachable from an untrusted network.

`KRISK_ALLOW_INSECURE_REMOTE_BIND=1` permits a non-loopback bind for development. It
does not make that deployment secure. Before any shared deployment, add TLS,
authentication, per-user authorization, audit logging, secret management, and source
access isolation in front of Krisk.

## Export boundary

HTML and notebook exports intentionally contain snapshot values and saved SQL because
they are evidence artifacts. Review them before sharing. They do not contain source
credentials, and the Live view does not embed its later responses into the static file.

Typed chart overrides reject executable JavaScript. Text rendered into HTML and live
status messages is escaped. As with any research artifact, conclusions and snapshot
values may still be sensitive even when credentials are absent.
