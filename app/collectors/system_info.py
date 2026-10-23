import platform
import socket
import os
from datetime import datetime, timezone

def collect_system_info():
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "is_admin": _is_admin(),
    }

def _is_admin():
    try:
        if os.name == "nt":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return hasattr(os, "geteuid") and os.geteuid() == 0
    except Exception:
        return False
