#!/usr/bin/env bash

# default arguments values
honeypot_interval=15
honeypot_runtime=60
honeypot_ip="10.10.10.10"

# parsing arg
# source: https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --interval)
    honeypot_interval="$2"
    shift # past argument
    shift # past value
    ;;
    --runtime)
    honeypot_runtime="$2"
    shift # past argument
    shift # past value
    ;;
    --ip)
    honeypot_ip="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

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

echo 0  | tee /proc/sys/net/bridge/bridge-nf-call-iptables &>/dev/null

# setting iptables rules
echo "[*] Rate limiting outgoing connections on tap0"
iptables -I OUTPUT -o tap0 -m conntrack --ctstate NEW -m recent --name outbound-connections --set -m comment --comment "Track outbound connections"
iptables -I OUTPUT 2 -o tap0 -m conntrack --ctstate NEW -m recent --name "outbound-connections" --update --seconds 120 --hitcount 5 -j DROP -m comment --comment "drop excessive outbound connections"

# remove old overlay for now...
if [ -f "image-overlay.qcow2" ]; then
  rm image-overlay.qcow2
fi
# create overlay if it doesn't exist
if [ ! -f "image-overlay.qcow2" ]; then
  echo "[*] Creating image-overlay.qcow2"
  qemu-img create -f qcow2 -b image.raw image-overlay.qcow2
fi

# start tcpdump to record net traffic
tcpdump -i tap0 -s 65535 -w net_dump.pcap &>/dev/null &
tcpdump_pid=$!

# start filebeat
filebeat &
filebeat_pid=$!

# start qemu
export QEMU_AUDIO_DRV=none
qemu-system-arm -M vexpress-a9 -m 256 -kernel ../../kernels/armel/zImage.armel -dtb ../../kernels/armel/vexpress-v2p-ca9.dtb -drive if=sd,file=image-overlay.qcow2,format=qcow2 -append "root=/dev/mmcblk0p1 console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rdinit=/firmadyne/preInit.sh rw debug ignore_loglevel print-fatal-signals=1 user_debug=31 firmadyne.syscall=0" -nographic -monitor unix:qemu-monitor.sock,server,nowait -serial unix:qemu-serial.sock,server,nowait -qmp unix:qemu-qmp.sock,server,nowait -net nic,netdev=net0 -netdev type=tap,ifname=tap0,id=net0,script=no,downscript=no &
qemu_pid=$!

echo "[*] qemu started!"
echo "[*] Serial access available on qemu-serial.sock"
echo "[*] Monitor access available on qemu-monitor.sock"
echo "[*] QMP access available on qemu-qmp.sock"

# run the honeypot monitor
honeypot_monitor.py --interval $honeypot_interval --runtime $honeypot_runtime --ip $honeypot_ip

# stop processes
echo "[*] Stopping qemu..."
kill $qemu_pid

echo "[*] Stopping filebeat..."
kill $filebeat_pid

echo "[*] Stopping tcpdump..."
kill $tcpdump_pid

echo "[*] Removing iptable rules for rate limiting..."
iptables -D OUTPUT 2
iptables -D OUTPUT 1

echo "[*] Removing sockets..."
rm qemu-monitor.sock qemu-qmp.sock qemu-serial.sock
