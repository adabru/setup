#!/usr/bin/sh
confirm() {
    package=$1
    if ! pacman -Q $package >/dev/null 2>&1; then
        sudo pacman -S --noconfirm $package
    fi
}
aur_confirm() {
    package=$1
    if ! pacman -Q $package >/dev/null 2>&1; then
        paru -S --noconfirm $package
    fi
}

# sync
./setup/bin/sync.py
if [ $? -ne 0 ]; then
    read -p "Not everything is synced. Do you want to run the sync.py script interactively? (y/N): " choice
    if [ "$choice" = "y" ]; then
        ./setup/bin/sync.py interactive
    fi
fi

# if .bashrc was changed, reload it
source ~/.bashrc

# if getty (autologin) was changed, reload it
sudo systemctl daemon-reload

# update system
if ! command -v reflector; then
    i reflector
    mirror
    update
fi

# install aur-helper
if ! command -v paru; then
    git clone https://aur.archlinux.org/paru.git
    cd paru
    makepkg -si
    cd ..
    rm -rf paru
fi

# brightness
aur_confirm brillo
sudo usermod -a -G video adabru

# sfs
confirm squashfuse squashfs-tools ntfs-3g

# i tried community/code twice, but switched to insiders due to issues (the second time marketplace didn't work)
confirm shfmt
aur_confirm visual-studio-code-insiders-bin

# sway
confirm alacritty sway xorg-xwayland

confirm nm-connection-editor

confirm vivaldi
# proprietary codecs
sudo /opt/vivaldi/update-ffmpeg

confirm partitionmanager polkit-gnome

confirm mpv
confirm nautilus gvfs-smb gvfs-mtp

confirm thunderbird
# gmx https://support.gmx.com/pop-imap/imap/outlook.html
# gmail
# rwth https://help.itc.rwth-aachen.de/en/service/1jefzdccuvuch/article/614566f01671435d9f0e267e49aeae54/

confirm featherpad

# font
# see font coverage on https://www.fileformat.info/info/unicode/block/miscellaneous_symbols_and_pictographs/fontsupport.htm
confirm ttf-dejavu gucharmap
aur_confirm ttf-unifont

# audio
confirm alsa-utils pulseaudio pavucontrol

confirm tmux wl-clipboard

confirm bluez bluez-utils pulseaudio-bluetooth blueman
sudo systemctl enable --now bluetooth

# printer
confirm cups cups-pdf
aur_confirm brother-mfc-9332cdw
sudo systemctl enable --now cups.service
# setup printer at http://localhost:631/admin

# pdf reader
confirm evince

# screenshot
confirm slurp grim eog

# anti webspam
aur_confirm hosts-update
sudo hosts-update

# auto mount
confirm udiskie

# wallpapers
aur_confirm multibg-sway
