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
from nexus_terminal.cloudflared import check_cloudflared, run_tunnel
from nexus_terminal.wizard import run_wizard, list_custom_commands, RESERVED_PREFIXES


def print_help(messages):
    """Print formatted help information."""
    print(f'\n{messages["help_title"]}')
    print(f'{messages["help_usage"]}\n')
    print(messages['help_modes'])
    print(messages['help_u'])
    print(messages['help_v6'])
    print(messages['help_url'])
    print(messages['help_c'])
    print(messages['help_ls'])
    print(messages['help_help'])
    print(messages['help_version'])
    print(messages['help_custom'])
    print()


def check_and_run_tunnel(url, messages):
    """Check cloudflared availability and run tunnel with the given URL."""
    config = ConfigManager()
    cf_path = config.get('cloudflared_path')
    if not check_cloudflared(cf_path):
        print(messages['cloudflared_not_found'])
        print(messages['cloudflared_hint'])
        print(messages['cloudflared_url'])
        print(messages['cloudflared_path_hint'])
        return 1
    return run_tunnel(url, cf_path, messages)


def handle_tunnel_short(args, messages):
    """Handle: nt u [-v4|-v6] <port>"""
    protocol = None
    port_str = None

    for arg in args:
        if arg == '-v4':
            protocol = '4'
        elif arg == '-v6':
            protocol = '6'
        elif not arg.startswith('-') and port_str is None:
            port_str = arg
        else:
            print(messages['unknown_arg'].format(arg))
            return 1

    if port_str is None:
        print(messages['port_missing'])
        return 1

    try:
        port = int(port_str)
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


def handle_tunnel_url(args, messages):
    """Handle: nt url <url>"""
    if not args:
        print(messages['url_missing'])
        return 1
    return check_and_run_tunnel(args[0], messages)


def handle_custom(args, messages):
    """Handle: nt c [-ls]"""
    if '-ls' in args:
        list_custom_commands(messages)
        return 0
    for arg in args:
        if arg.startswith('-'):
            print(messages['unknown_arg'].format(arg))
            return 1
    run_wizard(messages)
    return 0


def try_custom_command(messages):
    """Check if the first argument is a custom command invocation (--<prefix>).

    Returns True if handled (found or errored), False if not a custom command attempt.
    """
    if len(sys.argv) < 2:
        return False

    first_arg = sys.argv[1]
    if not first_arg.startswith('--') or len(first_arg) <= 2:
        return False

    prefix = first_arg[2:]
    if prefix in RESERVED_PREFIXES:
        return False

    config = ConfigManager()
    custom = config.get_custom_command(prefix)
    if not custom:
        print(messages['custom_not_found'].format(prefix))
        sys.exit(1)

    cmd = custom['command'] if isinstance(custom, dict) else str(custom)
    print(messages['custom_executing'].format(cmd), flush=True)
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(messages['custom_interrupted'])
    return True


def main():
    messages = get_messages()

    # No arguments -> show help
    if len(sys.argv) == 1:
        print_help(messages)
        return 0

    # Custom command: nt --<prefix>
    if try_custom_command(messages):
        return 0

    mode = sys.argv[1].lower()
    args = sys.argv[2:]

    if mode in ('help', 'h'):
        print_help(messages)
        return 0

    if mode in ('version', 'v'):
        print(messages['version_info'].format(__version__))
        return 0

    if mode == 'u':
        return handle_tunnel_short(args, messages)

    if mode == 'url':
        return handle_tunnel_url(args, messages)

    if mode == 'c':
        return handle_custom(args, messages)

    # Unknown mode
    print(messages['unknown_mode'].format(sys.argv[1]))
    return 1


if __name__ == '__main__':
    sys.exit(main())
