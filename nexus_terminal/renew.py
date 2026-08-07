"""Update check — fetch Renew.json from remote repos to check for new versions."""

import json
import re
import urllib.request
import webbrowser

from . import __version__
from .i18n import detect_language

GITEE_RENEW_URL = "https://gitee.com/Lisselde_E/Nexus-Terminal/raw/main/Renew.json"
GITHUB_RENEW_URL = "https://raw.githubusercontent.com/LisseldeE/Nexus-Terminal/main/Renew.json"

GITEE_RELEASES_URL = "https://gitee.com/Lisselde_E/Nexus-Terminal/releases"
GITHUB_RELEASES_URL = "https://github.com/LisseldeE/Nexus-Terminal/releases"


def check_update(messages):
    """Check for updates by fetching Renew.json from remote repos.

    Returns:
        0 if no update or user declined,
        1 if user chose to update (opens browser),
       -1 on error.
    """
    if detect_language() == 'zh':
        renew_url = GITEE_RENEW_URL
        releases_url = GITEE_RELEASES_URL
    else:
        renew_url = GITHUB_RENEW_URL
        releases_url = GITHUB_RELEASES_URL

    print()
    print(messages['renew_checking'])

    try:
        req = urllib.request.Request(renew_url)
        req.add_header('User-Agent', 'Nexus-Terminal')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(messages['renew_failed'].format(error=str(e)))
        return -1

    remote_version = data.get('Renew', '')
    if not remote_version:
        print(messages['renew_parse_error'])
        return -1

    current = __version__

    if _is_newer(remote_version, current):
        print(messages['renew_new_version'].format(version=remote_version))
        print(messages['renew_ask'])
        try:
            choice = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if choice in ('y', 'yes'):
            webbrowser.open(releases_url)
            print(messages['renew_opening'])
            return 1
        print(messages['renew_cancelled'])
        return 0

    print(messages['renew_latest'])
    return 0


def _is_newer(remote, current):
    """Compare version strings like 'R1.2.0.0' > 'R1.1.0.0'.

    Returns True if remote is newer than current.
    """
    remote_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', remote)
    current_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', current)

    if not remote_match or not current_match:
        return False

    remote_parts = tuple(map(int, remote_match.groups()))
    current_parts = tuple(map(int, current_match.groups()))

    return remote_parts > current_parts