# delete bridge
ip link set dev tap0 nomaster
ip link set dev ens19 nomaster 
ip link del dev br0
ip link set dev ens19 down
ip link set dev ens19 up

# delete tap
ip tuntap del dev tap0 mode tap
