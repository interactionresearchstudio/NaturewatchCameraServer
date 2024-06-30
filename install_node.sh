#!/bin/bash
# chmod +x install_node.sh

# Check for sudo permissions
if [ $EUID != 0 ]; then
    echo "Launch the script as sudo"
    sudo "$0" "$@"
    exit $?
fi

apt-get clean
apt-get update
apt-get upgrade -y
apt-get dist-upgrade -y

apt-get install curl -y
# From https://linuxize.com/post/how-to-install-node-js-on-debian-10/
apt-get remove nodejs npm -y
curl -sL https://deb.nodesource.com/setup_16.x | sudo bash -
apt-get install nodejs -y

apt-get autoremove -y
