#!/bin/sh
# TODO / CURRENT STATE
# the apt-get update installs py3.5 and this confuses the script 
# current process is to uninstall py3.4 with apt-get remove
# install numpy 
# remake opencv

mkdir /var/www
mkdir /var/www/html
mkdir /var/www/html/out
mkdir /var/www/html/out/false
mkdir /var/www/html/out/maybe
mkdir /var/www/html/out/cal
chown -R ams:ams /var/www


## install gcc#

update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-6    
apt-get install git
git clone https://github.com/mikehankey/fireball_camera


## enable shell login on pi
## enable vnc login on pi raspi-config

apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages update
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages dist-upgrade
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages upgrade

#
## install opencv per this doc
## http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/
#
#exit

apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install build-essential cmake pkg-config
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libxvidcore-dev libx264-dev
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libgtk2.0-dev
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libatlas-base-dev gfortran
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install python2.7-dev python3.5-dev
cd ~

wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip
unzip opencv_contrib.zip

apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev

#
##python
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
pip install numpy
pip install netifaces
pip install pyephem

apt-get install python3-dateutil
apt-get install python3-pil
pip install pytesseract

#
##compile opencv
#


cd ~/opencv-3.1.0/
mkdir build
cd build
#make clean
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.1.0/modules \
    -D WITH_OPENMP=ON \
    -D BUILD_EXAMPLES=ON ..
make -j4
# if errors then compile on 1 core
make install
ldconfig

# NEED TO INSTALL GCC6 FOR ASTROMETRY TO WORK
#awk '{gsub(/\jessie/,"stretch"); print}' /etc/apt/sources.list > sources.list.x
#cp sources.list.x /etc/apt/sources.list
#apt-get update
#apt-get install gcc-6 g++-6
#awk '{gsub(/\stretch/,"jessie"); print}' /etc/apt/sources.list > sources.list.x
#cp sources.list.x /etc/apt/sources.list
#apt-get update
#apt --fix-broken install

# INSTALL ASTROMETRY.NET PRE-REQUISITS
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libwcs4
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install wcslib-dev

# Set gcc6 as CC env var 
CC=/usr/bin/gcc-6
export CC

NETPBM_INC=-I/usr/include
NETPBM_LIB=/usr/lib/libnetpbm.a
export NETPBM_INC
export NETPBM_LIB

WCS_SLIB="-Lwcs"
WCSLIB_INC="-I/usr/local/include/wcslib-5.15"
WCL_LIB="-Lwcs"
export WCS_SLIB
export WCSLIB_INC
export WCS_LIB

apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libcairo2-dev libnetpbm10-dev netpbm \
                       libpng12-dev libjpeg-dev python-numpy \
                       python-pyfits python-dev zlib1g-dev \
                       libbz2-dev swig libcfitsio-dev

cd ~
wget http://astrometry.net/downloads/astrometry.net-latest.tar.gz
gunzip astrometry.net-latest.tar.gz
tar xf astrometry.net-latest.tar

mv /usr/bin/gcc /usr/bin/gcc.bak
ln -s /usr/bin/arm-linux-gnueabihf-gcc-6 /usr/bin/gcc

cd astrometry.net-*
make
make py
make extra
make install

#when done
rm /usr/bin/gcc
mv /usr/bin/gcc.bak /usr/bin/gcc
#index-4116.fits  index-4117.fits  index-4118.fits  index-4119.fits

wget http://broiler.astrometry.net/~dstn/4100/index-4116.fits
mv index-4116.fits /usr/local/astrometry/data 
wget http://broiler.astrometry.net/~dstn/4100/index-4117.fits
mv index-4117.fits /usr/local/astrometry/data 
wget http://broiler.astrometry.net/~dstn/4100/index-4118.fits
mv index-4118.fits /usr/local/astrometry/data 
wget http://broiler.astrometry.net/~dstn/4100/index-4119.fits
mv index-4119.fits /usr/local/astrometry/data 

### additions this failed.. along with PIP
pip install netifaces
apt-get install npm
npm config set prefix /usr/local
npm install -g bower
pip install pathlib 
install pycrypto
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install isc-dhcp-server
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install xfce4 xfce4-goodies vnc4server
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install ubuntu-gnome-desktop -y

apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install gnome-menu-editor -y
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install gnome-panel -y
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install curl -y
apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install lynx -y
##
