#!/bin/bash
# Mac OS Sierra Install script
# Assumes Xcode already installed

sudo easy_install pip
sudo -H pip install pydicom
sudo -H pip install matplotlib
sudo -H pip install --ignore-installed six
sudo -H pip install dicompyler-core

# after mysql package installer and server running
# mysql -u root -h 127.0.0.1 -p
# enter temp password
# install mysql python connector via oracle download