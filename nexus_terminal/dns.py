"""DNS record query — A, AAAA, CNAME, MX, NS, TXT records."""

import socket
import subprocess
import sys
import re
import ipaddress


def _is_ip_address(text):
    """Check if text is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return False


def _resolve_a_aaaa(domain):
    """Resolve A and AAAA records via socket.getaddrinfo()."""
    a_records = []
    aaaa_records = []
    try:
        addrs = socket.getaddrinfo(domain, None)
        for family, _type, _proto, _canon, sockaddr in addrs:
            ip = sockaddr[0]
            if family == socket.AF_INET:
                if ip not in a_records:
                    a_records.append(ip)
            elif family == socket.AF_INET6:
                ip = ip.split('%')[0]
                if ip not in aaaa_records:
                    aaaa_records.append(ip)
    except socket.gaierror:
        pass
    return a_records, aaaa_records


def _resolve_nslookup(domain, record_type, server=None):
    """Resolve a specific record type via nslookup.

    Returns a list of result strings.
    """
    if sys.platform != 'win32':
        return []

    cmd = ['nslookup', '-type', record_type, domain]
    if server:
        cmd.append(server)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
    except Exception:
        return []

    # nslookup always returns exit code 0 even on failure, so we check output
    if 'Non-existent domain' in output or 'can''t find' in output:
        return []

    lines = output.splitlines()
    records = []
    is_authoritative = False

    for line in lines:
        # Skip non-authoritative header
        if 'Non-authoritative answer' in line:
            is_authoritative = True
            continue
        if 'Authoritative answers can be found' in line:
            is_authoritative = True
            continue

        # Parse based on record type
        if record_type == 'MX':
            m = re.search(r'MX\s+preference = (\d+),\s+mail exchanger = (\S+)', line, re.I)
            if m:
                records.append(f'{m.group(2)}  (priority {m.group(1)})')
        elif record_type == 'NS':
            m = re.search(r'nameserver\s+=\s+(\S+)', line, re.I)
            if m and m.group(1) != 'Unknown':
                records.append(m.group(1))
        elif record_type == 'CNAME':
            m = re.search(r'canonical name\s+=\s+(\S+)', line, re.I)
            if m and m.group(1) != 'Unknown':
                records.append(m.group(1))

    return records


def _resolve_mx_linux(domain):
    """Resolve MX records on Linux via `host` or `dig`."""
    # Try `host` first (more commonly available)
    try:
        result = subprocess.run(
            ['host', '-t', 'MX', domain],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            records = []
            for line in result.stdout.splitlines():
                m = re.search(r'(\S+)\s+mail is handled by\s+(\d+)\s+(\S+)', line)
                if m:
                    records.append(f'{m.group(3)}  (priority {m.group(2)})')
            if records:
                return records
    except Exception:
        pass

    # Fallback to `dig`
    try:
        result = subprocess.run(
            ['dig', domain, 'MX', '+short'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            records = []
            for line in result.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2:
                    records.append(f'{parts[1]}  (priority {parts[0]})')
            return records
    except Exception:
        pass

    return []


def _resolve_txt_linux(domain):
    """Resolve TXT records on Linux via `dig`."""
    try:
        result = subprocess.run(
            ['dig', domain, 'TXT', '+short'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            records = []
            for line in result.stdout.splitlines():
                txt = line.strip().strip('"')
                if txt and txt not in records:
                    records.append(txt)
            return records
    except Exception:
        pass
    return []


COMMON_SERVERS = {
    '114': '114.114.114.114',
    'ali': '223.5.5.5',
    'google': '8.8.8.8',
    'cloudflare': '1.1.1.1',
}


def dns_query(domain, messages):
    """Query DNS records for a domain and display results.

    Args:
        domain: Domain name to query.
        messages: i18n messages dict.

    Returns:
        Exit code (0 or 1).
    """
    # If the input is already an IP address, do reverse lookup hint
    if _is_ip_address(domain):
        try:
            hostname, _, _ = socket.gethostbyaddr(domain)
            print()
            print(messages['dns_reverse'].format(ip=domain, hostname=hostname))
            print()
            return 0
        except socket.herror:
            print()
            print(messages['dns_no_reverse'].format(ip=domain))
            print()
            return 1

    # Remove trailing dot if present
    domain = domain.rstrip('.')

    print()
    print(messages['dns_querying'].format(domain=domain))
    print(messages['dns_separator'])

    # A / AAAA via socket.getaddrinfo (always available)
    a_records, aaaa_records = _resolve_a_aaaa(domain)

    if a_records:
        print(f'  A:')
        for ip in a_records:
            print(f'    {ip}')
    if aaaa_records:
        print(f'  AAAA:')
        for ip in aaaa_records:
            print(f'    {ip}')

    if not a_records and not aaaa_records:
        print(messages['dns_no_records'])

    # CNAME via nslookup (Windows) or not available
    if sys.platform == 'win32':
        cname_records = _resolve_nslookup(domain, 'CNAME')
        if cname_records:
            print(f'  CNAME:')
            for r in cname_records:
                print(f'    {r}')
    else:
        # Try `host -t CNAME` on Linux
        try:
            result = subprocess.run(
                ['host', '-t', 'CNAME', domain],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                cnames = []
                for line in result.stdout.splitlines():
                    m = re.search(r'(\S+)\s+is an alias for\s+(\S+)', line)
                    if m:
                        cnames.append(m.group(2))
                if cnames:
                    print(f'  CNAME:')
                    for r in cnames:
                        print(f'    {r}')
        except Exception:
            pass

    # MX via nslookup (Windows) or host/dig (Linux)
    if sys.platform == 'win32':
        mx_records = _resolve_nslookup(domain, 'MX')
        if mx_records:
            print(f'  MX:')
            for r in mx_records:
                print(f'    {r}')
    else:
        mx_records = _resolve_mx_linux(domain)
        if mx_records:
            print(f'  MX:')
            for r in mx_records:
                print(f'    {r}')

    # NS via nslookup (Windows) or host (Linux)
    if sys.platform == 'win32':
        ns_records = _resolve_nslookup(domain, 'NS')
        if ns_records:
            print(f'  NS:')
            for r in ns_records:
                print(f'    {r}')
    else:
        try:
            result = subprocess.run(
                ['host', '-t', 'NS', domain],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                nss = []
                for line in result.stdout.splitlines():
                    m = re.search(r'name server (\S+)', line)
                    if m:
                        nss.append(m.group(1).rstrip('.'))
                if nss:
                    print(f'  NS:')
                    for r in nss:
                        print(f'    {r}')
        except Exception:
            pass

    # TXT (Linux only via dig, Windows nslookup output is messy)
    if sys.platform != 'win32':
        txt_records = _resolve_txt_linux(domain)
        if txt_records:
            print(f'  TXT:')
            for r in txt_records:
                # Truncate very long TXT records for display
                if len(r) > 120:
                    r = r[:117] + '...'
                print(f'    {r}')

    print(messages['dns_separator'])
    print()
    return 0


def handle_dns(args, messages):
    """Entry point for ``nt dns``.

    Direct forms:
      nt dns <domain>       — query DNS records for a domain
      nt dns <ip>           — reverse DNS lookup
      nt dns                — interactive: input domain
    """
    from nexus_terminal.interactive import prompt_input, InteractiveExit

    if args:
        return dns_query(args[0], messages)

    try:
        domain = prompt_input(messages['dns_input_domain'], messages)
        if domain is None:
            return 0
    except InteractiveExit:
        return 0

    return dns_query(domain, messages)