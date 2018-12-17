#!/usr/bin/python

import os, filecmp

if os.geteuid() == 0:
  print("Don't run as root. Exiting.")
  exit()

def sync(source, target):
  print("\033[96m{:} \033[39m→ \033[94m{:}\033[39m: ".format(source, target), end="")
  source = os.path.expanduser(source)
  target = os.path.expanduser(target)
  if not os.path.exists(source):
    print("\033[33msource doesn't exist")
  elif os.path.realpath(target) == source:
    print("\033[93m✔")
  elif not os.path.exists(os.path.dirname(target)):
    print("\033[93mtarget dir doesn't exist (yet).")
  elif os.path.islink(target):
    print("\033[33mtarget already links to {:}".format(os.path.realpath(target)))
  elif os.path.isdir(source) and os.path.isfile(target):
    print("\033[33msource is a dir but target is a file")
  elif os.path.isfile(source) and os.path.isdir(target):
    print("\033[33msource is a file but target is a dir")
  elif os.path.exists(target) and filecmp.cmp(source, target, shallow=False) and os.access(target, os.W_OK):
    print("remove target and sync again")
  elif os.path.exists(target) and filecmp.cmp(source, target, shallow=False) and not os.access(target, os.W_OK):
    print("\033[93m(✔)")
  elif os.path.exists(target):
    print("\033[33msource and target differ")
  elif not os.access(os.path.dirname(target), os.W_OK):
    print("sudo copy source to target")
  else:
    os.symlink(source, target)
    print("\033[93m✔")
  print("\033[39m", end="")

# refind
sync("~/setup/refind.conf", "/boot/efi/EFI/refind/refind.conf")
sync("~/setup/os_arcolinux.png", "/boot/efi/EFI/refind/icons/os_arcolinux.png")
sync("~/setup/os_grub.png", "/boot/efi/EFI/refind/icons/os_grub.png")

# keyboard
sync("~/setup/kbd_ab.map", "/usr/share/kbd/keymaps/ab.map")
sync("~/setup/xkb_ab", "/usr/share/X11/xkb/symbols/ab")

# sway
sync("~/setup/sway_config", "~/.config/sway/config")
sync("~/setup/bin/statusbar.py", "~/bin/statusbar.py")

# firewall and doc
sync("~/setup/nftables.conf", "/etc/nftables.conf")

# VS Code config
sync("~/repo/vscode-adabru-markup", "~/.vscode-oss/extensions/vscode-adabru-markup")
sync("~/setup/vscode_keybindings.json", "~/.config/Code - OSS/User/keybindings.json")
sync("~/setup/vscode_settings.json", "~/.config/Code - OSS/User/settings.json")

# terminal + envs
sync("~/setup/termite_config", "~/.config/termite/config")
sync("~/setup/bashrc", "~/.bashrc")
sync("~/setup/clingrc", "~/.clingrc")
sync("~/setup/pythonrc", "~/.pythonrc")
sync("~/setup/tmux.conf", "~/.tmux.conf")
sync("~/setup/bin/copy.py", "~/bin/copy.py")
sync("~/setup/XCompose", "~/.XCompose")
sync("~/setup/bin/node", "~/bin/node")

# brightness
sync("~/setup/udev_backlight.rules", "/etc/udev/rules.d/backlight.rules")

# launcher
sync("~/setup/bin/launcher.sh", "~/bin/launcher.sh")

# inkscape
# sync("~/setup/inkscape.xml", ???)

# virtual MIDI keyboard
sync("~/setup/vkeybdmap", "~/.vkeybdmap")

# sync
sync("~/setup/sync.py", "~/bin/sync.py")

# youtube
sync("~/setup/bin/yt.py", "~/bin/yt")

# bluetooth
sync("~/setup/bin/bt.py", "~/bin/bt")

# packaging
sync("~/setup/makepkg.conf", "~/.makepkg.conf")

# android emulator
sync("~/setup/bin/whatsapp", "~/bin/whatsapp")