import psutil
import socket

def collect_network():
    interfaces = {}
    for name, addrs in psutil.net_if_addrs().items():
        interfaces[name] = []
        for addr in addrs:
            family = str(addr.family)
            interfaces[name].append({
                "family": family,
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
            })

    interface_stats = {}
    for name, stat in psutil.net_if_stats().items():
        interface_stats[name] = {
            "is_up": stat.isup, "duplex": str(stat.duplex),
            "speed_mbps": stat.speed, "mtu": stat.mtu
        }

    listeners = []
    listener_status = "MEASURED"
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.status == psutil.CONN_LISTEN or (conn.type == socket.SOCK_DGRAM and conn.laddr):
                listeners.append({
                    "family": str(conn.family),
                    "type": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                    "local_address": getattr(conn.laddr, "ip", None),
                    "local_port": getattr(conn.laddr, "port", None),
                    "status": conn.status,
                    "pid": conn.pid,
                })
    except (psutil.AccessDenied, OSError) as exc:
        listener_status = "NOT_TESTED"
        listener_error = str(exc)
    else:
        listener_error = None

    result = {"interfaces": interfaces, "interface_stats": interface_stats,
              "listeners": listeners, "listeners_status": listener_status}
    if listener_error:
        result["listeners_reason"] = listener_error
    return result
