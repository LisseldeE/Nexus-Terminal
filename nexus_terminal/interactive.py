"""Interactive command selector with multi-level menu navigation.

Flow:
- Main menu: select a command, Enter to confirm
- Sub-menu: select sub-options (e.g. protocol), Enter to confirm
- Input prompt: type value, Enter to execute
- Esc at any level goes back / cancels
"""

import sys
import ctypes

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

# Key codes (bytes)
KEY_ENTER = b'\r'
KEY_ESC = b'\x1b'
KEY_BACKSPACE = b'\x08'
KEY_CTRL_C = b'\x03'
KEY_UP = b'\xe0H'
KEY_DOWN = b'\xe0P'

# ANSI colors
C_RESET = '\033[0m'
C_CYAN = '\033[36m'
C_GREEN = '\033[32m'
C_BOLD_GREEN = '\033[1;32m'
C_GRAY = '\033[90m'


class InteractiveExit(Exception):
    """Raised when user presses Ctrl+C in interactive mode — exit silently."""
    pass


def _enable_vt_mode():
    """Enable VT100 escape sequence processing on Windows console."""
    if sys.platform != 'win32':
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


def _get_key():
    """Read a single key press, returns bytes."""
    ch = msvcrt.getch()
    if ch in (b'\xe0', b'\x00'):
        return ch + msvcrt.getch()
    return ch


def select_option(title, subtitle, options, messages, page_size=None):
    """Show a list of options for selection.

    Args:
        title: Header title.
        subtitle: Hint line (navigation instructions).
        options: List of (value, description) tuples.
        messages: i18n messages dict.
        page_size: Optional max number of visible options. When the list
            exceeds this, a sliding window centered on the selection is
            rendered instead, keeping output within the terminal viewport
            so cleanup is always reliable for very long lists.

    Returns:
        Selected value string, or None if cancelled.
    """
    if not HAS_MSVCRT:
        return None

    _enable_vt_mode()

    selected = 0
    last_lines = 0

    def render():
        nonlocal last_lines
        if last_lines > 0:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')

        out = [
            f'{C_CYAN}{title}{C_RESET}',
            f'{C_GRAY}{subtitle}{C_RESET}',
            '',
        ]

        max_len = max(len(v) for v, _ in options) if options else 0

        # Sliding window for long lists — keeps last_lines bounded so the
        # relative-cursor cleanup never overflows the terminal viewport.
        use_window = bool(page_size and len(options) > page_size)
        if use_window:
            half = page_size // 2
            start = max(0, selected - half)
            end = min(len(options), start + page_size)
            start = max(0, end - page_size)
        else:
            start, end = 0, len(options)

        if use_window and start > 0:
            out.append(f'{C_GRAY}  ↑ {start}{C_RESET}')

        for i in range(start, end):
            value, desc = options[i]
            pad = ' ' * (max_len - len(value) + 2)
            if i == selected:
                out.append(
                    f'{C_GREEN}❯{C_RESET} {C_BOLD_GREEN}{value}{C_RESET}'
                    f'{pad}{C_GRAY}{desc}{C_RESET}'
                )
            else:
                out.append(f'  {value}{pad}{C_GRAY}{desc}{C_RESET}')

        if use_window and end < len(options):
            out.append(f'{C_GRAY}  ↓ {len(options) - end}{C_RESET}')

        out.append('')

        sys.stdout.write('\n'.join(out))
        sys.stdout.flush()
        last_lines = len(out) - 1

    render()

    while True:
        key = _get_key()

        if key == KEY_ENTER:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')
            return options[selected][0] if options else None

        elif key == KEY_CTRL_C:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')
            raise InteractiveExit()

        elif key == KEY_ESC:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')
            return None

        elif key == KEY_UP:
            if options:
                selected = (selected - 1) % len(options)

        elif key == KEY_DOWN:
            if options:
                selected = (selected + 1) % len(options)

        else:
            continue

        render()


def prompt_input(label, messages, default=''):
    """Prompt for text input.

    Args:
        label: Prompt label shown above the input line.
        messages: i18n messages dict.
        default: Optional pre-filled value (used by edit flows so the user
            can press Enter to keep the current value).

    Returns:
        Input string, or None if cancelled (Esc).
    """
    if not HAS_MSVCRT:
        return None

    _enable_vt_mode()

    query = default
    last_lines = 0

    def render():
        nonlocal last_lines
        if last_lines > 0:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')

        out = [
            f'{C_CYAN}{label}{C_RESET}',
            '',
            f'{C_CYAN}>{C_RESET} {query}',
        ]

        sys.stdout.write('\n'.join(out))
        sys.stdout.flush()
        last_lines = len(out) - 1

    render()

    while True:
        key = _get_key()

        if key == KEY_ENTER:
            if query.strip():
                sys.stdout.write(f'\033[{last_lines}A\r\033[J')
                return query.strip()
            continue  # Empty — keep waiting

        elif key == KEY_CTRL_C:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')
            raise InteractiveExit()

        elif key == KEY_ESC:
            sys.stdout.write(f'\033[{last_lines}A\r\033[J')
            return None

        elif key == KEY_BACKSPACE:
            query = query[:-1]

        elif len(key) == 1 and 32 <= key[0] <= 126:
            query += key.decode('ascii')

        else:
            continue

        render()


