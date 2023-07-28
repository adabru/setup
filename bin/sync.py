#!/usr/bin/python

import os, filecmp, shutil, subprocess
from pathlib import Path
import sys

if os.geteuid() == 0:
    print("Don't run as root. Exiting.")
    exit()

if len(sys.argv) > 2 or len(sys.argv) == 2 and not sys.argv[1] in {"audio", "setup"}:
    print("usage:\n\n  sync.py [setup] | audio")
    exit()

command = "setup"
if len(sys.argv) == 2:
    command = sys.argv[1]


def is_git(path):
    return subprocess.run(["git", "rev-parse"], cwd=path.parent).returncode == 0


def sync(source, target):
    # symbolic links are not supported on FAT32, check with target.parent.owner() != "root"
    print("\033[96m{:} \033[39m \033[94m{:}\033[39m : ".format(source, target), end="")
    source = Path(source).expanduser()
    target = Path(target).expanduser()
    if not source.exists():
        print("\033[33msource doesn't exist")
    elif target.resolve() == source:
        print("\033[92m✔")
    elif not target.parent.exists():
        try:
            target.parent.mkdir(parents=True)
            return sync(source, target)
        except IOError:
            print("\033[93mdirectory creation failed!")
    elif target.is_symlink():
        print("\033[33mtarget already links to {:}".format(target.resolve()))
    elif source.is_dir() and target.is_file():
        print("\033[33msource is a dir but target is a file")
    elif source.is_file() and target.is_dir():
        print("\033[33msource is a file but target is a dir")
    elif (
        target.exists()
        and (not os.access(target, os.W_OK) or target.parent.owner() == "root")
        and filecmp.cmp(source, target, shallow=False)
    ):
        print("\033[92m(✔)")
    elif target.exists() and not filecmp.cmp(source, target, shallow=False):
        print("\033[93msource and target differ")
    elif target.exists() and is_git(target):
        print("duplicate target")
    elif target.exists():
        print("remove duplicate target and sync again to create a link")
    elif not os.access(target.parent, os.W_OK):
        print("\033[93msudo copy source to target")
    elif target.parent.owner() == "root":
        shutil.copyfile(source, target)
        print("\033[92m(✔)")
    elif is_git(target):
        shutil.copyfile(source, target)
        print("\033[92m(✔)")
    else:
        target.symlink_to(source)
        print("\033[92m✔")
    print("\033[39m", end="")


def exec(cmd, **kwargs):
    # echo command for debugging
    print("\033[90m%s\033[0m" % cmd)
    if type(cmd) == str:
        cmd = cmd.split()
    return 0 == subprocess.call(cmd, **kwargs)


if command == "setup":
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

    # automount
    sync(
        "~/setup/services/adabru.udiskie.service",
        "/etc/systemd/user/adabru.udiskie.service",
    )

    # firewall and doc
    sync("~/setup/nftables.conf", "/etc/nftables.conf")

    # VS Code config

    sync(
        "~/repo/vscode-adabru-markup",
        "~/.vscode-insiders/extensions/vscode-adabru-markup",
    )
    sync(
        "~/repo/app/godot/addons/vscode-diff-plugin",
        "~/.vscode-insiders/extensions/vscode-diff-plugin",
    )
    sync(
        "~/setup/vscode/keybindings.json",
        "~/.config/Code - Insiders/User/keybindings.json",
    )
    sync("~/setup/vscode/settings.json", "~/.config/Code - Insiders/User/settings.json")
    sync("~/setup/vscode/snippets", "~/.config/Code - Insiders/User/snippets")

    # terminal + envs
    sync("~/setup/alacritty.yml", "~/.config/alacritty/alacritty.yml")
    sync("~/setup/bashrc", "~/.bashrc")
    sync("~/setup/trizen.conf", "~/.config/trizen/trizen.conf")
    sync("~/setup/vimrc", "~/.vimrc")
    sync("~/setup/clingrc", "~/.clingrc")
    sync("~/setup/pythonrc", "~/.pythonrc")
    sync("~/setup/tmux.conf", "~/.tmux.conf")
    sync("~/setup/screenrc", "~/.screenrc")
    sync("~/setup/XCompose", "~/.XCompose")
    sync("~/setup/bin/rename.py", "~/bin/rename.py")
    sync("~/setup/bin/dates.py", "~/bin/dates.py")

    # headset mic boost
    sync("~/setup/bin/headset_daemon.py", "~/bin/headset_daemon.py")
    sync(
        "~/setup/services/adabru.headset.service",
        "/etc/systemd/user/adabru.headset.service",
    )

    # brightness
    sync("~/setup/udev_backlight.rules", "/etc/udev/rules.d/backlight.rules")

    # hdmi sound
    sync("~/setup/udev_hdmi_sound.rules", "/etc/udev/rules.d/hdmi_sound.rules")

    # no beep
    sync("~/setup/udev_no_beep.conf", "/etc/modprobe.d/udev_no_beep.conf")

    # clipboard manager
    sync(
        "~/setup/services/adabru.copyq.service",
        "/etc/systemd/user/adabru.copyq.service",
    )

    # launcher
    sync(
        "~/setup/services/adabru.albert.service",
        "/etc/systemd/user/adabru.albert.service",
    )
    sync("~/setup/albert.conf", "~/.config/albert.conf")
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

    # eye tracking + speech
    sync(
        "~/repo/speech/service/speech.eyeput.service",
        "/etc/systemd/user/speech.eyeput.service",
    )
    sync("~/repo/speech/cursor/AdabruCursors", "~/.icons/AdabruCursors")
    sync("~/repo/speech/parrot_patterns.json", "~/.talon/parrot/patterns.json")
    sync("~/repo/speech/adabru_talon", "~/.talon/user/adabru")
    sync(
        "~/repo/speech/adabru_talon/cursorless-settings",
        "~/.talon/user/cursorless-settings",
    )
    sync("~/repo/gists/unix_socket.py", "~/repo/eyeput/unix_socket.py")
    sync(
        "~/repo/gists/unix_socket.py", "~/repo/speech/adabru_talon/code/unix_socket.py"
    )
    sync("~/repo/gists/unix_socket.py", "~/repo/speech/run/unix_socket.py")
    sync(
        "~/repo/eyeput/session_bus.py",
        "~/repo/speech/adabru_talon/apps/eyeput/session_bus.py",
    )
    sync(
        "~/repo/eyeput/shared_tags.py",
        "~/repo/speech/adabru_talon/apps/eyeput/shared_tags.py",
    )

    # authentication
    sync("~/setup/bin/authentication.py", "~/bin/authentication.py")

elif command == "audio":
    ip = "192.168.178.78"
    home = Path.home()
    # see https://rafaelc.org/posts/mounting-kde-connect-filesystem-via-cli/
    exec(
        f"sshfs -o rw,nosuid,nodev,identityfile={home}/.config/kdeconnect/privateKey.pem,port=1740,HostKeyAlgorithms=+ssh-rsa,PubkeyAcceptedKeyTypes=+ssh-rsa kdeconnect@{ip}:/ {home}/mnt"
    )
    exec(
        f'rsync -avh --progress --update --delete --exclude=".*" {home}/audio/ {home}/mnt/Music/'
    )
