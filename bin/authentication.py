#!/usr/bin/python

import asyncio
from dataclasses import dataclass
from pathlib import Path
import pickle
from random import random
import base64
from re import findall
import re
import subprocess
from sys import argv
from time import sleep

if len(argv) < 2 or not argv[1] in {"edit", "replace", "type"}:
    print("usage:\n\n  authentication.py edit | replace <input-path> | type <domain>")
    exit()
command = argv[1]

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


key = Path("~/.cache/authentication_py/key").expanduser()
cache = Path("~/.cache/authentication_py/cache").expanduser()


@dataclass(init=False)
class Vault:
    path: Path
    password: Fernet


def open_vault(vault: Vault):
    # load user file
    with vault.path.open("rb") as file:
        raw_encrypted = file.read()
        raw = vault.password.decrypt(raw_encrypted).decode("utf-8")
        return raw


def store(raw: str, vault: Vault):
    # encrypt and save file
    encrypted = vault.password.encrypt(raw)
    with vault.path.open("wb") as file:
        file.write(encrypted)

    # generate new cache
    key.parent.mkdir(exist_ok=True, parents=True)
    new_key = Fernet(Fernet.generate_key())
    with key.open("wb") as file:
        pickle.dump(new_key, file)
    with cache.open("wb") as file:
        encrypted = new_key.encrypt(pickle.dumps(vault))
        file.write(encrypted)


def create_key(password: str):
    # os.urandom(16)
    salt = b"\xb1\xa3\xcd\xe1\xc9\xb9\r?\xd6\x9aD\xf1\xec\xcc\x10>"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)


# load cache
try:
    with key.open("rb") as file:
        old_key = pickle.load(file)
    with cache.open("rb") as file:
        encrypted = file.read()
        decrypted = old_key.decrypt(encrypted)
        vault = pickle.loads(decrypted)
except FileNotFoundError as e:
    vault = Vault()
    print("enter path:")
    vault.path = Path(input()).expanduser()
    print("enter password:")
    vault.password = create_key(input())

if command == "replace":
    # copy content of <input-path> and store encrypted version in predefined path
    with Path(argv[2]).open("rb") as file:
        raw = file.read()
    store(raw, vault)

elif command == "edit":
    # open in editor
    async def edit_file():
        raw = open_vault(vault)

        # copy to tmp
        tmp = Path("/tmp/auth-" + str(random()))
        with tmp.open("w") as file:
            file.write(raw)

        # edit externally
        process = await asyncio.subprocess.create_subprocess_exec(
            "featherpad", "-s", tmp
        )
        await asyncio.sleep(0.5)
        tmp.unlink()
        await process.wait()

        # remove tmp and store edited user file
        if tmp.exists():
            with tmp.open("rb") as file:
                raw = file.read()
            tmp.unlink()
            store(raw, vault)

    asyncio.run(edit_file())
    print("exit")

elif command == "type":
    raw = open_vault(vault)
    query = argv[2]
    # extract domain name
    query = re.sub(r".+//|www.|/.*", "", query)
    for match in findall(r"\((.*)\)(\n.+)(\n.+)?\n\n", raw):
        if query in match[0].lower().split(" "):
            if match[2] == "":
                user = ""
                password = match[1][1:]
            else:
                user = match[1][1:]
                password = match[2][1:]
            break
    if user == "":
        subprocess.run(("wtype", password))
    else:
        # some keys don't work in xwayland
        # https://github.com/atx/wtype/issues/31
        # https://github.com/atx/wtype/issues/46
        # https://github.com/atx/wtype/issues/39
        # subprocess.run(("wtype", user, "-k", "tab", password))

        # workaround using clipboard
        subprocess.run(("wl-copy", user))
        # wait a second
        sleep(0.1)
        subprocess.run(("wtype", "-d", "10", "-M", "ctrl", "-k", "v", "-m", "ctrl"))
        sleep(0.1)
        subprocess.run(("wtype", "-k", "tab"))
        subprocess.run(("wl-copy", password))
        sleep(0.1)
        subprocess.run(("wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"))
        sleep(0.1)
        subprocess.run(("wl-copy", argv[2]))
