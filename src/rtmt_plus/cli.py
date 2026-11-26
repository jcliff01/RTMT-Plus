"""CLI entry point for streaming RTMT/CUCM log search."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime
import json
import os
import sys

from . import rtmt
from .search import search

FIELDS = ["path", "line", "timestamp", "call_id", "cause", "cause_text", "text"]


def safe_csv(value: object) -> object:
    """Prevent spreadsheet formula interpretation for untrusted log fields."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def print_rtmt_info(install: rtmt.RtmtInstall) -> None:
    java = rtmt.find_java()
    print(f"RTMT folder:     {install.root}")
    print(f"RTMT version:    {install.version or 'unknown'}")
    trace = install.trace_download_path
    status = "" if trace is None else (" (exists)" if trace.is_dir() else " (not found on this computer)")
    print(f"Trace downloads: {trace or 'not set'}{status}")
    print(f"Cause catalogs:  {', '.join(sorted(install.catalogs)) or 'none'}")
    ok = "OK" if rtmt.java_supported(java) else "RTMT 15 needs Java 1.8.0_300+ (Java 8)"
    print(f"Java:            {java or 'not found'} - {ok}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search local CUCM/RTMT log files")
    parser.add_argument("paths", nargs="*",
                        help="Files or folders to search (default with --rtmt-home: RTMT's trace download folder)")
    parser.add_argument("-q", "--query", help="Text or regular expression")
    parser.add_argument("--regex", action="store_true", help="Interpret query as regex")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--since", type=datetime.fromisoformat, help="ISO timestamp, e.g. 2026-11-17T09:00:00")
    parser.add_argument("--until", type=datetime.fromisoformat)
    parser.add_argument("--call-id", help="Exact call ID on matching lines")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum results (default 1000)")
    parser.add_argument("--format", choices=("text", "jsonl", "csv"), default="text")
    rt = parser.add_argument_group("Cisco RTMT integration (uses your local RTMT install)")
    rt.add_argument("--rtmt-home", help=f"RTMT install folder (or set {rtmt.ENV_VAR})")
    rt.add_argument("--cause-catalog", default="ucm", choices=sorted(rtmt.CATALOG_FILES),
                    help="RTMT cause-code table used to decode causes (default ucm)")
    rt.add_argument("--rtmt-info", action="store_true", help="Show detected RTMT install details and exit")
    rt.add_argument("--launch-rtmt", action="store_true", help="Start Cisco RTMT and exit")
    args = parser.parse_args(argv)

    install = None
    try:
        if args.rtmt_home or args.rtmt_info or args.launch_rtmt or os.environ.get(rtmt.ENV_VAR):
            install = rtmt.load_install(args.rtmt_home)
        if args.rtmt_info:
            print_rtmt_info(install)
            return 0
        if args.launch_rtmt:
            rtmt.launch(install)
            print(f"Started RTMT {install.version or '(unknown version)'} from {install.root}")
            return 0
        if not args.query:
            parser.error("the following arguments are required: -q/--query")
        paths = args.paths
        if not paths:
            if install is None or install.trace_download_path is None:
                parser.error("give a file or folder to search (or --rtmt-home with a trace download path set)")
            paths = [install.trace_download_path]

        matches = search(paths, args.query, regex=args.regex,
                         ignore_case=not args.case_sensitive, since=args.since,
                         until=args.until, call_id=args.call_id, limit=args.limit)
        writer = None
        if args.format == "csv":
            writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
            writer.writeheader()
        for match in matches:
            row = match.to_dict()
            row["cause_text"] = install.describe(match.cause, args.cause_catalog) if install else None
            if writer:
                writer.writerow({key: safe_csv(row[key]) for key in FIELDS})
            elif args.format == "jsonl":
                print(json.dumps(row, ensure_ascii=False))
            else:
                cause = ""
                if match.cause is not None:
                    cause = f" [cause {match.cause}{': ' + row['cause_text'] if row['cause_text'] else ''}]"
                print(f"{match.path}:{match.line} [{match.timestamp or 'no timestamp'}] {match.text}{cause}")
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"rtmt-plus: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
