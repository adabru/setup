#!/usr/bin/python

import os, filecmp

if os.geteuid() == 0:
  print("Don't run as root. Exiting.")
  exit()

def sync(source, target):
  print("\033[96m{:} \033[39m→ \033[94m{:}\033[39m: ".format(source, target), end="")
  source = os.path.expanduser(source)
  target = os.path.expanduser(target)
  if os.path.realpath(target) == source:
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
  elif os.path.isfile(target) and not os.access(target, os.W_OK):
    print("sudo copy source to target")
  else:
    os.symlink(source, target)
    print("\033[93m✔")
  print("\033[39m", end="")

# keyboard
sync("~/setup/kbd_ab.map", "/usr/share/kbd/keymaps/ab.map")
sync("~/setup/xkb_ab", "/usr/share/X11/xkb/symbols/ab")

# sway
sync("~/setup/sway_config", "~/.config/sway/config")

# firewall and doc
sync("~/setup/nftables.conf", "/etc/nftables.conf")

# VS Code config
sync("~/repo/vscode-adabru-markup", "~/.vscode-oss/extensions/vscode-adabru-markup")
sync("~/setup/vscode_keybindings.json", "~/.config/Code - OSS/User/keybindings.json")
sync("~/setup/vscode_settings.json", "~/.config/Code - OSS/User/settings.json")

# terminal
sync("~/setup/bashrc", "~/.bashrc")
sync("~/setup/clingrc", "~/.clingrc")
sync("~/setup/pythonrc", "~/.pythonrc")
sync("~/setup/tmux.conf", "~/.tmux.conf")
sync("~/setup/XCompose", "~/.XCompose")

# brightness
sync("~/setup/udev_backlight.rules", "/etc/udev/rules.d/backlight.rules")

# inkscape
# sync("~/setup/inkscape.xml", ???)

# virtual MIDI keyboard
sync("~/setup/vkeybdmap", "~/.vkeybdmap")
