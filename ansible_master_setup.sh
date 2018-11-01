#!/bin/bash 

echo '##Clone git repo and move into directory'
#git clone https://github.com/jo-gay/CloudComputing2018.git
#cd CloudComputing2018/

echo '## generate ssh key (no passphrase, do nothing if already exists)'
cat /dev/zero | ssh-keygen -q -N ""

echo '## inject ssh key into cloudinit file'
sshkey="$(cat ~/.ssh/id_rsa.pub)"
echo " - echo '$sshkey' >> ~/.ssh/authorized_keys" >> sparknode/cloud-cfg.txt

echo '## Set up server ready for use'
sudo echo "127.0.1.1 group2amnew" >> /etc/hosts
sudo echo "export LC_ALL='en_US.UTF-8'" >> ~/.bashrc
export LC_ALL='en_US.UTF-8'
source ~/.bashrc
sudo apt-get update
sudo apt install -y python-pip
sudo apt-get update
sudo apt-get -y upgrade

echo '## Installing Openstack '
sudo apt install -y software-properties-common
sudo add-apt-repository -y cloud-archive:newton
sudo apt update -y && sudo apt dist-upgrade -y
##what about the reboot?
sudo apt install -y python-openstackclient

echo '## Write hostname to file to start creation of ansible hosts file'
ip="$(hostname -I)"
sudo echo "ansible-node ansible_ssh_host=$ip" > /etc/ansible/hosts

#echo '## set up environment for openstack - now handled by python file'
#source ~/SNIC-openrc.sh

echo '## Create the spark master and workers'
sudo python sparknode/ssc-instance-userdata.py group2sm
sudo python sparknode/ssc-instance-userdata.py group2sw

echo '## Installing Ansible '
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ansible

echo '# Run ansible to configure the spark master and workers'
ansible-playbook -b spark_deployment.yml

######################

