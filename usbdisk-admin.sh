#USEFUL COMMANDS
#df -k
#sudo umount /dev/sdc1 
#sudo mkfs -t ext4 /dev/sdc1  
#sudo mount /dev/sdc1 /mnt/ams2
chmod 777 /mnt/ams2
#sudo blkid
#sudo vi /etc/fstab
#UUID=c350d74c-eb37-4a59-a99f-0095e718f836 /mnt/ams ext4 defaults 0 0

# Setup for qotcom dual nic computers with 1TB HD
# Generally these come unmounted after install as sda1
# To test / check use these commands
# sudo blkid
# df -h

# Once the 1TB drive has been identified reformat it with linux ext4 file system
# sudo mkfs -t ext4 /dev/sda1

# mount the drive, chown and make the default dirs 
# sudo mount /dev/sda1 /mnt/ams2
# setup drive 1st time.sh

