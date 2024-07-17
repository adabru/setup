#!/usr/bin/python

import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

if os.geteuid() == 0:
    print("Don't run as root. Exiting.")
    exit()

if len(sys.argv) > 2 or len(sys.argv) == 2 and not sys.argv[1] in {"audio", "setup"}:
    print("usage:\n\n  sync.py [setup] | audio")
    exit()

command = "setup"
if len(sys.argv) == 2:
    command = sys.argv[1]

error = 0


def is_git(path):
    return subprocess.run(["git", "rev-parse"], cwd=path.parent).returncode == 0


def sync(source, target):
    return
    global error
    # symbolic links are not supported on FAT32, check with target.parent.owner() != "root"
    # print("\033[96m{:} \033[39m \033[94m{:}\033[39m : ".format(source, target), end="")
    source = Path(source).expanduser()
    target = Path(target).expanduser()
    if not source.exists():
        print("\033[33msource doesn't exist")
        error = 1
    elif target.resolve() == source:
        print("\033[92m✔")
    elif not target.parent.exists():
        try:
            target.parent.mkdir(parents=True)
            return sync(source, target)
        except IOError:
            print("\033[93mdirectory creation failed!")
            error = 2
    elif target.is_symlink():
        print("\033[33mtarget already links to {:}".format(target.resolve()))
        error = 3
    elif source.is_dir() and target.is_file():
        print("\033[33msource is a dir but target is a file")
        error = 4
    elif source.is_file() and target.is_dir():
        print("\033[33msource is a file but target is a dir")
        error = 5
    elif (
        target.exists()
        and (not os.access(target, os.W_OK) or target.parent.owner() == "root")
        and filecmp.cmp(source, target, shallow=False)
    ):
        print("\033[92m(✔)")
    elif target.exists() and not filecmp.cmp(source, target, shallow=False):
        print("\033[93msource and target differ")
        error = 6
    elif target.exists() and is_git(target):
        print("duplicate target")
    elif target.exists():
        print("remove duplicate target and sync again to create a link")
        error = 7
    elif not os.access(target.parent, os.W_OK):
        print("\033[93msudo copy source to target")
        error = 8
    elif target.parent.owner() == "root":
        shutil.copyfile(source, target)
        print("\033[92m(✔)")
    # file used in multiple repositories
    # commented for now because gitignored data should be symlinked
    # elif is_git(target) :
    #     shutil.copyfile(source, target)
    #     print("\033[92m(✔)")
    else:
        target.symlink_to(source)
        print("\033[92m✔")
    print("\033[39m", end="")


def exec(cmd):
    # echo command for debugging
    print("\033[90m%s\033[0m" % cmd)
    return 0 == subprocess.call(["sh", "-c", cmd])


def bin_sync(source, target_name=""):
    """
    Sync from <source> to ~/bin/<source|target_name>
    """
    if target_name == "":
        target_name = Path(source).name
    user_sync(source, f"~/bin/{target_name}")


def db_sync(target):
    """
    Sync from ~/db/<target> to ~/<target>.
    """
    sync(f"~/db/{target}", f"~/{target}")


def user_sync(source, target):
    """
    Sync from ~/setup/user/<target> to ~/<target>.
    """
    # sync(f"~/setup/user/{target}", f"~/{target}")
    source = Path(source).expanduser()
    target = Path(target).expanduser()
    # create target folder in ~/setup/user or ~/setup/root
    if target.parts[1] == "home" and target.parts[2] == "adabru":
        relTarget = Path.home() / "setup/user" / target.relative_to(Path.home())
        # print(relTarget.parent)
        # create ~/setup/user/<relParent>
        # os.makedirs(relTarget.parent, exist_ok=True)
        # move source to relTarget
        # shutil.move(source, relTarget)
        # print(source)
    elif target.parts[1] != "home":
        relTarget = Path.home() / "setup/root" / target.relative_to(Path("/"))
        os.makedirs(relTarget.parent, exist_ok=True)
        if source.exists():
            shutil.move(source, relTarget)
    return


def root_sync(target):
    """
    Sync from ~/setup/root/<target> to /<target>.
    """
    sync(f"~/setup/root/{target}", f"/{target}")


