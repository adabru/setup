#!/usr/bin/python

import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Type


def is_privileged():
    if sys.platform == "linux":
        return os.geteuid() == 0
    elif sys.platform == "win32":
        import ctypes

        return ctypes.windll.shell32.IsUserAnAdmin() != 0


if is_privileged():
    print("Don't run as root. Exiting.")
    exit()

if (
    len(sys.argv) > 2
    or len(sys.argv) == 2
    and not sys.argv[1] in {"audio", "run", "interactive"}
):
    print("usage:\n\n  sync.py [run] | interacive | audio")
    exit()

command = "run"
if len(sys.argv) == 2:
    command = sys.argv[1]

error = 0
interactive: bool = False


def is_git_tracked(path):
    # Check if the path is in a Git repository
    in_git_repo = (
        subprocess.run(
            ["git", "rev-parse"],
            cwd=path.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )

    # If the path is in a Git repository, check if it's ignored
    if in_git_repo:
        is_ignored = (
            subprocess.run(
                ["git", "check-ignore", str(path)],
                cwd=path.parent,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
        return not is_ignored

    return False


def rm(path):
    if path.parent.owner() == "root":
        # elevate permissions
        subprocess.run(["sudo", "rm", "-rf", path])
    else:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def cp(source, target):
    if target.parent.owner() == "root":
        # elevate permissions
        subprocess.run(["sudo", "cp", "-r", source, target])
    else:
        shutil.copytree(source, target)


def mkdir(path):
    if path.parent.owner() == "root":
        # elevate permissions
        subprocess.run(["sudo", "mkdir", "-p", path])
    else:
        path.mkdir(parents=True)


class ActionContext:
    def __init__(self, source, target, interactive: bool):
        self.source = Path(source).expanduser()
        self.target = Path(target).expanduser()
        self.interactive = interactive
        self.done = False
        self.errors = []

    def __enter__(self):
        print(
            "\033[96m{:} \033[39m \033[94m{:}\033[39m : ".format(
                self.source, self.target
            ),
            end="",
        )
        return self

    def __exit__(self, type, value, traceback):
        print("\033[39m", end="")


class Action:

    @classmethod
    def process(cls: Type["Action"], context: ActionContext):
        global error
        try:
            if context.done:
                return
            action = cls()
            if action.isResponsibleFor(context):
                print(action.getMessage(context))
                if isinstance(action, RunnableAction):
                    if not context.interactive:
                        raise Exception("Interactive mode required.")
                    # interactive mode, offer to show diff
                    while True:
                        print(
                            "\033[0m[any letter to skip or 'd' to show diff]:", end=""
                        )
                        command = input()
                        if command == "d":
                            os.system(
                                f"git diff --color-words --no-index {context.source} {context.target}"
                            )
                        elif command == "":
                            action.runCommand(context)
                            break
                        else:
                            print("\033[0mSkipped")
                            break
                else:
                    # just print the message and exit
                    context.done = True
        except Exception as e:
            print("\033[91mError: ", e)
            error = 1

    def isResponsibleFor(self, context: ActionContext):
        raise NotImplementedError

    def getMessage(self, context: ActionContext):
        raise NotImplementedError


class RunnableAction(Action):
    def runCommand(self, context: ActionContext):
        raise NotImplementedError


class AssertSource(Action):
    def isResponsibleFor(self, context: ActionContext):
        return not context.source.exists()

    def getMessage(self, context: ActionContext):
        return "\033[33mSource doesn't exist."


class CreateTargetDir(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return not context.target.parent.exists()

    def getMessage(self, context: ActionContext):
        return "\033[33mTarget directory doesn't exist. Create?"

    def runCommand(self, context: ActionContext):
        mkdir(context.target.parent)


class CreateSudoCopy(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return not context.target.exists() and context.target.parent.owner() == "root"

    def getMessage(self, context: ActionContext):
        return "\033[93mTarget directory is owned by root. Sudo copy source to target?"

    def runCommand(self, context: ActionContext):
        cp(context.source, context.target)


class CreateGitCopy(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return not context.target.exists() and is_git_tracked(context.target)

    def getMessage(self, context: ActionContext):
        return "\033[93mTarget is git controlled. Copy source to target?"

    def runCommand(self, context: ActionContext):
        shutil.copyfile(context.source, context.target)


# symbolic links are not supported on FAT32, check with target.parent.owner() != "root"
class CreateFAT32Copy(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return context.target.parent.owner() == "root"

    def getMessage(self, context: ActionContext):
        return "\033[93mTarget is on a FAT32 partition. Copy source to target?"

    def runCommand(self, context: ActionContext):
        shutil.copyfile(context.source, context.target)


class CreateSymlink(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return not context.target.exists()

    def getMessage(self, context: ActionContext):
        return "\033[92mCreate symlink?"

    def runCommand(self, context: ActionContext):
        context.target.symlink_to(context.source)


class DifferentTargetNoSymlink(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return (
            context.target.exists()
            and context.target.parent.owner() != "root"
            and not is_git_tracked(context.target)
            and not context.target.is_symlink()
        )

    def getMessage(self, context: ActionContext):
        return "\033[93mTarget is not a symlink. Remove target?"

    def runCommand(self, context: ActionContext):
        rm(context.target)


class DifferentSymlink(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return (
            context.target.is_symlink() and context.target.resolve() != context.source
        )

    def getMessage(self, context: ActionContext):
        return "\033[93mTarget already links to a different source. Unlink target?"

    def runCommand(self, context: ActionContext):
        rm(context.target)


class DifferentTypeTargetFile(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return context.source.is_dir() and context.target.is_file()

    def getMessage(self, context: ActionContext):
        return "\033[33mSource is a directory but target is a file. Remove target?"

    def runCommand(self, context: ActionContext):
        rm(context.target)


class DifferentTypeTargetDir(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return context.source.is_file() and context.target.is_dir()

    def getMessage(self, context: ActionContext):
        return "\033[33mSource is a file but target is a directory. Remove target?"

    def runCommand(self, context: ActionContext):
        rm(context.target)


class DifferentContent(RunnableAction):
    def isResponsibleFor(self, context: ActionContext):
        return (
            context.source.is_file()
            and context.target.is_file()
            and context.target.exists()
            and not filecmp.cmp(context.source, context.target, shallow=False)
        )

    def getMessage(self, context: ActionContext):
        return "\033[93mSource and target differ. Remove target?"

    def runCommand(self, context: ActionContext):
        rm(context.target)


class CheckSymlink(Action):
    def isResponsibleFor(self, context: ActionContext):
        return context.target.resolve() == context.source

    def getMessage(self, context: ActionContext):
        return "\033[92m✔"


class CheckCopy(Action):
    def isResponsibleFor(self, context: ActionContext):
        return (
            context.target.exists()
            and (
                not os.access(context.target, os.W_OK)
                or context.target.parent.owner() == "root"
                or is_git_tracked(context.target)
            )
            and filecmp.cmp(context.source, context.target, shallow=False)
        )

    def getMessage(self, context: ActionContext):
        return "\033[92m(✔)"


def sync(source, target):
    global error

    with ActionContext(source, target, interactive) as context:
        AssertSource.process(context)

        DifferentContent.process(context)
        DifferentSymlink.process(context)
        DifferentTypeTargetDir.process(context)
        DifferentTypeTargetFile.process(context)
        DifferentTargetNoSymlink.process(context)

        # CreateFAT32Copy.process(context)
        CreateTargetDir.process(context)
        CreateGitCopy.process(context)
        if sys.platform == "linux":
            CreateSudoCopy.process(context)
        CreateSymlink.process(context)

        CheckSymlink.process(context)
        CheckCopy.process(context)


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


if command == "interactive":
    interactive = True
    command = "run"

if command == "run":
    try:
        if sys.platform == "linux":
            setup_dir = Path.home() / "setup"

            # sync user and root files
            sync_recursive(
                setup_dir / "linux/user",
                Path.home(),
                dir_links=[".local/share/applications/adabru"],
            )
            sync_recursive(setup_dir / "linux/root", Path("/"))

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
                "~/repo/gists/unix_socket.py",
                "~/repo/speech/adabru_talon/code/unix_socket.py",
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
        elif sys.platform == "win32":
            setup_dir = Path.home() / "Documents/git/setup"

            # sync user files
            sync_recursive(setup_dir / "windows/user", Path.home())

        exit(error)

    except KeyboardInterrupt:
        print("\nInterrupted")
        exit(error)


elif command == "audio":
    audio_dir = Path.home() / "Nextcloud/audio"

    def exec(cmd):
        # echo command for debugging
        print("\033[90m%s\033[0m" % cmd)
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0

    adb_config_file = Path.home() / ".adb_config"

    ip = ""
    port = "5555"

    if adb_config_file.exists():
        config = adb_config_file.read_text().strip().split(":")
        if len(config) == 2:
            ip, port = config

    ip = input(f"Enter ip [{ip}]: ") or ip
    port = input(f"Enter port [{port}]: ") or port

    adb_config_file.write_text(f"{ip}:{port}")
    # there is no return code if connect fails
    exec(f"adb connect {ip}:{port}")
    # adb push to android music folder
    exec(f"adb push {audio_dir} /storage/emulated/0/Music")
