#!/bin/sh

# Once the 1TB drive has been identified reformat it with linux ext4 file system
sudo mkfs -t ext4 /dev/sda1

# mount the drive, chown and make the default dirs
sudo mount /dev/sda1 /mnt/ams2

sudo chown -R ams:ams /mnt/ams2
mkdir /mnt/ams2/HD
mkdir /mnt/ams2/SD
mkdir /mnt/ams2/SD/proc
mkdir /mnt/ams2/SD/proc/daytime
mkdir /mnt/ams2/meteors/
mkdir /mnt/ams2/cal/
mkdir /mnt/ams2/saved/
mkdir /mnt/ams2/saved/planes
mkdir /mnt/ams2/saved/sats
mkdir /mnt/ams2/saved/interesting

sudo cp rc.local.start /etc/rc.local
