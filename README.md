# Setup & Configuration

## Arcolinux Setup

- burn arcolinux-full to stick and try in live-mode
  - Rufus ! in dd-mode ! https://wiki.archlinux.org/index.php/USB_flash_installation_media#Using_Rufus
- backup Portable/ and home/ with arcolinux
  mksquashfs ~ /media/adabru/500_LapStore/2018-10-25-home.sqsh -e ~/.cache
- burn Windows to stick, remove all partitions and make 80.000MB partition (will auto-create system partitions)
  - install
  - disable fastboot
  - update driver with device manager
- burn arcolinuxd to stick
- install arcolinuxd
  - mount 100MB Windows System partition as /boot/efi
  - make 80GB btrfs partition mount as /
  - make 16GB swap partition
- setup arcolinuxd

  ```sh
  # git setup
  git config --global user.email b.brunnmeier@gmx.de
  git config --global user.name adabru

  # load keymap
  # wget -O- https://github.com/adabru/setup/archive/master.tar.gz | tar xz
  git clone https://github.com/adabru/setup
  sudo loadkeys setup-master/kbd_ab.map
  sudo cp ~/setup/kbd_ab.map /usr/share/kbd/keymaps/ab.map
  sudo sh -c "echo KEYMAP=ab > /etc/vconsole.conf"

  # wlan
  # check wlan on/off switch
  rfkill list all
  mcli device wifi
  nmcli device wifi connect your_ap_name_ssid
  nmcli connection

  # update system
  mirror
  # alternatively `yay`
  update
  pksyua

  # number of installed packages
  pacman -Qq | wc -l

  # install terminal
  pacman -S termite

  # setup xkb layout
  sudo cp ~/setup/xkb_ab /usr/share/X11/xkb/symbols/ab

  # install sway
  # https://wiki.archlinux.org/index.php/Sway#Installation
  # https://github.com/swaywm/sway/wiki
  yay -S wlroots-git sway-git
  export XKB_DEFAULT_LAYOUT=ab; sway

  # browser
  yay -S vivaldi

  wget -O- https://aur.archlinux.org/cgit/aur.git/snapshot/vivaldi-codecs-ffmpeg-extra-bin.tar.gz | tar xz
  cd vivaldi*
  yay -S pup-bin
  ./update_pkg.sh
  makepkg
  pacman -U ./*.pkg.tar.xz

  yay -S vivaldi-widevine

  # albert
  yay -S albert-lite

  # brightness
  yay -S brillo
  sudo cp setup/udev_backlight.rules /etc/udev/rules.d/backlight.rules
  grep XF86MonBrightness /usr/share/.../symbols

  # autologin
  sudo vim /lib/systemd/system/getty@.service
  # replace: ExecStart=-/sbin/agetty -o '-p -- \\u' --noclear %I %TERM
  # with:    ExecStart=-/sbin/agetty -a adabru %I %TERM

  # sudo keep display
  # https://askubuntu.com/questions/175611/cannot-connect-to-x-server-when-running-app-with-sudo#175615
  sudo visudo
  # Defaults env_keep += "DISPLAY"
  xhost local:root

  # data transfer
  pacman -S partitionmanager
  # create FAT32 partition
  sudo sh -c "echo \"/dev/disk/by-label/PORTABLE /home/adabru/portable vfat rw,umask=0000 0 0\" >> /etc/fstab"
  mkdir ~/portable
  sudo mount -a
  # navigate to backup
  sudo mount /dev/disk/by-label/500_LapStore /mnt
  tar xzf *portable.tar.gz -C ~/portable
  ```

- setup other applications
  - nautilus open terminal is hardcoded: <https://bbs.archlinux.org/viewtopic.php?id=159139>

  ```sh
  # visualstudio code
  pacman -S code

  # ranger
  # pacman -S thunar gvfs
  pacman -S ranger highlight mediainfo
  # yay -S nautilus nautilus-open-terminal

  # access documentation on 127.0.7.1:7000 via doc/
  pacman -S nftables
  echo "127.0.7.1       doc" | sudo tee --append /etc/hosts
  sudo cp ~/setup/nftables.conf /etc
  sudo systemctl enable nftables
  sudo systemctl restart nftable

  # mail
  yay -S mailpile

  pacman -S geany

  # font
  yay -S symbola gucharmap

  # check Wayland/XWayland
  # https://fedoraproject.org/wiki/How_to_debug_Wayland_problems
  xlsclients
  xwininfo

  # eduroam
  # connect to mops
  wget http://cdp.pca.dfn.de/global-root-ca/pub/cacert/cacert.pem
  sudo mv ./cacert.pem "/etc/ca-certificates/trust-source/anchors/DFN-Verein PCA Global - G01.crt"
  wget http://cdp.pca.dfn.de/rwth-ca/pub/cacert/cacert.pem
  sudo mv ./cacert.pem "/etc/ca-certificates/trust-source/anchors/RWTH Aachen CA.crt"
  wget http://cdp.pca.dfn.de/telekom-root-ca-2/pub/cacert/cacert.pem
  sudo mv ./cacert.pem "/etc/ca-certificates/trust-source/anchors/Deutsche Telekom Root CA 2.crt"
  sudo trust extract-compat
  trust list | less
  nm-connection-editor
  # SSID:eduroam, WPA2, PEAP, Deutsche_Telekom, MSCHAPv2, username, password
  nmcli connection up id eduroam

  # create ssh-key for github and gitlab
  # eval "$(ssh-agent -s)"
  # ssh-add -l
  ssh-keygen -t rsa -C "adam.brunnmeier@rwth-aachen.de" -b 4096
  cat ~/.ssh/id_rsa.pub
  # add to https://gitlab.com and https://github.com
  ssh -T git@github.com
  ssh -T git@gitlab.com

  # audio
  pacman -S alsa-utils
  alsamixer
  speaker-test
  ```

|
|@virtualenv / @pip|
  - <https://virtualenv.pypa.io/en/latest/installation.html>
  - ```
    wget -O- https://pypi.python.org/packages/source/v/virtualenv/virtualenv-16.0.0.tar.gz | tar xz
    cd virtualenv-*
    python setup.py install --prefix ~/.virtualenv
    cd ~/.virtualenv
    export PYTHONPATH=./lib/python3.7/site-packages
    ./bin/virtualenv -p python3 .
    . ./bin/activate
    ```
  - @youtube-dl @ipython @plac @colorama
|@nvm / @npm|
  - <https://github.com/creationix/nvm>

    ```
    mkdir ~/.nvm
    curl -o- https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
    exec bash
    nvm install node
    ```
  - make node available outside of terminal, add `~/bin/node` :

    ```
    #!/bin/sh

    export NVM_DIR="/home/adabru/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm
    node $@
    ```
  - make executable: └▪chmod a+x ~/bin/node↵


libreoffice-fresh # Finanzen
