import platform
import subprocess

def collect_recent_logs(limit=40):
    """
    Conservative cross-platform log summary. Reads only a bounded tail from
    supported native commands. Does not clear or alter source logs.
    """
    system = platform.system()
    if system == "Linux":
        command = ["journalctl", "-n", str(limit), "--no-pager", "-o", "short-iso"]
    elif system == "Darwin":
        command = ["log", "show", "--last", "1h", "--style", "compact", "--info"]
    elif system == "Windows":
        # PowerShell query is read-only and bounded to recent System events.
        command = ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                   f"Get-WinEvent -LogName System -MaxEvents {int(limit)} | "
                   "Select-Object TimeCreated,Id,LevelDisplayName,ProviderName,Message | "
                   "ConvertTo-Json -Depth 3"]
    else:
        return {"status": "NOT_TESTED", "reason": "Unsupported operating system", "entries": []}

    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=15,
                                   check=False, errors="replace")
        if completed.returncode != 0:
            return {"status": "NOT_TESTED",
                    "reason": (completed.stderr or "Log command unavailable")[:1000],
                    "entries": []}
        output = completed.stdout[-100_000:]
        return {"status": "COLLECTED", "source": command[0], "entries_text": output}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "NOT_TESTED", "reason": str(exc), "entries": []}
