# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys, re
import inspect
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

if len(sys.argv) > 1:
    instance_name = str(sys.argv[1])
else:
    sys.exit("Need to give an argument name")

flavor = "ACCHT18.normal" 
private_net = "SNIC 2018/10-30 Internal IPv4 Network"
floating_ip_pool_name = None
floating_ip = None
image_name = "Ubuntu 16.04 LTS (Xenial Xerus) - latest"

loader = loading.get_plugin_loader('password')

#auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
#                                username=env['OS_USERNAME'],
#                                password=env['OS_PASSWORD'],
#                                project_name=env['OS_PROJECT_NAME'],
#                                project_domain_name=env['OS_USER_DOMAIN_NAME'],
#                                project_id=env['OS_PROJECT_ID'],
#                                user_domain_name=env['OS_USER_DOMAIN_NAME'])

auth = loader.load_from_options(auth_url            = 'https://uppmax.cloud.snic.se:5000/v3',
                                username            = 's10791',
                                password            = 'nCcEcCoDp9167',
                                project_name        = 'SNIC 2018/10-30',
                                project_domain_name = 'snic',
                                project_id          = '2344cddf33a1412b846290a9fb90b762',
                                user_domain_name    = 'snic')

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print "user authorization completed."

image = nova.glance.find_image(image_name)

flavor = nova.flavors.find(name=flavor)

if private_net != None:
    net = nova.neutron.find_network(private_net)
    nics = [{'net-id': net.id}]
else:
    sys.exit("private-net not defined.")

#print("Path at terminal when executing this file")
print(os.getcwd() + "\n")
cfg_file_path =  'sparknode/cloud-cfg.txt'
#cfg_file_path =  'cloud-cfg.txt'
if os.path.isfile(cfg_file_path):
    userdata = open(cfg_file_path)
else:
    sys.exit("cloud-cfg.txt is not in current working directory")

secgroups = ['default']

print "Creating instance ... "
instance = nova.servers.create(name=instance_name, image=image, flavor=flavor, userdata=userdata, nics=nics,security_groups=secgroups)
inst_status = instance.status
print "waiting for 10 seconds.. "
time.sleep(10)

while inst_status == 'BUILD':
    print "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..."
    time.sleep(5)
    instance = nova.servers.get(instance.id)
    inst_status = instance.status


ip_adress = None
for network in instance.networks[private_net]:
    if re.match('\d+\.\d+\.\d+\.\d+', network):
        ip_adress = network
        break
if ip_adress == None:
    print('No IP adress found')
    sys.exit(1)
    
print "Instance: "+ instance.name +" is in " + inst_status + "state. With IP: " + str(ip_adress)

f = open("/etc/hosts", "a")
f.write(ip_adress + " " + instance.name)

# ansible-node ansible_ssh_host=192.168.1.12
# sparkmaster  ansible_ssh_host=192.168.1.20
# sparkworker1 ansible_ssh_host=192.168.1.19
# sparkworker2 ansible_ssh_host=192.168.1.18

# [configNode]
# ansible-node ansible_connection=local ansible_user=ubuntu

# [sparkmaster]
# sparkmaster ansible_connection=ssh ansible_user=ubuntu

# [sparkworker]
# sparkworker[1:2] ansible_connection=ssh ansible_user=ubuntu


f2 = open("/etc/ansible/hosts", "a")
ash = "ansible_ssh_host="
anc = "ansible_connection="
asu = "ansible_user=ubuntu"


