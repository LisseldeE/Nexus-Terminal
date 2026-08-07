#!/usr/bin/env python3
"""Nexus Terminal - A lightweight CLI tool for cloudflared tunnels and custom commands."""

import sys
import os
import subprocess

# Fix Windows console encoding for Chinese characters via Win32 API
# (avoids os.system spawning a cmd.exe window that steals focus)
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure the nexus_terminal package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_terminal import __version__
from nexus_terminal.i18n import get_messages
from nexus_terminal.config import ConfigManager
from nexus_terminal.cloudflared import (
    check_cloudflared, run_tunnel, ensure_cloudflared,
    download_and_extract_cf, install_cf, get_cloudflared_version,
)
from nexus_terminal.wizard import (
    run_wizard, list_custom_commands,
    remove_custom_command, remove_custom_command_interactive,
)
from nexus_terminal.network import get_network_info, format_network_info
from nexus_terminal.ports import get_listening_ports, format_ports
from nexus_terminal.kill import kill_process_by_port, kill_interactive
from nexus_terminal.downloader import download_file
from nexus_terminal.tool import handle_tool_command
from nexus_terminal.renew import check_update


def print_help(messages):
    """Print formatted help information."""
    print(f'\n{messages["help_title"]}')
    print(f'{messages["help_usage"]}\n')
    print(messages['help_modes'])
    print(messages['help_u'])
    print(messages['help_v6'])
    print(messages['help_url'])
    print(messages['help_server'])
    print(messages['help_c'])
    print(messages['help_ls'])
    print(messages['help_rm'])
    print(messages['help_install'])
    print(messages['help_ip'])
    print(messages['help_ports'])
    print(messages['help_kill'])
    print(messages['help_download'])
    print(messages['help_tool'])
    print(messages['help_renew'])
    print(messages['help_help'])
    print(messages['help_version'])
    print(messages['help_custom'])
    print()


def check_and_run_tunnel(url, messages):
    """Check cloudflared availability and run tunnel with the given URL.

    If cloudflared is not found, prompts the user to download and install
    it automatically. After successful installation, re-executes the tunnel.
    """
    config = ConfigManager()
    cf_path = config.get('cloudflared_path')

    if check_cloudflared(cf_path):
        # Already available — run tunnel directly
        return run_tunnel(url, cf_path, messages)

    # Not available — try to download and install
    if not ensure_cloudflared(cf_path, messages):
        print(messages['cloudflared_hint'])
        print(messages['cloudflared_url'])
        print(messages['cloudflared_path_hint'])
        return 1

    # Just installed — re-execute the tunnel
    if messages:
        print(messages['cf_re_executing'])
    return run_tunnel(url, cf_path, messages)


def handle_tunnel(args, messages):
    """Handle: nt u|url [-v4|-v6] <port|url>

    u and url are unified: auto-detects whether the argument is a
    port number (int) or a full URL (contains '://').
    """
    protocol = None
    target = None

    for arg in args:
        if arg == '-v4':
            protocol = '4'
        elif arg == '-v6':
            protocol = '6'
        elif not arg.startswith('-') and target is None:
            target = arg
        else:
            print(messages['unknown_arg'].format(arg))
            return 1

    if target is None:
        print(messages['port_missing'])
        return 1

    # URL mode: argument contains a scheme
    if '://' in target:
        return check_and_run_tunnel(target, messages)

    # Port mode: parse as integer
    try:
        port = int(target)
    except ValueError:
        print(messages['port_invalid'])
        return 1

    if not (1 <= port <= 65535):
        print(messages['port_invalid'])
        return 1

    if protocol == '6':
        url = f'http://[::1]:{port}'
    else:
        url = f'http://127.0.0.1:{port}'

    return check_and_run_tunnel(url, messages)


