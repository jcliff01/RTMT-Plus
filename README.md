# RTMT Plus

Advanced search, correlation, and troubleshooting for Cisco Unified Communications Manager (CUCM) RTMT logs.

> **Status:** Early development. Local log search is available through the Python CLI and an optional desktop UI. Not affiliated with or endorsed by Cisco.

## Get started

- [Install and search logs](docs/GETTING_STARTED.md) with Python 3.10 or newer.
- [Download a CI build or package the Windows EXE](docs/WINDOWS_BUILD.md).

## Vision

RTMT Plus is a standalone, local-first desktop companion to Cisco Real-Time Monitoring Tool (RTMT). It helps engineers search large log collections, correlate events across CUCM nodes, and reconstruct troubleshooting timelines without modifying Cisco's proprietary software.

## Planned capabilities

- Import downloaded RTMT / CUCM trace and log files.
- Full-text and regular-expression search across multiple files.
- Filter by timestamp, severity, host, device, IP address, extension, and call identifiers where available.
- Normalize timestamps and correlate events across cluster nodes.
- Trace SIP signaling and call disconnect causes.
- Export filtered results and incident timelines.
- Support large log collections with incremental indexing.

## Roadmap

### Phase 1 — Search Foundation
Desktop UI, file import, indexing, regex search, time filters, and CSV/JSON export.

### Phase 2 — Correlation
Cross-node event timelines, call-ID matching, SIP dialog reconstruction, and saved searches.

### Phase 3 — Monitoring
Optional read-only integrations with supported Cisco Serviceability, RISPort, and PerfMon interfaces; dashboards and alert views.

### Phase 4 — Diagnostics
Rule-based detection of recurring issues, optional AI-assisted explanations, and privacy-preserving root-cause workflows.

## Proposed stack

- **Python 3.12+** for application logic.
- **PySide6** for a Windows-first desktop interface.
- **SQLite (FTS5)** for local search indexing.
- **pytest** for automated tests.
- Pluggable parsers for log formats and version-specific Cisco data.

## Architecture

```text
Desktop UI (PySide6)
       |
Search / Correlation / Analytics
       |
Parser + Normalization + Local Index
       |
Downloaded CUCM/RTMT logs
       |
Optional supported read-only Cisco APIs (future)
```

## Security and privacy

- Local-first processing; no default cloud upload.
- Do not commit production traces, credentials, customer data, or call-detail records.
- Redact sensitive identifiers in sample logs and reports.
- Future API integrations must use least-privilege credentials and secure storage.
- Log timestamps, formats, and available fields vary by CUCM release; parsers must be validated against representative sanitized samples.

## Planned layout

```text
src/rtmt_plus/
  ui/
  parsers/
  search/
  correlation/
  integrations/
  analytics/
tests/
docs/
examples/sanitized_logs/
```

## Development milestones

1. Import a folder of logs and display indexed files.
2. Search across logs with text/regex and time-range filters.
3. Correlate messages by call ID and node.
4. Export a shareable troubleshooting report.
5. Add live integrations only after confirming API compatibility and permissions.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Cisco, CUCM, and RTMT are trademarks of their respective owners. RTMT Plus is an independent community project.
