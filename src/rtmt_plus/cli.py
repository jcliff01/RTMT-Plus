"""CLI entry point for streaming RTMT/CUCM log search."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime
import json
import sys

from .search import search

def safe_csv(value: object) -> object:
    """Prevent spreadsheet formula interpretation for untrusted log fields."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search local CUCM/RTMT log files")
    parser.add_argument("paths", nargs="+", help="Files or folders to search")
    parser.add_argument("-q", "--query", required=True, help="Text or regular expression")
    parser.add_argument("--regex", action="store_true", help="Interpret query as regex")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--since", type=datetime.fromisoformat, help="ISO timestamp, e.g. 2026-11-17T09:00:00")
    parser.add_argument("--until", type=datetime.fromisoformat)
    parser.add_argument("--call-id", help="Exact call ID on matching lines")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum results (default 1000)")
    parser.add_argument("--format", choices=("text", "jsonl", "csv"), default="text")
    args = parser.parse_args(argv)
    try:
        matches = search(args.paths, args.query, regex=args.regex,
                         ignore_case=not args.case_sensitive, since=args.since,
                         until=args.until, call_id=args.call_id, limit=args.limit)
        if args.format == "csv":
            writer = csv.DictWriter(sys.stdout, fieldnames=["path", "line", "timestamp", "call_id", "text"])
            writer.writeheader()
            for match in matches:
                writer.writerow({key: safe_csv(value) for key, value in match.to_dict().items()})
        else:
            for match in matches:
                if args.format == "jsonl":
                    print(json.dumps(match.to_dict(), ensure_ascii=False))
                else:
                    print(f"{match.path}:{match.line} [{match.timestamp or 'no timestamp'}] {match.text}")
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"rtmt-plus: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
