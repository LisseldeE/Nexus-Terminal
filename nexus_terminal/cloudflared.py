"""Cloudflared detection and tunnel runner."""

import os
import shutil
import subprocess


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
