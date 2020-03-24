#!/usr/bin/env python3


import sys
import os
import os.path
import pathlib
from shutil import copyfile

def main():
    if len(sys.argv) < 2:
        print("Usage: %s diff_file" % sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1]) as f:
        cwd = os.getcwd()
        for line in f:
             line = line.split(' and ')
             i1_file = line[0].replace('Files ', '')
             i2_file = line[1].replace(' differ', '')
             files = (cwd + '/' + i1_file.strip(), cwd + '/' + i2_file.strip())
             retain_files(files)

def retain_files(files):
    if os.path.isfile(files[1]): # dropped or modified files
        base = os.path.basename(files[1])
        dir_path = 'files/' + files[1].replace(base, '').replace(os.getcwd(), '').replace('i2_files', 'dropped')
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        copyfile(files[1], dir_path + '/' + base)
    elif os.path.isfile(files[0]): # deleted files
        base = os.path.basename(files[0])
        dir_path = 'files/' + files[0].replace(base, '').replace(os.getcwd(), '').replace('i1_files', 'deleted')
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        copyfile(files[0], dir_path + '/' + base)


if __name__ == '__main__':
    main()
