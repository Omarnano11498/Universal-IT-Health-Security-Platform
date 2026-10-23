# Security notes

This is an initial development scaffold, not a production-secure fleet manager.

- The API has no authentication in this version.
- Bind to 127.0.0.1 only.
- Do not publish the API to a LAN or the internet.
- Only submit reports from authorized devices.
- Reports can contain hostnames, addresses, process identifiers and logs. Treat them as sensitive.
- Keep original logs unchanged; exported summaries may need redaction.
- The approval endpoint records approval but does not execute system modifications.
- Before production deployment, add TLS, authentication, RBAC, enrollment, audit integrity, rate limits, secrets management, database migrations, and a formal threat-model review.
