#!/bin/bash
exec > /dev/null 2>&1

cp nftables.conf /etc/
sudo systemctl restart nftables
