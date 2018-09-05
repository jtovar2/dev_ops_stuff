import os
import time
import subprocess
from google.cloud import datastore
import requests
import json

LCP = os.environ['LCP']
DOGECOIN_EXECUTABLES_LOCATION = '/home/javier/dogecoin-1.10.0/bin/dogecoind'
DIGIBYTE_EXECUTABLES_LOCATION = '/home/javier/digibyte-6.16.2/bin/digibyted'
MAX_RETRY = 5

datastore_client = datastore.Client()

daemon_to_exec_map = {
        'dogecoin': DOGECOIN_EXECUTABLES_LOCATION,
        'digibyte': DIGIBYTE_EXECUTABLES_LOCATION
        }

def start_daemon(daemon_cmd):
    print("about to start this daemon")
    subprocess.Popen(['nohup', daemon_cmd],stdout=open('/dev/null', 'w'),
            stderr=open('/home/javier/logfile.log', 'a'),
            preexec_fn=os.setpgrp)
    print("daemon started")

def check_that_service_is_running(daemon):
    output = subprocess.check_output(['ps', '-A'])
    if daemon not in output:
        start_daemon( daemon_to_exec_map[daemon] )
        print( daemon + " is not running")

def check_ping():
    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False
        print("ping failed so sleep")
        time.sleep(30)
    return pingstatus

def update_ip():
    ip_api_address = 'https://api.ipify.org/?format=json'
    response = requests.get(ip_api_address)
    json_dict = response.json()
    # The kind for the new entity
    kind = 'wallet_{LCP}'.format(LCP=LCP)
    # The name/ID for the new entity
    name = 'main'
    # The Cloud Datastore key for the new entity
    task_key = datastore_client.key(kind, name)

    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task['IP'] = json_dict['ip']

    # Saves the entity
    datastore_client.put(task)

    print('Saved {}: {}'.format(task.key.name, task['IP']))

internet_conn = check_ping()
if not internet_conn:
    response = os.system("dhclient")
    internet_conn = check_ping()
    retry_count = MAX_RETRY
    while not internet_conn or retry_count > 0:
        response = os.system("dhclient")
        time.sleep(30)
        internet_conn = check_ping()
        retry_count = retry_count - 1

internet_conn = check_ping()
if not internet_conn:
    exit()

else:
    print("there is internet connection")


for daemon in daemon_to_exec_map:
    if check_that_service_is_running(daemon):
        spawn_deamon(start_daemon,daemon)

update_ip()

