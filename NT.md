# Nexus Terminal

基于 Python 的轻量级 CLI 工具，用于 Cloudflare 隧道与自定义命令映射。

## 命令

| 命令 | 说明 |
|------|------|
| `nt u <port>` | 快速暴露本地端口（默认 IPv4: 127.0.0.1） |
| `nt u -v6 <port>` | 使用 IPv6 ([::1]) 暴露端口 |
| `nt url <url>` | 通过完整 URL 建立 cloudflare 隧道 |
| `nt server <port>` | 启动 HTTP 文件服务器 |
| `nt c` | 进入自定义命令向导 |
| `nt c -ls` | 列出所有自定义命令 |
| `nt c -rm <前缀>` | 删除自定义命令 |
| `nt install cf` | 安装 cloudflared 到 System32 |
| `nt ip` | 显示本机 IP 地址 |
| `nt ports` | 列出监听中的端口 |
| `nt <前缀>` | 执行自定义命令 |
| `nt help` | 显示帮助信息 |
| `nt version` | 显示版本信息 |
| `nt` | 无参数显示帮助 |

### 示例

```bash
nt u 5000              # 暴露 127.0.0.1:5000
nt u -v6 5000          # 暴露 [::1]:5000
nt u 5000 -v6          # 子参数顺序灵活
nt U 5000              # 大小写不敏感
nt url http://localhost:8080
nt server 5000         # 启动 HTTP 文件服务器
nt s 5000              # 简写
nt c                   # 创建自定义命令
nt c -ls               # 列出自定义命令
nt c -rm mytunnel      # 删除自定义命令
nt install cf          # 安装 cloudflared
nt ip                  # 显示本机 IP
nt ports               # 列出监听端口
nt mytunnel            # 执行自定义命令
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

保留前缀（不可用于自定义命令）：`help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports`

---

# Nexus Terminal

A lightweight Python CLI tool for Cloudflare tunnels and custom command mapping.

## Commands

| Command | Description |
|---------|-------------|
| `nt u <port>` | Quick tunnel for local port (default: IPv4 127.0.0.1) |
| `nt u -v6 <port>` | Use IPv6 ([::1]) |
| `nt url <url>` | Create a tunnel via full URL |
| `nt server <port>` | Start HTTP file server |
| `nt c` | Enter custom command wizard |
| `nt c -ls` | List all custom commands |
| `nt c -rm <prefix>` | Remove a custom command |
| `nt install cf` | Install cloudflared to System32 |
| `nt ip` | Show local IP addresses |
| `nt ports` | List listening ports |
| `nt <prefix>` | Execute a custom command |
| `nt help` | Show help |
| `nt version` | Show version |
| `nt` | No args shows help |

### Examples

```bash
nt u 5000              # Tunnel 127.0.0.1:5000
nt u -v6 5000          # Tunnel [::1]:5000
nt u 5000 -v6          # Sub-arg order is flexible
nt U 5000              # Case-insensitive
nt url http://localhost:8080
nt server 5000         # Start HTTP file server
nt s 5000              # Shorthand
nt c                   # Create custom command
nt c -ls               # List custom commands
nt c -rm mytunnel      # Remove custom command
nt install cf          # Install cloudflared
nt ip                  # Show local IP
nt ports               # List listening ports
nt mytunnel            # Execute custom command
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

Reserved prefixes: `help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports`
