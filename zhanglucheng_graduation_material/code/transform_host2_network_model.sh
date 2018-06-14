#!/bin/bash

sed -i 'N;25a           --bip=10.0.1.1/24 \' /usr/lib/systemd/system/docker.service
systemctl start docker.service
systemctl enable docker.service

systemctl start openvswitch
systemctl enable openvswitch

ovs-vsctl add-br br-tun
ovs-vsctl add-port br-tun vxlan0 -- set Interface vxlan0 type=vxlan options:remote_ip=192.168.149.132
brctl addif docker0 br-tun
ip route add 10.0.2.0/24 via 192.168.149.132 dev ens33