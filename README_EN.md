# Nexus Terminal - Terminal Assistant Tool

<p align="center">
  <a href="https://github.com/LisseldeE/Nexus-Terminal/releases"><img src="https://img.shields.io/github/v/release/LisseldeE/Nexus-Terminal" alt="Latest Version"></a>
  <a href="https://github.com/LisseldeE/Nexus-Terminal/releases"><img src="https://img.shields.io/github/release-date/LisseldeE/Nexus-Terminal" alt="Release Date"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/LisseldeE/Nexus-Terminal" alt="License"></a>
  <img src="https://img.shields.io/badge/platform-Windows-blue?logo=windows" alt="Platform">
</p>

## Project Introduction

Nexus Terminal is a lightweight Python-based terminal assistant tool that provides a rich set of built-in commands alongside custom command shortcuts, streamlining your terminal workflow and boosting productivity.

No need to memorize complex command parameters. Whether through an intuitive interactive menu or concise CLI calls, you can quickly set up tunnels, manage ports, download files, spin up HTTP servers, and handle other everyday development tasks.

## Screenshots

![Interface](https://lisseldee.github.io/images/webp/6-1.webp)

## Project Information

- **Project Name**: Nexus Terminal
- **Project Author**: Lisselde_E
- **Project Homepage**: https://lisseldee.github.io/#6
- **Project Repository**: https://github.com/LisseldeE/Nexus-Terminal

## Download

- **GitHub Releases**: https://github.com/LisseldeE/Nexus-Terminal/releases

Download `nt.exe` and place it in `C:\Windows\System32\`. The `nt` command will then be available from any terminal without any environment variable configuration.

## Features

### Quick Navigation
- Interactive Mode
- Network
    - Tunnel (u / url)
    - IP Query (ip)
    - Route Trace (trace)
- Process Management
    - Port List (ports)
    - Port Kill (kill)
    - Process Monitor (monitor)
- File
    - File Server (server)
    - File Download (download)
    - File Hash (hash)
- System
    - Install (install)
    - System Tools (tool)
    - Check Update (renew)
- Custom Commands (c)
- Help (help)
- Version (version)

### Tunnel Service
- One-command Cloudflare tunnel setup to expose local ports instantly
- IPv4/IPv6 protocol selection
- Full URL tunnel support (`nt url <url>`)
- Automatic cloudflared binary detection and installation

### Custom Command Mapping
- Map any shell command to a short prefix of your choice
- Execute via `nt <prefix>`, case-insensitive
- Interactive wizard for creation, listing, and deletion

### Port Management
- List all listening ports with associated process names
- One-command kill for processes occupying a specific port
- Both interactive selection and direct port specification supported

### File Download
- Multi-threaded parallel downloads with Range header support
- Graceful fallback to single-thread when server doesn't support Range
- Real-time progress bar display

### Network Tools
- Local IP address lookup (IPv4/IPv6)
- Listening port listing (process name, PID, port number)

### HTTP Server
- Quick-start HTTP file server
- Any port can be specified
- Graceful handling of port in-use, permission denied, and other errors

### System Tools
- Recursive file ownership change (`takeown` + `icacls`)
- Target options: Current User or Everyone
- Automatic administrator privilege detection with clear prompts

### Interactive Mode
- No command memorization required — navigate with arrow keys, confirm with Enter
- Multi-level menu guidance for step-by-step operations
- Real-time command filtering for quick navigation
- All menu UI auto-clears after selection, leaving only execution results

## Command List

| Command | Description |
|---------|-------------|
| `nt` | Enter interactive mode |
| `nt u <port\|url>` | Create a tunnel (default IPv4: 127.0.0.1, or full URL) |
| `nt u -v6 <port>` | Use IPv6 ([::1]) |
| `nt url <url>` | Alias of `u`, create a tunnel via full URL |
| `nt server <port>` | Start HTTP file server (shorthand `nt s`) |
| `nt c` | Enter custom command wizard |
| `nt c -ls` | List all custom commands |
| `nt c -rm <prefix>` | Remove a custom command |
| `nt install cf` | Install cloudflared to System32 (shows version if already installed) |
| `nt ip` | Show local IP addresses |
| `nt ports` | List listening ports |
| `nt kill [port]` | Kill process by port (no arg = interactive selection) |
| `nt download <url>` | Multi-threaded download to current directory |
| `nt tool` | Enter system tools |
| `nt tool jurisdiction <current_user\|Everyone>` | Recursively change file owner in CWD to the selected user |
| `nt <prefix>` | Execute a custom command |
| `nt help` | Show help |
| `nt version` | Show version |

## Interactive Mode

Type `nt` (no arguments) to enter interactive mode:

```
Nexus Terminal R1.1.0.0 - Interactive Mode
Up/Down Navigate  Enter Confirm  Esc Cancel

❯ url      Create a tunnel
  server   Start HTTP file server
  install  Install components
  ip       Show local IP addresses
  ports    List listening ports
  kill     Kill process by port
  download Multi-threaded file download
  tool     System tools
  version  Show version information
  custom   Custom command management
  ...      [custom command list]
  help     Show help message
  exit     Exit
```

### Key Controls

| Key | Action |
|-----|--------|
| **Up/Down** | Navigate options |
| **Enter** | Confirm / Execute |
| **Esc** | Go back / Cancel |
| **Ctrl+C** | Exit silently |

### Multi-level Menus

| Menu Item | Sub-flow |
|-----------|----------|
| `url` | Select protocol (IPv4/IPv6) → Enter port |
| `server` | Enter port |
| `custom` | Create / List / Remove |
| `install` | Select component to install |
| `kill` | Select a listening port's process to kill |
| `download` | Enter download URL |
| `tool` | Select tool (jurisdiction: select owner → confirm) |

## Examples

```bash
# Interactive mode
nt

# Tunnels
nt u 5000                     # Expose 127.0.0.1:5000
nt u -v6 5000                 # Expose [::1]:5000
nt u 5000 -v6                 # Sub-arg order is flexible
nt U 5000                     # Case-insensitive
nt u http://localhost:8080    # Tunnel via URL
nt url http://localhost:8080  # Same as above

# HTTP file server
nt server 5000
nt s 5000

# Custom commands
nt c                          # Create custom command
nt c -ls                      # List custom commands
nt c -rm mytunnel             # Remove custom command
nt mytunnel                   # Execute custom command

# Install cloudflared
nt install cf

# Network tools
nt ip                         # Show local IP
nt ports                      # List listening ports

# Process management
nt kill                       # Interactive kill
nt kill 5000                  # Kill process on port 5000

# File download
nt download https://example.com/file.zip

# System tools
nt tool jurisdiction Everyone  # Recursively change owner to Everyone
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

Reserved prefixes: `help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports` `kill` `download` `tool`

## Change Log

See [Changelog](CHANGELOG.md)

## Tech Stack

- Python 3.x
- Pure standard library (zero third-party dependencies)
- Compiled with Nuitka for single-file distribution

## Installation & Running

### System Requirements

- Windows 10 or higher
- Python 3.6 or higher (when running from source)

### How to Run

1. Download `nt.exe` from [Releases](https://github.com/LisseldeE/Nexus-Terminal/releases)
2. Place `nt.exe` in `C:\Windows\System32\`
3. Use the `nt` command from any terminal

## Feedback

**This application is under development. If you have any questions or new ideas, feel free to reach out!**

Issues and Pull Requests are welcome!