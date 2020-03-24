#!/bin/bash

# place firmware image in /root with a name starting with "image"

# sleep for 5s to give postgres enough time to load database schema

# grab firmware
image=$(readlink -f $1)

# start firmadyne process...
export PGPASSWORD=firmadyne
cd ~/firmadyne
id=$(timeout --preserve-status --signal SIGINT 60 ./sources/extractor/extractor.py -np -nk -b "honeypot" -sql 127.0.0.1 "${image}" images | grep ">> Database Image ID: " | cut -d ' ' -f 5)
re='^[0-9]+$'
if ! [[ $id =~ $re ]] ; then
   echo "error: timeout"; exit 1
fi

arch=$(./scripts/getArch.sh ./images/${id}.tar.gz | grep armel | wc -l)
if [ $arch -eq '0' ]; then
  echo Image ${id}: not armel
  rm ./images/${id}.tar.gz
  exit 1
fi
./scripts/tar2db.py -i ${id} -f ./images/${id}.tar.gz > /dev/null
./scripts/makeImage.sh ${id} > /dev/null
./scripts/inferNetwork.sh ${id}
cd /iothoneypot/scratch/${id}
echo "Image extract to /iothoneypot/scratch/${id}!"
