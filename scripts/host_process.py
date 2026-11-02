"""Windows process ownership: creation time prevents killing a reused PID."""

import ctypes
from ctypes import wintypes
import os
import subprocess


def identity(pid: int) -> str | None:
    if os.name != "nt":
        raise RuntimeError(
            "Detached host mode currently supports Windows only; Docker mode is portable."
        )
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME),
    ]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        created, exited, system, user = (wintypes.FILETIME() for _ in range(4))
        if not kernel.GetProcessTimes(
            handle,
            ctypes.byref(created),
            ctypes.byref(exited),
            ctypes.byref(system),
            ctypes.byref(user),
        ):
            return None
        return str((created.dwHighDateTime << 32) | created.dwLowDateTime)
    finally:
        kernel.CloseHandle(handle)


def stop_owned(record: dict) -> None:
    if identity(record["pid"]) != record["creationTime"]:
        print(
            f"Stale PID record {record['pid']}; no unrelated process will be stopped."
        )
        return
    subprocess.run(
        ["taskkill.exe", "/PID", str(record["pid"]), "/T", "/F"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
