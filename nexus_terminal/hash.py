"""File hash calculator — MD5, SHA1, SHA256."""

import hashlib
import os


def _calculate_hashes(filepath):
    """Calculate MD5, SHA1, SHA256 for a file.

    Returns (md5, sha1, sha256) hex digest strings.
    """
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)

    return md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest()


def hash_file(filepath, messages):
    """Calculate and display hash values for a file.

    Args:
        filepath: Path to the file (relative to CWD or absolute).
        messages: i18n messages dict.

    Returns:
        Exit code (0 or 1).
    """
    abs_path = os.path.abspath(filepath)
    if not os.path.isfile(abs_path):
        print(messages['hash_file_not_found'].format(filepath))
        return 1

    filename = os.path.basename(abs_path)

    try:
        md5, sha1, sha256 = _calculate_hashes(abs_path)
    except Exception as e:
        print(messages['hash_error'].format(e))
        return 1

    print()
    print(messages['hash_separator'])
    print(messages['hash_header'].format(name=filename))
    print(messages['hash_separator'])
    print(messages['hash_md5'].format(hash=md5))
    print(messages['hash_sha1'].format(hash=sha1))
    print(messages['hash_sha256'].format(hash=sha256))
    print(messages['hash_separator'])
    print()
    return 0


def hash_interactive(messages):
    """Interactive file selection for hash calculation.

    Lists files in the current directory and lets the user choose one.
    """
    files = []
    for entry in os.scandir(os.getcwd()):
        if entry.is_file():
            files.append(entry.name)

    if not files:
        print(messages['hash_no_files'])
        return 1

    files.sort()

    from nexus_terminal.interactive import select_option, InteractiveExit, HAS_MSVCRT

    if not HAS_MSVCRT:
        print(messages['hash_usage'])
        return 1

    options = [(f, '') for f in files]

    try:
        choice = select_option(
            messages['hash_select_file'],
            messages['interactive_hint'],
            options,
            messages,
        )
        if choice is None:
            return 0
    except InteractiveExit:
        return 0

    return hash_file(choice, messages)