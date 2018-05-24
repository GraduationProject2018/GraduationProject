#!/bin/bash

yum install docker
systemctl restart docker.service

yum -y install wget gcc make python-devel openssl-devel kernel-devel graphviz kernel-debug-devel autoconf automake rpm-build redhat-rpm-config libtool

adduser ovs
su - ovs
mkdir -p ~/rpmbuild/SOURCES
wget http://openvswitch.org/releases/openvswitch-2.3.2.tar.gz
cp openvswitch-2.5.0.tar.gz ~/rpmbuild/SOURCES/
tar xfz openvswitch-2.5.0.tar.gz
sed 's/openvswitch-kmod, //g' openvswitch-2.5.0/rhel/openvswitch.spec > openvswitch-2.5.0/rhel/	openvswitch_no_kmod.spec
rpmbuild -bb --nocheck openvswitch-2.5.0/rhel/openvswitch_no_kmod.spec

mkdir /etc/openvswitch
yum localinstall /home/ovs/rpmbuild/RPMS/x86_64/openvswitch-2.3.2-1.x86_64.rpm -y
systemctl start openvswitch.service
systemctl is-active openvswitch
ovs-vsctl -V
systemctl enable openvswitch

rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm
yum --enablerepo=elrepo-kernel install  kernel-ml-devel kernel-ml
awk -F\' '$1=="menuentry " {print $2}' /etc/grub2.cfg
grub2-set-default 0
reboot