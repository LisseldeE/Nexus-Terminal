"""Port scanner — scan remote hosts for open ports."""

import socket
import itertools
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# Top 20 most common ports with service names
COMMON_PORTS = [
    (21, 'FTP'),
    (22, 'SSH'),
    (23, 'Telnet'),
    (25, 'SMTP'),
    (53, 'DNS'),
    (80, 'HTTP'),
    (110, 'POP3'),
    (143, 'IMAP'),
    (443, 'HTTPS'),
    (445, 'SMB'),
    (993, 'IMAPS'),
    (995, 'POP3S'),
    (1433, 'MSSQL'),
    (1521, 'Oracle'),
    (3306, 'MySQL'),
    (3389, 'RDP'),
    (5432, 'PostgreSQL'),
    (5900, 'VNC'),
    (6379, 'Redis'),
    (8080, 'HTTP-Alt'),
    (8443, 'HTTPS-Alt'),
    (27017, 'MongoDB'),
]

SCAN_TIMEOUT = 2
MAX_THREADS = 100


def _scan_port(host, port):
    """Scan a single port on the given host.

    Returns (port, open) tuple.
    """
    try:
        with socket.create_connection((host, port), timeout=SCAN_TIMEOUT):
            return port, True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return port, False


def _parse_port_spec(spec):
    """Parse a port specification string into a list of ports.

    Supported formats:
      '80'           -> [80]
      '80,443,8080'  -> [80, 443, 8080]
      '1-1000'       -> [1, 2, ..., 1000]
      '80,443,8000-8100' -> combination
      ''             -> None (use common ports)
    """
    if not spec or not spec.strip():
        return None

    ports = []
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > 65535 or start > end:
                    return None
                ports.extend(range(start, end + 1))
            except ValueError:
                return None
        else:
            try:
                p = int(part)
                if p < 1 or p > 65535:
                    return None
                ports.append(p)
            except ValueError:
                return None

    return sorted(set(ports))


def _get_service_name(port):
    """Get service name for a port, preferring common ports list."""
    for p, name in COMMON_PORTS:
        if p == port:
            return name
    try:
        return socket.getservbyport(port)
    except OSError:
        return ''


def scan_ports(host, ports, messages):
    """Scan ports on a host and display results.

    Args:
        host: Target hostname or IP address.
        ports: List of port numbers to scan, or None for common ports.
        messages: i18n messages dict.

    Returns:
        Exit code (0 or 1).
    """
    # Resolve hostname
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        print(messages['scan_host_not_found'].format(host=host))
        return 1

    if ports is None:
        port_list = [p for p, _ in COMMON_PORTS]
    else:
        port_list = ports

    print()
    print(messages['scan_starting'].format(host=host, ip=ip, count=len(port_list)))
    print(messages['scan_separator'])
    print()

    open_ports = []
    scanned = 0
    total = len(port_list)
    last_progress = [0]
    lock = threading.Lock()

    def progress_callback():
        nonlocal scanned
        with lock:
            scanned += 1
            # Show progress every 10%
            pct = scanned * 100 // total
            if pct // 10 > last_progress[0] // 10:
                last_progress[0] = pct
                sys.stdout.write(
                    f'\r  {messages["scan_progress"].format(pct=pct)}'
                )
                sys.stdout.flush()

    # Use ThreadPoolExecutor for concurrent scanning
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {}
        for port in port_list:
            future = executor.submit(_scan_port, host, port)
            futures[future] = port

        for future in as_completed(futures):
            port, is_open = future.result()
            if is_open:
                service = _get_service_name(port)
                open_ports.append((port, service))
            progress_callback()

    # Clear progress line
    print('\r' + ' ' * 60 + '\r', end='')

    print(messages['scan_separator'])
    if open_ports:
        print(f'  {messages["scan_open_ports"]} ({len(open_ports)}/{total}):')
        print()
        for port, service in sorted(open_ports):
            tag = f'  ({service})' if service else ''
            print(f'    {port:<5} {tag}')
    else:
        print(f'  {messages["scan_no_open"]}')
    print(messages['scan_separator'])
    print()
    return 0


def handle_scan(args, messages):
    """Entry point for ``nt scan``.

    Direct forms:
      nt scan <host>              — scan common ports only
      nt scan <host> <ports>      — scan specified ports
      nt scan                     — interactive: input host
    """
    from nexus_terminal.interactive import prompt_input, InteractiveExit

    # Direct: nt scan <host> [ports]
    if args:
        host = args[0]
        if len(args) >= 2:
            ports = _parse_port_spec(args[1])
            if ports is None:
                print(messages['scan_invalid_ports'])
                return 1
        else:
            ports = None
        return scan_ports(host, ports, messages)

    # Interactive: input host, then scan common ports
    try:
        host = prompt_input(messages['scan_input_host'], messages)
        if host is None:
            return 0
    except InteractiveExit:
        return 0

    return scan_ports(host, None, messages)