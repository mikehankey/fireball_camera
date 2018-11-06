sudo umount /dev/sda1
sudo mkfs -t ext4 /dev/sda1
sudo mount /dev/sda1
sudo chown -R ams:ams /mnt/ams2
mkdir /mnt/ams2/SD
mkdir /mnt/ams2/SD/proc
mkdir /mnt/ams2/SD/proc/daytime
mkdir /mnt/ams2/HD/
mkdir /mnt/ams2/meteors
mkdir /mnt/ams2/cal/
mkdir /mnt/ams2/cal/solved
mkdir /mnt/ams2/cal/bad
mkdir /mnt/ams2/cal/failed
mkdir /mnt/ams2/saved/
mkdir /mnt/ams2/saved/sats
mkdir /mnt/ams2/saved/interesting
mkdir /mnt/ams2/saved/planes
