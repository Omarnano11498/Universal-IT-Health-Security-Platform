import psutil

def collect_health():
    vm = psutil.virtual_memory()
    cpu = {}
    try:
        cpu = {"logical_cpus": psutil.cpu_count(logical=True),
               "physical_cpus": psutil.cpu_count(logical=False),
               "cpu_percent_sample": psutil.cpu_percent(interval=0.2)}
    except Exception as exc:
        cpu = {"status": "NOT_TESTED", "reason": str(exc)}

    disks = []
    for part in psutil.disk_partitions(all=False):
        item: dict[str, object] = {
            "device": part.device,
            "mountpoint": part.mountpoint,
            "filesystem": part.fstype,
            "options": part.opts,
        }
        try:
            usage = psutil.disk_usage(part.mountpoint)
            item.update({"total_bytes": usage.total, "used_bytes": usage.used,
                         "free_bytes": usage.free, "percent_used": usage.percent,
                         "status": "MEASURED"})
        except (PermissionError, OSError) as exc:
            item.update({"status": "NOT_TESTED", "reason": str(exc)})
        disks.append(item)

    batteries = None
    try:
        battery = psutil.sensors_battery()
        if battery is not None:
            batteries = {"percent": battery.percent, "plugged_in": battery.power_plugged,
                         "seconds_left": battery.secsleft if battery.secsleft >= 0 else None}
    except Exception:
        batteries = {"status": "NOT_TESTED", "reason": "Battery telemetry unavailable"}

    return {
        "cpu": cpu,
        "memory": {"total_bytes": vm.total, "available_bytes": vm.available,
                   "used_bytes": vm.used, "percent_used": vm.percent},
        "disks": disks,
        "battery": batteries,
        "boot_time_epoch": psutil.boot_time(),
        "process_count": len(psutil.pids()),
    }
