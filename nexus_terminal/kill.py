"""Process termination utility — kill processes by port."""

import subprocess

from .ports import get_listening_ports, get_process_name


def kill_process_by_port(port, messages):
    """Kill the process listening on the given port.

    Args:
        port: Port number.
        messages: i18n messages dict.

    Returns:
        0 on success, 1 on failure.
    """
    ports = get_listening_ports()
    targets = [p for p in ports if p['port'] == port and p['pid'] != 0]

    if not targets:
        print(messages['kill_port_not_found'].format(port))
        return 1

    for p in targets:
        pid = p['pid']
        proc_name = get_process_name(pid)  # Get name before killing
        try:
            result = subprocess.run(
                ['taskkill', '/PID', str(pid), '/F'],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print(messages['kill_success'].format(port, proc_name, pid))
            else:
                print(messages['kill_failed'].format(pid, result.stderr.strip()))
                return 1
        except Exception as e:
            print(messages['kill_error'].format(e))
            return 1

    return 0


def kill_interactive(messages):
    """Interactive process killer — show listening ports, select one to kill.

    Args:
        messages: i18n messages dict.

    Returns:
        0 on success, 1 if no ports or cancelled.
    """
    from .interactive import select_option, InteractiveExit

    ports = get_listening_ports()
    if not ports:
        print(messages['kill_no_ports'])
        return 1

    # Build options: port number as value, "process_name  PID xxx" as desc
    options = []
    for p in ports:
        proc_name = get_process_name(p['pid'])
        value = str(p['port'])
        desc = f'{proc_name}  PID {p["pid"]}'
        options.append((value, desc))

    try:
        choice = select_option(
            messages['kill_select'],
            messages['interactive_hint'],
            options,
            messages,
        )
    except InteractiveExit:
        return 0  # Ctrl+C — silent exit

    if choice is None:
        return 0  # Esc — cancelled

    try:
        port = int(choice)
    except ValueError:
        return 1

    return kill_process_by_port(port, messages)
