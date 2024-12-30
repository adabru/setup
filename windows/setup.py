import ctypes
import sys
import winreg as reg
from pathlib import Path


def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def set_desktop_wallpaper(image_path: Path):
    print("Setting desktop wallpaper...", end=" ")
    SPI_SETDESKWALLPAPER = 20
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, str(image_path), 3
    )
    if not result:
        raise ctypes.WinError()
    print("✔")


def set_lock_screen_image(image_path: Path):
    print("Setting lock screen image...", end=" ")
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP"
    try:
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path, 0, reg.KEY_SET_VALUE)
    except FileNotFoundError:
        key = reg.CreateKey(reg.HKEY_LOCAL_MACHINE, key_path)
    with key:
        reg.SetValueEx(key, "LockScreenImagePath", 0, reg.REG_SZ, str(image_path))
        reg.SetValueEx(key, "LockScreenImageStatus", 0, reg.REG_DWORD, 1)
    print("✔")


def enable_developer_mode():
    print("Enabling Developer Mode...", end=" ")
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path, 0, reg.KEY_SET_VALUE) as key:
        reg.SetValueEx(key, "AllowDevelopmentWithoutDevLicense", 0, reg.REG_DWORD, 1)
    print("✔")


def set_powershell_execution_policy(policy="RemoteSigned"):
    print(
        f"Setting PowerShell Execution Policy to '{policy}' via the registry...",
        end=" ",
    )
    key_path = r"SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell"
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path, 0, reg.KEY_SET_VALUE) as key:
        reg.SetValueEx(key, "ExecutionPolicy", 0, reg.REG_SZ, policy)
    print("✔")


if __name__ == "__main__":
    desktop_image = Path.home() / "Documents/git/setup/wallpapers/LVDS-1/_default.png"
    lock_screen_image = (
        Path.home() / "Documents/git/setup/wallpapers/LVDS-1/_default.png"
    )

    # Editing HKLM registry requires admin privileges
    if not is_admin():
        print("Attempting to restart with admin privileges.")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

    try:
        enable_developer_mode()
        set_powershell_execution_policy()
        set_desktop_wallpaper(desktop_image)
        set_lock_screen_image(lock_screen_image)
    finally:
        input("Press Enter to exit...")
