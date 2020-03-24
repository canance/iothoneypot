#!/usr/bin/env bash

if [ $# -eq 0 ]; then
  image="image.raw"
else
  image=$1
fi
image_dir="${image}_dir"
password="$1$I3WeL16H$aGTuMsqNjLMWSGQuIRSIV." # md5 hash - "admin"

mount_image.sh $image

# is /etc/passwd a symlink?
if [ -L "$image_dir/etc/passwd" ]; then
  rm "$image_dir/etc/passwd"
fi

# does /etc/passwd exist?
if [ ! -f "$image_dir/etc/passwd" ]; then
  touch "$image_dir/etc/passwd"
fi

if [ -f "$image_dir/etc/passwd" ]; then
  if [ "`grep ^root $image_dir/etc/passwd | wc -l`" = "0" ]; then
    echo 'root:$1$I3WeL16H$aGTuMsqNjLMWSGQuIRSIV.:0:0:admin:/:/bin/sh' >> $image_dir/etc/passwd
    echo "Added root account to /etc/passwd."
  else
    sed 's/^root.*/root:$1$I3WeL16H$aGTuMsqNjLMWSGQuIRSIV.:0:0:root:\/root:\/bin\/sh/' $image_dir/etc/passwd
    echo "Set root account password!"
  fi


  if [ "`grep ^admin $image_dir/etc/passwd | wc -l`" = "0" ]; then
    echo 'admin:$1$I3WeL16H$aGTuMsqNjLMWSGQuIRSIV.:0:0:admin:/:/bin/sh' >> $image_dir/etc/passwd
    echo "Added admin account to /etc/passwd."
  else
    sed -i 's/^admin.*/admin:$1$I3WeL16H$aGTuMsqNjLMWSGQuIRSIV.:0:0:admin:\/:\/bin\/sh/' $image_dir/etc/passwd
    echo "Set admin account password!"
  fi
else
  echo "/etc/passwd doesn't exist!"
fi

unmount_image.sh $image
