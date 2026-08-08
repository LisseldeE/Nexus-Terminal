"""Route tracing utility — shows the path packets take to a host."""

import subprocess
import sys
import platform


def trace_route(host, messages):
    """Trace route to a host and display the path.

    Runs tracert (Windows) or traceroute (Unix) with -d/-n flag
    to skip DNS resolution for faster results, showing only IPs.

    Args:
        host: Target hostname or IP address.
        messages: i18n messages dict.

    Returns:
        Exit code (0 or 1).
    """
    print()
    print(messages['trace_header'].format(host=host))
    print()

    if platform.system() == 'Windows':
        cmd = ['tracert', '-d', host]
    else:
        cmd = ['traceroute', '-n', host]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

        process.wait()
    except FileNotFoundError:
        print(messages['trace_not_found'])
        return 1
    except Exception as e:
        print(messages['trace_error'].format(e))
        return 1

    print()
    return 0