def handle_server(args, messages):
    """Handle: nt server [-http] <port>

    Starts a simple HTTP file server (python http.server) on the given port,
    serving the current working directory.
    """
    import errno
    import http.server

    port_str = None
    for arg in args:
        if arg == '-http':
            continue  # Explicit HTTP flag (default, reserved for future protocols)
        elif not arg.startswith('-') and port_str is None:
            port_str = arg
        else:
            print(messages['unknown_arg'].format(arg))
            return 1

    if port_str is None:
        print(messages['server_port_missing'])
        return 1

    try:
        port = int(port_str)
    except ValueError:
        print(messages['port_invalid'])
        return 1

    if not (1 <= port <= 65535):
        print(messages['port_invalid'])
        return 1

    cwd = os.getcwd()

    print()
    print(messages['server_running'])
    print(f'  {messages["server_port_label"]}: {port}')
    print(f'  {messages["server_directory"]}: {cwd}')
    print(f'  URL: http://localhost:{port}')
    print(messages['server_stop_hint'])

    handler = http.server.SimpleHTTPRequestHandler

    try:
        with http.server.ThreadingHTTPServer(('', port), handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(messages['server_stopped'])
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(messages['server_port_in_use'].format(port))
        elif e.errno == errno.EACCES:
            print(messages['server_port_denied'].format(port))
        else:
            print(messages['server_error'].format(e))
        return 1

    return 0


def handle_custom(args, messages):
    """Handle: nt c [-ls] [-rm <prefix>]"""
    if '-ls' in args:
        list_custom_commands(messages)
        return 0

    if '-rm' in args:
        idx = args.index('-rm')
        if idx + 1 < len(args):
            return remove_custom_command(args[idx + 1], messages)
        return remove_custom_command_interactive(messages)

    for arg in args:
        if arg.startswith('-'):
            print(messages['unknown_arg'].format(arg))
            return 1
    run_wizard(messages)
    return 0


def handle_install(args, messages):
    """Handle: nt install cf (or nt install u)"""
    if not args or args[0].lower() not in ('cf', 'u'):
        print(messages['install_usage'])
        return 1

    # Already installed — show version and exit
    config = ConfigManager()
    cf_path = config.get('cloudflared_path')
    if check_cloudflared(cf_path):
        binary = cf_path if (cf_path and os.path.isfile(cf_path)) else 'cloudflared'
        version = get_cloudflared_version(binary)
        if version:
            print(messages['install_already_exists_version'].format(version))
        else:
            print(messages['install_already_exists'])
        return 0

    print(messages['install_starting'])

    try:
        exe_path = download_and_extract_cf(messages)
        if install_cf(exe_path, messages):
            print(messages['install_success'])
            return 0
        print(messages['install_failed'])
        return 1
    except Exception as e:
        print(messages['cf_download_failed'].format(e))
        return 1


def handle_ip(messages):
    """Handle: nt ip — show local IP addresses."""
    info = get_network_info()
    lines = format_network_info(info, messages)
    print()
    for line in lines:
        print(line)
    return 0


def handle_ports(messages):
    """Handle: nt ports — list all listening ports."""
    ports = get_listening_ports()
    print()
    print(messages['ports_header'])
    for line in format_ports(ports, messages):
        print(line)
    return 0


def handle_kill(args, messages):
    """Handle: nt kill [port] — kill process by port.

    No port arg → interactive selection from listening ports.
    Port arg    → kill directly.
    """
    if args:
        try:
            port = int(args[0])
        except ValueError:
            print(messages['port_invalid'])
            return 1
        return kill_process_by_port(port, messages)

    return kill_interactive(messages)


def handle_download(args, messages):
    """Handle: nt download <url>

    Multi-threaded download of a file from the given URL.
    Saves to the current working directory.
    """
    if not args:
        print(messages['download_missing_url'])
        print(messages['download_usage'])
        return 1

    url = args[0]
    result = download_file(url, messages=messages)
    return 0 if result else 1


def handle_renew(messages):
    """Handle: nt renew — check for updates."""
    return check_update(messages)


def main():
    messages = get_messages()

    first_arg = None
    args = []

    if len(sys.argv) == 1:
        # No arguments — try interactive mode, fallback to help
        from nexus_terminal.interactive import run_interactive, HAS_MSVCRT, InteractiveExit
        if HAS_MSVCRT:
            config = ConfigManager()
            custom = config.get_all_custom_commands()
            try:
                cmd = run_interactive(__version__, custom, messages)
            except InteractiveExit:
                # Ctrl+C — exit silently
                return 0
            if cmd:
                parts = cmd.split()
                first_arg = parts[0] if parts else None
                args = parts[1:]
        if first_arg is None:
            print_help(messages)
            return 0
    else:
        first_arg = sys.argv[1]
        args = sys.argv[2:]

    mode = first_arg.lower()

    # Built-in modes (case-insensitive)
    if mode in ('help', 'h'):
        print_help(messages)
        return 0

    if mode in ('version', 'v'):
        print(messages['version_info'].format(__version__))
        print(messages['copyright'])
        return 0

    if mode in ('u', 'url'):
        return handle_tunnel(args, messages)

    if mode in ('server', 's'):
        return handle_server(args, messages)

    if mode == 'c':
        return handle_custom(args, messages)

    if mode == 'install':
        return handle_install(args, messages)

    if mode == 'ip':
        return handle_ip(messages)

    if mode == 'ports':
        return handle_ports(messages)

    if mode == 'kill':
        return handle_kill(args, messages)

    if mode == 'download':
        return handle_download(args, messages)

    if mode == 'tool':
        return handle_tool_command(args, messages)

    if mode == 'renew':
        return handle_renew(messages)

    # Not a built-in — try custom command (case-insensitive match)
    # Strip leading -- for backward compat
    lookup = first_arg[2:] if first_arg.startswith('--') and len(first_arg) > 2 else first_arg

    config = ConfigManager()
    custom = None
    for prefix, data in config.get_all_custom_commands().items():
        if prefix.lower() == lookup.lower():
            custom = data
            break

    if custom:
        cmd = custom['command'] if isinstance(custom, dict) else str(custom)
        print(messages['custom_executing'].format(cmd), flush=True)
        try:
            subprocess.run(cmd, shell=True)
        except KeyboardInterrupt:
            print(messages['custom_interrupted'])
        return 0

    # Unknown mode
    print(messages['unknown_mode'].format(first_arg))
    return 1


if __name__ == '__main__':
    sys.exit(main())
