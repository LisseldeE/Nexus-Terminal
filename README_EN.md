# Nexus Terminal - Lightweight CLI Tool

## Project Introduction

Nexus Terminal is a lightweight Python CLI tool that integrates Cloudflare tunnels, custom command mapping, and network utilities. Provides an efficient development experience through interactive menus or direct command-line invocation.

## Project Information

- **Project Name**: Nexus Terminal
- **Project Author**: Lisselde_E
- **Project Repository**: https://github.com/LisseldeE/Nexus-Terminal

## Download

- **GitHub Releases**: https://github.com/LisseldeE/Nexus-Terminal/releases

Download `nt.exe` and place it in `C:\Windows\System32\` to use the `nt` command from any terminal.

## Command List

| Command | Description |
|---------|-------------|
| `nt u <port\|url>` | Create a tunnel (port defaults to IPv4 127.0.0.1, or full URL) |
| `nt u -v6 <port>` | Use IPv6 ([::1]) |
| `nt url <url>` | Alias of `u`, create a tunnel via full URL |
| `nt server <port>` | Start HTTP file server (shorthand `nt s`) |
| `nt c` | Enter custom command wizard |
| `nt c -ls` | List all custom commands |
| `nt c -rm <prefix>` | Remove a custom command |
| `nt install cf` | Install cloudflared to System32 (shows version if already installed) |
| `nt ip` | Show local IP addresses |
| `nt ports` | List listening ports |
| `nt kill [port]` | Kill process by port (no arg = interactive) |
| `nt <prefix>` | Execute a custom command |
| `nt help` | Show help |
| `nt version` | Show version |
| `nt` | No args enters interactive mode |

## Interactive Mode

Type `nt` (no arguments) to enter interactive mode:

- **Up/Down** arrows to navigate
- **Enter** to confirm / execute
- **Esc** to go back / cancel
- **Ctrl+C** to exit silently

Supports multi-level menus:
- `url` → select protocol (IPv4/IPv6) → input port
- `server` → input port
- `custom` → create / list / remove
- `install` → select component to install
- `kill` → select a listening port's process to kill

## Examples

```bash
nt                      # Enter interactive mode
nt u 5000               # Tunnel 127.0.0.1:5000
nt u -v6 5000           # Tunnel [::1]:5000
nt u 5000 -v6           # Sub-arg order is flexible
nt U 5000               # Case-insensitive
nt u http://localhost:8080  # Tunnel via URL
nt url http://localhost:8080 # Same as above
nt server 5000          # Start HTTP file server
nt s 5000               # Shorthand
nt c                    # Create custom command
nt c -ls                # List custom commands
nt c -rm mytunnel       # Remove custom command
nt install cf           # Install cloudflared
nt ip                   # Show local IP
nt ports                # List listening ports
nt kill                 # Interactive kill
nt kill 5000            # Kill process on port 5000
nt mytunnel             # Execute custom command
```

## Config

Path: `~/.nexusterminal/config.json`

```json
{
  "language": "auto",
  "cloudflared_path": null,
  "custom_commands": {
    "mytunnel": { "command": "...", "description": "..." }
  }
}
```

Reserved prefixes: `help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports` `kill`

## Change Log

See [Changelog](CHANGELOG.md)

## Tech Stack

- Python 3.x
- Pure standard library (zero third-party dependencies)
- Compiled with Nuitka

## Installation & Running

### Option 1: Use Compiled Version

Download `nt.exe`, place it in `C:\Windows\System32\`, and use the `nt` command from any terminal.

### Option 2: Run from Source

```bash
python NT.py
```

### System Requirements

- Windows 10 or higher
- Python 3.6 or higher (when running from source)

## Feedback

**This application is under development, if you have any questions or new ideas, feel free to contact me!**

Issues and Pull Requests are welcome!
