"""Update check — fetch version from GitHub Pages to check for new versions."""

import re
import ssl
import urllib.request
import webbrowser

from . import __version__
from .i18n import detect_language

# 版本号托管于 GitHub Pages 纯文本文件，避免 raw 外链滥用/API tags 频率限制
UPDATE_URL = "https://lisseldee.github.io/version/nexusterminal"
# 下载落地页（按语言区分，保持不变）
GITEE_RELEASES_URL = "https://gitee.com/Lisselde_E/Nexus-Terminal/releases"
GITHUB_RELEASES_URL = "https://github.com/LisseldeE/Nexus-Terminal/releases"

# SSL 上下文（避免 SSL 证书校验错误导致无法更新）
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE


def _get_latest_version():
    """从 GitHub Pages 纯文本文件拉取最新版本号
    返回值: (版本号字符串, 错误信息字符串) 元组
        成功时: ("R1.3.2.0", None)
        失败时: (None, "错误描述")
    """
    req = urllib.request.Request(UPDATE_URL)
    req.add_header('User-Agent', 'Nexus-Terminal')

    try:
        with urllib.request.urlopen(req, timeout=15, context=_ssl_context) as response:
            body = response.read().decode('utf-8').strip()
        # io 文件为 R 前缀四段（如 R1.3.2.0），校验后直接返回。
        if not re.match(r'R\d+(\.\d+){0,3}', body):
            return None, None
        return body, None
    except Exception as e:
        return None, str(e)


def check_update(messages):
    """Check for updates by fetching the version from GitHub Pages.

    Returns:
        0 if no update or user declined,
        1 if user chose to update (opens browser),
       -1 on error.
    """
    if detect_language() == 'zh':
        releases_url = GITEE_RELEASES_URL
    else:
        releases_url = GITHUB_RELEASES_URL

    print()
    print(messages['renew_checking'])

    latest, err = _get_latest_version()
    if not latest:
        print(messages['renew_failed'].format(error=err or messages['renew_parse_error']))
        return -1

    current = __version__

    if _is_newer(latest, current):
        print(messages['renew_new_version'].format(version=latest))
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
    """Compare version strings like 'R1.3.2.0' > 'R1.3.1.0'.

    Returns True if remote is newer than current.
    """
    remote_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', remote)
    current_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', current)

    if not remote_match or not current_match:
        return False

    remote_parts = tuple(map(int, remote_match.groups()))
    current_parts = tuple(map(int, current_match.groups()))

    return remote_parts > current_parts