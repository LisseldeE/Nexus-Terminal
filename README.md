# Nexus Terminal - 终端辅助工具

<p align="center">
  <a href="https://github.com/LisseldeE/Nexus-Terminal/releases"><img src="https://img.shields.io/github/v/release/LisseldeE/Nexus-Terminal" alt="最新版本"></a>
  <a href="https://github.com/LisseldeE/Nexus-Terminal/releases"><img src="https://img.shields.io/github/release-date/LisseldeE/Nexus-Terminal" alt="发布时间"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/LisseldeE/Nexus-Terminal" alt="开源协议"></a>
  <img src="https://img.shields.io/badge/platform-Windows-blue?logo=windows" alt="支持平台">
</p>

## 项目简介

Nexus Terminal 是一款基于 Python 的轻量级终端辅助工具，提供多种预设命令以及自定义快捷命令映射，优化终端操作体验，提升使用效率。

无需繁琐的命令参数记忆，通过交互式菜单或简洁的命令行调用，即可快速完成隧道建立、端口管理、文件下载、HTTP 服务启动等日常开发操作。

## 项目截图

![界面](https://lisseldee.github.io/images/webp/6-1.webp)

## 项目信息

- **项目名称**: Nexus Terminal
- **项目作者**: Lisselde_E
- **项目主页**: https://lisseldee.github.io/#6
- **项目仓库**: https://github.com/LisseldeE/Nexus-Terminal

## 下载

- **Gitee Releases**: https://gitee.com/Lisselde_E/Nexus-Terminal/releases
- **GitHub Releases**: https://github.com/LisseldeE/Nexus-Terminal/releases

下载 `nt.exe` 后放入 `C:\Windows\System32\`，即可在任意终端中通过 `nt` 命令直接调用，无需配置环境变量。

## 功能特性

### 快速导航
- 交互模式
- 网络
    - 隧道 (u / url)
    - IP 查询 (ip)
    - 路由追踪 (trace)
    - DNS 查询 (dns)
    - 端口扫描 (scan)
    - HTTP 请求 (http)
- 进程管理
    - 端口列表 (ports)
    - 端口终止 (kill)
    - 进程监控 (monitor)
- 文件
    - 文件服务器 (server)
    - 文件下载 (download)
    - 文件哈希 (hash)
- 系统
    - hosts 管理 (hosts)
    - 安装 (install)
    - 系统工具 (tool)
    - 检查更新 (renew)
- 自定义命令 (c)
- 帮助 (help)
- 版本 (version)

### 隧道服务
- 一键建立 Cloudflare 隧道，快速暴露本地端口
- 支持 IPv4/IPv6 协议选择
- 支持完整 URL 隧道（`nt url <url>`）
- 自动检测并安装 cloudflared 运行时

### 自定义命令映射
- 支持将任意 Shell 命令映射为简短前缀
- 通过 `nt <前缀>` 直接执行，大小写不敏感
- 交互式向导创建、列表查询、删除管理

### 端口管理
- 列出所有监听端口及对应进程名
- 一键终止占用指定端口的进程
- 支持交互式选择进程和直接端口指定

### 文件下载
- 多线程并行下载，支持 Range 协议
- 自动降级为单线程（服务器不支持 Range 时）
- 实时进度条显示

### 网络工具
- 本机 IP 地址查询（IPv4/IPv6）
- 监听端口列表（进程名、PID、端口号）

### HTTP 服务
- 快速启动 HTTP 文件服务器
- 支持任意端口指定
- 自动处理端口占用、权限不足等异常

### 系统工具
- 递归更改文件所有者（`takeown` + `icacls`）
- 支持当前用户和 Everyone 两种目标
- 管理员权限自动检测，优雅提示

### 交互模式
- 无需记忆命令，方向键选择 + Enter 确认
- 多级菜单引导，循序渐进完成操作
- 实时过滤候选命令，快速定位
- 所有菜单操作完成后自动消失，仅保留执行结果

## 命令列表

详见 [命令列表](https://github.com/LisseldeE/Nexus-Terminal/blob/main/NT.md)

## 交互模式

直接输入 `nt`（无参数）进入交互模式：

```
Nexus Terminal R1.1.0.0 - 交互模式
↑↓ 选择  Enter 确认  Esc 退出

❯ url      建立隧道
  server   启动 HTTP 文件服务器
  install  安装组件
  ip       显示本机 IP 地址
  ports    列出监听端口
  kill     终止占用端口的进程
  download 多线程下载文件
  tool     系统工具集
  version  显示版本信息
  custom   自定义命令管理
  ...      ...
```

### 按键操作

| 按键 | 功能 |
|------|------|
| **↑↓** | 选择选项 |
| **Enter** | 确认 / 执行 |
| **Esc** | 返回上一级 / 退出 |
| **Ctrl+C** | 静默退出 |

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

保留前缀（不可用于自定义命令）：`help` `url` `version` `u` `c` `install` `ip` `server` `s` `ports` `kill` `download` `tool`

## 更新日志

详见 [更新日志](CHANGELOG.md)

## 技术栈

- Python 3.x
- 纯标准库（零第三方依赖）
- Nuitka 编译打包，单文件分发

## 安装与运行

### 系统要求

- Windows 10 或更高版本
- Python 3.6 或更高版本（源码运行时）

### 运行方法

1. 从 Releases 下载 `nt.exe`
2. 将 `nt.exe` 放入 `C:\Windows\System32\`
3. 在任意终端中直接使用 `nt` 命令

## 反馈

**如有问题或新的创意欢迎和我联系！**

欢迎提交 Issue 和 Pull Request！