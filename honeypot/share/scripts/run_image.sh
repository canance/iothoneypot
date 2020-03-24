#!/usr/bin/env bash

# check if tap needs to be created
tap0_exist=$(ip addr show | grep tap0 | wc -l)
if [[ $tap0_exist -eq 0 ]]; then
  echo "[*] tap0 network interface missing!"
  echo "[*] Trying to create tap interface..."
  net_start.sh
  tap0_exist=$(ip addr show | grep tap0 | wc -l)
  if [[ $tap0_exist -eq 0 ]]; then
    echo "[*ERROR] Unable to create tap interface."
    echo "[*ERROR] Please create tap interface (tap0) and then try again."
    exit 1
  fi
fi

# remove docker blocking
echo 0  | tee /proc/sys/net/bridge/bridge-nf-call-iptables &>/dev/null

# run image
qemu-system-arm -M vexpress-a9 -m 256 -kernel ../../kernels/armel/zImage.armel -dtb ../../kernels/armel/vexpress-v2p-ca9.dtb -drive if=sd,file=image.raw,format=raw -append "root=/dev/mmcblk0p1 console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rdinit=/firmadyne/preInit.sh rw debug ignore_loglevel print-fatal-signals=1 user_debug=31 firmadyne.syscall=0" -nographic -net nic,netdev=net0 -netdev type=tap,ifname=tap0,id=net0,script=no,downscript=no
