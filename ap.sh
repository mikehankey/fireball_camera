cat <<EOH>> /etc/apache2/sites-enabled/000-default.conf 

<Directory /var/www/html/pycgi>
Options ExecCGI
AddHandler cgi-script .py
</Directory>

EOH

service apache2 restart

sudo ln -s /etc/apache2/mods-available/cgi.load /etc/apache2/mods-enabled/cgi.load
