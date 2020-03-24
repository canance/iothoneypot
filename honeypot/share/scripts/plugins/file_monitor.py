from yapsy.IPlugin import IPlugin
import sys
import os
import os.path
import pathlib
import subprocess
import time
import hashlib
import shutil
import json

OVERLAY_IMAGE = 'image-overlay.qcow2'
ORIG_IMAGE = 'image.raw'

class file_monitor(IPlugin):

    def __init__(self):
        self.prev_image = None
        super().__init__()
    def activate(self):
        print("[*] file_monitor plugin activated")

    def deactivate(self):
        print("Removing %s..." % self.prev_image)
        os.remove(self.prev_image)
        shutil.rmtree('%s_files' % self.prev_image)
        shutil.rmtree('%s_files' % ORIG_IMAGE)
        print("[*] file_monitor plugin deactivated")

    def run(self, *args, **kwargs):
        self.uuid = kwargs['uuid']
        self.logger = kwargs['logger']

        epoch_time = int(time.time())
        diff_file = 'diff_%s' % epoch_time
        current_image = 'image_%s.raw' % epoch_time
        qcow2_to_raw(OVERLAY_IMAGE, current_image)
        if self.prev_image == None: # is this the first time?  If so, use original image.
            command_line = ['dropped_files.sh', ORIG_IMAGE, current_image, diff_file]
        else:
            command_line = ['dropped_files.sh', self.prev_image, current_image, diff_file]
        print("Running " + str(command_line))
        output = subprocess.check_output(command_line)
        with open(diff_file) as f:
            cwd = os.getcwd()
            for line in f:
                 line = line.split(' and ')
                 i1_file = line[0].replace('Files ', '')
                 i2_file = line[1].replace(' differ', '')
                 files = (cwd + '/' + i1_file.strip(), cwd + '/' + i2_file.strip())
                 self.retain_files(files)
        if self.prev_image != None: # we don't want to delete the original image
            print("Removing %s..." % self.prev_image)
            os.remove(self.prev_image)
            shutil.rmtree('%s_files' % self.prev_image)

        self.prev_image = current_image
        os.remove(diff_file)

    def retain_files(self, files):
        if os.path.isfile(files[1]): # dropped or modified files
            print('[*] Dropped/Modified file: %s' % files[1])

            base = os.path.basename(files[1])
            dir_path = os.path.dirname(files[1]).replace(os.getcwd(), '')[1:]
            try:
                image_dir = dir_path[:dir_path.index('/')]
            except:
                image_dir = dir_path
            dir_path = 'files/' + dir_path.replace(image_dir, 'dropped')
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(files[1], dir_path + '/' + base)

            # get hash
            with open(files[1], 'rb') as f:
                bytes = f.read()
                hash = hashlib.sha256(bytes).hexdigest()

            vt_url = "https://www.virustotal.com/gui/file/%s" % hash
            # log
            msg = {'event': 'dropped_or_modified_file', 'desc': base, 'path': files[1], 'uuid': self.uuid, 'sha256': hash, 'virus_total': vt_url}
            self.logger.info(json.dumps(msg))
        elif os.path.isfile(files[0]): # deleted files
            print('[*] Deleted file: %s' % files[0])
            base = os.path.basename(files[0])
            dir_path = os.path.dirname(files[0]).replace(os.getcwd(), '')[1:]
            try:
                image_dir = dir_path[:dir_path.index('/')]
            except:
                image_dir = dir_path
            dir_path = 'files/' + dir_path.replace(image_dir, 'deleted')
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(files[0], dir_path + '/' + base)

            # get hash
            with open(files[0], 'rb') as f:
                bytes = f.read()
                hash = hashlib.sha256(bytes).hexdigest()

            vt_url = "https://www.virustotal.com/gui/file/%s" % hash

            # log
            msg = {'event': 'deleted_file', 'desc': base, 'path': files[0], 'uuid': self.uuid, 'sha256': hash, 'virus_total': vt_url}
            self.logger.info(json.dumps(msg))
def qcow2_to_raw(image1, image2):
    subprocess.check_output(['qcow2_to_raw.sh', image1, image2])
