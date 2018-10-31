# http://docs.openstack.org/developer/python-novaclient/ref/v2/servers.html
import time, os, sys, re
import inspect
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

if len(sys.argv) > 1:
    worker_name = str(sys.argv[1])
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

server = nova.servers.find(name=worker_name)
server.delete()
print 'Deleting, please wait...'
