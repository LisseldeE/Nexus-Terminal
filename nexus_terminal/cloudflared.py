"""Cloudflared detection, download, installation, and tunnel runner."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

from .i18n import detect_language

CF_INSTALL_DIR = r"C:\Windows\System32"
CF_EXE_NAME = "cloudflared.exe"


def get_cf_download_url():
    """Return the cloudflared download URL based on system language."""
    if detect_language() == 'zh':
        return "https://gitee.com/Lisselde_E/Nexus-Terminal/releases/download/plugins/cloudflared.zip"
    return "https://github.com/LisseldeE/Nexus-Terminal/releases/download/plugins/cloudflared.zip"


def check_cloudflared(cloudflared_path=None):
    """Check if cloudflared binary is available.

    Args:
        cloudflared_path: Optional explicit path from config file.

    Returns:
        True if cloudflared is found, False otherwise.
    """
    if cloudflared_path and os.path.isfile(cloudflared_path):
        return True
    return shutil.which('cloudflared') is not None


def get_cloudflared_version(binary='cloudflared'):
    """Get cloudflared version string.

    Returns the version (e.g. '2024.7.3') or None if it cannot be determined.
    """
    try:
        result = subprocess.run(
            [binary, 'version'],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (result.stdout or '') + (result.stderr or '')
        # cloudflared version output formats vary, e.g.:
        #   "cloudflared version 2024.7.3"
        #   "INF Version 2024.7.3"
        match = re.search(r'(\d+\.\d+\.\d+)', output)
        return match.group(1) if match else None
    except Exception:
        return None


def run_tunnel(url, cloudflared_path=None, messages=None):
    """Run 'cloudflared tunnel --url <url>' as a foreground process.

    Handles Ctrl+C gracefully to ensure the child process is terminated.

    Args:
        url: The URL to tunnel.
        cloudflared_path: Optional explicit path to cloudflared binary.
        messages: i18n messages dict for localized output.

    Returns:
        Process exit code.
    """
    if cloudflared_path and os.path.isfile(cloudflared_path):
        binary = cloudflared_path
    else:
        binary = 'cloudflared'

    cmd = [binary, 'tunnel', '--url', url]

    if messages:
        print(messages['tunnel_starting'], flush=True)

    # Use Popen so we can explicitly terminate the child on Ctrl+C,
    # avoiding orphaned cloudflared processes.
    proc = subprocess.Popen(cmd)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        if messages:
            print(messages['tunnel_stopped'])
    return proc.returncode


# ---------------------------------------------------------------------------
# Download & Install
# ---------------------------------------------------------------------------

def _download_progress(block_num, block_size, total_size):
    """Progress callback for urllib.urlretrieve."""
    if total_size > 0:
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 // total_size)
        bar_len = 30
        filled = bar_len * percent // 100
        bar = '#' * filled + '-' * (bar_len - filled)
        sys.stdout.write(f'\r  [{bar}] {percent}%')
        sys.stdout.flush()
        if percent >= 100:
            print()


def download_and_extract_cf(messages=None):
    """Download cloudflared.zip, extract it, and return the path to cloudflared.exe."""
    temp_dir = tempfile.mkdtemp(prefix="nt_cf_")
    zip_path = os.path.join(temp_dir, "cloudflared.zip")

    if messages:
        print(messages['cf_downloading'])

    url = get_cf_download_url()
    urllib.request.urlretrieve(url, zip_path, _download_progress)

    if messages:
        print(messages['cf_extracting'])

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_dir)

    # Locate cloudflared.exe (may be at root or in a subdirectory)
    exe_path = os.path.join(temp_dir, CF_EXE_NAME)
    if not os.path.exists(exe_path):
        for root, _dirs, files in os.walk(temp_dir):
            if CF_EXE_NAME in files:
                exe_path = os.path.join(root, CF_EXE_NAME)
                break
        else:
            raise FileNotFoundError("cloudflared.exe not found in archive")

    return exe_path


def install_cf(exe_path, messages=None):
    """Install cloudflared.exe to C:\\Windows\\System32.

    Tries a direct copy first; if permission is denied, re-launches an
    elevated process via UAC to perform the copy (waits for completion).

    Returns True on success, False on failure.
    """
    target = os.path.join(CF_INSTALL_DIR, CF_EXE_NAME)

    if messages:
        print(messages['cf_installing'])

    # Try direct copy first (works if we already have admin rights)
    try:
        shutil.copy2(exe_path, target)
        return True
    except PermissionError:
        pass

    # Need elevation — use PowerShell Start-Process -Verb RunAs -Wait
    return _install_elevated(exe_path, target, messages)


def _install_elevated(exe_path, target, messages=None):
    """Copy to System32 using an elevated process (triggers UAC prompt)."""
    if messages:
        print(messages['cf_uac_prompt'])

    # Write a batch file to avoid quoting issues with spaces in paths
    bat_path = os.path.join(tempfile.gettempdir(), "nt_install_cf.bat")
    with open(bat_path, 'w') as f:
        f.write(f'@echo off\r\ncopy /Y "{exe_path}" "{target}"\r\n')

    try:
        ps_script = (
            f"Start-Process cmd -ArgumentList "
            f"'/c \"{bat_path}\"' -Verb RunAs -Wait"
        )
        subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_script],
            capture_output=True,
            timeout=120,
        )
        return os.path.exists(target)
    except Exception:
        return False


def ensure_cloudflared(config_path=None, messages=None):
    """Ensure cloudflared is available; if not, prompt to download & install.

    Returns True if cloudflared is available (already installed or just
    installed), False if the user declined or installation failed.
    """
    if check_cloudflared(config_path):
        return True

    if messages:
        print(messages['cf_not_found'])

    try:
        choice = input(messages['cf_download_prompt']).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False

    if choice not in ('y', 'yes'):
        return False

    try:
        exe_path = download_and_extract_cf(messages)
        if not install_cf(exe_path, messages):
            if messages:
                print(messages['cf_install_failed'])
            return False

        if messages:
            print(messages['cf_install_success'])

        # Verify — check_cloudflared() searches PATH (System32 is always there)
        return check_cloudflared()
    except Exception as e:
        if messages:
            print(messages['cf_download_failed'].format(e))
        return False
