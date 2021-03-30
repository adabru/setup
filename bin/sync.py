#!/usr/bin/python

import os
import filecmp
import shutil

if os.geteuid() == 0:
    print("Don't run as root. Exiting.")
    exit()


def sync(source, target):
    # symbolic links are not supported on FAT32, check with `os.stat(os.path.dirname(target)).st_uid != 0`
    print("\033[96m{:} \033[39m \033[94m{:}\033[39m : ".format(
        source, target), end="")
    source = os.path.expanduser(source)
    target = os.path.expanduser(target)
    if not os.path.exists(source):
        print("\033[33msource doesn't exist")
    elif os.path.realpath(target) == source:
        print("\033[93m✔")
    elif not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
            return sync(source, target)
        except IOError:
            print("\033[93mdirectory creation failed!")
    elif os.path.islink(target):
        print("\033[33mtarget already links to {:}".format(
            os.path.realpath(target)))
    elif os.path.isdir(source) and os.path.isfile(target):
        print("\033[33msource is a dir but target is a file")
    elif os.path.isfile(source) and os.path.isdir(target):
        print("\033[33msource is a file but target is a dir")
    elif (os.path.exists(target) and (not os.access(target, os.W_OK) or os.stat(os.path.dirname(target)).st_uid == 0)
          and filecmp.cmp(source, target, shallow=False)):
        print("\033[93m(✔)")
    elif os.path.exists(target) and not filecmp.cmp(source, target, shallow=False):
        print("\033[33msource and target differ")
    elif os.path.exists(target):
        print("remove duplicate target and sync again to create a link")
    elif not os.access(os.path.dirname(target), os.W_OK):
        print("sudo copy source to target")
    elif os.stat(os.path.dirname(target)).st_uid == 0:
        shutil.copyfile(source, target)
        print("\033[93m(✔)")
    else:
        os.symlink(source, target)
        print("\033[93m✔")
    print("\033[39m", end="")


# refind
sync("~/setup/refind.conf", "/boot/EFI/refind/refind.conf")
sync("~/setup/os_grub.png", "/boot/EFI/refind/icons/os_grub.png")
sync("~/setup/rorschach.png", "/boot/EFI/refind/rorschach.png")

# keyboard
sync("~/setup/kbd_ab.map", "/usr/share/kbd/keymaps/ab.map")
sync("~/setup/xkb_ab", "/usr/share/X11/xkb/symbols/ab")

# sway
sync("~/setup/sway_config", "~/.config/sway/config")
sync("~/setup/bin/statusbar.py", "~/bin/statusbar.py")
sync("~/setup/bin/statuswindow.py", "~/bin/statuswindow.py")
sync("~/setup/bin/toggle_mic.py", "~/bin/toggle_mic.py")

# autologin
sync("~/setup/getty.conf", "/etc/systemd/system/getty@tty1.service.d/override.conf")

# firewall and doc
sync("~/setup/nftables.conf", "/etc/nftables.conf")

# VS Code config

sync("~/repo/vscode-adabru-markup",
     "~/.vscode-insiders/extensions/vscode-adabru-markup")
sync("~/repo/app/godot/addons/vscode-diff-plugin",
     "~/.vscode-insiders/extensions/vscode-diff-plugin")
sync("~/setup/vscode_keybindings.json",
     "~/.config/Code - Insiders/User/keybindings.json")
sync("~/setup/vscode_settings.json",
     "~/.config/Code - Insiders/User/settings.json")

# terminal + envs
sync("~/setup/termite_config", "~/.config/termite/config")
sync("~/setup/bashrc", "~/.bashrc")
sync("~/setup/trizen.conf", "~/.config/trizen/trizen.conf")
sync("~/setup/vimrc", "~/.vimrc")
sync("~/setup/clingrc", "~/.clingrc")
sync("~/setup/pythonrc", "~/.pythonrc")
sync("~/setup/tmux.conf", "~/.tmux.conf")
sync("~/setup/screenrc", "~/.screenrc")
sync("~/setup/bin/copy.py", "~/bin/copy.py")
sync("~/setup/XCompose", "~/.XCompose")
sync("~/setup/bin/rename.py", "~/bin/rename.py")
sync("~/setup/bin/dates.py", "~/bin/dates.py")

# headset mic boost
sync("~/setup/bin/headset_daemon.py", "~/bin/headset_daemon.py")

# brightness
sync("~/setup/udev_backlight.rules", "/etc/udev/rules.d/backlight.rules")

# hdmi sound
sync("~/setup/udev_hdmi_sound.rules", "/etc/udev/rules.d/hdmi_sound.rules")

# launcher
sync("~/setup/bin/launcher.sh", "~/bin/launcher.sh")
sync("~/setup/albert.conf", "~/.config/albert/albert.conf")
sync("~/setup/user-dirs.dirs", "~/.config/user-dirs.dirs")
sync("~/setup/applications", "~/.local/share/applications/adabru")

# inkscape
sync("~/setup/inkscape.xml", "~/.config/inkscape/keys/default.xml")

# virtual MIDI keyboard
sync("~/setup/vkeybdmap", "~/.vkeybdmap")

# sync
sync("~/setup/bin/sync.py", "~/bin/sync.py")

# youtube
sync("~/setup/bin/yt.py", "~/bin/yt")

# bluetooth
sync("~/setup/bin/bt.py", "~/bin/bt")

# radio stations
sync("~/setup/goodvibes_stations.xml", "~/.local/share/goodvibes/stations.xml")

# packaging
sync("~/setup/makepkg.conf", "~/.makepkg.conf")

# android emulator
sync("~/setup/bin/whatsapp", "~/bin/whatsapp")

# documentation
sync("~/repo/adabru-server/Readme", "~/documentation/Homepage/Server")

# mindcloud
sync("~/repo/app/.godot/script_templates/UIState.gd",
     "~/.config/godot/script_templates/UIState.gd")
sync("~/repo/app/.godot/script_templates/UIElement.gd",
     "~/.config/godot/script_templates/UIElement.gd")
sync("~/repo/app/.godot/editor_settings-3.tres",
     "~/.config/godot/editor_settings-3.tres")

# ftp
sync("~/setup/bin/ftp_here.sh", "~/bin/ftp_here.sh")

# wake up timer
sync("~/setup/bin/wake_me_up.py", "~/bin/wake_me_up.py")

# network
sync("~/setup/NetworkManager.conf", "/etc/NetworkManager/NetworkManager.conf")
sync("~/setup/resolv.conf", "/etc/resolv.conf")

# backup
sync("~/setup/bin/backup.py", "~/bin/backup.py")
sync("~/setup/bin/sqfs-mount.sh", "~/bin/sqfs-mount.sh")
sync("~/setup/sqfs-mount.desktop", "/usr/share/applications/sqfs-mount.desktop")

# work
sync("~/setup/bin/karsoft_workspace.sh", "~/bin/karsoft_workspace.sh")
