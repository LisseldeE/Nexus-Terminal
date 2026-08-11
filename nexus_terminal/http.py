"""Quick HTTP request — GET a URL, display status, timing, headers, body preview."""

import urllib.request
import urllib.error
import time
import sys


def _format_size(n):
    """Format a byte count human-readably."""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f'{n:.1f} {unit}'
        n /= 1024
    return f'{n:.1f} TB'


def _truncate_body(text, max_lines=20, max_chars=2000):
    """Truncate body text for preview display."""
    lines = text.splitlines()
    total = len(lines)
    truncated = False

    if total > max_lines:
        lines = lines[:max_lines]
        truncated = True

    # Check total character count
    out = '\n'.join(lines)
    if len(out) > max_chars:
        out = out[:max_chars]
        truncated = True

    return out, truncated, total


def http_request(url, messages):
    """Send a GET request to the URL and display results.

    Args:
        url: URL to request.
        messages: i18n messages dict.

    Returns:
        Exit code (0 or 1).
    """
    # Auto-prepend http:// if no scheme given
    if '://' not in url:
        url = 'http://' + url

    print()
    print(messages['http_connecting'].format(url=url))

    start = time.perf_counter()

    try:
        req = urllib.request.Request(url, method='GET')
        # Set a common User-Agent to avoid being blocked
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=15) as resp:
            elapsed = time.perf_counter() - start
            body_bytes = resp.read()
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start
        print(messages['http_error'].format(error=f'{e.code} {e.reason}'))
        print()
        return 1
    except urllib.error.URLError as e:
        elapsed = time.perf_counter() - start
        reason = e.reason
        if isinstance(reason, str):
            msg = reason
        else:
            msg = str(reason)
        print(messages['http_error'].format(error=msg))
        print()
        return 1
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(messages['http_error'].format(error=str(e)))
        print()
        return 1

    # --- Status line ---
    status = resp.status
    reason = resp.reason
    size = len(body_bytes)
    print(messages['http_separator'])
    print(f'  {messages["http_status"]}:  {status} {reason}')
    print(f'  {messages["http_time"]}:    {elapsed:.3f}s')
    print(f'  {messages["http_size"]}:    {_format_size(size)}')
    print()

    # --- Headers ---
    print(f'  {messages["http_headers"]}:')
    for key, value in resp.getheaders():
        print(f'    {key}: {value}')
    print()

    # --- Body preview ---
    # Try to decode as UTF-8; fallback to showing raw size
    content_type = resp.headers.get('Content-Type', '')
    if 'text' in content_type or 'json' in content_type or 'xml' in content_type:
        try:
            body_text = body_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                body_text = body_bytes.decode('latin-1')
            except Exception:
                body_text = None

        if body_text is not None:
            preview, truncated, total_lines = _truncate_body(body_text)
            print(f'  {messages["http_body"]}:')
            print()
            for line in preview.splitlines():
                # Truncate very long lines for display
                if len(line) > 200:
                    line = line[:197] + '...'
                print(f'    {line}')
            if truncated:
                more = total_lines - 20
                print(f'    ... ({messages["http_more_lines"].format(n=more)})')
            print()

    print(messages['http_separator'])
    print()
    return 0


def handle_http(args, messages):
    """Entry point for ``nt http``.

    Direct forms:
      nt http <url>    — GET request, display results
      nt http          — interactive: input URL
    """
    from nexus_terminal.interactive import prompt_input, InteractiveExit

    if args:
        return http_request(args[0], messages)

    try:
        url = prompt_input('URL:', messages)
        if url is None:
            return 0
    except InteractiveExit:
        return 0

    return http_request(url, messages)