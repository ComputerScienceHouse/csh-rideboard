#!/bin/bash

source config.sh

if [ "$1" = true ] 
then 
    # Fix for Cannot open TUN/TAP dev /dev/net/tun: No such file or directory
    mkdir -p /dev/net
    mknod /dev/net/tun c 10 200
    addgroup -S vpn
    rm -rf /tmp/*

    # Start up openvpn
    openvpn --config /usr/src/vpn/client.ovpn --auth-user-pass /usr/src/vpn/client.pass &
fi

FLASK_APP=app.py FLASK_DEBUG=1 python3 -m flask run --host=0.0.0.0 --port=8080