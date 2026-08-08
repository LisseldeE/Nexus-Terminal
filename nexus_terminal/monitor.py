"""Process monitor — real-time CPU, memory, network I/O monitoring by port.

Uses Windows API (ctypes) for zero-dependency process introspection.
"""

import ctypes
import ctypes.wintypes
import os
import subprocess
import sys
import time

from .ports import get_listening_ports, get_process_name

# ── Windows API constants ──────────────────────────────────────────────
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

# ── ctypes structures ──────────────────────────────────────────────────


class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", ctypes.wintypes.DWORD),
        ("dwHighDateTime", ctypes.wintypes.DWORD),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.wintypes.DWORD),
        ("PageFaultCount", ctypes.wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.wintypes.DWORD),
        ("dwMemoryLoad", ctypes.wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


# ── Windows API DLLs ──────────────────────────────────────────────────

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

kernel32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
kernel32.OpenProcess.restype = ctypes.wintypes.HANDLE
kernel32.CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
kernel32.CloseHandle.restype = ctypes.wintypes.BOOL
kernel32.GetProcessTimes.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME)]
kernel32.GetProcessTimes.restype = ctypes.wintypes.BOOL
kernel32.GetProcessIoCounters.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(IO_COUNTERS)]
kernel32.GetProcessIoCounters.restype = ctypes.wintypes.BOOL
kernel32.GetExitCodeProcess.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.DWORD)]
kernel32.GetExitCodeProcess.restype = ctypes.wintypes.BOOL
kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
kernel32.GlobalMemoryStatusEx.restype = ctypes.wintypes.BOOL

psapi.GetProcessMemoryInfo.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), ctypes.wintypes.DWORD]
psapi.GetProcessMemoryInfo.restype = ctypes.wintypes.BOOL

STILL_ACTIVE = 259

# ── Toolhelp32 constants ──────────────────────────────────────────────
TH32CS_SNAPTHREAD = 0x00000004


class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.wintypes.DWORD),
        ("cntUsage", ctypes.wintypes.DWORD),
        ("th32ThreadID", ctypes.wintypes.DWORD),
        ("th32OwnerProcessID", ctypes.wintypes.DWORD),
        ("tpBasePri", ctypes.wintypes.LONG),
        ("tpDeltaPri", ctypes.wintypes.LONG),
        ("dwFlags", ctypes.wintypes.DWORD),
    ]


def _filetime_to_us(ft):
    """Convert FILETIME (100-ns intervals) to microseconds."""
    return (ft.dwHighDateTime << 32 | ft.dwLowDateTime) // 10


def _format_size(bytes_val):
    """Format bytes to human-readable string (KB/MB)."""
    if bytes_val < 1024:
        return f'{bytes_val} B'
    elif bytes_val < 1024 * 1024:
        return f'{bytes_val / 1024:.1f} KB'
    else:
        return f'{bytes_val / (1024 * 1024):.1f} MB'


def _format_speed(bytes_per_sec):
    """Format bytes/sec to human-readable speed string."""
    if bytes_per_sec < 1024:
        return f'{bytes_per_sec:.1f} B/s'
    elif bytes_per_sec < 1024 * 1024:
        return f'{bytes_per_sec / 1024:.1f} KB/s'
    else:
        return f'{bytes_per_sec / (1024 * 1024):.1f} MB/s'


def _find_pid_by_port(port):
    """Find the PID of the process listening on the given port."""
    ports = get_listening_ports()
    for p in ports:
        if p['port'] == port:
            return p['pid']
    return None


def _get_connection_count(pid):
    """Count TCP connections for a given PID using netstat."""
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True, text=True, timeout=5
        )
        count = 0
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[-1].isdigit() and int(parts[-1]) == pid:
                # Only count established TCP connections
                if 'ESTABLISHED' in line.upper():
                    count += 1
        return count
    except Exception:
        return 0


def _get_process_info(pid):
    """Get process info snapshot: CPU time, memory, IO counters.

    Returns a dict or None if the process is not accessible.
    """
    handle = kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid
    )
    if not handle:
        return None

    try:
        # Check if process is still alive
        exit_code = ctypes.wintypes.DWORD(0)
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return None
        if exit_code.value != STILL_ACTIVE:
            return None

        # CPU times
        create = FILETIME()
        exit_ft = FILETIME()
        kernel_ft = FILETIME()
        user_ft = FILETIME()
        if not kernel32.GetProcessTimes(handle, ctypes.byref(create), ctypes.byref(exit_ft),
                                         ctypes.byref(kernel_ft), ctypes.byref(user_ft)):
            return None
        kernel_us = _filetime_to_us(kernel_ft)
        user_us = _filetime_to_us(user_ft)

        # Memory
        pmc = PROCESS_MEMORY_COUNTERS()
        pmc.cb = ctypes.sizeof(pmc)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), ctypes.sizeof(pmc)):
            return None

        # IO counters
        io = IO_COUNTERS()
        if not kernel32.GetProcessIoCounters(handle, ctypes.byref(io)):
            return None

        return {
            'kernel_us': kernel_us,
            'user_us': user_us,
            'memory_bytes': pmc.WorkingSetSize,
            'io_read_bytes': io.ReadTransferCount,
            'io_write_bytes': io.WriteTransferCount,
        }
    finally:
        kernel32.CloseHandle(handle)


def _get_thread_count(pid):
    """Get thread count using CreateToolhelp32Snapshot."""
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snapshot == -1:
        return 0

    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(te)

    if not kernel32.Thread32First(snapshot, ctypes.byref(te)):
        kernel32.CloseHandle(snapshot)
        return 0

    count = 0
    while True:
        if te.th32OwnerProcessID == pid:
            count += 1
        if not kernel32.Thread32Next(snapshot, ctypes.byref(te)):
            break

    kernel32.CloseHandle(snapshot)
    return count


