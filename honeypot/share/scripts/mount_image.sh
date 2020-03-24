#!/usr/bin/env bash

if [ $# -eq 0 ]; then
  image="image.raw"
else
  image=$1
fi

mkdir "${image}_dir"

loop=$(kpartx -avs "$image" | cut -d ' ' -f 3)

fsck -y /dev/mapper/$loop
mount /dev/mapper/$loop "${image}_dir"
