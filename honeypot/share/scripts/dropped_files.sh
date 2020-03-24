#!/usr/bin/env bash

if [ $# != 3 ]; then
    echo "Usage: $0 image1 image2 diff_file"
    exit 1
fi
image1="$1"
image2="$2"
diff_file="$3"

mkdir i1 i2 "${image1}_files" "${image2}_files" &>/dev/null

# mount image.raw and copy files
loop=$(kpartx -avs $image1 | cut -d ' ' -f 3)
fsck -y /dev/mapper/$loop
mount /dev/mapper/$loop i1
cp -R i1/* "${image1}_files"
umount i1
kpartx -d $image1 &>/dev/null
rm -rf i1

# mount image-overlay.raw and copy files
loop=$(kpartx -avs $image2 | cut -d ' ' -f 3)
fsck -y /dev/mapper/$loop
mount /dev/mapper/$loop i2
cp -R i2/* "${image2}_files"
umount i2
kpartx -d $image2 &>/dev/null
rm -rf i2

# diff
diff -Naurq "${image1}_files/" "${image2}_files/" 2>/dev/null | grep differ > $diff_file

exit 0
