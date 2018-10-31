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
    print instance_name
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
f.write(ip_adress + " " + instance.name + "\n")

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

f = open('/etc/ansible/hosts', 'r')
fw = open('/etc/ansible/hosts', 'w')

lines = f.read().splitlines()


f.close()

lines = [ line for line in lines if "#" not in line ]

asn = "ansible-node"
ash = "ansible_ssh_host="
anc = "ansible_connection="
asu = "ansible_user=ubuntu"

sm = "sparkmaster"
sw = "sparkworker"

arg = "ansible_ssh_common_args='-o StrictHostKeyChecking=no'"


worker_number = None
new_wn = None
last_worker_index = None
spark_master_index = None

ans_node = asn + " " + anc + "local " + asu

if '[configNode]' not in lines:
    lines.append('')
    lines.append('[configNode]')
    lines.append(ans_node)

if "w" in instance_name:
    for index in range(len(lines)):

        # Check for either the last worker or if there is a sparkmaster index
        if sm in lines[index] and ash in lines[index]:
            spark_master_index = index
        if sw in lines[index] and ash in lines[index]:
            last_worker_index = index
            
            # extract the last digit from sparkworkers ( sparkworker5 -> 5 ) 
            s = re.search(r"\d+(\d+)?", line)
            worker_number = s.group(0)
            
    if worker_number is not None:
        new_wn = str(int(worker_number) + 1)
    else:
        new_wn = "1"
        
    if last_worker_index is not None:
        lines.insert(last_worker_index + 1, sw + new_wn + " " +ash + ip_adress)
    elif spark_master_index is not None:
        lines.insert(spark_master_index + 1, sw + new_wn + " " +ash + ip_adress)


    end_line = sw + '[1:' + new_wn + '] ' + anc + "ssh" + " " + asu + " " + arg
    if '[sparkworker]' in lines:
        for index in range(len(lines)):
            if sw + '[1:' in lines[index]:
                lines[index] = end_line
    else:
        lines.append('')
        lines.append('[sparkworker]')
        lines.append(end_line)



if "m" in instance_name:

    insert_sm = True
    
    for line in lines:
        if sm in line and ash in line:
            insert_sm = False
            
    if insert_sm is True:
        lines.insert(1, sm + " " + ash + ip_adress)
        
    end_line = sm + " " + anc + "ssh" + " " + asu + " " + arg
    if '[sparkmaster]' in lines:
        for index in range(len(lines)):
            if sw + '[1:' in lines[index]:
                lines[index] = end_line
    else:
        lines.append('')
        lines.append('[sparkmaster]')
        lines.append(end_line)

for line in lines:
    fw.write(line + "\n")

fw.close()