def _build_main_options(custom_commands, messages):
    """Build the main menu options list."""
    # Built-in commands sorted alphabetically
    builtin_keys = ['dns', 'download', 'hash', 'hosts', 'http', 'install', 'ip', 'kill', 'monitor', 'ports',
                    'renew', 'scan', 'server', 'tool', 'trace', 'url', 'version']
    options = []
    for key in builtin_keys:
        desc_key = f'cmd_desc_{key}'
        options.append((key, messages[desc_key]))
    options.append(('custom', messages['cmd_desc_custom']))
    for prefix, data in custom_commands.items():
        if isinstance(data, dict):
            desc = data.get('description', '') or data.get('command', '')
        else:
            desc = str(data)
        options.append((prefix, f'[{messages["interactive_custom"]}] {desc}'))
    options.append(('help', messages['cmd_desc_help']))
    options.append(('exit', messages['cmd_desc_exit']))
    return options


def _handle_url(messages):
    """URL sub-flow: select protocol → input port → return command string."""
    proto = select_option(
        messages['url_select_protocol'],
        messages['interactive_hint'],
        [
            ('v4', messages['url_ipv4']),
            ('v6', messages['url_ipv6']),
        ],
        messages,
    )
    if proto is None:
        return None

    port = prompt_input(messages['url_input_port'], messages)
    if port is None:
        return None

    return f'url -{proto} {port}'


def _handle_server(messages):
    """Server sub-flow: input port → return command string."""
    port = prompt_input(messages['server_input_port'], messages)
    if port is None:
        return None
    return f'server {port}'


def _handle_custom(custom_commands, messages):
    """Custom command sub-flow: select action → return command string."""
    action = select_option(
        messages['custom_select_action'],
        messages['interactive_hint'],
        [
            ('wizard', messages['custom_action_wizard']),
            ('list', messages['custom_action_list']),
            ('remove', messages['custom_action_remove']),
        ],
        messages,
    )
    if action is None:
        return None

    if action == 'wizard':
        return 'c'
    if action == 'list':
        return 'c -ls'

    # Remove — show command picker if any exist
    if not custom_commands:
        return 'c -rm'  # wizard will handle empty case

    remove_options = []
    for prefix, data in custom_commands.items():
        if isinstance(data, dict):
            desc = data.get('description', '') or data.get('command', '')
        else:
            desc = str(data)
        remove_options.append((prefix, desc))

    target = select_option(
        messages['custom_select_remove'],
        messages['interactive_hint'],
        remove_options,
        messages,
    )
    if target is None:
        return None
    return f'c -rm {target}'


def _handle_install(messages):
    """Install sub-flow: select component → return command string."""
    target = select_option(
        messages['install_select'],
        messages['interactive_hint'],
        [
            ('cf', messages['install_desc_cf']),
        ],
        messages,
    )
    if target is None:
        return None
    return f'install {target}'


def _handle_download(messages):
    """Download sub-flow: input URL → return command string."""
    url = prompt_input('URL:', messages)
    if url is None:
        return None
    return f'download {url}'


def _handle_tool(messages):
    """Tool sub-flow: return 'tool' to let NT.py handle interactive selection."""
    return 'tool'


def _handle_trace(messages):
    """Trace sub-flow: input host/IP → return command string."""
    host = prompt_input('Host/IP:', messages)
    if host is None:
        return None
    return f'trace {host}'


def _handle_hosts(messages):
    """Hosts sub-flow: return 'hosts' to let nt.py handle the sub-menu."""
    return 'hosts'


def _handle_dns(messages):
    """DNS sub-flow: return 'dns' to let nt.py handle interactive input."""
    return 'dns'


def _handle_scan(messages):
    """Scan sub-flow: return 'scan' to let nt.py handle the sub-menu."""
    return 'scan'


def _handle_http(messages):
    """HTTP sub-flow: return 'http' to let nt.py handle interactive input."""
    return 'http'


def run_interactive(version, custom_commands, messages):
    """Run the interactive command selector.

    Args:
        version: Version string for the title.
        custom_commands: Dict of custom commands from config.
        messages: i18n messages dict.

    Returns:
        Command string to execute, or None if cancelled.
    """
    if not HAS_MSVCRT:
        return None

    main_options = _build_main_options(custom_commands, messages)

    choice = select_option(
        messages['interactive_title'].format(version),
        messages['interactive_hint'],
        main_options,
        messages,
    )

    if choice is None:
        return None

    # Custom commands — execute directly
    simple_commands = {'url', 'server', 'custom', 'install',
                       'ip', 'ports', 'kill', 'download', 'monitor', 'tool', 'renew',
                       'hash', 'hosts', 'http', 'dns', 'scan', 'trace', 'help', 'version', 'exit'}
    if choice not in simple_commands:
        return choice

    if choice == 'exit':
        raise InteractiveExit()

    if choice == 'url':
        return _handle_url(messages)
    if choice == 'server':
        return _handle_server(messages)
    if choice == 'custom':
        return _handle_custom(custom_commands, messages)
    if choice == 'install':
        return _handle_install(messages)
    if choice == 'download':
        return _handle_download(messages)
    if choice == 'tool':
        return _handle_tool(messages)
    if choice == 'trace':
        return _handle_trace(messages)
    if choice == 'hosts':
        return _handle_hosts(messages)
    if choice == 'dns':
        return _handle_dns(messages)
    if choice == 'scan':
        return _handle_scan(messages)
    if choice == 'http':
        return _handle_http(messages)

    # Simple commands (ip, ports, help, version) — execute directly
    return choice
