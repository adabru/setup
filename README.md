# Setup & Configuration

## Arch Setup

- download from https://www.archlinux.de/download
- burn to stick with rufus dd (alternatively via dd from linux), see https://wiki.archlinux.org/index.php/USB_flash_installation_media#Using_Rufus
- make backup via ~/bin/backup.py
- connect lan (if connected lateron, run `dhcpcd`)
- boot from pendrive

```sh
# following commands come from https://wiki.archlinux.de/title/Arch_Install_Scripts
loadkeys de-latin1
lsblk
cfdisk
  100MB fat32 /boot
  xGB btrfs /
  2xRAM swap
mkfs.vfat -F 32 /dev/sda1
mkfs.btrfs /dev/sda2
mount /dev/sda2 /mnt
mount /dev/sda1 /mnt/boot
mkswap /dev/sda3 swapon /dev/sda3

pacstrap /mnt base base-devel linux linux-firmware vim git networkmanager python bash-completion
genfstab -p /mnt >> /mnt/etc/fstab
arch-chroot /mnt
echo adabru-reserve > /etc/hostname
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime
# uncomment 'de_DE.UTF-8 UTF-8' and 'en_US.UTF-8 UTF-8' in /etc/locale.gen
locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
mkinitcpio -p linux
passwd # set root passwd
echo KEYMAP=de > /etc/vconsole.conf

pacman -S grub os-prober
# for UEFI:
pacman -S efibootmgr

grub-install /dev/sda
# auto-detects windows via os-prober. if not, mount windows partition before
grub-mkconfig -o /boot/grub/grub.cfg
# for UEFI instead:
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=Arch-Linux-grub

exit
umount /mnt/boot
umount /mnt
```

- poweroff
- eject pendrive and boot
- install  windows
  - download and burn latest iso
  - install without internet to avoid updates
  - create a xGB partition during installation
- disable fastboot via `powercfg.cpl`
- update driver with device manager
- boot via arch pendrive to restore boot loader:

```sh
lsblk
mount /dev/sda2 /mnt
mount /dev/sda1 /mnt/boot
arch-chroot /mnt
os-prober
# if it doesn't see windows:
mount /dev/sda4 /mnt
os-prober
grub-mkconfig -o /boot/grub/grub.cfg
```

- reboot

```sh
# enable wifi
systemctl enable NetworkManager.service
systemctl start NetworkManager
nmcli
nmcli device wifi
nmcli device wifi -a MY_SSID

useradd -m adabru
passwd adabru
EDITOR=vim visudo
su adabru

git clone https://github.com/adabru/setup
sudo loadkeys setup/kbd_ab.map
setup/sync.py

# store keymap
sudo cp ~/setup/kbd_ab.map /usr/share/kbd/keymaps/ab.map
sudo sh -c "echo KEYMAP=ab > /etc/vconsole.conf"
~/setup/sync.py

# restore backup
pacman -S squashfuse rsync squashfs-tools
# plugin drive
lsblk
sudo mount -o uid=adabru,ro /dev/sdb1 /mnt
sqfs-mount.sh /mnt/20xx-xx-xx-backup.sqfs
rsync -r --info=progress2 ~/mnt/20xx-xx-xx-backup.sqfs/xx ~/xx
# rsync -r --info=progress2 --exclude '*/node_modules/' ~/mnt/20xx-xx-xx-backup.sqfs/xx ~/xx

# wlan
# check wlan on/off switch
rfkill list all
nmcli device wifi
nmcli device wifi connect your_ap_name_ssid
nmcli connection

# update system
pacman -S reflector
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
pacman -S sway xorg-server-xwayland
export XKB_DEFAULT_LAYOUT=ab; sway
# setxkbmap -layout de
# setxkbmap -layout ab

# install yay
...
# in /etc/pacman.conf :
# uncomment option 'Color'
# uncomment source [multilib]

# ssh
pacman -S openssh

# browser
yay -S vivaldi vivaldi-widevine vivaldi-codecs-ffmpeg-extra-bin

# albert
pacman -S albert muparser

# brightness
yay -S brillo
sudo cp setup/udev_backlight.rules /etc/udev/rules.d/backlight.rules
grep XF86MonBrightness /usr/share/.../symbols

# autologin
# https://wiki.archlinux.org/index.php/Getty#Virtual_console
# https://wiki.archlinux.org/index.php/Systemd#Editing_provided_units
# sudo systemctl edit getty^TAB
sudo mkdir /etc/systemd/system/getty@tty1.service.d/
sudo cp ~/setup/getty.conf /etc/systemd/system/getty@tty1.service.d/override.conf
systemctl daemon-reload

# sudo keep display
# https://askubuntu.com/questions/175611/cannot-connect-to-x-server-when-running-app-with-sudo#175615
echo "xhost local:root" > ~/.xinitrc

# data transfer
pacman -S partitionmanager
# create 50gb XFS partition with label VM for virtual drives
sudo sh -c "echo \"/dev/disk/by-label/VM /home/adabru/vm xfs users 0 0\" >> /etc/fstab"
# if partitionmanager doesn't get permissions, you can use
# su
# dbus-launch --exit-with-session partitionmanager

mkdir ~/vm
sudo mount -a
# navigate to backup
sudo mount /dev/disk/by-label/500_LapStore /mnt
```



