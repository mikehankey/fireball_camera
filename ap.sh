cat <<EOH>> /etc/apache2/sites-enabled/000-default.conf 

<Directory /var/www/html/pycgi>
Options ExecCGI
AddHandler cgi-script .py
</Directory>

EOH


ln -s /etc/apache2/mods-available/cgi.load /etc/apache2/mods-enabled/cgi.load
rm /var/www/html/index.html
ln -s /home/ams/fireball_camera/pycgi/index.html /var/www/html/index.html
/etc/init.d/apache2 restart
