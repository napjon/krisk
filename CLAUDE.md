# Krisk Development

- Preserve traditional pandas/Jupyter use without requiring a server, MCP, or database.
- Keep REST and MCP thin; all behavior belongs in `KriskService` or lower layers.
- Never persist or log connection URLs, credentials, or environment-variable values.
- MCP/REST chart specifications must remain declarative and reject executable JavaScript.
- Use `uv` for Python and `bun` for JavaScript. Do not use pip, npm, or yarn.
- Bind the unauthenticated v1 server to loopback on port 8060.
- Do not add Postgres or Redis containers; local development uses the shared infrastructure.
- Do not modify legacy notebooks merely to normalize their outputs.
