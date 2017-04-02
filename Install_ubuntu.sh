#!/bin/bash
# Ubuntu install script

# Install apt-get and pip
sudo apt-get update
sudo apt install python-pip
sudo pip install --upgrade pip

# MySQL Install
sudo apt-get install mysql-server
sudo mysql_secure_installation
mysqld --initialize

# Install essential packages
sudo pip install pydicom
sudo pip install numpy
sudo apt-get install python-matplotlib
sudo pip install dicompyler-core
sudo pip install --allow-external mysql-connector-python mysql-connector-python
