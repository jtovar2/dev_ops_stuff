import os
import time
import subprocess
from google.cloud import datastore


LCP = os.environ['LCP']
DOGECOIN_EXECUTABLES_LOCATION = 'nohup /home/javier/dogecoin-1.10.0/bin/dogecoind &'
DIGIBYTE_EXECUTABLES_LOCATION = '/home/javier/digibyte-6.16.2/bin/digibyted'
MAX_RETRY = 5

store_client = datastore.Client()

daemon_to_exec_map = {
        'dogecoin': DOGECOIN_EXECUTABLES_LOCATION,
        'digibyte': DIGIBYTE_EXECUTABLES_LOCATION
        }

def start_daemon(daemon_cmd):
    response = os.system(daemon_cmd)


    if response == 0:
        return True
    else:
        return False

def check_that_service_is_running(daemon):
    print(daemon)
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
    return pingstatus

def update_ip():
    # The kind for the new entity
    kind = 'wallet_{LCP}'.format(LCP=LCP)
    # The name/ID for the new entity
    name = 'main'
    # The Cloud Datastore key for the new entity
    task_key = datastore_client.key(kind, name)

    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task['IP'] = 'test'

    # Saves the entity
    datastore_client.put(task)

    print('Saved {}: {}'.format(task.key.name, task['IP']))

internet_conn = check_ping()

if not internet_conn:
    response = os.system("dhclient")
    internet_conn = check_ping()
    retry_count = MAX_RETRY
    while not internet_conn and retry_count > 0:
        response = os.system("dhclient")
        time.sleep(30)
        internet_conn = check_ping()
        retry_count = retry_count - 1

internet_conn = check_ping()
if not internet_conn:
    exit()



for daemon in daemon_to_exec_map:
    if check_that_service_is_running(daemon):
        result = start_deamon(daemon)
        retry_count = MAX_RETRY
        while not result and retry_count > 0:
            result = start_daemon(daemon)
            retry_count = retry_count - 1

        if not result:
            ##unable to start daemon
            print("prob with {deamon}".format(daemon=daemon))

update_ip()

