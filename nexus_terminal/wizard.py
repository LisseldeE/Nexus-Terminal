"""Custom command wizard and listing."""

import re

from .config import ConfigManager

# Prefixes reserved for built-in commands (used with -- prefix)
RESERVED_PREFIXES = {'help', 'url', 'version', 'u', 'c', 'install', 'ip', 'server', 's', 'ports', 'kill', 'download', 'tool', 'renew', 'monitor', 'hash', 'trace'}

# Valid prefix pattern: letters, numbers, hyphens, underscores
PREFIX_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


def run_wizard(messages):
    """Interactive wizard for adding a custom command.

    Flow:
      1. Prompt for custom prefix (validate: non-empty, valid chars, not reserved, not existing)
      2. Prompt for the mapped command (validate: non-empty)
      3. Prompt for optional description (empty = skip)
      4. Save to config file
    """
    config = ConfigManager()

    # Step 1: Enter prefix
    prefix = input(messages['wizard_prefix_prompt']).strip()
    if not prefix:
        print(messages['wizard_prefix_empty'])
        return
    if not PREFIX_PATTERN.match(prefix):
        print(messages['wizard_prefix_invalid'])
        return
    if prefix in RESERVED_PREFIXES:
        print(messages['wizard_prefix_reserved'].format(prefix))
        return
    if config.get_custom_command(prefix):
        print(messages['wizard_prefix_exists'].format(prefix))
        return

    # Step 2: Enter mapped command
    command = input(messages['wizard_command_prompt']).strip()
    if not command:
        print(messages['wizard_command_empty'])
        return

    # Step 3: Optional description
    description = input(messages['wizard_desc_prompt']).strip()

    # Step 4: Save
    config.add_custom_command(prefix, command, description)
    print(messages['wizard_added'].format(prefix))


def list_custom_commands(messages):
    """List all defined custom commands."""
    config = ConfigManager()
    commands = config.get_all_custom_commands()

    print(messages['wizard_list_header'])
    if not commands:
        print(messages['wizard_list_empty'])
        return

    for prefix, data in commands.items():
        if isinstance(data, dict):
            desc = data.get('description', '')
            cmd = data.get('command', '')
        else:
            # Backward compat: simple string mapping
            desc = ''
            cmd = str(data)

        # Show description if available, otherwise show the command itself
        display = desc if desc else cmd
        print(f'  {prefix:<18} {display}')


def remove_custom_command(prefix, messages):
    """Remove a custom command by prefix (non-interactive).

    Returns 0 on success, 1 if not found.
    """
    config = ConfigManager()
    if not config.get_custom_command(prefix):
        print(messages['wizard_rm_not_found'].format(prefix))
        return 1
    config.remove_custom_command(prefix)
    print(messages['wizard_rm_success'].format(prefix))
    return 0


def remove_custom_command_interactive(messages):
    """Interactive prompt to remove a custom command. Returns exit code."""
    prefix = input(messages['wizard_rm_prompt']).strip()
    if not prefix:
        print(messages['wizard_rm_empty'])
        return 1
    return remove_custom_command(prefix, messages)
