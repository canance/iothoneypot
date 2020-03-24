from yapsy.IPlugin import IPlugin
from pygtail import Pygtail
import json
import subprocess
import time

class EveListener(IPlugin):

    def __init__(self, log_path='/var/log/suricata/eve.json'):
        self.log = Pygtail(log_path)
        super().__init__()

    def activate(self):
        print("[*] eve_listener plugin activated")

        command_line = ['suricata', '-i', 'tap0']
        self.suricata = subprocess.Popen(command_line)

    def deactivate(self):
        print("[eve_listener] Stopping suricata...")
        self.suricata.terminate()
        self.suricata.wait()
        self.run()
        print("[*] eve_listener plugin deactivated")

    def run(self, *args, **kwargs):
        if 'uuid' in kwargs:
            self.uuid = kwargs['uuid']
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        if 'ip' in kwargs:
            self.ip = kwargs['ip']

        for line in self.log:
            line = json.loads(line)

            # if line['event_type'] == 'flow':
                # print("[EVE_LISTNER] Found --> " + str(line))

            if line['event_type'] == 'flow' and (line['src_ip'] == self.ip or line['dest_ip'] == self.ip):
                # print("Found flow from %s --> %s" % (line['src_ip'], line['dest_ip']))

                #line['event'] = 'flow'
                #line['uuid'] = self.uuid
                #self.logger.info(json.dumps(line))
                try:
                    event = {}
                    event['uuid'] = self.uuid
                    event['event'] = 'flow_start'
                    event['dest_ip'] = line['dest_ip']
                    event['src_ip'] = line['src_ip']
                    event['dest_port'] = line['dest_port']
                    event['src_port'] = line['src_port']
                    event['timestamp'] = line['flow']['start']
                    event['desc'] = "%s:%s --> %s:%s" % (line['src_ip'], line['src_port'], line['dest_ip'], line['dest_port'])
                    self.logger.info(json.dumps(event))

                    event['event'] = 'flow_end'
                    event['timestamp'] = line['flow']['end']
                    self.logger.info(json.dumps(event))
                except:
                    print("[*ERROR] eve_listener:")
                    print(str(line))
