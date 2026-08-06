# Nexus Terminal - 轻量级 CLI 命令行工具

## 项目简介

Nexus Terminal 是一款基于 Python 的轻量级命令行工具，集成了 Cloudflare 隧道、自定义命令映射、网络工具等功能。通过交互式菜单或直接命令行调用，提供高效的开发体验。

## 项目信息

- **项目名称**: Nexus Terminal
- **项目作者**: Lisselde_E
- **项目仓库**: https://github.com/LisseldeE/Nexus-Terminal

## 下载

- **GitHub Releases**: https://github.com/LisseldeE/Nexus-Terminal/releases

下载 `nt.exe` 后放入 `C:\Windows\System32\` 即可在任意终端通过 `nt` 命令调用。

## 命令列表

| 命令 | 说明 |
|------|------|
| `nt u <port\|url>` | 建立隧道（端口默认 IPv4: 127.0.0.1，或完整 URL） |
| `nt u -v6 <port>` | 使用 IPv6 ([::1]) 暴露端口 |
| `nt url <url>` | `u` 的别名，通过完整 URL 建立隧道 |
| `nt server <port>` | 启动 HTTP 文件服务器（简写 `nt s`） |
| `nt c` | 进入自定义命令向导 |
| `nt c -ls` | 列出所有自定义命令 |
| `nt c -rm <前缀>` | 删除自定义命令 |
| `nt install cf` | 安装 cloudflared 到 System32（已安装则显示版本） |
| `nt ip` | 显示本机 IP 地址 |
| `nt ports` | 列出监听中的端口 |
| `nt kill [port]` | 终止占用端口的进程（无参进入交互选择） |
| `nt <前缀>` | 执行自定义命令 |
| `nt help` | 显示帮助信息 |
| `nt version` | 显示版本信息 |
| `nt` | 无参数进入交互模式 |

## 交互模式

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
- `kill` → 选择监听端口对应的进程终止

## 示例

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

## 配置

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

保留前缀（不可用于自定义命令）：`help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports` `kill`

## 更新日志

详见 [更新日志](CHANGELOG.md)

## 技术栈

- Python 3.x
- 纯标准库（零第三方依赖）
- Nuitka 编译打包

## 安装与运行

### 方式一：直接使用编译版

下载 `nt.exe`，放入 `C:\Windows\System32\`，即可在任意终端使用 `nt` 命令。

### 方式二：从源码运行

```bash
python NT.py
```

### 系统要求

- Windows 10 或更高版本
- Python 3.6 或更高版本（源码运行时）

## 反馈

**如有问题或新的创意欢迎和我联系！**

欢迎提交 Issue 和 Pull Request！
