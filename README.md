# Setup & Configurations

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

  ```
  # git setup
  git config --global user.email b.brunnmeier@gmx.de
  git config --global user.name adabru
  
  # load keymap
  # wget -O- https://github.com/adabru/setup/archive/master.tar.gz | tar xz
  git clone https://github.com/adabru/setup
  sudo loadkeys setup-master/kbd_ab.map
  sudo cp setup-master/kbd_ab.map /usr/share/kbd/keymaps/ab.map
  sudo sh -c "echo KEYMAP=ab > /etc/vconsole.conf"
  
  # wlan
  # https://wiki.archlinux.org/index.php/broadcom_wireless
  lspci -vnn -d 14e4:
  # check wlan on/off switch
  rfkill list all
  # no solution found!

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
  sudo ln -s /home/adabru/setup/xkb_ab /usr/share/X11/xkb/symbols/ab

  # install sway
  # https://wiki.archlinux.org/index.php/Sway#Installation
  # https://github.com/swaywm/sway/wiki
  yay -S wlroots-git sway-git
  mkdir -p .config/sway
  cp setup/sway_config .config/sway/config
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
  ```
- setup other applications

  ```
  # visualstudio code
  pacman -S code
  cp ~/setup/vscode_keybindings.json ~/.config/Code\ -\ OSS/User/keybindings.json
  cp ~/setup/vscode_settings.json ~/.config/Code\ -\ OSS/User/settings.json
  ```

