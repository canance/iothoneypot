
# clone firmadyne kernel
# git clone https://github.com/firmadyne/kernel-v4.1
cd /root
# use this repo for the libvmi kernel module
wget https://github.com/canance/firmadyne-arm-kernel-libvmi/archive/firmadyne-v4.1.17.zip
unzip firmadyne-v4.1.17.zip # located at ~/kernel-v4.1-firmadyne-v4.1.17
# kernel src path /root/kernel-v4.1-firmadyne-v4.1.17

# extract arm-linux-musleabi.tar.gz to /opt/cross

# compile kernel
export CROSS_COMPILE=/opt/cross/arm-linux-musleabi/bin/arm-linux-musleabi-
export ARCH=arm
cd /root/kernel-v4.1-firmadyne-v4.1.17
mkdir -p build/armel
cp config.armel build/armel/.config
make ARCH=arm CROSS_COMPILE=/opt/cross/arm-linux-musleabi/bin/arm-linux-musleabi- O=./build/armel zImage

# compile linux-offset-finder
export CROSS_COMPILE=/opt/cross/arm-linux-musleabi/bin/arm-linux-musleabi-
export ARCH=arm
cd ~/libvmi/tools/linux-offset-finder
cat > Makefile <<EOF
ARCH := arm
CROSS_COMPILE := /opt/cross/arm-linux-musleabi/bin/arm-linux-musleabi-

obj-m := findoffsets.o
KDIR := /root/kernel-v4.1-firmadyne-v4.1.17/build/armel
PWD := $(shell pwd)

all:
        make -C $(KDIR) M=$(PWD) modules

clean:
        make -C $(KDIR) M=$(PWD) clean
EOF
make
