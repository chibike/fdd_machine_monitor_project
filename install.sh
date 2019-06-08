#!/bin/bash

INSTALL_DIR=$(pwd)

sudo apt-get update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
sudo apt install -y software-properties-common apt-transport-https
sudo apt install -y git-core python3 python3-pip python-dev python3-dev
sudo apt install -y libboost1.62-all-dev

cd /usr/lib/arm-linux-gnueabihf/
# sudo find libboost_python-py35.so / | grep libboost_python-py35
sudo ln -s libboost_python-py35.so libboost_python3.so

cd $INSTALL_DIR/fdd_machine_monitor_project/py-spidev
make
sudo make install

cd ../RF24
sudo make install

cd pyRF24
sudo python3 setup.py install

cd ../../web
sudo python3 -m pip install -r requirements.txt
python3 manage.py makemigrations basic_app
python3 manage.py makemigrations device_manager
python3 manage.py migrate