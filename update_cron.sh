#!/bin/sh

sudo cp crontab.txt /var/spool/cron/crontabs/pi
sudo chown pi /var/spool/cron/crontabs/pi
sudo chgrp crontab /var/spool/cron/crontabs/pi
sudo chmod 600 /var/spool/cron/crontabs/pi
sudo /etc/init.d/cron restart
