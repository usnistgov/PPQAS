#!/bin/sh

################################################################################
#
# Required Python Dependencies:
#	- flask
#	- pymongo 
#	- xmltodict 
#	- flask_login 
#	- flask_wtf 
#	- docopt 
#	- flask_mail
#
#
#
################################################################################

#pip install --user [package_name]
#pip2 install --user [package_name]

pip2 install --upgrade pip
pip2 install --user flask pymongo xmltodict flask_login flask_wtf docopt flask_mail


# Download and install MongoDB
#wget http://downloads.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-latest.zip
#unzip mongodb-win32-x86_64-2008plus-ssl-latest.zip
wget http://downloads.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-3.7.3.zip
unzip mongodb-win32-x86_64-2008plus-ssl-3.7.3.zip
chmod +x mongodb-win32-x86_64-2008plus-ssl-3.7.3/bin/*
mv mongodb-win32-x86_64-2008plus-ssl-3.7.3/bin/* /usr/local/bin
mkdir -p /cygdrive/c/data/db

#####
# mongod &
#####

# Download PPQAS Source from GitHub
cd ~
git clone https://github.com/usnistgov/PPQAS.git

cd ~/PPQAS/ps-aug19-2017
python runserver.py
python runserver.py > runserver_`date +%s`.log 2>&1 &