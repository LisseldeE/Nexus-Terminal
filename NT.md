# Nexus Terminal

## 命令

| 命令 | 说明 |
|------|------|
| `nt` | 无参数进入交互模式 |
| `nt u <port\|url>` | 建立隧道（端口默认 IPv4: 127.0.0.1，或完整 URL） |
| `nt u -v6 <port>` | 使用 IPv6 ([::1]) 暴露端口 |
| `nt url <url>` | `u` 的别名，通过完整 URL 建立隧道 |
| `nt server <port>` | 启动 HTTP 文件服务器（简写 `nt s`） |
| `nt c` | 进入自定义命令向导 |
| `nt c -ls` | 列出所有自定义命令 |
| `nt c -rm <前缀>` | 删除自定义命令 |
| `nt install cf` | 安装 cloudflared 到 System32（已安装则显示版本） |
| `nt tool` | 系统工具集 |
| `nt tool jurisdiction <user>` | 递归更改当前目录文件所有者为选定用户 |
| `nt renew` | 检查更新（从远程仓库读取版本信息） |
| `nt ip` | 显示本机 IP 地址 |
| `nt ports` | 列出监听中的端口 |
| `nt kill [port]` | 终止占用端口的进程（无参进入交互选择） |
| `nt download <url>` | 多线程下载文件到当前目录 |
| `nt hash [file]` | 计算文件哈希值 (MD5/SHA1/SHA256) |
| `nt monitor [port]` | 实时监控端口进程 CPU、内存、网络等资源占用 |
| `nt <前缀>` | 执行自定义命令 |
| `nt help` | 显示帮助信息 |
| `nt version` | 显示版本信息 |

### 交互模式

直接输入 `nt`（无参数）进入交互模式：

- **↑↓** 选择选项
- **Enter** 确认 / 执行
- **Esc** 返回上一级 / 退出
- **Ctrl+C** 静默退出

支持多级菜单：
- `url` → 选择协议 (IPv4/IPv6) → 输入端口
- `server` → 输入端口
- `custom` → 创建 / 列表 / 删除
- `install` → 选择安装组件
- `download` → 输入下载地址
- `hash` → 选择文件 → 显示哈希值
- `monitor` → 选择端口 → 实时监控
- `tool` → 选择工具 (jurisdiction: 选择所有者 → 确认)
- `renew` → 检查更新

### 示例

```bash
nt                      # 进入交互模式
nt u 5000               # 暴露 127.0.0.1:5000
nt u -v6 5000           # 暴露 [::1]:5000
nt u 5000 -v6           # 子参数顺序灵活
nt U 5000               # 大小写不敏感
nt u http://localhost:8080  # 通过 URL 建立隧道
nt url http://localhost:8080 # 同上
nt server 5000          # 启动 HTTP 文件服务器
nt s 5000               # 简写
nt c                    # 创建自定义命令
nt c -ls                # 列出自定义命令
nt c -rm mytunnel       # 删除自定义命令
nt install cf           # 安装 cloudflared
nt ip                   # 显示本机 IP
nt ports                # 列出监听端口
nt kill                 # 交互选择进程终止
nt kill 5000            # 终止占用 5000 端口的进程
nt mytunnel             # 执行自定义命令
```

### 配置

路径：`~/.nexusterminal/config.json`

```json
{
  "language": "auto",
  "cloudflared_path": null,
  "custom_commands": {
    "mytunnel": { "command": "...", "description": "..." }
  }
}
```

保留前缀（不可用于自定义命令）：`help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports` `kill` `download` `tool` `renew` `monitor` `hash`

---

# Nexus Terminal

A lightweight Python CLI tool for Cloudflare tunnels and custom command mapping.

## Commands

| Command | Description |
|---------|-------------|
| `nt` | No args enters interactive mode |
| `nt u <port\|url>` | Create a tunnel (port defaults to IPv4 127.0.0.1, or full URL) |
| `nt u -v6 <port>` | Use IPv6 ([::1]) |
| `nt url <url>` | Alias of `u`, create a tunnel via full URL |
| `nt server <port>` | Start HTTP file server (shorthand `nt s`) |
| `nt c` | Enter custom command wizard |
| `nt c -ls` | List all custom commands |
| `nt c -rm <prefix>` | Remove a custom command |
| `nt install cf` | Install cloudflared to System32 (shows version if already installed) |
| `nt tool` | System tools |
| `nt tool jurisdiction <user>` | Recursively change file owner in CWD to the selected user |
| `nt renew` | Check for updates (fetches version info from remote repos) |
| `nt ip` | Show local IP addresses |
| `nt ports` | List listening ports |
| `nt kill [port]` | Kill process by port (no arg = interactive) |
| `nt download <url>` | Multi-threaded download to current directory |
| `nt hash [file]` | Calculate file hash (MD5/SHA1/SHA256) |
| `nt monitor [port]` | Real-time process monitoring (CPU, memory, network) |
| `nt <prefix>` | Execute a custom command |
| `nt help` | Show help |
| `nt version` | Show version |

### Interactive Mode

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
- `download` → input URL
- `hash` → select file → show hash values
- `monitor` → select port → real-time monitoring
- `tool` → select tool (jurisdiction: select owner → confirm)
- `renew` → check for updates

### Examples

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

### Config

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

Reserved prefixes: `help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports` `kill` `download` `tool` `renew` `monitor`
