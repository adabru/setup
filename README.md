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
  - make 80GB btrfs partition mount as / , label with "ARCOLINUX"
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
  ~/setup/sync.py

  # wlan
  # check wlan on/off switch
  rfkill list all
  nmcli device wifi
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
  echo "xhost local:root" > ~/.xinitrc

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
  pacman -S ranger highlight mediainfo mpv
  # w3m image preview doesn't work in termite: https://github.com/thestinger/termite/issues/501
  # mpv instead: https://github.com/ranger/ranger/wiki/Image-Previews#with-mpv
  #   $ranger = /usr/lib/python3.7/site-packages/ranger/
  sudo vim /usr/lib/python3.7/site-packages/ranger/ext/img_display.py
  sudo vim /usr/lib/python3.7/site-packages/ranger/core/fm.py

  # yay -S nautilus nautilus-open-terminal

  # access documentation on 127.0.7.1:7000 via doc/
  pacman -S nftables
  echo "127.0.7.1       doc" | sudo tee --append /etc/hosts
  sudo cp ~/setup/nftables.conf /etc
  sudo systemctl enable nftables
  sudo systemctl restart nftable

  # refind
  pacman -S refind-efi
  refind-install
  sudo cp ~/setup/refind.conf /boot/efi/EFI/refind/refind.conf
  sudo cp ~/setup/os_grub.png /boot/efi/EFI/refind/icons/os_grub.png
  sudo cp ~/setup/os_arcolinux.png /boot/efi/EFI/refind/icons/os_arcolinux.png
  poweroff --reboot

  # messaging
  yay -S thunderbird rambox
  # gmx https://support.gmx.com/pop-imap/imap/outlook.html
  # gmail
  # rwth https://www.welcome.itc.rwth-aachen.de/en/email.htm
  # rambox:
  #   Mail http://localhost:33411 https://www.mailpile.is/img/icon-512x512.png
  #   FB https://facebook.com https://en.facebookbrand.com/wp-content/uploads/2016/05/flogo_rgb_hex-brc-site-250.png
  #   Mindcloud Slack mind-cloud
  #   InfoAG Slack infoaghh
  #   i9 RocketChat https://rclufgi9.informatik.rwth-aachen.de/home
  #   WA Whatsapp
  #   yjs Gitter
  #   Jungschar Threema

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
  pacman -S alsa-utils pulseaudio pavucontrol
  alsamixer
  speaker-test
  # reboot for pulseaudio to start

  # tmux
  # wl-clipboard as temporary workaround for https://github.com/swaywm/sway/issues/926
  yay -S tmux wl-clipboard

  # bluetooth
  pacman -S bluez bluez-utils pulseaudio-bluetooth blueman
  sudo systemctl enable bluetooth
  sudo systemctl restart bluetooth
  blueman

  # printer
  pacman -S cups cups-pdf
  yay -S brother-mfc-9332cdw
  systemctl enable org.cups.cupsd.service
  systemctl start org.cups.cupsd.service
  # setup printer at http://localhost:631/admin

  # pdf reader
  pacman -S evince

  # flash
  pacman -S pepper-flash

  # screenshot
  yay -S slurp grim
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


libreoffice-fresh # finance, work-table
gimp # backgrounds, gifts
inkscape # svg editing
graphicsmagick # image conversion
docker # i9 work
namcap # AUR packaging