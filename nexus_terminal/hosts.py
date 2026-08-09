"""Hosts file management — add, delete, edit, list, open in notepad."""

import sys
import subprocess

if sys.platform == 'win32':
    HOSTS_PATH = r'C:\Windows\System32\drivers\etc\hosts'
else:
    HOSTS_PATH = '/etc/hosts'


def _is_admin():
    """Check if the current process is running as administrator."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Low-level file I/O
# ---------------------------------------------------------------------------

def _read_hosts_content():
    """Read hosts file as a list of lines (without line endings).

    Uses utf-8-sig to transparently strip a BOM if present.
    Returns [] if the file cannot be read.
    """
    try:
        with open(HOSTS_PATH, 'r', encoding='utf-8-sig') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []
    except Exception:
        return []


def _write_hosts_content(lines):
    """Write lines back to the hosts file (UTF-8, no BOM)."""
    with open(HOSTS_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def _parse_entries():
    """Parse the hosts file into structured entries.

    Each entry is a dict with a ``type`` key:
      - ``entry``:   {ip, hostname, comment, raw, line_no}
      - ``comment``: {raw, line_no}
      - ``blank``:   {raw, line_no}

    ``line_no`` is 1-based and refers to the position in the raw file so
    that add/delete/edit can locate the exact line to modify.
    """
    entries = []
    for i, raw in enumerate(_read_hosts_content(), 1):
        stripped = raw.strip()
        if not stripped:
            entries.append({'type': 'blank', 'raw': raw, 'line_no': i})
            continue
        if stripped.startswith('#'):
            entries.append({'type': 'comment', 'raw': raw, 'line_no': i})
            continue
        parts = stripped.split(None, 2)
        entries.append({
            'type': 'entry',
            'ip': parts[0],
            'hostname': parts[1] if len(parts) > 1 else '',
            'comment': parts[2] if len(parts) > 2 else '',
            'raw': raw,
            'line_no': i,
        })
    return entries


def _get_host_entries(entries):
    """Return only actual host entries (skip comments and blank lines)."""
    return [e for e in entries if e['type'] == 'entry']


def _validate_ip(ip):
    """Validate an IPv4 or IPv6 address."""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def _validate_hostname(hostname):
    """Validate a hostname (letters, digits, dots, hyphens)."""
    if not hostname:
        return False
    return all(c.isalnum() or c in '.-' for c in hostname)


def _require_admin(messages):
    """Print admin-required notice and return True if admin is missing."""
    if _is_admin():
        return False
    print()
    print(messages['hosts_no_admin'])
    print(messages['hosts_admin_hint'])
    print()
    return True


def _page_size_for_terminal():
    """Calculate a safe page size from the current terminal height."""
    import shutil
    term_height = shutil.get_terminal_size((80, 24)).lines
    return max(5, term_height - 8)


# ---------------------------------------------------------------------------
# Public operations
# ---------------------------------------------------------------------------

def hosts_list(messages):
    """Display all host entries."""
    host_entries = _get_host_entries(_parse_entries())

    print()
    print(messages['hosts_list_title'])
    print(messages['hosts_separator'])
    if not host_entries:
        print(messages['hosts_empty'])
    else:
        for i, e in enumerate(host_entries, 1):
            print(f'  {i:>3}.  {e["ip"]:<15}  {e["hostname"]}')
    print(messages['hosts_separator'])
    print()
    return 0


def hosts_add(ip, hostname, messages):
    """Add a new ``ip hostname`` entry to the hosts file."""
    if _require_admin(messages):
        return 1

    if not _validate_ip(ip):
        print(messages['hosts_invalid_ip'].format(ip=ip))
        return 1
    if not _validate_hostname(hostname):
        print(messages['hosts_invalid_hostname'].format(hostname=hostname))
        return 1

    new_line = f'{ip} {hostname}'
    lines = _read_hosts_content()
    for line in lines:
        if line.strip() == new_line:
            print(messages['hosts_exists'])
            return 1

    lines.append(new_line)
    try:
        _write_hosts_content(lines)
    except Exception as e:
        print(messages['hosts_error'].format(error=str(e)))
        return 1

    print(messages['hosts_added'].format(ip=ip, hostname=hostname))
    return 0


def hosts_open(messages):
    """Open the hosts file in Notepad.

    On Windows, launches Notepad elevated (via ``runas``) so the user can
    save changes; falls back to a normal launch if elevation is declined.
    """
    if sys.platform != 'win32':
        print(messages['hosts_windows_only'])
        return 1

    try:
        if _is_admin():
            subprocess.Popen(['notepad', HOSTS_PATH])
        else:
            import ctypes
            retval = ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', 'notepad.exe', HOSTS_PATH, None, 1,  # SW_SHOWNORMAL
            )
            if retval <= 32:
                # User declined UAC or elevation failed — open read-only.
                subprocess.Popen(['notepad', HOSTS_PATH])
        print(messages['hosts_opening'])
    except Exception as e:
        print(messages['hosts_error'].format(error=str(e)))
        return 1
    return 0


# ---------------------------------------------------------------------------
# Interactive operations
# ---------------------------------------------------------------------------

def _build_entry_options(host_entries):
    """Build (value, desc) options for select_option from host entries."""
    options = []
    for i, e in enumerate(host_entries):
        options.append((str(i + 1), f'{e["ip"]:<15} {e["hostname"]}'))
    return options


def _hosts_add_interactive(messages):
    """Interactive add: prompt for IP and hostname, then append."""
    from nexus_terminal.interactive import prompt_input, InteractiveExit

    if _require_admin(messages):
        return 1

    try:
        ip = prompt_input(messages['hosts_input_ip'], messages)
        if ip is None:
            return 0
        hostname = prompt_input(messages['hosts_input_hostname'], messages)
        if hostname is None:
            return 0
    except InteractiveExit:
        return 0

    return hosts_add(ip, hostname, messages)


def _hosts_delete_interactive(messages):
    """Interactive delete: select an entry from a paginated list, then remove."""
    from nexus_terminal.interactive import select_option, InteractiveExit

    if _require_admin(messages):
        return 1

    host_entries = _get_host_entries(_parse_entries())
    if not host_entries:
        print(messages['hosts_empty'])
        return 1

    try:
        choice = select_option(
            messages['hosts_select_delete'],
            messages['interactive_hint'],
            _build_entry_options(host_entries),
            messages,
            page_size=_page_size_for_terminal(),
        )
    except InteractiveExit:
        return 0
    if choice is None:
        return 0

    selected = host_entries[int(choice) - 1]
    lines = _read_hosts_content()
    del lines[selected['line_no'] - 1]
    try:
        _write_hosts_content(lines)
    except Exception as e:
        print(messages['hosts_error'].format(error=str(e)))
        return 1

    print(messages['hosts_deleted'].format(ip=selected['ip'], hostname=selected['hostname']))
    return 0


def _hosts_edit_interactive(messages):
    """Interactive edit: select an entry, pre-fill IP/hostname, write back."""
    from nexus_terminal.interactive import select_option, prompt_input, InteractiveExit

    if _require_admin(messages):
        return 1

    host_entries = _get_host_entries(_parse_entries())
    if not host_entries:
        print(messages['hosts_empty'])
        return 1

    try:
        choice = select_option(
            messages['hosts_select_edit'],
            messages['interactive_hint'],
            _build_entry_options(host_entries),
            messages,
            page_size=_page_size_for_terminal(),
        )
    except InteractiveExit:
        return 0
    if choice is None:
        return 0

    selected = host_entries[int(choice) - 1]

    try:
        new_ip = prompt_input(messages['hosts_input_new_ip'], messages,
                              default=selected['ip'])
        if new_ip is None:
            return 0
        new_hostname = prompt_input(messages['hosts_input_new_hostname'], messages,
                                    default=selected['hostname'])
        if new_hostname is None:
            return 0
    except InteractiveExit:
        return 0

    if not _validate_ip(new_ip):
        print(messages['hosts_invalid_ip'].format(ip=new_ip))
        return 1
    if not _validate_hostname(new_hostname):
        print(messages['hosts_invalid_hostname'].format(hostname=new_hostname))
        return 1

    lines = _read_hosts_content()
    lines[selected['line_no'] - 1] = f'{new_ip} {new_hostname}'
    try:
        _write_hosts_content(lines)
    except Exception as e:
        print(messages['hosts_error'].format(error=str(e)))
        return 1

    print(messages['hosts_edited'].format(ip=new_ip, hostname=new_hostname))
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def handle_hosts(args, messages):
    """Entry point for ``nt hosts`` — interactive sub-menu or direct subcommand.

    Direct forms:
      nt hosts list          — list all entries
      nt hosts open          — open in Notepad (elevated)
      nt hosts add <ip> <hn> — append an entry
      nt hosts del           — interactive delete
      nt hosts edit          — interactive edit
      nt hosts               — interactive sub-menu
    """
    from nexus_terminal.interactive import select_option, HAS_MSVCRT, InteractiveExit

    # --- Direct subcommands ---
    if args:
        sub = args[0].lower()
        if sub in ('list', '-ls', 'ls'):
            return hosts_list(messages)
        if sub == 'open':
            return hosts_open(messages)
        if sub == 'add':
            if len(args) >= 3:
                return hosts_add(args[1], args[2], messages)
            return _hosts_add_interactive(messages)
        if sub in ('del', 'delete', 'rm'):
            return _hosts_delete_interactive(messages)
        if sub in ('edit', 'mod'):
            return _hosts_edit_interactive(messages)
        print(messages['hosts_usage'])
        return 1

    # --- Interactive sub-menu ---
    if not HAS_MSVCRT:
        print(messages['hosts_usage'])
        return 1

    try:
        action = select_option(
            messages['hosts_title'],
            messages['interactive_hint'],
            [
                ('add', messages['hosts_action_add']),
                ('del', messages['hosts_action_del']),
                ('edit', messages['hosts_action_edit']),
                ('list', messages['hosts_action_list']),
                ('open', messages['hosts_action_open']),
            ],
            messages,
        )
    except InteractiveExit:
        return 0

    if action is None:
        return 0

    if action == 'add':
        return _hosts_add_interactive(messages)
    if action == 'del':
        return _hosts_delete_interactive(messages)
    if action == 'edit':
        return _hosts_edit_interactive(messages)
    if action == 'list':
        return hosts_list(messages)
    if action == 'open':
        return hosts_open(messages)

    return 0
