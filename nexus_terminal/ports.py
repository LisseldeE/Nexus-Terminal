"""Port listing utility — shows ports currently in LISTEN state."""

import socket
import subprocess
import re


def get_listening_ports():
    """Get all listening ports on the local machine.

    Uses 'netstat -ano' (available on Windows, Linux, macOS).
    Returns a list of dicts: {protocol, local_addr, local_port, pid, state}
    """
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout
    except Exception:
        return []

    ports = []
    seen = set()

    for line in output.splitlines():
        line = line.strip()
        if not line or 'LISTEN' not in line.upper():
            continue

        # Parse netstat line:
        # Proto  Local Address    Foreign Address  State    PID
        # TCP    0.0.0.0:5000     0.0.0.0:0        LISTENING  1234
        # TCP    [::]:5000        [::]:0           LISTENING  1234
        parts = line.split()
        if len(parts) < 5:
            continue

        proto = parts[0]
        local = parts[1]
        state = parts[3] if len(parts) > 4 else ''
        pid_str = parts[-1]

        # Extract port from local address (format: addr:port or [addr]:port)
        if ':' not in local:
            continue

        # Handle IPv6 [::]:port format
        if local.startswith('['):
            addr = local.rsplit(']', 1)[0].strip('[]')
            port_part = local.rsplit(']', 1)[1].lstrip(':')
        else:
            addr, port_part = local.rsplit(':', 1)

        try:
            port = int(port_part)
        except ValueError:
            continue

        try:
            pid = int(pid_str)
        except ValueError:
            pid = 0

        # Deduplicate by (port, proto)
        key = (port, proto)
        if key in seen:
            continue
        seen.add(key)

        ports.append({
            'protocol': proto,
            'address': addr,
            'port': port,
            'pid': pid,
            'state': state,
        })

    ports.sort(key=lambda p: p['port'])
    return ports


def get_process_name(pid):
    """Get process name for a PID. Returns 'Unknown' if not available."""
    if pid == 0:
        return 'Unknown'
    try:
        import ctypes
        from ctypes import wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            return 'Unknown'

        try:
            buf = ctypes.create_unicode_buffer(260)
            if ctypes.windll.psapi.GetProcessImageFileNameW(handle, buf, 260):
                # Return just the filename, not full path
                return buf.value.rsplit('\\', 1)[-1]
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        pass
    return 'Unknown'


def format_ports(ports, messages):
    """Format listening ports for display. Returns list of output lines."""
    if not ports:
        return [messages['ports_none']]

    lines = []
    for p in ports:
        proc_name = get_process_name(p['pid'])
        proto_tag = p['protocol']
        addr = p['address'] or '*'
        local = f'{addr}:{p["port"]}'
        lines.append(
            f'  {proto_tag:<4} {local:<24} PID {p["pid"]:<8} {proc_name}'
        )

    return lines
