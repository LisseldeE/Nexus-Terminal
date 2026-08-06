# 更新日志

## 2026.8.6 R1

### #01
- 新增：基于子命令模式的 CLI 工具（nt <模式> [子参数]）
- 新增：快速隧道 `nt u <port>`（默认 IPv4，支持 -v6 切换 IPv6）
- 新增：完整 URL 隧道 `nt url <url>`
- 新增：自定义命令向导 `nt c` 及列表 `nt c -ls`
- 新增：自定义命令执行 `nt --<前缀>`
- 新增：中英文自动切换（依据系统语言）
- 新增：删除自定义命令 `nt c -rm <prefix>`
- 新增：手动安装 cloudflared `nt install cf`（或 `nt install u`）
- 新增：`nt u` / `nt url` 缺少 cloudflared 时自动询问下载，从 Gitee 拉取并安装到 System32（含 UAC 提权）
- 新增：显示本机 IP 地址 `nt ip`（IPv4 + IPv6，标注主网络/本地链路）
- 新增：启动 HTTP 文件服务器 `nt server <port>`（简写 `nt s`，支持 `-http` 显式指定）
- 新增：列出监听端口 `nt ports`（含进程名、PID）
- 优化：`nt u` 默认改为 IPv4 (127.0.0.1)，避免 localhost 解析到 IPv6
- 优化：自定义命令调用不再需要 `--` 前缀，直接 `nt <前缀>` 即可（`nt --<前缀>` 仍兼容）
- 优化：自定义命令匹配改为大小写不敏感
