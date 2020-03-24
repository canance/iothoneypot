#!/usr/bin/env bash

if [ $# -eq 0 ]; then
  image="image.raw"
else
  image=$1
fi


umount "${image}_dir"
kpartx -d "$image" &>/dev/null
rm -rf "${image}_dir"
