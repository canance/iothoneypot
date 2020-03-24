# create bridge
ip link add name br0 type bridge
ip link set br0 up

# connect eth0/eno1 to bridge
ip link set dev ens19 master br0
ip link set dev ens19 up

# assign IP address to bridge
ip addr add 192.168.1.250/24 dev br0

# create tap
ip tuntap add dev tap0 mode tap
ip link set dev tap0 master br0

# bring tap0 up
ip link set tap0 up

# add route
#ip route del default via 192.168.1.1 dev eno1
#ip route add default via 192.168.1.1 dev br0
