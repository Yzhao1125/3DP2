#!/bin/bash
killall dhclient
killall wpa_supplicant
ip link set dev wlan0 down
ip addr flush dev wlan0
ip link set dev wlan0 up
wpa_supplicant -i wlan0 -Dnl80211 -c /root/3DP2/3DP2/wpa.conf > /root/3DP2/3DP2/abc.txt

