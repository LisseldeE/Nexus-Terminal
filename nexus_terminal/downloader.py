"""Multi-threaded file downloader.

Supports parallel chunked downloads via HTTP Range headers, with automatic
fallback to single-thread when the server does not support Range requests.
"""

import os
import re
import sys
import threading
import urllib.request
from urllib.parse import urlparse


class DownloadProgress:
    """Thread-safe progress tracker for aggregated download progress."""
    def __init__(self, total_size):
        self.total_size = total_size
        self.downloaded = 0
        self.lock = threading.Lock()

    def add(self, bytes_count):
        with self.lock:
            self.downloaded += bytes_count

    def get_percent(self):
        if self.total_size <= 0:
            return 0
        return min(100, self.downloaded * 100 // self.total_size)


def _format_size(size):
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'


def _resolve_url(url):
    """Follow redirects and return the final URL."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.url
    except Exception:
        return url


def _get_file_info(url):
    """Get file size and Range support via HEAD request.

    Returns:
        (size_in_bytes, supports_range, final_url) or (None, False, url)
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as resp:
            size = resp.headers.get('Content-Length')
            accept_ranges = resp.headers.get('Accept-Ranges', '')
            return (
                int(size) if size else None,
                'bytes' in accept_ranges,
                resp.url,  # final URL after redirects
            )
    except Exception:
        return (None, False, url)


def _extract_filename(url, response=None):
    """Extract filename from Content-Disposition header or URL path."""
    if response:
        cd = response.headers.get('Content-Disposition')
        if cd:
            match = re.search(r'filename="?([^"]+)"?', cd)
            if match:
                return match.group(1)
    path = urlparse(url).path
    basename = os.path.basename(path)
    if basename and basename != '/':
        return basename
    return 'download'


def _download_chunk(url, start, end, file_path, progress, timeout=30):
    """Download a byte range of a file and write it at the correct offset."""
    headers = {'Range': f'bytes={start}-{end}'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        with open(file_path, 'rb+') as f:
            f.seek(start)
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                progress.add(len(chunk))


def _download_single(url, output_path, messages=None):
    """Fallback single-thread download via urlretrieve."""
    if messages:
        print(messages['download_single_mode'])

    def _progress(block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            pct = min(100, downloaded * 100 // total_size)
            bar_len = 30
            filled = bar_len * pct // 100
            bar = '#' * filled + '-' * (bar_len - filled)
            sys.stdout.write(f'\r  [{bar}] {pct}%')
            sys.stdout.flush()
            if pct >= 100:
                print()

    try:
        urllib.request.urlretrieve(url, output_path, _progress)
        if messages:
            print(messages['download_success'].format(output_path))
        return output_path
    except Exception as e:
        if messages:
            print(messages['download_failed'].format(e))
        return None


def download_file(url, output_dir=None, num_threads=4, messages=None):
    """Multi-threaded file download.

    Downloads a file from *url* using parallel chunked requests.
    If the server does not support Range headers, falls back to
    single-thread download.

    Args:
        url: The URL to download from.
        output_dir: Directory to save the file (default: current working dir).
        num_threads: Number of parallel download threads (default: 4).
        messages: i18n messages dict for localized output.

    Returns:
        The absolute path to the downloaded file, or None on failure.
    """
    if output_dir is None:
        output_dir = os.getcwd()

    # Resolve the final URL first
    final_url = _resolve_url(url)

    # Get file info
    size, supports_range, _final_url = _get_file_info(final_url)

    if size is None or size == 0:
        # Cannot determine size — fall back to single-thread
        filename = _extract_filename(final_url)
        output_path = os.path.join(output_dir, filename)
        return _download_single(final_url, output_path, messages)

    if not supports_range:
        if messages:
            print(messages['download_no_range'])
        filename = _extract_filename(final_url)
        output_path = os.path.join(output_dir, filename)
        return _download_single(final_url, output_path, messages)

    # Determine filename
    try:
        sample_resp = urllib.request.urlopen(final_url, timeout=10)
        filename = _extract_filename(final_url, sample_resp)
        sample_resp.close()
    except Exception:
        filename = _extract_filename(final_url)

    output_path = os.path.join(output_dir, filename)

    if messages:
        print(messages['download_starting'].format(filename, _format_size(size)))

    # Pre-allocate the file
    try:
        with open(output_path, 'wb') as f:
            f.truncate(size)
    except IOError as e:
        if messages:
            print(messages['download_failed'].format(str(e)))
        return None

    # Calculate chunk boundaries
    chunk_size = size // num_threads
    chunks = []
    for i in range(num_threads):
        start = i * chunk_size
        if i < num_threads - 1:
            end = (i + 1) * chunk_size - 1
        else:
            end = size - 1
        chunks.append((start, end))

    progress = DownloadProgress(size)
    errors = []
    error_lock = threading.Lock()

    def _worker(start, end):
        try:
            _download_chunk(final_url, start, end, output_path, progress)
        except Exception as e:
            with error_lock:
                errors.append(e)

    # Launch threads
    threads = []
    for start, end in chunks:
        t = threading.Thread(target=_worker, args=(start, end))
        threads.append(t)
        t.start()

    # Progress display loop
    if messages:
        bar_len = 30
        try:
            while any(t.is_alive() for t in threads):
                pct = progress.get_percent()
                filled = bar_len * pct // 100
                bar = '#' * filled + '-' * (bar_len - filled)
                sys.stdout.write(f'\r  [{bar}] {pct}%')
                sys.stdout.flush()
                threading.Event().wait(0.1)
        except KeyboardInterrupt:
            print()
            if messages:
                print(messages['download_cancelled'])
            # Clean up partial file
            try:
                os.remove(output_path)
            except OSError:
                pass
            return None

    # Wait for all threads
    for t in threads:
        t.join()

    if errors:
        if messages:
            print()
            print(messages['download_failed'].format(str(errors[0])))
        try:
            os.remove(output_path)
        except OSError:
            pass
        return None

    # Final progress line
    if messages:
        print(f'\r  [{"#" * bar_len}] 100%')
        print(messages['download_success'].format(output_path))

    return output_path