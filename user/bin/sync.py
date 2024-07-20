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
    global error
    # symbolic links are not supported on FAT32, check with target.parent.owner() != "root"
    print("\033[96m{:} \033[39m \033[94m{:}\033[39m : ".format(source, target), end="")
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
    sync(source, f"~/bin/{target_name}")


def db_sync(target):
    """
    Sync from ~/db/<target> to ~/<target>.
    """
    sync(f"~/db/{target}", f"~/{target}")


def sync_recursive(source_base, target_base, dir_links=[]):
    for root, dirs, files in os.walk(source_base):
        for name in list(dirs):  # Create a copy of the dirs list
            rel_path: Path = Path(root).relative_to(source_base) / name
            if rel_path.as_posix() in dir_links:
                source = Path(root) / name
                target = target_base / source.relative_to(source_base)
                sync(source, target)
                dirs.remove(name)  # Skip syncing the directory contents
        for name in files:
            source = Path(root) / name
            target = target_base / source.relative_to(source_base)
            sync(source, target)


if command == "setup":

    # sync ~/setup/user/
    sync_recursive(
        Path.home() / "setup" / "user",
        Path.home(),
        dir_links=[".local/share/applications/adabru"],
    )

    # sync ~/setup/root/
    sync_recursive(Path.home() / "setup" / "root", Path("/"))

    # sync ~/db/user/
    sync_recursive(
        Path.home() / "db" / "user",
        Path.home(),
        dir_links=[
            ".ssh",
            ".gnupg",
            ".password-store",
            ".thunderbird",
            "repo/accounting/data",
            "repo/speech/adabru_talon/dictionary",
            "repo/hh-adabru/ads/db",
            "repo/hh-adabru/ads/scrapes",
        ],
    )

    bin_sync("~/repo/hh-adabru/ads/fill_form.py", "ff")
    bin_sync("~/repo/gists/job_search.py")

    # documentation
    sync("~/repo/adabru-server/Readme", "~/documentation/Homepage/Server")

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