def _get_handle_count(pid):
    """Get handle count using GetProcessHandleCount from kernel32."""
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
    if not handle:
        return 0
    try:
        count = ctypes.wintypes.DWORD(0)
        if kernel32.GetProcessHandleCount(handle, ctypes.byref(count)):
            return count.value
        return 0
    finally:
        kernel32.CloseHandle(handle)


def _get_thread_handle_count(pid):
    """Wrapper returning (thread_count, handle_count) tuple."""
    return _get_thread_count(pid), _get_handle_count(pid)


def _get_total_physical_memory():
    """Get total physical memory in bytes. Returns 0 on failure."""
    ms = MEMORYSTATUSEX()
    ms.dwLength = ctypes.sizeof(ms)
    if kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
        return ms.ullTotalPhys
    return 0


def monitor_process(port, messages):
    """Real-time monitor of a process by port.

    Shows CPU%, memory, network I/O, thread count, and connection count.
    Updates every 1 second. Press Ctrl+C to stop.

    Args:
        port: Port number to monitor.
        messages: i18n messages dict.

    Returns:
        Exit code (0).
    """
    # Find PID by port
    pid = _find_pid_by_port(port)
    if pid is None:
        print(messages['monitor_port_not_found'].format(port=port))
        return 1

    proc_name = get_process_name(pid)

    # Get initial snapshot
    info = _get_process_info(pid)
    if info is None:
        print(messages['monitor_process_not_found'].format(pid=pid))
        return 1

    # Number of logical CPUs for CPU% calculation
    try:
        num_cpus = os.cpu_count() or 1
    except Exception:
        num_cpus = 1

    # Total physical memory (static, used for memory %)
    total_memory = _get_total_physical_memory()

    # Polling loop
    prev_info = info
    prev_time = time.time()
    prev_connections = _get_connection_count(pid)
    running = True
    first_frame = True

    # Lines of output (fixed): header + sep + 6 data + sep + footer
    total_lines = 10

    while running:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            running = False
            break

        current_time = time.time()
        elapsed = current_time - prev_time

        info = _get_process_info(pid)
        if info is None:
            # Process exited
            sys.stdout.write('\033[J')
            print(messages['monitor_process_exited'].format(
                name=proc_name, pid=pid
            ))
            break

        connections = _get_connection_count(pid)
        threads, handles = _get_thread_handle_count(pid)

        # Calculate CPU%
        cpu_delta_us = (info['kernel_us'] - prev_info['kernel_us']) + \
                       (info['user_us'] - prev_info['user_us'])
        cpu_percent = cpu_delta_us / (elapsed * 1000000 * num_cpus) * 100
        cpu_percent = min(max(cpu_percent, 0), 100)  # clamp

        # Calculate network speeds
        read_speed = (info['io_read_bytes'] - prev_info['io_read_bytes']) / elapsed
        write_speed = (info['io_write_bytes'] - prev_info['io_write_bytes']) / elapsed

        # Memory
        mem_str = _format_size(info['memory_bytes'])
        mem_percent = info['memory_bytes'] / total_memory * 100 if total_memory else 0

        # Build display
        lines = [
            messages['monitor_header'].format(name=proc_name, pid=pid, port=port),
            messages['monitor_separator'],
            messages['monitor_cpu'].format(percent=cpu_percent),
            messages['monitor_memory'].format(mem=mem_str, percent=mem_percent),
            messages['monitor_network'].format(
                down=_format_speed(read_speed), up=_format_speed(write_speed)
            ),
            messages['monitor_threads'].format(n=threads),
            messages['monitor_handles'].format(n=handles),
            messages['monitor_connections'].format(n=connections),
            messages['monitor_separator'],
            messages['monitor_footer'],
        ]

        # Redraw: first frame just prints, subsequent frames overwrite in place
        if not first_frame:
            sys.stdout.write(f'\033[{total_lines}A\r')  # move cursor up to start
            sys.stdout.write('\033[J')                   # clear from cursor to end
        first_frame = False

        for line in lines:
            sys.stdout.write(line + '\n')
        sys.stdout.flush()

        prev_info = info
        prev_time = current_time
        prev_connections = connections

    # On exit: clear the display area if anything was drawn
    if not first_frame:
        sys.stdout.write(f'\033[{total_lines}A\r')
        sys.stdout.write('\033[J')
        sys.stdout.flush()
    return 0


def monitor_interactive(messages):
    """Interactive port selection for monitoring, then start monitoring.

    Shows a list of listening ports and lets the user choose one.
    """
    ports = get_listening_ports()
    if not ports:
        print(messages['monitor_no_ports'])
        return 1

    from nexus_terminal.interactive import select_option, InteractiveExit, HAS_MSVCRT

    if not HAS_MSVCRT:
        print(messages['monitor_usage'])
        return 1

    options = []
    for p in ports:
        proc_name = get_process_name(p['pid'])
        label = f'{p["port"]}  {proc_name}  PID {p["pid"]}'
        options.append((str(p['port']), label))

    try:
        # Inject a title option
        options_with_header = options
        choice = select_option(
            messages['monitor_select_port'],
            messages['interactive_hint'],
            options_with_header,
            messages,
        )
        if choice is None:
            return 0
        port = int(choice)
    except InteractiveExit:
        return 0
    except (ValueError, TypeError):
        return 0

    return monitor_process(port, messages)