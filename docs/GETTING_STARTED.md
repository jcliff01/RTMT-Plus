# Getting started

The [README](../README.md) has the full steps for Windows, macOS and Linux: downloading the Windows program, installing with Python, and every search option.

## Current limitations

- RTMT Plus is a separate program, not a Cisco RTMT plugin.
- Search reads every file each time; it doesn't build an index yet, so very large folders are slow.
- Timestamps are recognized only when written like `2026-11-17 09:00:00`.
- Call IDs are recognized by common labels (`Call-ID:`, `GlobalCallId=`), which vary by trace type.
- The search window pauses while a large search runs.
- No live connection to CUCM and no automatic diagnosis yet.
- Never commit customer or production logs.
