#!/usr/bin/env python3

import network_listener
import plugins
import time
import uuid
import logging
import logstash
import json
import datetime
import threading
import os
import shutil
import argparse
import sys
from yapsy.PluginManager import PluginManager


parser = argparse.ArgumentParser(description="Honeypot monitor")
parser.add_argument('--interval', action='store', default=15, type=int)
parser.add_argument('--runtime', action='store', default=60, type=int)
parser.add_argument('--ip', action='store', default='10.10.10.10', type=str)

args = parser.parse_args()
INTERVAL = args.interval
RUN_TIME = args.runtime
ip = args.ip

# setup plugin manager
plugin_manager = PluginManager()
plugin_manager.setPluginPlaces(["/iothoneypot/scripts/plugins"])
plugin_manager.collectPlugins()

session_uuid = str(uuid.uuid4())

# setup logger
logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler('localhost', 5000, version=1))
msg = {'event': 'session_start', 'uuid': session_uuid, 'desc': session_uuid}
logger.info(json.dumps(msg))


# activate plugins
for plugin_info in plugin_manager.getAllPlugins():
    plugin_manager.activatePluginByName(plugin_info.name)

network_listener.wait_for_activity(ip)

END_TIME = time.time() + RUN_TIME

# run plugins on interval
while time.time() < END_TIME:
    for plugin_info in plugin_manager.getAllPlugins():
        args = []
        kwargs = {
            'uuid': session_uuid,
            'logger': logger,
            'ip': ip,
        }
        plugin_thread = threading.Thread(target=plugin_info.plugin_object.run, args=args, kwargs=kwargs)
        plugin_thread.start()
    time.sleep(INTERVAL)

current_threads = threading.enumerate()
for t in current_threads:
    try:
        t.join() # wait for finish
    except RuntimeError:
        pass

# deactivate plugins
for plugin_info in plugin_manager.getAllPlugins():
     plugin_manager.deactivatePluginByName(plugin_info.name)

# create dir to hold artifacts
session_dir = session_uuid
os.mkdir(session_dir)
os.mkdir(session_dir + '/pcaps')

# move artifacts into session directory
shutil.move('./files', session_dir)
shutil.move('./net_dump.pcap', session_dir + '/pcaps')
if os.path.exists('./procs'):
    shutil.move('./procs', session_dir)