if command == "setup":

    # keyboard
    user_sync("~/setup/kbd_ab.map", "/usr/share/kbd/keymaps/ab.map")
    user_sync("~/setup/vconsole.conf", "/etc/vconsole.conf")
    user_sync("~/setup/xkb_ab", "/usr/share/X11/xkb/symbols/ab")

    # window manager
    user_sync("~/setup/sway_config", "~/.config/sway/config")
    bin_sync("~/setup/bin/statusbar.py")
    bin_sync("~/setup/bin/statuswindow.py")
    bin_sync("~/setup/bin/toggle_mic.py")

    # terminal
    user_sync("~/setup/alacritty.toml", "~/.config/alacritty/alacritty.toml")
    user_sync("~/setup/bashrc", "~/.bashrc")
    db_sync(".bash_history")
    user_sync("~/setup/vimrc", "~/.vimrc")
    user_sync("~/setup/clingrc", "~/.clingrc")
    user_sync("~/setup/pythonrc", "~/.pythonrc")
    user_sync("~/setup/tmux.conf", "~/.tmux.conf")
    user_sync("~/setup/screenrc", "~/.screenrc")
    user_sync("~/setup/XCompose", "~/.XCompose")
    bin_sync("~/setup/bin/rename.py")
    bin_sync("~/setup/bin/dates.py")
    # bin_sync("~/repo/hh-adabru/ads/fill_form.py", "ff")
    user_sync("~/setup/pacman.conf", "/etc/pacman.conf")

    # automount usb
    user_sync(
        "~/setup/services/adabru.udiskie.service",
        "/etc/systemd/user/adabru.udiskie.service",
    )

    # headset mic boost
    bin_sync("~/setup/bin/headset_daemon.py")
    user_sync(
        "~/setup/services/adabru.headset.service",
        "/etc/systemd/user/adabru.headset.service",
    )

    # brightness
    user_sync("~/setup/udev_backlight.rules", "/etc/udev/rules.d/backlight.rules")

    # hdmi sound
    user_sync("~/setup/udev_hdmi_sound.rules", "/etc/udev/rules.d/hdmi_sound.rules")

    # no beep
    user_sync("~/setup/udev_no_beep.conf", "/etc/modprobe.d/udev_no_beep.conf")

    # gammastep / redshift
    user_sync("~/setup/gammastep_config.ini", "~/.config/gammastep/config.ini")

    # launcher
    user_sync("~/setup/user-dirs.dirs", "~/.config/user-dirs.dirs")
    user_sync("~/setup/applications", "~/.local/share/applications/adabru")
    user_sync("~/setup/synapse_config.json", "~/.config/synapse/config.json")

    # inkscape
    user_sync("~/setup/inkscape.xml", "~/.config/inkscape/keys/default.xml")

    # sync
    bin_sync("~/setup/bin/sync.py")

    # youtube
    bin_sync("~/setup/bin/yt.py")

    # bluetooth
    bin_sync("~/setup/bin/bt.py")

    # packaging
    user_sync("~/setup/makepkg.conf", "~/.makepkg.conf")

    # documentation
    sync("~/repo/adabru-server/Readme", "~/documentation/Homepage/Server")

    # ftp
    bin_sync("~/setup/bin/ftp_here.sh")

    # network
    user_sync("~/setup/NetworkManager.conf", "/etc/NetworkManager/NetworkManager.conf")
    user_sync("~/setup/resolv.conf", "/etc/resolv.conf")

    # backup
    bin_sync("~/setup/bin/backup.py")

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
    bin_sync("~/setup/bin/type_pass.py")

    # gitconfig
    user_sync("~/setup/gitconfig", "~/.gitconfig")

    # keys and logins
    db_sync(".ssh")
    db_sync(".gnupg")
    db_sync(".password-store")

    # mail
    db_sync(".thunderbird")

    # ip6 tunnel
    db_sync("bin/tunnel_ipv6.sh")

    # project keys + data + config
    db_sync("repo/accounting/data")
    db_sync("repo/language-trainer/data/profile.json")
    db_sync("repo/server-apps/.env")
    db_sync("repo/server-apps/telegram/private-key.json")
    db_sync("repo/speech/adabru_talon/dictionary")
    db_sync("repo/hh-adabru/ads/db")
    db_sync("repo/hh-adabru/ads/scrapes")

elif command == "audio":
    ip = "192.168.178.89"
    user = "user"
    # exec(
    #     f'rsync -vh --size-only --progress --update --inplace --recursive --delete --exclude=".*" --no-perms -e "ssh -i ~/.ssh/id_phone -p 8022" {home}/audio/ {user}@{ip}:/sdcard/Music/'
    # )
    if exec(
        f"sshfs -o rw,nosuid,nodev,identityfile={home}/.ssh/id_phone,port=8022,HostKeyAlgorithms=+ssh-rsa,PubkeyAcceptedKeyTypes=+ssh-rsa {user}@{ip}:/ {home}/mnt"
    ):
        exec(
            f'rsync -vh --size-only --progress --update --inplace --recursive --delete --exclude=".*" --no-perms -e "ssh -i ~/.ssh/id_phone -p 8022" {home}/audio/ {home}/mnt/Music'
        )
    # # see https://rafaelc.org/posts/mounting-kde-connect-filesystem-via-cli/
    # exec(
    #     f"sshfs -o rw,nosuid,nodev,identityfile={home}/.config/kdeconnect/privateKey.pem,port=1740,HostKeyAlgorithms=+ssh-rsa,PubkeyAcceptedKeyTypes=+ssh-rsa kdeconnect@{ip}:/ {home}/mnt"
    # )
    # exec(
    #     f'rsync -avh --progress --update --delete --exclude=".*" {home}/audio/ {home}/mnt/Music/'
    # )
