# Getting started

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux for CLI; Windows-first desktop UI
- Locally downloaded, authorized CUCM/RTMT logs

## Install

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[desktop,dev]"
```

## Search from terminal

```bash
rtmt-plus ./logs --query "ERROR"
rtmt-plus ./logs -q "SIP/2.0 503" --format csv > matches.csv
rtmt-plus ./logs -q "Call-ID" --since 2026-11-17T09:00:00 --format jsonl
rtmt-plus ./logs -q "disconnect|timeout" --regex --limit 500
```

## With Cisco RTMT

```bash
rtmt-plus --rtmt-home "C:\Program Files\Cisco\RTMT15" --rtmt-info
rtmt-plus --rtmt-home "C:\Program Files\Cisco\RTMT15" -q "cause="
```

See [RTMT_INTEGRATION.md](RTMT_INTEGRATION.md).

## Desktop

```bash
rtmt-plus-desktop
```

Choose a folder containing downloaded log files, type a search term, and click Search.

## Tests

```bash
python -m pytest
```

## Current limitations

- This is an initial release, not a Cisco RTMT plugin.
- Search is streaming, not yet indexed; very large folders may be slow.
- Timestamp parsing recognizes generic ISO-style dates only.
- Call-ID matching is heuristic and format-dependent.
- Desktop search runs synchronously and may temporarily freeze on large folders.
- No live CUCM connection or automatic root-cause diagnosis yet.
- Never commit customer or production logs.
