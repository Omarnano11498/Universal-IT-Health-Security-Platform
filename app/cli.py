import argparse
import json
from pathlib import Path
import requests
from app.scanner import run_scan

def main():
    parser = argparse.ArgumentParser(description="Universal IT Health & Security local scanner")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Run a read-only local scan")
    scan.add_argument("--out", default="reports/scan.json", help="Output JSON path")
    scan.add_argument("--no-logs", action="store_true", help="Skip bounded recent-log collection")
    scan.add_argument("--post", help="Optional authorized central API endpoint, e.g. http://127.0.0.1:8000/api/scans")
    args = parser.parse_args()

    if args.command == "scan":
        result = run_scan(include_logs=not args.no_logs)
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Scan completed: {result['scan_id']}")
        print(f"Report written to: {output}")
        print(f"Findings: {len(result.get('findings', []))}")
        if args.post:
            response = requests.post(args.post, json=result, timeout=15)
            response.raise_for_status()
            print(f"Central server response: {response.status_code} {response.text}")
if __name__ == "__main__":
    main()
