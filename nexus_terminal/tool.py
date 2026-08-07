"""System tools — Windows-specific utility operations.

Currently implemented:
  - jurisdiction: Recursively change file/folder ownership in CWD.
"""

import subprocess
import os
import sys


def _is_admin():
    """Check if the current process is running as administrator."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _get_owner_label(target_owner, messages):
    """Get display label for the target owner type."""
    labels = {
        'current_user': messages.get('jurisdiction_label_current_user', 'Current User'),
        'Everyone': 'Everyone',
    }
    return labels.get(target_owner, target_owner)


def run_jurisdiction(target_owner, messages):
    """Recursively change ownership of all files in CWD.

    Technical approach:
      1. `takeown /F . /R /D Y` — Takes ownership for the current user.
         This handles TrustedInstaller-protected files and is the most
         reliable Windows-native way to gain ownership recursively.
      2. If target_owner is 'Everyone', additionally runs:
         `icacls . /setowner "Everyone" /T /Q` — Transfers ownership
         to Everyone group.

    Args:
        target_owner: 'current_user' or 'Everyone'.
        messages: i18n messages dict.

    Returns:
        0 on success, 1 on failure.
    """
    cwd = os.getcwd()

    # --- Admin check (elegant, early exit) ---
    if not _is_admin():
        print()
        print(messages['jurisdiction_no_admin'])
        print(messages['jurisdiction_admin_hint'])
        print()
        return 1

    owner_label = _get_owner_label(target_owner, messages)
    print()
    print(messages['jurisdiction_running'].format(
        target=owner_label, path=cwd
    ))

    # --- Step 1: takeown (always required) ---
    print(messages['jurisdiction_takeown_running'])
    try:
        result = subprocess.run(
            ['takeown', '/F', '.', '/R', '/D', 'Y'],
            capture_output=True, text=True, cwd=cwd
        )
        if result.returncode != 0:
            err = result.stderr.strip() or 'takeown failed'
            print(messages['jurisdiction_failed'].format(error=err))
            return 1
    except FileNotFoundError:
        print(messages['jurisdiction_no_takeown'])
        return 1
    except Exception as e:
        print(messages['jurisdiction_failed'].format(error=str(e)))
        return 1

    # --- Step 2: If target is Everyone, transfer ownership ---
    if target_owner == 'Everyone':
        print(messages['jurisdiction_setowner_running'])
        try:
            result = subprocess.run(
                ['icacls', '.', '/setowner', 'Everyone', '/T', '/Q'],
                capture_output=True, text=True, cwd=cwd
            )
            if result.returncode != 0:
                err = result.stderr.strip() or 'icacls /setowner failed'
                print(messages['jurisdiction_failed'].format(error=err))
                return 1
        except FileNotFoundError:
            print(messages['jurisdiction_no_icacls'])
            return 1
        except Exception as e:
            print(messages['jurisdiction_failed'].format(error=str(e)))
            return 1
        print(messages['jurisdiction_setowner_done'])

    print(messages['jurisdiction_done'])
    print()
    return 0


def handle_tool_command(args, messages):
    """Entry point for 'nt tool' — handles both interactive and direct execution.

    Args:
        args: Remaining CLI arguments after 'tool'.
        messages: i18n messages dict.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    from nexus_terminal.interactive import select_option, HAS_MSVCRT, InteractiveExit

    if not args:
        # nt tool — interactive tool picker
        if not HAS_MSVCRT:
            return _direct_usage(messages)

        try:
            tool = select_option(
                messages['tool_title'],
                messages['interactive_hint'],
                [
                    ('jurisdiction', messages['tool_desc_jurisdiction']),
                ],
                messages,
            )
        except InteractiveExit:
            return 0
        if tool is None:
            return 0
        args = [tool]

    tool_name = args[0]

    if tool_name == 'jurisdiction':
        return _handle_jurisdiction(args[1:], messages, select_option, HAS_MSVCRT, InteractiveExit)

    print(messages['tool_unknown'].format(tool=tool_name))
    return 1


def _handle_jurisdiction(args, messages, select_option, HAS_MSVCRT, InteractiveExit):
    """Handle jurisdiction: interactive selection or direct execution."""
    # Direct execution: nt tool jurisdiction Everyone
    if args:
        target_owner = args[0]
        if target_owner in ('current_user', 'Everyone'):
            return run_jurisdiction(target_owner, messages)
        print(messages['jurisdiction_usage'])
        return 1

    if not HAS_MSVCRT:
        print(messages['jurisdiction_usage'])
        return 1

    # Interactive: select target owner
    try:
        owner_options = [
            ('current_user', messages['jurisdiction_owner_current_user']),
            ('Everyone', messages['jurisdiction_owner_everyone']),
        ]
        target_owner = select_option(
            messages['jurisdiction_select_owner'],
            messages['interactive_hint'],
            owner_options,
            messages,
        )
        if target_owner is None:
            return 0

        # Confirm
        owner_label = _get_owner_label(target_owner, messages)
        cwd = os.getcwd()
        confirm_msg = messages['jurisdiction_confirm'].format(
            path=cwd, target=owner_label
        )
        confirmed = select_option(
            confirm_msg,
            messages['interactive_hint'],
            [
                ('yes', messages['jurisdiction_confirm_yes']),
                ('no', messages['jurisdiction_confirm_no']),
            ],
            messages,
        )
        if confirmed != 'yes':
            print(messages['jurisdiction_cancelled'])
            return 0

    except InteractiveExit:
        return 0

    return run_jurisdiction(target_owner, messages)


def _direct_usage(messages):
    """Print usage when terminal doesn't support interactive mode."""
    print(messages['tool_usage'])
    print(messages['jurisdiction_usage'])
    return 1