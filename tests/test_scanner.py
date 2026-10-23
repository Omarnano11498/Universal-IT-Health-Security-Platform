from app.scanner import build_findings, run_scan

def test_low_disk_space_warning():
    scan = {"health": {"disks": [{"status":"MEASURED","percent_used":95,"mountpoint":"/"}]},
            "network": {"listeners_status":"MEASURED"}}
    findings = build_findings(scan)
    assert any(f["title"] == "Low free disk capacity" for f in findings)

def test_limited_scope_not_claimed_secure():
    scan = {"health": {"disks":[]}, "network":{"listeners_status":"MEASURED"}}
    findings = build_findings(scan)
    assert findings[0]["status"] == "LIMITED_SCOPE"
    assert "does not establish" in findings[0]["recommendation"]


def test_run_scan_collects_local_data_without_logs():
    scan = run_scan(include_logs=False)
    assert scan["status"] == "COMPLETED"
    assert scan["scope"] == "LOCAL_DEVICE_READ_ONLY"
    assert scan["system_info"]["hostname"]
    assert "memory" in scan["health"]
    assert "interfaces" in scan["network"]
    assert scan["logs"]["status"] == "SKIPPED"
    assert scan["summary"]["total_findings"] == len(scan["findings"])
