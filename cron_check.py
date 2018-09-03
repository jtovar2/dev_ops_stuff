import os
import time
import subprocess

DOGECOIN_EXECUTABLES_LOCATION = 'nohup /home/javier/dogecoin-1.10.0/bin/dogecoind &'
DIGIBYTE_EXECUTABLES_LOCATION = 'digibyte-6.16.2/bin/digibyted'
MAX_RETRY = 5



daemon_to_exec_map = {
        'dogecoin': DOGECOIN_EXECUTABLES_LOCATION,
        'digibyte': DIGIBYTE_EXECUTABLES_LOCATION
        }

def start_daemon(deamon_name):
    cmd = deamon_to_exec_map[ deamon_name ]
    response = os.system(cmd )


    if response == 0:
        return True
    else:
        return False

def check_ping():
    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False
    return pingstatus 
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


output = subprocess.check_output(['ps', '-A'])

for daemon in daemon_to_exec_map:
    if daemon not in output:
        print( daemon + " is not running")

