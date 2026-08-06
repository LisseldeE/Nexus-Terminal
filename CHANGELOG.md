# 更新日志

## 2026.8.6 R1

### #01
- 新增：基于子命令模式的 CLI 工具（nt <模式> [子参数]）
- 新增：快速隧道 `nt u <port>`（默认 IPv4，支持 -v6 切换 IPv6）
- 新增：完整 URL 隧道 `nt url <url>`
- 新增：自定义命令向导 `nt c` 及列表 `nt c -ls`
- 新增：自定义命令执行 `nt --<前缀>`
- 新增：中英文自动切换（依据系统语言）
- 新增：配置文件 ~/.nexusterminal/config.json
- 新增：PATH 配置脚本 install.ps1
- 新增：nt.py 入口（避免批处理文件 Terminate batch job 问题）
