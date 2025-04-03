# PC Setup (dual boot)

## OS Installation

Arch can be installed on existing Windows installation and Windows can be installed on existing Arch installation.

Preferred way is to install Windows first (<https://wiki.archlinux.org/title/Dual_boot_with_Windows#Installation>)

Download arch.iso from <https://www.archlinux.de/download> .
Download windows.iso from <https://www.microsoft.com/de-de/software-download/windows11ISO>

For single boot, burn arch.iso to pendrive with rufus dd-mode or `pv arch.iso > /dev/sdx`.
For dualboot, use ventoy.

```sh
sudo pacman -S ventoy
lsblk
sudo ventoy -i /dev/sdx
sudo mount /dev/sdx1 /mnt
# if windows.iso is too large, you need to reformat the partition created by ventoy from fat32 to exfat
cp ~/Downloads/<windows.iso> /mnt && sync
cp ~/Downloads/<arch.iso> /mnt && sync
sudo umount /mnt
sudo eject /dev/sdx # may fail, doesn't matter
```

Boot ventoy on new system.

Install windows on new system. Optionally turn off internet to avoid updates.

Make the efi partition during windows installation: <https://wiki.archlinux.org/title/Dual_boot_with_Windows#The_EFI_system_partition_created_by_Windows_Setup_is_too_small> .

Disable fastboot via `powercfg.cpl`.

Make a system backup on old system with `backup.py`.

```sh
# following commands come from https://wiki.archlinux.de/title/Arch_Install_Scripts

loadkeys de-latin1

# connect to wifi as show in the printed instructions; use tab completion
iwctl

lsblk
cfdisk
  100MB fat32 /boot
  xGB btrfs /
  RAM+1GB swap
mkfs.vfat -F 32 /dev/sda1
mkfs.btrfs /dev/sda2
mount /dev/sda2 /mnt
mount /dev/sda1 /mnt/boot
mkswap /dev/sda3
swapon /dev/sda3

# the following command needs internet
pacstrap /mnt base base-devel linux linux-firmware vim git networkmanager python bash-completion
genfstab -p /mnt >> /mnt/etc/fstab
arch-chroot /mnt
echo adabru-linux > /etc/hostname
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime
# enable network time sync
timedatectl set-ntp true
# uncomment 'de_DE.UTF-8 UTF-8' and 'en_US.UTF-8 UTF-8' in /etc/locale.gen
locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
mkinitcpio -p linux
passwd # set root passwd
pacman -S refind
refind-install
vim /boot/refind_linux.conf
# "Boot with standard options" "root=/dev/nvme0n1p5 rw add_efi_memmap"

exit
poweroff
```

Eject pendrive and boot into arch. Refind will automatically find it.

## Arch Configuration

```sh
# enable wifi
systemctl enable --now NetworkManager.service
nmcli device wifi connect -a <tab completion>

groupadd sudo
useradd -m -G sudo adabru
passwd adabru
# enable sudo group permissions
EDITOR=vim visudo
su adabru
# faillock --release

git clone https://github.com/adabru/setup
./setup/linux/setup.sh

# restore backup; plugin drive
lsblk
backup_mount /dev/sdb1
# /mnt/20xx-xx-xx-backup.sqfs
backup_restore "20xx-xx-xx"

# change PARTUUID to your root partition
blkid
xdg-open /boot/EFI/refind/refind.conf
poweroff --reboot
# if some other installation or package has overwritten the boot order, use:
# sudo refind-mkdefault
```

## Windows Configuration

Run following command. It will open an elevation prompt. That is necessary to edit registry keys.

```powershell
python .\windows\setup.py
winget install Governikus.AusweisApp Microsoft.VisualStudioCode Git.Git Gyan.FFmpeg Python.Python.3.12 Unity.UnityHub GitHub.cli Bitwarden.Bitwarden KDE.Okular Google.Chrome Beeper.Beeper Mozilla.Thunderbird Discord.Discord Microsoft.PowerToys
```

## Further Software

```sh
systemctl --user enable --now adabru.headset

# check Wayland/XWayland
# https://fedoraproject.org/wiki/How_to_debug_Wayland_problems
# 1. check with QT_QPA_PLATFORM=xcb or other env var if known
# 2. check on other VTE ctrl+alt+fx with `weston-launch` (ctrl+alt+backspace to quit)
# 3. use startxfce4
xlsclients
xwininfo

# setup new wifi connection
nm-connection-editor
nmcli connection up id <connection_id>

# internal microphone boost is not saved per default because pulseaudio resets it
# see https://wiki.archlinux.org/index.php/PulseAudio/Troubleshooting#Pulse_overwrites_ALSA_settings)
# and https://wiki.archlinux.org/index.php/PulseAudio/Troubleshooting#Microphone_distorted_due_to_automatic_adjustment
# the workaround vie setting the [Element * Mic Boost] volume to 50 in sudo vim /usr/share/alsa-card-profile/mixer/paths/analog-input-mic.conf
# failed to work, too; so a daemon is used in the background to detect headset plugin and set the value
usermod -a -G input adabru
alsamixer
speaker-test
# reboot for pulseaudio to start

# enable audio loopback device with:
sudo modprobe snd-aloop
# route input to output, see https://thelinuxexperiment.com/pulseaudio-monitoring-your-line-in-interface/
pactl unload-module module-loopback
pactl load-module module-loopback latency_msec=1
# alternatively, see https://gist.github.com/ericbolo/1261438048147b97316ff65f1ee
# pactl list sources
# pactl list sinks short
# pacat -r --latency-msec=1 -d alsa_input.pci-0000_00_1b.0.analog-stereo | pacat -p --latency-msec=1 -d alsa_output.pci-0000_00_1b.0.analog-stereo

aplay -l
arecord -l
alsaloop -C hw:0,0 -P hw:0,0

# bluetooth
bluetoothctl power on
bluetoothctl devices
blueman

# disable wifi card if there are problems
lspci -k
sudo modprobe -r ath9k
# to make it permanent
sudo sh -c 'echo "blacklist ath9k" > /etc/modprobe.d/modprobe.conf'

# screencast
auri obs-studio wlrobs-hg
# then select "Wayland output (scpy)" for the whole screen or "Window Capture (Xcomposite)" for X windows

# ftp
auri stupid-ftpd
ftp_here.sh

# opendns + hosts
auri ddclient
sudo sh -c 'echo "
127.0.0.1   localhost
::1         localhost
127.0.7.1   doc
" > /etc/hosts.local'
sudo hosts-update
sync.py
sudo systemctl restart NetworkManager
# check `cat /etc/resolv.conf`
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

# install arduino extension in vscode
sudo usermod -a -G uucp,lock adabru
# logout → login
echo "ciao" > /dev/ttyUSB0
# see if lights are blinking
# set "port": "/dev/ttyUSB0" in arduino.json
# "open serial port" in vscode didn't work, using screen instead (cancel with CTRL+A K)
i screen
screen /dev/ttyUSB0 19200

# wine
i wine winetricks
winetricks dotnet452 corefonts

# gamepad: nintendo switch pro controller
## Alternative A
# https://wiki.archlinux.org/title/Gamepad
gpg --keyserver keyserver.ubuntu.com --recv-key E23B7E70B467F0BF
auri hid-nintendo-dkms xf86-input-joystick ydotool
# https://gamepad-tester.com
systemctl --user enable --now ydotool
ydotool mousemove --absolute 100 100
## Alternative B
auri sc-controller
## Alternative C
# https://wiki.archlinux.org/title/Gamepad#iPEGA-9017s_and_other_Bluetooth_gamepads
# https://www.reddit.com/r/RetroPie/comments/67lhv3/nintendo_switch_pro_controller_is_fully_working/
auri xboxdrv
sudo cp ~/setup/gamepad/udev_bt_switch_pro.rules /etc/udev/rules.d/99-bt_switch_pro.rules
sudo udevadm control --reload-rules
xboxdrv_switch_pro.conf
xboxdrv --evdev /dev/btjoy --config .config/xboxdrv/ipega.conf

```

- see <https://wiki.archlinux.org/index.php/System_maintenance>:
  - `systemctl --failed`
  - `journalctl -p 3 -xb`
  - update system with: `update` (pacman) or `tupdate` (trizen)
