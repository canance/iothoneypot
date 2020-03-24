import subprocess
import json
import time
import qmp
import hashlib
import os
import os.path
from yapsy.IPlugin import IPlugin

class vol_monitor(IPlugin):

    def __init__(self):
        self.prev_ps = None
        self.qmp_monitor = qmp.QEMUMonitorProtocol('qemu-qmp.sock')
        self.qmp_monitor.connect()
        super().__init__()

    def activate(self):


        print("[*] vol_monitor plugin initializing...")
        cmd = ['iptables', '-I', 'INPUT', '-i', 'tap0', '-j', 'DROP']
        output = subprocess.check_output(cmd)

        time.sleep(35)
        self.run()
        cmd = ['iptables', '-D', 'INPUT', '1']
        output = subprocess.check_output(cmd)
        print("[*] vol_monitor plugin activated")


    def deactivate(self):
        print("[*] vol_monitor plugin deactivated")

    def run(self, *args, **kwargs):
        self.uuid = kwargs['uuid'] if 'uuid' in kwargs else ""
        self.logger = kwargs['logger'] if 'logger' in kwargs else ""
        epoch_time = int(time.time())
        dump_file = 'memdump_%s' % epoch_time
        self.dump_memory(dump_file)
        output = get_procs(dump_file)
        if self.prev_ps == None:
            pretty_print(output)

        else:
            new_procs, terminated_procs = compare_outputs(self.prev_ps, output)
            print("[*] New processes")
            pretty_print(new_procs)
            print("[*] Terminated processes")
            pretty_print(terminated_procs)
            self.dump_procs(new_procs, dump_file)
            self.log(new_procs, 'new_process')
            self.log(terminated_procs, 'terminated_process')

        self.prev_ps = output
        os.remove(dump_file)

    def dump_procs(self, procs, dump_file):
        for proc in procs:
            pid = str(proc['Pid'])
            name = str(proc['Name'])
            if not os.path.exists('./procs'):
                os.makedirs('./procs')
            call_vol(dump_file, 'linux_procdump', '-D', './procs', '-p', pid)
            for fname in os.listdir('./procs'):
                if '%s.%s' % (name, pid) in fname:
                    with open('./procs/%s' % fname, 'rb') as f:
                        bytes = f.read()
                        proc['sha256'] = hashlib.sha256(bytes).hexdigest()
                        proc['virus_total'] = "https://www.virustotal.com/gui/file/%s" % proc['sha256']


    def dump_memory(self, dump_name):
        dump_path = '%s/%s' % (os.getcwd(), dump_name)
        arguments = {'paging': False, 'protocol': 'file:%s' % dump_path}
        self.qmp_monitor.cmd('dump-guest-memory', args=arguments)

    def log(self, output, event):
        output = list(output) # make copy so as to not modify the original list
        for obj in output:
            obj['event'] = event
            obj['uuid'] = self.uuid
            if 'cmd_line' in obj:
                obj['desc'] = obj['cmd_line']
            self.logger.info(json.dumps(obj))

def call_vol(memdump, command, *args):
    command_line = ['vol.py', '--plugins=/iothoneypot/vol-profiles/', '--profile=Linuxfirmadyne-v4_1_17ARM', '-f', memdump, '--output', 'json', command] + list(args)
    if command == 'linux_procdump':
        command_line.remove('--output')
        command_line.remove('json')
    output = subprocess.check_output(command_line)
    if command != 'linux_procdump':
        return json.loads(output.decode())


# takes volatility json output format and converts to cleaner output
# output must already be parsed into python dict using json.loads()
def vol_output_cleanup(output):

    l = []
    for row in output['rows']:
        new_entry = {}
        for i in range(len(output['columns'])):
            col_name = output['columns'][i]
            new_entry[col_name] = row[i]
        l.append(new_entry)
    return l

def get_procs(memdump):
    output = linux_pslist(memdump)
    output2 = linux_psaux(memdump)
    # combine pslist and psaux...
    for proc in output:
        proc['process_name'] = proc['Name']
        for proc2 in output2:
            if proc2['Pid'] == proc['Pid']:
                proc['Arguments'] = proc2['Arguments']
                if proc['Name'] not in proc['Arguments']:
                    if proc['Arguments'] != '':
                        proc['desc'] = "%s [%s]" % (proc['Name'], proc['Arguments'])
                    else:
                        proc['desc'] = proc['Name']
                else:
                    proc['desc'] = proc['Arguments']
        # for proc2 in output:
        #    if proc2['Pid'] == proc['PPid']:
        #        proc['PPid'] = "%d (%s)" % (proc2['Pid'], proc2['Name'])
    return output

def linux_psaux(memdump, kernel_threads=False):
    output = call_vol(memdump, 'linux_psaux')

    output = vol_output_cleanup(output)
    return output

def linux_pslist(memdump, kernel_threads=False):
    # grab output
    output = call_vol(memdump, 'linux_pslist')

    # cleanup output
    output = vol_output_cleanup(output)

    # remove kernel threads?
    if not kernel_threads:
        output = [o for o in output if o[u'DTB'] != -1]

    return output


# returns the difference between the second set and the first set
def compare_outputs(first, second):
    # use set
    # can't hash dict so convert back to json string
    first_set = set([json.dumps(item) for item in first])
    second_set = set([json.dumps(item) for item in second])
    # find differences
    z_set = second_set - first_set # new procs
    x_set = first_set - second_set # terminated procs
    # return difference as list of python objs

    new_procs = list([json.loads(item) for item in z_set])
    terminated_procs = list([json.loads(item) for item in x_set])
    return new_procs, terminated_procs




# prints output in human readable format
def pretty_print(output):
    if len(output) == 0:
        return
    cols = output[0].keys()
    for col in cols:
        print(str(col) + '\t', end='')
    print()
    for obj in output:
        for value in obj.values():
            print(str(value) + '\t', end='')
        print()
