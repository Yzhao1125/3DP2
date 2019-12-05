#!/bin/bash
udhcpc -i eth0:0 -T 1 -t 5 -n
ifconfig eth0 192.168.10.10 up