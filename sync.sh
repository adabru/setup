#!/bin/bash

if [ $EUID -eq 0 ]
  then echo "Don't run as root. Exiting."
  exit
fi

sync() {
  # source
  s="\e[96m$1\e[39m"
  # target
  t="\e[94m$2\e[39m"
  tf="\e[94m$2${1##*/}\e[39m"
  echo -ne "sync $s → $t: "
  if   [ -d "$s"   ] ;then
    echo -e "$s \e[91mis a folder, using suboptimal ln -s\e[39m"; ln -s "$1" "$2"
  elif [ ! -f "$1" ] ;then
    echo -e "$s \e[33mdoesn't exist\e[39m"
  elif [ ! -d "$2" ] ;then
    echo -e "$t \e[33mdoesn't exist\e[39m"
  elif [ ! -f "$2/${1##*/}" ] ;then
    echo -e "\e[32mcreate\e[39m"; cp "$1" "$2"; touch "$1" "$2/${1##*/}"
  else
    if   [ "$1" -nt "$2/${1##*/}" ] ;then
      echo -e "\e[32moverwrite\e[39m"; cp "$1" "$2"; touch "$1" "$2/${1##*/}"
    elif [ "$1" -ot "$2/${1##*/}" ] ;then
      echo -e "$tf \e[91mis newer\e[39m"
    else
      echo -e "\e[90mnothing to do\e[39m"
    fi
  fi
}

sync ~/setup/kbd_ab.map /usr/share/kbd/keymaps/ab.map
sync ~/setup/xkb_ab /usr/share/X11/xkb/symbols/ab

# sway
sync ~/setup/sway_config ~/.config/sway/config

# VS Code config
sync ~/repo/vscode-adabru-markup ~/.vscode/extensions
sync ~/setup/vscode_keybindings.json "~/.config/Code - OSS/User/keybindings.json"
sync ~/setup/vscode_settings.json "~/.config/Code - OSS/User/settings.json"

# terminal
sync ~/setup/bashrc ~/.bashrc
sync ~/setup/clingrc ~/.clingrc
sync ~/setup/pythonrc ~/.pythonrc
sync ~/setup/tmux.conf ~/.tmux.conf
sync ~/setup/XCompose ~/.XCompose

# brightness
sync ~/setup/udev_backlight.rules /etc/udev/rules.d/backlight.rules

# inkscape
# sync ~/setup/inkscape.xml ???

# virtual MIDI keyboard
sync ~/setup/vkeybdmap ~/.vkeybdmap
