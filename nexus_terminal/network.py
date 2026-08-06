"""Network utilities for local IP discovery."""

import socket


def get_network_info():
    """Get local network information.

    Returns a dict with:
      hostname:      machine hostname
      primary_ipv4:  primary IPv4 (the one used to reach the internet), may be None
      ipv4:          list of IPv4 addresses (primary first)
      ipv6:          list of IPv6 addresses (global first, link-local last)
    """
    hostname = socket.gethostname()

    ipv4 = []
    ipv6_global = []
    ipv6_link_local = []
    primary_ipv4 = None

    # Primary IPv4 via UDP connect trick (no data is actually sent)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(('8.8.8.8', 80))
        primary_ipv4 = s.getsockname()[0]
        s.close()
        ipv4.append(primary_ipv4)
    except Exception:
        pass

    # Collect all addresses from hostname resolution
    try:
        addrs = socket.getaddrinfo(hostname, None)
        for family, _type, _proto, _canon, sockaddr in addrs:
            ip = sockaddr[0]
            if family == socket.AF_INET and ip not in ipv4:
                ipv4.append(ip)
            elif family == socket.AF_INET6:
                # Strip zone id (e.g. fe80::1%eth0)
                ip = ip.split('%')[0]
                if ip.startswith('fe80'):
                    if ip not in ipv6_link_local:
                        ipv6_link_local.append(ip)
                else:
                    if ip not in ipv6_global:
                        ipv6_global.append(ip)
    except socket.gaierror:
        pass

    return {
        'hostname': hostname,
        'primary_ipv4': primary_ipv4,
        'ipv4': ipv4,
        'ipv6': ipv6_global + ipv6_link_local,
        'ipv6_link_local': set(ipv6_link_local),
    }


def format_network_info(info, messages):
    """Format network info for display. Returns a list of output lines."""
    lines = []

    lines.append(f'{messages["ip_hostname"]}: {info["hostname"]}')

    # IPv4
    if info['ipv4']:
        label = messages['ip_ipv4']
        for i, ip in enumerate(info['ipv4']):
            suffix = f'  ({messages["ip_primary"]})' if ip == info['primary_ipv4'] and i == 0 else ''
            prefix = f'{label:<8}' if i == 0 else '        '
            lines.append(f'{prefix}{ip}{suffix}')
    else:
        lines.append(f'{messages["ip_ipv4"]:<8}{messages["ip_none"]}')

    # IPv6
    if info['ipv6']:
        label = messages['ip_ipv6']
        for i, ip in enumerate(info['ipv6']):
            suffix = f'  ({messages["ip_link_local"]})' if ip in info['ipv6_link_local'] else ''
            prefix = f'{label:<8}' if i == 0 else '        '
            lines.append(f'{prefix}{ip}{suffix}')

    return lines
