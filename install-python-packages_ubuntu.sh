#!/bin/bash

# Make sure apt-get is up to date
sudo apt-get update

# Install the PostgreSQL python connector
sudo pip2.7 install psycopg2
sudo pip install pydicom
sudo pip install numpy
sudo apt-get install python-matplotlib
sudo pip install dicompyler-core
sudo pip install Jinja2
sudo pip install Requests
sudo pip install Tornado==4.4.2
sudo pip install PyYaml
sudo pip install bokeh
