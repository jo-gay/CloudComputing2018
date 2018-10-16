#!/bin/bash 

## generate ssh key
ssh-keygen

## inject ssh key into cloudinit file
echo "ssh" >> spark_cloudinit_file
sshkey="$(cat ~/.ssh/id_rsa.pub)"
echo " - $sshkey" >> spark_cloudinit_file
cat cloud-cfg.txt >> spark_cloudinit_file

## Set up server ready for use
sudo echo "127.0.1.1 group2-am" >> /etc/hosts
sudo echo "export LC_ALL='en_US.UTF-8'" >> ~/.bashrc
sudo source ~/.bashrc
sudo apt-get update
sudo apt install python-pip
sudo apt-get update
sudo apt-get upgrade

## Installing Openstack 
sudo apt-install software-properties-common
sudo add-apt-repository cloud-archive:newton
sudo apt update && apt dist-upgrade
##what about the reboot?
sudo apt install python-openstackclient

## set up environment for openstack
source ~/.SNIC-openrc.sh

## Create the spark master and workers
sudo python ssc-instance-userdata.py

## Installing Ansible 
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y ansible

## Write hostname to file to start creation of ansible hosts file

ip="$(hostname -I)"
echo "ansible-node ansible_ssh_host=$ip" > hosts_file

######################

