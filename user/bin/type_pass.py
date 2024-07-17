#!/usr/bin/python

import subprocess
from dataclasses import dataclass
from pathlib import Path
from sys import argv
from time import sleep

if len(argv) < 2 or not argv[1] in {"generate", "type"}:
    print(
        """
usage:

  type_pass.py generate
  type_pass.py type <id> (userpassw | user | passw | mailpassw | mail)        

"""
    )
    exit()
command = argv[1]


action_to_lines = {
    "passw": (0,),
    "user": (1,),
    "mail": (2,),
    "userpassw": (1, 0),
    "mailpassw": (2, 0),
}


@dataclass(init=False)
class Vault:
    path: Path
    password: str


if command == "generate":
    # prepare application folder
    desktopBasePath = Path("~/.local/share/applications/").expanduser()

    scriptPath = Path(__file__).resolve()

    # walk through password store
    storePath = Path("~/.password-store").expanduser()
    for path in storePath.glob("**/*.gpg"):
        if path.is_file():
            id = path.relative_to(storePath).with_suffix("").as_posix()
            entry = subprocess.run(
                ("pass", "show", id), capture_output=True
            ).stdout.decode("utf-8")
            # init passw, user, mail from entry
            lines = iter(entry.splitlines())
            passw = next(lines, "")
            user = next(lines, "")
            mail = next(lines, "")

            # generate desktop file
            actions = []
            if passw and user:
                actions.append("userpassw")
            if passw:
                actions.append("passw")
            if user:
                actions.append("user")
            if mail:
                actions.append("mail")
            if passw and mail:
                actions.append("mailpassw")
            defaultAction = actions[0]
            desktop = f"""
[Desktop Entry]
Version=1.0
Name={id}
Exec={scriptPath} type {id} {defaultAction}
Type=Application
Terminal=false
Actions={";".join(actions)};
"""
            for action in actions:
                desktop += f"""
[Desktop Action {action}]
Name={action}
Exec={scriptPath} type {id} {action}
"""
            escapedId = id.replace("/", "_")
            desktopPath = desktopBasePath / f"passwordstore_{escapedId}.desktop"
            desktopPath.write_text(desktop)

elif command == "type":
    id = argv[2]
    action = argv[3]
    lines = action_to_lines[action]

    # some keys don't work in xwayland
    # https://github.com/atx/wtype/issues/31
    # https://github.com/atx/wtype/issues/46
    # https://github.com/atx/wtype/issues/39
    # subprocess.run(("wtype", user, "-k", "tab", password))
    # workaround using clipboard

    # store current clipboard
    clipboard = subprocess.run(("wl-paste",), capture_output=True).stdout

    # get password store entry
    entry_lines = (
        subprocess.run(("pass", "show", id), capture_output=True)
        .stdout.decode("utf-8")
        .splitlines()
    )

    for i, line in enumerate(lines):
        subprocess.run(("wl-copy", entry_lines[line]))
        sleep(0.1)
        subprocess.run(("wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"))
        if i != len(lines) - 1:
            sleep(0.1)
            subprocess.run(("wtype", "-k", "tab"))

    # restore clipboard
    sleep(0.1)
    subprocess.run(("wl-copy", clipboard))
