# Architecture and phased roadmap

## Implemented in starter 0.1
1. Cross-platform read-only local inventory.
2. Basic health and storage metrics via psutil.
3. Local listener enumeration where OS permissions allow.
4. Bounded recent log collection using native commands.
5. JSON report with explicit limitations.
6. FastAPI central intake with SQLite.
7. Bilingual starter dashboard.
8. Approval workflow stub that records approval but intentionally does not execute repair commands.

## Recommended next phases
### Phase 2 — Identity and secure fleet enrollment
- Device enrollment tokens with rotation.
- Per-agent identity and TLS.
- API authentication, RBAC, tenant separation, and audit retention.
- PostgreSQL migration and database migrations.

### Phase 3 — Richer native collectors
- Windows Event Log/CIM/Defender/BitLocker adapters.
- Linux distro-specific patch, journal, SMART/NVMe and firewall adapters.
- macOS unified logs, FileVault, update and security configuration adapters.
- Capability matrix with NOT_TESTED states.

### Phase 4 — Security baseline
- Versioned CIS-aligned configuration checks where licensed/appropriate.
- CVE matching against trustworthy package inventory and vendor advisories.
- Evidence, confidence, severity, and false-positive review.

### Phase 5 — Approved remediation
- Signed, versioned action catalog.
- Policy evaluation, two-person approval for high-risk actions.
- Backup/snapshot, rollback and post-action verification.
- No arbitrary LLM-generated command execution.

### Phase 6 — Reporting and operations
- PDF/XLSX exports, history comparison, fleet filters, scheduled jobs.
- Alerting and retention policy.
- Packaging and OS-specific integration tests.

## Threat model highlights
- Treat logs, process names, package metadata and remote scan results as untrusted.
- Protect against command injection, path traversal, data leakage, unauthorized agent enrollment, and privilege escalation.
- Bind local API to loopback by default.
- Add authentication and TLS before any remote exposure.
- Keep sensitive data out of logs and reports unless explicitly needed.
