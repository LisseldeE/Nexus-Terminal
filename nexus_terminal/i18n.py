"""Internationalization module - Chinese/English auto-switch based on system language."""

import locale


def detect_language():
    """Detect system language. Returns 'zh' or 'en'."""
    try:
        lang = locale.getdefaultlocale()[0]
        if lang and lang.startswith('zh'):
            return 'zh'
    except Exception:
        pass
    return 'en'


MESSAGES = {
    'zh': {
        'app_name': 'Nexus Terminal',
        'help_title': 'Nexus Terminal - 轻量级命令行工具',
        'help_usage': '用法: nt <模式> [子参数]',
        'help_modes': '模式:',
        'help_u': '  u <port>           快速暴露本地端口 (默认 IPv4)',
        'help_v6': '    -v6              使用 IPv6 ([::1])',
        'help_url': '  url <url>          通过完整 URL 建立 cloudflare 隧道',
        'help_c': '  c                  进入自定义命令向导',
        'help_ls': '    -ls              列出所有自定义命令',
        'help_help': '  help               显示此帮助信息',
        'help_version': '  version            显示版本信息',
        'help_custom': '  --<前缀>           执行自定义命令',
        'port_missing': '错误: 缺少端口号，用法: nt u [-v4|-v6] <port>',
        'port_invalid': '错误: 端口号无效，请输入 1-65535 之间的数字',
        'url_missing': '错误: 缺少 URL，用法: nt url <url>',
        'unknown_mode': '错误: 未知模式 "{}"，使用 nt help 查看可用模式',
        'unknown_arg': '错误: 未知参数 "{}"',
        'cloudflared_not_found': '错误: 未找到 cloudflared，请先安装。',
        'cloudflared_hint': '提示: 可从以下地址下载:',
        'cloudflared_url': '  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/',
        'cloudflared_path_hint': '提示: 或在配置文件中设置 cloudflared_path 指向可执行文件路径',
        'tunnel_starting': '正在启动 cloudflare 隧道...',
        'tunnel_stopped': '\n隧道已停止。',
        'wizard_prefix_prompt': '请输入自定义前缀: ',
        'wizard_prefix_empty': '错误: 前缀不能为空',
        'wizard_prefix_invalid': '错误: 前缀只能包含字母、数字和连字符',
        'wizard_prefix_reserved': '错误: 前缀 "{}" 是保留字，请使用其他名称',
        'wizard_prefix_exists': '错误: 前缀 "{}" 已存在',
        'wizard_command_prompt': '请输入要映射的命令: ',
        'wizard_command_empty': '错误: 命令不能为空',
        'wizard_desc_prompt': '请输入描述 (可选，留空跳过): ',
        'wizard_added': '已添加自定义命令: --{}',
        'wizard_list_header': '自定义命令列表:',
        'wizard_list_empty': '暂无自定义命令',
        'custom_not_found': '错误: 未找到自定义命令 "--{}"',
        'custom_executing': '正在执行: {}',
        'custom_interrupted': '\n命令已中断。',
        'config_created': '已创建配置文件: {}',
        'config_error': '错误: 无法读取配置文件: {}',
        'version_info': 'Nexus Terminal v{}',
    },
    'en': {
        'app_name': 'Nexus Terminal',
        'help_title': 'Nexus Terminal - Lightweight CLI Tool',
        'help_usage': 'Usage: nt <mode> [sub-args]',
        'help_modes': 'Modes:',
        'help_u': '  u <port>           Quick tunnel for local port (default: IPv4)',
        'help_v6': '    -v6              Use IPv6 ([::1])',
        'help_url': '  url <url>          Create a tunnel via full URL',
        'help_c': '  c                  Enter custom command wizard',
        'help_ls': '    -ls              List all custom commands',
        'help_help': '  help               Show this help message',
        'help_version': '  version            Show version information',
        'help_custom': '  --<prefix>         Execute a custom command',
        'port_missing': 'Error: missing port, usage: nt u [-v4|-v6] <port>',
        'port_invalid': 'Error: invalid port, enter a number between 1-65535',
        'url_missing': 'Error: missing URL, usage: nt url <url>',
        'unknown_mode': 'Error: unknown mode "{}", use nt help to see available modes',
        'unknown_arg': 'Error: unknown argument "{}"',
        'cloudflared_not_found': 'Error: cloudflared not found. Please install it first.',
        'cloudflared_hint': 'Hint: Download from:',
        'cloudflared_url': '  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/',
        'cloudflared_path_hint': 'Hint: Or set cloudflared_path in config file to point to the executable',
        'tunnel_starting': 'Starting cloudflare tunnel...',
        'tunnel_stopped': '\nTunnel stopped.',
        'wizard_prefix_prompt': 'Enter custom prefix: ',
        'wizard_prefix_empty': 'Error: prefix cannot be empty',
        'wizard_prefix_invalid': 'Error: prefix can only contain letters, numbers and hyphens',
        'wizard_prefix_reserved': 'Error: prefix "{}" is reserved, please use another name',
        'wizard_prefix_exists': 'Error: prefix "{}" already exists',
        'wizard_command_prompt': 'Enter command to map: ',
        'wizard_command_empty': 'Error: command cannot be empty',
        'wizard_desc_prompt': 'Enter description (optional, leave empty to skip): ',
        'wizard_added': 'Added custom command: --{}',
        'wizard_list_header': 'Custom commands:',
        'wizard_list_empty': 'No custom commands defined',
        'custom_not_found': 'Error: custom command "--{}" not found',
        'custom_executing': 'Executing: {}',
        'custom_interrupted': '\nCommand interrupted.',
        'config_created': 'Created config file: {}',
        'config_error': 'Error: failed to read config file: {}',
        'version_info': 'Nexus Terminal v{}',
    },
}


def get_messages():
    """Return messages dict for the detected system language."""
    return MESSAGES[detect_language()]
