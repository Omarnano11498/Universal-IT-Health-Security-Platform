import logging
import uuid
from datetime import datetime, timezone

from app.collectors.health import collect_health
from app.collectors.logs import collect_recent_logs
from app.collectors.network import collect_network
from app.collectors.system_info import collect_system_info

logger = logging.getLogger(__name__)


def _collect(name, collector):
    try:
        return collector()
    except Exception as exc:
        logger.exception("The %s collector failed", name)
        return {"status": "NOT_TESTED", "reason": str(exc)}


def build_findings(scan):
    findings = [{
        "title": "Limited assessment scope",
        "severity": "INFO",
        "status": "LIMITED_SCOPE",
        "recommendation": (
            "This read-only local scan does not establish that the device is secure "
            "or replace a complete security assessment."
        ),
    }]

    health = scan.get("health") or {}
    memory = health.get("memory") or {}
    if memory.get("percent_used", 0) >= 90:
        findings.append({
            "title": "High memory utilization",
            "severity": "MEDIUM",
            "status": "OBSERVED",
            "recommendation": "Review memory-consuming applications and confirm whether the load is expected.",
        })

    cpu = health.get("cpu") or {}
    if cpu.get("cpu_percent_sample", 0) >= 90:
        findings.append({
            "title": "High CPU utilization",
            "severity": "MEDIUM",
            "status": "OBSERVED",
            "recommendation": "Review CPU utilization over time and identify expected or unexpected workloads.",
        })

    for disk in health.get("disks", []):
        if disk.get("status") == "MEASURED" and disk.get("percent_used", 0) >= 90:
            findings.append({
                "title": "Low free disk capacity",
                "severity": "MEDIUM",
                "status": "OBSERVED",
                "mountpoint": disk.get("mountpoint"),
                "recommendation": "Review disk usage and safely remove or archive unnecessary files.",
            })
    return findings


def run_scan(include_logs=True):
    scan = {
        "scan_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETED",
        "scope": "LOCAL_DEVICE_READ_ONLY",
        "system_info": _collect("system information", collect_system_info),
        "health": _collect("health", collect_health),
        "network": _collect("network", collect_network),
        "logs": (
            _collect("recent logs", collect_recent_logs)
            if include_logs
            else {"status": "SKIPPED", "entries": []}
        ),
    }
    scan["findings"] = build_findings(scan)
    scan["summary"] = {
        "total_findings": len(scan["findings"]),
        "critical": sum(item["severity"] == "CRITICAL" for item in scan["findings"]),
        "high": sum(item["severity"] == "HIGH" for item in scan["findings"]),
        "medium": sum(item["severity"] == "MEDIUM" for item in scan["findings"]),
        "info": sum(item["severity"] == "INFO" for item in scan["findings"]),
    }
    return scan
