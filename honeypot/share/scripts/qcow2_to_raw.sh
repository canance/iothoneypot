#!/usr/bin/env bash

if [ $# != 2 ]; then
    echo "Usage: $0 image raw_name"
    exit 1
fi

cp $1 $2.qcow2
qemu-img convert $2.qcow2 $2
rm $2.qcow2
