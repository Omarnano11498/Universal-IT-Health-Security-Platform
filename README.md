# Universal IT Health & Security Platform

An initial runnable version for inspecting Windows, Linux, and macOS devices, featuring a centralized API and a simple interactive web dashboard.

## Overview
The Universal IT Health & Security Platform provides read-only local health and security baseline checks across multi-platform desktop and server environments. It collects key system metrics, exposes a central API for receiving and serving report data, and offers an intuitive web UI for monitoring device status.

## What Works in This Version?
- **Read-Only Local Scanning:** System information, CPU/RAM usage, disk space, network interfaces, listening ports, and process summaries.
- **Centralized API:** Endpoints to initiate local scans, receive inspection reports, and query scan history.
- **Interactive Web Dashboard:** Available in both English and Arabic, allowing users to trigger scans, view and filter recent results, and export reports in JSON format.
- **JSON Reporting:** Standardized, structured output for local and remote consumption.
- **Explicit Scan Re-Run Prompting:** Clarifies consent before re-running a scan; does not execute auto-remediations or destructive system commands.
- **Automated Testing:** Suite of unit tests covering core functionality.

## Scope & Limitations
This version is **not** a formal compliance audit tool or a comprehensive vulnerability scanner. It does not test for every known exploit, guarantee physical hardware integrity, or perform offensive network scanning. Certain data metrics require elevated system privileges or native platform tools. Unavailable metrics are explicitly marked as such rather than assumed successful.

## Prerequisites
- **Python:** 3.10 or higher
- **Package Manager:** `pip`

## Installation

### Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Running a Local Scan
```bash
python -m app.cli scan --out reports/scan.json
```
*Note: The scanner collects data exclusively from the host device in read-only mode and does not probe other network hosts.*

## Launching the Web Dashboard
```bash
python -m uvicorn app.server:app --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser and click **Start Local Scan**. From the interface, you can refresh results, filter metrics, switch languages, and download JSON reports.

> **Security Notice:** The server binds to `127.0.0.1` (loopback) by default. Do not expose this interface to public or untrusted networks without configuring HTTPS, authentication, and proper network access controls.

## Submitting Scan Results via CLI
Ensure the server is running locally, then execute:
```bash
python -m app.cli scan --post http://127.0.0.1:8000/api/scans
```

### Primary API Endpoints
- `GET /api/health` – Server health status check.
- `POST /api/scan` – Triggers an on-demand local scan.
- `GET /api/scan/results` – Fetches the latest scan results.

## Running Tests
Run the test suite using `pytest`:
```bash
python -m pytest -q
```

## Security & Best Practices
- **Authorization:** Only collect data from hosts you own or have explicit authorization to inspect.
- **Privileges:** Avoid running the application as `Administrator` or `root` unless specifically required for accessing restricted metrics.
- **Scope Assurance:** Scan results provide basic observability indicators and are not definitive proof of security. The tool does not perform automatic remediation or remote host scanning.
- **Production Readiness:** The default SQLite storage is intended for development and local testing. For enterprise deployment, configure PostgreSQL, robust authentication, and TLS encryption.