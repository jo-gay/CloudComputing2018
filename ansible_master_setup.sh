#!/bin/bash 

## generate ssh key
ssh-keygen -q

## inject ssh key into cloudinit file
#echo "ssh_authorized_keys" >> spark_cloudinit_file
sshkey="$(cat ~/.ssh/id_rsa.pub)"
echo " - sudo echo '$sshkey' >> ~/.ssh/authorized_keys" >> cloud-cfg.txt
#cat cloud-cfg.txt >> cloud_init.txt

## Set up server ready for use
sudo echo "127.0.1.1 group2-am" >> /etc/hosts
sudo echo "export LC_ALL='en_US.UTF-8'" >> ~/.bashrc
export LC_ALL='en_US.UTF-8'
source ~/.bashrc
sudo apt-get update
sudo apt install -y python-pip
sudo apt-get update
sudo apt-get -y upgrade

## Installing Openstack 
sudo apt install -y software-properties-common
sudo add-apt-repository cloud-archive:newton
sudo apt update -y && apt dist-upgrade -y
##what about the reboot?
sudo apt install -y python-openstackclient

## Write hostname to file to start creation of ansible hosts file
ip="$(hostname -I)"
echo "ansible-node ansible_ssh_host=$ip" > hosts_file

## set up environment for openstack
source ~/SNIC-openrc.sh

## Create the spark master and workers
sudo python sparknode/ssc-instance-userdata.py group2_sm
sudo python sparknode/ssc-instance-userdata.py group2_sw

## Installing Ansible 
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ansible

######################