## Further Software

- setup other applications

```sh
# visualstudio code
yay -S visual-studio-code-insiders

# git setup
git config --global user.email b.brunnmeier@gmx.de
git config --global user.name adabru

# ranger
# pacman -S thunar gvfs
pacman -S mpv

yay -S nautilus nautilus-open-terminal gvfs-smb

# access documentation on 127.0.7.1:7000 via doc/
pacman -S nftables
echo "127.0.7.1       doc" | sudo tee --append /etc/hosts
sudo cp ~/setup/nftables.conf /etc
sudo systemctl enable nftables
sudo systemctl restart nftable

# refind
pacman -S refind-efi memtest86-efi
refind-install
sudo cp ~/setup/refind.conf /boot/efi/EFI/refind/refind.conf
sudo cp ~/setup/os_grub.png /boot/efi/EFI/refind/icons/os_grub.png
sudo cp ~/setup/os_arcolinux.png /boot/efi/EFI/refind/icons/os_arcolinux.png
sudo cp /usr/share/memtest86-efi/bootx64.efi /boot/efi/EFI/tools
poweroff --reboot

# messaging
yay -S thunderbird rambox
# gmx https://support.gmx.com/pop-imap/imap/outlook.html
# gmail
# rwth https://www.welcome.itc.rwth-aachen.de/en/email.htm
# rambox:
#   Mail http://localhost:33411 https://www.mailpile.is/img/icon-512x512.png
#   FB https://facebook.com https://en.facebookbrand.com/wp-content/uploads/2016/05/flogo_rgb_hex-brc-site-250.png
#   MindCloud Slack mind-cloud
#   MindCloud https://trello.com/mindcloud77 https://d2k1ftgv7pobq7.cloudfront.net/meta/u/res/images/brand-assets/Logos/0099ec3754bf473d2bbf317204ab6fea/trello-logo-blue.png
#   MindCloud https://calendar.google.com/calendar/r https://www.gstatic.com/images/branding/product/1x/calendar_48dp.png
#   Fablab Slack fablab-erkelenz
#   i9 RocketChat https://rclufgi9.informatik.rwth-aachen.de/home
#   WA Whatsapp
#   yjs Gitter
#   Jungschar Threema

yay -S geany

# font
# see font coverage on https://www.fileformat.info/info/unicode/block/miscellaneous_symbols_and_pictographs/fontsupport.htm
yay -S ttf-symbola ttf-unifont gucharmap

# check Wayland/XWayland
# https://fedoraproject.org/wiki/How_to_debug_Wayland_problems
xlsclients
xwininfo

# eduroam
# connect to mops
nm-connection-editor
# SSID:eduroam, WPA2, PWD, username, password
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
# ctrl+shift+insert as temporary workaround for https://github.com/thestinger/termite/issues/645
yay -S tmux wl-clipboard

# bluetooth
pacman -S bluez bluez-utils pulseaudio-bluetooth blueman
sudo systemctl enable bluetooth
sudo systemctl restart bluetooth
bluetoothctl power on
bluetoothctl devices
blueman

# disable wifi card if there are problems
lspci -k
sudo modprobe -r ath9k
# to make it permanent
sudo sh -c 'echo "blacklist ath9k" > /etc/modprobe.d/modprobe.conf'

# printer
pacman -S cups cups-pdf
yay -S brother-mfc-9332cdw
systemctl enable org.cups.cupsd.service
systemctl start org.cups.cupsd.service
# setup printer at http://localhost:631/admin

# pdf reader
pacman -S evince

# screenshot
yay -S slurp grim eog

# screencast
yay -S wlstream
wlstream 25 vaapi /dev/dri/renderD128 libx264 nv12 12 /tmp/screen.mkv
# mkfifo /tmp/buffer.ts /tmp/screen.ts
# mbuffer -i /tmp/buffer.ts -o /tmp/screen.ts
# wlstream 25 vaapi /dev/dri/renderD128 libx264rgb bgr0 12 /tmp/buffer.ts

# gst-launch-1.0 -v filesrc location=/tmp/screen.mkv ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5000
# gst-launch-1.0 videotestsrc ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5000
# vlc test.sdp
#   c=IN IP4 10.5.110.117
#   m=video 5000 RTP/AVP 96
#   a=rtpmap:96 H264/90000


# android emulator
yay -S android-sdk
sdkmanager --list
# https://wiki.archlinux.org/index.php/Android#Android_Studio
sudo chown -R adabru:adabru /opt/android-sdk/
# see https://developer.android.com/about/dashboards/
sudo mount -o remount,size=5G /tmp/
touch ~/.android/repositories.cfg
sdkmanager "system-images;android-23;google_apis;x86_64"
avdmanager create avd --name myandroid -k "system-images;android-23;google_apis;x86_64"
avdmanager list avd
sdkmanager emulator
yay -S  android-sdk-platform-tools
cd /opt/android-sdk/tools
# https://developer.android.com/studio/run/emulator-commandline
# https://developer.android.com/studio/run/emulator-comparison
emulator @myandroid
adb install ~/portable/Aktuell/Android/apps/WhatsApp.apk
# for WhatsApp-Web, connect (compatible) webcam and run
emulator @myandroid -webcam-list
emulator @myandroid -camera-back webcam1

# cloud storage
pacman -S rclone
rclone config
# dropbox, google
rclone lsd dropbox:
rclone ls dropbox:
cd ~/portable/cloud/dropbox
rclone -P sync dropbox:Gemeindelieder ./Gemeindelieder
rclone lsd google:

# ftp
usermod -a -G ftp adabru
pacman -S bftpd
sudo chmod 770 /srv/ftp

# anti webspam
yay -S hosts-update
hosts-update

# opendns + hosts
yay -S ddclient
sudo sh -c 'echo "
127.0.0.1   localhost
::1         localhost
127.0.7.1   doc
" > /etc/hosts.local'
sudo hosts-update
sudo sh -c 'echo "
nameserver 208.67.222.222
nameserver 208.67.220.220
search fritz.box
nameserver 192.168.178.1
nameserver fd00::e228:6dff:fe95:24b5
" > /etc/resolv.conf'
# disable overwriting resolv.conf by network-manager https://askubuntu.com/a/623956/452398
sudo sh -c 'echo "
[main]
dns=none
" >> /etc/NetworkManager/NetworkManager.conf'
sudo systemctl restart NetworkManager
# check with `cat /etc/resolv.conf`
# see https://support.opendns.com/hc/en-us/articles/227987727-Linux-IP-Updater-for-Dynamic-Networks
sudo sh -c 'echo "
##
## OpenDNS.com account-configuration
##
protocol=dyndns2
use=web, web=myip.dnsomatic.com
ssl=yes
server=updates.opendns.com
login=opendns_username
password=‘opendns_password’
opendns_network_label
" > /etc/ddclient.conf'
# set username and password
sudo systemctl start ddclient

# setup IPv6 tunnel with hurricane electrics (free)
# login and create tunnel
# save commands to ~/bin/tunnel_ipv6.sh
# replace local ip4 from router by local ip4 of laptop, e.g. 192.168.178.41
echo 'echo "using wlan"' >> ~/bin/tunnel_ipv6.sh
sudo tunnel_ipv6.sh
# remove with `sudo ip tunnel del he-ipv6`


# node
yay -S nodejs yarn

# arduino
yay -S arduino
# install arduino extension in vscode
sudo usermod -a -G uucp,lock adabru
# logout → login
echo "ciao" > /dev/ttyUSB0
# see if lights are blinking
# set "port": "/dev/ttyUSB0" in arduino.json
# "open serial port" in vscode didn't work, using screen instead (cancel with CTRL+A K)
yay -S screen
screen /dev/ttyUSB0 19200

# wine
yay -S wine winetricks
winetricks dotnet452 corefonts
```

- see <https://wiki.archlinux.org/index.php/System_maintenance>:
  - `systemctl --failed`
  - `journalctl -p 3 -xb`

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
  - @youtube-dl @ipython @plac @colorama @Pillow


libreoffice-fresh # finance, work-table
gimp              # backgrounds, gifts
inkscape          # svg editing
graphicsmagick    # image conversion
docker            # i9 work
owncloud-client   # i9 work
firefox           # web development (test)
namcap            # AUR packaging
spotify           # music streaming
grive             # mindcloud
cura              # 3d printing
kvm               # i9 work
tk                # python GUI, lockscreen
tribler, vlc, python2-pyopenssl, python2-service-identity
                  # torrents
pdfshuffler       # typesetting
ghostscript       # typesetting
pulseeffects      # audio playback
godot             # mindcloud
stupid-ftpd       # local file shares
git-lfs           # git repos with large binaries
texworks          # latex editor

