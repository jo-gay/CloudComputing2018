#!/bin/bash 

echo '##Clone git repo and move into directory'
git clone https://github.com/jo-gay/CloudComputing2018.git
cd CloudComputing2018/

echo '## generate ssh key (no passphrase, do nothing if already exists)'
cat /dev/zero | ssh-keygen -q -N ""

echo '## inject ssh key into cloudinit file'
sshkey="$(cat /root/.ssh/id_rsa.pub)"
echo " - echo '$sshkey' >> /home/ubuntu/.ssh/authorized_keys" >> sparknode/cloud-cfg.txt

echo '## Set up server ready for use'
hname="$(hostname)"
sudo echo "127.0.1.1 $hname" >> /etc/hosts
sudo echo "export LC_ALL='en_US.UTF-8'" >> ~/.bashrc
export LC_ALL='en_US.UTF-8'
source ~/.bashrc
sudo apt-get update
sudo apt install -y python-pip
sudo pip install flask
sudo apt-get update
sudo apt-get -y upgrade

echo '## Installing Openstack '
sudo apt install -y software-properties-common
sudo add-apt-repository -y cloud-archive:newton
sudo apt update -y && sudo apt dist-upgrade -y
sudo apt install -y python-openstackclient

echo '## Write hostname to file to start creation of ansible hosts file'
ip="$(hostname -I)"
sudo echo "ansible-node ansible_ssh_host=$ip" > /etc/ansible/hosts

echo '## Create the spark master and workers'
sudo python sparknode/ssc-instance-userdata.py group2sm
sudo python sparknode/ssc-instance-userdata.py group2sw

echo '## Installing Ansible '
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ansible

echo '# Run ansible to configure the spark master and workers'
sleep 10
ansible-playbook -b spark_deployment.yml | tee ansible_out.txt

cat ansible_out.txt | grep token | grep , | awk '{print $3}' | cut -f2 -d"\"" | cut -f1 -d"\\" > jupyter_token

echo 'Run the API'
screen python restapi.py &


######################

